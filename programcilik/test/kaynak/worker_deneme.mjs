/* Worker denemesi: taklit sunucu (gerçek PostgreSQL + worker.js + bellekte R2) üzerinden.
   Çalıştırma: sh test/sql/calistir.sh (veritabanını kurar), sonra node test/kaynak/worker_deneme.mjs */
import { spawn } from "node:child_process";
const PORT = 8797, K = "http://127.0.0.1:" + PORT, W = K + "/worker";
const KOKEN = "http://127.0.0.1:8765";
let gecen = 0, kalan = 0;
const kontrol = (ad, k, ek) => { if (k) { gecen++; console.log("GEÇTİ " + ad); } else { kalan++; console.log("KALDI " + ad + (ek !== undefined ? "  — " + JSON.stringify(ek) : "")); } };
const b64 = o => Buffer.from(JSON.stringify(o)).toString("base64url");
const jwt = (sub, sid, eposta) => b64({ alg: "HS256" }) + "." + b64({ sub, session_id: sid, email: eposta, role: "authenticated", exp: Math.floor(Date.now() / 1000) + 3600 }) + ".imza";
const A = jwt("aaaaaaaa-0000-4000-8000-00000000000a", "aaaaaaaa-1111-4000-8000-00000000000a", "wa@kocaelisaglik.edu.tr");
const B = jwt("bbbbbbbb-0000-4000-8000-00000000000b", "bbbbbbbb-1111-4000-8000-00000000000b", "wb@kocaelisaglik.edu.tr");
const webp = n => { const b = Buffer.alloc(n, 7); b.write("RIFF", 0); b.writeUInt32LE(n - 8, 4); b.write("WEBPVP8 ", 8); return b; };
const ist = (yol, belirtec, s = {}) => fetch(W + yol, { ...s, headers: { Origin: KOKEN, ...(belirtec ? { Authorization: "Bearer " + belirtec } : {}), ...(s.headers || {}) } });
const rest = (yol, belirtec, s = {}) => fetch(K + "/rest/v1" + yol, { ...s, headers: { apikey: "sb_publishable_deneme", Authorization: "Bearer " + belirtec, "Content-Type": "application/json", Prefer: "return=representation", ...(s.headers || {}) } });
const sql = q => fetch(K + "/sql", { method: "POST", body: q }).then(r => r.json());

const sunucu = spawn("node", [new URL("./sahte_sunucu.mjs", import.meta.url).pathname, String(PORT)], { stdio: ["ignore", "pipe", "inherit"] });
await new Promise(r => sunucu.stdout.once("data", r));
try {
  // Kimlik ve köken
  let r = await fetch(W + "/durum", { headers: { Origin: "https://kotu.ornek", Authorization: "Bearer " + A } });
  kontrol("bilinmeyen köken reddedilir (403, CORS başlığı yok)", r.status === 403 && !r.headers.get("access-control-allow-origin"));
  r = await fetch(W + "/durum", { method: "OPTIONS", headers: { Origin: KOKEN } });
  kontrol("ön istek (OPTIONS) izinli kökene 204", r.status === 204 && r.headers.get("access-control-allow-origin") === KOKEN);
  r = await ist("/durum", null);
  kontrol("belirteçsiz istek 401", r.status === 401);
  r = await ist("/durum", "bozuk.belirtec");
  kontrol("bozuk belirteç 401", r.status === 401);
  r = await ist("/durum", A); const d = await r.json();
  kontrol("durum: 50 MB, 0 kullanılan", r.status === 200 && d.azami_bayt === 52428800 && d.kullanilan_bayt === 0, d);

  // Tasnif (uygulamanın yaptığı gibi doğrudan Supabase'e)
  r = await rest("/kaynak_tasnif", A, { method: "POST", body: JSON.stringify({ ad: "Donanım" }) });
  const T = (await r.json())[0];
  kontrol("tasnif açılır", r.status === 200 && T && T.derinlik === 1, T);
  r = await rest("/kaynak_tasnif", A, { method: "POST", body: JSON.stringify({ ad: "Anakart", ust: T.id }) });
  const T2 = (await r.json())[0];

  // Yükleme
  r = await ist("/resim?tasnif=" + T.id + "&en=2048&boy=1536", A, { method: "POST", headers: { "Content-Type": "image/webp" }, body: webp(300000) });
  const R1 = await r.json();
  kontrol("WebP yüklenir (201), satır döner", r.status === 201 && R1.bayt === 300000 && R1.tasnif === T.id, R1);
  const r2 = await (await fetch(K + "/r2")).json();
  kontrol("R2 anahtarı <kullanıcı>/<id>.webp", r2.includes("aaaaaaaa-0000-4000-8000-00000000000a/" + R1.id + ".webp"), r2);
  r = await ist("/resim?tasnif=" + T.id + "&en=10&boy=10", A, { method: "POST", body: Buffer.from("\x89PNG\r\n\x1a\nxxxxxxxxxxxxxxxx") });
  kontrol("WebP olmayan dosya 415", r.status === 415);
  r = await ist("/resim?tasnif=" + T.id + "&en=10&boy=10", A, { method: "POST", body: webp(5 * 1024 * 1024) });
  kontrol("4 MB'tan büyük resim 413", r.status === 413);
  r = await ist("/resim?tasnif=" + T.id + "&en=9000&boy=10", A, { method: "POST", body: webp(1000) });
  kontrol("4096 px'ten büyük ölçü 400", r.status === 400);
  r = await ist("/resim?tasnif=nedir&en=10&boy=10", A, { method: "POST", body: webp(1000) });
  kontrol("geçersiz tasnif 400", r.status === 400);

  // Okuma ve başkası
  r = await ist("/resim/" + R1.id, A);
  const veri = Buffer.from(await r.arrayBuffer());
  kontrol("sahibi resmi alır (image/webp, aynı bayt)", r.status === 200 && r.headers.get("content-type") === "image/webp" && veri.length === 300000);
  r = await ist("/resim/" + R1.id, B);
  kontrol("başkası aynı kimlikle alamaz (404)", r.status === 404);
  r = await ist("/resim?tasnif=" + T.id + "&en=10&boy=10", B, { method: "POST", body: webp(1000) });
  kontrol("başkasının tasnifine yükleyemez (404), R2'de artık kalmaz", r.status === 404 && (await (await fetch(K + "/r2")).json()).length === 1);
  r = await ist("/resim/" + R1.id, B, { method: "DELETE" });
  kontrol("başkasının silmesi A'nın resmine dokunmaz", (await (await fetch(K + "/r2")).json()).length === 1);

  // Kota: hakkı 1 MB'a indir
  await sql("update public.kaynak_kota set azami_mb = 1 where eposta = 'wa@kocaelisaglik.edu.tr'");
  r = await ist("/resim?tasnif=" + T2.id + "&en=10&boy=10", A, { method: "POST", body: webp(800000) });
  const kota = await r.json();
  kontrol("hak dolunca 413 ve kota işareti (300000 + 800000 bayt > 1 MB)", r.status === 413 && kota.kota === true, kota);
  kontrol("reddedilen resim R2'de kalmaz", (await (await fetch(K + "/r2")).json()).length === 1);
  await sql("update public.kaynak_kota set azami_mb = 50 where eposta = 'wa@kocaelisaglik.edu.tr'");
  r = await ist("/resim?tasnif=" + T2.id + "&en=10&boy=10", A, { method: "POST", body: webp(800000) });
  const R2y = await r.json();
  kontrol("hak artınca yüklenir", r.status === 201, R2y);
  r = await ist("/durum", A);
  kontrol("durum kullanımı günceller (1100000 bayt)", (await r.json()).kullanilan_bayt === 1100000);

  // R2'de artık kalmış (kaydı olmayan) dosya okunamaz
  await sql("delete from public.kaynak_oge where id = '" + R2y.id + "'");
  r = await ist("/resim/" + R2y.id, A);
  kontrol("kaydı silinmiş resim R2'de olsa da verilmez (404)", r.status === 404 && (await (await fetch(K + "/r2")).json()).some(x => x.includes(R2y.id)));
  r = await ist("/resim?tasnif=" + T.id + "&en=10&boy=10", A, { method: "POST", body: Buffer.concat([webp(1000), Buffer.alloc(50)]) });
  kontrol("RIFF boyu dosyayla uyuşmayan sahte WebP 415", r.status === 415);
  r = await ist("/resim/" + R1.id, A);
  kontrol("resim yanıtı tarayıcı diskine yazılmaz (no-store, nosniff)", r.headers.get("cache-control").includes("no-store") && r.headers.get("x-content-type-options") === "nosniff");

  // Uygulamanın ürettiği kimlik: yeniden gönderim çift kayıt açmaz
  const RID = "aaaaaaaa-5555-4000-8000-000000000001";
  const r2say = async () => (await (await fetch(K + "/r2")).json()).length;
  const once = await r2say();
  r = await ist("/resim?tasnif=" + T.id + "&en=10&boy=10&id=" + RID + "&zaman=" + encodeURIComponent(new Date(Date.now() - 3600e3).toISOString()), A, { method: "POST", body: webp(2000) });
  const RK = await r.json();
  kontrol("istenen kimlikle yüklenir (201) ve cihazdaki anı korunur", r.status === 201 && RK.id === RID && Math.abs(Date.parse(RK.olusma) - (Date.now() - 3600e3)) < 5000, RK);
  r = await ist("/resim?tasnif=" + T.id + "&en=10&boy=10&id=" + RID, A, { method: "POST", body: webp(2000) });
  const RK2 = await r.json();
  const satirSay = (await sql("select count(*)::int as n, sum(bayt)::int as b from public.kaynak_oge where id = '" + RID + "'"))[0];
  kontrol("aynı kimlik yeniden gelince var olan satır döner (200), ikinci satır yok", r.status === 200 && RK2.id === RID && satirSay.n === 1 && satirSay.b === 2000 && (await r2say()) === once + 1, [r.status, satirSay]);
  r = await ist("/resim?tasnif=" + T.id + "&en=10&boy=10&id=" + RID, B, { method: "POST", body: webp(1000) });
  kontrol("başkasının kimliğiyle yükleme reddedilir, R2'de artık kalmaz", r.status === 409 && (await r2say()) === once + 1, r.status);
  r = await ist("/resim?tasnif=" + T.id + "&en=10&boy=10&id=bozuk", A, { method: "POST", body: webp(1000) });
  kontrol("geçersiz kimlik 400", r.status === 400);

  // Notun içindeki resim; notu resimleriyle silme
  const NID = "aaaaaaaa-6666-4000-8000-000000000001";
  r = await rest("/kaynak_oge", A, { method: "POST", body: JSON.stringify({ id: NID, tasnif: T.id, tur: "not", baslik: "Başlık", metin: "<p>x</p>", bicim: "html" }) });
  kontrol("biçimli not kimliğiyle açılır", r.status === 200 && (await r.json())[0].id === NID);
  r = await ist("/resim?tasnif=" + T.id + "&en=10&boy=10&not=" + NID + "&id=aaaaaaaa-5555-4000-8000-000000000002", A, { method: "POST", body: webp(1500) });
  const NR = await r.json();
  kontrol("notun içine resim (not_id)", r.status === 201 && NR.not_id === NID, NR);
  r = await ist("/resim?tasnif=" + T2.id + "&en=10&boy=10&not=" + NID, A, { method: "POST", body: webp(1500) });
  kontrol("başka tasnifteki nota resim bağlanamaz (404), R2'de artık kalmaz", r.status === 404 && (await r2say()) === once + 2, r.status);
  r = await rest("/kaynak_oge?id=eq." + NID, A, { method: "DELETE" });
  kontrol("resimli not doğrudan silinemez", r.status !== 200 || (await sql("select count(*)::int as n from public.kaynak_oge where id = '" + NID + "'"))[0].n === 1);
  r = await ist("/not/" + NID, B, { method: "DELETE" });
  kontrol("başkası A'nın notunu silemez (hiçbir şey silinmez)", r.status === 200 && (await r.json()).silinen_resim === 0 && (await sql("select count(*)::int as n from public.kaynak_oge where id = '" + NID + "'"))[0].n === 1);
  r = await ist("/not/" + NID, A, { method: "DELETE" });
  const ns = await r.json();
  kontrol("not resmiyle silinir, resim R2'den de", r.status === 200 && ns.silinen_resim === 1 && !(await (await fetch(K + "/r2")).json()).some(x => x.includes(NR.id))
    && (await sql("select count(*)::int as n from public.kaynak_oge where id in ('" + NID + "', '" + NR.id + "')"))[0].n === 0, ns);
  r = await ist("/not/" + NID, A, { method: "DELETE" });
  kontrol("silinmiş notu yeniden silmek zararsız (200)", r.status === 200 && (await r.json()).silinen_resim === 0);

  // Silme
  r = await ist("/resim/" + R1.id, A, { method: "DELETE" });
  kontrol("resim silinir (204), R2'den de", r.status === 204 && !(await (await fetch(K + "/r2")).json()).some(x => x.includes(R1.id)));
  r = await ist("/tasnif/" + T.id, A, { method: "DELETE" });
  const ts = await r.json();
  kontrol("tasnif bütün içiyle silinir (içindeki resim R2'den)", r.status === 200 && ts.silinen_resim === 1 && !(await (await fetch(K + "/r2")).json()).some(x => x.includes(R1.id) || x.includes(RID)), ts);
  // Cihaz devredilince yazma hemen durur (yazmada kimlik önbelleği yok)
  r = await ist("/durum", A); await r.json();
  r = await rest("/kaynak_tasnif", A, { method: "POST", body: JSON.stringify({ ad: "Yeni" }) });
  const T3 = (await r.json())[0];
  r = await ist("/resim/" + "00000000-0000-4000-8000-000000000000", A);   // okuma: önbelleğe girer
  await sql("delete from public.cihaz_yerleri where kullanici = 'aaaaaaaa-0000-4000-8000-00000000000a'");
  r = await ist("/resim?tasnif=" + T3.id + "&en=10&boy=10", A, { method: "POST", body: webp(1000) });
  kontrol("cihaz devredilince yükleme hemen reddedilir (403)", r.status === 403, r.status);
  r = await ist("/tasnif/" + T3.id, A, { method: "DELETE" });
  kontrol("cihaz devredilince silme hemen reddedilir (403)", r.status === 403, r.status);
  await sql("insert into public.cihaz_yerleri (kullanici, oturum) values ('aaaaaaaa-0000-4000-8000-00000000000a', 'aaaaaaaa-1111-4000-8000-00000000000a')");
  r = await ist("/tasnif/" + T3.id, A, { method: "DELETE" });

  const kalanSatir = await sql("select count(*)::int as n from public.kaynak_tasnif where kullanici = 'aaaaaaaa-0000-4000-8000-00000000000a'");
  kontrol("tablolarda satır kalmaz", kalanSatir[0].n === 0, kalanSatir);
} finally { sunucu.kill(); }
console.log("\n" + gecen + "/" + (gecen + kalan) + " geçti");
process.exit(kalan ? 1 : 0);

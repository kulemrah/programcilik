/* ==========================================================================
   Kostü - Ders · Kaynak Worker'ı (Cloudflare)
   Öğrencilerin Kaynak resimlerini R2'de tutar. Uygulama R2'ye doğrudan
   erişemez (anahtar uygulamaya yazılamaz); her istek buradan geçer:

     GET    /durum            hak ve kullanım (bayt)
     POST   /resim?tasnif=…&en=…&boy=…[&id=…&not=…&zaman=…]
                              gövde: WebP; R2'ye koyar, satırı açar. id: uygulamanın
                              ürettiği kimlik (aynı id yeniden gelirse var olan satır
                              döner, R2'ye yeniden yazılmaz); not: resim bu notun
                              metninin içinde; zaman: cihazda eklendiği an (ISO)
     GET    /resim/<id>       resmi verir (yalnızca sahibine ve kaydı varsa)
     DELETE /resim/<id>       R2'den ve tablodan siler
     DELETE /not/<id>         notu içindeki resimlerle (R2'den) siler
     DELETE /tasnif/<id>      tasnifi bütün içiyle (resimler R2'den) siler
   Silmeler yeniden gönderilebilir: olmayanı silmek hata değildir.

   Kimlik: istekteki Supabase belirteci (Authorization: Bearer …) ile
   public.kaynak_durum çağrılır. PostgREST belirteci doğrular; işlev,
   öğrencinin okul üyesi, sözleşmeyi onaylamış ve hesabın aktif cihazında
   olduğunu söyler, kullanıcı kimliğini döner. R2 anahtarı bu kimlikten
   kurulur ("<kullanici>/<id>.webp"): başkasının resmine yol yoktur.
   Kota ve satır yazımı gizli anahtarla (service_role) yapılan işlevlerdedir
   (01-sema.sql, 8. bölüm).

   Ortam (wrangler.toml ve Cloudflare panelindeki sırlar):
     KAYNAK                 R2 kovası bağlantısı
     SUPABASE_URL           https://<proje>.supabase.co
     SUPABASE_ANAHTAR       publishable key (sb_publishable_…)
     SUPABASE_GIZLI_ANAHTAR secret key (sb_secret_…), sır olarak
     IZINLI_KOKENLER        virgülle ayrılmış kökenler (https://kulemrah.github.io)
   ========================================================================== */

const AZAMI_DOSYA = 4 * 1024 * 1024;          /* bir resim en çok 4 MB (2048 px WebP ~0,2–0,5 MB) */
const AZAMI_KENAR = 4096;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const KIMLIK_SURESI = 60 * 1000;               /* yalnızca okumada: doğrulanmış belirteç en çok bu kadar hatırlanır */
const kimlikBellegi = new Map();

function koken(istek, env) {
  const gelen = istek.headers.get("Origin") || "";
  const izinli = String(env.IZINLI_KOKENLER || "").split(",").map(s => s.trim()).filter(Boolean);
  return izinli.includes(gelen) ? gelen : null;
}

function corsBasliklari(k) {
  if (!k) return {};
  return {
    "Access-Control-Allow-Origin": k,
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin"
  };
}

function cevap(veri, durum, k, ek) {
  return new Response(veri === null ? null : JSON.stringify(veri), {
    status: durum,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsBasliklari(k), ...(ek || {}) }
  });
}
const hata = (mesaj, durum, k) => cevap({ hata: mesaj }, durum, k);

/* Gizli anahtarla Supabase işlevi çağırır (yeni sb_secret_ anahtarı yalnızca apikey başlığında gider) */
async function servis(env, islev, govde) {
  const basliklar = { apikey: env.SUPABASE_GIZLI_ANAHTAR, "Content-Type": "application/json" };
  if (String(env.SUPABASE_GIZLI_ANAHTAR).startsWith("eyJ")) basliklar.Authorization = "Bearer " + env.SUPABASE_GIZLI_ANAHTAR;
  const c = await fetch(env.SUPABASE_URL + "/rest/v1/rpc/" + islev, { method: "POST", headers: basliklar, body: JSON.stringify(govde) });
  const metin = await c.text();
  let veri = null;
  try { veri = metin ? JSON.parse(metin) : null; } catch (e) { veri = metin; }
  if (!c.ok) {
    const e = new Error((veri && veri.message) || ("Supabase " + c.status));
    e.durum = c.status;
    throw e;
  }
  return veri;
}

/* Belirtecin bitiş anı (ms); okunamazsa 0. İmza burada denetlenmez (onu PostgREST yapar);
   yalnızca önbellekte belirtecin süresinden uzun tutulmaması için okunur. */
function bitisAni(b) {
  try {
    const p = b.slice(7).split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const exp = JSON.parse(atob(p + "===".slice((p.length + 3) % 4))).exp;
    return typeof exp === "number" ? exp * 1000 : 0;
  } catch (e) { return 0; }
}

/* İstekteki belirteçle kaynak_durum: { kullanici, azami_bayt, kullanilan_bayt }.
   Yazma isteklerinde (POST, DELETE) her seferinde Supabase'e sorulur: oturum
   kapanınca ya da cihaz devredilince yazma hemen durur. Okumada en çok 60 sn
   (ve belirtecin süresi kadar) hatırlanır. */
async function kimlik(istek, env) {
  const b = istek.headers.get("Authorization") || "";
  if (!b.startsWith("Bearer ") || b.length > 4096) return { durum: 401 };
  const simdi = Date.now();
  const okuma = istek.method === "GET";
  const bellek = okuma ? kimlikBellegi.get(b) : null;
  if (bellek && bellek.son > simdi) return { durum: 200, k: bellek.k };
  const c = await fetch(env.SUPABASE_URL + "/rest/v1/rpc/kaynak_durum", {
    method: "POST",
    headers: { apikey: env.SUPABASE_ANAHTAR, Authorization: b, "Content-Type": "application/json" },
    body: "{}"
  });
  if (c.status === 401 || c.status === 403) return { durum: 401 };
  if (!c.ok) return { durum: 502 };
  const d = await c.json();
  if (!d || !d.izin || !UUID.test(String(d.kullanici))) return { durum: 403 };
  if (kimlikBellegi.size > 500) kimlikBellegi.clear();
  const son = Math.min(simdi + KIMLIK_SURESI, bitisAni(b) || simdi);
  if (okuma && son > simdi) kimlikBellegi.set(b, { k: d, son });
  return { durum: 200, k: d };
}

/* RIFF/WEBP imzası, RIFF boyutu dosyayla uyumlu ve ilk parça VP8/VP8L/VP8X */
function webpMi(bayt) {
  if (bayt.length < 20) return false;
  const yazi = (i, n) => String.fromCharCode(...bayt.slice(i, i + n));
  const riffBoyu = bayt[4] | (bayt[5] << 8) | (bayt[6] << 16) | (bayt[7] << 24);
  return yazi(0, 4) === "RIFF" && yazi(8, 4) === "WEBP" &&
    (riffBoyu + 8 === bayt.length || riffBoyu + 9 === bayt.length) &&
    ["VP8 ", "VP8L", "VP8X"].includes(yazi(12, 4));
}

/* Gövdeyi en çok "sinir" bayt okur; aşarsa null (bütün gövde belleğe alınmaz) */
async function sinirliOku(istek, sinir) {
  if (!istek.body) return new Uint8Array(0);
  const okuyucu = istek.body.getReader();
  const parcalar = [];
  let toplam = 0;
  for (;;) {
    const { done, value } = await okuyucu.read();
    if (done) break;
    toplam += value.length;
    if (toplam > sinir) { try { await okuyucu.cancel(); } catch (e) {} return null; }
    parcalar.push(value);
  }
  const sonuc = new Uint8Array(toplam);
  let i = 0;
  for (const p of parcalar) { sonuc.set(p, i); i += p.length; }
  return sonuc;
}

const anahtar = (kullanici, id) => kullanici + "/" + id + ".webp";

export default {
  async fetch(istek, env) {
    const k = koken(istek, env);
    if (istek.method === "OPTIONS") return new Response(null, { status: k ? 204 : 403, headers: corsBasliklari(k) });
    if (!k) return hata("Bu kökenden istek kabul edilmez.", 403, null);

    const url = new URL(istek.url);
    const yol = url.pathname.replace(/\/+$/, "").split("/").filter(Boolean);

    let kim;
    try { kim = await kimlik(istek, env); }
    catch (e) { return hata("Hesap doğrulanamadı.", 502, k); }
    if (kim.durum === 401) return hata("Oturum geçersiz.", 401, k);
    if (kim.durum === 403) return hata("Bu hesapla Kaynak kullanılamaz.", 403, k);
    if (kim.durum !== 200) return hata("Hesap doğrulanamadı.", 502, k);
    const ben = kim.k.kullanici;

    try {
      /* GET /durum */
      if (istek.method === "GET" && yol.length === 1 && yol[0] === "durum") {
        const d = await servisDurum(env, istek);
        return cevap(d, 200, k, { "Cache-Control": "no-store" });
      }

      /* POST /resim */
      if (istek.method === "POST" && yol.length === 1 && yol[0] === "resim") {
        const tasnif = url.searchParams.get("tasnif") || "";
        const en = parseInt(url.searchParams.get("en"), 10), boy = parseInt(url.searchParams.get("boy"), 10);
        const istenenId = url.searchParams.get("id") || "";
        const notId = url.searchParams.get("not") || "";
        const zamanYazisi = url.searchParams.get("zaman") || "";
        if (!UUID.test(tasnif)) return hata("Tasnif geçersiz.", 400, k);
        if (!(en > 0 && en <= AZAMI_KENAR && boy > 0 && boy <= AZAMI_KENAR)) return hata("Resim ölçüsü geçersiz.", 400, k);
        if (istenenId && !UUID.test(istenenId)) return hata("Kimlik geçersiz.", 400, k);
        if (notId && !UUID.test(notId)) return hata("Not geçersiz.", 400, k);
        const zaman = zamanYazisi && Number.isFinite(Date.parse(zamanYazisi)) ? new Date(Date.parse(zamanYazisi)).toISOString() : null;
        /* Aynı kimlik yeniden geldi (önceki cevap yolda kaybolmuştu): var olan satır döner */
        if (istenenId) {
          const var_ = await servis(env, "kaynak_resim_satiri", { sahip: ben, oge_id: istenenId });
          if (var_ && var_.id) return cevap(var_, 200, k);
        }
        const uzunluk = parseInt(istek.headers.get("Content-Length") || "0", 10);
        if (uzunluk > AZAMI_DOSYA) return hata("Resim çok büyük.", 413, k);
        const bayt = await sinirliOku(istek, AZAMI_DOSYA);
        if (!bayt) return hata("Resim çok büyük.", 413, k);
        if (!bayt.length) return hata("Resim boş.", 400, k);
        if (!webpMi(bayt)) return hata("Yalnızca WebP kabul edilir.", 415, k);
        /* Hızlı ön denetim (asıl denetim kaynak_resim_ekle'de, kilitle) */
        if (Number(kim.k.kullanilan_bayt) + bayt.length > Number(kim.k.azami_bayt)) {
          return cevap({ hata: "Resim hakkınız doldu.", kota: true }, 413, k);
        }
        const id = istenenId || crypto.randomUUID();
        await env.KAYNAK.put(anahtar(ben, id), bayt, { httpMetadata: { contentType: "image/webp" } });
        let satir;
        try {
          const govde = { sahip: ben, oge_id: id, tasnif_id: tasnif, boyut: bayt.length, genislik: en, yukseklik: boy };
          if (notId) govde.not_kimligi = notId;
          if (zaman) govde.zaman = zaman;
          satir = await servis(env, "kaynak_resim_ekle", govde);
        } catch (e) {
          await env.KAYNAK.delete(anahtar(ben, id));
          if (/^kota$/.test(e.message)) return cevap({ hata: "Resim hakkınız doldu.", kota: true }, 413, k);
          if (/Tasnif/.test(e.message)) return hata("Tasnif bulunamadı.", 404, k);
          if (/Not bulunamad/.test(e.message)) return hata("Not bulunamadı.", 404, k);
          if (/^kimlik$/.test(e.message)) return hata("Kimlik kullanılıyor.", 409, k);
          throw e;
        }
        return cevap(satir, 201, k);
      }

      /* GET | DELETE /resim/<id> */
      if (yol.length === 2 && yol[0] === "resim" && UUID.test(yol[1])) {
        const id = yol[1];
        if (istek.method === "GET") {
          /* Yalnızca kaydı olan resim verilir: R2'de artık kalmış bir dosya okunamaz */
          if (!(await servis(env, "kaynak_resim_var", { sahip: ben, oge_id: id }))) return hata("Resim bulunamadı.", 404, k);
          const nesne = await env.KAYNAK.get(anahtar(ben, id));
          if (!nesne) return hata("Resim bulunamadı.", 404, k);
          /* Tarayıcının diskine yazılmaz (ortak bilgisayar); uygulama kendi kopyasını tutar */
          return new Response(nesne.body, {
            status: 200,
            headers: { "Content-Type": "image/webp", "Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff", ...corsBasliklari(k) }
          });
        }
        if (istek.method === "DELETE") {
          /* Önce satır (kota hemen boşalır), sonra R2 */
          await servis(env, "kaynak_resim_sil", { sahip: ben, oge_id: id });
          await env.KAYNAK.delete(anahtar(ben, id));
          return cevap(null, 204, k);
        }
      }

      /* DELETE /not/<id> */
      if (istek.method === "DELETE" && yol.length === 2 && yol[0] === "not" && UUID.test(yol[1])) {
        const resimler = [].concat(await servis(env, "kaynak_not_sil", { sahip: ben, not_kimligi: yol[1] }) || []);
        const anahtarlar = resimler
          .map(x => typeof x === "string" ? x : x && x.kaynak_not_sil)
          .filter(x => UUID.test(String(x)))
          .map(x => anahtar(ben, x));
        for (let i = 0; i < anahtarlar.length; i += 1000) await env.KAYNAK.delete(anahtarlar.slice(i, i + 1000));
        return cevap({ silinen_resim: anahtarlar.length }, 200, k);
      }

      /* DELETE /tasnif/<id> */
      if (istek.method === "DELETE" && yol.length === 2 && yol[0] === "tasnif" && UUID.test(yol[1])) {
        /* Satırlar tek işlemde silinir ve silinen resimlerin kimlikleri döner
           (bu sırada eklenmiş resim de dahil); sonra tam olarak onlar R2'den */
        const resimler = [].concat(await servis(env, "kaynak_tasnif_icini_sil", { sahip: ben, tasnif_id: yol[1] }) || []);
        const anahtarlar = resimler
          .map(x => typeof x === "string" ? x : x && x.kaynak_tasnif_icini_sil)
          .filter(x => UUID.test(String(x)))
          .map(x => anahtar(ben, x));
        for (let i = 0; i < anahtarlar.length; i += 1000) await env.KAYNAK.delete(anahtarlar.slice(i, i + 1000));
        return cevap({ silinen_resim: anahtarlar.length }, 200, k);
      }

      return hata("Bulunamadı.", 404, k);
    } catch (e) {
      /* Ayrıntı yalnızca Worker günlüğüne; kullanıcıya genel ileti */
      console.error("kaynak hata", istek.method, url.pathname, e && e.message);
      return hata("Sunucu hatası. Biraz sonra yeniden deneyin.", 500, k);
    }
  }
};

/* /durum her zaman taze okunur (bellekteki kimlik eski kullanımı tutabilir) */
async function servisDurum(env, istek) {
  const c = await fetch(env.SUPABASE_URL + "/rest/v1/rpc/kaynak_durum", {
    method: "POST",
    headers: { apikey: env.SUPABASE_ANAHTAR, Authorization: istek.headers.get("Authorization"), "Content-Type": "application/json" },
    body: "{}"
  });
  const d = await c.json();
  return { azami_bayt: Number(d.azami_bayt), kullanilan_bayt: Number(d.kullanilan_bayt) };
}

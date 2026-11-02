/* Kaynak için taklit sunucu (yalnızca deneme).
   - /rest/v1/...      : PostgREST'in Kaynak'ın kullandığı küçük bir parçası; istekler
                         gerçek PostgreSQL'deki şemaya (01-sema.sql) rol ve JWT
                         alanlarıyla iletilir, yani RLS ve izinler gerçekten işler.
   - /worker/...       : kaynak-worker/worker.js'in kendisi; R2 bellekte tutulur.
   Belirteç: test düzeneğinin ürettiği JWT (imzası denetlenmez); alanları
   request.jwt.claims'e yazılır. Her yeni belirteç için kullanıcı, oturum, cihaz
   yeri ve sözleşme kurulur (uye() doğru olsun diye).
   Kullanım: node sahte_sunucu.mjs <port>   (PG: /tmp soketi, 5499, veritabanı sema_deneme) */
import http from "node:http";
import pg from "pg";
import worker from "../../kaynak-worker/worker.js";

const PORT = parseInt(process.argv[2] || "8798", 10);
const KOK = "http://127.0.0.1:" + PORT;
const GIZLI = "sb_secret_deneme";
const ACIK = "sb_publishable_deneme";
const havuz = new pg.Pool({ host: "/tmp", port: 5499, user: "postgres", database: process.env.PGDATABASE || "sema_deneme", max: 4 });

/* R2 taklidi */
export const R2 = new Map();
const kova = {
  async put(k, v, s) { R2.set(k, { veri: Buffer.from(v), tur: s && s.httpMetadata && s.httpMetadata.contentType }); },
  async get(k) { const n = R2.get(k); return n ? { body: n.veri } : null; },
  async delete(k) { (Array.isArray(k) ? k : [k]).forEach(x => R2.delete(x)); }
};
const ENV = { KAYNAK: kova, SUPABASE_URL: KOK, SUPABASE_ANAHTAR: ACIK, SUPABASE_GIZLI_ANAHTAR: GIZLI,
  IZINLI_KOKENLER: "http://127.0.0.1:8765,https://kulemrah.github.io" };

const kurulanlar = new Set();
let kurulumSirasi = Promise.resolve();   /* aynı anda gelen istekler üyeliği sırayla kursun */
function uyelikKur(c, claims) {
  const is = kurulumSirasi.then(() => uyelikKurAsil(c, claims));
  kurulumSirasi = is.catch(() => {});
  return is;
}
async function uyelikKurAsil(c, claims) {
  const anahtar = claims.sub + "|" + claims.session_id;
  if (kurulanlar.has(anahtar)) return;
  const eposta = claims.email || "ogr@kocaelisaglik.edu.tr";
  await c.query("insert into auth.users (id, email, email_confirmed_at) values ($1, $2, now()) on conflict (id) do nothing", [claims.sub, eposta]);
  if (claims.session_id) {
    await c.query("insert into auth.sessions (id, user_id, user_agent) values ($1, $2, 'test') on conflict (id) do nothing", [claims.session_id, claims.sub]);
    await c.query("insert into public.hesap_cihazlari (kullanici, eposta) values ($1, $2) on conflict (kullanici) do nothing", [claims.sub, eposta]);
    await c.query("delete from public.cihaz_yerleri where kullanici = $1 and oturum <> $2", [claims.sub, claims.session_id]);
    await c.query("insert into public.cihaz_yerleri (kullanici, oturum) values ($1, $2) on conflict do nothing", [claims.sub, claims.session_id]);
  }
  await c.query("insert into public.profiller (kullanici, program, sinif, sozlesme_surumu) values ($1, 'bilgisayar-programciligi', 1, public.sozlesme_surumu()) on conflict (kullanici) do nothing", [claims.sub]);
  kurulanlar.add(anahtar);
}

function claimsOku(basliklar) {
  const apikey = basliklar["apikey"] || "";
  const b = basliklar["authorization"] || "";
  if (apikey === GIZLI && (!b || b === "Bearer " + GIZLI)) return { rol: "service_role", claims: { role: "service_role" } };
  if (!b.startsWith("Bearer ")) return { rol: "anon", claims: { role: "anon" } };
  const parca = b.slice(7).split(".");
  if (parca.length !== 3) return null;
  try {
    const claims = JSON.parse(Buffer.from(parca[1], "base64url").toString());
    if (claims.exp && claims.exp * 1000 < Date.now()) return null;
    return { rol: "authenticated", claims };
  } catch (e) { return null; }
}

const TABLOLAR = new Set(["kaynak_tasnif", "kaynak_oge"]);
const kimlikAdi = s => { if (!/^[a-z_]+$/.test(s)) throw new Error("ad"); return '"' + s + '"'; };

async function rest(yol, sorgu, yontem, basliklar, govde) {
  const kim = claimsOku(basliklar);
  if (!kim) return [401, { message: "JWT geçersiz" }];
  const c = await havuz.connect();
  try {
    if (kim.rol === "authenticated") await uyelikKur(c, kim.claims);
    await c.query("begin");
    await c.query("select set_config('request.jwt.claims', $1, true)", [JSON.stringify(kim.claims)]);
    await c.query("set local role " + kim.rol);
    let sonuc;
    const m = yol.match(/^\/rest\/v1\/rpc\/([a-z_]+)$/);
    if (m && yontem === "POST") {
      const a = govde ? JSON.parse(govde) : {};
      const adlar = Object.keys(a);
      const r = await c.query("select * from public." + kimlikAdi(m[1]) + "(" + adlar.map((n, i) => kimlikAdi(n) + " => $" + (i + 1)).join(", ") + ")", adlar.map(n => a[n]));
      const sutun = r.fields.length === 1 ? r.fields[0].name : null;
      /* PostgREST gibi: küme döndüren işlev her zaman dizi verir */
      const kume = (await c.query("select bool_or(proretset) as k from pg_proc where proname = $1", [m[1]])).rows[0].k;
      const tek = !kume && r.rows.length === 1 && sutun === m[1];
      sonuc = tek ? r.rows[0][sutun] : (sutun === m[1] ? r.rows.map(x => x[sutun]) : r.rows);
    } else {
      const t = (yol.match(/^\/rest\/v1\/([a-z_]+)$/) || [])[1];
      if (!TABLOLAR.has(t)) return [404, { message: "yok" }];
      const kosul = [], deger = [];
      for (const [k, v] of sorgu) {
        if (["select", "order", "limit", "columns"].includes(k)) continue;
        const e = v.match(/^eq\.(.*)$/); const i = v.match(/^in\.\((.*)\)$/);
        if (e) { deger.push(e[1]); kosul.push(kimlikAdi(k) + "::text = $" + deger.length); }
        else if (i) { deger.push(i[1].split(",").map(x => x.replace(/^"|"$/g, ""))); kosul.push(kimlikAdi(k) + "::text = any($" + deger.length + ")"); }
      }
      const nerede = kosul.length ? " where " + kosul.join(" and ") : "";
      if (yontem === "GET") sonuc = (await c.query("select * from public." + t + nerede + " order by olusma, id", deger)).rows;
      else if (yontem === "POST") {
        const satirlar = [].concat(JSON.parse(govde));
        sonuc = [];
        for (const s of satirlar) {
          const ad = Object.keys(s);
          sonuc.push((await c.query("insert into public." + t + " (" + ad.map(kimlikAdi).join(",") + ") values (" + ad.map((_, i) => "$" + (i + 1)).join(",") + ") returning *", ad.map(n => s[n]))).rows[0]);
        }
      } else if (yontem === "PATCH") {
        const s = JSON.parse(govde); const ad = Object.keys(s);
        const d2 = deger.concat(ad.map(n => s[n]));
        sonuc = (await c.query("update public." + t + " set " + ad.map((n, i) => kimlikAdi(n) + " = $" + (deger.length + i + 1)).join(",") + nerede + " returning *", d2)).rows;
      } else if (yontem === "DELETE") sonuc = (await c.query("delete from public." + t + nerede + " returning *", deger)).rows;
    }
    await c.query("commit");
    return [200, sonuc];
  } catch (e) {
    await c.query("rollback").catch(() => {});
    return [/permission denied|row-level security/.test(e.message) ? 403 : 400, { message: e.message, code: e.code }];
  } finally { c.release(); }
}

const sunucu = http.createServer(async (istek, yanit) => {
  const parcalar = [];
  for await (const p of istek) parcalar.push(p);
  const govde = Buffer.concat(parcalar);
  const url = new URL(istek.url, KOK);
  try {
    if (url.pathname.startsWith("/worker/")) {
      const wurl = new URL(url.pathname.slice(7) + url.search, "https://kaynak.ornek");
      const r = await worker.fetch(new Request(wurl, {
        method: istek.method, headers: istek.headers,
        body: ["GET", "HEAD", "OPTIONS"].includes(istek.method) ? undefined : govde
      }), ENV);
      const bas = {}; r.headers.forEach((v, k) => { bas[k] = v; });
      yanit.writeHead(r.status, bas);
      yanit.end(Buffer.from(await r.arrayBuffer()));
      return;
    }
    if (url.pathname === "/r2") { yanit.writeHead(200, { "Content-Type": "application/json" }); yanit.end(JSON.stringify([...R2.keys()])); return; }
    if (url.pathname.startsWith("/sql") && istek.method === "POST") {   /* test düzeneği için doğrudan SQL */
      const r = await havuz.query(govde.toString());
      yanit.writeHead(200, { "Content-Type": "application/json" }); yanit.end(JSON.stringify(r.rows)); return;
    }
    const [durum, veri] = await rest(url.pathname, url.searchParams, istek.method, istek.headers, govde.toString());
    const tekil = (istek.headers["accept"] || "").includes("vnd.pgrst.object");
    const cikti = tekil && Array.isArray(veri) ? veri[0] : veri;
    yanit.writeHead(durum, { "Content-Type": "application/json" });
    yanit.end(JSON.stringify(cikti === undefined ? null : cikti));
  } catch (e) {
    yanit.writeHead(500, { "Content-Type": "application/json" }); yanit.end(JSON.stringify({ message: String(e && e.message) }));
  }
});
sunucu.listen(PORT, "127.0.0.1", () => console.log("taklit sunucu " + KOK));

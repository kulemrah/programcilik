#!/usr/bin/env node
/* ==========================================================================
   İçerik aktarıcı
   icerik/ klasörünü baştan sona doğrular; tek bir hata bile varsa hiçbir
   şey yazmadan durur. Doğrulama geçerse yalnızca değişen konuları,
   ağacı ve görselleri Supabase'e yükler, depodan kaldırılan konuları siler.

   Kullanım:
     node araclar/icerik-aktar.mjs --kuru     yalnızca doğrula (anahtar gerekmez)
     node araclar/icerik-aktar.mjs            doğrula ve yükle
   Ortam değişkenleri (yükleme için):
     SUPABASE_URL             https://xxxx.supabase.co
     SUPABASE_GIZLI_ANAHTAR   sb_secret_... (ya da eski service_role anahtarı)
     TOPLU_SILME=evet         çok sayıda konunun silinmesine izin verir
   Biçimin tarifi: icerik/BICIM.md
   ========================================================================== */

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, dirname, extname } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const KOK = join(dirname(fileURLToPath(import.meta.url)), "..");
const ICERIK = join(KOK, "icerik");
const DERSLER = join(ICERIK, "dersler");
const KURU = process.argv.includes("--kuru");

const KIMLIK = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const DOSYA_ADI = /^(\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*$/;
const GORSEL_ADI = /^[a-z0-9]+(?:-[a-z0-9]+)*\.(svg|png|jpg|jpeg|webp)$/;
const GORSEL_TURU = { svg: "image/svg+xml", png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", webp: "image/webp" };
const GORSEL_SINIRI = 2 * 1024 * 1024;
const SORU_TIPLERI = ["secme", "dy", "bosluk", "dizme", "esles", "izleme", "hesap", "klasik"];

const hatalar = [];
function hata(yer, mesaj) { hatalar.push(yer + ": " + mesaj); }

/* ---------- Küçük yardımcılar ---------- */
function metinMi(d) { return typeof d === "string" && d.trim().length > 0; }
function temizMetin(yer, ad, d, zorunlu = true) {
  if (d === undefined) { if (zorunlu) hata(yer, "'" + ad + "' alanı eksik"); return; }
  if (!metinMi(d)) { hata(yer, "'" + ad + "' boş olmayan bir metin olmalı"); return; }
  if (d !== d.trim()) hata(yer, "'" + ad + "' başında ya da sonunda boşluk var");
}
function bilinmeyenAlanlar(yer, nesne, izinli) {
  Object.keys(nesne).forEach(k => { if (!izinli.includes(k)) hata(yer, "bilinmeyen alan '" + k + "'"); });
}
/* Uygulamadaki kucult() ile aynı: I, İ, ı ve i aynı sayılır */
function kucuk(s) { return s.replace(/[Iİı]/g, "i").toLowerCase(); }
/* Uygulama çizerken bu karakterleri yer tutucu olarak kullanır */
const OZEL_KARAKTER = /[\uE000-\uE002]/;
function jsonOku(yol, yer) {
  let ham;
  try { ham = readFileSync(yol, "utf8"); } catch (e) { hata(yer, "okunamadı"); return null; }
  if (ham.charCodeAt(0) === 0xfeff) { hata(yer, "dosya BOM ile başlıyor"); ham = ham.slice(1); }
  if (ham.includes("\r")) hata(yer, "satır sonlarında CR (\\r) var; LF olmalı");
  try { return JSON.parse(ham); } catch (e) { hata(yer, "geçersiz JSON: " + e.message); return null; }
}
function ozet(veri) { return createHash("sha256").update(JSON.stringify(veri)).digest("hex"); }
/* Satır içi biçim eşleşmesi: uygulama `kod` ve **kalın** işaretlerini satır
   satır çizer; kapanmayan işaret ekranda olduğu gibi (yıldız ya da ters
   tırnak olarak) görünürdü. Kod içindeki yıldızlar (SELECT *) sayılmaz. */
function bicimHatasi(satir) {
  if ((satir.match(/`/g) || []).length % 2) return "kapanmayan ters tırnak (`)";
  if ((satir.replace(/`[^`]*`/g, "").match(/\*\*/g) || []).length % 2) return "kapanmayan kalın işareti (**)";
  return null;
}

/* ---------- 1) Ağaç ---------- */
function agaciDogrula() {
  const yer = "icerik/agac.json";
  const agac = jsonOku(join(ICERIK, "agac.json"), yer);
  const dersler = new Map();
  if (!agac) return { agac: null, dersler };
  bilinmeyenAlanlar(yer, agac, ["gruplar"]);
  if (!Array.isArray(agac.gruplar) || !agac.gruplar.length) { hata(yer, "'gruplar' boş olmayan bir dizi olmalı"); return { agac, dersler }; }
  const kimlikler = new Set();
  const kimlikKaydet = (y, id) => {
    if (typeof id !== "string" || !KIMLIK.test(id)) hata(y, "kimlik '" + id + "' küçük harf, rakam ve tire içermeli");
    else if (kimlikler.has(id)) hata(y, "kimlik '" + id + "' ağaçta birden fazla kez geçiyor");
    kimlikler.add(id);
  };
  const dersleriOku = (y, liste, grup, donem, hususi) => {
    if (!Array.isArray(liste)) { hata(y, "'dersler' bir dizi olmalı"); return; }
    liste.forEach((d, i) => {
      const dy = y + " > dersler[" + i + "]";
      if (!d || typeof d !== "object") { hata(dy, "nesne olmalı"); return; }
      bilinmeyenAlanlar(dy, d, ["id", "ad", "kisa"]);
      kimlikKaydet(dy, d.id);
      temizMetin(dy, "ad", d.ad);
      temizMetin(dy, "kisa", d.kisa, false);
      dersler.set(d.id, { grup, donem, hususi });
    });
  };
  agac.gruplar.forEach((g, i) => {
    const gy = yer + " > gruplar[" + i + "]";
    if (!g || typeof g !== "object") { hata(gy, "nesne olmalı"); return; }
    bilinmeyenAlanlar(gy, g, ["id", "ad", "hususi", "donemler", "dersler"]);
    kimlikKaydet(gy, g.id);
    temizMetin(gy, "ad", g.ad);
    /* Hususi grup yalnızca hususi yetkisi olan hesaplarda görünür */
    if (g.hususi !== undefined && typeof g.hususi !== "boolean") hata(gy, "'hususi' true ya da false olmalı");
    const hususi = g.hususi === true;
    const donemli = g.donemler !== undefined, dogrudan = g.dersler !== undefined;
    if (donemli === dogrudan) { hata(gy, "ya 'donemler' ya da 'dersler' olmalı (ikisi birden değil)"); return; }
    if (dogrudan) { dersleriOku(gy, g.dersler, g.id, null, hususi); return; }
    if (!Array.isArray(g.donemler)) { hata(gy, "'donemler' bir dizi olmalı"); return; }
    g.donemler.forEach((dn, j) => {
      const dny = gy + " > donemler[" + j + "]";
      if (!dn || typeof dn !== "object") { hata(dny, "nesne olmalı"); return; }
      bilinmeyenAlanlar(dny, dn, ["id", "ad", "dersler"]);
      kimlikKaydet(dny, dn.id);
      temizMetin(dny, "ad", dn.ad);
      dersleriOku(dny, dn.dersler, g.id, dn.id, hususi);
    });
  });
  return { agac, dersler };
}

/* ---------- 2) Markdown ---------- */
function markdownDogrula(yer, md, gorseller) {
  const basliklar = [];
  if (md.charCodeAt(0) === 0xfeff) hata(yer, "dosya BOM ile başlıyor");
  if (md.includes("\r")) hata(yer, "satır sonlarında CR (\\r) var; LF olmalı");
  if (!md.trim()) hata(yer, "metin boş");
  const satirlar = md.split("\n");
  let kodIcinde = false, kodBasi = 0, tablo = null;
  satirlar.forEach((satir, i) => {
    const sy = yer + ":" + (i + 1);
    if (OZEL_KARAKTER.test(satir)) hata(sy, "U+E000–U+E002 özel karakterleri kullanılamaz");
    /* Uygulama kod bloğunu yalnızca satır başındaki ``` ile açıp kapatır;
       girintili çit, sonraki her şeyi kodun içine alırdı */
    if (/^\s+```/.test(satir)) { hata(sy, "kod bloğunun açılış ve kapanış çiti (```) satır başında olmalı"); return; }
    if (/^```/.test(satir)) {
      kodIcinde = !kodIcinde; kodBasi = i + 1; tablo = null; return;
    }
    if (kodIcinde) return;
    const bicim = bicimHatasi(satir);
    if (bicim) hata(sy, bicim);
    /* İç içe liste ve alıntı içinde liste çizilmez; düz metin görünürdü */
    if (/^\s+(- |\d+\. )/.test(satir)) hata(sy, "girintili (iç içe) liste kullanılamaz; tek düzey liste yaz");
    if (/^>\s*(- |\d+\. |#{1,6} )/.test(satir)) hata(sy, "alıntı (>) içinde liste ya da başlık kullanılamaz");
    const b = satir.match(/^(#+)\s*(.*)$/);
    if (b) {
      if (b[1].length !== 3 && b[1].length !== 4) hata(sy, "yalnızca ### ve #### başlık kullanılabilir");
      else if (!/^#+ \S/.test(satir)) hata(sy, "başlık işaretinden sonra tek boşluk ve metin olmalı");
      else {
        const metin = b[2].trim();
        if (basliklar.some(x => x.metin === metin)) hata(sy, "'" + metin + "' başlığı bu konuda iki kez geçiyor");
        /* Öğrencinin "mühim" işareti başlık metnine bağlanır; hesaptaki anahtar sınırı aşılmasın */
        if (metin.length > 150) hata(sy, "başlık 150 karakterden uzun olamaz");
        basliklar.push({ seviye: b[1].length, metin });
      }
    }
    if (/^####/.test(satir) && !basliklar.some(x => x.seviye === 3)) hata(sy, "#### başlığından önce bir ### başlığı olmalı");
    /* Tablo: başlık satırı, ayraç satırı, gövde; hepsi aynı sütun sayısında */
    if (/^\|.*\|\s*$/.test(satir)) {
      const hucre = satir.trim().slice(1, -1).split("|").length;
      if (!tablo) tablo = { sutun: hucre, satir: 0 };
      tablo.satir++;
      if (tablo.satir === 2 && !/^\|(\s*:?-{3,}:?\s*\|)+\s*$/.test(satir)) hata(sy, "tablonun ikinci satırı | --- | biçiminde ayraç olmalı");
      if (hucre !== tablo.sutun) hata(sy, "tablo satırı " + hucre + " sütunlu, başlık " + tablo.sutun + " sütunlu");
    } else {
      if (tablo && tablo.satir < 2) hata(yer + ":" + i, "tablo ayraç satırı eksik");
      tablo = null;
    }
    const resimler = satir.matchAll(/!\[([^\]]*)\]\(([^)]*)\)/g);
    for (const r of resimler) {
      if (!r[1].trim()) hata(sy, "görselin açıklaması (alt metni) boş");
      const m = r[2].match(/^gorseller\/(.+)$/);
      if (!m) hata(sy, "görsel yolu 'gorseller/dosya.svg' biçiminde olmalı: " + r[2]);
      else if (!gorseller.has(m[1])) hata(sy, "görsel bulunamadı: " + r[2]);
    }
    if (/^\s*<\s*\/?\s*[a-z]/i.test(satir)) hata(sy, "HTML etiketi kullanılamaz");
  });
  if (kodIcinde) hata(yer + ":" + kodBasi, "kod bloğu kapanmamış");
  return basliklar.map(x => x.metin);
}

/* ---------- 3) Konu JSON'u ---------- */
const KONU_ALANLARI = ["id", "baslik", "kaynak", "kavramlar", "sorular", "kartlar"];
const SORU_ALANLARI = {
  secme:  ["id", "tip", "yer", "soru", "kod", "secenekler", "dogru", "izah"],
  dy:     ["id", "tip", "yer", "ifade", "dogru", "izah"],
  bosluk: ["id", "tip", "yer", "metin", "cevaplar", "izah"],
  dizme:  ["id", "tip", "yer", "soru", "parcalar", "komut", "izah"],
  esles:  ["id", "tip", "yer", "soru", "ciftler", "izah"],
  izleme: ["id", "tip", "yer", "soru", "kod", "secenekler", "dogru", "izah"],
  hesap:  ["id", "tip", "yer", "soru", "cevap", "tolerans", "birim", "izah"],
  klasik: ["id", "tip", "yer", "soru", "cevap", "anahtarlar"]
};

function seceneklerDogrula(y, s) {
  if (!Array.isArray(s.secenekler) || s.secenekler.length < 2 || s.secenekler.length > 6) {
    hata(y, "'secenekler' 2 ile 6 arası metin olmalı"); return;
  }
  s.secenekler.forEach((x, i) => temizMetin(y, "secenekler[" + i + "]", x));
  const tekil = new Set(s.secenekler.map(x => typeof x === "string" ? kucuk(x.trim()) : x));
  if (tekil.size !== s.secenekler.length) hata(y, "aynı seçenek iki kez yazılmış");
  if (!Number.isInteger(s.dogru) || s.dogru < 0 || s.dogru >= s.secenekler.length) hata(y, "'dogru' seçeneklerin sıra numarası (0'dan başlar) olmalı");
}

function soruDogrula(y, s) {
  if (!s || typeof s !== "object") { hata(y, "nesne olmalı"); return; }
  if (!SORU_TIPLERI.includes(s.tip)) { hata(y, "bilinmeyen tip '" + s.tip + "'"); return; }
  bilinmeyenAlanlar(y, s, SORU_ALANLARI[s.tip]);
  if (s.tip !== "klasik" && s.tip !== "dizme" && s.tip !== "esles" && s.tip !== "bosluk") temizMetin(y, "izah", s.izah);
  else temizMetin(y, "izah", s.izah, false);
  switch (s.tip) {
    case "secme":
      temizMetin(y, "soru", s.soru);
      if (s.kod !== undefined && !metinMi(s.kod)) hata(y, "'kod' boş olamaz");
      seceneklerDogrula(y, s);
      break;
    case "izleme":
      temizMetin(y, "soru", s.soru);
      if (!metinMi(s.kod)) hata(y, "'kod' alanı zorunlu: çıktısı sorulan kod ya da akış");
      seceneklerDogrula(y, s);
      break;
    case "dy":
      temizMetin(y, "ifade", s.ifade);
      if (typeof s.dogru !== "boolean") hata(y, "'dogru' true ya da false olmalı");
      break;
    case "bosluk": {
      temizMetin(y, "metin", s.metin);
      if (typeof s.metin !== "string") break;
      if (/_{4,}/.test(s.metin)) hata(y, "boşluk tam olarak üç alt çizgiyle (___) yazılmalı");
      const adet = (s.metin.match(/___/g) || []).length;
      if (!adet) hata(y, "metinde boşluk (___) yok");
      if (!Array.isArray(s.cevaplar) || s.cevaplar.length !== adet) { hata(y, "'cevaplar' her boşluk için bir dizi olmalı (" + adet + " boşluk)"); break; }
      s.cevaplar.forEach((c, i) => {
        if (!Array.isArray(c) || !c.length) { hata(y, "cevaplar[" + i + "] en az bir kabul edilen cevap içermeli"); return; }
        c.forEach((x, j) => temizMetin(y, "cevaplar[" + i + "][" + j + "]", x));
      });
      break;
    }
    case "dizme":
      temizMetin(y, "soru", s.soru);
      if (!Array.isArray(s.parcalar) || s.parcalar.length < 2) hata(y, "'parcalar' doğru sırada en az 2 parça olmalı");
      else s.parcalar.forEach((x, i) => temizMetin(y, "parcalar[" + i + "]", x));
      if (s.komut !== undefined && typeof s.komut !== "boolean") hata(y, "'komut' true ya da false olmalı");
      break;
    case "esles":
      temizMetin(y, "soru", s.soru);
      if (!Array.isArray(s.ciftler) || s.ciftler.length < 2 || s.ciftler.length > 8) { hata(y, "'ciftler' 2 ile 8 arası [sol, sağ] çifti olmalı"); break; }
      s.ciftler.forEach((c, i) => {
        if (!Array.isArray(c) || c.length !== 2) { hata(y, "ciftler[" + i + "] tam olarak [sol, sağ] olmalı"); return; }
        temizMetin(y, "ciftler[" + i + "][0]", c[0]); temizMetin(y, "ciftler[" + i + "][1]", c[1]);
      });
      if (s.ciftler.every(c => Array.isArray(c) && c.length === 2)) {
        if (new Set(s.ciftler.map(c => c[0])).size !== s.ciftler.length) hata(y, "sol sütunda aynı öğe iki kez var");
        if (new Set(s.ciftler.map(c => c[1])).size !== s.ciftler.length) hata(y, "sağ sütunda aynı öğe iki kez var");
      }
      break;
    case "hesap":
      temizMetin(y, "soru", s.soru);
      if (typeof s.cevap !== "number" || !Number.isFinite(s.cevap)) hata(y, "'cevap' bir sayı olmalı");
      if (s.tolerans !== undefined && (typeof s.tolerans !== "number" || !(s.tolerans >= 0))) hata(y, "'tolerans' sıfır ya da pozitif bir sayı olmalı");
      temizMetin(y, "birim", s.birim, false);
      break;
    case "klasik":
      temizMetin(y, "soru", s.soru);
      temizMetin(y, "cevap", s.cevap);
      if (s.anahtarlar !== undefined) {
        if (!Array.isArray(s.anahtarlar) || !s.anahtarlar.length) hata(y, "'anahtarlar' boş olmayan bir dizi olmalı");
        else s.anahtarlar.forEach((x, i) => temizMetin(y, "anahtarlar[" + i + "]", x));
      }
      break;
  }
}

/* JSON'daki bütün metinleri dolaşır: görsel yalnızca .md metninde çizilir */
function jsonMetinleriniDenetle(yer, deger, yol) {
  if (typeof deger === "string") {
    if (/!\[[^\]]*\]\(/.test(deger)) hata(yer, yol + ": görsel yalnızca konu metninde (.md) kullanılabilir");
    if (OZEL_KARAKTER.test(deger)) hata(yer, yol + ": U+E000–U+E002 özel karakterleri kullanılamaz");
    /* "kod" alanı olduğu gibi gösterilir; biçim işareti aranmaz */
    if (!/(^|\.)kod$/.test(yol)) {
      for (const satir of deger.split("\n")) {
        const bicim = bicimHatasi(satir);
        if (bicim) { hata(yer, yol + ": " + bicim); break; }
      }
    }
  } else if (Array.isArray(deger)) deger.forEach((x, i) => jsonMetinleriniDenetle(yer, x, yol + "[" + i + "]"));
  else if (deger && typeof deger === "object") Object.keys(deger).forEach(k => jsonMetinleriniDenetle(yer, deger[k], yol ? yol + "." + k : k));
}

function konuDogrula(yer, konu, basliklar, kimlikler) {
  if (!konu || typeof konu !== "object" || Array.isArray(konu)) { hata(yer, "kök bir nesne olmalı"); return false; }
  jsonMetinleriniDenetle(yer, konu, "");
  bilinmeyenAlanlar(yer, konu, KONU_ALANLARI);
  if (typeof konu.id !== "string" || !KIMLIK.test(konu.id)) { hata(yer, "'id' küçük harf, rakam ve tire içermeli"); return false; }
  if (kimlikler.has(konu.id)) hata(yer, "konu kimliği '" + konu.id + "' başka bir dosyada da var");
  kimlikler.add(konu.id);
  temizMetin(yer, "baslik", konu.baslik);
  temizMetin(yer, "kaynak", konu.kaynak, false);
  const yerDogrula = (y, nesne) => {
    if (nesne.yer === undefined) return;
    if (!basliklar.includes(nesne.yer)) hata(y, "'yer' metindeki bir ### ya da #### başlığıyla birebir aynı olmalı: '" + nesne.yer + "'");
  };
  const altKimlik = (y, nesne, onEk) => {
    if (typeof nesne.id !== "string" || !nesne.id.startsWith(konu.id + ".") ||
        !KIMLIK.test(nesne.id.slice(konu.id.length + 1)) || !nesne.id.slice(konu.id.length + 1).startsWith(onEk)) {
      hata(y, "'id' '" + konu.id + "." + onEk + "1' biçiminde olmalı"); return;
    }
    if (kimlikler.has(nesne.id)) hata(y, "kimlik '" + nesne.id + "' iki kez kullanılmış");
    kimlikler.add(nesne.id);
  };
  ["kavramlar", "sorular", "kartlar"].forEach(ad => {
    if (konu[ad] !== undefined && !Array.isArray(konu[ad])) hata(yer, "'" + ad + "' bir dizi olmalı");
  });
  const terimler = new Set();
  (Array.isArray(konu.kavramlar) ? konu.kavramlar : []).forEach((k, i) => {
    const y = yer + " > kavramlar[" + i + "]";
    if (!k || typeof k !== "object") { hata(y, "nesne olmalı"); return; }
    bilinmeyenAlanlar(y, k, ["terim", "izah", "yer"]);
    temizMetin(y, "terim", k.terim); temizMetin(y, "izah", k.izah);
    if (typeof k.terim === "string") {
      if (terimler.has(kucuk(k.terim))) hata(y, "'" + k.terim + "' terimi iki kez yazılmış");
      terimler.add(kucuk(k.terim));
    }
    yerDogrula(y, k);
  });
  (Array.isArray(konu.sorular) ? konu.sorular : []).forEach((s, i) => {
    const y = yer + " > sorular[" + i + "]";
    if (s && typeof s === "object") altKimlik(y, s, "s");
    soruDogrula(y, s);
    if (s && typeof s === "object") yerDogrula(y, s);
  });
  (Array.isArray(konu.kartlar) ? konu.kartlar : []).forEach((k, i) => {
    const y = yer + " > kartlar[" + i + "]";
    if (!k || typeof k !== "object") { hata(y, "nesne olmalı"); return; }
    bilinmeyenAlanlar(y, k, ["id", "on", "arka", "yer"]);
    altKimlik(y, k, "k");
    temizMetin(y, "on", k.on); temizMetin(y, "arka", k.arka);
    yerDogrula(y, k);
  });
  return true;
}

/* ---------- 4) Ders klasörleri ---------- */
function dersleriOku(agacDersleri) {
  const konular = [], gorseller = [];
  const kimlikler = new Set();
  if (!existsSync(DERSLER)) return { konular, gorseller };
  readdirSync(DERSLER).sort().forEach(ders => {
    const dersYolu = join(DERSLER, ders);
    const dy = "icerik/dersler/" + ders;
    if (!statSync(dersYolu).isDirectory()) { hata(dy, "dersler/ altında yalnızca klasör olmalı"); return; }
    if (!agacDersleri.has(ders)) { hata(dy, "bu ders agac.json'da tanımlı değil"); return; }
    const dersGorselleri = new Map();
    const gorselKlasoru = join(dersYolu, "gorseller");
    if (existsSync(gorselKlasoru)) {
      readdirSync(gorselKlasoru).sort().forEach(ad => {
        const gy = dy + "/gorseller/" + ad;
        if (!GORSEL_ADI.test(ad)) { hata(gy, "görsel adı küçük harf, rakam, tire ve svg/png/jpg/webp uzantısı içermeli"); return; }
        const boyut = statSync(join(gorselKlasoru, ad)).size;
        if (boyut > GORSEL_SINIRI) hata(gy, "görsel 2 MB'tan büyük");
        /* Depodaki ad içeriğin özetiyle başlar: görsel aynı adla değiştirilince
           yeni ad olur, konunun özeti de değişir; cihazlar eski görseli
           önbellekten göstermeye devam etmez. */
        const yolu = join(gorselKlasoru, ad);
        const kisa = createHash("sha256").update(readFileSync(yolu)).digest("hex").slice(0, 10);
        dersGorselleri.set(ad, { yol: yolu, depoAdi: kisa + "-" + ad });
      });
    }
    const dosyalar = readdirSync(dersYolu).filter(a => a !== "gorseller").sort();
    const tabanlar = new Map();
    dosyalar.forEach(ad => {
      const uz = extname(ad), taban = ad.slice(0, -uz.length);
      if ((uz !== ".json" && uz !== ".md") || !DOSYA_ADI.test(taban)) { hata(dy + "/" + ad, "dosya adı 'NN-ad.json' ya da 'NN-ad.md' biçiminde olmalı"); return; }
      if (!tabanlar.has(taban)) tabanlar.set(taban, {});
      tabanlar.get(taban)[uz] = join(dersYolu, ad);
    });
    const siralar = new Set();
    const kullanilanGorseller = new Set();
    tabanlar.forEach((cift, taban) => {
      const y = dy + "/" + taban;
      if (!cift[".json"] || !cift[".md"]) { hata(y, "her konunun hem .json hem .md dosyası olmalı"); return; }
      const sira = Number(taban.slice(0, 2));
      if (siralar.has(sira)) hata(y, "aynı sıra numarası (" + taban.slice(0, 2) + ") iki konuda var");
      siralar.add(sira);
      const md = readFileSync(cift[".md"], "utf8");
      for (const m of md.matchAll(/!\[[^\]]*\]\(gorseller\/([^)]+)\)/g)) kullanilanGorseller.add(m[1]);
      const basliklar = markdownDogrula(y + ".md", md, dersGorselleri);
      const konu = jsonOku(cift[".json"], y + ".json");
      if (!konu || !konuDogrula(y + ".json", konu, basliklar, kimlikler)) return;
      const yuklenecekMetin = md.replace(/(!\[[^\]]*\]\(gorseller\/)([^)]+)\)/g,
        (tum, on, ad) => dersGorselleri.has(ad) ? on + dersGorselleri.get(ad).depoAdi + ")" : tum);
      konular.push({
        id: konu.id, ders, sira, baslik: konu.baslik, metin: yuklenecekMetin, hususi: agacDersleri.get(ders).hususi,
        kavramlar: konu.kavramlar || [], sorular: konu.sorular || [], kartlar: konu.kartlar || [],
        kaynak: konu.kaynak
      });
    });
    dersGorselleri.forEach((g, ad) => {
      if (!kullanilanGorseller.has(ad)) hata(dy + "/gorseller/" + ad, "hiçbir konuda kullanılmıyor");
      gorseller.push({ yol: g.yol, depoYolu: ders + "/" + g.depoAdi, tur: GORSEL_TURU[extname(ad).slice(1)] });
    });
  });
  return { konular, gorseller };
}

/* ---------- 5) Supabase ---------- */
function baglanti() {
  const url = (process.env.SUPABASE_URL || "").replace(/\/+$/, "");
  const anahtar = process.env.SUPABASE_GIZLI_ANAHTAR || "";
  if (!/^https:\/\/[a-z0-9-]+\.supabase\.co$/.test(url) && !/^http:\/\/(127\.0\.0\.1|localhost)(:\d+)?$/.test(url)) {
    throw new Error("SUPABASE_URL tanımlı değil ya da https://xxxx.supabase.co biçiminde değil");
  }
  if (!anahtar) throw new Error("SUPABASE_GIZLI_ANAHTAR tanımlı değil");
  /* Yeni sb_secret_ anahtarı yalnızca apikey başlığında gider; Authorization'a
     konursa JWT sanılıp reddedilir. Eski service_role anahtarı ise JWT'dir. */
  const basliklar = { apikey: anahtar };
  if (anahtar.startsWith("eyJ")) basliklar.Authorization = "Bearer " + anahtar;
  return async function istek(yol, secenek = {}) {
    const cevap = await fetch(url + yol, { ...secenek, headers: { ...basliklar, ...(secenek.headers || {}) } });
    const govde = await cevap.text();
    if (!cevap.ok) throw new Error(secenek.method + " " + yol.split("?")[0] + " → " + cevap.status + " " + govde.slice(0, 400));
    return govde ? JSON.parse(govde) : null;
  };
}

async function yukle(agac, konular, gorseller) {
  const istek = baglanti();
  /* Sunucu tek seferde en çok 1000 satır verir: sayfa sayfa okunur.
     Eksik okunan liste silinecek konuları gözden kaçırırdı. */
  const uzak = [];
  for (let bas = 0; ; bas += 1000) {
    const sayfa = await istek("/rest/v1/konular?select=id,ozet&order=id.asc&limit=1000&offset=" + bas, { method: "GET" });
    uzak.push(...sayfa);
    if (sayfa.length < 1000) break;
  }
  const uzakOzet = new Map(uzak.map(r => [r.id, r.ozet]));
  const yerelKimlikler = new Set(konular.map(k => k.id));
  const simdi = new Date().toISOString();

  const satirlar = konular.map(k => {
    const { kaynak, ...satir } = k;
    return { ...satir, ozet: ozet([k.ders, k.sira, k.baslik, k.metin, k.kavramlar, k.sorular, k.kartlar, k.hususi]), guncellendi: simdi };
  });
  const degisen = satirlar.filter(s => uzakOzet.get(s.id) !== s.ozet);
  const silinecek = uzak.map(r => r.id).filter(id => !yerelKimlikler.has(id));

  /* Toplu silme koruması: depo bir hata yüzünden boş okunduysa her şey silinmesin */
  if (silinecek.length) {
    const toplu = !konular.length || (silinecek.length > 3 && silinecek.length > uzak.length / 2);
    if (toplu && process.env.TOPLU_SILME !== "evet") {
      throw new Error(silinecek.length + " konu silinecekti (" + silinecek.slice(0, 10).join(", ") +
        "). Bu bilerek yapıldıysa TOPLU_SILME=evet ile yeniden çalıştır.");
    }
  }

  for (const g of gorseller) {
    const yol = "/storage/v1/object/gorseller/" + g.depoYolu.split("/").map(encodeURIComponent).join("/");
    await istek(yol, { method: "POST", headers: { "Content-Type": g.tur, "x-upsert": "true", "Cache-Control": "max-age=3600" }, body: readFileSync(g.yol) });
  }
  console.log("Görsel: " + gorseller.length + " yüklendi");

  for (let i = 0; i < degisen.length; i += 50) {
    await istek("/rest/v1/konular?on_conflict=id", {
      method: "POST",
      headers: { "Content-Type": "application/json", Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify(degisen.slice(i, i + 50))
    });
  }
  console.log("Konu: " + degisen.length + " güncellendi, " + (satirlar.length - degisen.length) + " aynı");

  /* Ağaç iki satıra bölünür: 1 herkesin gördüğü gruplar, 2 hususi gruplar.
     Konular (hususi işaretiyle) ağaçtan önce yüklendiği için, hususiye
     alınan bir grup hiçbir an yetkisiz hesaba açık kalmaz. */
  const agacSatirlari = [
    { id: 1, veri: { gruplar: agac.gruplar.filter(g => g.hususi !== true) } },
    { id: 2, veri: { gruplar: agac.gruplar.filter(g => g.hususi === true) } }
  ].filter(r => r.id === 1 || r.veri.gruplar.length);
  const uzakAgac = new Map((await istek("/rest/v1/agac?select=id,ozet", { method: "GET" })).map(r => [r.id, r.ozet]));
  const degisenAgac = agacSatirlari
    .map(r => ({ ...r, ozet: ozet(r.veri), guncellendi: simdi }))
    .filter(r => uzakAgac.get(r.id) !== r.ozet);
  if (degisenAgac.length) {
    await istek("/rest/v1/agac?on_conflict=id", {
      method: "POST",
      headers: { "Content-Type": "application/json", Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify(degisenAgac)
    });
  }
  if (uzakAgac.has(2) && !agacSatirlari.some(r => r.id === 2)) {
    await istek("/rest/v1/agac?id=eq.2", { method: "DELETE", headers: { Prefer: "return=minimal" } });
  }
  console.log("Ağaç: " + (degisenAgac.length ? "güncellendi (" + degisenAgac.map(r => r.id === 1 ? "genel" : "hususi").join(", ") + ")" : "aynı") +
    (uzakAgac.has(2) && !agacSatirlari.some(r => r.id === 2) ? ", hususi ağaç silindi" : ""));

  /* Adres çok uzamasın diye silme 100'er konuluk parçalarla yapılır */
  for (let i = 0; i < silinecek.length; i += 100) {
    await istek("/rest/v1/konular?id=in.(" + silinecek.slice(i, i + 100).map(encodeURIComponent).join(",") + ")", {
      method: "DELETE", headers: { Prefer: "return=minimal" }
    });
  }
  console.log("Silinen konu: " + silinecek.length + (silinecek.length
    ? " (" + silinecek.slice(0, 20).join(", ") + (silinecek.length > 20 ? ", …" : "") + ")" : ""));
}

/* ---------- Akış ---------- */
const { agac, dersler } = agaciDogrula();
const { konular, gorseller } = agac ? dersleriOku(dersler) : { konular: [], gorseller: [] };

if (hatalar.length) {
  console.error(hatalar.length + " hata bulundu, hiçbir şey yüklenmedi:\n");
  hatalar.forEach(h => console.error("  • " + h));
  process.exit(1);
}

const soruSayisi = konular.reduce((t, k) => t + k.sorular.length, 0);
const kartSayisi = konular.reduce((t, k) => t + k.kartlar.length, 0);
const hususiSayisi = konular.filter(k => k.hususi).length;
console.log("Doğrulama tamam: " + dersler.size + " ders, " + konular.length + " konu" + (hususiSayisi ? " (" + hususiSayisi + " hususi)" : "") + ", " +
  soruSayisi + " soru, " + kartSayisi + " kart, " + gorseller.length + " görsel");

if (!KURU) {
  try { await yukle(agac, konular, gorseller); }
  catch (e) { console.error("Yükleme durdu: " + e.message); process.exit(1); }
}

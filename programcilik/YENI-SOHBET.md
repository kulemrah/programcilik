# Yeni sohbet: buradan başlayın

**Proje:** "Kostü - Ders" (uygulama içi başlık "Bilgisayar Programcılığı"): KOSTÜ Bilgisayar Programcılığı sınıfı için ders notu (Kıraat), soru (Temrin), kart (42 Tarzı), kişisel not (Notlar) PWA'sı. Depo `kulemrah/programcilik` → `https://kulemrah.github.io/programcilik/`. Arka uç: Supabase (giriş, içerik, kayıtlar) + Cloudflare Worker/R2 (Notlar resimleri).

Bu dosya kısa haritadır. Ayrıntı `DEVIR-NOTU.md`'de: yalnızca işin gerektirdiği bölümü okuyun (bölüm numaraları aşağıda).

## 1. Sohbete ekleyin

| Dosya | Ne için | Nereye açılır |
| --- | --- | --- |
| `programcilik-son.zip` | Projenin bütün son hâli (testler dahil; ekran görüntüleri ve ara çıktılar hariç) | `/home/claude/` (içinden `programcilik/` çıkar) |
| `elektrik-devam.zip` | Yalnızca Elektrik dersine devam edilecekse | `/home/claude/` (`elektrik-is/` çıkar) |
| İşlenecek ders PDF'i/PPTX'i | Yeni ders notu için | eklendiği yer |

İlk komut: `cd /home/claude && unzip -q programcilik-son.zip` (`-q`: dosya dosya yazmadan, sessiz açar).

## 2. Çalışma kuralları

- Türkçe; Hamza'ya ve uygulamada öğrenciye **"siz"**.
- **Hata payı yok** (sınav konusu): uydurma yok, hocanın ifadesi korunur; slayt hatası **Dikkat** kutusunda düzeltilir, slaytta olmayan bilgi **Ek** kutusuna gider.
- Algoritma'da **C++ yok** (derste henüz girilmedi). Yalnızca hocanın kendi slaytlarındaki C++ kalır.
- Teslimde **yalnızca değişen dosyalar**, depodaki yollarıyla zip (`guncelleme-NN.zip`; son verilen **39**).
- Verilen **her komut açıklanır**: ne yapar, bayraklar/işaretler, beklenen çıktı.
- Hamza'nın kararları **🔶 Sizin karar vermeniz gerekenler** başlığıyla, belirgin.
- Plan/rehber belgelerinde yalnızca son durum yazılır.
- Sırlar (Supabase gizli anahtar, Resend anahtarı) sohbete yazdırılmaz.
- **Limit az harcanır:** `index.html`'i bütün okumayın; aşağıdaki haritayla ilgili bölümü bulup o aralığı okuyun.
- Elektrik'in kalanı yalnızca Hamza "devam" deyince.

## 3. Neyi nerede bulursunuz

```
programcilik/
├── YENI-SOHBET.md            ← bu dosya
├── DEVIR-NOTU.md             ← ayrıntı: §2 canlı kurulum, §3 teslimler, §4 açık işler,
│                                §6 içerik tablosu ve kurallar, §7 Elektrik, §8 uygulama mimarisi, §9 testler
├── KURULUM.md                ← canlı kurulum adımları, günlük kullanım, Kaynak (R2), Yedek
├── .github/workflows/
│   ├── yayimla.yml           ← uygulama/** değişince → GitHub Pages
│   └── icerik.yml            ← icerik/** veya araclar/** değişince → doğrula + Supabase'e yükle
├── icerik/
│   ├── ISLEME.md             ← ders işleme kademeleri K0–K13 (yeni not işlemeden önce oku)
│   ├── BICIM.md              ← .md/.json biçimi, soru türleri, görseller, "Sınav takvimi"
│   ├── agac.json             ← sınıf/dönem/ders ağacı + sinavlar listesi
│   ├── dersler/<ders>/       ← NN-ad.md (not) + NN-ad.json (kavram/soru/kart) + gorseller/
│   └── envanter/<ders>.md    ← slayt slayt döküm, sorunlar, kararlar (uygulamaya gitmez)
├── araclar/
│   ├── icerik-aktar.mjs      ← doğrula (--kuru) ve Supabase'e yükle (konular, agac; sınavlar dahil)
│   ├── icerik-denetle.py     ← soru kalitesi uyarıları
│   └── sekiller/<ders>.py    ← SVG/görsel üreticiler (donanim-kaynak/ = fotoğraf kaynakları)
├── uygulama/
│   ├── index.html            ← tek dosya uygulama (~12.400 satır; harita §4)
│   ├── sw.js                 ← önbellek programcilik-v25 (index.html değişince +1)
│   ├── supabase.js, manifest.webmanifest, kostu-*.png, webp/ (iPhone WebP kodlayıcı)
├── supabase/01-sema.sql      ← tekrar çalıştırılabilir tam şema (8. bölüm: Notlar/Kaynak)
├── kaynak-worker/            ← worker.js (R2 + kota), wrangler.toml
└── test/
    ├── tarayici/*_sina.py    ← Playwright testleri; yardim/hepsi.sh hepsi, yardim/sunucu.sh site (8765)
    ├── gercek/sahte_supa.py  ← aktarıcıyı yükleyen taklit Supabase (8799) → cikti/yuklenen.json
    ├── sql/, kaynak/         ← şemanın yerel PostgreSQL denemesi, Notlar taklit sunucusu
```

Ders kimlikleri: `algoritma`, `veritabani`, `donanim`, `aglar`, `elektrik`, `ekoloji` (1. Sınıf › Güz; hepsi Bilgisayar Programcılığı); `born2beroot` (42, hususi). Bölümler `agac.json › programlar`'da; şu an yalnızca `bilgisayar-programciligi` (`bp`).

## 4. index.html haritası

Bölümleri bulmak (dosyayı okumadan):
```
grep -n "^/\* ----------\|^/\* ----" uygulama/index.html
```
`grep -n` eşleşen satırları satır numarasıyla yazar; desen, bölüm başlığı yorumlarını (`/* ---------- Ad`) yakalar. Ardından Read ile yalnızca o aralık okunur.

| Satır (yaklaşık) | Ne var |
| --- | --- |
| 16–46 | `<head>` betiği: ölçek ve tema ilk boyamadan önce |
| 47–2168 | CSS (ikinci yarısı 1484'ten itibaren yeni görünüm; çekmece 1778, sınavlar 1949, Bu cihaz 1968, Notlar 2014, not editörü 2113) |
| 2193 | Yapılandırma (`AYAR`, Supabase, `KAYNAK_URL`) |
| 2252 / 2322 | Bu cihaz (ölçek, cihaz türü) / Alt kısayolları |
| 2523 / 2551 | Tema / göz koruyucu |
| 3395–3740 | İçerik eşitleme (`icerikEsitle`, `AGAC`), kayıtlar gönder/çek, çıkış |
| 4572–5420 | Çekmece: toplama, çizelgeler, takvimler, **sınav takvimi (5216)** |
| 7051–7612 | Ders ağacı, görseller, konu okuma, sesli okuma |
| 8587–9540 | Temrin: yanlış defteri, kök, kapsam, soru oturumu |
| 9540–10330 | 42 Tarzı (`kartSayfasiCiz`, `kartOturumu` 9693, sürükleme) |
| 10332–11690 | Notlar (sıra, gönderim, silme, süzgeç, resimler, ekran, Hesap kutusu) |
| 11693– | Not editörü |

Arama için işlev adları: `GUNCELLEMELER` (yama notları; yeni sürümde başa eklenir), `SEKMELER`, `cekmeceSurukleKur`, `altCubukKaydirmaKur`, `sinavBolumu`, `takvimBolumu`, `cihazBolumu`, `ekranOrani`, `geriAdimi`, `kaynakGonder`.

## 5. Sık işler

**Yeni sınav:** `icerik/agac.json › sinavlar`'a bir satır:
`{ "ders": "aglar", "ad": "1. Kısa Sınav", "zaman": "2026-11-06T21:30+03:00", "lms": true }` (Sınav Modülü'nde ise `"modul": true`; uygulamada olmayan ders için `"dersAdi": "..."` ve `ders` yok) (+ isteğe bağlı `"yer"`, `"not"`). Sonra `node araclar/icerik-aktar.mjs --kuru`; `test/tarayici/sinav_sina.py`'nin 1. kontrolü gerçek listeyi beklediği için o satır da güncellenir.

**Yeni bölüm** (Hamza adını ve derslerini verir): `agac.json › programlar`'a `{ "id", "ad", "onek", "sinifSayisi" }`; ortak derslerin `programlar` listesine bölüm eklenir, yeni dersler o bölümle açılır; `--kuru`. Kodu Hamza İdare'den üretir (KURULUM.md "Bölüm kodları"). Sınav takvimi yalnızca BP 1. sınıfa gider.

**Yeni ders notu:** ISLEME.md'yi oku → envanter → plan → `.md` → şekiller (358 px'te bak) → `.json` (10–18 soru, 4–9 kart) → `--kuru` + `icerik-denetle.py` → taklit yükleme + ders testi + `tum_sorular_sina.py` → bağımsız denetim ajanı → teslim + 🔶.

**Uygulama değişikliği:** `index.html` + `sw.js` sürümü +1; yeni özellikse `GUNCELLEMELER`'e not; ilgili test + `cihaz_sina.py` (yama notu sürümünü bekler).

**Test hazırlığı** (ayrıntı DEVIR-NOTU §9):
```
su pgk -c "/usr/lib/postgresql/16/bin/pg_ctl -D /home/claude/pgdeneme/veri -o '-p 5499 -k /tmp' -l /home/claude/pgdeneme/log start"
cd /home/claude/programcilik
(python3 test/gercek/sahte_supa.py test/gercek/cikti 8799 >/dev/null 2>&1 &)
SUPABASE_URL=http://127.0.0.1:8799 SUPABASE_GIZLI_ANAHTAR=x node araclar/icerik-aktar.mjs; fuser -k 8799/tcp
cd test/tarayici && sh kur.sh && (sh yardim/sunucu.sh >/dev/null 2>&1 &)
python3 <test>_sina.py
```
Yeni konteynerde PostgreSQL kurulu değilse ya da `pgk` kullanıcısı yoksa: DEVIR-NOTU §9.3'teki `useradd`/`initdb` adımları. `kaynak`, `notlar_editor`, `cihaz` testleri PostgreSQL ister.

## 6. Durum (4 Kasım 2026)

- Son teslimler: guncelleme-31…39, algoritma-hafta-5, algoritma-hafta-6. GitHub'a yüklendiği **teyit edilmedi** (DEVIR-NOTU §3). `programcilik-son.zip` bütün bunları kapsar.
- Sınav listesinde: Veritabanı ve Ağlar 1. Kısa Sınav (6 Kasım 20:30 / 21:30, LMS), Algoritma Sınavı (9 Kasım 20:00, Sınav Modülü), Ekoloji 1. Kısa Sınav (10 Kasım 19:00, LMS), Matematik Kısa Sınavı (10 Kasım 20:30, Sınav Modülü).
- 🔶 Bekleyen kararlar: DEVIR-NOTU §4 (göz koruyucu yenilemesi, sınav listesi ayrıntıları, Algoritma 5. hafta soruları, hocaya sorulacaklar, eski kararlar).

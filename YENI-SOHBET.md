# Yeni sohbet: buradan başlayın

**Proje:** "Kostü - Ders": KOSTÜ Bilgisayar Programcılığı sınıf arkadaşları için ders notu, temrin (soru) ve 42 Tarzı (kart) PWA'sı. Depo `kulemrah/programcilik` (GitHub Pages + Supabase). Ayrıntı: `DEVIR-NOTU.md`.

## Sohbete ekleyin

| Dosya | Ne için |
| --- | --- |
| `programcilik-son.zip` | Projenin son hâli. Çalışma yeri: `/home/claude/programcilik` |
| `test-son.zip` | Tarayıcı testleri. `/home/claude/programcilik/test/` altına açılır |
| `elektrik-devam.zip` | Yalnızca Elektrik dersine devam edilecekse |
| İşlenecek ders PDF'i/PPTX'i | Yeni ders notu için |

## Çalışma kuralları (kısa)

- Türkçe, "siz" hitabı. Hata payı yok; hocanın ifadesi korunur; slayt hatası Dikkat kutusunda, dayanaksız bilgi Ek kutusunda.
- Teslimde yalnızca değişen dosyalar, depodaki yollarıyla zip.
- Her komut açıklanır (ne yapar, bayraklar, beklenen çıktı).
- Kararlar **🔶 Sizin karar vermeniz gerekenler** başlığıyla.
- Sırlar sohbete yazdırılmaz. Limit az harcanır.

## Neyi nerede bulursunuz

```
programcilik/
├── DEVIR-NOTU.md            ← ayrıntılı durum, açık işler, mimari, testler
├── KURULUM.md               ← canlı kurulum ve günlük kullanım
├── icerik/
│   ├── ISLEME.md            ← ders işleme kademeleri K0–K13 (her yeni not için oku)
│   ├── BICIM.md             ← dosya biçimi, soru türleri, görsel/dizi/soru görseli
│   ├── agac.json            ← dersler: algoritma, veritabani, donanim, aglar, elektrik, ekoloji (+ 42: born2beroot)
│   ├── dersler/<ders>/      ← NN-ad.md (not) + NN-ad.json (kavram/soru/kart) + gorseller/
│   └── envanter/<ders>.md   ← slayt slayt döküm + sorunlar tablosu
├── araclar/
│   ├── icerik-aktar.mjs     ← doğrula (--kuru) / yükle
│   ├── icerik-denetle.py    ← kalite denetimi
│   └── sekiller/<ders>.py   ← şekil/görsel üreticiler (donanim-kaynak/ = fotoğraf kaynakları)
├── uygulama/index.html      ← tek dosya uygulama (sw.js önbellek: programcilik-v18)
├── kaynak-worker/           ← Kaynak resimleri için Cloudflare Worker (R2, kota)
├── supabase/01-sema.sql
└── test/tarayici/*_sina.py  ← Playwright testleri; yardim/hepsi.sh hepsini çalıştırır
```

## Yeni ders notu işleme akışı

1. Kaynağı oku. Her slayt bir satır olarak `icerik/envanter/<ders>.md`'ye yazılır.
2. Konu ve başlık planı (konu başına 5–15 başlık).
3. `.md` notlar.
4. Şekiller (`araclar/sekiller/<ders>.py`; 358 px'te bakılır).
5. `.json`: kavram, 10–18 soru, 4–9 kart.
6. Denetim komutları:
   ```
   node araclar/icerik-aktar.mjs --kuru
   python3 araclar/icerik-denetle.py icerik/dersler/<ders>
   ```
7. Taklit sunucuya yükleme + `<ders>_sina.py` + `tum_sorular_sina.py`.
8. Bağımsız denetim ajanı (yalnızca slaytları ölçüt alır).
9. Teslim: değişen dosyalar + rapor + 🔶.

## Şu an açık olanlar

- **Elektrik:** konu 01–15 yayında; 16–23 (P09–P14) kalan. Yalnızca Hamza "devam" deyince.
- **Hocaya sorulacaklar:**
  - Veritabanı konu 14 (iç içe SELECT)
  - Ağlar: A sınıfı 0–126 / 1–126; ODTÜ/IANA ifadesi
  - Donanım: numaralı resimde 3; arka panelde 4 ve 6
- **Kaynak (R2):** kod hazır, kurulum bekliyor (KURULUM.md "Kaynak (R2)": şema, Cloudflare hesabı, kova, Worker, `AYAR.KAYNAK_URL`).
- **Teyit bekleyen:**
  - GitHub'a yükleme: `programcilik-son.zip` bütün paketleri kapsar.
  - Supabase e-posta gönderen adı ve şablonları.
  - Gerçek telefonda deneme.

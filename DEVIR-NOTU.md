# Devir notu: "Kostü - Ders" (Bilgisayar Programcılığı ders notları PWA'sı)

Yeni sohbete geçiş içindir. Önce `YENI-SOHBET.md`'yi okuyun (kısa harita); bu not ayrıntıdır.

## 1. Kullanıcı ve çalışma biçimi

- Hamza; KOSTÜ (Kocaeli Sağlık ve Teknoloji Üniversitesi) Bilgisayar Programcılığı 1. sınıf ve 42 öğrencisi. Her şey Türkçe. Hamza'ya ve uygulamada öğrenciye **"siz"** diye hitap edilir.
- **Hata payı yok:** okul sınav konuları. İçerikte uydurma yok, hocanın ifadesi korunur; slayttaki hata Dikkat kutusunda düzeltilir, dayanaksız bilgi Ek kutusuna gider.
- Hamza'nın vermesi gereken kararlar **🔶 Sizin karar vermeniz gerekenler** başlığıyla ayrı ve belirgin yazılır.
- Güncellemede **yalnızca değişen dosyalar** verilir (zip içinde depodaki yollarıyla).
- Verilen her komut açıklanır: ne yapar, bayrakları ve işaretleri (`|` gibi) ne demek, beklenen çıktı ne.
- Plan ve rehber belgelerinde yalnızca son durum yazılır.
- Sırlar (secret key, Resend anahtarı) asla sohbete yazdırılmaz.
- Limit tasarrufu önemli: gereksiz ekran görüntüsü, tekrar okuma ve uzun döküm yapılmaz.
- Elektrik dersinin kalanı (aşağıda 7) yalnızca Hamza "devam" deyince yapılır.

## 2. Canlı kurulum

| Parça | Değer |
| --- | --- |
| Site | `https://kulemrah.github.io/programcilik/` (GitHub Pages, iş akışıyla) |
| Depo | `kulemrah/programcilik`, herkese açık (GitHub Pro gelince private; adres değişmez) |
| Git | SSH anahtarı `~/.ssh/id_ed25519_kulemrah`, depo içi `core.sshCommand`; yazar `kulemrah` + noreply e-posta |
| Supabase | Proje `nzhruevikugpmyoozpyc` (Free, org `yuksek_okul`, hesap birkulemrah@gmail.com) |
| GitHub sır/değişken | `SUPABASE_URL` (Variables), `SUPABASE_GIZLI_ANAHTAR` (Secrets) |
| Kanca | Before User Created → `public.kayit_kapisi` (yalnız @kocaelisaglik.edu.tr) |
| E-posta | Resend, alan `posta.eskimezyazi.app` (Verified). Gönderen `giris@posta.eskimezyazi.app` |
| OTP | 6 hane, 900 sn; iki kod arası 60 sn |
| Tashih adresi | birkulemrah@gmail.com |
| Uygulama adı | Ana ekranda **Kostü - Ders**; uygulama içi başlık **Bilgisayar Programcılığı** |
| Şema | `supabase/01-sema.sql` (sözleşme sürümü 2, kayıt türü `calisma`; 8. bölüm Kaynak: `kaynak_kota`, `kaynak_tasnif`, `kaynak_oge` — notta `baslik`, `bicim`, resimde `not_id`) |
| Notlar / Kaynak (R2) | **Kuruldu (2 Kasım 2026).** Uygulamadaki adı **Notlar**, iç adı `kaynak`. Cloudflare hesabı birkulemrah@gmail.com, kova `kostu-kaynak`, Worker `https://kostu-kaynak.kostu.workers.dev` (`kaynak-worker/`, workers.dev alt alanı `kostu`), Worker sırrı `SUPABASE_GIZLI_ANAHTAR`. `AYAR.KAYNAK_URL` bu adres. Kişi başı hak `kaynak_kota.azami_mb` (öntanımlı 100). Şemayı ve Worker'ı değiştiren güncellemede sıra: SQL → `npx wrangler deploy` → uygulama |

## 3. Teslim durumu

- **Çalışma kopyasının son hâli `programcilik-son.zip`'tedir** (4 Kasım 2026; guncelleme-36 ve algoritma-hafta-6'ya kadar her şey). GitHub'daki depo bu hâle getirilmelidir; aradaki paketlerin hiçbirinin yüklendiği teyit edilmedi. Paket, test ekran görüntülerini (`test/tarayici/*.png`), test sitesini (`site/`), aktarıcı çıktısını (`test/gercek/cikti/`) ve `node_modules`'ü içermez; bunlar testlerde yeniden üretilir.
- Paketlerin sırası (hepsi teslim edildi; yüklendiği teyit edilmedi):
  - guncelleme-31: Kaynak → **Notlar**; bağlantısız sıra, 5 sn geri al, iki sütunlu kutucuklar, + menüsü, biçimli not editörü, Hesap › Notlar › Resimler. **Şema ve Worker değişti:** önce SQL Editor'de `01-sema.sql`, sonra `kaynak-worker`'da `npx wrangler deploy`, sonra uygulama.
  - guncelleme-32/33: Hesap › Bu cihaz (Bilgisayar/Tablet/Telefon, ölçek), alt çubukta ve çekmecede kaydırarak geçiş, Alt kısayolları, geniş ekranda "Derslere göre süre" düzeltmesi; ölçek üst başlık ve alt çubuğu etkilemez; çekmecede ters yön; yama notu s2.1 ve Hesap › Yama Notları. Hamza telefonda denedi: alt çubuk kaydırması ve Alt sorunsuz.
  - algoritma-hafta-5: Algoritma konu 11–13 (KDV ve denklem, sayaç, sayaç örnekleri; Ek akış şemaları); bütün Algoritma notlarından C++ ekleri kaldırıldı. Yalnızca içerik.
  - guncelleme-34: sınav takvimi (menü › Takvim'in altı; `agac.json › sinavlar`), yama notu s2.2, sw v22.
  - guncelleme-35: Ekoloji 1. Kısa Sınav eklendi (yalnızca `agac.json` + `sinav_sina.py`).
  - algoritma-hafta-6: Algoritma konu 14–15 (Akış Diyagramları, Akış Diyagramı Örnekleri; hocanın sembolleri ve 9 akış diyagramı); 5. haftanın 3 Ek akış şeması hocanın sembolleriyle yeniden çizildi (ISO sembol şekli kaldırıldı); 02, 04, 07, 09, 10, 11, 12, 13. konularda 6. haftaya göre düzeltmeler (çok durumlu kararda hocanın "adıma git" yolu, Örnek 2 ve 4'ün hocanın çözümü). Yalnızca içerik.
  - guncelleme-37: Algoritma Sınavı (9 Kasım) ve Matematik Kısa Sınavı (10 Kasım) eklendi; sınav satırına `modul` (Sınav Modülü cümlesi) ve `dersAdi` (ağaçta olmayan ders) alanları; sw v24.
  - guncelleme-36: Temrin'de "Bilmiyorum" (klasik ve kavram kartları hariç her tür; yanlış sayılır, doğrusu gösterilir), yazım hoşgörüsü (`cevapTutar`, `metindeGeciyor`: büyük/küçük, ı/i ve Türkçe harf farkı; 5–7 harfte 1, 8+ harfte 2 harf hatası; ilk harf, rakam ve işaretler tam tutmalı; 4 harf ve altı tam), ilerleme çubuğu düzeltmesi (`.dolu` satır içi olduğu için genişlik almıyordu), notta ilgili bölümün yanıp sönmesi (`bolumuYak`) ve başlığın üst çubuğun altında kalmaması; yama notu s2.3, sw v23.
- Depoda `uygulama/ikon-*.png` ya da `uygulama/apple-touch-icon.png` kaldıysa `git rm` ile silinir (guncelleme-24'te kaldırıldılar).
- Sınav listesi şu an: Veritabanı 1. Kısa Sınav 6 Kasım 20:30 ve Ağlar 1. Kısa Sınav 6 Kasım 21:30 (LMS); Algoritma "Sınav" 9 Kasım 20:00–21:00 (10 soru, 20 dk, %10; KOSTÜ Sınav Modülü); Ekoloji 1. Kısa Sınav 10 Kasım 19:00 (10 soru, 10 dk, 19:00–20:00 açık; LMS); Matematik I ve Genel Matematik Kısa Sınavı 10 Kasım 20:30 (KOSTÜ Sınav Modülü; ağaçta olmayan ders, `dersAdi`).

## 4. 🔶 Açık kalanlar

### 4.1 Hamza'nın kararını bekleyenler (yeni)

1. **Göz koruyucu yenilemesi:** şimdiki mod ekranın önüne sıcak renkli (turuncu) yarı saydam bir katman koyar (3 kademe). Kanıta göre mavi ışık süzmenin göz yorgunluğuna etkisi zayıf (Cochrane 2023); gerçekten işe yarayanlar 20-20-20 molası, göz kırpma, parlaklığı/parlamayı azaltmak, okuma rahatlığı. Önerilip **karar bekleyenler:**
   - 20-20-20 mola hatırlatıcısı (20 dk'da bir "20 sn uzağa bakın") ve göz kırpma hatırlatıcısı: aralığı ne olsun, kapatılabilsin mi?
   - Turuncu katmanın yerine siyah karartma kaydırıcısı mı, ikisi birlikte mi?
   - Okuma rahatlığı ayarları (kontrast, satır aralığı, yazı boyu).
   - Akşam otomatik açılma.
   Hiçbiri yapılmadı.
2. **Sınav listesi:** (a) günü geçen sınav şimdi gizleniyor; gri hâlde kalsın mı? (b) hocanın adı da yazsın mı?
3. **Algoritma 5. ve 6. hafta:**
   - Çözüm belgelerinin (`bp_5_hafta.pdf`, `6_hafta_blp.pdf`) yazarı "laboratuvar" mı, hoca mı? Notta "hocanın çözümü" yazıyor.
   - 5. hafta slaytlarının "_2" kısmı gelmedi; 6. hafta dosyası "_3" ile bitiyor. Eksik parça varsa işlenecek.
   - Hocaya sorulacaklar: KDV/denklem çözümünde `delta^1/2` ve `/2*a` yazımı (işlem önceliği), en büyük sayı çözümündeki `yenienbuyuk` hatası, üçgen çözümünde metin (iki ayrı Eğer) ile akış diyagramının 3, 3, 3 girişinde farklı sonuç vermesi (notlarda Dikkat ile açıklandı, hocanınki korundu).
4. **Algoritma konu 02:** hocanın kendi slaytlarındaki C++ bölümleri (dil seviyeleri, "Neden C++") şimdilik duruyor; Hamza kaldırılmasını isterse kaldırılır.
5. **Bu cihaz:** Tablet ve Telefon modlarının ayrı davranışı henüz yok (yalnızca Bilgisayar'da Alt kısayolları); ne farklı olsun?
6. **guncelleme-31'den:** Notlar'da sıralama (şimdi en son değişen üstte), içi dolu tasnif silme onayı, öntanımlı kota (100 MB), + menüsünün etiketleri; Hamza denedikten sonra değiştirmek isterse.

### 4.2 Eski açıklar

1. **Kod e-postası paneli:** Supabase SMTP **Sender name** `Kostü - Ders` ve iki şablon (Confirm sign up, Magic link or OTP) KURULUM.md bölüm 2'ye göre güncellenecek; yapıldığı teyit edilmedi.
2. **GitHub Pro:** öğrenci başvurusu bekleniyor; gelince depo private yapılacak.
3. **Hocaya sorulacaklar:**
   - Veritabanı konu 14, iç içe SELECT sorusu (envanter K5 slayt 10).
   - Ağlar: A sınıfı ilk oktet "0–126" mı "1–126" mı (notta 1–126 + Dikkat); slayt 17'deki ODTÜ/IANA ifadesi.
   - Donanım: numaralı resimde 3 numara (resimde PCI Express x16, bağlantısı AGP slaytına); arka panel resminde 4 ve 6.
4. **Kararı bekleyen:** Donanım'daki ASUS A8N-SLI resminin üç etiketi resmin üzerinde düzeltildi (bkz. 6.3); Hamza özgünü isterse geri alınır.
5. **Bekleyen eski kararlar:** dondurma birikmesine üst sınır (şimdi yok), koyu temada beyaz saat kartları, iPhone'da yeni ikon için uygulamanın ana ekrana yeniden eklenmesi.
6. **guncelleme-31'in sırası:** SQL Editor'de `01-sema.sql`, sonra `kaynak-worker`'da `npx wrangler deploy`, sonra uygulama. Yapıldığı teyit edilmedi.
7. İsteğe bağlı: Supabase'in R2 yedeği kurulmadı (KURULUM.md "Yedek"); Kaynak resimlerinin tek kopyası R2'dedir.
8. Silinen hesapların R2'deki resimlerini temizleyecek yönetici komutu yazılmadı.
9. Gerçek cihazda denenmedi: Android/iPhone'da menü kapanması, Brave'de oturum, yana kaydırılan resimler ve büyüteç; her sekmenin kendi geri geçmişi (özellikle Kıraat kökündeki çıkış uyarısı); Notlar'da iPhone'dan resim ekleme (WebAssembly kodlayıcı); not editöründe klavye üstü çubuk (visualViewport), Gboard/iOS klavyesiyle "- " kısayolu, biçim düğmelerine dokununca klavyenin açık kalması; alt çubukta kaydırma (Android hareketli gezinmede alt kenar), ölçekle (zoom) yerleşim, kurulu masaüstü uygulamasında Alt'ın pencere menüsünü açmaması.

## 5. Depo düzeni

```
.github/workflows/   icerik.yml (doğrula + Supabase'e aktar), yayimla.yml (uygulama/ → Pages)
araclar/
  icerik-aktar.mjs   içeriği doğrular ve yükler (--kuru: yalnız doğrula)
  icerik-denetle.py  kalite uyarıları (en uzun doğru şık, D/Y dengesi, sınav tahmini...)
  sekiller/<ders>.py SVG/görsel üreticiler: algoritma, veritabani, ekoloji, elektrik, aglar, donanim
  sekiller/donanim-kaynak/  Donanım fotoğraflarının kaynakları (slaytlardan + Hamza'nın 2 resmi)
icerik/
  ISLEME.md          PDF → not/temrin/kart işleme kademeleri K0–K13 (kurallar burada)
  BICIM.md           dosya biçimi (Markdown kuralları, soru türleri, görseller, soru görselleri)
  agac.json          sınıf/dönem/ders ağacı
  dersler/<ders>/    NN-ad.md (not) + NN-ad.json (kavram, soru, kart) + gorseller/
  envanter/<ders>.md slayt slayt döküm, sorunlar tablosu ve kararlar (uygulamaya gitmez)
supabase/01-sema.sql tekrar çalıştırılabilir tam şema (8. bölüm Kaynak)
kaynak-worker/       worker.js (R2 + kota, Cloudflare Worker), wrangler.toml, package.json
uygulama/            index.html (tek dosya PWA), sw.js (önbellek programcilik-v23), manifest,
                     supabase.js, ikonlar kostu-192/512.png, kostu-maskable-512.png, kostu-apple-180.png
test/tarayici/       Playwright testleri, test/gercek/sahte_supa.py
test/sql/            şemanın yerel PostgreSQL denemesi (Supabase taklidi + Kaynak denemesi)
test/kaynak/         Kaynak taklit sunucusu (PostgREST parçası + worker.js + bellekte R2), Worker denemesi
uygulama/webp/       iPhone için WebP kodlayıcı (@jsquash/webp 1.4.0, Apache-2.0)
KURULUM.md           kurulum ve günlük kullanım
DEVIR-NOTU.md, YENI-SOHBET.md
```

## 6. İçerik

Ağaç: 1. Sınıf › Güz: Algoritma, Veritabanı, Donanım, Ağlar, Elektrik, Ekoloji. 42 (hususi): Born2beRoot.

| Ders (id) | Konu | Soru | Kart | Durum |
| --- | --- | --- | --- | --- |
| algoritma | 15 | 248 | 99 | 1–6. hafta tamam (algoritma-hafta-6); C++ ekleri kaldırıldı |
| veritabani | 14 | 252 | 100 | tamam (konu 14'te hocaya soru) |
| donanim | 7 | 99 | 36 | 1. not tamam (guncelleme-25) |
| aglar | 3 | 47 | 18 | 1. not tamam (aglar-ders-1) |
| elektrik | 15 | 254 | 112 | 01–15 tamam; 16–23 kalan |
| ekoloji | 4 | 64 | 30 | tamam |
| born2beroot (hususi) | 17 | 64 | 20 | tamam |

### 6.1 İçerik kuralları (özet; ayrıntı ISLEME.md, BICIM.md)

- Konu başına 5–15 başlık (### / ####), 10–18 soru, 4–9 kart. `yer` bir başlıkla harfi harfine aynı. Kimlik `<konu-id>.sN` / `.kN`, yayımlandıktan sonra değişmez.
- Soru türleri: secme, dy, bosluk, dizme, esles, izleme, hesap, klasik. Doğru şık en uzun olmaz; "hepsi/hiçbiri" yok; Ek'ten ya da slaytlar arası çelişkili değerden soru yok; sınav tahmini cümlesi yok.
- **Algoritma'da C++ yok (Hamza):** derste henüz C++'a girilmedi; notlara, sorulara, kartlara C++ karşılığı ya da dile özgü (C++, C, Python) bilgi yazılmaz. Hocanın kendi slaytlarındaki C++ (dil seviyeleri, "Neden C++") kalır. Algoritmalar doğrulama için yine C++'ta çalıştırılabilir; bu yalnızca envantere yazılır.
- **Algoritma akış diyagramları:** hocanın 6. hafta sembolleriyle çizilir (`araclar/sekiller/algoritma.py`, `a_uc`/`a_oku`/`a_yaz`/`a_islem`/`a_karar`): BAŞLA/BİTİR elips, OKU klavyeden giriş sembolü (üst kenarı eğik dörtgen), YAZ paralelkenar, hesaplama dikdörtgen, karar eşkenar dörtgen; çıkışlar slaytlardaki gibi Evet/Hayır, çözüm belgesindekiler gibi E/H. Hocanın çizmediği diyagramlar "Ek"tir.
- Her ders: envanter (K0) → plan → not → şekil (358 px'te bakılır) → soru/kart → `node araclar/icerik-aktar.mjs --kuru` + `python3 araclar/icerik-denetle.py icerik/dersler/<ders>` → uçtan uca test → **bağımsız denetim ajanı** (KRİTİK/ORTA/DÜŞÜK) → teslim raporu + 🔶.

### 6.2 Görseller

- Not içinde `![açıklama](gorseller/ad.ext)`; boş satırsız art arda görsel satırları **yana kaydırılan dizi** olur.
- Sorularda isteğe bağlı `gorseller: ["a.webp", ...]` (1–8): soru metninin altında çizilir, açıklama yazısı gösterilmez.
- Her görsele dokununca **büyüteç** açılır (dokunulan yer 2,5 kat büyür; geri tuşu/Kapat kapatır).
- Görsel en az bir notta ya da bir sorunun `gorseller`'inde kullanılmalı; yoksa aktarıcı hata verir.

### 6.3 Donanım'a özgü

- `python3 araclar/sekiller/donanim.py icerik/dersler/donanim/gorseller` bütün görselleri üretir:
  - slayt fotoğraflarını yeniden adlandırır;
  - 2. slayttaki Gigabyte GA-8I945P-G anakartında 12 elemanı kırmızı-beyaz çerçeveyle işaretler (`anakart-isaret-<eleman>.webp` ve `-yakin.webp`);
  - Hamza'nın verdiği iki etiketli resmi işler: X58 (hocanın 3. slaytındaki resmin büyüğü → `anakart-etiketli.jpg`) ve ASUS A8N-SLI (`anakart-etiketli-2.jpg`; üç etiket düzeltildi: "Güney Köprüsü" → "Güç devresi soğutucusu", "Kuzey Köprüsü" → "Yonga seti (nForce4)", "Sulotları" → "DDR RAM yuvaları");
  - iki etiketli karttan etiket yazısı içermeyen yakın görünümler (`anakart-asus-*.webp`, `anakart-x58-*.webp`).
- 24 resimli soru; her eleman sorusunda dizi: hocanın kartı (tam + yakın) + ASUS + X58.
- Slayt 13/14 menü bağlantıları ve çelişkiler `icerik/envanter/donanim.md`'de.

## 7. Elektrik dersi (Temel Elektrik ve Elektronik): sürüyor, "devam" bekleniyor

- Kaynak `temel_elektrik_elektronik_st_1.pdf` (206 slayt; Hamza'nın bilgisayarında `~/İndirilenler/`). 14 parça (P01–P14), 23 konu. Her parça ayrı yazılır, ayrı denetlenir (K12).
- Yayında: P01–P08 (slayt 1–120), konu 01–15. P08'in bağımsız denetimi yapıldı (0 KRİTİK, 4 ORTA, 8 DÜŞÜK); ORTA'ların hepsi ve DÜŞÜK 1, 3, 4, 7, 8 kapatıldı; DÜŞÜK 2, 5, 6 bilerek bırakıldı (`elektrik-is/denetim/p08-denetim.md`).
- Kalan: P09 (121–137: 16 direnç çeşitleri), P10 (138–149: 17 kondansatör), P11 (150–158: 18 bobin), P12 (159–177: 19 yarı iletkenler, 20 diyot), P13 (178–192: 21 alternatif akım), P14 (193–206: 22 şebeke-alternatör-trafo, 23 enerji-Joule). Hiçbirinin dosyası yok; P09'dan başlanır.
- Çalışma düzeni `elektrik-devam.zip` (`elektrik-is/`): `PLAN.md`, `YAZICI.md`, `DENETCI.md`, parça envanterleri, raporlar, denetimler, şekil parçaları, `sekiller/yap.sh`. Birleştirme: envanter parçaları ders bitince `icerik/envanter/elektrik.md`'ye; şekil parçaları `yap.sh` ile `araclar/sekiller/elektrik.py`'ye. Denetçinin beklediği slayt düzeni: `/home/claude/kaynak/elektrik/` (PDF, `sayfa/s-NNN.png` 110 dpi ve `s-NNN.txt`).

## 8. Uygulamanın mimarisi (uygulama/index.html)

- **Giriş:** okul adresine OTP. Sözleşme sürüm 2 (`SOZLESME.surum` ile SQL'deki `sozlesme_surumu()` birlikte artırılır). iPhone Safari'de önce "ana ekrana ekle" adımları.
- **Cihaz sınırı:** 1; doluysa e-postaya ikinci kodla devralma (`cihaz_yokla`, `devralma_iste`, `cihazi_sahiplen`). `KOD_ARALIGI = 60`.
- **Veri:** içerik `konular`/`agac` tablolarından, IndexedDB'de (`vt`) internetsiz durur. Notlardaki ve sorulardaki bütün görseller eşitlemeden sonra arka planda iner (`gorselleriOnceIndir`, `konuGorselYollari`); kullanılmayanlar budanır (`gorselleriBuda`).
- **İnternetsiz:** giriş yapılmış cihaz internetsiz açılır; oturum süresi dolsa da kapatılmaz; yapılanlar bekler, internet gelince gider.
- **Kayıtlar** (`kayitlar`, tür + anahtar, son yazan kazanır, silme `silindi`): okundu, boya, yildiz, yanlis, kart, ayar, yer, muhim, calisma. `ayar/hedef` = `{gecmis:[{g,gun,hafta}]}`, `ayar/dondurma` = `{gunler:[...]}`, `ayar/kimlik`.
- **Cihazda kalanlar (localStorage):** `pg.mod` (tema), `pg.gozFiltre`, `pg.olcek`, `pg.cihazTuru`, `pg.cekmeceEkrani`, `pg.dondurmaSoruldu`, `pg.yarimCalis`, `pg.yarimKart`, `pg.kapsam` (Temrin seçimi), `pg.kartKapsam` (42 Tarzı seçimi), `pg.muhimSuzgec`, `pg.kartMuhim`, `pg.kartBilemedik`. Eski `pg.kartDers` / `pg.kartKonular` ilk açılışta `pg.kartKapsam`'a taşınıp silinir (`kartKapsaminiTasi`).
- **Bu cihaz (Hesap'ta `cihazBolumu`):** hesaba gitmez.
  - *Ölçek:* %70–150, 10'ar; bütün arayüz `html`'e CSS `zoom` ile (`olcekUygula`; ilk boyama `<head>`'deki betikte, aynı kural). Büyütme yerleşim genişliğini 320 px'in altına indirmez (`olcekSiniri`; ekran döndürülünce yeniden). Zoom varken imleç/`getBoundingClientRect`/`visualViewport` ekran pikseli, `style` px'i ve `offsetWidth`/`clientWidth` CSS pikselidir: aradaki çeviri `ekranOrani()` ile (ipucu, kart sürükleme ve uçuşu, editörün klavyeye sığması ve resim çubuğu, çekmece sürükleme). vh/vw CSS'te `var(--zoom-olcek)`'e bölünür (`--olcek` adı istatistik çubuk rengine ait). Üst başlık (`header.ust`) ve alt çubuk ölçekten etkilenmez: onlarda zoom `var(--zoom-ters)` (= 1/ölçek) ile geri alınır; alt çubuğa göre konan her şey (sayfa sonu boşluğu, şeritler, kısa bildirim, + düğmesi, geri al, kenar tutamağı) px'i ölçeğe bölerek konur. Alt çubuğa göre yeni bir sabit konum eklenirse o da bölünmeli. Pikselle konum hesaplayan yeni kod `ekranOrani()`'yi kullanmalı.
  - *Cihaz türü:* `cihazTuru()` = seçilen ya da tahmin (fare+hover: bilgisayar; dokunmatik kısa kenar ≥ 600: tablet; değilse telefon); `html[data-cihaz]`. Şimdilik yalnızca Bilgisayar'da Alt kısayolları açılır.
  - *Alt kısayolları:* Alt basılıyken görünen ve tıklanabilen her öğeye (üstü kapalı olmayan; `elementFromPoint`) rozet (`.kisayol-katman`); Alt + harf `click()` (yazı alanına odak). Harf `e.code`'dan (klavye düzeninden bağımsız); D, E, F kullanılmaz; ad harfi önce (alt çubuk önce dağıtılır: K, A, T, 4, N); 33'ten çok öğede iki harf. Mac'te yazı alanındayken ve AltGr'de devreye girmez. Düğmeye odak verilmez (editörde seçim kalsın).
- **Üst çubuk:** başlık, göz koruyucu (3 kademe), tema (açık, pembe, koyu, simsiyah), menü (≡).
- **Çekmece:** menü düğmesi ya da sağ kenardan çekme (`#kenarTutamak`). Dışarıya tek dokunuşla kapanır (`perdeKapatmayiKur`, `cekmeceyiKapat`). Başlık satırında sağa çekmek kapatır; gövdede yana kaydırmak bölüm değiştirir (`cekmeceSurukleKur` + `bolumKaydir`; yön sayfa çevirir gibi, alt çubuğun tersi: parmak sola → sağdaki bölüm; uçlarda döner; çip satırı, girdi ve yana kayan alanlarda devreye girmez; grafiklerin üstünden de olur; gövdede `touch-action:pan-y`). İstatistik düzeni ekrana değil çekmecenin genişliğine bakar (`.hesap-ic` kapsayıcı, `@container`). Dört ekran:
  - **Hedef ve seri:** yapraklı geri sayan saat (`saatKarti`, `geriSayimSaati`; animasyonlar kapalıyken de döner).
  - **İstatistikler.**
  - **Çalışma takvimi:** günlük/haftalık; tarih her açılışta hesaplanır; ince çizgiler `vector-effect:non-scaling-stroke`. Altında **Sınavlar** (`sinavBolumu`): `AGAC.sinavlar` (ağaçla iner, cihazda kalır), Türkiye saatiyle (`trGunu`, UTC+3); yakından uzağa, aynı gün tek kutu (`.sinav-kutu`), günü geçen gizli, saati geçen sönük; dersin rengi soldaki şeritte. Yeni sınav: `icerik/agac.json`'a bir satır + push (BICIM.md "Sınav takvimi").
  - **Hesap.**
- **Dondurma:** ilk hedefin ayından itibaren her ay 3 hak, kullanılmayan birikir (`kalanDondurma`, `dondurmaYeterMi`).
- **Seri:** günlük hedefe ulaşılan ardışık günler; dondurulan gün köprüdür.
- **Süre ölçümü:** 5 sn'lik tik, `calisma/"GG|YAZICI"`; bir konuda günde 3 dakikadan azsa süre sayılmaz.
- **Görseller:** `gorselHtml` (tek görsel ya da dizi), `galeriGuncelle` (sayaç/nokta/ok; oklar `.galeri-ok.onceki` / `.ileri`, genel `.geri` sınıfı kullanılmaz), `galeriYuksekligi` (dizinin yüksekliği görünen görsele uyar, kaydırırken ikisi arasında geçer; görseller en çok 60vh), `buyutecAc` (`.galeri-serit` ya da `[data-buyutec-dizi]` içindeki öbür görsellere oklar, yana kaydırma ve klavye oklarıyla geçilir; `[data-buyutec-dizi]`'de sıra `img[data-sira]`'dan; kapanınca dizi son bakılan görselde durur), `soruGorselleri` (soru kutusunda).
- **Alt çubuk:** Kıraat (iç adı `oku`, `#sayfaOku`), Ara, Temrin (`calis`), 42 Tarzı (`kart`), Notlar (`kaynak`). Parmakla yana kaydırma bir sekme geçirir: parmak sola → soldaki sekme, uçlarda öbür uca (`altCubukKaydirmaKur`; çubukta `touch-action:none`, ardından gelen tıklama yutulur). Görünen ad yalnızca `SEKMELER`'deki `etiket`tir; kimlikler değişmez.
- **Geri tuşu (her sekmenin kendi geçmişi):** `SEKME_GECMISI` (oku, ara, calis, kart) sekme başına geri adımlarını tutar; `derinlesGit(islev)` bulunulan sekmeye ekler. Telefonun geri tuşu ve sayfa içi geri düğmeleri (`geriDon`) aynı `geriAdimi`'ni çalıştırır: sekmenin yığını → yığın boşsa bir üst ekran (Kıraat'te konu → ders → kök; ötekilerde kök) → sekmenin kökündeyse Kıraat → Kıraat'in kökünde çıkış uyarısı (`cikisUyarisi`, ikinci basış çıkarır). Tarayıcı geçmişi yalnızca yer tutucudur (`{k, y}`, `gecmisKonumu`); yer tutucular kullanıcı dokunuşlarıyla eklenir (derinleşme, sekme değiştirme); tabanda bekçi (`bekciKur`). Sekmeler arası atlama (aramadan ya da sorudan "konuda oku") `donusIslevi` ile işaretlenir: geri → gelinen yer, Kıraat önceki konusuna döner; atlamadan sonra kullanıcı başka sekmeye geçerse dönüş adımları silinir ve açılan konu Kıraat'in olur. Etkin sekmeye yeniden dokunmak o sekmenin geçmişini siler.
- **Notlar sekmesi (5. sekme; iç adı `kaynak`, `#sayfaKaynak`):** öğrencinin kendi tasnifleri (en çok 3 kademe, kademe sunucuda hesaplanır), biçimli notları ve resimleri; yalnızca sahibi görür (RLS + `uye()`).
  - *Veri:* önce cihaz, sonra sunucu. Görünüm (`KAYNAK`) = sunucu kopyası (`KAYNAK_SUNUCU`, cihazda `liste`) + gönderilecekler sırası (`KAYNAK_KUYRUK`; her iş cihazda ayrı kayıt `k/<no>` — iki sekme birbirini ezmez). İşler: `tasnif_ekle/adlandir/sil`, `not_ekle/guncelle/sil`, `resim_ekle/sil`; kimliği uygulama üretir (`yeniKimlik`), yolda kaybolan cevaptan sonra yeniden gönderim çift kayıt açmaz (insert'te 23505 → güncelleme; Worker'da aynı `id` → var olan satır). `kaynakIsEkle` aynı notun gönderilmemiş işini birleştirir; `kaynakSilIsiEkle` silinenle ilgili gönderilmemiş işleri atar, öğe sunucudaysa silme işi ekler. `kaynakGonder` sırayı baştan gönderir (`kaynakSirada` ile yenilemeyle sırayla); geçici hatada (ağ, 401/403/5xx, PostgREST) bekler (3 sn → 5 dk), kalıcı hatada (SQL veri hatası, 400/404/409/413/415) iş "hata" olur, öğe cihazda kalır ve "gönderilemedi" gösterilir (Yeniden dene). Uygulama açılınca (`kaynakBasla`), bağlantı gelince ve öne gelince gönderilir. `kaynakYenile` sunucudan sayfa sayfa (1000) alır, sırayı ayıklar (`kaynakKuyruguBuda`).
  - *Silme:* `kaynakSilmeyeBasla` öğeyi hemen gizler, alttan "… silindi · Geri al (5)" (`geriAlBildirimi`); 5 sn sonra ya da uygulama arka plana geçince (`visibilitychange`, `pagehide`) sıraya girer. İçi dolu tasnifte önce onay sorulur.
  - *Ekran:* kökte hak çubuğu ve tasnif listesi; tasnifte alt tasnifler, sonra iki sütunlu kutucuklar (`kaynakIzgara`; en son değişen üstte, yükseklik tahminiyle kısa sütuna). Not kutucuğu: başlık, ön izleme (`kaynakNotOnizleme`), ilk resmi, tarih, resim sayısı. Sağ altta + (`kaynakFab`): kökte doğrudan yeni tasnif; tasnifte Not / Resim / Alt tasnif. Görünen hiçbir şey değişmediyse sayfa yeniden çizilmez (`kaynakImzasi`).
  - *Not editörü (`kaynakNotAc`):* tam ekran; başlık, "Değiştirildi … · N karakter / Oluşturuldu …", `contenteditable` metin; klavye üstünde biçim çubuğu (visualViewport'a sığar). Biçimler `execCommand` ile (geri al/yinele her adımı kapsar). "- ", "* " madde, "1. " numaralı liste açar. Kayıt: 1,5 sn ara, arka plana geçerken, kapanırken; boşaltılan not kapanınca silinir (geri alınabilir). Metne eklenen resim hemen küçültülüp cihaza yazılır (`r/<id>`), not kaydedilince `resim_ekle` (`not_id` ile) sıraya girer; kapanırken metinden çıkarılan resimler silinir. Yapıştırma ve bırakma süzülür.
  - *Biçim (`notHtmlDugumleri`):* saklanan ve gösterilen her şey DOMParser'da çözülüp izinli öğelerle yeniden kurulur: p, h3, ul/ol/li, br, b, i, u, s, `span[data-renk]` (`NOT_RENKLERI`: kirmizi, turuncu, yesil, mavi, mor; "yok" = varsayılan), `img[data-resim][width][height]`. Öznitelik kopyalanmaz; betik, stil, çerçeve, svg içiyle atılır. `bicim = 'duz'` (ilk sürümün notları) düz yazı olarak açılır, düzenlenince `html` olur.
  - *Sunucu:* tasnif ve notları uygulama Supabase'e doğrudan yazar (istemci kimliği ve anı: `kaynak_zaman` son 90 gün içindeyse cihazın anını kabul eder). Resim satırlarını, kotayı ve silmeleri Worker yazar (service_role işlevleri `kaynak_resim_ekle`, `kaynak_resim_satiri`, `kaynak_resim_sil`, `kaynak_not_sil`, `kaynak_tasnif_icini_sil`); notun resimleri varken not doğrudan silinemez (`not_id` dış anahtarı). Worker resmi yalnızca kaydı varsa verir; silmelerde önce satır, sonra R2. Sınırlar: kota yalnızca resimleri (notların içindekiler dahil) sayar; kişi başı 300 tasnif, 3000 not, not başına 60.000 harf, notların toplamı 5 MB.
  - *Hesap:* "Notlar" bölümü (`kaynakHesapBolumu`): hak çubuğu ve "Resimler" kutusu; dokununca `kaynakResimPaneliAc` (bütün resimler, yolları, silme). MB yalnızca Notlar kökünde ve burada yazar.
- **Güncelleme notları:** `GUNCELLEMELER` yeniden eskiye; yeni sürümde başa bir not eklenir (`surum`, `tarih`, `baslik`, `maddeler`). Açılışta bu cihazda görülmemiş notlar bir kutuda eskiden yeniye gösterilir (`gorulmemisNotlar`; hiç görülmemişse hepsi), Anladım `pg.notSurumu`'na en yeni sürümü yazar. Hepsi Hesap › Yama Notları'nda (`yamaNotlariBolumu`).
- **Pencere (`pencereAc`):** `girdi: { deger, yer, azami, cok }` ile metin ister (Tamam yazılanı, Vazgeç `null` döner). Pencere açıkken telefonun geri tuşu yalnızca pencereyi kapatır.
- **Seçim ekranı (kapsam):** `kapsamCiz(alan)` / `dersKapsamiCiz(ders, alan)` Temrin (`calis`, bütün konular) ve 42 Tarzı (`kart`, yalnızca kartlı konular) için ortaktır; ayarları `KAPSAM_ALANLARI`'nda. Seçimler ayrı tutulur.
- **42 Tarzı:** ana ekranda "Ders ve konular" düğmesi, iki anahtar (mühim yerler, bilemediklerim), "N kartla çalış" ve "Kartları liste hâlinde oku" (`kartListesiCiz`, ayrı ekran). Seçim yoksa yalnızca "Ders ve konu seç".
- **Yüzen şeritler:** kurulum şeridi (`.kurulum`) ve okuma çubuğu (`.oynatma`) alt çubuğun üstünde sabit durur. `altBosluguAyarla` (MutationObserver + ResizeObserver) görünür şeridin yüksekliğini `--serit-alt` değişkenine yazar; `body`'nin alt boşluğu buna göre büyür ki en alttaki düğmeler (konu seçimindeki "Tamam" gibi) şeridin altında kalmasın. Yeni bir sabit alt şerit eklenirse `YUZEN_SERITLER` seçicisine eklenir.
- **Service worker:** önbellek `programcilik-v23`; index.html değişince `sw.js`'teki sürüm bir artırılır.

## 9. Test düzeneği (programcilik-son.zip içinde)

Proje `/home/claude/programcilik`, testler `test/tarayici` ve `test/gercek` altında varsayılır.

1. İçeriği taklit sunucuya yükle:
   ```
   cd test/gercek && rm -rf cikti && (setsid python3 sahte_supa.py cikti 8799 >/dev/null 2>&1 &)
   cd ../.. && SUPABASE_URL=http://127.0.0.1:8799 SUPABASE_GIZLI_ANAHTAR=x node araclar/icerik-aktar.mjs
   fuser -k 8799/tcp
   ```
   Not: `pkill -f sahte_supa` komutun kendisini de öldürür; `fuser -k 8799/tcp` kullanın.
2. `cd test/tarayici && sh kur.sh` (uygulama/ → site/, test ayarlarıyla).
3. `sh yardim/sunucu.sh` test sitesini 8765'te açar; `sh yardim/hepsi.sh` bütün testleri sırayla çalıştırır (yaklaşık 45 dakika; arka planda çalıştırın).
   `kaynak_sina.py` için önce PostgreSQL açılır (konteynerde PostgreSQL 16 kurulu; root iken ayrı bir kullanıcıyla):
   ```
   useradd -m pgk; mkdir -p /home/claude/pgdeneme && chown pgk /home/claude/pgdeneme
   su pgk -c "/usr/lib/postgresql/16/bin/initdb -D /home/claude/pgdeneme/veri -U postgres -A trust"
   su pgk -c "/usr/lib/postgresql/16/bin/pg_ctl -D /home/claude/pgdeneme/veri -o '-p 5499 -k /tmp' -l /home/claude/pgdeneme/log start"
   cd test/kaynak && npm i      # taklit sunucunun PostgreSQL istemcisi (pg)
   ```
   `sh test/sql/calistir.sh` şemayı Supabase taklidiyle iki kez kurar ve Kaynak SQL denemesini yapar ("KAYNAK SQL: TAMAM", 78 denetim); `node test/kaynak/worker_deneme.mjs` Worker'ı dener (39 kontrol). `kaynak_sina.py`, `notlar_editor_sina.py` ve `cihaz_sina.py` (ortak düzenek `kaynak_taban.py`) bunları kendisi kurar, taklit sunucuyu 8796'da açar.
4. Testler (hepsi son durumda geçiyor):
   - `sina.py` (99)
   - dersler: `alg_sina.py`, `vt_sina.py`, `eko_sina.py`, `el_sina.py`, `ag_sina.py`, `dn_sina.py`
   - `tum_sorular_sina.py` (bütün soruların doğru cevapla doğru sayılması)
   - `bilmiyorum_sina.py` (51: her türde Bilmiyorum, yazım hoşgörüsü, ilerleme çubuğu, notta bölümün yanıp sönmesi)
   - `galeri_sina.py` (dizi, büyüteç, soru görselleri)
   - `cevrimdisi_sina.py`, `buda_sina.py`
   - `hedef_sina.py`, `saat_cekmece_sina.py`, `takvim_gelecek_sina.py`
   - `tasma_sina.py`, `tema_sina.py`, `ios_sina.py`, `dokunus_sina.py`
   - `istatistik_sina.py`, `kalicilik_sina.py`, `devam_sina.py`, `aralik_sina.py`, `baslik_sina.py`
   - `geri_sina.py` (sekme değişince sayfa içi geri düğmeleri, Kıraat etiketi, 42 Tarzı eski seçiminin taşınması)
   - Ders testlerinin 42 Tarzı bölümü ortak `kart_kapsam_sina` (vt_taban.py) ile yapılır.
   - `kaynak_sina.py` (Notlar uçtan uca, 74: tasnif, 3 kademe, + menüsü, resim küçültme ve WebP, Safari yolu, kutucuklar, büyüteç sırası, 5 sn geri al, geri, bağlantısız sıra ve kalıcılığı, kota, kalıcı hata ve Yeniden dene, Hesap › Resimler paneli, tasnif silme, çıkış uyarısı, 358 px)
   - `notlar_editor_sina.py` (not editörü, 85: biçimler, kısayollar, renk, ara başlık, geri al/yinele, otomatik kayıt, tarihler, metindeki resim, yapıştırma süzgeci, kötü niyetli kayıt, düz notlar, boş/uzun not, silme, iki sekme, dar ekran ve klavye)
   - `sinav_sina.py` (sınav takvimi, 18: sıralama, aynı gün tek kutu, LMS, yer/not, geçmiş gizli, saati geçen sönük, hususi süzme, sunucusuz açılış, başka saat dilimi)
   - `cihaz_sina.py` (Bu cihaz, 88: alt çubukta ve çekmecede kaydırma, ölçek ve sınırı, cihaz türü, Alt kısayolları, geniş ekranda halka listesi, zoom'da ipucu/rozet/editör, çubukların ölçekten etkilenmemesi, güncelleme notu ve Yama Notları)
   - `serit_sina.py` (kurulum şeridi açıkken en alttaki düğmeler dokunulabilir mi; konu seçimi → Tamam → temrin yolları)
   - Ortak düzenek `vt_taban.py`: Supabase taklidi; görselleri uzantısına göre doğru türle verir. `akis-1.svg` (test görseli) `test/tarayici/` içinde durur.
   - Testlerin çoğu gerçek ilk kullanımı taklit etmez: `cihaz_ac` kurulum şeridini öntanımlı olarak gizler, test hesabına hedef önceden konur. Şerit `serit_sina.py`'de, hedef sorusu `hedef_sina.py`'de denenir; ilk kullanıma dokunan bir değişiklikte bu ikisi mutlaka çalıştırılır.
5. Yeni ders için test: `ag_sina.py`'yi kopyalayıp ders kimliği ve adlarını değiştirin.

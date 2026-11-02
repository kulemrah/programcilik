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
| Şema | `supabase/01-sema.sql` (sözleşme sürümü 2, kayıt türü `calisma`); yeni özellikler `kayitlar` tablosundaki `ayar` kayıtlarını kullanır, yeni SQL gerekmez |

## 3. Teslim durumu

- Çalışma kopyasının son hâli: `programcilik-son.zip` + üstüne guncelleme-28 (guncelleme-26 ve 27'yi kapsar). GitHub'daki deponun bu hâle getirilmesi gerekir.
- Teslim edilen ama GitHub'a yüklendiği **teyit edilmeyen** paketler: guncelleme-20, 21, 22, 23, 24, aglar-ders-1, guncelleme-25. `programcilik-son.zip` bunların hepsini kapsar; tek tek yüklemeye gerek yok.
- guncelleme-28 (26 ve 27'yi de kapsar): kurulum şeridinin en alttaki düğmeleri örtmesi; her sekmenin kendi geri geçmişi; "Oku" sekmesinin adı "Kıraat"; 42 Tarzı'nda ders ve konu seçimi Temrin'deki seçim ekranıyla; Hesap ekranında kutular arası boşluk; Elektrik 13–15. Teslim edildi, GitHub'a yüklendiği teyit edilmedi. `programcilik-son.zip`'in üstüne yüklenir; 26 ve 27'yi ayrıca yüklemeye gerek yok.
- guncelleme-24'te eski ikonlar silindi: depoda `uygulama/ikon-*.png` ve `uygulama/apple-touch-icon.png` kaldıysa `git rm` ile silinir.

## 4. 🔶 Açık kalanlar

1. **Kod e-postası paneli:** Supabase SMTP **Sender name** `Kostü - Ders` ve iki şablon (Confirm sign up, Magic link or OTP) KURULUM.md bölüm 2'ye göre güncellenecek; yapıldığı teyit edilmedi.
2. **GitHub Pro:** öğrenci başvurusu bekleniyor; gelince depo private yapılacak.
3. **Hocaya sorulacaklar:**
   - Veritabanı konu 14, iç içe SELECT sorusu (envanter K5 slayt 10).
   - Ağlar: A sınıfı ilk oktet "0–126" mı "1–126" mı (notta 1–126 + Dikkat); slayt 17'deki ODTÜ/IANA ifadesi.
   - Donanım: numaralı resimde 3 numara (resimde PCI Express x16, bağlantısı AGP slaytına); arka panel resminde 4 ve 6.
4. **Kararı bekleyen:** Donanım'daki ASUS A8N-SLI resminin üç etiketi resmin üzerinde düzeltildi (bkz. 6.3); Hamza özgünü isterse geri alınır.
5. **Bekleyen eski kararlar:** dondurma birikmesine üst sınır (şimdi yok), koyu temada beyaz saat kartları, iPhone'da yeni ikon için uygulamanın ana ekrana yeniden eklenmesi.
6. İsteğe bağlı: R2 yedeği kurulmadı (KURULUM.md "Yedek").
7. Gerçek cihazda denenmedi: Android/iPhone'da menü kapanması, Brave'de oturum, yana kaydırılan resimler ve büyüteç.

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
supabase/01-sema.sql tekrar çalıştırılabilir tam şema
uygulama/            index.html (tek dosya PWA), sw.js (önbellek programcilik-v16), manifest,
                     supabase.js, ikonlar kostu-192/512.png, kostu-maskable-512.png, kostu-apple-180.png
test/tarayici/       Playwright testleri (test-son.zip'te), test/gercek/sahte_supa.py
KURULUM.md           kurulum ve günlük kullanım
DEVIR-NOTU.md, YENI-SOHBET.md
```

## 6. İçerik

Ağaç: 1. Sınıf › Güz: Algoritma, Veritabanı, Donanım, Ağlar, Elektrik, Ekoloji. 42 (hususi): Born2beRoot.

| Ders (id) | Konu | Soru | Kart | Durum |
| --- | --- | --- | --- | --- |
| algoritma | 10 | 172 | 68 | tamam |
| veritabani | 14 | 252 | 100 | tamam (konu 14'te hocaya soru) |
| donanim | 7 | 99 | 36 | 1. not tamam (guncelleme-25) |
| aglar | 3 | 47 | 18 | 1. not tamam (aglar-ders-1) |
| elektrik | 15 | 254 | 112 | 01–15 tamam; 16–23 kalan |
| ekoloji | 4 | 64 | 30 | tamam |
| born2beroot (hususi) | 17 | 64 | 20 | tamam |

### 6.1 İçerik kuralları (özet; ayrıntı ISLEME.md, BICIM.md)

- Konu başına 5–15 başlık (### / ####), 10–18 soru, 4–9 kart. `yer` bir başlıkla harfi harfine aynı. Kimlik `<konu-id>.sN` / `.kN`, yayımlandıktan sonra değişmez.
- Soru türleri: secme, dy, bosluk, dizme, esles, izleme, hesap, klasik. Doğru şık en uzun olmaz; "hepsi/hiçbiri" yok; Ek'ten ya da slaytlar arası çelişkili değerden soru yok; sınav tahmini cümlesi yok.
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
- **Cihazda kalanlar (localStorage):** `pg.mod` (tema), `pg.gozFiltre`, `pg.cekmeceEkrani`, `pg.dondurmaSoruldu`, `pg.yarimCalis`, `pg.yarimKart`, `pg.kapsam` (Temrin seçimi), `pg.kartKapsam` (42 Tarzı seçimi), `pg.muhimSuzgec`, `pg.kartMuhim`, `pg.kartBilemedik`. Eski `pg.kartDers` / `pg.kartKonular` ilk açılışta `pg.kartKapsam`'a taşınıp silinir (`kartKapsaminiTasi`).
- **Üst çubuk:** başlık, göz koruyucu (3 kademe), tema (açık, pembe, koyu, simsiyah), menü (≡).
- **Çekmece:** menü düğmesi ya da sağ kenardan çekme (`#kenarTutamak`). Dışarıya tek dokunuşla kapanır (`perdeKapatmayiKur`, `cekmeceyiKapat`). Dört ekran:
  - **Hedef ve seri:** yapraklı geri sayan saat (`saatKarti`, `geriSayimSaati`; animasyonlar kapalıyken de döner).
  - **İstatistikler.**
  - **Çalışma takvimi:** günlük/haftalık; tarih her açılışta hesaplanır; ince çizgiler `vector-effect:non-scaling-stroke`.
  - **Hesap.**
- **Dondurma:** ilk hedefin ayından itibaren her ay 3 hak, kullanılmayan birikir (`kalanDondurma`, `dondurmaYeterMi`).
- **Seri:** günlük hedefe ulaşılan ardışık günler; dondurulan gün köprüdür.
- **Süre ölçümü:** 5 sn'lik tik, `calisma/"GG|YAZICI"`; bir konuda günde 3 dakikadan azsa süre sayılmaz.
- **Görseller:** `gorselHtml` (tek görsel ya da dizi), `galeriGuncelle` (sayaç/nokta/ok), `buyutecAc`, `soruGorselleri` (soru kutusunda).
- **Alt çubuk:** Kıraat (iç adı `oku`, `#sayfaOku`), Ara, Temrin (`calis`), 42 Tarzı (`kart`). Görünen ad yalnızca `SEKMELER`'deki `etiket`tir; kimlikler değişmez.
- **Geri tuşu (her sekmenin kendi geçmişi):** `SEKME_GECMISI` (oku, ara, calis, kart) sekme başına geri adımlarını tutar; `derinlesGit(islev)` bulunulan sekmeye ekler. Telefonun geri tuşu ve sayfa içi geri düğmeleri (`geriDon`) aynı `geriAdimi`'ni çalıştırır: sekmenin yığını → yığın boşsa bir üst ekran (Kıraat'te konu → ders → kök; ötekilerde kök) → sekmenin kökündeyse Kıraat → Kıraat'in kökünde çıkış uyarısı (`cikisUyarisi`, ikinci basış çıkarır). Tarayıcı geçmişi yalnızca yer tutucudur (`{k, y}`, `gecmisKonumu`); yer tutucular kullanıcı dokunuşlarıyla eklenir (derinleşme, sekme değiştirme); tabanda bekçi (`bekciKur`). Sekmeler arası atlama (aramadan ya da sorudan "konuda oku") `donusIslevi` ile işaretlenir: geri → gelinen yer, Kıraat önceki konusuna döner; atlamadan sonra kullanıcı başka sekmeye geçerse dönüş adımları silinir ve açılan konu Kıraat'in olur. Etkin sekmeye yeniden dokunmak o sekmenin geçmişini siler.
- **Seçim ekranı (kapsam):** `kapsamCiz(alan)` / `dersKapsamiCiz(ders, alan)` Temrin (`calis`, bütün konular) ve 42 Tarzı (`kart`, yalnızca kartlı konular) için ortaktır; ayarları `KAPSAM_ALANLARI`'nda. Seçimler ayrı tutulur.
- **42 Tarzı:** ana ekranda "Ders ve konular" düğmesi, iki anahtar (mühim yerler, bilemediklerim), "N kartla çalış" ve "Kartları liste hâlinde oku" (`kartListesiCiz`, ayrı ekran). Seçim yoksa yalnızca "Ders ve konu seç".
- **Yüzen şeritler:** kurulum şeridi (`.kurulum`) ve okuma çubuğu (`.oynatma`) alt çubuğun üstünde sabit durur. `altBosluguAyarla` (MutationObserver + ResizeObserver) görünür şeridin yüksekliğini `--serit-alt` değişkenine yazar; `body`'nin alt boşluğu buna göre büyür ki en alttaki düğmeler (konu seçimindeki "Tamam" gibi) şeridin altında kalmasın. Yeni bir sabit alt şerit eklenirse `YUZEN_SERITLER` seçicisine eklenir.
- **Service worker:** önbellek `programcilik-v16`; index.html değişince `sw.js`'teki sürüm bir artırılır.

## 9. Test düzeneği (test-son.zip)

Proje `/home/claude/programcilik`, testler `test/tarayici` ve `test/gercek` altında varsayılır.

1. İçeriği taklit sunucuya yükle:
   ```
   cd test/gercek && rm -rf cikti && (setsid python3 sahte_supa.py cikti 8799 >/dev/null 2>&1 &)
   cd ../.. && SUPABASE_URL=http://127.0.0.1:8799 SUPABASE_GIZLI_ANAHTAR=x node araclar/icerik-aktar.mjs
   fuser -k 8799/tcp
   ```
   Not: `pkill -f sahte_supa` komutun kendisini de öldürür; `fuser -k 8799/tcp` kullanın.
2. `cd test/tarayici && sh kur.sh` (uygulama/ → site/, test ayarlarıyla).
3. `sh yardim/sunucu.sh` test sitesini 8765'te açar; `sh yardim/hepsi.sh` bütün testleri sırayla çalıştırır (yaklaşık 40 dakika; arka planda çalıştırın).
4. Testler (hepsi son durumda geçiyor):
   - `sina.py` (99)
   - dersler: `alg_sina.py`, `vt_sina.py`, `eko_sina.py`, `el_sina.py`, `ag_sina.py`, `dn_sina.py`
   - `tum_sorular_sina.py` (bütün soruların doğru cevapla doğru sayılması)
   - `galeri_sina.py` (dizi, büyüteç, soru görselleri)
   - `cevrimdisi_sina.py`, `buda_sina.py`
   - `hedef_sina.py`, `saat_cekmece_sina.py`, `takvim_gelecek_sina.py`
   - `tasma_sina.py`, `tema_sina.py`, `ios_sina.py`, `dokunus_sina.py`
   - `istatistik_sina.py`, `kalicilik_sina.py`, `devam_sina.py`, `aralik_sina.py`, `baslik_sina.py`
   - `geri_sina.py` (sekme değişince sayfa içi geri düğmeleri, Kıraat etiketi, 42 Tarzı eski seçiminin taşınması)
   - Ders testlerinin 42 Tarzı bölümü ortak `kart_kapsam_sina` (vt_taban.py) ile yapılır.
   - `serit_sina.py` (kurulum şeridi açıkken en alttaki düğmeler dokunulabilir mi; konu seçimi → Tamam → temrin yolları)
   - Ortak düzenek `vt_taban.py`: Supabase taklidi; görselleri uzantısına göre doğru türle verir. `akis-1.svg` (test görseli) `test/tarayici/` içinde durur.
   - Testlerin çoğu gerçek ilk kullanımı taklit etmez: `cihaz_ac` kurulum şeridini öntanımlı olarak gizler, test hesabına hedef önceden konur. Şerit `serit_sina.py`'de, hedef sorusu `hedef_sina.py`'de denenir; ilk kullanıma dokunan bir değişiklikte bu ikisi mutlaka çalıştırılır.
5. Yeni ders için test: `ag_sina.py`'yi kopyalayıp ders kimliği ve adlarını değiştirin.

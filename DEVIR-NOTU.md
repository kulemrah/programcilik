# Devir notu — "Kostü - Ders" (Bilgisayar Programcılığı ders notları PWA'sı)

Bu not yeni sohbete geçiş içindir. Yanındaki `programcilik.zip` projenin son hâlidir (GitHub'daki depo ile aynı olmalı), `test.zip` tarayıcı testleridir.

## Kullanıcı ve çalışma biçimi

- Hamza; KOSTÜ (Kocaeli Sağlık ve Teknoloji Üniversitesi) Bilgisayar Programcılığı 1. sınıf ve 42 öğrencisi. Her şey Türkçe.
- **Hata payı yok:** okul sınav konuları ve soruları. İçerikte uydurma yok, hocanın ifadesi korunur.
- Uygulama öğrenciye **"siz"** diye hitap eder. Hamza'ya da "siz" denir.
- Hamza'nın karar vermesi gerekenler **🔶 Sizin karar vermeniz gerekenler** başlığıyla belirgin işaretlenir.
- Güncellemede **yalnızca değişen dosyalar** verilir (tam zip yalnızca gerektiğinde).
- Verilen her komut açıklanır: ne yapar, bayrakları ve işaretleri (`|` gibi) ne demek, beklenen çıktı ne.
- Plan ve rehber belgelerinde yalnızca son durum yazılır; "önce şöyleydi" bölümleri olmaz.
- Sırlar (secret key, Resend anahtarı, erişim anahtarları) asla sohbete yazdırılmaz. Ekrana basılan komutlar anahtarı kesecek biçimde verilir.

## Canlı kurulum (yapıldı)

| Parça | Değer |
|---|---|
| Site | `https://kulemrah.github.io/programcilik/` (GitHub Pages, iş akışıyla) |
| Depo | `kulemrah/programcilik`: **herkese açık** (bilinçli karar; Pro gelince private yapılacak, adres değişmez) |
| Git | SSH anahtarı `~/.ssh/id_ed25519_kulemrah`, depo içi `core.sshCommand`; yazar `kulemrah` + noreply e-posta |
| Supabase | Proje `nzhruevikugpmyoozpyc` (Free, org `yuksek_okul`, hesap birkulemrah@gmail.com) |
| GitHub sır/değişken | `SUPABASE_URL` (Variables), `SUPABASE_GIZLI_ANAHTAR` (Secrets; yenilenmiş `new_secret_key`) |
| Kanca | Before User Created → `public.kayit_kapisi` (yalnız @kocaelisaglik.edu.tr) |
| E-posta | Resend, alan `posta.eskimezyazi.app` (Verified; DNS eski Cloudflare hesabındaki `eskimezyazi.app` bölgesinde, CNAME'ler DNS only). Gönderen `giris@posta.eskimezyazi.app`. Bölge Tokyo seçilmiş (çalışıyor). |
| OTP | 6 hane, 900 sn; iki kod arası 60 sn (öntanımlı, değiştirilmeyecek) |
| Tashih adresi | birkulemrah@gmail.com |
| Uygulama adı | Ana ekranda/sekmede **Kostü - Ders**; uygulama içi başlık **Bilgisayar Programcılığı** |
| Şema | `supabase/01-sema.sql` son hâli çalıştırıldı (sözleşme sürümü 2, kayıt türü `calisma`) |

## 🔶 Açık kalanlar

1. **Kod e-postası paneli:** gönderen adı `Kostü - Ders` (karar verildi). Supabase SMTP **Sender name** ve iki şablon (Confirm sign up, Magic link or OTP) KURULUM.md bölüm 2'deki metne göre panelde güncellenecek; yapıldığı teyit edilmedi.
2. **guncelleme-20** (`KOD_ARALIGI = 60`, KURULUM.md bölüm 2), **guncelleme-21** (Elektrik konu 01–12) **guncelleme-22** (iPhone tarzı görünüm, kart kaydırma/dönme, yazı seçimi) **guncelleme-23** (hedef, seri, dondurma, çekmece, takvimler, göz koruyucu, turuncu vurgu; 22'deki dosyaları da kapsar) ve **guncelleme-24** (biriken dondurma hakkı, internetsiz görseller, yeni ikon, perdeye tek dokunuşla kapanma, saat ve takvim çizgileri; önbellek `programcilik-v12`; eski 4 ikon dosyası `git rm` ile silinir) teslim edildi. GitHub'a yüklenip yüklenmedikleri teyit edilmedi.
3. **GitHub Pro:** öğrenci başvurusu bekleniyor. Gelince depo private yapılacak.
4. **Hocaya sorulacak:** Veritabanı dersindeki iç içe SELECT sorusu (veritabanı konu 14; envanter K5 slayt 10). Veritabanı dersinde sonraki çalışmada hatırlatılmalı.
5. İsteğe bağlı: R2 yedeği (Cloudflare, yeni hesapla) henüz kurulmadı; KURULUM.md "Yedek" bölümü.

## Depo düzeni

```
.github/workflows/  icerik.yml (doğrula + Supabase'e aktar), yayimla.yml (uygulama/ → Pages)
araclar/            icerik-aktar.mjs (--kuru: yalnız doğrula), icerik-denetle.py (kalite uyarıları), şekil üreticiler
icerik/             ISLEME.md (PDF → not/temrin/kart işleme kuralları), BICIM.md, agac.json,
                    dersler/<ders>/NN-ad.md + .json, envanter/<ders>.md (kaynak slayt dökümü ve kararlar)
supabase/01-sema.sql  tekrar çalıştırılabilir tam şema
uygulama/           index.html (tek dosya PWA), sw.js, manifest.webmanifest, supabase.js,
                    ikonlar: kostu-192/512.png (saydam, "any"), kostu-maskable-512.png (Android, içerik güvenli dairede),
                    kostu-apple-180.png (iOS, köşeleri dolu kare; iOS kendisi yuvarlar)
KURULUM.md          kurulumun ve günlük kullanımın son hâli
```

İçerik: 7 ders (5'inde içerik var: algoritma, veritabanı, ekoloji, born2beroot, elektrik), 57 konu (17 hususi), 762 soru, 313 kart, 91 görsel. Doğrulama: `node araclar/icerik-aktar.mjs --kuru`; kalite: `python3 araclar/icerik-denetle.py icerik/dersler/<ders>` (5 derste 0 uyarı).

İçerik kuralları (ayrıntı ISLEME.md / BICIM.md):
- `yer` bir ### ya da #### başlığıyla birebir aynı olur; kimlikler `<konu>.sN` / `.kN` biçiminde.
- Tablo hücresinde `|` olmaz.
- Doğru şık en uzun yanlış şıkkın 1,25 katını geçmez.
- Ek'ten ya da tartışmalı slayt değerinden soru çıkarılmaz.
- Sınav tahmini cümlesi yazılmaz.
- Hocanın algoritma adımları ("Sonucu yaz") olduğu gibi kalır.
- Soru türleri: secme, dy, bosluk, dizme, esles, izleme, hesap, klasik.

## Uygulamanın mimarisi (index.html)

- **Giriş:** okul adresine OTP kodu. Kanca okul dışı adrese hesap açtırmaz; parola tetikle engellenir. Sözleşme **sürüm 2** (madde 7: ad-soyad ve çalışma süreleri de tutulur). Sürüm değişirse `SOZLESME.surum` ve SQL'deki `sozlesme_surumu()` birlikte artırılır.
- **iPhone/iPad:** Safari'de giriş ekranı önce "ana ekrana ekle" adımlarını gösterir (••• › Paylaş › Ana Ekrana Ekle; iOS 26). Altındaki bağlantıyla Safari'de devam edilebilir (karar: kalsın). Safari ile ana ekran uygulamasının depoları ayrıdır; aynı cihazı tanımak mümkün değil.
- **Cihaz sınırı:** öntanımlı 1. Doluysa e-postaya ikinci kodla devralma; mantığı SQL'de (`cihaz_yokla`, `devralma_iste`, `cihazi_sahiplen`). `KOD_ARALIGI = 60` (index.html, Supabase'in öntanımlı aralığıyla aynı); sunucu daha uzun bekletirse sayaç ona uyar.
- **Veri:** içerik `konular`/`agac` tablolarından gelir, IndexedDB'de (`vt`) internetsiz durur. Notlardaki bütün görseller de her başarılı eşitlemeden sonra arka planda cihaza iner (`gorselleriOnceIndir`); konu internetsiz ilk kez açılsa da şekiller görünür.
- **İnternetsiz kullanım:** giriş yapılmış cihazda uygulama internetsiz sıfırdan açılır (service worker kabuğu, IndexedDB içerik ve görseller); oturum süresi dolmuş olsa da kapatılmaz. Okuma, temrin, 42 Tarzı ve menü çalışır; yapılanlar cihazda bekler, internet gelince gönderilir (`cevrimdisi_sina.py`). Kullanıcı kayıtları `kayitlar` tablosunda (tür + anahtar, son yazan kazanır, silme yerine `silindi`). Türler: okundu, boya, yildiz, yanlis, kart, ayar, yer, muhim, calisma.
- **Üst çubuk:** başlık, göz koruyucu (3 kademe sıcak renk süzgeci, 4. dokunuş kapatır; `pg.gozFiltre`, `data-goz`), tema, menü (≡). Başlık ekran genişliğiyle küçülür, 330 px altında iki satıra iner.
- **Çekmece (hesap alanı):** menü düğmesi ya da sağ kenardaki boydan boya ince çizgiden (`#kenarTutamak`) sola çekince sağdan açılır; sağa çekince, ×, perde ya da geri tuşuyla kapanır. Perde (dışarısı) `click` beklemez, parmak kalkınca kapatır ve ardından gelen tıklamayı yutar (alttaki ekrana geçmesin); geri gidiş olmazsa `cekmeceyiKapat` 450 ms sonra doğrudan kapatıp yığını düzeltir. Telefonda kenardan çekip açınca dışarıya ilk dokunuşun boşa gittiği bildirildi; bilgisayarda yeniden üretilemedi, bu yolla giderildi. Son açılan ekran hatırlanır (`pg.cekmeceEkrani`). Dört ekran:
  - **Hedef ve seri:** günlük ve haftalık hedefe kalan süre (yapraklı geri sayan saat, ortada çizgi yok; açılınca hedefin tamamından kalana iner, o gün hiç çalışılmadıysa sıfırdan hedefe çıkar, böylece her açılışta döner; cihazda animasyonlar kapalıyken de döner), seri ve bu haftanın günleri, dondurma hakkı, hedefi değiştirme.
  - **İstatistikler:** dönem (Bugün/7/30/Tümü), 4 özet kutusu (süre, seri, temrin %, 42 Tarzı %), çalışma türleri, halka çizelgesi + liste (iç halka ders, dış halka konu), son 14 gün çubukları, derslere göre ilerleme.
  - **Çalışma takvimi:** günlük ve haftalık (hafta sayısı ekran genişliğine göre 12–26).
  - **Hesap:** isteğe bağlı ad-soyad (`ayar/kimlik`), eşitleme bilgisi, çıkış, tashih adresi, sözleşme.
- **Hedef:** `ayar/hedef` = `{ gecmis: [{ g, gun, hafta }] }` (saniye; g'den itibaren geçerli). Hedef yoksa ilk eşitlemeden sonra sorulur (`hedefSorusunuAc`). Saat ve dakika (5'er) seçilir; günlük değişince haftalık 7 katı olur, artırılabilir, azaltılırsa uyarı çıkar. Değişiklik bugünden geçerli; geçmiş günler kendi hedefiyle, ilk hedeften önceki günler ilk hedefle (yeşil kenarsız) değerlendirilir.
- **Seri:** günlük hedefe ulaşılan ardışık günler; dondurulan gün köprüdür (bozmaz, uzatmaz). Bugün henüz tamamlanmadıysa dünden sayılır.
- **Dondurma:** `ayar/dondurma` = `{ gunler: [...] }`. İlk hedefin ayından başlayarak her ay 3 hak eklenir, kullanılmayanlar birikir (üst sınır yok). Bir gün ancak o günün ayına kadar kazanılmış haklarla dondurulabilir (`dondurmaYeterMi`: en eski adayın ayından bu aya her ay sonunda bakiye ≥ 0). 8'e kadar hak buz buz, fazlası "❄ × N" gösterilir. Seri koptuysa (dünden geriye hedefsiz ve dondurulmamış günler, öncesinde en az bir tamam gün) açılışta sorulur; aynı kopukluk için cihaz başına bir kez (`pg.dondurmaSoruldu`). Hak yetmezse yalnızca bilgi verilir. Haftalık hedeften dondurulan her gün için o günün günlük hedefi düşülür.
- **Takvim:** kademe gün süresinin günlük hedefe oranıyla: 1 <½, 2 ½–1, 3 1–1,5 (hedefte, yeşil kenar), 4 1,5–2, 5 ≥2. Dondurulan gün buz işaretli. Ay sınırları ince çizgi (1 px, `vector-effect:non-scaling-stroke`; SVG büyüyünce kalınlaşmaz); ay adı ayın 1'ini içeren sütunda. Takvim tarih tablosu gömülü değil, her açılışta cihazın saatinden hesaplanır; 2 yıl boyunca her gün için (artık yıl, yılbaşı, yaz saati olan saat dilimi) `takvim_gelecek_sina.py` ile denendi. Fareyle üstüne gelince yüzen kutu; tıklayınca/dokununca bilgi takvimin altındaki satırda kalır (parmak örtmez). Haftalık takvimde hedef dondurmalara göre düşülmüş haftalık hedeftir.
- **İpuçları (`ipucuBagla`):** fareyle üstüne gelince gösterir; tıklama ya da dokunuşla sabitlenir, başka yere dokununca kapanır. Parmakla dokununca yüzen kutu parmağın 64 px üstünde, yer yoksa yanında durur.
- **Soru ve uyarı penceresi:** `soruSor` / `uyariGoster` (tarayıcının confirm/alert'i kullanılmaz; "bu sayfanın pencere açmasını engelle" seçilince confirm sessizce hayır dönüyordu).
- **Süre ölçümü:**
  - 5 sn'lik tik. Konu/soru/kart ekrandayken sayar; 3 dk (kart 2 dk) dokunulmazsa durur; sesli okumada sayar.
  - Dakikada bir ve arka plana geçerken `calisma/"GG|YAZICI"` kaydına sessizce yazılır (hemen ağa çıkmaz).
  - Değer: `o/t/k` saniye, `d/y` temrin doğru/yanlış, `b/n` bildim/bilemedim; konu kimliğine göre.
  - **YAZICI** kimliği IndexedDB'de durur, kayıtlarla birlikte doğar ve silinir; tarayıcı kilidiyle (Web Locks) tek sekmede tutulur. Böylece hiçbir satır, onu tamamen bilmeyen bir yazıcı tarafından ezilmez.
  - Kaldırılmış konunun süresi "Öbür konular"da sayılır.
  - **3 dk kuralı:** bir konuda bir günde (bütün cihazlar toplamı) 3 dakikadan az kalındıysa o günkü süresi hiçbir yerde sayılmaz (`istatistikTopla`); doğru/yanlış ve bildim/bilemedim sayıları kalır.
  - Klasik soruda "Kısmen" yanlış sayılır.
- **Yarım oturum:** temrin ve deste, sekmeye dokunma, geri, uygulama kapanması sonrası **Devam et** kartıyla sürer. Cihazda `pg.yarimCalis` / `pg.yarimKart` anahtarlarında durur, hesaba gitmez, çıkışta silinir.
- **Geri tuşu:** her derin ekran geçmişe adım ekler (`derinlesGit`). Kökte "bekçi" adımı var: ilk geri uyarı verir, 2,5 sn içinde ikincisi çıkar. Adımlar yükleme kimliğiyle (`y`) işaretli; yenilemeden kalan eski adımlar sessizce atlanır.
- **Görünüm (iPhone tarzı):** gri zemin üstünde kenarsız gruplu yüzeyler; ardışık satırlar (ders, konu, kapsam, yıldız, arama sonucu) tek yuvarlak kutuda birleşir, aralarında ince çizgi (`:has()` ile). Her dersin renkli kare simgesi var (`DERS_SIMGELERI`, renk `dersRengi`; tanınmayan derste kitap). Sistem yazı tipi; daktilo yazı yalnızca kodda. Vurgu turuncu (pembe temada mürdüm), anahtar düğmeleri yeşil; istatistikteki büyüklük ölçekleri mavi. CSS'te "iPhone tarzı görünüm" bölümü üstteki kuralların üstüne yazar.
- **Dokunma:** basılı tutunca yazı seçilmez; yalnızca okuma metni (`.okuma`) ve yazı alanları seçilir. 42 Tarzı kartı yazısının üstünden de kaydırılır (`.deste *{touch-action:pan-y}`; kartın yazı alanı kendi kaydırma kutusu olduğu için gerekli). Cihazda animasyonlar kapalıyken geçişler kapanır ama kartın dönmesi, yaylanması ve yığına uçması kalır.
- **Temalar:** açık (öntanımlı), pembe, koyu, simsiyah. `data-mod` = gunduz/pembe/gece/siyah, `pg.mod`'da hatırlanır, `<head>`'de ilk boyamadan önce kurulur. Ders renkleri doğrulanmış 8'li kategorik palet (açık/koyu ayrı tonlar). Pembe temada büyüklük ölçeği pembe tonları.
- **Service worker** önbelleği `programcilik-v12`. index.html değişince `sw.js`'teki sürüm bir artırılır.

## Test düzeneği (test.zip)

Kurulum (yeni ortamda): `test/tarayici` ve `test/gercek` klasörleri, proje `/home/claude/programcilik` altında varsayılır (yollar gerekirse düzeltilir).

1. İçeriği taklit sunucuya aktar (bir kez):
   `cd test/gercek && rm -rf cikti && python3 sahte_supa.py cikti 8799 &`, ardından proje kökünde
   `SUPABASE_URL=http://127.0.0.1:8799 SUPABASE_GIZLI_ANAHTAR=x node araclar/icerik-aktar.mjs`
   Bu `test/gercek/cikti/yuklenen.json` ve görselleri üretir.
2. `cd test/tarayici && sh kur.sh`: `uygulama/`'yı test ayarlarıyla `site/`'a kopyalar.
3. `python3 -m http.server 8765 --directory <tam yol>/test/tarayici/site` sunucusu arka planda çalışır.
4. Testler (Playwright, Supabase istekleri taklit):
   - `sina.py` (99, iki cihaz/giriş/eşitleme)
   - `alg_sina.py` (51), `eko_sina.py` (33), `vt_sina.py` (63)
   - `buda_sina.py`, `tum_sorular_sina.py` (552 sorunun hepsi)
   - `tasma_sina.py` (`GENISLIK=358` ve `320`)
   - `tema_sina.py`, `ios_sina.py`, `aralik_sina.py`
   - `dokunus_sina.py` (gerçek dokunuşla kart kaydırma, animasyonlar kapalıyken dönme, yazı seçilmemesi)
   - `hedef_sina.py` (hedef sorusu, haftalık azaltma uyarısı, 3 dk kuralı, seri, dondurma, takvim kademeleri, çekmece ve kenardan çekme, göz koruyucu, çıkış penceresi)
   - `saat_cekmece_sina.py` (animasyonlar kapalıyken saatin dönmesi, kenardan açılan menünün tek dokunuşla kapanması; tıklama gelmezse/geri gidilmezse de; takvim çizgi kalınlıkları)
   - `cevrimdisi_sina.py` (giriş → tarayıcı kapanır → internetsiz, oturumu dolmuş sıfırdan açılış → internet gelince gönderim)
   - `takvim_gelecek_sina.py` (2 yıl her gün; `TZ_ADI=Europe/Berlin` ile yaz saati)
   - Taklit sunucuda oturum yenileme (`refresh_token`) gerçekteki gibi aynı oturum kimliğini sürdürür.
   - Test hesaplarında hedef önceden konmuştur (`vt_taban.py`/`sina.py` içinde `hazir_kayit`); çekmece için `cekmece(s, ekran)`, soru penceresi için `onayla(s)`.
   - `istatistik_sina.py` (`GENISLIK=320/390/900`), `kalicilik_sina.py`, `devam_sina.py`
   - Son durumda hepsi eksiksiz geçiyor.
5. Görsel kontrol: `goruntu_sina.py`, `derin_goruntu.py` ve `yeni_goruntu.py` (hedef, takvim, çekmece) (soru türleri, kart, arama, kapsam; `TEMALAR=gunduz,pembe,gece,siyah`), `pafta.py`.

## Elektrik dersi (Temel Elektrik ve Elektronik): sürüyor

- Kaynak: `temel_elektrik_elektronik_st_1.pdf` (206 slayt, 2022–2023 Güz). 14 parçaya (P01–P14), 23 konuya bölündü. Her parça ayrı oturumda yazılır, ayrı bir oturumda bağımsız denetlenir (K12), bulgular kapanır.
- **Yayında (guncelleme-21):** P01–P07 = slayt 1–107, konu 01–12 (210 soru, 95 kart, 141 kavram, 32 görsel). Uçtan uca test (`el_sina.py` 55/55, `tasma_sina.py` 358 ve 320 px 117/117) geçti.
- **Kalan:** P08 (slayt 108–120: 13 pil-akü, 14 renk kodları, 15 topraklama) yazıldı, denetlenmedi. P09 (121–137: 16 direnç çeşitleri) yarım. P10–P14 (138–206: kondansatör, bobin, yarı iletken, diyot, alternatif akım, şebeke-trafo, enerji-Joule) başlanmadı.
- Çalışma düzeni ve yarım işler `elektrik-devam.zip`'te: `PLAN.md` (konu planı, uzlaşımlar), `YAZICI.md` ve `DENETCI.md` (oturum görev tanımları), parça envanterleri, raporlar ve şekil parçaları, `sekiller/yap.sh`, P08 konu dosyaları, test (`el_sina.py`). Birleştirme: envanter parçaları `icerik/envanter/elektrik.md`'ye, şekil parçaları (`00-ortak.py` + `01-devre.py` + `pNN.py`) `araclar/sekiller/elektrik.py`'ye eklenir.
- Hamza'ya sorulan kararlar parça raporlarının 4. bölümündedir; cevaplar gelince ilgili konular düzeltilir.

## Teslim geçmişinin son hâli

- Projenin son hâli: `programcilik.zip` (guncelleme-19'a kadar) + üstüne guncelleme-20 + guncelleme-21 (Elektrik konu 01–12) + guncelleme-22 (görünüm ve dokunma) + guncelleme-23 (hedef, seri, çekmece) + guncelleme-24 (dondurma birikmesi, internetsiz görseller, ikon).
- Önceki küçük paketler (guncelleme-12…19) artık gereksiz.

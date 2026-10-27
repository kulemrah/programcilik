# Kurulum

Bir kez yapılır; sıra önemlidir, adımları yukarıdan aşağıya izle. Supabase, Resend ve GitHub panellerindeki menü adları zamanla değişebilir; aşağıdaki yollar yaklaşık yerleri gösterir.

## Depo düzeni

```
uygulama/            Pages'e yayımlanan kabuk; içinde hiç not yok
icerik/              notlar, sorular, kartlar (yalnızca Supabase'e gider)
araclar/             içerik doğrulayıcı ve aktarıcı
supabase/            veritabanı şeması
.github/workflows/   yayım ve içerik aktarma
```

## 0. Hesaplar

Bu proje gibi okul yan işleri için ayrı adres: `birkulemrah@gmail.com`. Aşağıdaki hesaplar bu adresle açılır:

- **GitHub**: yeni hesap. Kullanıcı adı, sitenin adresinde görünür (`kullaniciadi.github.io/programcilik/`); öğrencilerin gireceği adres budur, ona göre seç.
- **Supabase**: yeni hesap (ister bu adresle, ister yeni GitHub hesabıyla giriş). Ücretsiz plan yeterli.
- **Resend**: yeni hesap (giriş kodu e-postaları için, bölüm 2).
- **Cloudflare**: `eskimezyazi.app` alan adı hangi Cloudflare hesabındaysa DNS kaydı oradan eklenir (bölüm 2). R2 yedeği istenirse (bölüm "Yedek") yeni adresle ayrı bir Cloudflare hesabı açılabilir.

Ücretsiz planların bu projeyi ilgilendiren sınırları:

- **GitHub Free**: private depodan Pages yayımı **yoktur**; GitHub Pro gerekir. Öğrenci adresini GitHub hesabına ekleyip GitHub Education (Student Developer Pack) başvurusu onaylanınca Pro ücretsiz gelir; onay hemen gelmeyebilir. Pro gelene kadar ne yapılacağı bölüm 3'te.
- **Supabase Free**: bir hafta boyunca hiç kullanılmayan proje duraklatılır (tatillerde olabilir). Öğrenciler her gün açtıkça olmaz; olursa panelde projeye girip **Resume project** ile geri açılır, veriler yerinde kalır.
- **Resend Free**: günde 100, ayda 3.000 e-posta. Her giriş bir, cihaz devralma iki e-posta harcar; sınıfın ilk gününe yeter, ama aynı gün herkes birkaç kez kod isterse sınıra yaklaşılabilir.

## 1. Supabase

1. Yeni bir proje oluştur (bölge olarak Avrupa, ör. Frankfurt, gecikme açısından iyidir). Veritabanı parolasını bir yere not et.
2. **SQL Editor**'de `supabase/01-sema.sql` dosyasının tamamını çalıştır. Tekrar çalıştırmak güvenlidir.
3. Aynı yerde kendine hususi yetki ver (42 grubu, Born2beRoot yalnızca böyle görünür; okul adresini küçük harfle yaz):
   ```sql
   insert into public.hususi_yetki (eposta) values ('okul.adresin@kocaelisaglik.edu.tr');
   ```
   Bunu içerik aktarılmadan önce yapmak gerekir (bkz. "Hususi dersler").
4. **Authentication › Sign In / Providers › Email**: Email açık, **Confirm email** açık kalsın. Yeni kayıtlar açık kalsın; kimin kayıt olabileceğini 6. adımdaki kanca belirler.
5. Aynı yerde **Email OTP Length** 6 olsun. **Email OTP Expiration** için 900 saniye (15 dakika) yeterli.
6. **Authentication › Hooks › Before User Created**: türü *Postgres function*, işlev `public.kayit_kapisi`. Bu kanca okul adresi olmayan birine hesap açtırmaz; kod e-postası da gönderilmez. (Ücretsiz planda vardır.)
   Okul alan adı (`kocaelisaglik.edu.tr`) iki yerde yazılıdır: SQL'deki `okul_adresi_mi` işlevi ve kanca mesajı, bir de `index.html` içindeki `AYAR.OKUL_ALANI`. Değişirse ikisi birlikte değişir.
   Giriş yalnızca kodla olur: şema, `auth.users` tablosuna konulan parolayı silen bir tetik kurar (`parola_engeli`). Öğrenci uygulama dışından kendine parola koysa da parolayla giriş yapamaz.
7. **Project Settings › API Keys** (bunları not et, bölüm 3'te kullanılacak):
   - **Publishable key** (`sb_publishable_…`) → `uygulama/index.html` içindeki `AYAR.ANAHTAR`
   - **Secret key** (`sb_secret_…`) → yalnızca GitHub sırrı olarak. Bu anahtar hiçbir dosyaya yazılmaz.
   - Proje adresi (`https://xxxx.supabase.co`) → `AYAR.SUPABASE_URL` ve GitHub değişkeni.

## 2. Giriş kodunun e-postası (Resend)

Supabase'in kendi e-posta servisi yalnızca proje ekibine gönderir; öğrencilere kod gidebilmesi için kendi gönderici adresin gerekir.

1. Resend'de **Domains**'e `posta.eskimezyazi.app` ekle. Ana alan adını değil alt alan adını kullanmak, gönderim itibarını öbür işlerinden ayırır.
2. Resend'in verdiği DNS kayıtlarını Cloudflare'de `eskimezyazi.app` bölgesine ekle; alan adı "Verified" olana kadar bekle.
3. Resend'de bir API anahtarı oluştur (yalnız gönderme yetkili).
4. Supabase **Authentication › Emails › SMTP Settings**:
   - Host `smtp.resend.com`, port `465`, kullanıcı adı `resend`, parola: Resend API anahtarı
   - Gönderen adres `giris@posta.eskimezyazi.app`, gönderen adı `Programcılık`
5. **Authentication › Rate Limits**: saatlik e-posta sınırını sınıfın ilk gün hep birlikte girebileceği kadar yükselt (ör. 100). Resend'in günlük 100 sınırı ayrıca geçerlidir.
6. **Authentication › Emails › Templates**: hem **Confirm signup** hem **Magic Link** şablonuna aynı metni koy. Yeni öğrenciye ilki, eskiye ikincisi gider; ikisinde de bağlantı değil kod olmalı. Uygulama öğrencilere "siz" diye hitap eder; e-posta da öyle:

   Konu:
   ```
   Programcılık giriş kodunuz: {{ .Token }}
   ```
   Gövde:
   ```html
   <p>Programcılık uygulamasına giriş kodunuz:</p>
   <p style="font-size:28px;font-weight:bold;letter-spacing:6px">{{ .Token }}</p>
   <p>Bu kod uygulamaya giriş ya da hesabınızı başka bir cihaza geçirmek için istendi ve 15 dakika geçerlidir.</p>
   <p>İsteği siz yapmadıysanız bu e-postayı dikkate almayın; kod girilmedikçe hesabınız başka cihaza geçmez.</p>
   ```

Supabase aynı adrese en çok dakikada bir e-posta gönderir (**Authentication › Rate Limits**'teki kullanıcı başı aralık). Uygulama cihaz devralma kodunda bu süreyi sayaçla bekletir; bu değeri değiştirirsen `index.html` içindeki `KOD_ARALIGI` da aynı olmalı.

## 3. GitHub

1. Yeni bir **private** depo aç (ör. `programcilik`). Henüz dosya yükleme.
2. **Settings › Secrets and variables › Actions**:
   - **Variables** sekmesi: `SUPABASE_URL` = proje adresi
   - **Secrets** sekmesi: `SUPABASE_GIZLI_ANAHTAR` = Supabase secret key
3. `uygulama/index.html` içindeki `AYAR` bölümünü doldur:
   ```js
   SUPABASE_URL: "https://xxxx.supabase.co",
   ANAHTAR: "sb_publishable_…",
   OKUL_ALANI: "kocaelisaglik.edu.tr",
   TASHIH_EPOSTA: "birkulemrah@gmail.com"   // dolduruldu
   ```
   `SUPABASE_URL`, `ANAHTAR` ve `TASHIH_EPOSTA` dolu değilse uygulama giriş ekranında "yapılandırılmadı" uyarısı verir. Tashih adresi sözleşmede ve hesap panelinde öğrencilere görünür.
4. Bu klasörün tamamını depoya yükle (`uygulama/`, `icerik/`, `araclar/`, `supabase/`, `.github/`, `KURULUM.md`). İki dikkat: proje 180'den fazla dosyadır, GitHub'ın web sayfasından tek seferde en çok 100 dosya yüklenir; ve `.github` klasörü noktayla başladığı için bazı sistemlerde gizli görünür, yüklenmezse otomatik işler hiç çalışmaz. Bu yüzden terminalden git ile yüklemek en sağlamıdır (klasörün içindeyken):
   ```bash
   git init                       # bu klasörü bir git deposu yapar
   git config user.name "KULLANICIADI"              # kayıtlarda görünecek ad; --global yazılmadığı için yalnızca bu depoda geçerli,
   git config user.email "birkulemrah@gmail.com"    # öbür projelerindeki kimliğine dokunmaz
   git add .                      # bütün dosyaları (gizli .github dahil) gönderilecekler listesine ekler; nokta "bu klasör" demek
   git commit -m "İlk yükleme"    # o listeyi bir kayıt (commit) olarak saklar; -m kaydın açıklamasıdır
   git branch -M main             # dalın adını main yapar (iş akışları main dalını dinler)
   git remote add origin https://github.com/KULLANICIADI/programcilik.git   # GitHub'daki depoyu "origin" adıyla tanıtır
   git push -u origin main        # kaydı GitHub'a gönderir; -u bundan sonra yalnızca "git push" yazmayı yeter kılar
   ```
   Sonuncusu GitHub kullanıcı adını ve parola yerine bir **erişim anahtarı** ister: **Settings › Developer settings › Personal access tokens**'tan, yalnızca bu depoya, **Contents** ve **Workflows** için okuma-yazma izniyle oluştur (Workflows izni olmazsa `.github/workflows` dosyaları reddedilir); GitHub Desktop kullanılırsa bu adımlar düğmelerle yapılır. Çıktıda `main -> main` görünmesi yüklemenin bittiği anlamına gelir. Yükleme iki işi başlatır (**Actions** sekmesi):
   - *İçeriği aktar*: `icerik/` klasörünü doğrulayıp Supabase'e yükler. Ücretsiz hesapta da çalışır.
   - *Uygulamayı yayımla*: `uygulama/` klasörünü Pages'e koyar. **GitHub Pro yoksa bu iş hata verir** (aşağıya bak).
5. Pages: **Settings › Pages › Source**: *GitHub Actions*. Pro geldikten sonra **Actions › Uygulamayı yayımla › Run workflow** ile yayımı başlat.

### GitHub Pro gelene kadar

Private depo Pages'e çıkamaz. Notlar zaten Supabase'de olduğu için yalnızca uygulamanın kabuğu (içinde not olmayan `uygulama/` klasörü) için şu yollardan biri seçilir:

- **Bekle**: öğrenci başvurusu onaylanıp Pro gelince 5. adım. O zamana kadar *Uygulamayı yayımla* işini **Actions › Uygulamayı yayımla › ⋯ › Disable workflow** ile kapatabilirsin; kırmızı çarpılar birikmez.
- **Ayrı, herkese açık bir site deposu**: ikinci bir **public** depo aç (ör. `programcilik-site`), içine yalnızca `uygulama/` klasörünün **içindekileri** yükle, **Settings › Pages › Source**: *Deploy from a branch*, dal `main`, klasör `/ (root)`. Bu depoda not yoktur; yayımlanabilir anahtar zaten herkese açık olacak şekilde tasarlandı (verileri RLS kuralları korur). Uygulamada değişiklik olunca `uygulama/` dosyalarını bu depoya da yükle. Pro gelince bu depo silinip ana depodan yayıma geçilebilir; adres değişeceği için öğrencilere yeni adres verilir.

Site adresi belli olunca Supabase'de **Authentication › URL Configuration › Site URL** alanına bu adresi yaz (ör. `https://kullaniciadi.github.io/programcilik/`). Giriş bağlantıyla değil kodla olduğu için yönlendirme kullanılmaz; bu ayar yalnızca Supabase'in varsayılan adresi (`localhost`) yerine doğru adresin durması içindir. **Redirect URLs** listesine bir şey eklemek gerekmez.

Pages sitesi herkese açıktır ama içinde not yoktur. Notlar yalnızca okul adresiyle kod girip sözleşmeyi onaylayan hesaplara veritabanından gelir.

## 4. İlk deneme

1. Siteyi telefondan aç, okul adresinle kod iste; kodun gelen kutusuna mı gereksiz klasörüne mi düştüğüne bak.
2. Kodu gir, sözleşmeyi onayla. Oku sekmesinde 1. Sınıf › Güz derslerini ve 42 grubunu (hususi) görmelisin.
3. Okul dışı bir adresle kod istemeyi dene: "Yalnızca @kocaelisaglik.edu.tr…" uyarısı gelmeli.
4. iPhone'da Safari'den **Paylaş › Ana Ekrana Ekle**, Android'de tarayıcının menüsünden **Uygulamayı yükle** ile kur ve ana ekrandan açıp yeniden giriş yap.

## Cihaz sınırı

Bir hesap aynı anda en çok **azami cihaz** sayısı kadar cihazda açık olabilir; öntanımlı değer 1'dir. Kural veritabanında işler (`01-sema.sql`, "Cihaz sınırı" bölümü); Supabase'in ücretli "tek oturum" ayarı gerekmez.

- Boş yer varsa giriş soru sorulmadan olur. Sınır doluysa, kod doğrulandıktan sonra "Diğer cihazınızdan çıkış yapmak için mailinize kod gelsin mi?" diye sorulur. Evet denirse e-postaya ikinci bir kod gider; o kod girilince **en uzun süredir kullanılmayan** cihaz çıkarılır ve hesap yeni cihazda açılır. Sınırı 2 olan bir öğrencinin öbür cihazı açık kalır.
- Sunucu devralma isteğini yalnızca son 30 dakikada kodla açılmış bir oturumdan alır, devralmayı da yalnızca istekten **sonra** açılmış bir oturuma tanır; ikinci kod adımı uygulama değiştirilerek ya da eski bir oturum saklanarak atlanamaz. İstek 30 dakika geçerlidir.
- Çıkarılan cihaz notlara erişimini hemen kaybeder; bir sonraki eşitlemede (açılışta, öne gelince ya da en geç 5 dakikada) kendi verisini silip giriş ekranına döner. Hesaba gönderemediği değişiklikler kaybolur.
- Uygulamadan "Çıkış yap" ile çıkılırsa yer boşalır; sıradaki cihaz soru sorulmadan girer. Bağlantı yokken çıkılmak istenirse uygulama, yerin hesapta dolu kalacağını söyleyip sorar.
- Okunan konular, boyalar, yıldızlar, yanlışlar ve kart sonuçları hesapta tutulur; açık cihazlar arasında her eşitlemede güncellenir.

### Bir öğrencinin sınırını artırmak

Öğrenci en az bir kez giriş yapmış olmalı (satırı ilk girişte açılır). **Table Editor › hesap_cihazlari**'nda öğrenciyi `eposta` sütunundan bulup `azami_cihaz` değerini değiştir (1–10), ya da SQL Editor'de:

```sql
update public.hesap_cihazlari
set azami_cihaz = 2
where eposta = 'ad.soyad@kocaelisaglik.edu.tr';
```

Değer anında geçerli olur; öğrencinin ikinci cihazı soru sorulmadan girer. Sınırı düşürürsen fazla cihazlar, en uzun süredir kullanılmayandan başlayarak hemen notlara erişimini kaybeder ve bir sonraki eşitlemede giriş ekranına döner.

### Cihaz değişim sayacı

Bir oturum her cihaz yeri aldığında `cihaz_degisim_sayisi` bir artar; ilk giriş de sayılır. Belirtecin kendiliğinden yenilenmesi sayılmaz, çıkış yapıp yeniden girmek sayılır. Sınırı 1 olan öğrencide X'te giriş → Y'ye geçiş → yeniden X = 3. Sınırı 2 olan öğrenci aynı iki cihazı kullandıkça sayaç 2'de kalır; üçüncü bir cihaz eklenince artar.

En çok değişim yapan hesaplar:

```sql
select eposta, azami_cihaz, cihaz_degisim_sayisi
from public.hesap_cihazlari
order by cihaz_degisim_sayisi desc
limit 20;
```

Bir hesabın geçmişi (zaman, yol, tarayıcı bilgisi). Tarayıcı bilgisi Supabase'in oturum kaydından alınır; iki farklı telefonun sırayla birbirinden hesabı devraldığı burada görünür:

```sql
select g.zaman, g.yol, g.tarayici
from public.cihaz_gecmisi g
join public.hesap_cihazlari h using (kullanici)
where h.eposta = 'ad.soyad@kocaelisaglik.edu.tr'
order by g.zaman;
```

`yol` sütunu `serbest` (boş yere girdi) ya da `devralma` (bir cihazı çıkararak girdi) değerini alır. Bu kayıtların tutulduğu kullanım sözleşmesinde yazar.

Öğrenci telefonunu kaybederse yeni cihazdan girip devralma koduyla hesabı alır; en uzun süredir kullanılmayan cihaz (kaybolan telefon) çıkarılır. Senin bir şey yapman gerekmez.

## Hususi dersler

`icerik/agac.json`'da `"hususi": true` yazılan grup (şu an 42 grubu, içinde Born2beRoot) yalnızca hususi yetkisi olan hesaplarda görünür. Ağaçtaki yeri, notları, soruları, kartları ve görselleri de yalnızca o hesaplara iner. Kural veritabanında işler (`01-sema.sql`: `hususi_yetki` tablosu, `agac` ve `konular` kuralları, görsel kuralı).

Kendine (ya da başka birine) yetki vermek için SQL Editor'de, okul adresini küçük harfle yazarak:

```sql
insert into public.hususi_yetki (eposta) values ('ad.soyad@kocaelisaglik.edu.tr');
```

Ya da **Table Editor › hususi_yetki › Insert row**. Yetkiyi geri almak:

```sql
delete from public.hususi_yetki where eposta = 'ad.soyad@kocaelisaglik.edu.tr';
```

Yetki bir sonraki eşitlemede işler (uygulama açılınca, öne gelince ya da en geç 5 dakikada): verilince hususi dersler kendiliğinden iner ve görünür, geri alınınca notları ve önbelleğe alınmış görselleri cihazdan silinir. (Okundu, boya gibi kişisel kayıtlar hesapta kalır; yetki geri gelince yerlerine oturur.)

Sıra önemli: dosyaları depoya **yüklemeden önce** `01-sema.sql`'i çalıştır ve kendine yetkiyi ver (bölüm 1, 2. ve 3. adım). Yükleme `icerik/` ve `araclar/` klasörlerine dokunduğu için *İçeriği aktar* hemen çalışır; şema yoksa iş durur ve hiçbir şey yüklenmez. Öyle olursa şemayı çalıştırıp işi **Actions › İçeriği aktar › Run workflow** ile yeniden başlat. Yetkiyi vermeden içerik aktarılırsa 42 grubu senin uygulamanda görünmez; yetkiyi verince bir sonraki eşitlemede gelir.

## Günlük kullanım

- Yeni not, soru ya da kart: `icerik/dersler/<ders>/` altına dosyaları koy ve gönder. Görseli düzeltmek için aynı adla değiştirmen yeterli; cihazlar yenisini indirir. *İçeriği aktar* yalnızca değişen konuları yükler; bir hata varsa hiçbir şey yüklemez ve hatanın yerini yazar. Biçim: `icerik/BICIM.md`.
- Yeni ders: önce `icerik/agac.json`'a ekle, sonra ders klasörünü aç.
- Bir konuyu silmek: dosya çiftini depodan kaldır. Aynı anda çok sayıda konu silinecekse iş durur; bilerek yapıyorsan *İçeriği aktar*'ı **Run workflow** ile elle çalıştırıp "Çok sayıda konunun silinmesine izin ver" kutusunu işaretle.
- Bir güncellemede `supabase/01-sema.sql` da değiştiyse önce onu SQL Editor'de çalıştır, sonra uygulamayı yayımla. (Uygulama yeni bir kayıt türünü şemadan önce kullanırsa o kayıtlar cihazda bekler, şema güncellenince gönderilir.)
- Uygulamada değişiklik yaptıktan sonra `uygulama/sw.js` içindeki `ONBELLEK` satırında sürümü bir artır (`"v2"` ise `"v3"` gibi); kurulu uygulamalar yeni sürümü böyle alır.
- Uygulama ayrı bir site deposundan yayımlanıyorsa (bölüm 3, "GitHub Pro gelene kadar") değişen `uygulama/` dosyalarını o depoya da yükle.
- `supabase.js` kütüphanesini yenilersen `index.html` ve `sw.js` içindeki `supabase.js?v=…` sürümünü de değiştir; yoksa cihazlar bir açılış boyunca eski kütüphaneyle çalışır.
- Sözleşme metnini değiştirirsen `SOZLESME.surum` (index.html) ve `public.sozlesme_surumu()` (SQL) birlikte artırılır; herkes yeni metni yeniden onaylar.
- Yeni bir bölüm (program) eklemek: `public.programlar` tablosuna satır ekle. Birden fazla program olunca uygulama girişte bölüm sorar.

## Yedek

Supabase'in ücretsiz planında otomatik yedek yok. Defter için kurduğun gecelik şifreli R2 yedeğinin aynısını bu proje için de (yeni adresle açılacak Cloudflare hesabında) kurmak, öğrencilerin ilerlemesini (kayitlar ve profiller tabloları) ve cihaz kayıtlarını (hesap_cihazlari, cihaz_gecmisi) güvenceye alır. Notların asıl kopyası zaten bu depodadır.

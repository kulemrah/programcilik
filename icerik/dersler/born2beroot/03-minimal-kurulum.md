### Neden grafik arayüz (X.org / Wayland) yasak — sunucu felsefesi
Sunucu, arka planda hizmet veren, önünde oturup fare tıklanmayan bir makinedir. X.org/Wayland gibi grafik sunucuları hem gereksiz kaynak tüketir hem de saldırı yüzeyini büyütür (daha fazla paket = daha fazla güvenlik açığı ihtimali). Subject bunu, kurulu bulunursa notunuzun SIFIR olacağı kadar ciddiye alıyor — kurulum sırasında "masaüstü ortamı" (GNOME, Xfce vb.) seçeneğini KESİNLİKLE işaretlemeyin.

### Netinstall / minimal kurulum akışı
Debian netinst ISO'sunu indirin (küçük boyutlu, kurulum sırasında internetten paket çeker). Sihirbazda: dil/klavye seçin > hostname girin (login+42 formatında, örn. htopakta42 — baştan doğru girin) > disk partisyonlama ekranına gelin (bkz. bölüm 4) > paket seçim ekranında SADECE "SSH server" ve "standard system utilities" işaretli kalsın, masaüstü ortamı seçeneklerini MUTLAKA kaldırın.

### Kurulum sırasında dikkat edilecek ekranlar (disk, ağ, paket seçimi)
En kritik üç an: (1) partisyon ekranı — "Manuel" seçilir, LVM+şifreleme adımını siz yönetirsiniz, (2) paket seçim ekranı — masaüstü ortamı işaretlerini temizleyin, (3) GRUB boot loader ekranı — ana diske kurulmasını onaylayın, aksi hâlde VM açılmaz.

### Klavye düzeni tuzağı
Kurulumda seçtiğiniz klavye düzeni, sonradan parola yazarken de geçerli olur. Türkçe düzende `q w x` ve özellikle `. , : / -` gibi işaretler İngilizce düzendekinden farklı tuşlara düşer. Parolanızda özel karakter varsa ve düzen beklediğinizden farklıysa doğru parolayı yazdığınız hâlde giremezsiniz — üstelik ekranda yıldız göründüğü için sebebini de göremezsiniz. İki korunma yolu: kurulumda hangi düzeni seçtiğinizi not edin ya da parolayı yalnızca harf ve rakamdan kurun (politika zaten büyük/küçük harf + rakam istiyor, özel karakter şart değil). Aynı tuzak LUKS parolası için de geçerli ve orada bedeli daha ağır: diski açamazsanız kurulumu baştan yapmak zorunda kalırsınız.

### Kurulumdan sonra GUI kalıntısı sızmadığını doğrulama
```bash
dpkg -l | grep -iE 'xserver|wayland|gnome|xfce'
```
Bu komut boş dönmeli. Bir şey listelenirse `sudo apt purge <paket>` ile kaldırın — GUI kalıntısı savunmada doğrudan not kaybı demektir; kurulumdan hemen sonra kontrol etmeyi alışkanlık hâline getirin.

### Kurulum bitince muhtemelen elle kurmanız gereken paketler
Minimal netinstall'da "SSH server" + "standard system utilities" dışında çoğu şey yok — özellikle `sudo` ve `ufw` çoğu zaman kurulu GELMEZ:
```bash
apt install sudo ufw
```
(root olarak, çünkü henüz sudo yok). Bu adım atlanırsa bölüm 7 (firewall) ve bölüm 11 (sudo) çalışmaya başlayamaz bile.

### Kurulumdan sonraki iş sırası
Karışmasın diye net bir sıra: (1) GUI kalıntısı var mı diye bakın, (2) root'a geçip `sudo` ve `ufw` paketlerini kurun, kendinizi sudo grubuna ekleyin, (3) SSH'ı 4242'ye taşıyıp port yönlendirmeyi ayarlayın ve ana makineden bağlanabildiğinizi doğrulayın. Üçüncü adım bittiği anda projenin geri kalanını host terminalinden, kopyala-yapıştır ederek yapabilirsiniz (bölüm 6) — bu yüzden onu erkene almak baştaki en kârlı yatırımdır.

### İlk açılışta root'a geçmek ve dosyaları düzenlemek
Kurulumdan sonra kendi kullanıcınızla giriş yaparsınız, ama o kullanıcı henüz sudo grubunda değildir. Root'a şöyle geçersiniz:
```bash
su -
```
(kurulumda belirlediğiniz root parolasını ister; `-` işareti root'un kendi ortamını da yükler). Root'ken `apt install sudo ufw` yapar, kendinizi sudo grubuna ekler (bölüm 9), sonra `exit` ile kendi kullanıcınıza dönersiniz.

Config dosyalarını düzenlemek için grafik arayüz olmadığından terminal editörü kullanılır: `nano` (basit; kaydet Ctrl+O, çık Ctrl+X) ya da `vim`. Minimal kurulumda ikisi de gelmemiş olabilir, o zaman `apt install nano` yeterli. Tek istisna sudoers dosyasıdır: ona hiçbir zaman doğrudan editörle dokunmayın, `visudo` kullanın (bölüm 11).

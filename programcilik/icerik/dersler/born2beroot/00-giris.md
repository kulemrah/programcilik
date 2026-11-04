### Projenin amacı ve değerlendirme mantığı
Born2beRoot, 42 müfredatının ilk sistem yönetimi projesi. Amaç: VirtualBox (ya da UTM) içinde Debian tabanlı, GUI'siz, minimal ve güvenli bir sunucu kurup katı kurallara göre yapılandırmak. Değerlendirme "kod oku" şeklinde değil — bir peer (ya da personel) VM'inizi AÇIP CANLI geziyor: SSH ile bağlanıyor, sudo deniyor, yeni kullanıcı açtırıyor, monitoring.sh'i durdurmanızı istiyor, hostname değiştirtiyor. Bilmeniz gereken şey ezberlenmiş bir kurulum değil, YAŞAYAN bir sistemi anlık açıklayabilme becerisi.

### Teslimat sadece README.md + signature.txt; VM canlı olarak incelenir
Git reposuna SADECE bu iki dosya konur, VM'in kendisi asla eklenmez — mekanizmanın tamamı bölüm 14'te.

### 42'nin AI politikasıyla ilişkisi: bu rehber bir anlama aracıdır, çözüm kaynağı değil
Bu yüzden hazır config dosyaları değil kavram ve örnek sözdizimi sunuyor — gerçek dosyaları VM'de SİZ yazacaksınız, savunmada "neden bu değeri verdiniz" sorusuna cevap verebilmeniz gerekiyor.

### Rehberi okurken izlenecek sıra: önce kavram, sonra komut, sonra "neden" sorusu
Her alt başlığı üç soruyla okuyun: (1) Bu ne — kavram ne anlatıyor? (2) Nasıl yapılır — hangi komut/dosya? (3) Neden böyle — alternatifi ne olurdu, savunmada nasıl sorulabilir? Bu üçlü hem ezber yerine kavrama sağlar hem savunmaya hazırlar.

### Hızlı Kavram Sözlüğü — okumaya başlamadan önce göz atın
```
VM (Sanal Makine) : Fiziksel bilgisayar içinde çalışan, bağımsız bir bilgisayar simülasyonu
Hypervisor         : VM oluşturup yöneten yazılım (VirtualBox, UTM gibi)
Partition          : Bir diskin ayrılmış bölümü
Mount point        : Bir partition'ın dizin ağacında göründüğü yer (/, /boot, /home gibi)
sudo               : Yetkili komutları geçici olarak, iz bırakarak çalıştırma aracı
Firewall           : Ağ trafiğini kurallara göre süzen güvenlik katmanı
```
Daha ileri terimler (LVM, LUKS, PAM, MAC/DAC, cron, systemd...) kendi bölümlerinde açıklanıyor ve savunma öncesi tekrar için Ek bölümünde topluca listeleniyor — burada tekrar edilmiyor.

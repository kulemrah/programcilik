### SSH'ın çalışma mantığı (kısaca)
SSH (Secure Shell), bir makineye ağ üzerinden şifreli şekilde uzaktan komut satırı erişimi sağlayan protokol/servistir. Sunucu tarafında sshd (SSH daemon) dinlemede olur, istemci `ssh` komutuyla bağlanır. Bu proje SSH'ı savunmanın omurgası yapar: değerlendirici VM'inize SSH ile bağlanıp gerçek zamanlı test yapacak.

### sshd_config üzerinden port değişikliği (22 → 4242)
`/etc/ssh/sshd_config` dosyasında:
```
Port 4242
```
satırını ekleyin/düzenleyin. Değişiklikten sonra servisi yeniden başlatın:
```bash
sudo systemctl restart sshd
```

### Root ile SSH girişinin kapatılması (PermitRootLogin no)
Aynı dosyada:
```
PermitRootLogin no
```
Bu, root'un doğrudan SSH ile giriş yapmasını engeller — root'a HER ZAMAN normal kullanıcı+sudo üzerinden erişilmeli, asla doğrudan değil.

### Servisi yeniden başlatma ve port dinlediğini doğrulama (ss -tunlp)
```bash
sudo systemctl restart sshd
sudo ss -tunlp | grep 4242
```
Çıktıda 4242 portunun LISTEN durumda ve sshd'ye ait olduğunu görmelisiniz. Süreç adı (sshd) yalnızca sudo ile çalıştırınca görünür.

### Önce SSH'ı ayarlayın, gerisini host'tan bağlanarak yapın
VirtualBox penceresi ile ana makineniz arasında pano paylaşımı yoktur: VM konsolunda her şeyi harf harf elle yazarsınız; uzun bir `secure_path` satırını ya da pwquality kurallarını böyle yazmak hem yorucu hem hataya açıktır. Bu yüzden SSH, kurulum sonrası sıradaki üçüncü ama en kârlı adımdır (bu bölüm + bölüm 1'deki port yönlendirme; sıranın tamamı bölüm 3'te). SSH çalışır çalışmaz ana makinenizin kendi terminalinden bağlanırsınız:
```bash
ssh login@127.0.0.1 -p 4242
```
Artık kopyala-yapıştır, kaydırma ve düzgün bir terminal kullanabilirsiniz; projenin geri kalanını böyle yapmak hem çok daha hızlıdır hem yazım hatalarını keser. Ayrıca SSH'ın gerçekten dışarıdan çalıştığını da her gün doğrulamış olursunuz.

### Savunmada yeni hesapla bağlantı testi
Değerlendirici "yeni bir hesap açalım, onunla SSH ile bağlanalım" diyecek — yani hem kullanıcı açma pratiğini hem SSH'ın gerçekten 4242'de ve root'suz çalıştığını AYNI ANDA test ediyor. Bu ikisini birlikte prova edin.

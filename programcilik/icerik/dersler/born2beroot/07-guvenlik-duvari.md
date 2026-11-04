### Firewall mantığı: varsayılan red, istisna izin
Bir firewall, gelen/giden ağ trafiğini kurallara göre süzer. Bu projede felsefe "varsayılan red, istisna izin": HER ŞEY kapatılır, yalnızca ihtiyaç duyulan tek port (4242) açılır.

### UFW ile sadece 4242 portunu açma (Debian)
```bash
sudo ufw allow 4242/tcp
sudo ufw enable
sudo ufw status
```
UFW (Uncomplicated Firewall), Debian'da iptables'ı basitleştiren bir ön yüzdür. `ufw allow` yalnızca kural ekler; güvenlik duvarını `ufw enable` açar ve onu her açılışta da etkin kılar.

### firewalld ile zone / service / port kavramları (Rocky)
```bash
sudo firewall-cmd --permanent --add-port=4242/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```
UFW'den farklı olarak "zone" (bölge) kavramı vardır — her arayüz bir zone'a atanır, kurallar zone bazlı tanımlanır. `--permanent` olmadan yapılan değişiklik reboot'ta kaybolur, `--reload` ile devreye alınır.

### Açılışta otomatik aktif olacak şekilde servis etkinleştirme
```bash
sudo ufw enable                         # Debian: hem şimdi hem her açılışta etkin
sudo systemctl is-enabled ufw           # servisin açılışta başladığını doğrula: enabled
sudo systemctl enable --now firewalld   # Rocky: başlat ve açılışa ekle
```
Subject açıkça "firewall VM başlar başlamaz aktif olmalı" diyor. Debian'da bunu `ufw enable` kendisi sağlar: `/etc/ufw/ufw.conf` dosyasına `ENABLED=yes` yazar; ufw servisi de paket kurulunca açılışta başlayacak şekilde gelir. `systemctl is-enabled ufw` ile bunu doğrularsınız; `disabled` çıkarsa `sudo systemctl enable ufw` yazın. VM'i yeniden başlatıp `sudo ufw status` ile "Status: active" gördüğünüzü kontrol edin.

### Durum doğrulama: ufw status, firewall-cmd --state / --list-ports
```bash
sudo ufw status
sudo firewall-cmd --state
sudo firewall-cmd --list-ports
```
Savunmadan hemen önce bu kontrolü alışkanlık hâline getirin.

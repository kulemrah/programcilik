### Betiğin görevi ve wall komutunun rolü
Betiğin görevi sistem durumunu (CPU, RAM, disk, ağ vb.) TÜM açık terminallere yayınlamaktır. Bunu `wall` komutu yapar — sistemdeki tüm oturum açmış kullanıcıların terminaline mesaj basar (broadcast).

### İstenen bilgi kalemleri ↔ hangi komut/dosya eşleştirmesi
```
Mimari/kernel     : uname -a
Fiziksel CPU      : lscpu | grep "Socket(s)"
vCPU              : nproc
RAM kullanımı     : free -m
Disk kullanımı    : df -h /
CPU yükü          : top -bn1 | grep "Cpu(s)"  (mpstat de olur ama sysstat paketi ister)
Son reboot        : who -b  (ya da uptime -s)
LVM aktif mi      : lsblk | grep lvm  (ya da vgs)
Aktif bağlantı    : ss -ta | grep ESTAB | wc -l
Kullanıcı sayısı  : who | wc -l
IP + MAC          : ip a  (tek komut yeter — "inet" satırı IP, "link/ether" satırı MAC)
sudo komut sayısı : /var/log/sudo/ log dosyasındaki satır/komut sayısı
```
Bu tablo bölüm 11'deki log_output ile bağlantılı: sudo sayacı için orada kurulan log dosyası grep'lenir.

### Betiği çalıştırılabilir yapma: shebang ve chmod
Betiğin en üstüne `#!/bin/bash` (shebang) satırını koyun, sonra çalıştırma izni verin:
```bash
chmod +x /usr/local/bin/monitoring.sh
```
Bu ikisi olmadan cron betiği DOĞRUDAN çalıştıramaz — "yazdığım script çalışmıyor" şikâyetlerinin en sık nedeni budur.

### Açılışta ve her 10 dakikada çalıştırma: cron (@reboot, */10 * * * *)
```bash
crontab -e
```
```
@reboot /usr/local/bin/monitoring.sh
*/10 * * * * /usr/local/bin/monitoring.sh
```
İlk satır açılışta bir kez, ikinci satır her 10 dakikada bir çalıştırır.

### Savunmada betiği değiştirmeden durdurma
Subject, script'i DEĞİŞTİRMEDEN durdurmanızın isteneceğini söylüyor. Cevap script'i silmek/düzenlemek DEĞİL — cron job'unu geçici olarak devre dışı bırakmaktır:
```bash
crontab -e   # ilgili satırın başına # koyun, kaydedin
```

### Hatasız (stderr'siz) çalışmayı garanti etme
Değişkenlerin boş dönebileceği durumları (ör. hiç sudo komutu çalıştırılmamışsa log dosyası boş) kontrol edin, bulunamayan komutların hata basmasını engelleyin — subject "hiçbir hata gösterilmemeli" diyor; bu, kelimenin tam anlamıyla ciddiye alınmalı.

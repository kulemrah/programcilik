### hostname, /etc/hostname, /etc/hosts ilişkisi
`/etc/hostname` makinenin adını tek satır olarak tutar. `/etc/hosts` ise IP-isim eşleşmelerini tutar; genelde 127.0.1.1 satırında hostname'in de geçmesi gerekir, yoksa bazı komutlar (sudo dahil) yavaşlar/hata verir.

### login+42 formatı (örnek: htopakta42)
Hostname'in 42 login'iniz + "42" olması gerekiyor (subject'teki örnek wil42; kendi login'inize göre karşılığını kullanın).

### Kalıcı değiştirme (hostnamectl) ve savunmada anlık değiştirme farkı
```bash
sudo hostnamectl set-hostname yenihostname
```
Bu komut hem `/etc/hostname`'i günceller hem anlık uygular (reboot gerekmez, ama yeni terminal/oturum açmanız gerekebilir). Subject, savunma sırasında hostname'i DEĞİŞTİRTECEĞİNİ söylüyor — bu komutu ezbere bilmeniz gerekiyor, çünkü canlı, izlenerek yapacaksınız.

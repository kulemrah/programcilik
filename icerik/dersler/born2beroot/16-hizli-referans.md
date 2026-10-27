### Sık karışan terimlerin tek satırlık tanımları
```
LVM      : Esnek disk/partition yönetim katmanı (PV → VG → LV)
LUKS     : Linux disk şifreleme standardı
PAM      : Eklenti tabanlı kimlik doğrulama çerçevesi
MAC      : Mandatory Access Control — sistem çapında zorunlu erişim kısıtı
DAC      : Discretionary Access Control — klasik sahip/izin sistemi
TTY      : Gerçek bir terminal oturumu
cron     : Zamanlanmış görev çalıştırıcı
systemd  : Modern Linux servis/başlatma yöneticisi (systemctl ile kontrol edilir)
```

### Hızlı doğrulama komutları listesi
```bash
sestatus              # SELinux durumu (Rocky)
aa-status              # AppArmor durumu (Debian)
ufw status             # Firewall durumu (Debian)
firewall-cmd --state   # Firewall durumu (Rocky)
sudo ss -tunlp          # Dinleyen portlar
chage -l login         # Parola politikası durumu
crontab -l             # Zamanlanmış görevler
lsblk / vgs / lvs       # LVM yapısı
```

### Savunmadan önce son gözden geçirme kontrol listesi
(1) VM'de hiçbir snapshot olmadığını kontrol edin. (2) `sudo ufw status` ile firewall'da yalnızca 4242'nin açık olduğunu doğrulayın. (3) `aa-status` ile AppArmor'ın enforce/aktif olduğunu doğrulayın. (4) `chage -l` ile parola politikasının TÜM hesaplara (root dahil) uygulandığını doğrulayın. (5) `crontab -l` ile monitoring.sh'in kayıtlı olduğunu doğrulayın. (6) `hostnamectl status` ile hostname'in doğru formatta olduğunu doğrulayın.

### Kurulum iş sırası (makine başında)
1. VirtualBox'ta VM'i oluşturun: RAM, sanal disk, Debian ISO bağlantısı — bölüm 1
2. Ağ modunu ayarlayın: port yönlendirme ya da köprülenmiş adaptör — bölüm 1
3. Netinstall'ı çalıştırın; hostname login+42, masaüstü ortamı işaretsiz — bölüm 3
4. Manuel partisyonlama: /boot + şifreli LVM (root, swap, home) — bölüm 4
5. Kurulum sonrası GUI kalıntısı kalmadığını doğrulayın — bölüm 3
6. `su -` ile root'a geçin, `apt install sudo ufw` çalıştırın — bölüm 3
7. Kendi kullanıcınızı user42 ve sudo gruplarına ekleyin — bölüm 9
8. SSH'ı 4242'ye taşıyın, PermitRootLogin no yapın, servisi yeniden başlatın — bölüm 6
9. Ana makineden SSH ile bağlanabildiğinizi doğrulayın; gerisini böyle yapın — bölüm 6
10. UFW'de yalnızca 4242'yi açın, `ufw enable` ile etkinleştirin (açılışta da etkin kalır) — bölüm 7
11. AppArmor'ın açılışta aktif olduğunu `aa-status` ile doğrulayın — bölüm 5
12. login.defs ve pwquality.conf ile parola politikasını yazın — bölüm 10
13. chage ile var olan hesaplara uygulayın, root dahil tüm parolaları değiştirin — bölüm 10
14. visudo ile sudo kurallarını yazın, /var/log/sudo klasörünü oluşturun — bölüm 11
15. monitoring.sh'i yazın, çalıştırılabilir yapın, cron'a @reboot ve */10 ekleyin — bölüm 12
16. README.md'yi yazın: dört karşılaştırma ve AI kullanımı dahil — bölüm 13
17. Disk imzasını alın, signature.txt'ye yazın, VM'i repoya KOYMAYIN — bölüm 14

### Savunma öncesi kontrol listesi
- VM'de hiç snapshot kalmadı — bölüm 14
- `sudo ss -tunlp` ile SSH'ın 4242'yi dinlediği görünüyor — bölüm 6
- `sudo aa-status` ile AppArmor aktif — bölüm 5
- `sudo ufw status` ile firewall aktif ve tek kurallı — bölüm 7
- `sudo chage -l` ile politika root dahil tüm hesaplarda — bölüm 10
- `crontab -l` ile monitoring.sh kayıtlı — bölüm 12
- `hostnamectl status` ile hostname login+42 biçiminde — bölüm 8
- `lsblk` ile şifreli LVM yapısı görünüyor — bölüm 4
- GUI paketi sızmamış (`dpkg -l | grep xserver`) — bölüm 3
- README.md ve signature.txt repoda, VM repoda değil — bölüm 14
- Hostname değiştirme, kullanıcı açma, SSH ve cron durdurma prova edildi — bölüm 15

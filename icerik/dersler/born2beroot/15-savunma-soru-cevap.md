42'de savunma, projenizi anlatıp evocunun sorularını canlı cevaplamanız şeklinde işler. Aşağıdakiler bu malumatnamedeki konulara özel, gerçekten sorulması muhtemel sorular — ezberlemek için değil, kendi cümlelerinizle yeniden üretebilmek için okuyun. "(canlı)" işaretli olanlar subject'te açıkça "peer review'da test edilecek" diye geçenler.

### Genel / Kavramsal
**S:** Bu proje ne yapıyor, kısaca anlatır mısınız?
**C:** VirtualBox'ta minimal, GUI'siz bir Debian sunucusu kurup LVM+şifreleme, AppArmor, sıkı SSH/firewall/parola/sudo kuralları ve bir izleme betiğiyle güvenli hâle getirdim.

**S:** Neden GUI kurulu değil?
**C:** Sunucu arka planda hizmet veriyor, önünde oturulmuyor; X.org/Wayland gereksiz kaynak tüketir ve saldırı yüzeyini büyütür — subject bunu 0 puanla cezalandırıyor.

### İşletim Sistemi
**S:** Debian mı Rocky mi kullandınız, neden?
**C:** Debian — sistem yönetimine yeniyim, subject de bunu öneriyor; ayrıca Ubuntu'yla çalışacağım için apt/dpkg/systemd/AppArmor bilgim doğrudan buraya taşınıyor.

**S:** apt ile aptitude farkı ne?
**C:** İkisi de dpkg'yi kullanır; apt daha basit/modern bağımlılık çözümü sunar, aptitude farklı bir çözme stratejisi ve interaktif arayüzle gelen alternatif bir ön yüzdür.

### Partisyonlama / LVM / Şifreleme
**S:** LVM nedir, neden kullandınız?
**C:** Disk alanını PV→VG→LV katmanlarıyla esnek yöneten bir yönetim katmanı; `lvextend` ile bir LV, disk yeniden bölümlenmeden büyütülebilir.

**S:** Şifreleme parolanız ile login parolanız aynı mı?
**C:** Hayır — biri (LUKS) diski açılışta kilitten çıkarıyor, diğeri sisteme giriş yapıyor; tamamen ayrı iki parola.

**S:** LVM aktif mi, nasıl gösterirsiniz?
**C:** `lsblk`, `pvs`, `vgs`, `lvs` — dördü birlikte PV/VG/LV zincirini gösterir.

### Güvenlik Çerçevesi
**S:** AppArmor ne işe yarar?
**C:** Kullanıcı izinlerinin ötesinde, sistem çapında bir programın erişebileceği dosyaları profil bazlı sınırlayan zorunlu bir güvenlik katmanı (MAC); bir servis ele geçirilse bile hasarı sınırlar.

**S:** AppArmor açık mı, nasıl kontrol edersiniz?
**C:** `sudo aa-status` — kaç profilin enforce modda olduğunu gösterir.

### SSH
**S:** SSH hangi portta, neden root ile bağlanılamıyor?
**C:** 4242'de; root'a doğrudan SSH girişini kapattım (PermitRootLogin no) çünkü root'a HER ZAMAN normal kullanıcı+sudo üzerinden erişilmeli.

### Firewall
**S:** Firewall'da hangi portlar açık?
**C:** Sadece 4242/tcp — her şey varsayılan kapalı, tek istisna bu.

### Hostname
**S:** (canlı) Hostname'i değiştirin.
**C:** `sudo hostnamectl set-hostname yenisim` — hem dosyayı günceller hem anlık uygular.

### Kullanıcı / Grup
**S:** (canlı) Yeni kullanıcı açın, bir gruba atayın.
**C:** `sudo adduser isim`, sonra `sudo usermod -aG grupadi isim` — `-a` olmadan kullanıcının var olan ikincil grupları silinir; eklemek için `-a` ile `-G` birlikte kullanılır.

### Parola Politikası
**S:** Parola politikanız neleri kapsıyor?
**C:** 30 günde zorunlu değişim, değişimler arası min 2 gün, 7 gün önce uyarı, min 10 karakter + büyük/küçük harf + rakam, 3'ten fazla ardışık aynı karakter yasak, kullanıcı adı içeremez, root hariç yeni parola eskisinden en az 7 karakter farklı olmalı.

**S:** Bu kuralları var olan hesaplara nasıl uyguladınız?
**C:** login.defs sadece YENİ kullanıcıları etkiler; root ve kendi hesabıma `chage -M 30 -m 2 -W 7` ile elle uyguladım. pwquality kuralları ise bir sonraki parola değişiminde devreye girdiği için politika bitince bütün parolaları (root dahil) `passwd` ile yeniden değiştirdim.

### sudo
**S:** sudo loglarını nereden görürsünüz?
**C:** /var/log/sudo/ altında; log_input/log_output ile hem komut hem çıktı kaydediliyor, sudoreplay ile tekrar oynatılabiliyor.

### monitoring.sh
**S:** (canlı) monitoring.sh nasıl çalışıyor, açıklayın.
**C:** cron ile açılışta bir kez (@reboot) ve her 10 dakikada bir (*/10 * * * *) çalışıyor, wall ile CPU/RAM/disk/LVM/bağlantı/kullanıcı/IP-MAC/sudo sayacını tüm terminallere yayınlıyor.

**S:** (canlı) Betiği DEĞİŞTİRMEDEN durdurun.
**C:** `crontab -e` ile ilgili satırın başına # koyup kaydediyorum — dosyaya dokunmuyorum, sadece zamanlamayı devre dışı bırakıyorum.

### Teslim / Savunma Mekaniği
**S:** signature.txt ne işe yarar?
**C:** VM diskimin sha1 özeti; değerlendirici bunu canlı VM'imle karşılaştırıp gerçekten benim ürettiğim makine olduğunu doğruluyor.

**S:** Savunma öncesi VM'de snapshot olmalı mı?
**C:** Hayır, snapshot'sız başlamalı; savunmaya özel snapshot savunma sırasında alınıp sonunda siliniyor.

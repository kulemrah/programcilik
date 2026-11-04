### DAC ile MAC (Mandatory Access Control) farkı
Discretionary Access Control (DAC), klasik Linux izin sistemidir (rwx, kullanıcı/grup) — dosyanın SAHİBİ izinleri belirler. Mandatory Access Control (MAC) ise sistem çapında, kullanıcının bile değiştiremeyeceği ek bir kural katmanıdır: "bu program SADECE şu dosyalara, şu şekilde erişebilir" diye merkezi politika dayatır. Bir servis ele geçirilse bile MAC, saldırganın sistemin geri kalanına sıçramasını engeller.

### AppArmor: profil mantığı, aa-status, Debian'da açılışta aktiflik
Debian'ın varsayılan MAC aracıdır. Profil tabanlı çalışır: her uygulama için `/etc/apparmor.d/` altında bir profil dosyası, o uygulamanın hangi dosyalara okuma/yazma/çalıştırma izni olduğunu tanımlar.
```bash
sudo aa-status
```
Bu komut kaç profilin "enforce" (zorlanan) ve kaç tanesinin "complain" (sadece loglanan) modda olduğunu gösterir. Açılışta otomatik başlaması için servisin systemctl ile enabled olması gerekir.

### SELinux: enforcing/permissive modları, sestatus
Rocky'nin varsayılan MAC aracıdır, AppArmor'dan daha ayrıntılıdır: dosya YOLUNA değil, dosyanın "context" (etiket) bilgisine göre çalışır. İki ana modu vardır: enforcing (kurallar zorlanır) ve permissive (ihlaller sadece loglanır).
```bash
sestatus
```

### Rocky özel durumu: KDump gerekmez, ama SELinux zorunlu
Subject, Rocky'nin SELinux'u enforcing modda ve açılışta aktif tutmasını şart koşuyor (KDump kurulumunu ise muaf tutuyor). Debian kuruyorsanız README karşılaştırması açısından bu kadarını bilmeniz yeterli.

### Savunmada "bu ne işe yarar" sorusuna hazırlık
Muhtemel soru: "AppArmor/SELinux ne işe yarar, neden var?" Tek cümlelik cevap: "Kullanıcı izinlerinin ötesinde, sistem çapında bir programın erişebileceği kaynakları sınırlayan zorunlu bir güvenlik katmanı; bir servis ele geçirilse bile hasarı sınırlar."

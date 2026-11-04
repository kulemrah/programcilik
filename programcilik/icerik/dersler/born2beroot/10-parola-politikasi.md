### PAM'in rolü (kısaca)
PAM (Pluggable Authentication Modules), Linux'ta kimlik doğrulamayı merkezi, eklenti tabanlı modüllerle çözen bir çerçevedir. Parola karmaşıklık kuralları (pam_pwquality gibi) PAM modülleri aracılığıyla `/etc/pam.d/common-password` (Debian) dosyasına eklenir.

### /etc/login.defs: PASS_MAX_DAYS (30), PASS_MIN_DAYS (2), PASS_WARN_AGE (7)
```
PASS_MAX_DAYS   30
PASS_MIN_DAYS   2
PASS_WARN_AGE   7
```
PASS_MAX_DAYS: parolanın kaç günde bir zorunlu süresi dolsun. PASS_MIN_DAYS: değiştirdikten sonra tekrar değiştirmeden önceki minimum bekleme (kullanıcının parolayı art arda değiştirip eski parolaya "dönmesini" engeller). PASS_WARN_AGE: süre dolmadan kaç gün önce uyarı verilsin. DİKKAT: bu dosya sadece YENİ kullanıcılara varsayılan olur — VAR OLAN kullanıcılara (root dahil) `chage` ile AYRICA uygulamanız gerekir.

### pam_pwquality ile karmaşıklık: min 10 karakter, büyük/küçük harf + rakam, 3'ten fazla ardışık aynı karakter yasağı
`/etc/security/pwquality.conf` içinde:
```
minlen = 10
ucredit = -1
lcredit = -1
dcredit = -1
maxrepeat = 3
```
minlen: minimum uzunluk. ucredit/lcredit/dcredit = -1: sırasıyla en az 1 büyük harf, 1 küçük harf, 1 rakam ZORUNLU (eksi değer "zorunlu" demektir — kafa karıştırıcı ama ezberlenmesi gereken bir PAM tuhaflığı). maxrepeat = 3: 3'ten fazla ardışık AYNI karakter yasak.

### Kullanıcı adını parolada yasaklama
Yine `/etc/security/pwquality.conf` içinde:
```
usercheck = 1
enforce_for_root
```
`usercheck = 1`, parolanın kullanıcı adını (düz ya da ters) içermesini engeller; varsayılan değeri zaten 1'dir, açıkça yazmak savunmada göstermeyi kolaylaştırır. Rehberlerde sık görülen `reject_username` eski pam_cracklib'in seçeneğidir: pam_pwquality onu `/etc/pam.d/common-password` satırında yalnızca uyumluluk için görmezden gelir. pwquality.conf'a yazmayın: orada tanınmayan bir ayar sayılır ve dosyanın sonraki satırlarının okunmasını engelleyebilir. `enforce_for_root` OLMADAN bu kurallar ROOT'a UYGULANMAZ — subject "root parolası da bu politikaya uymalı" dediği için bu satırı eklemeniz gerekiyor; sıkça unutulan bir ayrıntı.

### difok kuralı: yeni parolanın eskisinden en az 7 karakter farklı olması (root hariç)
```
difok = 7
```
Subject bunun ROOT'a uygulanmayacağını AÇIKÇA belirtiyor — tek istisna budur.

### Politika sonrası TÜM hesapların (root dahil) parolasının değiştirilmesi
Bütün kuralları yazdıktan sonra, sistemde zaten var olan hesapların parolaları henüz yeni kurallara göre belirlenmemiştir. Subject açıkça, config bitince TÜM parolaların (root dahil) YENİDEN değiştirilmesini istiyor:
```bash
sudo passwd root
sudo passwd login
```

### Var olan hesaplara login.defs değerlerini chage ile geriye dönük uygulama
login.defs sadece YENİ oluşturulacak kullanıcıları etkiler; root ve sizin kullanıcınız zaten VARDI, o yüzden onlara elle vermeniz gerekir:
```bash
sudo chage -M 30 -m 2 -W 7 root
sudo chage -M 30 -m 2 -W 7 login
```
-M: max gün, -m: min gün, -W: uyarı günü — login.defs'teki üç değerin var olan hesaplara uygulanma yolu budur; atlanırsa politika sadece kâğıt üzerinde kalır.

### chage -l ile doğrulama
```bash
sudo chage -l login
```
Bir kullanıcının parola yaşlanma bilgilerini (son değişiklik, max/min gün, uyarı günü) gösterir — hem kendi kontrolünüz hem savunmada "politika gerçekten uygulanmış mı" kanıtı için kullanılır.

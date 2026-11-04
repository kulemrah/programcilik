### Partition, dosya sistemi, mount point temel kavramları
Partition, bir diskin ayrılmış bölümüdür. Dosya sistemi (ext4 gibi) o bölüme nasıl dosya yazılıp okunacağını belirler. Mount point, o bölümün Linux dizin ağacında NEREDE görüneceğidir (ör. /boot, /, /home). /boot çekirdek dosyalarını tutar ve genelde ŞİFRELENMEZ (bootloader'ın okuyabilmesi gerekir); geri kalan her şey şifreli LVM içinde olabilir.

### LVM: Physical Volume / Volume Group / Logical Volume ilişkisi
LVM (Logical Volume Manager), diskleri esnek şekilde bölümlemenizi sağlayan bir katmandır. Physical Volume (PV): LVM'e verilen ham disk/partition. Volume Group (VG): birden fazla PV'nin birleştiği havuz. Logical Volume (LV): bu havuzdan kesilen, gerçek mount edilebilir "sanal partition". Zincir: disk → PV → VG → LV → dosya sistemi → mount point.

### LUKS ile disk şifreleme mantığı
LUKS (Linux Unified Key Setup), Linux'ta disk şifrelemesinin standardıdır. Şifreli bir partition açılışta parola istemeden mount edilemez — disk çalınsa bile içerik okunamaz. Bu projede LVM, LUKS'un ÜZERİNE kurulur: önce partition LUKS ile şifrelenir (sda5_crypt gibi bir "crypt" cihazı oluşur), sonra o cihazın İÇİNE LVM (PV/VG/LV) kurulur. Sıralama: partition → LUKS şifreleme → LVM → dosya sistemleri.

### "En az 2 şifreli bölüm" ne demek
Subject'in istediği, diskte iki ayrı şifreli kap açmanız değil: tek bir LUKS kabının içinde LVM ile en az iki mantıksal birim (LV) oluşturmanız yeterlidir. Aşağıdaki şemada root, swap ve home diye üç LV var; üçü de aynı şifreli kabın içinde olduğu için üçü de şifrelidir ve şart fazlasıyla karşılanır. /boot bunun dışındadır, sayıya dahil değildir.

### En az 2 şifreli LVM partisyonu kurulum sihirbazında nasıl oluşturulur
Debian kurulumunda "Manuel" partisyonlamayı seçin > diskte küçük bir /boot partition'ı ayırın (şifrelenmeyecek) > kalan alanı "şifreli birim yapılandır" ile şifreleyin, bir parola belirleyin (unutmayın, disk kilidini bu açar) > şifreli alanı "LVM birimi yapılandır" ile PV yapın, bir VG oluşturun > VG içinde root, swap, home için ayrı LV'ler oluşturun, her birine dosya sistemi (ext4, swap) ve mount point atayın. DİKKAT: burada belirlediğiniz şifreleme parolası, ileride kullanıcı hesabına gireceğiniz login parolasıyla AYNI ŞEY DEĞİL — bu, VM her açıldığında diski kilidinden çıkarmak için sorulan, tamamen ayrı bir parola.

### Örnek şema (/boot, root, swap, home) ve boyutlandırma ilkesi
Örnek: /boot (500MB, şifresiz) + şifreli LVM içinde root (~10GB), swap (RAM'in 1-2 katı; 1-2GB RAM'de 2GB swap yeterli), home (kalan alan). Subject'teki örnek 8GB'lık bir diskte veriliyor — kendi disk boyutunuza göre ORANLAYIN, örneği birebir kopyalamayın. "Gereksiz yer kaplama" uyarısını ciddiye alın: aşırı büyük swap ya da gereksiz büyük root, savunmada "neden bu kadar" sorusunu doğurur.

### Kurulum sihirbazının arka planda yaptığının komut karşılığı (kavramsal)
```bash
cryptsetup luksFormat /dev/sda5
cryptsetup open /dev/sda5 sda5_crypt
pvcreate /dev/mapper/sda5_crypt
vgcreate VGname /dev/mapper/sda5_crypt
lvcreate -L 10G -n root VGname
lvcreate -L 2G  -n swap VGname
lvcreate -l 100%FREE -n home VGname
```
Sihirbaz bunu tıklamalarla sizin için yapıyor; bu komutları görmek LVM'in NEDEN tercih edildiğini de açıklıyor: `lvextend` ile ileride bir LV'yi disk yeniden partitionlanmadan büyütebilirsiniz — ham partition'larla bu mümkün değildir.

### Doğrulama komutları: lsblk, pvs, vgs, lvs
```bash
lsblk   # disk/partition/LV ağacını gösterir
pvs     # Physical Volume'leri listeler
vgs     # Volume Group'ları listeler
lvs     # Logical Volume'leri listeler
```
Kurulum bittikten sonra bu dört komutla yapının beklediğiniz gibi olduğunu doğrulayın; savunmada da aynı komutlarla "LVM aktif mi" sorusuna canlı cevap verirsiniz.

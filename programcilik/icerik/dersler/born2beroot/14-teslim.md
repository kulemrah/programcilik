### Neden sadece README.md + signature.txt teslim edilir
VM'in kendisi asla repoya girmez; sadece bu iki dosya yeterlidir, çünkü değerlendirme sizin FİZİKSEL VM'iniz üzerinden canlı yapılır; dosyalar yalnızca kimlik doğrulama ve dokümantasyon içindir.

### İşletim sistemine göre imza alma komutları (Windows/Linux/Mac)
```bash
# Windows
certUtil -hashfile diskadi.vdi sha1
# Linux
sha1sum diskadi.vdi
# Mac (Intel)
shasum diskadi.vdi
# Mac M1 (UTM)
shasum diskadi.utm/Images/disk-0.qcow2
```

### VM her açıldığında imzanın değişmesi — disk kopyalama veya snapshot stratejisi
VM her başlatıldığında disk dosyası değişir, yani sha1 imzası da değişir. Çözüm: (a) disk dosyasının bir KOPYASINI ayrı tutun, imzayı o kopyadan alın, VEYA (b) her değerlendirme öncesi bir SNAPSHOT alın, imzayı o snapshot anındaki diskten hesaplayın.

### Snapshot kısıtlaması: savunma başında snapshot olmamalı
Her savunma SNAPSHOT'SIZ başlamalı. Savunmaya özel bir snapshot savunma başında alınır, savunma bitince SİLİNİR. Bu mantığı savunmadan önce mutlaka pratik edin.

### Savunmada beklenebilecek canlı görevler
Toparlarsak: hostname değiştirme (bölüm 8), yeni kullanıcı açıp gruba atama (bölüm 9), o kullanıcıyla SSH bağlantısı kurma (bölüm 6), monitoring.sh'i değiştirmeden durdurma (bölüm 12) ve genel olarak küçük bir kod/config değişikliği. Hepsini VM üzerinde en az bir kez PRATİK EDİN.

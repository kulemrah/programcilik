### Sanal makine (VM) ve hypervisor kavramı
Sanal makine (VM), fiziksel bilgisayarınızın içinde çalışan, kendi sanal donanımına (CPU, RAM, disk, ağ kartı) sahip bağımsız bir bilgisayar simülasyonudur. Bunu mümkün kılan yazılıma hypervisor denir; VirtualBox ve UTM birer hypervisor'dür (Tip-2, yani normal işletim sisteminin üzerinde bir uygulama gibi çalışırlar). VM sayesinde ana makinenizi bozma riski olmadan sıfırdan bir Linux sunucusu deneyebilirsiniz.

### VirtualBox'ta yeni VM oluşturma adımları (RAM, sanal disk, ISO bağlama)
Yeni > isim ve tip (Linux/Debian) seçin > RAM ayarlayın (1-2GB genelde yeterli, projede performans değil doğruluk önemli) > "Sanal sabit disk oluştur"u seçin, VDI formatı, "dinamik olarak ayrılan" boyut (ör. 8-10GB, ihtiyaca göre büyür) > Ayarlar > Depolama'dan indirdiğiniz .iso dosyasını sanal CD sürücüsüne bağlayın > Başlat, kurulum sihirbazı açılır.

### UTM ne zaman kullanılır (Apple Silicon durumu)
Subject VirtualBox'ı ister; VirtualBox'ı kullanamıyorsanız UTM'ye (QEMU tabanlı) izin verir. Apple Silicon (M1/M2/M3) Mac'lerde VirtualBox uzun süre desteklenmediği için bu Mac'lerde UTM yaygın tercihtir (VirtualBox, Apple Silicon desteğini 7.1 sürümüyle, Eylül 2024'te getirdi). UTM'de disk dosyası .qcow2 uzantılıdır, VirtualBox'taki .vdi'nin karşılığıdır — signature.txt için hash alırken bunu unutmayın.

### .vdi / .qcow2 disk dosyaları: ne işe yarar, nerede saklanır
Bunlar VM'inizin sanal sabit diskini temsil eden dosyalardır; kurduğunuz işletim sisteminin tamamı (partition'lar, dosyalar, her şey) içinde saklanır. Windows'ta `%HOMEDRIVE%%HOMEPATH%\VirtualBox VMs\`, Linux/Mac'te `~/VirtualBox VMs/` altında bulunur (UTM için `~/Library/Containers/com.utmapp.UTM/Data/Documents/`). Bu dosya ASLA git'e eklenmez — signature.txt için yalnızca hash'i alınır.

### Ağ modu ve port yönlendirme: SSH'a dışarıdan nasıl ulaşılır
VirtualBox varsayılan olarak NAT modu kullanır — VM dışarı çıkabilir ama dışarıdan VM'e DOĞRUDAN ulaşılamaz. Değerlendiricinin (ya da host'un) VM'in SSH'ına (4242) bağlanabilmesi için Ayarlar > Ağ > Gelişmiş > Port Yönlendirme'den bir kural eklemeniz gerekir: host'ta bir port → guest'te 4242. Alternatif: ağ modunu "Köprülenmiş Adaptör" (Bridged) yaparsanız VM ağda kendi IP'sini alır, doğrudan o IP + 4242 ile erişilir, port yönlendirmeye gerek kalmaz — savunmalarda genelde bu daha sorunsuzdur. Bölüm 6'daki SSH ayarları bu adım olmadan dışarıdan test edilemez.

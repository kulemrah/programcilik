### sudoers dosyasını sadece visudo ile düzenlemenin önemi
```bash
sudo visudo
```
sudoers dosyasını DOĞRUDAN bir editörle AÇMAYIN — sözdizimi hatası sudo'yu TAMAMEN kilitleyebilir; o zaman düzeltmek için root'a `su -` ile geçmek gerekir. visudo, kaydetmeden önce sözdizimini kontrol eder. Bu proje için `/etc/sudoers.d/` altına ayrı bir dosya oluşturmak, ana sudoers dosyasını bozma riskini azaltır.

### passwd_tries=3 ile deneme sınırı
```
Defaults passwd_tries=3
```
Yanlış parola girişini 3 denemeyle sınırlar.

### Yanlış parolada özel mesaj (badpass_message)
```
Defaults badpass_message="Kendi mesajınız buraya"
```
Subject "kendi seçtiğiniz bir mesaj" diyor — serbest metin; ezbere bir cümle hazırlayın.

### log_input / log_output ile /var/log/sudo/ altına loglama
log_input / log_output ile TAM oturum (yazılan komutlar VE ekrana basılan çıktı) kaydedilir. Bu kayıtların nereye yazılacağını iolog_dir belirler:
```
Defaults log_input, log_output
Defaults iolog_dir="/var/log/sudo/"
```
Klasörü sudo ilk kayıtta kendisi oluşturur; önceden `sudo mkdir -p /var/log/sudo` ile açmak da zararsızdır. Kayıtları bir video gibi geri oynatabilirsiniz: dizin değiştirildiği için `sudo sudoreplay -d /var/log/sudo -l` kayıtları listeler, `sudo sudoreplay -d /var/log/sudo <id>` oynatır — I/O logging'in ayırt edici özelliği budur.

### requiretty (TTY modu)
```
Defaults requiretty
```
sudo'nun sadece gerçek bir terminal (TTY) üzerinden çalıştırılmasını zorunlu kılar — arka plandaki script'ler sudo çalıştıramaz, bir güvenlik önlemidir.

### secure_path ile PATH kısıtlama
```
Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"
```
sudo çalıştırılırken kullanılabilecek PATH'i bu listeyle sınırlar — kullanıcının kendi PATH'ine sızdırdığı zararlı bir "sahte" binary'nin sudo ile çalıştırılmasını engeller.

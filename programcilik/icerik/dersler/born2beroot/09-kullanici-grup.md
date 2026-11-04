### root dışında kendi login'inizle kullanıcı açma
```bash
sudo adduser login
```
`adduser` (Debian'a özgü, etkileşimli, "dostane") ya da `useradd -m login` (daha ham, manuel parola atama gerektirir) ile root dışında, kendi login'inizle bir kullanıcı açarsınız.

### user42 ve sudo gruplarına ekleme (usermod -aG)
```bash
sudo usermod -aG user42 login
sudo usermod -aG sudo login
```
`-a` (append/ekle) ÇOK KRİTİK: `-a` olmadan `-G` kullanırsanız kullanıcının var olan TÜM ikincil gruplarını SİLİP yalnızca belirttiğiniz grupla değiştirirsiniz — tipik ve ciddi bir tuzak.

### groups, id komutlarıyla doğrulama
```bash
groups login
id login
```
`groups`, kullanıcının üye olduğu tüm grupları listeler; `id` hem kullanıcı hem grup ID'lerini (UID/GID) gösterir. Her ikisinde de user42 ve sudo görünmeli.

### Savunmada yeni kullanıcı oluşturup gruba atama pratiği
Değerlendirici sizden CANLI yeni bir kullanıcı açıp bir gruba atamanızı isteyecek. `adduser` + `usermod -aG` komutlarını ezbere, tereddütsüz yazabilmeniz gerekiyor — subject'te açıkça "peer review'da test edileceği" yazan iki maddeden biri.

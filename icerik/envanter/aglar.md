# Kaynak envanteri: Bilgisayar Ağları

Her slaytın hangi konuya ve başlığa işlendiği. Kapsama denetimi bu tabloyla yapılır: boş satır kalmaz. Bu klasör uygulamaya gitmez.

## Kaynak 1: "IP Kavramı ve IP Adresleme"

Dosya: `ip-kavrami-ve-ip-adresleme.pdf`, 20 slayt. Slaytlarda hoca adı, dönem ve değerlendirme bilgisi yok. 11. slayt ikinci bir kapaktır ("IP Adresleme ve IP Adresi Sınıfları · Ağ Mühendisliği ve Protokoller · Temel Ders Serisi"); dosya iki ayrı sunumun birleştirilmiş hâli gibi görünüyor.

| Slayt | İçerik | Konu › Başlık |
| --- | --- | --- |
| 1 | Kapak: "IP Kavramı ve IP Adresleme · Ağdaki cihazları tanımak, adreslemek ve yönlendirmek" | ag-ip-adresi › Temel fikir: ağda herkesin bir adresi olmalı (alt başlık) |
| 2 | Temel fikir: benzersiz tanımlayıcı, posta adresi benzetmesi | ag-ip-adresi › Temel fikir: ağda herkesin bir adresi olmalı |
| 3 | IP adresi nedir: 32 bitlik sayı, mantıksal adres, yönlendirme bilgisi | ag-ip-adresi › IP adresi nedir |
| 4 | IPv4 yapısı: 32 bit, dört oktet, 0–255, ikilik örnek | ag-ip-adresi › IPv4'ün yapısı: 32 bit, dört oktet |
| 5 | Dönüşüm: bit ağırlıkları, 11000000.10101000.00000000.00000001 → 192.168.0.1 | ag-ip-adresi › İkilikten noktalı ondalığa dönüşüm |
| 6 | Ağ + host: ağ kısmı, host kısmı, sınıflar bu bölünmenin sabit biçimleri | ag-ip-adresi › Ağ kısmı ve host kısmı |
| 7 | Bölüm 2 kapağı: adres sınıfları | ag-siniflar › Sınıflı adresleme: A'dan E'ye beş sınıf |
| 8 | Beş sınıf; ilk oktet sınıfı belirler; A, B, C genel, D, E özel amaç | ag-siniflar › Sınıflı adresleme: A'dan E'ye beş sınıf |
| 9 | Sınıf A: 8 bit ağ, 24 bit host, "0–126", ~16 milyon host, 10.24.8.17 | ag-siniflar › Sınıf A: az ağ, çok host |
| 10 | Sınıf B ve C tablosu; CIDR notu | ag-siniflar › Sınıf B ve Sınıf C; Sınıf B: orta ölçekli ağ; Sınıf C: küçük ağ |
| 11 | İkinci kapak: "IP Adresleme ve IP Adresi Sınıfları" | — (yalnızca başlık) |
| 12 | Sınıf D (224–239, multicast) ve E (240–255, deneysel) | ag-siniflar › Sınıf D ve E: özel kullanım blokları |
| 13 | 2ⁿ − 2: ağ adresi, yayın adresi, Sınıf C 254 | ag-siniflar › Neden 2ⁿ − 2 host; Ağ adresi: host bitlerinin tümü 0; Yayın (broadcast) adresi: host bitlerinin tümü 1; Hocanın örneği: Sınıf C |
| 14 | 127.x.x.x loopback; A sınıfı 1–126; 126 ağ; /8 test bloğu | ag-siniflar › 127.x.x.x ve loopback |
| 15 | RFC 1918: genel ve özel IP, üç özel blok | ag-tukenme › Özel ve genel IP adresleri (RFC 1918) |
| 16 | Alt ağ maskesi: varsayılan maskeler, CIDR, 192.168.1.0/24 | ag-siniflar › Alt ağ maskesi |
| 17 | Adresleri kim dağıtır: IANA, RIPE NCC, ODTÜ, A ve B blokları tükendi | ag-tukenme › Adresleri kim dağıtır |
| 18 | IPv4 tükeniyor: 2³² ≈ 4,29 milyar, verimsiz dağıtım, IBM örneği; grafik | ag-tukenme › IPv4 adreslerinin tükenmesi |
| 19 | NAT: port eşleme, iç ağda tasarruf, ömrü uzatan bariyer | ag-tukenme › Çözüm 1: NAT; İç ağda tasarruf; Ömrü uzatan bariyer |
| 20 | IPv6: 128 bit, 3,4×10³⁸, onaltılık, 8 grup, NAT'sız uçtan uca | ag-tukenme › Çözüm 2: IPv6; Adres kapasitesi; Yapı ve örnek |

Sıra notu: 16. slayt (alt ağ maskesi) sınıflarla birlikte anlatıldığı için "ag-siniflar" konusuna, 15. slayt (özel IP) tükenme ve NAT ile bağlantılı olduğu için "ag-tukenme" konusuna alındı.

## Sorunlar

| Slayt | Sorun | Karar |
| --- | --- | --- |
| 9 ↔ 14 | A sınıfının ilk oktet aralığı 9. slaytta "0–126", 14. slaytta "1'den 126'ya" | Notta 1–126; Dikkat kutusunda slayttaki "0–126" söylendi. Alt sınırdan soru yok. "126 ağ" sorusu 14. slayta dayanır |
| 17 | "Türkiye: Dağıtımı ODTÜ yürütür" güncel durumu yansıtmayabilir (Türkiye RIPE NCC bölgesinde; ODTÜ'nün bilinen görevi .tr alan adı kaydıydı). "IANA ve Internet Society gözetiminde": Internet Society kayıt kuruluşlarını denetlemez | Hocanın ifadesi korundu, iki nokta Dikkat kutusunda; bu slayttan soru yok, kartta yalnızca doğru kısım |
| 18 | Grafik etiketleri açık zeminde beyaz, zor okunuyor; eksende birim yok. Grafikte atanabilir genel alan toplamın büyük kısmı (yaklaşık 3,7 / 4,3) görünüyor, metin ise "pratikte kullanılabilir sayı çok daha azdır" diyor | Grafik Ek kutusunda betimlendi; grafikten soru yok |
| 19 | Tek genel IP'nin paylaştırıldığı cihaz sayısı "yüzlerce" ve "binlerce" diye iki türlü | Dikkat kutusunda söylendi; sayıdan soru yok |
| 20 | Örnek IPv6 adresinde 6 grup yazılı, "8 grup" denmiş (`::` kısaltması açıklanmamış) | Ek kutusunda `::` açıklandı ve açık yazım verildi |
| 16 | "Varsayılan Maske" ve maskeler hücreye sığmadığı için bölünmüş ("Varsayıla n", "255.255.2 55.0") | Sessizce düzeltildi |

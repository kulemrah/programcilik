### Özel ve genel IP adresleri (RFC 1918)

**Genel IP** adresi internette **benzersizdir.** Lisans gerektirmeyen **özel bloklar** ise yerel ağlarda **tekrar kullanılabilir.** Bu bloklar RFC 1918 standardında tanımlanır.

| Özel blok | Aralık | Hocanın verdiği kullanım |
| --- | --- | --- |
| 10.0.0.0/8 | 10.0.0.0 – 10.255.255.255 | Büyük kurumlar ve veri merkezleri için geniş iç adres alanı |
| 172.16.0.0/12 | 172.16.0.0 – 172.31.255.255 | Orta ölçekli kampüs ağları |
| 192.168.0.0/16 | 192.168.0.0 – 192.168.255.255 | Ev ve küçük ofis modemlerinde yaygın özel blok |

> **Ek:** 10.0.0.0/8 ve 192.168.0.0/16 bloklarının aralığı slaytta yazılmamıştır; tablodaki aralıklar /8 ve /16 gösteriminden çıkar. RFC (Request for Comments), internet standartlarının yayımlandığı belge dizisidir.

> **Dikkat:** "Özel IP" ile "özel amaçlı sınıf" farklı şeylerdir. Özel IP blokları (10, 172.16–172.31, 192.168) A, B ve C sınıflarının içindedir ve yerel ağlarda cihazlara verilir. D ve E sınıfları ise cihazlara hiç verilmeyen özel amaçlı sınıflardır.

> **Ek:** Evinizdeki modemin size verdiği `192.168.1.x` gibi adres özel adrestir; aynı adres komşunuzun evinde de kullanılıyor olabilir. İnternete çıkarken bu adres, modemin genel IP adresine çevrilir (aşağıda, NAT).

### Adresleri kim dağıtır

IP adresleri **rastgele seçilemez**; küresel ve yerel kayıt otoritelerinin **hiyerarşik denetimindedir.**

Hocanın slaytına göre:

- **Küresel:** IANA ve Internet Society gözetiminde, RIPE NCC gibi kıtasal kayıt kuruluşları blokları bölüştürür.
- **Türkiye:** Dağıtımı ODTÜ yürütür; ilk dönem dağıtım ve koordinasyonunu bünyesindeki kurullar yürütmüştür.
- **A ve B blokları:** Kurumlara tek seferde milyonlarca IP sağlayan büyük bloklar yıllar önce tamamen tükenmiştir.

> **Dikkat:** Bu slayttaki iki ifade güncel durumu tam yansıtmayabilir. Türkiye, IP adresleri bakımından RIPE NCC'nin hizmet bölgesindedir; kurumlar ve servis sağlayıcılar adres bloklarını RIPE NCC'den alır. ODTÜ'nün uzun yıllar yürüttüğü bilinen görev ise .tr alan adlarının kaydıdır (bu görev 2022'de BTK'ya geçti). Ayrıca IANA'nın görevi bugün ICANN'e bağlı olarak yürütülür; Internet Society kayıt kuruluşlarını denetleyen bir kurum değildir. Notta hocanın ifadesi korundu.

> **Ek:** IANA (Internet Assigned Numbers Authority), adres havuzunun en üstteki yöneticisidir; blokları kıtasal kayıt kuruluşlarına (RIR) verir. RIPE NCC, Avrupa, Orta Doğu ve Orta Asya'nın bir bölümünden sorumlu kayıt kuruluşudur.

### IPv4 adreslerinin tükenmesi

32 bitlik adres uzayı, **2³²** formülüyle yaklaşık **4,29 milyar** adres sunar. Ancak **verimsiz dağıtım** nedeniyle pratikte kullanılabilir sayı çok daha azdır.

Hocanın örneği: **IBM gibi devler**, erken dönemde kendilerine ayrılan **A sınıfı blokların** çok küçük bir bölümünü fiilen kullanmıştır.

> **Ek:** 2³² = 4.294.967.296. Bir A sınıfı blok tek başına yaklaşık 16 milyon adres demektir; böyle bir blok tek bir kuruma verildiğinde kullanılmayan adresler başkasına da verilemez. Slayttaki grafik üç çubuk gösterir: toplam teorik IPv4 (4'ün biraz üstü), özel, rezerve ve kayıp adresler (küçük bir bölüm) ve atanabilir genel alan (yaklaşık 3,7). Eksende birim yazılmamıştır; değerler milyar adres olarak okunabilir.

### Çözüm 1: NAT

**Ağ Adresi Dönüştürme (NAT)**, dinamik port eşlemesiyle **tek genel IP'yi** çok sayıda yerel cihaza paylaştırır. Hoca NAT'ı "geçici cankurtaran" diye anar.

#### İç ağda tasarruf

RFC 1918 özel adresleri (ör. 192.168.x.x) yerel ağda kullanılır; internete çıkarken **tek IP'ye** çevrilir.

#### Ömrü uzatan bariyer

Bazılarına göre NAT, IPv6'ya geçişi gereksiz kılar; bazı uzmanlara göre ise IPv6 ihtiyacını **onlarca yıl ertelemiştir.**

> **Dikkat:** Slaytta tek genel IP'nin paylaştırıldığı cihaz sayısı iki yerde farklı yazılmış: başlık altında "yüzlerce yerel cihaz", slaytın altında "1 Genel IP → Binlerce Yerel Kullanıcı". Ana fikir sayı değil, **bir genel IP'nin birçok yerel cihaza paylaştırılmasıdır.**

> **Ek:** NAT'ın İngilizce açılımı Network Address Translation'dır. "Dinamik port eşleme" şöyle işler: yerel ağdaki her bağlantıya, genel IP'nin üzerinde ayrı bir port numarası verilir. Cevap geldiğinde modem port numarasına bakarak paketi doğru yerel cihaza iletir.

### Çözüm 2: IPv6

**128 bitlik** yeni nesil protokol, adres kıtlığını **matematiksel olarak ortadan kaldırır.** Hoca IPv6'yı "kalıcı ve nihai gelecek" diye anar.

#### Adres kapasitesi

Yaklaşık **3,4 × 10³⁸** adres: hocanın benzetmesiyle, her kum tanesine milyarlarca benzersiz IP atayabilecek evrensel bir adres uzayı.

#### Yapı ve örnek

128 bit, **onaltılık (hexadecimal)** sayılarla ve **8 grup** hâlinde yazılır. Hocanın örneği: `2001:0db8:85a3::8a2e:0370:7334`

IPv6, **NAT gereksinimini kaldırır**; cihazlar arasında **uçtan uca doğrudan bağlantı** geri döner.

> **Ek:** Gruplar iki nokta üst üste (`:`) ile ayrılır; her grup 16 bittir (8 × 16 = 128). Hocanın örneğindeki `::`, art arda gelen sıfır grupları kısaltır: örnekte 6 grup yazılıdır, `::` kalan 2 sıfır grubunun yerini tutar. Açık yazımı `2001:0db8:85a3:0000:0000:8a2e:0370:7334`'tür. 2¹²⁸ ≈ 3,4 × 10³⁸ eder.

> **Dikkat:** IPv4 ile IPv6'yı karıştırmayın: IPv4 **32 bit**, dört oktet, noktalı **ondalık** gösterim (192.168.0.1); IPv6 **128 bit**, sekiz grup, iki nokta üst üsteli **onaltılık** gösterim.

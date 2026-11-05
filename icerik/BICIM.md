# İçerik biçimi

Ders notlarının hangi kademelerden geçerek işlendiği `ISLEME.md`'dedir; bu dosya yalnızca biçimi anlatır.

Bu klasördeki her şey `araclar/icerik-aktar.mjs` ile doğrulanır; tek bir kural bozuksa hiçbir şey yüklenmez. Yüklemeden önce yerelde denemek için:

```
node araclar/icerik-aktar.mjs --kuru
```

## Klasör düzeni

```
icerik/
  agac.json                         Sınıf > Dönem > Ders yapısı
  dersler/
    <ders-id>/
      01-konu-adi.md                konunun okuma metni
      01-konu-adi.json              konunun kimliği, başlığı, kavramları, soruları, kartları
      02-baska-konu.md
      02-baska-konu.json
      gorseller/
        akis-1.svg                  konularda kullanılan görseller
```

- Ders klasörünün adı `agac.json` içindeki ders kimliğiyle aynıdır.
- Dosya adı `NN-ad` biçimindedir. `NN` iki haneli sıra numarasıdır ve konu listesindeki sırayı belirler. `00` başlığında numara gösterilmez.
- Her konunun hem `.md` hem `.json` dosyası olmak zorundadır.
- Dosyalar UTF-8 ve LF satır sonuyla kaydedilir; BOM olmaz.

## agac.json

```json
{
  "gruplar": [
    { "id": "sinif-1", "ad": "1. Sınıf", "donemler": [
      { "id": "sinif-1-guz", "ad": "Güz", "dersler": [
        { "id": "algoritma", "ad": "Algoritma ve Programlama Temelleri", "kisa": "Algoritma" }
      ] }
    ] },
    { "id": "42", "ad": "42", "hususi": true, "dersler": [ { "id": "born2beroot", "ad": "Born2beRoot" } ] }
  ]
}
```

- Bir grup ya `donemler` ya da doğrudan `dersler` taşır, ikisini birden taşımaz.
- `"hususi": true` yazılan grup (ör. 42) yalnızca hususi yetkisi olan hesaplarda görünür; notları, soruları, kartları ve görselleri de yalnızca o hesaplara iner. Yetki Supabase'de verilir (KURULUM.md, "Hususi dersler"). Hususilik grup düzeyindedir; aynı grupta hem hususi hem herkese açık ders olmaz.
- `kisa` isteğe bağlıdır; etiketlerde ve çiplerde uzun ad yerine kullanılır.
- Kimlikler (`id`) küçük harf, rakam ve tireden oluşur; ağaçta tekildir.
- Notu olmayan ders ağaçta durabilir; uygulamada "yakında" görünür.

### Sınav takvimi

`agac.json` isteğe bağlı bir `sinavlar` listesi de taşır. Sınavlar uygulamada menünün Takvim bölümünün altında yakından uzağa gösterilir; aynı günün sınavları tek kutuda alt alta durur, günü geçen sınavlar gösterilmez.

```json
"sinavlar": [
  { "ders": "veritabani", "ad": "1. Kısa Sınav", "zaman": "2026-11-06T20:30+03:00", "lms": true },
  { "ders": "ekoloji", "ad": "Vize", "zaman": "2026-11-12T10:00+03:00", "yer": "B-201", "not": "Hesap makinesi getirilecek." }
]
```

- `ders`: ağaçtaki bir ders kimliği; uygulamada dersin tam adı yazılır. Hususi bir dersin sınavı yalnızca hususi hesaplara gider.
- `dersAdi`: uygulamada olmayan bir dersin sınavı için (ör. Matematik) `ders` yerine düz yazı ders adı; ikisi birlikte yazılmaz. Böyle sınav herkese gider.
- `ad`: sınavın adı (1. Kısa Sınav, Vize, Final…).
- `zaman`: Türkiye saatiyle, saat dilimi yazılarak: `YYYY-AA-GGTSS:DD+03:00`.
- `lms`: `true` ise "Sınav LMS üzerinden çevrimiçi olacak." yazar.
- `modul`: `true` ise "Sınav KOSTÜ Sınav Modülü üzerinden çevrimiçi olacak." yazar (`lms` ile birlikte true olamaz).
- `yer`, `not`: isteğe bağlı; yazılırsa gösterilir.
- Geçmiş sınavlar listeden silinmeyebilir; uygulama onları zaten göstermez.

## Konu metni (.md)

Her boş olmayan satır ayrı bir paragraftır; satırlar birleştirilmez. Konu başlığı `.json` dosyasındadır, metne yazılmaz.

| Yazım | Sonuç |
| --- | --- |
| `### Alt başlık` | Alt başlık; içindekiler listesine girer |
| `#### Daha alt başlık` | İkinci kademe; önünde mutlaka bir `###` olur |
| `- madde` | Madde işaretli liste |
| `1. madde` | Numaralı liste |
| `> not` | Vurgulu not kutusu |
| `**kalın**` | Kalın yazı |
| `` `kod` `` | Satır içi kod |
| `![açıklama](gorseller/ad.svg)` | Görsel; satırda tek başınaysa altına açıklaması yazılır. Boş satır bırakmadan art arda yazılan görsel satırları tek bir dizi olur: yana kaydırılarak gezilir |

Kod bloğu satır başından başlayan üç ters tırnakla açılıp kapanır; dil adı yazılabilir ama gösterilmez. Açılış da kapanış da satır başında olur; girintili çit hata sayılır.

Listeler tek düzeydir: girintili (iç içe) liste ve alıntı (`>`) içinde liste ya da başlık kullanılmaz.

Tablo: ilk satır başlık, ikinci satır `| --- |` ayracı; bütün satırlar aynı sütun sayısında.

Satır içi `` `kod` `` ve `**kalın**` işaretleri aynı satırda kapanır; kapanmayan işaret hata sayılır.

Kullanılmayanlar: `#` ve `##` başlıkları, HTML etiketleri, italik (yıldızlı tek vurgu), bağlantılar, U+E000–U+E002 özel karakterleri (uygulama bunları iç işaret olarak kullanır).

Bir konudaki başlık metinleri birbirinden farklı olmalıdır ve en çok 150 karakter olur. Soruların `yer` alanı ve öğrencilerin "mühim" işaretleri bu metinlere bağlanır: yayımlanmış bir başlığın metni değişirse ona konmuş mühim işaretleri görünmez olur (başlık eski hâline dönerse geri gelir).

`yer` alanı "Yalnızca mühim yerler" süzgecinde de kullanılır: soru, kart ya da kavram hangi başlığa bağlıysa o başlık mühimse gelir. `yer` alanı olmayanlar konunun geneli sayılır. Bu yüzden her soruya, karta ve kavrama mümkünse `yer` yazılır.

## Konu dosyası (.json)

```json
{
  "id": "alg-akis",
  "baslik": "Akış Şemaları",
  "kaynak": "3. hafta ders notu",
  "kavramlar": [ { "terim": "Akış şeması", "izah": "…", "yer": "Akış şeması nedir" } ],
  "sorular": [ … ],
  "kartlar": [ { "id": "alg-akis.k1", "on": "Soru", "arka": "Cevap" } ]
}
```

- `id` konunun kalıcı kimliğidir; konu yeniden adlandırılsa ya da sırası değişse bile **değişmez**. Öğrencilerin okundu işaretleri, boyaları ve yanlış defteri bu kimliğe bağlıdır.
- `kaynak` yalnızca depoda kalır, uygulamaya gitmez.
- Soru kimliği `<konu-id>.s<n>`, kart kimliği `<konu-id>.k<n>` biçimindedir; bunlar da sonradan değiştirilmez. Bir soru silinirse kimliği yeniden kullanılmaz.
- `yer` isteğe bağlıdır; metindeki bir `###` ya da `####` başlığıyla harfi harfine aynı olmalıdır. Uygulama "konuda oku" denince o başlığa gider.
- Metin alanlarının başında ve sonunda boşluk olmaz. Soru, şık, izah ve kart metinlerinde `` `kod` `` ve `**kalın**` kullanılabilir (`` **`sudo`** `` gibi iç içe de olur); kart arkası ve klasik cevap birden çok satır olabilir.
- Görsel konu metninde (.md) ve sorunun `gorseller` alanında kullanılır; başka .json alanlarına (kart, kavram, şık) görsel yazılmaz.

## Soru türleri

Bütün türlerde `id`, `tip` ve isteğe bağlı `yer` bulunur. Her tür isteğe bağlı `gorseller` alabilir: `gorseller/` klasöründeki 1–8 dosya adı (`["anakart-isaret-pci.webp", "anakart-isaret-pci-yakin.webp"]` gibi). Görseller soru metninin altında çizilir; birden çoksa yana kaydırılır. Soru görsellerinin açıklaması gösterilmez (cevabı ele vermesin); işaret ya da numara görselin içine çizilir.

| tip | Alanlar | Not |
| --- | --- | --- |
| `secme` | `soru`, `secenekler` (2–6), `dogru` (0'dan başlayan sıra), `izah`, isteğe bağlı `kod` | Şıklar her gösterimde karışır |
| `dy` | `ifade`, `dogru` (true/false), `izah` | Doğru mu, yanlış mı |
| `bosluk` | `metin` (boşluk yerine `___`), `cevaplar` (her boşluk için kabul edilen cevaplar dizisi), isteğe bağlı `izah` | Büyük/küçük harf (I/ı/İ/i dahil), ş/s, ğ/g, ü/u, ö/o, ç/c farkı, fazla boşluk ve sondaki nokta önemsiz; 5–7 harflik cevapta 1, 8+ harfte 2 harf yazım hatası kabul edilir (ilk harf, rakam ve işaretler tam tutmalı; 4 harf ve altı tam). Yazımı ayrı ama anlamı aynı karşılıklar ("geri besleme"/"geribesleme") yine `cevaplar`'a yazılır. Boşluk kod içinde de olabilir: `` `usermod ___ -aG sudo` `` |
| `dizme` | `soru`, `parcalar` (doğru sırada, en az 2), isteğe bağlı `komut` (true ise parçalar boşlukla birleşir), `izah` | |
| `esles` | `soru`, `ciftler` ([sol, sağ], 2–8 çift), isteğe bağlı `izah` | Sol ve sağ sütunda tekrar olmaz |
| `izleme` | `soru`, `kod` (zorunlu), `secenekler`, `dogru`, `izah` | Kodun ya da akışın çıktısı sorulur |
| `hesap` | `soru`, `cevap` (sayı), isteğe bağlı `tolerans` (≥0) ve `birim`, `izah` (çözüm yolu) | Virgül de ondalık ayırıcı sayılır; binlik ayırıcılı cevap (1.000) yazılırsa öğrenciye sorulur |
| `klasik` | `soru`, `cevap` (örnek cevap), isteğe bağlı `anahtarlar` | Öğrenci kendini Bildim / Kısmen / Bilemedim diye puanlar; `anahtarlar` aynı hoşgörüyle ve ekli hâliyle de ("işlemciye") yeşil olur |

Örnek:

```json
{ "id": "alg-akis.s3", "tip": "hesap", "soru": "10 Ω'luk dirençten 2 A geçiyor. Gerilim kaç volttur?",
  "cevap": 20, "birim": "V", "izah": "V = I · R = 2 · 10 = 20 V", "yer": "Ohm kanunu" }
```

## Görseller

- `gorseller/` içindeki dosya adı küçük harf, rakam ve tireden oluşur; uzantısı `svg`, `png`, `jpg`, `jpeg` ya da `webp` olur.
- Her görsel en çok 2 MB olabilir.
- Açıklama (alt metin) boş bırakılmaz.
- Bir görsel ya notta ya da bir sorunun `gorseller` alanında kullanılmış olmalıdır; ikisi de kullanım sayılır.
- Uygulamada nottaki ya da sorudaki bir görsele dokunulunca görsel tam ekran büyüteçte açılır.
- Görseller notlarla aynı korumayla gizli bir kovada durur; yalnızca sözleşmeyi onaylamış okul hesapları görür.
- Bir görseli düzeltmek için dosyayı aynı adla değiştirmek yeterlidir. Aktarıcı depoya içeriğin özetiyle başlayan bir adla yükler (`900fbe9342-sema.svg` gibi); görsel değişince adı da değişir ve cihazlar yenisini indirir.

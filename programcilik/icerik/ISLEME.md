# Ders notlarının işlenmesi

Bir dersin PDF notları (hoca slaytları) bu rehberle okuma notuna, temrine ve 42 kartına çevrilir. Rehber, işi hangi sohbette ya da oturumda yapılırsa yapılsın aynı sistemle yürütmek için yazıldı. Biçim kuralları `BICIM.md`'dedir; bu dosya süreci ve içerik kurallarını anlatır.

Bunlar okul sınavının soruları ve konularıdır: **hata payı yoktur.** Her kademe bir öncekinin çıktısını denetler; bir kademede bulunan hata düzeltilmeden sonrakine geçilmez.

## Girdi ve çıktı

Girdi: hocanın PDF'leri (bir ya da birkaç hafta). Dosya adındaki hafta numarasına ve kapaktaki döneme bakılır; eksik hafta ya da dönem tutarsızlığı varsa teslimde sorulur.

Çıktı (ders klasörü `icerik/dersler/<ders-id>/`):

| Dosya | İçerik |
| --- | --- |
| `NN-ad.md` | Konunun okuma notu |
| `NN-ad.json` | Konunun kimliği, başlığı, kaynağı, kavramları, soruları, kartları |
| `gorseller/*.svg` | Notlarda kullanılan şekiller |
| `icerik/envanter/<ders-id>.md` | Kaynak envanteri: hangi slayt hangi başlığa işlendi, kaynakta görülen sorunlar ve verilen karar (uygulamaya gitmez) |
| `araclar/sekiller/<ders-id>.py` | Şekilleri üreten betik |

Teslimde yalnızca değişen dosyalar verilir.

## Kademeler

| # | Kademe | Ne yapılır | Bitti sayılması için |
| --- | --- | --- | --- |
| K0 | Kaynak envanteri | PDF'in metni çıkarılır (`pdftotext -layout`), bütün sayfalar küçük resim olarak taranır, şekilli sayfalar yüksek çözünürlükle ayrıca açılır. Her slayt bir satır olarak envantere yazılır. | Her slaytın içeriği bir cümleyle envanterde |
| K1 | Konu ve başlık planı | Slaytlar konulara, konular `###` / `####` başlıklarına bölünür. Konu kimliği (`<ders-kısa>-<konu>`) ve dosya adları belirlenir. Envanterin "Konu › Başlık" sütunu doldurulur. | Boş satır yok; her başlığın kaynağı belli |
| K2 | Okuma notları | `.md` dosyaları yazılır (aşağıdaki "Okuma notu kuralları"). Kod örneği varsa gerçekten çalıştırılır. | Notlar slaytların tamamını karşılıyor |
| K3 | Görseller | Şekiller betikle SVG olarak üretilir, telefon genişliğinde (358 px) resme çevrilip gözle bakılır (aşağıdaki "Görseller"). | Taşma, üst üste binme, yanlış ok yok; slaytla birebir |
| K4 | Doğruluk tahlili | Notlardaki her cümle slayta (metin ya da şekil) bağlanır. Dayanağı olmayan cümle ya "Ek" kutusuna alınır ya da silinir. Şekilden aktarılan bilgi yüksek çözünürlüklü resimle doğrulanır. | Ek dışında dayanaksız cümle yok |
| K5 | Kapsam ve ikaz taraması | Envanterdeki her satırın başlığı notta var mı, notta slaytsız başlık var mı (varsa envantere nedeni yazılır) denetlenir. Sınavda karıştırılabilecek her nokta için "Dikkat" kutusu yazılır. Slayttaki yazım hataları ve tutarsızlıklar envanterin "sorunlar" tablosuna işlenir. | Kapsam tablosu temiz; ikaz listesi notlarda |
| K6 | Temrin planı | Her konu için hangi bilginin hangi soru türüne uygun olduğu çıkarılır (aşağıdaki "Soru türü seçimi"). | Konu × tür tablosu |
| K7 | Temrinlerin yazılması | Sorular `.json`'a yazılır; her soruya `yer`. | Plan karşılandı |
| K8 | Soru ve cevap tahlili | Her sorunun tek doğru cevabı olduğu, çeldiricilerin savunulabilir biçimde doğru olmadığı, sorunun belirsiz olmadığı denetlenir. Otomatik denetimler çalıştırılır (K11). | Belirsiz soru yok; uyarılar kapatıldı |
| K9 | 42 kartları | Sözlü sınav tarzı kartlar yazılır (aşağıdaki "Kartlar"). | Her ana kavram ve karşılaştırma bir kartta |
| K10 | Kart tahlili | Kart arkasının slayta uyduğu, Ek bilginin "Ek:" diye ayrıldığı denetlenir. | Dayanaksız kart cümlesi yok |
| K11 | Teknik doğrulama | Biçim denetimi, içerik denetimi, uygulamada uçtan uca deneme (aşağıdaki "Denetim araçları"). | Üçü de temiz |
| K12 | Bağımsız son denetim | İşi yapmamış ayrı bir denetçi (ayrı bir ajan ya da oturum), yalnızca slaytları ölçüt alarak notları, soruları, kartları ve şekilleri denetler. Bulgular KRİTİK / ORTA / DÜŞÜK diye sınıflanır. | KRİTİK ve ORTA bulguların hepsi kapandı; DÜŞÜK'ler tek tek değerlendirildi |
| K13 | Teslim | Değişen dosyalar ve teslim raporu (aşağıdaki "Teslim raporu"). | Kararlar Hamza'ya açıkça soruldu |

Kod çalıştırma (K2), görsel doğrulama (K3), envanter (K0), çeldirici kalitesi ve kopya kontrolü (K8, K11) ile bağımsız denetim (K12), istenen kademelere sonradan eklenmiş kademelerdir; atlanmaz.

## Okuma notu kuralları

- Ana metin **hocanın içeriğidir.** Hocanın tanımı, sırası ve örnekleri korunur; tanım cümlesi mümkün olduğunca hocanın sözüyle verilir (sınavda o beklenir).
- Hocanın örnekleri "Hocanın örneği:" diye açıkça belirtilir. Hocanın şeklinde geçen ad metindekinden farklıysa (ör. metinde "öğretim elemanı", şekilde `öğretmen`) bu bir cümleyle söylenir.
- Slaytta olmayan her bilgi `> **Ek:**` kutusuna yazılır: açıklayıcı örnek, kavramın İngilizcesi, kaynak kitaptaki tanım, kod örneği. Bir başlığın tamamı ek bilgiyse başlığın sonuna `(Ek)` yazılır. Bir bilginin yalnızca şekilde olduğu, yazıyla verilmediği Ek kutusunda belirtilir.
- `> **Dikkat:**` kutusu iki iş görür: sınavda karıştırılan noktaları ayırır (aynı sözün iki anlamı, birbirine benzeyen gösterimler, bir kavramın iki aşamada geçmesi) ve slayttaki tutarsızlığı ya da yanlış ifadeyi düzeltip açıklar. Slayttaki ifadenin düzeltildiği her yerde öğrenciye slaytta ne yazdığı söylenir.
- Notta sınavda neyin sorulacağı ya da neyin geçerli sayılacağı söylenmez ("Sınavda … esastır" yazılmaz); gerekiyorsa hocanın ifadesinin korunduğu belirtilir ("Notta hocanın ifadesi korundu.").
- Slayttaki yazım hataları (ör. "yağısında" → "yapısında") sessizce düzeltilir ve envantere yazılır. Anlamı etkileyen düzeltme ise Dikkat kutusunda da söylenir.
- Konu başlığı `.json`'dadır; `.md`'ye yazılmaz. Başlık metinleri `yer` alanlarının ve mühim işaretlerinin bağlandığı anahtardır: yayımlandıktan sonra değiştirilmez.
- Bir konu 5–15 başlık arasında tutulur. Liste tek düzeydir; alıntı kutusunun içinde liste olmaz (`BICIM.md`).
- Kod örnekleri (ör. SQL) gerçek bir ortamda çalıştırılıp çıktısı doğrulanmadan nota konmaz. VTYS'ye özgü ayrıntı varsa Ek kutusunda söylenir.

## Görseller

- Şekiller elle çizilmez; `araclar/sekiller/<ders-id>.py` betiğiyle SVG olarak üretilir. Yeni ders için `araclar/sekiller/veritabani.py` kopyalanır: renkler ve yardımcılar (`Sekil`, `kutu`, `mini_tablo`, `satir_bagintisi`) aynen kalır.
- Şekil, hocanın şeklinin sadeleştirilmiş ve telefonda okunur hâlidir. Hocanın şeklindeki adlar, oklar, işaretler ve nitelikler birebir korunur. Şekle hocanın söylemediği bir kural ya da yorum yazılmaz; açıklayıcı alt yazı slayttaki cümleyi kullanır.
- Kök SVG'de beyaz arka plan ve `<title>` vardır; yazılar 11 px'ten küçük olmaz. Baştaki boşluk SVG'de görünmez: girintili kod satırları `x` kaydırılarak girintilenir.
- Her şekil 358 px genişlikte resme çevrilip gözle bakılır: yazı taşması, üst üste binen elips ya da kutu, tuval dışına taşan öğe, kesişen çizgi aranır. Sonra uygulama içinde de bakılır.
- Görsel adı küçük harf ve tiredir (`er-gosterim.svg`); her görsel en az bir konuda kullanılır ve açıklaması (alt metni) boş bırakılmaz.

## Soru türü seçimi

| Bilginin türü | Uygun soru türü |
| --- | --- |
| Tanım | `secme` (çeldiriciler aynı dersin başka tanımları), `bosluk` (tanımın anahtar sözcüğü) |
| Sınıflandırma (A, B, C türleri) | `esles` (tür ↔ tanım ya da örnek), `secme` ("hangisi ... değildir") |
| Sıralı adımlar, aşamalar, tarih sırası | `dizme` |
| Gösterim ve şekil | `esles` (şekil ↔ anlam), `secme` |
| Hocanın örneği | `secme` / `dy` (örnek hangi kavrama ait) |
| Yeni bir duruma uygulama | `secme` (yalnızca tek cevabı tartışmasız olan durumlar) |
| Sayılabilen ya da hesaplanan | `hesap` |
| Karıştırılan iki kavram | `dy` (yanlış ifade, karıştırılanı söyler) |
| Liste hâlinde sayılması istenen | `klasik` |
| Kod çıktısı | `izleme` |

Kurallar:

- Sorular yalnızca hocanın içeriğinden sorulur; Ek kutusundaki bilgiden soru yazılmaz.
- Her sorunun **tek** doğru cevabı vardır. Çeldirici, aynı dersin başka bir doğru bilgisinden seçilir (başka bir kavramın tanımı, başka bir türün örneği); saçma ya da kolayca elenen çeldirici yazılmaz.
- Doğru şık en uzun, en ayrıntılı ya da hocanın cümlesinin aynısı olduğu için ele vermemelidir: çeldiriciler aynı uzunlukta ve aynı dil yapısında yazılır.
- "Hepsi", "hiçbiri", "A ve B" gibi şıklar kullanılmaz (uygulama şıkları karıştırır).
- `bosluk`'ta mümkünse tek boşluk olur; birden çok boşluk sıraya bağlıdır. Kabul edilen eşdeğer yazımlar (ör. "varolma", "var olma") cevaplara eklenir.
- `klasik` sorunun `anahtarlar`'ı kısa ve öğrencinin yazacağı biçimdedir; her anahtar örnek cevabın içinde harfi harfine geçer (uygulama, öğrencinin yazdığında anahtarı arar).
- D/Y sorularında doğru ve yanlış cevaplar dengelidir.
- Her soruya, cevabının bulunduğu başlık `yer` olarak yazılır. `izah`, cevabın neden doğru olduğunu ve gerekiyorsa çeldiricinin neye ait olduğunu söyler. Uygulama şıkları karıştırdığı için `izah` şıkların sırasına atıf yapmaz ("ilk şık", "sırasıyla" yazılmaz); şıktan söz edilecekse içeriğiyle anılır.
- Slayttaki bir değer resmi belgeyle çelişiyorsa (envanterde karara bağlanır) o değerden soru sorulmaz; çeldiricide de kullanılmaz. Şıklardan biri slayttaki çelişkili bir değerle doğru çıkabiliyorsa o şık değiştirilir.
- Konu başına 10–18 soru, türler karışık.

## Kartlar

- Kart, sözlü sınavda ya da 42 savunmasında sorulabilecek bir sorudur: "X nedir?", "X ile Y'nin farkı nedir?", "Hocanın örneğini anlat", "Adımları say".
- Arka yüz kısa ve doğrudan cevaptır; liste kullanılabilir. Hocanın tanımı önce gelir. Ek açıklama varsa ayrı satırda "Ek:" diye başlar.
- Her ana kavram, her karşılaştırma ve her süreç için bir kart olur; konu başına 4–9 kart.
- Her karta `yer` yazılır; kart kimliği `<konu-id>.kN`'dir ve sonradan değişmez.

## Kavramlar

Her konunun ana terimleri `kavramlar`'a yazılır (`terim`, `izah`, `yer`). `izah` hocanın tanımının kısa hâlidir; kavram kartlarında ön yüz terim, arka yüz izahtır. Tanım slaytta yoksa izahın başında bunun söylenmesi gerekir (ör. "Ders kitabındaki tanım (slaytta yalnızca örnek var): ...").

## Uzlaşımlar

| Konu | Kural |
| --- | --- |
| Konu kimliği | `<ders-kısa>-<konu>`, ör. `vt-baginti-kisit`; kalıcıdır |
| Dosya adı | `NN-ad.md` / `NN-ad.json`; `NN` sıradır |
| Soru / kart kimliği | `<konu-id>.sN` / `<konu-id>.kN`; silinen kimlik yeniden kullanılmaz |
| `kaynak` | `dosya-adı.pdf, slayt a–b` (birden çok aralık virgülle) |
| `yer` | Bir `###` ya da `####` başlığıyla harfi harfine aynı |
| Dil | Bütün metinler, kod açıklamaları ve betik yorumları Türkçe |
| Hitap | Öğrenciye "siz" diye hitap edilir: soru ve kartlarda "eşleştirin, dizin, yazın, anlatın", notlarda "karıştırmayın, dikkat edin". Hocanın algoritma adımları ("Sonucu yaz") ve alıntıları olduğu gibi kalır |

## Denetim araçları

```
node araclar/icerik-aktar.mjs --kuru
python3 araclar/icerik-denetle.py icerik/dersler/<ders-id>
python3 araclar/sekiller/<ders-id>.py icerik/dersler/<ders-id>/gorseller
```

- `icerik-aktar.mjs --kuru` biçimi denetler: alanlar, `yer` eşleşmesi, kimlikler, görsel adları, Markdown kuralları, kapanmayan `**` ve ters tırnak.
- `icerik-denetle.py` içeriği denetler: eksik `yer`, en uzun doğru şık, şık sırasına atıf yapan izah, örnek cevapta geçmeyen anahtar, tekrarlanan cevap, kopya soru ya da kart, D/Y dengesi, sınav tahmini cümlesi, derste olmayan bir konuya atıf, çift boşluk, noktalamadan önce boşluk ve "sen" hitabı; konu başına sayıları da çıkarır.
- Uygulamada uçtan uca deneme (düzeneği depoda değildir, Playwright ile kurulur): içerik, `SUPABASE_URL=http://127.0.0.1:<port>` ile gerçek aktarıcı çalıştırılarak sahte bir sunucuya yüklenir (karşılanacak uçlar: `/rest/v1/konular`, `/rest/v1/agac` için GET ve POST, `/storage/v1/object/gorseller/<yol>` için POST), uygulama tarayıcıda açılır ve şunlar denenir: her konunun başlıkları birebir çizildi mi, her görsel yüklendi mi, tablolar çizildi mi; **her soru, içerikteki doğru cevapla cevaplanınca doğru sayılıyor mu**; klasik sorularda örnek cevap yazılınca bütün anahtarlar yeşil mi; "konuda oku" bağlantısı doğru başlığa gidiyor mu; 42 Tarzı'nda ders ve konu seçimi kart sayılarını doğru veriyor mu.

## Teslim raporu

Teslim mesajı şu sırayı izler:

1. Ne üretildi: konu sayısı, soru sayısı (türlere göre), kart ve kavram sayısı, görsel sayısı.
2. Denetim sonuçları: biçim denetimi, içerik denetimi, uçtan uca deneme, bağımsız denetimin bulgu sayıları ve hepsinin nasıl kapandığı.
3. Kaynakta bulunan sorunlar ve verilen karar (envanterden kısaca).
4. **🔶 Senin karar vermen gerekenler:** dönem, eksik hafta, ders adı, ağırlıklar gibi Hamza'nın bilmesi gereken ve içerikten çözülemeyen noktalar, belirgin biçimde ayrı bir bölümde.
5. Değişen dosyaların listesi.

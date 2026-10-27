"""Bir dersin içeriğini kalite yönünden denetler (icerik-aktar.mjs biçimi denetler, bu araç içeriği).

Kullanım:
    python3 araclar/icerik-denetle.py icerik/dersler/<ders-id>

Hata değil uyarı verir; her uyarı gözle bakılıp ya düzeltilir ya da bilerek bırakılır.
Denetlenenler:
  - yer: her kavram, soru ve kartta var mı; hiçbir şeye bağlanmamış başlıklar
  - kimlik sırası: s1, s2... ve k1, k2... (boşluk silinmiş kimliktir, uyarı değil bilgi)
  - seçme/izleme: doğru şık belirgin biçimde en uzun şık mı (cevabı ele verir);
    izah şıkların sırasına atıf yapıyor mu ("ilk şık", "sırasıyla"; şıklar karışır)
  - klasik: her anahtar kelime örnek cevabın içinde geçiyor mu (geçmiyorsa öğrenci
    örnek cevabı yazsa bile yeşil yanmaz)
  - boşluk: aynı cevabın iki kez yazılması, birden çok boşlukta sıra bağımlılığı
  - kopya: aynı soru metni ya da aynı kart önü iki kez
  - dağılım: konu başına tür sayıları, D/Y doğru-yanlış dengesi
  - atıf: '"X" konusu' diye anılan konu bu derste var mı
  - üslup: sınav tahmini cümlesi ("sınavda ... sorulur/esastır"); notta
    hocanın ifadesinin korunduğu söylenir, sınavda ne olacağı söylenmez
  - yazım: çift boşluk, noktalamadan önce boşluk (kod dışında)
  - hitap: uygulama öğrenciye "siz" diye hitap eder; "sen" biçimleri (yaz, diz,
    eşleştir...; yaparsın, kullanabilirsin; senin) uyarılır
"""
import json, os, re, sys
from collections import Counter

if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
    print(__doc__); sys.exit(2)
KLASOR = sys.argv[1]

def kucuk(s):
    return s.replace("İ", "i").replace("I", "ı").lower()

def normal(s):
    s = kucuk(re.sub(r"[`*]", "", str(s)))
    return re.sub(r"[.,;:!?]+$", "", re.sub(r"\s+", " ", s).strip())

uyarilar, bilgiler = [], []
uyar = lambda y, m: uyarilar.append(y + ": " + m)
bilgi = lambda y, m: bilgiler.append(y + ": " + m)

dosyalar = sorted(f[:-5] for f in os.listdir(KLASOR) if re.match(r"^\d\d-.+\.json$", f))
KONU_BASLIKLARI = {json.load(open(os.path.join(KLASOR, a + ".json"), encoding="utf-8")).get("baslik") for a in dosyalar}
SINAV_TAHMINI = re.compile(r"sınavda\s+.{0,60}?\b(?:esastır|geçerlidir|sorulur|çıkar|beklenir|kullan|yaz|cevap ver)\b", re.I)

SEN_EMIR = re.compile(r"(?<![\wçğıöşü'])(yaz|diz|eşleştir|sırala|anlat|açıkla|söyle|say|seç|ver|karıştırma|unutma|dikkat et|düşün)(?=[.:;!?]|$| ve )")
SEN_FIIL = re.compile(r"(?<![\wçğıöşü'])(sen|senin|sana|seni|kendin|[\wçğıöşü]{2,}(?:abilir|ebilir|ıyor|iyor|uyor|üyor|malı|meli|acak|ecek|ır|ir|ur|ür|ar|er)(?:sın|sin|sun|sün))(?![\wçğıöşü])")

def uslup_denetle(yer, metin, hitap=True):
    """Sınav tahmini, bilinmeyen konu atfı ve boşluk yazımı (kod dışında)."""
    duz = re.sub(r"`[^`]*`", "KOD", metin)
    if SINAV_TAHMINI.search(duz):
        uyar(yer, "sınav tahmini cümlesi; 'Notta hocanın ifadesi korundu' gibi yaz: " + SINAV_TAHMINI.search(duz).group(0)[:60])
    bulunan = [m.group(0) for m in SEN_FIIL.finditer(kucuk(duz))] + [m.group(1) for m in SEN_EMIR.finditer(duz)]
    if hitap and bulunan: uyar(yer, "\"sen\" hitabı (uygulama \"siz\" der): " + ", ".join(bulunan[:4]))
    for ref in re.findall(r"\"([^\"]{3,120})\" konusu", duz):
        if ref not in KONU_BASLIKLARI: uyar(yer, "bu derste '" + ref + "' adlı konu yok")
    for satir in duz.split("\n"):
        if re.match(r"^\s*\|", satir): continue
        if re.search(r"\S {2,}\S", satir): uyar(yer, "çift boşluk: " + satir.strip()[:60])
        # İki nokta hariç: hocanın sözde kodunda "Oku : A, B" biçimi var
        if re.search(r"\S [,.;!?](\s|$)", satir): uyar(yer, "noktalamadan önce boşluk: " + satir.strip()[:60])

gorulen_soru, gorulen_kart = {}, {}
dy_say = Counter()
ozet = []
for ad in dosyalar:
    konu = json.load(open(os.path.join(KLASOR, ad + ".json"), encoding="utf-8"))
    md = open(os.path.join(KLASOR, ad + ".md"), encoding="utf-8").read()
    basliklar = [re.sub(r"^#+\s*", "", l).strip() for l in md.split("\n") if re.match(r"^#{3,4} ", l)]
    kid = konu.get("id", ad)
    kodda = False
    for no, satir in enumerate(md.split("\n"), 1):
        if satir.startswith("```"): kodda = not kodda; continue
        # Numaralı liste satırları hocanın algoritma adımları olabilir ("Sonucu yaz"); hitap aranmaz
        if not kodda: uslup_denetle("%s.md:%d" % (ad, no), satir, hitap=not re.match(r"^\d+\. ", satir))
    def metinler(o):
        if isinstance(o, str): yield o
        elif isinstance(o, list):
            for x in o: yield from metinler(x)
        elif isinstance(o, dict):
            for k, v in o.items():
                if k not in ("id", "tip", "yer", "kod", "kaynak", "parcalar"): yield from metinler(v)
    for alan in ("kavramlar", "sorular", "kartlar"):
        for o in konu.get(alan, []):
            for m in metinler(o): uslup_denetle(o.get("id") or "%s %s" % (ad, alan), m)
    bagli = set()
    for alan in ("kavramlar", "sorular", "kartlar"):
        for i, o in enumerate(konu.get(alan, [])):
            y = "%s %s[%d]" % (ad, alan, i)
            if "yer" not in o: uyar(y, "'yer' yok; mühim süzgecinde konunun geneli sayılır")
            else: bagli.add(o["yer"])
    bos = [b for b in basliklar if b not in bagli]
    if bos: bilgi(ad, "hiçbir kavram, soru ya da karta bağlanmamış başlıklar: " + "; ".join(bos))

    for onek, alan in (("s", "sorular"), ("k", "kartlar")):
        nolar = []
        for o in konu.get(alan, []):
            m = re.match(re.escape(kid) + r"\." + onek + r"(\d+)$", o.get("id", ""))
            if not m: uyar(ad, "kimlik biçimi beklenmedik: " + str(o.get("id")))
            else: nolar.append(int(m.group(1)))
        if nolar and nolar != list(range(1, len(nolar) + 1)):
            bilgi(ad, alan + " kimlikleri ardışık değil (silinmiş kimlik olabilir): " + ", ".join(map(str, nolar)))

    for s in konu.get("sorular", []):
        y = s.get("id", ad)
        tip = s.get("tip")
        if tip in ("secme", "izleme", "dy") and re.search(r"\b(ilk|ikinci|üçüncü|dördüncü|son|diğer)\s+(şık|seçenek)|sırasıyla|seçeneklerdeki", kucuk(s.get("izah", ""))):
            uyar(y, "izah şıkların sırasına atıf yapıyor; şıklar her gösterimde karışır, şıkkın içeriğiyle yaz")
        if tip in ("secme", "izleme"):
            uz = [len(normal(x)) for x in s["secenekler"]]
            dogru = uz[s["dogru"]]
            digerleri = sorted(uz[:s["dogru"]] + uz[s["dogru"] + 1:])
            if digerleri and dogru > 1.25 * digerleri[-1]:
                uyar(y, "doğru şık belirgin biçimde en uzun (%d karaktere karşı en çok %d)" % (dogru, digerleri[-1]))
        if tip == "klasik":
            cevap = normal(s.get("cevap", ""))
            eksik = [a for a in s.get("anahtarlar", []) if normal(a) not in cevap]
            if eksik: uyar(y, "anahtar örnek cevapta geçmiyor: " + ", ".join(eksik))
        if tip == "bosluk":
            for i, c in enumerate(s.get("cevaplar", [])):
                n = [normal(x) for x in c]
                if len(set(n)) != len(n): uyar(y, "%d. boşlukta aynı cevap iki kez yazılmış" % (i + 1))
            if len(s.get("cevaplar", [])) > 1:
                bilgi(y, "birden çok boşluk var; cevaplar sıraya bağlı, yer değiştirilmiş doğru cevap yanlış sayılır")
        if tip == "dy": dy_say[s["dogru"]] += 1
        metin = normal(s.get("soru") or s.get("ifade") or s.get("metin") or "")
        if tip in ("secme", "izleme") and s.get("kod"): metin += " | " + normal(s["kod"])
        if metin in gorulen_soru: uyar(y, "aynı soru metni şurada da var: " + gorulen_soru[metin])
        else: gorulen_soru[metin] = y
    for k in konu.get("kartlar", []):
        on = normal(k.get("on", ""))
        if on in gorulen_kart: uyar(k.get("id", ad), "aynı kart önü şurada da var: " + gorulen_kart[on])
        else: gorulen_kart[on] = k.get("id", ad)
    tipler = Counter(s.get("tip") for s in konu.get("sorular", []))
    ozet.append((ad, len(konu.get("kavramlar", [])), len(konu.get("sorular", [])), len(konu.get("kartlar", [])),
                 " ".join("%s:%d" % (t, n) for t, n in sorted(tipler.items()))))

print("Konu                              kavram soru kart  türler")
for ad, kv, so, ka, t in ozet:
    print("%-34s %5d %5d %4d  %s" % (ad[:34], kv, so, ka, t))
toplam = [sum(x[i] for x in ozet) for i in (1, 2, 3)]
print("%-34s %5d %5d %4d" % ("TOPLAM", *toplam))
if dy_say:
    print("Doğru mu yanlış mı: %d doğru, %d yanlış" % (dy_say[True], dy_say[False]))
    if min(dy_say[True], dy_say[False]) < 0.3 * sum(dy_say.values()):
        uyar("ders", "D/Y soruları dengesiz; cevabın hep aynı olması tahmini kolaylaştırır")
if bilgiler:
    print("\nBilgi (%d):" % len(bilgiler))
    for b in bilgiler: print("  · " + b)
print("\nUyarı (%d):" % len(uyarilar))
for u in uyarilar: print("  • " + u)
if not uyarilar: print("  yok")

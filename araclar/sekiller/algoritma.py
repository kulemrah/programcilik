"""Algoritma ve Programlama Temelleri ders notlarının SVG şekillerini üretir.

Kullanım:
    python3 araclar/sekiller/algoritma.py icerik/dersler/algoritma/gorseller

Şekiller elle değil bu dosyadan üretilir; bir şekli düzeltmek için burayı değiştirip
yeniden çalıştır. Üstteki renkler ve yardımcılar veritabani.py'den aynen alındı;
altındaki şekiller bu derse göre yazıldı. Kurallar: icerik/ISLEME.md, "Görseller".
"""
import math, os, sys

HEDEF = sys.argv[1]
os.makedirs(HEDEF, exist_ok=True)

YAZI = "#1A202C"; SONUK = "#4A5568"; VURGU = "#C05621"
VARLIK_D = "#DCEBFA"; CIZGI = "#2B6CB0"; NITELIK_D = "#EEF6FF"; BAG_D = "#FFF1DC"; BAG_C = "#B7791F"
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class Sekil:
    def __init__(self, g, y, baslik):
        self.g, self.y, self.baslik, self.p = g, y, baslik, []
    def ekle(self, s): self.p.append(s)
    def yazi(self, x, y, s, boy=14, renk=YAZI, kalin=False, hiza="middle", font=FONT, alti=False, egik=False):
        self.ekle('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s"%s text-anchor="%s"%s%s>%s</text>' % (
            x, y, font, boy, renk, ' font-weight="600"' if kalin else "", hiza,
            ' text-decoration="underline"' if alti else "", ' font-style="italic"' if egik else "", esc(s)))
    def cizgi(self, x1, y1, x2, y2, renk=CIZGI, kal=1.6, kesik=False):
        self.ekle('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s/>' % (
            x1, y1, x2, y2, renk, kal, ' stroke-dasharray="5 4"' if kesik else ""))
    def ok(self, x1, y1, x2, y2, renk=SONUK, kal=1.5):
        self.cizgi(x1, y1, x2, y2, renk, kal)
        a = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - 9 * math.cos(a - 0.4), y2 - 9 * math.sin(a - 0.4))
        p2 = (x2 - 9 * math.cos(a + 0.4), y2 - 9 * math.sin(a + 0.4))
        self.ekle('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (x2, y2, p1[0], p1[1], p2[0], p2[1], renk))
    def varlik(self, x, y, g, y_, ad, zayif=False, boy=14):
        self.ekle('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x, y, g, y_, VARLIK_D, CIZGI))
        if zayif:
            self.ekle('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="1.3"/>' % (x + 4, y + 4, g - 8, y_ - 8, CIZGI))
        self.yazi(x + g / 2, y + y_ / 2 + boy * 0.35, ad, boy)
    def nitelik(self, cx, cy, ad, tur="duz", rx=None, ry=14, boy=13):
        rx = rx or max(30, len(ad) * 4.2 + 14)
        kesik = ' stroke-dasharray="4 3"' if tur == "turetilmis" else ""
        self.ekle('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="1.4"%s/>' % (cx, cy, rx, ry, NITELIK_D, CIZGI, kesik))
        if tur == "cok":
            self.ekle('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="1.2"/>' % (cx, cy, rx - 4, ry - 4, CIZGI))
        self.yazi(cx, cy + boy * 0.35, ad, boy, alti=(tur == "anahtar"))
        return rx
    def bag(self, cx, cy, ad, g=None, y_=46, cift=False, boy=13):
        g = g or max(84, len(ad) * 7.2 + 30)
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx, cy - y_ / 2, cx + g / 2, cy, cx, cy + y_ / 2, cx - g / 2, cy)
        self.ekle('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (pts, BAG_D, BAG_C))
        if cift:
            k = 0.8
            pts2 = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx, cy - y_ / 2 * k, cx + g / 2 * k, cy, cx, cy + y_ / 2 * k, cx - g / 2 * k, cy)
            self.ekle('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.2"/>' % (pts2, BAG_C))
        self.yazi(cx, cy + boy * 0.35, ad, boy)
        return g
    def isaret(self, ex, ey, ux, uy, tur, renk=CIZGI):
        """ex,ey: çizginin varlığa değdiği nokta; ux,uy: varlıktan dışarı doğru birim yön.
        tur: '||' bir ve yalnız bir, 'o|' sıfır ya da bir, '|<' bir ya da çok, 'o<' sıfır ya da çok"""
        px, py = -uy, ux
        def bar(d):
            cx, cy = ex + ux * d, ey + uy * d
            self.cizgi(cx - px * 7, cy - py * 7, cx + px * 7, cy + py * 7, renk, 1.6)
        def daire(d):
            cx, cy = ex + ux * d, ey + uy * d
            self.ekle('<circle cx="%.1f" cy="%.1f" r="4.5" fill="#FFFFFF" stroke="%s" stroke-width="1.5"/>' % (cx, cy, renk))
        def kaz():
            tx, ty = ex + ux * 14, ey + uy * 14
            for s in (-1, 0, 1):
                self.cizgi(tx, ty, ex + px * 8 * s, ey + py * 8 * s, renk, 1.6)
        if tur == "||": bar(7); bar(13)
        elif tur == "o|": bar(7); daire(19)
        elif tur == "|<": kaz(); bar(20)
        elif tur == "o<": kaz(); daire(22)
    def bulut(self, cx, cy, rx, ry, n=11):
        nok = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
        d = "M %.1f %.1f " % nok[0]
        for i in range(n):
            a, b = nok[i], nok[(i + 1) % n]
            r = math.hypot(b[0] - a[0], b[1] - a[1]) * 0.58
            d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (r, r, b[0], b[1])
        self.ekle('<path d="%s" fill="#E6F6F6" stroke="#2C7A7B" stroke-width="1.5"/>' % d)
    def kaydet(self, ad):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img">\n'
               '<title>%s</title>\n<rect width="100%%" height="100%%" fill="#FFFFFF"/>\n%s\n</svg>\n') % (
            self.g, self.y, self.g, self.y, esc(self.baslik), "\n".join(self.p))
        with open(os.path.join(HEDEF, ad), "w", encoding="utf-8") as f:
            f.write(svg)

def kutu(s, x, y, g, y_, dolgu="#F7FAFC", cizgi_="#CBD5E0", rx=8):
    s.ekle('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="%s" stroke="%s" stroke-width="1.2"/>' % (x, y, g, y_, rx, dolgu, cizgi_))

def mini_tablo(s, x, y, ad, alanlar, satirlar, sg=60, sy=20, etiket_sag=False):
    if etiket_sag: s.yazi(x + sg * len(alanlar) + 8, y + 15, ad, 12, kalin=True, hiza="start")
    else: s.yazi(x, y - 6, ad, 12, kalin=True, hiza="start")
    for j, a in enumerate(alanlar):
        s.ekle('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="#4A7FBF" stroke="#FFFFFF"/>' % (x + j * sg, y, sg, sy))
        s.yazi(x + j * sg + sg / 2, y + 14, a, 11, renk="#FFFFFF", kalin=True)
    for i, r in enumerate(satirlar):
        for j, h in enumerate(r):
            s.ekle('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="%s" stroke="#FFFFFF"/>' % (x + j * sg, y + sy * (i + 1), sg, sy, "#E2ECF7" if i % 2 == 0 else "#F1F6FB"))
            s.yazi(x + j * sg + sg / 2, y + sy * (i + 1) + 14, h, 11)

YESIL = "#2F855A"; KIRMIZI = "#C53030"; TURUNCU = "#C05621"; MOR = "#6B46C1"

def hucre_satiri(s, x, y, adlar, g, anahtarlar=(), y_=28, boy=12, isaretli=None):
    """Yan yana başlık hücreleri çizer; her hücrenin orta x'ini döndürür.
    g: tek sayı ya da hücre genişlikleri listesi; anahtarlar: altı çizili adlar;
    isaretli: {ad: renk} kenarı renkli hücreler"""
    gler = g if isinstance(g, (list, tuple)) else [g] * len(adlar)
    ortalar, cx = [], x
    for ad, gg in zip(adlar, gler):
        renk = (isaretli or {}).get(ad)
        s.ekle('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" fill="%s" stroke="%s" stroke-width="%s"/>' % (
            cx, y, gg, y_, "#FFF5F5" if renk else "#E2ECF7", renk or "#FFFFFF", 2 if renk else 1))
        s.yazi(cx + gg / 2, y + y_ / 2 + boy * 0.36, ad, boy, kalin=True, alti=(ad in anahtarlar))
        ortalar.append(cx + gg / 2)
        cx += gg
    return ortalar

def kod_satiri(x, y, parcalar, boy=13):
    """parcalar: [(metin, renk, kalin)] yan yana tek satır kod; tek aralıklı yazıda karakter genişliği ~0.6em"""
    cx = x
    for t, renk, kalin in parcalar:
        s.yazi(cx, y, t, boy, renk, kalin=kalin, hiza="start", font=MONO)
        cx += len(t) * boy * 0.6
    return cx

def isaret_imi(x, y, var):
    if var:
        s.ekle('<circle cx="%.1f" cy="%.1f" r="9" fill="%s"/>' % (x, y, YESIL))
        s.ekle('<path d="M %.1f %.1f l 3.5 3.5 l 6 -7" fill="none" stroke="#FFFFFF" stroke-width="2.2"/>' % (x - 5, y))
    else:
        s.ekle('<circle cx="%.1f" cy="%.1f" r="9" fill="#EDF2F7" stroke="#CBD5E0"/>' % (x, y))
        s.ekle('<path d="M %.1f %.1f l 7 7 M %.1f %.1f l -7 7" fill="none" stroke="#A0AEC0" stroke-width="2"/>' % (x - 3.5, y - 3.5, x + 3.5, y - 3.5))

# ================================================================ ŞEKİLLER
TURUNCU_D = "#FFF4E5"

def deger_kutusu(x, y, g, deger, eski=None, yeni=False, bos=False):
    """Bellekteki bir değişkenin kutusu; yeni atanan değer turuncu, silinen eski değer üstü çizili."""
    s.ekle('<rect x="%.1f" y="%.1f" width="%d" height="34" rx="6" fill="%s" stroke="%s" stroke-width="%s"/>' % (
        x, y, g, TURUNCU_D if yeni else ("#F7FAFC" if bos else "#FFFFFF"), VURGU if yeni else "#CBD5E0", 1.8 if yeni else 1.2))
    if bos:
        s.yazi(x + g / 2, y + 22, "–", 13, "#A0AEC0")
        return
    s.yazi(x + g / 2 + (6 if eski else 0), y + 23, deger, 15, VURGU if yeni else YAZI, kalin=yeni, font=MONO)
    if eski:
        s.yazi(x + 10, y + 15, eski, 11, "#A0AEC0", hiza="start", font=MONO)
        s.cizgi(x + 7, y + 11, x + 11 + len(eski) * 7, y + 11, "#A0AEC0", 1.2)

# ---------------------------------------------------------------- 1) atama örnekleri
s = Sekil(400, 336, "Atama: sağ taraf hesaplanır, sonuç soldaki değişkene yazılır")
DEG = ["SAYI", "TOPLAM", "A"]; XD = [178, 252, 326]
s.yazi(14, 24, "komut", 12, SONUK, kalin=True, hiza="start")
for ad, x in zip(DEG, XD):
    s.yazi(x + 33, 24, ad, 12, SONUK, kalin=True, font=MONO)
adimlar = [("SAYI = 2", "", {"SAYI": ("2", None)}),
           ("SAYI = 5", "2 silinir", {"SAYI": ("5", "2")}),
           ("SAYI = SAYI+1", "5+1 = 6", {"SAYI": ("6", "5")}),
           ("TOPLAM = SAYI+5", "6+5 = 11", {"TOPLAM": ("11", None)}),
           ("A = 8*3", "8*3 = 24", {"A": ("24", None)})]
durum = {}
for i, (kod, hesap, degisen) in enumerate(adimlar):
    y = 38 + i * 54
    if i % 2 == 0: s.ekle('<rect x="6" y="%d" width="388" height="50" rx="8" fill="#F7FAFC"/>' % (y - 4))
    s.yazi(14, y + 18, kod, 12.5, YAZI, kalin=True, hiza="start", font=MONO)
    if hesap: s.yazi(14, y + 36, hesap, 11.5, SONUK, hiza="start", font=MONO)
    for ad, x in zip(DEG, XD):
        if ad in degisen:
            yeni, eski = degisen[ad]; durum[ad] = yeni
            deger_kutusu(x, y + 4, 66, yeni, eski, yeni=True)
        elif ad in durum: deger_kutusu(x, y + 4, 66, durum[ad])
        else: deger_kutusu(x, y + 4, 66, "", bos=True)
s.yazi(200, 322, "eşittirin sağı hesaplanır → sonuç soldaki değişkene", 11.5, SONUK)
s.kaydet("atama-sayi.svg")

# ---------------------------------------------------------------- 2) işlem önceliği
s = Sekil(400, 268, "İşlem önceliği: X=2*3/6+2")
def ifade(y, parcalar, vurgu=None, renk=VURGU):
    """parcalar: karakter dizileri; vurgu: (baş, son) vurgulanacak parça aralığı"""
    boy = 18; gk = boy * 0.6; x0 = 30
    tum = "".join(parcalar)
    if vurgu:
        a = len("".join(parcalar[:vurgu[0]])); b = len("".join(parcalar[:vurgu[1]]))
        s.ekle('<rect x="%.1f" y="%d" width="%.1f" height="28" rx="5" fill="%s"/>' % (x0 + a * gk - 3, y - 20, (b - a) * gk + 6, TURUNCU_D))
        s.cizgi(x0 + a * gk - 2, y + 6, x0 + b * gk + 2, y + 6, renk, 2)
    s.yazi(x0, y, tum, boy, YAZI, hiza="start", font=MONO)
satirlar_ = [(["X = ", "2*3", "/6+2"], (1, 2), "1. çarpma ve bölme önce;", "aynı öncelik: soldan sağa"),
             (["X = ", "6/6", "+2"], (1, 2), "2. sıradaki bölme", ""),
             (["X = ", "1+2"], (1, 2), "3. toplama en son", ""),
             (["X = ", "3"], None, "sonuç", "")]
for i, (p, v, n1, n2) in enumerate(satirlar_):
    y = 40 + i * 58
    ifade(y, p, v)
    s.yazi(206, y - 4, n1, 12, SONUK, hiza="start")
    if n2: s.yazi(206, y + 12, n2, 12, SONUK, hiza="start")
    if i < 3: s.ok(60, y + 12, 60, y + 32, "#A0AEC0", 1.4)
s.ekle('<rect x="20" y="%d" width="80" height="34" rx="6" fill="none" stroke="%s" stroke-width="1.8"/>' % (40 + 3 * 58 - 24, YESIL))
s.yazi(200, 258, "öncelik: () → ^ → * / → + -", 12, VURGU, kalin=True)
s.kaydet("islem-onceligi.svg")

# ---------------------------------------------------------------- 3) mantıksal örnek
s = Sekil(400, 262, "(5>6 && 2<=7) ifadesinin çözümü")
s.ekle('<rect x="70" y="10" width="260" height="40" rx="8" fill="#EBF4FF" stroke="#2B6CB0" stroke-width="1.6"/>')
s.yazi(200, 37, "(5>6 && 2<=7)", 16, YAZI, kalin=True, font=MONO)
for x, ust, alt, renk, zemin in ((24, "5>6", "yanlış → 0", KIRMIZI, "#FFF5F5"), (216, "2<=7", "doğru → 1", YESIL, "#F0FFF4")):
    s.ok(200 + (x - 120) * 0.45, 52, x + 80, 84, SONUK, 1.5)
    s.ekle('<rect x="%d" y="88" width="160" height="58" rx="8" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x, zemin, renk))
    s.yazi(x + 80, 112, ust, 15, YAZI, kalin=True, font=MONO)
    s.yazi(x + 80, 134, alt, 13, renk, kalin=True)
    s.ok(x + 80, 148, 200 + (x - 120) * 0.25, 176, SONUK, 1.5)
s.ekle('<rect x="110" y="180" width="180" height="40" rx="8" fill="#FFF5F5" stroke="%s" stroke-width="1.8"/>' % KIRMIZI)
s.yazi(200, 206, "0 VE 1 = 0", 15, KIRMIZI, kalin=True)
s.yazi(200, 246, "sonuç: 0 (yanlış)", 13, SONUK, kalin=True)
s.kaydet("mantiksal-ornek.svg")

# ---------------------------------------------------------------- 4) örnek 1 izleme
s = Sekil(400, 322, "Örnek 1'in adımları ve değişkenler")
XS = [184, 230, 276, 340]; GS = [44, 44, 62, 52]
basl = ["A", "B", "TOPLAM", "ekran"]
s.yazi(14, 22, "adım", 12, SONUK, kalin=True, hiza="start")
for b, x, g in zip(basl, XS, GS):
    s.yazi(x + g / 2, 22, b, 11.5, SONUK, kalin=True, font=MONO if b != "ekran" else FONT)
adim1 = [("1. BAŞLA", "", {}), ("2. OKU: A", "klavye: 4", {"A": "4"}), ("3. OKU: B", "klavye: 7", {"B": "7"}),
         ("4. TOPLAM=A+B", "4+7 = 11", {"TOPLAM": "11"}), ("5. YAZ: TOPLAM", "", {"ekran": "11"}), ("6. BİTİR", "", {})]
durum = {}
for i, (ad, alt, deg) in enumerate(adim1):
    y = 34 + i * 44
    if i % 2 == 0: s.ekle('<rect x="6" y="%d" width="388" height="42" rx="8" fill="#F7FAFC"/>' % (y - 2))
    s.yazi(14, y + (16 if alt else 24), ad, 12.5, YAZI, kalin=True, hiza="start", font=MONO)
    if alt: s.yazi(26, y + 33, alt, 11, SONUK, hiza="start")
    for b, x, g in zip(basl, XS, GS):
        if b in deg:
            durum[b] = deg[b]
            s.ekle('<rect x="%d" y="%d" width="%d" height="30" rx="5" fill="%s" stroke="%s" stroke-width="1.8"/>' % (x + 2, y + 4, g - 4, TURUNCU_D, VURGU))
            s.yazi(x + g / 2, y + 24, deg[b], 14, VURGU, kalin=True, font=MONO)
        elif b in durum:
            s.ekle('<rect x="%d" y="%d" width="%d" height="30" rx="5" fill="#FFFFFF" stroke="#CBD5E0"/>' % (x + 2, y + 4, g - 4))
            s.yazi(x + g / 2, y + 24, durum[b], 14, YAZI, font=MONO)
s.yazi(200, 314, "turuncu: o adımda değeri değişen yer", 11.5, SONUK)
s.kaydet("ornek1-izleme.svg")

# ---------------------------------------------------------------- 5) temel algoritma grupları
s = Sekil(400, 470, "Hocanın verdiği temel algoritma grupları")
gruplar_ = [("1. Sıralama", [("basit:", None), ("Bubble", 0), ("Selection", 0), ("Insertion", 0), ("\n", None), ("gelişmiş:", None), ("Quick", 1), ("Merge", 1)], "#2B6CB0"),
            ("2. Arama", [("Linear", 0), ("Binary", 0)], "#2C7A7B"),
            ("3. Graf", [("BFS", 0), ("DFS", 0), ("Dijkstra", 0), ("Floyd-Warshall", 0)], MOR),
            ("4. Dinamik programlama", [("Fibonacci", 0), ("Knapsack", 0)], YESIL),
            ("5. Karmaşık sınıflar", [("Greedy", 0), ("Hashing", 0), ("Şifreleme", 0), ("Makine öğrenimi", 0)], VURGU)]
y = 10
for ad, ogeler, renk in gruplar_:
    # önce çipleri satırlara yerleştir
    satir_, x = [[]], 16
    for t, tur in ogeler:
        if t == "\n": satir_.append([]); x = 16; continue
        g = len(t) * 7.2 + (0 if tur is None else 20)
        if x + g > 384: satir_.append([]); x = 16
        satir_[-1].append((t, tur, x, g)); x += g + 6
    yuk = 34 + len(satir_) * 32 + 6
    s.ekle('<rect x="8" y="%d" width="384" height="%d" rx="10" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % (y, yuk, renk))
    s.ekle('<rect x="8" y="%d" width="6" height="%d" rx="3" fill="%s"/>' % (y, yuk, renk))
    s.yazi(22, y + 24, ad, 14, renk, kalin=True, hiza="start")
    for k, sat in enumerate(satir_):
        yy = y + 36 + k * 32
        for t, tur, x, g in sat:
            if tur is None:
                s.yazi(x, yy + 18, t, 12, SONUK, hiza="start")
            else:
                s.ekle('<rect x="%.1f" y="%d" width="%.1f" height="26" rx="13" fill="%s" stroke="%s"/>' % (x, yy, g, "#F7FAFC", "#CBD5E0"))
                s.yazi(x + g / 2, yy + 17.5, t, 12, YAZI)
    y += yuk + 10
s.y = y
s.kaydet("temel-algoritmalar.svg")

# ---------------------------------------------------------------- 6) ikili arama
s = Sekil(400, 300, "İkili arama: arama alanı her adımda yarıya iner")
dizi = [4, 8, 15, 16, 23, 31, 42, 50, 61]; aranan = 50
s.yazi(14, 22, "sıralı dizi, aranan: 50", 13, YAZI, kalin=True, hiza="start")
lo, hi, adim, y = 0, len(dizi) - 1, 1, 40
while lo <= hi:
    orta = (lo + hi) // 2
    for k, d in enumerate(dizi):
        x = 18 + k * 40
        icinde = lo <= k <= hi
        dolgu = TURUNCU_D if k == orta else ("#EBF4FF" if icinde else "#F7FAFC")
        cizgi_ = VURGU if k == orta else ("#90CDF4" if icinde else "#E2E8F0")
        s.ekle('<rect x="%d" y="%d" width="36" height="32" rx="5" fill="%s" stroke="%s" stroke-width="%s"/>' % (x, y, dolgu, cizgi_, 1.8 if k == orta else 1.2))
        s.yazi(x + 18, y + 21, str(d), 13, YAZI if icinde else "#A0AEC0", kalin=(k == orta), font=MONO)
    if dizi[orta] == aranan: not_ = "%d. adım: orta %d = 50 → bulundu" % (adim, dizi[orta]); renk = YESIL
    elif dizi[orta] < aranan: not_ = "%d. adım: orta %d < 50 → sağ yarıda ara" % (adim, dizi[orta]); renk = SONUK
    else: not_ = "%d. adım: orta %d > 50 → sol yarıda ara" % (adim, dizi[orta]); renk = SONUK
    s.yazi(18, y + 52, not_, 12, renk, kalin=(renk == YESIL), hiza="start")
    if dizi[orta] == aranan: break
    if dizi[orta] < aranan: lo = orta + 1
    else: hi = orta - 1
    adim += 1; y += 78
s.y = y + 70
s.kaydet("ikili-arama.svg")

# ================================================================ 1.–2. HAFTA
MAVI = "#2B6CB0"; TURKUAZ = "#2C7A7B"

def kutucuk(x, y, g, y_, baslik, alt, renk, zemin="#FFFFFF", boy=14):
    s.ekle('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="%s" stroke="%s" stroke-width="1.8"/>' % (x, y, g, y_, zemin, renk))
    satir = [alt] if isinstance(alt, str) else alt
    ust = y + y_ / 2 - (len(satir) * 15) / 2 + (4 if satir and satir[0] else 10)
    s.yazi(x + g / 2, ust, baslik, boy, renk, kalin=True)
    for k, a in enumerate(satir):
        if a: s.yazi(x + g / 2, ust + 18 + k * 15, a, 11.5, SONUK)

# ---------------------------------------------------------------- 7) bilgisayarın birimleri
s = Sekil(400, 414, "Bilgisayarın birimleri")
kutucuk(10, 126, 92, 76, "Giriş", ["klavye, fare,", "mikrofon"], MAVI)
kutucuk(298, 126, 92, 76, "Çıkış", ["ekran,", "yazıcı"], MAVI)
s.ekle('<rect x="114" y="14" width="172" height="300" rx="12" fill="#F7FAFC" stroke="%s" stroke-width="2"/>' % MOR)
s.yazi(200, 38, "CPU (işlemci)", 15, MOR, kalin=True)
s.yazi(200, 55, "bilgisayarın beyni", 11.5, SONUK)
kutucuk(126, 68, 148, 70, "CU", ["kontrol (denetim)", "birimi: komut sırası"], MOR, boy=13)
kutucuk(126, 146, 148, 70, "ALU", ["aritmetik ve", "mantıksal işlemler"], MOR, boy=13)
kutucuk(126, 224, 148, 76, "Registers", ["saklayıcılar: hızlı,", "geçici depo"], MOR, boy=13)
s.ok(104, 164, 112, 164, SONUK, 1.8); s.ok(288, 164, 296, 164, SONUK, 1.8)
s.ok(200, 316, 200, 334, SONUK, 1.8); s.ok(200, 334, 200, 316, SONUK, 1.8)
s.ekle('<rect x="20" y="338" width="360" height="68" rx="12" fill="#F7FAFC" stroke="%s" stroke-width="2"/>' % YESIL)
s.yazi(34, 358, "Bellek", 14, YESIL, kalin=True, hiza="start")
s.yazi(120, 358, "birincil: RAM", 12.5, YAZI, kalin=True, hiza="start")
s.yazi(120, 376, "geçici, hızlı; elektrik gidince silinir", 11.5, SONUK, hiza="start")
s.yazi(120, 391, "ikincil: sabit disk (kalıcı)", 11.5, SONUK, hiza="start")
s.kaydet("bilgisayar-birimleri.svg")

# ---------------------------------------------------------------- 8) dil seviyeleri
s = Sekil(400, 228, "Programlama dillerinin seviyeleri")
for i, (ad, ornek, renk) in enumerate([("Yüksek seviyeli diller", "Basic, Fortran, Pascal", MAVI),
                                        ("Orta seviyeli diller", "C/C++", MOR),
                                        ("Düşük seviyeli diller", "makine dili, assembly", VURGU)]):
    y = 12 + i * 70
    s.ekle('<rect x="20" y="%d" width="360" height="60" rx="10" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % (y, renk))
    s.ekle('<rect x="20" y="%d" width="8" height="60" rx="4" fill="%s"/>' % (y, renk))
    s.yazi(44, y + 26, ad, 14, renk, kalin=True, hiza="start")
    s.yazi(44, y + 46, ornek, 12.5, YAZI, hiza="start")
s.kaydet("dil-seviyeleri.svg")

# ---------------------------------------------------------------- 9) derleme
s = Sekil(400, 296, "Kaynak koddan makine diline")
adim_ = [("Kaynak kodu", "kolay yazılıp okunan kod", MAVI), ("Derleyici (compiler)", "makine diline çevirir", MOR),
         ("Nesne kodu", "makine diline çevrilmiş kod", TURKUAZ), ("CPU yürütür", "0 ve 1'lerden oluşan yönergeler", YESIL)]
for i, (b, a, renk) in enumerate(adim_):
    y = 10 + i * 72
    kutucuk(60, y, 280, 54, b, a, renk)
    if i < 3: s.ok(200, y + 56, 200, y + 70, SONUK, 1.8)
s.kaydet("derleme.svg")

# ---------------------------------------------------------------- 10) derleyici ve yorumlayıcı
s = Sekil(400, 300, "Derleyici ile yorumlayıcı arasındaki fark")
for x, bas, renk, satir_, alt_ in ((10, "Derleyici", MOR, ["makine diline çevirir,", "söz dizimi hatası bulur", "makine dili kodu", "saklanır"], "Pascal, C/C++, Delphi"),
                                   (206, "Yorumlayıcı", TURKUAZ, ["o anda çevirir; her", "çalıştırmada yeniden", "makine dili kodu", "saklanmaz"], "ASP, JavaScript, MATLAB")):
    s.ekle('<rect x="%d" y="10" width="184" height="280" rx="12" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % (x, renk))
    s.ekle('<rect x="%d" y="10" width="184" height="40" rx="12" fill="%s"/>' % (x, renk))
    s.ekle('<rect x="%d" y="36" width="184" height="14" fill="%s"/>' % (x, renk))
    s.yazi(x + 92, 36, bas, 15, "#FFFFFF", kalin=True)
    for k, t_ in enumerate(satir_):
        s.yazi(x + 92, 84 + k * 22 + (10 if k >= 2 else 0), t_, 12.5, YAZI, kalin=(k in (1, 3)))
    s.cizgi(x + 20, 216, x + 164, 216, "#E2E8F0", 1.2)
    s.yazi(x + 92, 240, "hocanın örnekleri:", 11.5, SONUK)
    s.yazi(x + 92, 262, alt_, 12, YAZI)
s.kaydet("derleyici-yorumlayici.svg")

# ---------------------------------------------------------------- 11) problem çözümü
s = Sekil(400, 520, "Problem çözümü adımları")
pc = ["Sorunu net anla", "İhtiyaç ve istekleri belirle", "Zihinsel alıştırmalar yap", "En uygun çözümü seç",
      "Çözümü algoritmayla ifade et", "Akış çizgesi oluştur", "Dil seç, bilgisayara aktar", "Verilerle test et", "Sorunları düzelt"]
for i, t_ in enumerate(pc):
    y = 10 + i * 56
    son = i == len(pc) - 1
    renk = VURGU if son else (MAVI if i < 4 else (MOR if i < 6 else YESIL))
    s.ekle('<rect x="40" y="%d" width="270" height="42" rx="8" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % (y, renk))
    s.ekle('<circle cx="62" cy="%d" r="12" fill="%s"/>' % (y + 21, renk))
    s.yazi(62, y + 25.5, str(i + 1), 12, "#FFFFFF", kalin=True)
    s.yazi(84, y + 26, t_, 13, YAZI, hiza="start")
    if not son: s.ok(175, y + 43, 175, y + 54, "#A0AEC0", 1.4)
# düzeltme döngüsü: 9'dan 8'e geri
y8, y9 = 10 + 7 * 56 + 21, 10 + 8 * 56 + 21
for k, t_ in enumerate(["ilgili", "kısımlar", "tekrar", "gözden", "geçirilir"]):
    s.yazi(354, y9 - 30 + k * 14, t_, 11, VURGU, hiza="middle")
s.kaydet("problem-cozumu.svg")

# ---------------------------------------------------------------- 12) algoritmanın özellikleri
s = Sekil(400, 384, "Algoritmanın beş özelliği")
oz = [("Etkinlik", "adımlar anlaşılır, basit, kesin; yorum gerektirmez", MAVI),
      ("Sonluluk", "başlangıç, adımlar, bitiş; sonsuz döngü yok", MOR),
      ("Kesinlik", "aynı veriyle her çalıştırmada aynı sonuç", TURKUAZ),
      ("Giriş/çıkış", "işlenecek değerler girer, sonuçlar çıkar", YESIL),
      ("Başarım", "bellek ve süre dikkate alınır", VURGU)]
for i, (ad, a, renk) in enumerate(oz):
    y = 10 + i * 74
    s.ekle('<rect x="10" y="%d" width="380" height="64" rx="10" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % (y, renk))
    s.ekle('<rect x="10" y="%d" width="8" height="64" rx="4" fill="%s"/>' % (y, renk))
    s.yazi(32, y + 27, ad, 15, renk, kalin=True, hiza="start")
    s.yazi(32, y + 48, a, 12, YAZI, hiza="start")
s.kaydet("algoritma-ozellikleri.svg")

# ---------------------------------------------------------------- 13) suyun durumu
s = Sekil(400, 340, "Suyun durumu: ayrı Eğer'ler ile değilse eğer zinciri")
s.yazi(200, 22, "sıcaklık = -5 girildiğinde", 13, YAZI, kalin=True)
for x, bas, renk, satir_, sonuc in ((8, "ayrı \"Eğer\"ler", KIRMIZI,
                                     [("Eğer <0 → Buz", True), ("Eğer >=100 → Buhar", False), ("Değilse → Su", True)], "Su (yanlış)"),
                                    (204, "\"değilse eğer\" zinciri", YESIL,
                                     [("Eğer <0 → Buz", True), ("Değilse eğer >=100", None), ("Değilse → Su", None)], "Buz (doğru)")):
    s.ekle('<rect x="%d" y="36" width="188" height="294" rx="12" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % (x, renk))
    s.yazi(x + 94, 62, bas, 13, renk, kalin=True)
    for k, (t_, calisti) in enumerate(satir_):
        y = 84 + k * 58
        dolgu = TURUNCU_D if calisti else "#F7FAFC"
        cz = VURGU if calisti else "#CBD5E0"
        s.ekle('<rect x="%d" y="%d" width="164" height="44" rx="8" fill="%s" stroke="%s" stroke-width="1.4"/>' % (x + 12, y, dolgu, cz))
        s.yazi(x + 94, y + 20, t_, 12, YAZI if calisti is not None else "#A0AEC0", kalin=bool(calisti), font=MONO)
        not_ = {True: "çalıştı", False: "koşul yanlış", None: "atlandı"}[calisti]
        s.yazi(x + 94, y + 36, not_, 11, VURGU if calisti else SONUK)
    s.yazi(x + 94, 286, "Durum =", 12, SONUK)
    s.yazi(x + 94, 308, sonuc, 14, renk, kalin=True)
s.kaydet("su-durumu.svg")

# ================================================================ 4. HAFTA: KARAR YAPILARI
YESIL_D = "#F0FFF4"; KIRMIZI_D = "#FFF5F5"

# ---------------------------------------------------------------- 14) karar yapısı
s = Sekil(400, 352, "Karar yapısı: koşuldan dönen değere göre iki kısımdan yalnızca biri")
s.ekle('<rect x="90" y="10" width="220" height="62" rx="10" fill="#EBF4FF" stroke="%s" stroke-width="1.8"/>' % MAVI)
s.yazi(200, 36, "EĞER (koşul) İSE", 15, MAVI, kalin=True)
s.yazi(200, 58, "koşuldan dönen değer?", 12, SONUK)
for x, etiket, renk, zemin, b1, b2, a1, a2 in (
        (10, "doğru", YESIL, YESIL_D, "EĞER İSE kısmındaki", "işlemler gerçekleştirilir", "DEĞİL İSE kısmındaki", "işlemler gerçekleştirilmez"),
        (206, "yanlış", KIRMIZI, KIRMIZI_D, "DEĞİL İSE kısmındaki", "işlemler gerçekleştirilir", "başka bir koşula", "bakılmadan")):
    cx = x + 92
    s.ok(200 + (cx - 200) * 0.35, 74, cx, 128, renk, 1.8)
    s.yazi(cx + (-34 if x < 100 else 34), 104, etiket, 13, renk, kalin=True)
    s.ekle('<rect x="%d" y="132" width="184" height="120" rx="10" fill="%s" stroke="%s" stroke-width="1.8"/>' % (x, zemin, renk))
    s.yazi(cx, 162, b1, 12.5, YAZI, kalin=True)
    s.yazi(cx, 182, b2, 12.5, YAZI, kalin=True)
    s.cizgi(x + 20, 198, x + 164, 198, "#E2E8F0", 1.2)
    s.yazi(cx, 220, a1, 11.5, SONUK)
    s.yazi(cx, 237, a2, 11.5, SONUK)
    s.ok(cx, 254, 200 + (cx - 200) * 0.3, 292, SONUK, 1.5)
s.ekle('<rect x="120" y="296" width="160" height="40" rx="10" fill="#F7FAFC" stroke="#CBD5E0" stroke-width="1.4"/>')
s.yazi(200, 321, "sonraki adım", 13, SONUK, kalin=True)
s.kaydet("karar-yapisi.svg")

# ---------------------------------------------------------------- 15) hocanın örneği: iki sayıdan büyük olanı
s = Sekil(400, 352, "Hocanın örneği üç farklı girişle")
s.ekle('<rect x="8" y="8" width="384" height="104" rx="10" fill="#F7FAFC" stroke="#CBD5E0" stroke-width="1.2"/>')
for k, parca in enumerate([[("1.Başla", YAZI, False)],
                           [("2.Oku : A, B", YAZI, False)],
                           # boşluklar ayrı parça: SVG baştaki ve sondaki boşluğu yutar, kod_satiri ise genişliği sayar
                           [("3.", YAZI, False), ("EĞER", MAVI, True), (" ", YAZI, False), ("A>B", YAZI, False), (" ", YAZI, False),
                            ("İSE", MAVI, True), ("  ", YAZI, False), ("Yaz: A", YAZI, False)],
                           [("  ", YAZI, False), ("DEĞİL İSE", MAVI, True), ("  ", YAZI, False), ("Yaz: B", YAZI, False)],
                           [("4.Bitir.", YAZI, False)]]):
    kod_satiri(22, 28 + k * 19, parca, 13)
BAS = [("A, B", 16), ("A>B", 112), ("gerçekleşen kısım", 186), ("ekran", 344)]
for t_, x in BAS:
    s.yazi(x + (0 if t_ != "ekran" else 18), 138, t_, 12, SONUK, kalin=True, hiza="start" if t_ != "ekran" else "middle")
for i, (a, b) in enumerate([(8, 3), (4, 9), (7, 7)]):
    y = 150 + i * 62
    dogru = a > b
    renk = YESIL if dogru else KIRMIZI
    if i % 2 == 0: s.ekle('<rect x="6" y="%d" width="388" height="56" rx="8" fill="#F7FAFC"/>' % y)
    s.yazi(16, y + 34, "%d, %d" % (a, b), 15, YAZI, kalin=True, hiza="start", font=MONO)
    s.yazi(112, y + 24, "%d>%d" % (a, b), 13, YAZI, hiza="start", font=MONO)
    s.yazi(112, y + 42, "doğru" if dogru else "yanlış", 12, renk, kalin=True, hiza="start")
    s.ekle('<rect x="184" y="%d" width="140" height="40" rx="8" fill="%s" stroke="%s" stroke-width="1.6"/>' % (y + 8, TURUNCU_D, VURGU))
    s.yazi(254, y + 25, "EĞER İSE" if dogru else "DEĞİL İSE", 12, VURGU, kalin=True)
    s.yazi(254, y + 41, "Yaz: A" if dogru else "Yaz: B", 12, YAZI, font=MONO)
    s.ekle('<rect x="336" y="%d" width="52" height="40" rx="8" fill="#FFFFFF" stroke="#CBD5E0" stroke-width="1.4"/>' % (y + 8))
    s.yazi(362, y + 34, str(a if dogru else b), 16, YAZI, kalin=True, font=MONO)
s.yazi(200, 342, "7, 7: 7>7 yanlış → DEĞİL İSE, B yazılır", 11.5, SONUK)
s.kaydet("buyuk-sayi.svg")

def aralik_seridi(baslik, dilimler, ad):
    """dilimler: [(etiket, alt yazı satırları, genişlik, renk)] soldan sağa yan yana dilimler."""
    global s
    s = Sekil(400, 150, baslik)
    s.yazi(200, 22, baslik, 13, YAZI, kalin=True)
    x = 20
    for etiket, altlar, g, renk in dilimler:
        s.ekle('<rect x="%d" y="36" width="%d" height="52" fill="%s" stroke="#FFFFFF" stroke-width="2"/>' % (x, g, renk))
        s.yazi(x + g / 2, 68, etiket, 15 if len(etiket) <= 2 else 13, "#FFFFFF", kalin=True)
        for k, a in enumerate(altlar):
            s.yazi(x + g / 2, 108 + k * 15, a, 11.5, YAZI)
        x += g
    s.kaydet(ad)

# ---------------------------------------------------------------- 16) Örnek 7: harf notu
aralik_seridi("Örnek 7: not aralıkları",
              [("F", ["60 altı"], 120, KIRMIZI), ("D", ["60 - 69"], 60, VURGU), ("C", ["70 - 79"], 60, MOR),
               ("B", ["80 - 89"], 60, MAVI), ("A", ["90 ve", "üzeri"], 60, YESIL)], "harf-notu.svg")

# ---------------------------------------------------------------- 17) Örnek 8: yaş grupları
aralik_seridi("Örnek 8: yaş grupları",
              [("Çocuk", ["0-12"], 80, TURKUAZ), ("Genç", ["13-19"], 80, MAVI), ("Yetişkin", ["20-64"], 120, MOR),
               ("Yaşlı", ["65 ve", "üzeri"], 80, VURGU)], "yas-gruplari.svg")

print("tamam: " + HEDEF)

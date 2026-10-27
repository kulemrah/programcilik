"""Veritabanı ders notlarının SVG şekillerini üretir.

Kullanım:
    python3 araclar/sekiller/veritabani.py icerik/dersler/veritabani/gorseller

Şekiller elle değil bu dosyadan üretilir; bir şekli düzeltmek için burayı değiştirip
yeniden çalıştır. Başka bir ders için bu dosyayı kopyala: üstteki renkler ve
yardımcılar (Sekil, kutu, mini_tablo, satir_bagintisi) aynen kalır, altındaki
şekiller derse göre yazılır. Kurallar: icerik/ISLEME.md, "Görseller".
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

# ---------------------------------------------------------------- 1) veri türleri
s = Sekil(400, 372, "Yapısal olmayan, yarı yapısal ve yapısal veri")
for i, (b, a) in enumerate([("Yapısal olmayan", "belli bir veri modeli yok"), ("Yarı yapısal", "etiketlerle ifade edilir"), ("Yapısal", "bir veri modeline sahip")]):
    y0 = 12 + i * 120
    kutu(s, 10, y0, 380, 108)
    s.yazi(22, y0 + 24, b, 15, kalin=True, hiza="start")
    s.yazi(22, y0 + 43, a, 12, SONUK, hiza="start")
# yapısal olmayan: belge
s.ekle('<rect x="190" y="26" width="186" height="80" rx="4" fill="#FFFFFF" stroke="#A0AEC0"/>')
for k, t in enumerate(["Ali'nin telefon numaraları", "05xxx ve 05yyy'dir.", "Kitap, resim, ses, video,", "web sayfası..."]):
    s.yazi(200, 46 + k * 17, t, 12, YAZI if k < 2 else SONUK, hiza="start")
s.yazi(22, 92, "ör. web sayfası, kitap", 12, SONUK, hiza="start")
# yarı yapısal: XML
s.ekle('<rect x="190" y="146" width="186" height="80" rx="4" fill="#2D3748"/>')
for k, t in enumerate(["<kisi>Ali", "  <tel>05xxx</tel>", "  <tel>05yyy</tel>", "</kisi>"]):
    girinti = len(t) - len(t.lstrip(" "))   # SVG baştaki boşluğu yutar: girinti x ile verilir
    s.yazi(200 + girinti * 7.2, 166 + k * 17, t.lstrip(" "), 12, "#F7FAFC", hiza="start", font=MONO)
s.yazi(22, 212, "ör. XML", 12, SONUK, hiza="start")
# yapısal: iki tablo
mini_tablo(s, 186, 290, "Kisi", ["no", "ad"], [["1", "Ali"]], sg=40)
mini_tablo(s, 286, 290, "Telefonlar", ["no", "tel"], [["1", "05xxx"], ["1", "05yyy"]], sg=46)
s.ok(268, 320, 284, 320)
s.yazi(22, 332, "ör. veritabanı", 12, SONUK, hiza="start")
s.kaydet("veri-turleri.svg")

# ---------------------------------------------------------------- 2) veri modelleri
s = Sekil(400, 614, "Hiyerarşik, ağ ve ilişkisel veri modelleri")
def dugum(x, y, t, g=58):
    s.ekle('<rect x="%.1f" y="%.1f" width="%d" height="24" rx="3" fill="#FFFFFF" stroke="%s" stroke-width="1.4"/>' % (x - g / 2, y - 12, g, CIZGI))
    s.yazi(x, y + 4.5, t, 12)
kutu(s, 10, 10, 380, 170)
s.yazi(22, 34, "Hiyerarşik: ağaç", 15, kalin=True, hiza="start")
dugum(200, 62, "KÖK")
for x in (120, 280):
    s.ok(200, 74, x, 98); dugum(x, 110, "DAL")
    for dx in (-38, 38):
        s.ok(x, 122, x + dx, 146); dugum(x + dx, 158, "DAL", 52)
s.yazi(380, 34, "her düğümün tek üstü var", 11, SONUK, hiza="end")
kutu(s, 10, 192, 380, 196)
s.yazi(22, 216, "Ağ: graf", 15, kalin=True, hiza="start")
s.yazi(380, 216, "bir düğümün birden çok üstü olabilir", 11, SONUK, hiza="end")
P = {"Veri1": (200, 244), "Veri2": (90, 290), "Veri3": (310, 290), "Veri4": (130, 356), "Veri5": (290, 356)}
for a, b in [("Veri1", "Veri2"), ("Veri1", "Veri3"), ("Veri1", "Veri4"), ("Veri2", "Veri3"), ("Veri2", "Veri4"), ("Veri3", "Veri4"), ("Veri3", "Veri5")]:
    (x1, y1), (x2, y2) = P[a], P[b]
    a_ = math.atan2(y2 - y1, x2 - x1)
    # kutu kenarına kadar
    def kenar(x, y, a, g=29, h=12):
        t = min(g / abs(math.cos(a)) if abs(math.cos(a)) > 1e-6 else 1e9, h / abs(math.sin(a)) if abs(math.sin(a)) > 1e-6 else 1e9)
        return x + t * math.cos(a), y + t * math.sin(a)
    sx, sy = kenar(x1, y1, a_); tx, ty = kenar(x2, y2, a_ + math.pi)
    s.ok(sx, sy, tx, ty)
for k, (x, y) in P.items(): dugum(x, y, k)
kutu(s, 10, 400, 380, 204)
s.yazi(22, 424, "İlişkisel: tablolar", 15, kalin=True, hiza="start")
s.yazi(380, 424, "bağlantılar: matematiksel ilişkiler", 11, SONUK, hiza="end")
mini_tablo(s, 22, 458, "uye", ["uyeNo", "adi"], [["7", "Ece"]], sg=52)
mini_tablo(s, 150, 458, "odunc", ["oduncNo", "uyeNo", "kitapNo"], [["1", "7", "12"]], sg=60)
mini_tablo(s, 22, 556, "Kitap", ["kitapNo", "kitapAdi"], [["12", "Nutuk"]], sg=62, etiket_sag=True)
# uye.uyeNo -> odunc.uyeNo ; odunc.kitapNo -> Kitap.kitapNo
for nok in ([(48, 498), (48, 514), (240, 514), (240, 498)], [(300, 498), (300, 534), (53, 534), (53, 556)]):
    for (x1, y1), (x2, y2) in zip(nok, nok[1:]):
        s.cizgi(x1, y1, x2, y2, VURGU, 1.5, True)
s.yazi(316, 530, "kitapNo", 11, VURGU, hiza="start")
s.yazi(140, 528, "uyeNo", 11, VURGU)
s.kaydet("veri-modelleri.svg")

# ---------------------------------------------------------------- 3) veritabanı yapısı
s = Sekil(400, 318, "Veritabanı, tablolar ve bir tablonun alanları ile kayıtları")
s.ekle('<path d="M160 30 v44 a40 10 0 0 0 80 0 v-44" fill="#4A7FBF" stroke="#2B6CB0"/>')
s.ekle('<ellipse cx="200" cy="30" rx="40" ry="10" fill="#6C9BD2" stroke="#2B6CB0"/>')
s.yazi(200, 62, "Veritabanı", 13, "#FFFFFF", kalin=True)
xs = [40, 120, 200, 280, 360]
for x in xs:
    s.cizgi(200, 84, x, 112, "#90A4BE", 1.2)
    s.ekle('<rect x="%d" y="112" width="56" height="38" fill="#4A7FBF" stroke="#2B6CB0"/>' % (x - 28))
    s.yazi(x, 128, "Tablo", 11, "#FFFFFF", kalin=True)
s.cizgi(200, 150, 200, 176, "#90A4BE", 1.2)
tx, ty, sg, sy = 96, 186, 52, 24
s.ekle('<rect x="%d" y="%d" width="%d" height="%d" fill="#4A7FBF"/>' % (tx, ty, 26 + 4 * sg, sy))
for j in range(4):
    s.yazi(tx + 26 + j * sg + sg / 2, ty + 16, "Alan %d" % (j + 1), 11, "#FFFFFF", kalin=True)
for i in range(3):
    s.ekle('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#FFFFFF"/>' % (tx, ty + sy * (i + 1), 26 + 4 * sg, sy, "#E2ECF7" if i % 2 == 0 else "#F1F6FB"))
    s.yazi(tx + 13, ty + sy * (i + 1) + 16, str(i + 1), 11, SONUK)
s.ekle('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2"/>' % (tx + 26 + 2 * sg, ty, sg, sy * 4, VURGU))
s.yazi(tx + 26 + 2.5 * sg, ty - 8, "alan = sütun", 12, VURGU, kalin=True)
s.ekle('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#2C7A7B" stroke-width="2"/>' % (tx, ty + sy * 2, 26 + 4 * sg, sy))
s.yazi(tx + 26 + 4 * sg + 8, ty + sy * 2 + 16, "kayıt =", 12, "#2C7A7B", kalin=True, hiza="start")
s.yazi(tx + 26 + 4 * sg + 8, ty + sy * 2 + 31, "satır", 12, "#2C7A7B", kalin=True, hiza="start")
s.kaydet("vt-yapisi.svg")

# ---------------------------------------------------------------- 4) tasarım aşamaları
s = Sekil(400, 248, "Gereksinim belirlenmesi, kavramsal model, mantıksal model, fiziksel model")
renk = ["#C53030", "#6B46C1", "#2C9C8F", "#6E9E2D"]
adlar = [("Gereksinim", "belirlenmesi"), ("Kavramsal", "model"), ("Mantıksal", "model"), ("Fiziksel", "model")]
for i in range(4):
    x, y = 14 + i * 88, 14 + i * 58
    s.ekle('<rect x="%d" y="%d" width="112" height="46" rx="8" fill="%s"/>' % (x, y, renk[i]))
    s.yazi(x + 56, y + 20, adlar[i][0], 13, "#FFFFFF", kalin=True)
    s.yazi(x + 56, y + 37, adlar[i][1], 13, "#FFFFFF", kalin=True)
    if i < 3:
        s.ok(x + 40, y + 46, x + 40, y + 70, renk[i], 2)
        s.ok(x + 40, y + 70, x + 86, y + 70, renk[i], 2)
s.kaydet("tasarim-asamalari.svg")

# ---------------------------------------------------------------- 5) gereksinim belirleme
s = Sekil(400, 300, "Gereksinimlerin belirlenmesi: toplama ve analiz")
s.ekle('<rect x="110" y="12" width="180" height="46" rx="8" fill="#2C7A7B"/>')
s.yazi(200, 32, "Gereksinimlerin", 13, "#FFFFFF", kalin=True); s.yazi(200, 49, "belirlenmesi", 13, "#FFFFFF", kalin=True)
s.cizgi(200, 58, 200, 76, "#2C7A7B", 1.6); s.cizgi(100, 76, 300, 76, "#2C7A7B", 1.6)
s.ok(100, 76, 100, 94, "#2C7A7B", 1.6); s.ok(300, 76, 300, 94, "#2C7A7B", 1.6)
for x, b1, b2 in [(12, "1. Gereksinimlerin", "toplanması"), (212, "2. Gereksinim", "analizi")]:
    s.ekle('<rect x="%d" y="94" width="176" height="46" rx="8" fill="#E6F6F6" stroke="#2C7A7B" stroke-width="1.4"/>' % x)
    s.yazi(x + 88, 114, b1, 13, kalin=True); s.yazi(x + 88, 131, b2, 13, kalin=True)
sat = [("Geleneksel:", True), ("anketler", False), ("açık uçlu görüşmeler", False), ("doküman analizi", False), ("Grupsal:", True), ("beyin fırtınası", False), ("prototipleme", False)]
for k, (t, b) in enumerate(sat):
    s.yazi(22 if b else 32, 166 + k * 18, ("• " if not b else "") + t, 12, YAZI if b else SONUK, kalin=b, hiza="start")
sat2 = ["Gereksinimler", "özelliklerine göre", "gruplanır ve sistem", "tasarımına hazırlanır.", "", "Araç: Varlık Bağıntı", "(E-R) diyagramları"]
for k, t in enumerate(sat2):
    s.yazi(222, 166 + k * 18, t, 12, SONUK if k < 4 else YAZI, kalin=(k >= 5), hiza="start")
s.kaydet("gereksinim-belirleme.svg")

# ---------------------------------------------------------------- 6) nitelik türleri (kullanıcı)
s = Sekil(400, 376, "Kullanıcı varlığı ve nitelik türleri")
V = (150, 186, 100, 40)
cx, cy = V[0] + V[2] / 2, V[1] + V[3] / 2
attrs = [("kod", 95, 110, "anahtar"), ("şifre", 200, 70, "duz"), ("faks", 278, 86, "duz"), ("yaş", 338, 134, "turetilmis"),
         ("tel", 60, 168, "cok"), ("ePosta", 62, 232, "duz"), ("dTarihi", 345, 200, "duz"), ("adres", 345, 254, "duz"), ("açıklama", 300, 304, "duz")]
for ad, x, y, t in attrs:
    s.cizgi(cx, cy, x, y)
s.cizgi(cx, cy, 160, 292); s.cizgi(160, 292, 108, 346); s.cizgi(160, 292, 214, 346)
for ad, x, y, t in attrs:
    s.nitelik(x, y, ad, t)
s.nitelik(160, 292, "isim"); s.nitelik(108, 346, "soyAd"); s.nitelik(214, 346, "ad")
s.varlik(*V, "kullanıcı")
for t, x, y, h in [("anahtar (altı çizili)", 95, 88, "middle"), ("türetilmiş (kesikli)", 336, 112, "middle"),
                   ("çok değerli (çift)", 12, 146, "start"), ("çekirdek", 62, 262, "middle"), ("birleşik", 118, 296, "end")]:
    s.yazi(x, y, t, 11, VURGU, kalin=True, hiza=h)
s.kaydet("nitelik-turleri.svg")

# ---------------------------------------------------------------- 7) E-R gösterim özeti
s = Sekil(400, 470, "E-R diyagramında kullanılan şekiller")
satirlar = [
    ("Varlık", lambda y: s.varlik(30, y - 16, 110, 32, "öğrenci")),
    ("Zayıf varlık", lambda y: s.varlik(30, y - 16, 110, 32, "soruSeçenekleri", True, 12)),
    ("Nitelik (çekirdek)", lambda y: s.nitelik(85, y, "ePosta", rx=48)),
    ("Birincil anahtar", lambda y: s.nitelik(85, y, "kod", "anahtar", rx=48)),
    ("Türetilmiş nitelik", lambda y: s.nitelik(85, y, "yaş", "turetilmis", rx=48)),
    ("Birden çok değerli nitelik", lambda y: s.nitelik(85, y, "tel", "cok", rx=48)),
    ("Birleşik nitelik", None),
    ("Bağıntı", lambda y: s.bag(85, y, "soruTipi", g=110, y_=38)),
    ("Varolma bağıntısı", lambda y: s.bag(85, y, "seçenek", g=110, y_=38, cift=True)),
    ("Kümelenme", None),
]
for i, (ad, f) in enumerate(satirlar):
    y = 28 + i * 45
    if f: f(y)
    s.yazi(170, y + 5, ad, 13, hiza="start")
y = 28 + 6 * 45
s.cizgi(60, y - 4, 40, y + 12); s.cizgi(60, y - 4, 82, y + 12)
s.nitelik(60, y - 8, "isim", rx=26, ry=11, boy=11); s.nitelik(34, y + 15, "ad", rx=19, ry=10, boy=11); s.nitelik(92, y + 15, "soyAd", rx=30, ry=10, boy=11)
y = 28 + 9 * 45
s.bulut(85, y, 58, 19, n=10); s.bag(85, y, "öğrSınav", g=80, y_=26, boy=11)
s.kaydet("er-gosterim.svg")

# ---------------------------------------------------------------- yardımcı: yatay bağıntı satırı
def satir_bagintisi(s, y, sol, bag_ad, sag, sol_isaret, sag_isaret, gs=104, gb=118, cift=False, zayif_sag=False, x0=14, g=420):
    x1 = x0; x2 = g - x0 - gs
    bx = g / 2
    s.cizgi(x1 + gs, y, bx - gb / 2, y); s.cizgi(bx + gb / 2, y, x2, y)
    s.varlik(x1, y - 18, gs, 36, sol, boy=13)
    s.varlik(x2, y - 18, gs, 36, sag, zayif=zayif_sag, boy=13)
    s.bag(bx, y, bag_ad, g=gb, y_=42, cift=cift)
    s.isaret(x1 + gs, y, 1, 0, sol_isaret)
    s.isaret(x2, y, -1, 0, sag_isaret)

# ---------------------------------------------------------------- 8) eleman sayısı
s = Sekil(420, 372, "Birebir, bire çok ve çoğa çok bağıntı örnekleri")
ornekler = [
    ("1-1", "öğretmen", "ofisi", "ofis", "o|", "||", "Her öğretmenin bir ofisi var; bir ofis en çok bir öğretmenin."),
    ("1-N", "soruTipleri", "soruTipi", "sorular", "||", "o<", "Bir soru tipinde çok soru olabilir; her sorunun tek tipi var."),
    ("M-N", "sorular", "sınavSoruları", "sınavlar", "|<", "o<", "Bir sınavda çok soru, bir soru çok sınavda olabilir."),
]
for i, (t, a, b, c, i1, i2, ac) in enumerate(ornekler):
    y0 = 10 + i * 120
    kutu(s, 6, y0, 408, 110, "#FBFDFF", "#E2E8F0")
    s.yazi(18, y0 + 22, t, 14, VURGU, kalin=True, hiza="start")
    satir_bagintisi(s, y0 + 56, a, b, c, i1, i2)
    s.yazi(210, y0 + 98, ac, 12, SONUK)
s.kaydet("eleman-sayisi.svg")

# ---------------------------------------------------------------- 9) katılım
s = Sekil(420, 236, "Zorunlu ve kısmen katılım")
satir_bagintisi(s, 112, "sorular", "sınavSoruları", "sınavlar", "|<", "o<")
s.ok(70, 40, 132, 102, VURGU, 1.6)
s.yazi(14, 22, "Zorunlu katılım: düz çizgi", 13, VURGU, kalin=True, hiza="start")
s.yazi(14, 38, "her sınavda en az bir soru olmalı", 12, SONUK, hiza="start")
s.ok(352, 186, 286, 120, "#2C7A7B", 1.6)
s.yazi(406, 202, "Kısmen katılım: yuvarlak", 13, "#2C7A7B", kalin=True, hiza="end")
s.yazi(406, 218, "bir soru hiçbir sınavda olmayabilir", 12, SONUK, hiza="end")
s.kaydet("katilim.svg")

# ---------------------------------------------------------------- 10) işaretler
s = Sekil(400, 262, "Çizgi ucundaki işaretler ve anlamları")
tanim = [("||", "bir ve yalnız bir", "en az 1, en çok 1"), ("o|", "sıfır ya da bir", "en çok 1, zorunlu değil"),
         ("|<", "bir ya da çok", "en az 1, istenirse çok"), ("o<", "sıfır ya da çok", "hiç olmayabilir, çok olabilir")]
for i, (t, a, b) in enumerate(tanim):
    y = 34 + i * 60
    s.cizgi(20, y, 112, y)
    s.ekle('<rect x="112" y="%d" width="40" height="30" fill="%s" stroke="%s" stroke-width="1.6"/>' % (y - 15, VARLIK_D, CIZGI))
    s.isaret(112, y, -1, 0, t)
    s.yazi(170, y - 2, a, 14, kalin=True, hiza="start")
    s.yazi(170, y + 15, b, 12, SONUK, hiza="start")
s.yazi(20, 254, "yuvarlak: zorunlu değil (0) · düz çizgi: zorunlu (1) · kaz ayağı: çok", 11.5, VURGU, hiza="start")
s.kaydet("kardinalite-isaretleri.svg")

# ---------------------------------------------------------------- 11) varolma bağıntısı
s = Sekil(400, 336, "Varolma bağıntısı: sorular ve soruSeçenekleri")
ex, eg = 150, 120
s.cizgi(210, 66, 210, 140); s.cizgi(210, 188, 210, 254)
s.varlik(ex, 30, eg, 36, "sorular")
s.bag(210, 164, "seçenek", g=124, y_=48, cift=True)
for ad, x, y, t in [("kod", 70, 30, "anahtar"), ("sıra", 64, 66, "duz")]:
    s.cizgi(ex, 48, x, y); s.nitelik(x, y, ad, t)
s.isaret(210, 66, 0, 1, "||")
s.isaret(210, 254, 0, -1, "|<")
s.varlik(ex - 10, 254, eg + 20, 40, "soruSeçenekleri", zayif=True, boy=13)
for ad, x, y, t in [("kod", 70, 274, "anahtar"), ("puan", 340, 236, "duz"), ("metin", 340, 306, "duz")]:
    s.cizgi(ex + 65, 274, x, y); s.nitelik(x, y, ad, t)
s.varlik(ex - 10, 254, eg + 20, 40, "soruSeçenekleri", zayif=True, boy=13)
s.yazi(298, 154, "çift baklava:", 12, VURGU, kalin=True, hiza="start")
s.yazi(298, 170, "varolma bağıntısı", 12, VURGU, hiza="start")
s.yazi(20, 326, "çift dikdörtgen: zayıf varlık", 12, VURGU, kalin=True, hiza="start")
s.kaydet("varolma.svg")

# ---------------------------------------------------------------- 12) özyineli
s = Sekil(400, 210, "Özyineli bağıntı: öğretmen ve zümreBşk")
s.cizgi(140, 70, 280, 70); s.cizgi(280, 70, 280, 92)
s.cizgi(140, 120, 214, 120)
s.varlik(30, 56, 110, 78, "öğretmen")
s.bag(280, 120, "zümreBşk", g=132, y_=56)
s.isaret(140, 70, 1, 0, "o<")
s.isaret(140, 120, 1, 0, "||")
s.yazi(176, 60, "bir başkanın 0..N öğretmeni", 11, SONUK, hiza="start")
s.yazi(150, 140, "her öğretmenin", 11, SONUK, hiza="start")
s.yazi(150, 154, "1 zümre başkanı", 11, SONUK, hiza="start")
s.yazi(200, 196, "Tek varlık kendisiyle bağıntılı: derece 1 (1-li)", 12, VURGU, kalin=True)
s.kaydet("ozyineli.svg")

# ---------------------------------------------------------------- 13) üçüncü derece
s = Sekil(420, 326, "Üçüncü dereceden bağıntı: proje, sağlar, üretici, malzeme")
s.cizgi(108, 120, 162, 120); s.cizgi(258, 120, 312, 120); s.cizgi(210, 144, 210, 214)
s.varlik(14, 102, 94, 36, "proje")
s.varlik(312, 102, 94, 36, "üretici")
s.varlik(162, 214, 96, 36, "malzeme")
s.bag(210, 120, "sağlar", g=96, y_=48)
s.isaret(108, 120, 1, 0, "o<"); s.isaret(312, 120, -1, 0, "|<"); s.isaret(210, 214, 0, -1, "|<")
for ad, x, y, t, kx, ky in [("kod", 36, 54, "anahtar", 61, 102), ("açıklama", 128, 50, "duz", 61, 102), ("ad", 30, 178, "duz", 61, 138),
                             ("sicil", 306, 54, "anahtar", 359, 102), ("adres", 382, 54, "duz", 359, 102), ("ad", 370, 178, "duz", 359, 138), ("tel", 300, 178, "duz", 359, 138),
                             ("kod", 152, 296, "anahtar", 210, 250), ("ad", 92, 260, "duz", 162, 232), ("açıklama", 268, 296, "duz", 210, 250)]:
    s.cizgi(kx, ky, x, y)
    s.nitelik(x, y, ad, t)
s.varlik(14, 102, 94, 36, "proje"); s.varlik(312, 102, 94, 36, "üretici"); s.varlik(162, 214, 96, 36, "malzeme")
s.isaret(108, 120, 1, 0, "o<"); s.isaret(312, 120, -1, 0, "|<"); s.isaret(210, 214, 0, -1, "|<")
s.yazi(210, 20, "Hangi firma, hangi projedeki hangi malzemeyi sağladı?", 12, VURGU, kalin=True)
s.kaydet("ucuncu-derece.svg")

# ---------------------------------------------------------------- 14) kümelenme
s = Sekil(420, 404, "Kümelenme: öğrenciSınavları ve cevaplar")
s.cizgi(104, 112, 140, 112); s.cizgi(280, 112, 316, 112); s.cizgi(210, 130, 210, 237)
s.bulut(210, 112, 92, 44)
s.varlik(10, 94, 94, 36, "öğrenciler")
s.varlik(316, 94, 94, 36, "sınavlar")
s.bag(210, 112, "öğrenciSınavları", g=150, y_=46, boy=12)
s.yazi(210, 30, "kümelenme: öğrenciSınavları bağıntısı bulutun içinde", 12, VURGU, kalin=True)
s.yazi(222, 184, "öğrenciSınavları: süre, tarih,", 11, SONUK, hiza="start")
s.yazi(222, 198, "tdoğru, tyanlış, sonuç, açıklama", 11, SONUK, hiza="start")
s.cizgi(210, 283, 210, 330)
s.bag(210, 260, "cevaplar", g=112, y_=46)
s.yazi(282, 254, "cevaplar:", 11, SONUK, hiza="start"); s.yazi(282, 268, "değer, puan", 11, SONUK, hiza="start")
s.varlik(140, 330, 140, 40, "soruSeçenekleri", zayif=True, boy=13)
s.yazi(210, 394, "bulut, soruSeçenekleri ile birlikte cevaplar bağıntısına katılır", 11, SONUK)
s.kaydet("kumelenme.svg")

# ================================================================ Normalizasyon notu
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

def yay(s, x1, x2, y, d, renk, kal=1.6, kesik=False, yukari=False):
    """(x1,y)'den (x2,y)'ye dolaşan ok. Varsayılan: hücrelerin altından (y alt kenar),
    yukari=True: üstünden (y üst kenar). Ucu x2'de hücreye döner."""
    k = -1 if yukari else 1
    xm = (x1 + x2) / 2
    uy = y + 2 * k
    s.ekle('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="%s"%s/>' % (
        x1, y, xm, y + d * k, x2, uy, renk, kal, ' stroke-dasharray="5 4"' if kesik else ""))
    a = math.atan2(uy - (y + d * k), x2 - xm)
    p1 = (x2 - 8 * math.cos(a - 0.45), uy - 8 * math.sin(a - 0.45))
    p2 = (x2 - 8 * math.cos(a + 0.45), uy - 8 * math.sin(a + 0.45))
    s.ekle('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (x2, uy, p1[0], p1[1], p2[0], p2[1], renk))

def lejant(s, x, y, renk, metin, kesik=False):
    s.cizgi(x, y - 4, x + 22, y - 4, renk, 2, kesik)
    s.yazi(x + 28, y, metin, 11.5, SONUK, hiza="start")

# ---------------------------------------------------------------- 15) normal formlar iç içe
s = Sekil(400, 250, "3NF, 2NF'nin; 2NF de 1NF'nin içindedir")
for i, (ad, renk, dolgu) in enumerate([("1NF'ye uygun tablolar", "#2B6CB0", "#EBF4FF"), ("2NF'ye uygun tablolar", MOR, "#F3EEFF"), ("3NF'ye uygun tablolar", YESIL, "#E9F7EF")]):
    x, y = 14 + i * 30, 14 + i * 46
    s.ekle('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" stroke-width="1.8"/>' % (x, y, 372 - i * 60, 208 - i * 64, dolgu, renk))
    s.yazi(x + 14, y + 26, ad, 14, renk, kalin=True, hiza="start")
s.yazi(200, 244, "3NF'deki her tablo 2NF'ye ve 1NF'ye de uygundur.", 12, SONUK)
s.kaydet("normal-formlar.svg")

# ---------------------------------------------------------------- 16) normalizasyon adımları
s = Sekil(400, 336, "Ham tablodan 1NF, 2NF ve 3NF'ye")
adim = [("Ham tablo", "", "#718096"),
        ("1NF", "Tekrarlanan sütunlar ve tek alanda birden çok bilgi yeni tabloya", "#2B6CB0"),
        ("2NF", "Anahtarın yalnızca bir parçasına bağlı sütunlar ayrı tabloya", MOR),
        ("3NF", "Anahtar olmayan bir sütuna bağlı sütunlar ayrı tabloya", YESIL)]
for i, (ad, aciklama, renk) in enumerate(adim):
    y = 12 + i * 82
    s.ekle('<rect x="14" y="%d" width="74" height="54" rx="10" fill="%s"/>' % (y, renk))
    s.yazi(51, y + 33, ad, 15 if i else 12, "#FFFFFF", kalin=True)
    if aciklama:
        sozler, satir, satirlar_ = aciklama.split(), "", []
        for k in sozler:
            if len(satir + " " + k) > 36: satirlar_.append(satir); satir = k
            else: satir = (satir + " " + k).strip()
        satirlar_.append(satir)
        for j, t in enumerate(satirlar_):
            s.yazi(102, y + 22 + j * 17, t, 12.5, YAZI, hiza="start")
    if i < 3:
        s.ok(51, y + 56, 51, y + 80, adim[i + 1][2], 2)
s.kaydet("normalizasyon-adimlari.svg")

# ---------------------------------------------------------------- 17) 1NF telefonlar
s = Sekil(400, 404, "Telefonlar alanı ayrı bir tabloya taşınır")
s.yazi(14, 22, "Önce: telefonlar tek alanda", 13, KIRMIZI, kalin=True, hiza="start")
xs = hucre_satiri(s, 14, 32, ["Ogr_ID", "Adi", "Ders_Kodu", "Telefonlar"], [62, 70, 82, 158], isaretli={"Telefonlar": KIRMIZI})
for j, (a, b, d, c) in enumerate([("1", "Ali", "A115", "2159001, 2159002"), ("1", "Ali", "A116", "2159001, 2159002"),
                                  ("2", "Mehmet", "A116", "3101510"), ("2", "Mehmet", "A117", "3101510")]):
    y = 76 + j * 20
    s.yazi(xs[0], y, a, 12); s.yazi(xs[1], y, b, 12); s.yazi(xs[2], y, d, 12)
    s.yazi(xs[3], y, c, 12, KIRMIZI if j < 2 else YAZI, kalin=(j < 2))
s.yazi(14, 166, "(Soyadi, Adres, Dersin_Adi, Vize, Final sütunları gösterilmedi)", 11, SONUK, hiza="start")
s.ok(200, 174, 200, 198, SONUK, 2)
s.yazi(14, 218, "Sonra: her numara kendi satırında", 13, YESIL, kalin=True, hiza="start")
s.yazi(14, 242, "Ogrenci", 12, kalin=True, hiza="start")
xo = hucre_satiri(s, 14, 250, ["Ogr_ID", "Adi", "Ders_Kodu"], [62, 70, 82])
s.yazi(250, 242, "Telefonlar", 12, kalin=True, hiza="start")
xt = hucre_satiri(s, 250, 250, ["Ogr_ID", "Telefon_No"], [56, 92])
for j, (a, b, d) in enumerate([("1", "Ali", "A115"), ("1", "Ali", "A116"), ("2", "Mehmet", "A116"), ("2", "Mehmet", "A117")]):
    y = 294 + j * 20
    s.yazi(xo[0], y, a, 12); s.yazi(xo[1], y, b, 12); s.yazi(xo[2], y, d, 12)
for j, (a, b) in enumerate([("1", "2159001"), ("1", "2159002"), ("2", "3101510")]):
    y = 294 + j * 20
    s.yazi(xt[0], y, a, 12); s.yazi(xt[1], y, b, 12)
s.ekle('<path d="M %.1f 360 C %.1f 386, %.1f 386, %.1f 364" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>' % (xt[0], xt[0], xo[0], xo[0], TURUNCU))
s.ekle('<polygon points="%.1f,358 %.1f,367 %.1f,367" fill="%s"/>' % (xo[0], xo[0] - 4.5, xo[0] + 4.5, TURUNCU))
s.yazi(200, 396, "iki tablo Ogr_ID alanına göre ilişkilendirilir", 11, TURUNCU)
s.kaydet("1nf-telefonlar.svg")

# ---------------------------------------------------------------- 18) 2NF bağımlılık
s = Sekil(400, 310, "Ad ve Bolum anahtarın yalnızca bir parçasına bağlı")
s.yazi(14, 20, "OgrenciVeNot (anahtar: ogrNo + DersKodu)", 13, kalin=True, hiza="start")
x = hucre_satiri(s, 14, 84, ["ogrNo", "DersKodu", "Ad", "Bolum", "Not"], [72, 84, 70, 76, 70], anahtarlar=("ogrNo", "DersKodu"))
yay(s, x[0], x[2], 84, 34, KIRMIZI, yukari=True); yay(s, x[0], x[3], 84, 56, KIRMIZI, yukari=True)
s.ekle('<path d="M %.1f 112 L %.1f 120 L %.1f 120 L %.1f 112" fill="none" stroke="%s" stroke-width="1.6"/>' % (x[0], x[0], x[1], x[1], YESIL))
yay(s, (x[0] + x[1]) / 2, x[4], 120, 40, YESIL)
lejant(s, 20, 176, KIRMIZI, "yalnızca ogrNo'ya bağlı: 2NF'ye aykırı")
lejant(s, 20, 196, YESIL, "anahtarın iki sütununa birden bağlı: uygun")
s.ok(200, 206, 200, 228, SONUK, 2)
s.yazi(14, 248, "Ogrenci", 12, kalin=True, hiza="start")
hucre_satiri(s, 14, 256, ["ogrNo", "Ad", "Bolum"], [62, 62, 66], anahtarlar=("ogrNo",))
s.yazi(212, 248, "Not", 12, kalin=True, hiza="start")
hucre_satiri(s, 212, 256, ["ogrNo", "DersKodu", "Not"], [56, 74, 46], anahtarlar=("ogrNo", "DersKodu"))
s.kaydet("2nf-bagimlilik.svg")

# ---------------------------------------------------------------- 19) 3NF bağımlılık
s = Sekil(400, 290, "Birim Adı anahtara değil Birim sütununa bağlı")
s.yazi(14, 20, "Ürün (anahtar: ÜKodu)", 13, kalin=True, hiza="start")
x = hucre_satiri(s, 14, 70, ["ÜKodu", "Ad", "Birim", "Birim Adı"], [88, 88, 88, 108], anahtarlar=("ÜKodu",))
yay(s, x[0], x[1], 98, 30, YESIL); yay(s, x[0], x[2], 98, 52, YESIL)
yay(s, x[2], x[3], 70, 40, KIRMIZI, yukari=True)
lejant(s, 20, 168, YESIL, "anahtara bağlı: uygun")
lejant(s, 20, 188, KIRMIZI, "anahtar olmayan Birim'e bağlı: 3NF'ye aykırı")
s.ok(200, 198, 200, 220, SONUK, 2)
s.yazi(14, 238, "Ürün", 12, kalin=True, hiza="start")
hucre_satiri(s, 14, 246, ["ÜKodu", "Ad", "Birim"], [62, 56, 60], anahtarlar=("ÜKodu",))
s.yazi(232, 238, "Birim", 12, kalin=True, hiza="start")
hucre_satiri(s, 232, 246, ["Birim", "Birim Adı"], [60, 90], anahtarlar=("Birim",))
s.kaydet("3nf-bagimlilik.svg")

# ---------------------------------------------------------------- 20) örnek bağımlılık
s = Sekil(400, 374, "Örnek tablodaki bağımlılıklar")
s.yazi(14, 20, "Başlangıç (anahtar: musteri + Urun_id)", 13, kalin=True, hiza="start")
x = hucre_satiri(s, 14, 92, ["musteri", "Urun_id", "Sehir", "SehirKodu", "Miktar"], [72, 72, 70, 88, 70], anahtarlar=("musteri", "Urun_id"))
yay(s, x[0], x[2], 92, 34, KIRMIZI, yukari=True); yay(s, x[0], x[3], 92, 62, KIRMIZI, yukari=True)
s.ekle('<path d="M %.1f 120 L %.1f 128 L %.1f 128 L %.1f 120" fill="none" stroke="%s" stroke-width="1.6"/>' % (x[0], x[0], x[1], x[1], YESIL))
yay(s, (x[0] + x[1]) / 2, x[4], 128, 56, YESIL)
yay(s, x[3], x[2], 120, 24, TURUNCU, kesik=True)
lejant(s, 20, 196, KIRMIZI, "anahtarın bir parçasına bağlı: 2NF'ye aykırı")
lejant(s, 20, 216, TURUNCU, "anahtar olmayan sütuna bağlı: 3NF'ye aykırı", kesik=True)
lejant(s, 20, 236, YESIL, "anahtarın iki sütununa birden bağlı: uygun")
s.ok(200, 246, 200, 268, SONUK, 2)
s.yazi(14, 286, "3NF sonucu: üç tablo", 12, kalin=True, hiza="start")
hucre_satiri(s, 14, 296, ["musteri", "Urun_id", "Miktar"], [70, 70, 62], anahtarlar=("musteri", "Urun_id"))
hucre_satiri(s, 228, 296, ["musteri", "SehirKodu"], [70, 88], anahtarlar=("musteri",))
hucre_satiri(s, 14, 334, ["SehirKodu", "Sehir"], [88, 70], anahtarlar=("SehirKodu",))
s.kaydet("ornek-bagimlilik.svg")

# ---------------------------------------------------------------- 21) veri tipleri ağacı
s = Sekil(400, 380, "SQL veri tiplerinin gruplanışı")
def grup(x, y, g, baslik, alt, ogeler, renk):
    s.ekle('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % (x, y, g, 30 + len(ogeler) * 17 + (14 if alt else 0), renk))
    s.yazi(x + 10, y + 19, baslik, 12.5, renk, kalin=True, hiza="start")
    if alt: s.yazi(x + 10, y + 34, alt, 11, SONUK, hiza="start")
    for j, t in enumerate(ogeler):
        s.yazi(x + 14, y + (48 if alt else 36) + j * 17, t, 12, YAZI, hiza="start", font=MONO)
s.ekle('<rect x="120" y="8" width="160" height="30" rx="8" fill="#2D3748"/>'); s.yazi(200, 28, "SQL veri tipleri", 13, "#FFFFFF", kalin=True)
s.cizgi(200, 38, 200, 50, SONUK, 1.4); s.cizgi(100, 50, 300, 50, SONUK, 1.4); s.cizgi(100, 50, 100, 60, SONUK, 1.4); s.cizgi(300, 50, 300, 60, SONUK, 1.4)
s.yazi(100, 74, "Sayısal", 13, kalin=True); s.yazi(300, 74, "Metinsel", 13, kalin=True)
grup(8, 84, 186, "Tamsayı", "", ["bit", "tinyint", "smallint", "int", "bigint"], "#2B6CB0")
s.ekle('<rect x="8" y="208" width="186" height="164" rx="8" fill="#FAF5FF" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3"/>' % MOR)
s.yazi(18, 226, "Ondalıklı", 12.5, MOR, kalin=True, hiza="start")
grup(16, 236, 170, "Kesin ondalık", "", ["smallmoney", "money", "numeric = decimal"], MOR)
grup(16, 324, 170, "Kesirli", "", ["float, real"], TURUNCU)
grup(206, 84, 186, "ANSI", "1 karakter = 1 byte", ["char(n)", "varchar(n)", "text"], YESIL)
grup(206, 200, 186, "Unicode (N'li)", "1 karakter = 2 byte", ["nchar(n)", "nvarchar(n)", "nvarchar(MAX)", "ntext"], "#C53030")
s.kaydet("veri-tipleri.svg")

# ---------------------------------------------------------------- 22) char / varchar / nvarchar
s = Sekil(400, 262, "char(10), varchar(10) ve nvarchar(10) alanlarında “ali”")
def kutucuklar(y, etiket, dolu, toplam, renk, sonuc, harfler):
    s.yazi(14, y - 8, etiket, 13, kalin=True, hiza="start", font=MONO)
    for k in range(toplam):
        dolgu = renk if k < dolu else "#EDF2F7"
        s.ekle('<rect x="%d" y="%d" width="24" height="26" fill="%s" stroke="#FFFFFF" stroke-width="1.5"/>' % (14 + k * 25, y, dolgu))
        if k < len(harfler) and harfler[k]:
            s.yazi(26 + k * 25, y + 18, harfler[k], 13, "#FFFFFF", kalin=True, font=MONO)
    s.yazi(386, y + 18, sonuc, 13, renk if dolu else SONUK, kalin=True, hiza="end")
kutucuklar(36, "char(10)", 10, 10, "#2B6CB0", "10 byte", ["a", "l", "i", "", "", "", "", "", "", ""])
s.ekle('<rect x="89" y="36" width="174" height="26" fill="#90CDF4" opacity="0.55"/>')
s.yazi(176, 80, "kalan 7 byte da ayrılır: toplam 10 byte", 11, SONUK)
kutucuklar(118, "varchar(10)", 3, 3, YESIL, "3 byte", ["a", "l", "i"])
s.yazi(14, 164, "“mehmet” yazılırsa 6 byte", 11, SONUK, hiza="start")
kutucuklar(206, "nvarchar(10)", 6, 6, KIRMIZI, "6 byte", ["a", "", "l", "", "i", ""])
s.yazi(14, 252, "her karakter 2 byte (Unicode); “mehmet”: 12 byte", 11, SONUK, hiza="start")
s.kaydet("char-varchar.svg")

# ---------------------------------------------------------------- 23) bütünlük türleri
s = Sekil(400, 316, "Constraint işlemden önce, trigger işlemden sonra devreye girer")
kutular_ = [("Ekleme, güncelleme ya da", "silme isteği", "", "#4A5568", "#FFFFFF", 48),
            ("Constraint denetimi", "", "tanımsal · transaction'dan önce", "#2B6CB0", "#EBF4FF", 48),
            ("Transaction (işlem)", "", "", "#2D3748", "#EDF2F7", 48),
            ("Trigger, stored procedure,", "iş seviyesi uygulamalar", "programsal · transaction'dan sonra", MOR, "#F3EEFF", 64)]
y = 10
for i, (a, a2, b, renk, dolgu, yuk) in enumerate(kutular_):
    s.ekle('<rect x="14" y="%d" width="230" height="%d" rx="9" fill="%s" stroke="%s" stroke-width="1.6"/>' % (y, yuk, dolgu, renk))
    satirlar_ = [t for t in (a, a2) if t]
    ilk = y + (yuk - (len(satirlar_) * 16 + (15 if b else 0))) / 2 + 12
    for j, t in enumerate(satirlar_):
        s.yazi(129, ilk + j * 16, t, 12.5, renk, kalin=True)
    if b: s.yazi(129, ilk + len(satirlar_) * 16 + 1, b, 11, SONUK)
    if i < 3: s.ok(129, y + yuk, 129, y + yuk + 22, SONUK, 1.8)
    y += yuk + 24
s.yazi(256, 92, "etkin; ama dinamik", 11, "#2B6CB0", hiza="start"); s.yazi(256, 107, "değil, her sorunu", 11, "#2B6CB0", hiza="start"); s.yazi(256, 122, "çözemeyebilir", 11, "#2B6CB0", hiza="start")
for j, t in enumerate(["ya da bir sorgu daha", "kullanarak kontrol eder;", "her türlü kuralı", "denetler; çok kaynak", "tüketir"]):
    s.yazi(256, 234 + j * 15, t, 11, MOR, hiza="start")
s.kaydet("butunluk-turleri.svg")

# ---------------------------------------------------------------- 24) kısıtlayıcılar
s = Sekil(400, 324, "İki tablo üzerinde beş kısıtlayıcı")
def etiketli_tablo(x, y, ad, satirlar_, g=124):
    s.yazi(x, y - 8, ad, 13, kalin=True, hiza="start")
    for j, (alan, etiket, renk) in enumerate(satirlar_):
        yy = y + j * 30
        s.ekle('<rect x="%d" y="%d" width="%d" height="28" fill="#E2ECF7" stroke="#FFFFFF"/>' % (x, yy, g))
        s.yazi(x + 8, yy + 19, alan, 12, YAZI, hiza="start", font=MONO, alti=(etiket == "PRIMARY KEY"))
        if etiket:
            s.ekle('<rect x="%d" y="%d" width="%d" height="20" rx="10" fill="%s"/>' % (x + g + 8, yy + 4, len(etiket) * 7.2 + 18, renk))
            s.yazi(x + g + 17, yy + 18, etiket, 11, "#FFFFFF", kalin=True, hiza="start")
etiketli_tablo(44, 32, "Ogrenci", [("ogr_id", "PRIMARY KEY", "#2B6CB0"), ("tcKimlikNo", "UNIQUE", MOR), ("ad", "", ""), ("kayitTarihi", "DEFAULT bugün", YESIL)])
etiketli_tablo(44, 196, "OgrenciNot", [("ogr_id", "FOREIGN KEY", KIRMIZI), ("dersKodu", "", ""), ("notu", "CHECK 0–100", TURUNCU)])
s.ekle('<path d="M 44 210 C 10 210, 10 46, 36 46" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5 4"/>' % KIRMIZI)
s.ekle('<polygon points="44,46 35,41.5 35,50.5" fill="%s"/>' % KIRMIZI)
s.yazi(14, 312, "notu girilen ogr_id, Ogrenci tablosunda bulunmalı (foreign key)", 11, KIRMIZI, hiza="start")
s.kaydet("kisitlayicilar.svg")

# ================================================================ SQL notları
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

# ---------------------------------------------------------------- 25) SQL tarihçesi
s = Sekil(400, 176, "SQUARE, SEQUEL ve SQL")
for i, (ad, a1, a2, renk) in enumerate([("SQUARE", "matematiksel", "sözdizimi", "#718096"),
                                         ("SEQUEL", "İngilizceye benzer", "sözdizimi", "#2B6CB0"),
                                         ("SQL", "Structured", "Query Language", YESIL)]):
    x = 10 + i * 132
    s.ekle('<rect x="%d" y="20" width="116" height="104" rx="10" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % (x, renk))
    s.ekle('<rect x="%d" y="20" width="116" height="34" rx="10" fill="%s"/>' % (x, renk))
    s.ekle('<rect x="%d" y="44" width="116" height="10" fill="%s"/>' % (x, renk))
    s.yazi(x + 58, 43, ad, 15, "#FFFFFF", kalin=True)
    s.yazi(x + 58, 80, a1, 12, YAZI); s.yazi(x + 58, 97, a2, 12, YAZI)
    if i < 2: s.ok(x + 117, 72, x + 131, 72, SONUK, 1.8)
s.yazi(200, 150, "SEQUEL = Structured English Query Language", 11.5, SONUK)
s.yazi(200, 168, "SQL = Yapısal Sorgulama Dili", 11.5, SONUK)
s.kaydet("sql-tarihce.svg")

# ---------------------------------------------------------------- 26) SQL komut grupları
s = Sekil(400, 292, "DML, DDL ve DCL komutları")
gruplar_ = [("DML", "Veri İşleme Dili", "veriler üzerinde", ["SELECT", "INSERT", "UPDATE", "DELETE"], "#2B6CB0"),
            ("DDL", "Veri Tanımlama Dili", "tablo, indeks… yapısı", ["CREATE TABLE", "DROP TABLE", "ALTER TABLE", "CREATE INDEX", "DROP INDEX", "ALTER VIEW"], MOR),
            ("DCL", "Veri Kontrol Dili", "kullanıcı ve haklar", ["CREATE USER", "DROP USER", "ALTER USER", "GRANT", "REVOKE"], YESIL)]
for i, (kisa, uzun, ne, komutlar, renk) in enumerate(gruplar_):
    x = 8 + i * 130
    s.ekle('<rect x="%d" y="8" width="124" height="276" rx="10" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % (x, renk))
    s.ekle('<rect x="%d" y="8" width="124" height="66" rx="10" fill="%s"/>' % (x, renk))
    s.ekle('<rect x="%d" y="62" width="124" height="12" fill="%s"/>' % (x, renk))
    s.yazi(x + 62, 34, kisa, 17, "#FFFFFF", kalin=True)
    s.yazi(x + 62, 52, uzun, 11, "#FFFFFF")
    s.yazi(x + 62, 68, ne, 11, "#FFFFFF")
    for j, k in enumerate(komutlar):
        s.yazi(x + 12, 102 + j * 28, k, 12, YAZI, hiza="start", font=MONO)
s.kaydet("sql-komut-gruplari.svg")

# ---------------------------------------------------------------- 27) ORDER BY iki alan
s = Sekil(400, 300, "İki alana göre sıralama")
kod_satiri(14, 24, [("ORDER BY ", MOR, True), ("icerikno ", YAZI, False), ("DESC", KIRMIZI, True), (", ", YAZI, False), ("ogrno ", YAZI, False), ("ASC", YESIL, True)], 12.5)
xs = hucre_satiri(s, 14, 40, ["icerikno", "ogrno"], [90, 90])
satirlar_ = [("3", "9802"), ("2", "9801"), ("2", "9803"), ("1", "9801"), ("1", "9802"), ("1", "9804")]
gruplar_y = {"3": "#FFF5F5", "2": "#FFFAF0", "1": "#F0FFF4"}
for j, (a, b) in enumerate(satirlar_):
    y = 68 + j * 30
    s.ekle('<rect x="14" y="%d" width="180" height="28" fill="%s"/>' % (y, gruplar_y[a]))
    s.yazi(xs[0], y + 19, a, 13, kalin=True); s.yazi(xs[1], y + 19, b, 13)
for a, y1, y2 in (("3", 68, 96), ("2", 98, 156), ("1", 158, 246)):
    s.cizgi(204, y1 + 2, 204, y2 - 2, SONUK, 1.4); s.cizgi(198, y1 + 2, 204, y1 + 2, SONUK, 1.4); s.cizgi(198, y2 - 2, 204, y2 - 2, SONUK, 1.4)
s.yazi(214, 86, "icerikno 3", 11.5, SONUK, hiza="start")
s.yazi(214, 122, "icerikno 2: kendi", 11.5, SONUK, hiza="start"); s.yazi(214, 137, "içinde ogrno artan", 11.5, SONUK, hiza="start")
s.yazi(214, 197, "icerikno 1: kendi", 11.5, SONUK, hiza="start"); s.yazi(214, 212, "içinde ogrno artan", 11.5, SONUK, hiza="start")
s.yazi(14, 270, "1. önce icerikno büyükten küçüğe (DESC)", 12, KIRMIZI, hiza="start")
s.yazi(14, 290, "2. icerikno aynıysa ogrno küçükten büyüğe (ASC)", 12, YESIL, hiza="start")
s.kaydet("order-by.svg")

# ---------------------------------------------------------------- 28) AND / OR parantez
s = Sekil(400, 304, "Parantezin sonuca etkisi")
s.yazi(14, 20, "onemli_sayfalar", 13, kalin=True, hiza="start")
xs = hucre_satiri(s, 14, 74, ["ogrno", "icerikno"], [70, 74])
for x, renk, zemin, baslik_, satirlar_k in ((164, "#2B6CB0", "#EBF4FF", "parantezli", ["(ogrno=9801 OR", " ogrno=9802)", "AND icerikno=1"]),
                                            (282, KIRMIZI, "#FFF5F5", "parantezsiz", ["ogrno=9801 OR", "ogrno=9802", "AND icerikno=1"])):
    s.ekle('<rect x="%d" y="8" width="110" height="94" rx="6" fill="%s"/>' % (x, zemin))
    s.yazi(x + 55, 26, baslik_, 12, renk, kalin=True)
    for k, t in enumerate(satirlar_k):
        s.yazi(x + 8, 46 + k * 17, t, 11, renk, hiza="start", font=MONO)
veri_ = [("9801", "1", True, True), ("9802", "1", True, True), ("9802", "3", False, False), ("9803", "1", False, False), ("9801", "2", False, True)]
for j, (a, b, p1, p2) in enumerate(veri_):
    y = 128 + j * 30
    if p1 != p2: s.ekle('<rect x="10" y="%d" width="384" height="28" rx="6" fill="#FFFBEB"/>' % (y - 18))
    s.yazi(xs[0], y, a, 13); s.yazi(xs[1], y, b, 13)
    isaret_imi(219, y - 4, p1); isaret_imi(337, y - 4, p2)
s.yazi(219, 292, "2 kayıt", 12, "#2B6CB0", kalin=True); s.yazi(337, 292, "3 kayıt", 12, KIRMIZI, kalin=True)
s.kaydet("and-or-parantez.svg")

# ---------------------------------------------------------------- 29) SELECT sorgusunun parçaları
s = Sekil(400, 194, "SELECT sorgusunun parçaları")
parcalar_ = [([("SELECT ", "#2B6CB0", True), ("ogrno, tarih", YAZI, False)], "hangi alanlar?"),
             ([("FROM ", MOR, True), ("notlar", YAZI, False)], "hangi tablodan?"),
             ([("WHERE ", TURUNCU, True), ("ogrno=9801", YAZI, False)], "hangi kayıtlar? (koşul)"),
             ([("ORDER BY ", YESIL, True), ("tarih ", YAZI, False), ("DESC", YESIL, True), (";", YAZI, False)], "hangi sırayla?")]
for i, (kod, aciklama) in enumerate(parcalar_):
    y = 16 + i * 46
    s.ekle('<rect x="10" y="%d" width="228" height="36" rx="6" fill="#F7FAFC" stroke="#E2E8F0"/>' % y)
    kod_satiri(20, y + 23, kod, 12.5)
    s.ok(242, y + 18, 256, y + 18, SONUK, 1.4)
    s.yazi(262, y + 23, aciklama, 12, SONUK, hiza="start")
s.kaydet("sql-sorgu-parcalari.svg")

# ---------------------------------------------------------------- 30) LIKE jokeri
s = Sekil(400, 220, "LIKE ile başlayan ve biten")
for k, (desen, alan, aciklama, liste) in enumerate([("'S*'", "ad", "S ile başlayan", [("Sema (2 kayıt)", True), ("Serdar", True), ("Ayşe", False), ("Mehmet", False)]),
                                                    ("'*k'", "soyad", "k ile biten", [("Öztürk (2 kayıt)", True), ("Efe", False), ("Kubalı", False), ("Polat", False)])]):
    x = 10 + k * 196
    s.ekle('<rect x="%d" y="10" width="184" height="200" rx="10" fill="#FFFFFF" stroke="#CBD5E0" stroke-width="1.4"/>' % x)
    kod_satiri(x + 12, 36, [(alan + " LIKE ", "#2B6CB0", True), (desen, KIRMIZI, True)], 12.5)
    s.yazi(x + 12, 56, aciklama, 12, SONUK, hiza="start")
    for j, (ad, var) in enumerate(liste):
        y = 86 + j * 34
        isaret_imi(x + 24, y - 4, var)
        s.yazi(x + 42, y, ad, 13, YAZI if var else SONUK, kalin=var, hiza="start")
s.kaydet("like-joker.svg")

# ---------------------------------------------------------------- 31) iç içe SELECT
s = Sekil(400, 288, "İç sorgunun sonucunu dış sorgu kullanır")
s.yazi(14, 20, "arayuz_tercihleri", 12.5, kalin=True, hiza="start")
xs = hucre_satiri(s, 14, 28, ["ogrno", "arayuzno"], [64, 76])
for j, (a, b) in enumerate([("9801", "3"), ("9802", "3"), ("9803", "5")]):
    s.yazi(xs[0], 74 + j * 22, a, 12.5); s.yazi(xs[1], 74 + j * 22, b, 12.5, kalin=True)
s.ok(160, 92, 186, 92, SONUK, 1.8)
s.ekle('<rect x="190" y="28" width="200" height="90" rx="10" fill="#EBF4FF" stroke="#2B6CB0" stroke-width="1.6"/>')
s.yazi(200, 48, "1. iç sorgu (önce)", 12, "#2B6CB0", kalin=True, hiza="start")
s.yazi(200, 70, "SELECT DISTINCT", 11.5, YAZI, hiza="start", font=MONO); s.yazi(200, 87, "arayuzno ...", 11.5, YAZI, hiza="start", font=MONO)
s.yazi(200, 108, "sonuç: 3, 5", 12.5, "#2B6CB0", kalin=True, hiza="start")
s.ok(290, 120, 290, 148, SONUK, 1.8)
s.ekle('<rect x="190" y="152" width="200" height="90" rx="10" fill="#F0FFF4" stroke="%s" stroke-width="1.6"/>' % YESIL)
s.yazi(200, 172, "2. dış sorgu (sonra)", 12, YESIL, kalin=True, hiza="start")
s.yazi(200, 194, "SELECT COUNT(*)", 11.5, YAZI, hiza="start", font=MONO)
s.yazi(200, 211, "FROM (iç sorgu)", 11.5, YAZI, hiza="start", font=MONO)
s.yazi(200, 232, "COUNT(*) = 2", 12.5, YESIL, kalin=True, hiza="start", font=MONO)
s.yazi(14, 274, "3, 3 ve 5 seçildi → farklı arayüz sayısı 2", 12, VURGU, kalin=True, hiza="start")
s.kaydet("ic-ice-select.svg")

# ---------------------------------------------------------------- 32) BETWEEN
s = Sekil(400, 170, "BETWEEN aralığın iki ucunu da kapsar")
tarihler = ["27.02", "01.03", "02.03", "03.03", "04.03", "05.03"]
s.cizgi(20, 90, 384, 90, SONUK, 1.6)
s.ekle('<rect x="%d" y="72" width="%d" height="36" rx="18" fill="#F0FFF4" stroke="%s" stroke-width="1.6"/>' % (84, 2 * 62 + 44, YESIL))
for i, t in enumerate(tarihler):
    x = 44 + i * 62
    ic = 1 <= i <= 3
    s.ekle('<circle cx="%d" cy="90" r="7" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x, YESIL if ic else "#FFFFFF", YESIL if ic else "#A0AEC0"))
    s.yazi(x, 130, t, 12, YAZI if ic else SONUK, kalin=ic)
kod_satiri(14, 28, [("BETWEEN ", "#2B6CB0", True), ("#03/01/2009# ", YAZI, False), ("AND ", "#2B6CB0", True), ("#03/03/2009#", YAZI, False)], 12)
s.yazi(14, 52, "= tarih>=01.03.2009 AND tarih<=03.03.2009", 11.5, SONUK, hiza="start")
s.yazi(200, 160, "01.03 ve 03.03 de dahil: 3 kayıt", 12, YESIL, kalin=True)
s.kaydet("between.svg")

# ---------------------------------------------------------------- 33) INNER JOIN
s = Sekil(400, 300, "INNER JOIN yalnızca eşleşen kayıtları getirir")
s.yazi(14, 20, "tartisma_sorular", 12.5, kalin=True, hiza="start")
xa = hucre_satiri(s, 14, 28, ["id", "soru"], [34, 120])
s.yazi(234, 20, "tartisma_cevaplar", 12.5, kalin=True, hiza="start")
xb = hucre_satiri(s, 234, 28, ["soruno", "cevap"], [56, 100])
sorular_ = [("1", "SQL nedir?", True), ("2", "DISTINCT…?", True), ("3", "JOIN türleri?", False)]
cevaplar_ = [("1", "Yapısal…"), ("1", "Veritabanı…"), ("2", "Tekrarları…")]
for j, (i_, sr, var) in enumerate(sorular_):
    y = 74 + j * 30
    renk = YAZI if var else "#A0AEC0"
    s.yazi(xa[0], y, i_, 12.5, renk, kalin=var); s.yazi(xa[1], y, sr, 12, renk)
for j, (no, cv) in enumerate(cevaplar_):
    y = 74 + j * 30
    s.yazi(xb[0], y, no, 12.5, kalin=True); s.yazi(xb[1], y, cv, 12)
for (sj, cj) in ((0, 0), (0, 1), (1, 2)):
    s.cizgi(170, 70 + sj * 30, 232, 70 + cj * 30, YESIL, 1.6)
s.yazi(14, 178, "id 3 için eşleşen cevap yok: sonuca girmez", 11.5, "#A0AEC0", hiza="start")
s.yazi(14, 204, "Sonuç (ON tartisma_sorular.id = tartisma_cevaplar.soruno):", 11.5, YESIL, kalin=True, hiza="start")
for j, (sr, cv) in enumerate([("SQL nedir?", "Yapısal sorgulama dili"), ("SQL nedir?", "Veritabanı sorgu dili"), ("DISTINCT ne işe yarar?", "Tekrarları bir kez getirir")]):
    y = 226 + j * 22
    s.yazi(20, y, sr, 12, YAZI, hiza="start"); s.yazi(200, y, cv, 12, YAZI, hiza="start")
s.kaydet("inner-join.svg")

print("tamam: " + HEDEF)

"""Bilgisayar Ağları ders notlarının SVG şekillerini üretir.

Kullanım:
    python3 araclar/sekiller/aglar.py icerik/dersler/aglar/gorseller

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

# ---------------------------------------------------------------- 1) IPv4: 32 bit, dört oktet
s = Sekil(400, 204, "IPv4 adresi 32 bittir ve dört oktetten oluşur; her oktet ayrı ayrı ondalığa çevrilir")
OKTETLER = ["11000000", "10101000", "00000000", "00000001"]
ONDALIK = ["192", "168", "0", "1"]
X0, KG, KA = 12, 88, 8
s.cizgi(X0, 22, X0 + 4 * KG + 3 * KA, 22, SONUK, 1.3)
s.cizgi(X0, 17, X0, 27, SONUK, 1.3); s.cizgi(X0 + 4 * KG + 3 * KA, 17, X0 + 4 * KG + 3 * KA, 27, SONUK, 1.3)
s.yazi(200, 15, "32 bit", 12, SONUK, kalin=True)
for i in range(4):
    x = X0 + i * (KG + KA)
    s.yazi(x + KG / 2, 44, "%d. oktet" % (i + 1), 12, SONUK)
    s.ekle('<rect x="%d" y="52" width="%d" height="36" rx="6" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x, KG, VARLIK_D, CIZGI))
    s.yazi(x + KG / 2, 76, OKTETLER[i], 15, font=MONO, kalin=True)
    s.yazi(x + KG / 2, 106, "8 bit", 11.5, SONUK)
    s.ok(x + KG / 2, 112, x + KG / 2, 132, SONUK)
    s.ekle('<rect x="%d" y="138" width="%d" height="36" rx="6" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x, KG, BAG_D, BAG_C))
    s.yazi(x + KG / 2, 163, ONDALIK[i], 19, kalin=True)
    if i < 3:
        s.yazi(x + KG + KA / 2, 166, ".", 20, SONUK, kalin=True)
s.yazi(200, 196, "Noktalı ondalık gösterim: 192.168.0.1", 13, YAZI, kalin=True)
s.kaydet("ipv4-oktet.svg")

# ---------------------------------------------------------------- 2) Sınıflarda ağ ve host bölümleri
s = Sekil(400, 392, "A, B ve C sınıflarında ağ ve host bölümleri; D ve E özel amaçlıdır")
AG_D, AG_C = VARLIK_D, CIZGI
HOST_D, HOST_C = BAG_D, BAG_C
X0, CG, CA = 48, 82, 4
s.yazi(200, 16, "Dört oktet (32 bit)", 12, SONUK, kalin=True)
for i in range(4):
    s.yazi(X0 + i * (CG + CA) + CG / 2, 34, "%d. oktet" % (i + 1), 11.5, SONUK)
SATIRLAR = [("A", 1, "ağ 8 bit · host 24 bit (yaklaşık 16 milyon host)"),
            ("B", 2, "ağ 16 bit · host 16 bit (yaklaşık 65 bin host)"),
            ("C", 3, "ağ 24 bit · host 8 bit (254 host)")]
for r, (ad, ag, not_) in enumerate(SATIRLAR):
    y = 44 + r * 62
    s.yazi(24, y + 22, ad, 18, kalin=True)
    for i in range(4):
        x = X0 + i * (CG + CA)
        d, c, t = (AG_D, AG_C, "ağ") if i < ag else (HOST_D, HOST_C, "host")
        s.ekle('<rect x="%d" y="%d" width="%d" height="30" rx="5" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x, y, CG, d, c))
        s.yazi(x + CG / 2, y + 20, t, 13)
    s.yazi(X0, y + 46, not_, 11.5, SONUK, hiza="start")
for r, (ad, t, not_) in enumerate([("D", "çok noktaya yayın (multicast)", "özel amaç"), ("E", "deneysel ve Ar-Ge", "özel amaç")]):
    y = 44 + (3 + r) * 62
    s.yazi(24, y + 22, ad, 18, kalin=True)
    s.ekle('<rect x="%d" y="%d" width="%d" height="30" rx="5" fill="#EDF2F7" stroke="#A0AEC0" stroke-width="1.5"/>' % (X0, y, 4 * CG + 3 * CA))
    s.yazi(X0 + (4 * CG + 3 * CA) / 2, y + 20, t, 13)
    s.yazi(X0, y + 46, not_, 11.5, SONUK, hiza="start")
s.ekle('<rect x="48" y="368" width="14" height="14" rx="3" fill="%s" stroke="%s" stroke-width="1.4"/>' % (AG_D, AG_C))
s.yazi(68, 380, "ağ kısmı", 12, hiza="start")
s.ekle('<rect x="140" y="368" width="14" height="14" rx="3" fill="%s" stroke="%s" stroke-width="1.4"/>' % (HOST_D, HOST_C))
s.yazi(160, 380, "host kısmı", 12, hiza="start")
s.kaydet("sinif-bolunme.svg")

print("tamam: " + HEDEF)

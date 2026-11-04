"""Ekoloji Bilgisi ders notlarının SVG şekillerini üretir.

Kullanım:
    python3 araclar/sekiller/ekoloji.py icerik/dersler/ekoloji/gorseller

Şekiller elle değil bu dosyadan üretilir; bir şekli düzeltmek için burayı değiştirip
yeniden çalıştır. Üstteki renkler ve yardımcılar algoritma.py'den (o da veritabani.py'den)
aynen alındı; altındaki şekiller bu derse göre yazıldı. Şekiller hocanın slaytlarındaki
şema ve görsellerin sadeleştirilmiş hâlidir; adlar slayttaki gibidir.
Kurallar: icerik/ISLEME.md, "Görseller".
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
# Bu dersin renkleri: yeşil tonları canlı, mavi tonları cansız öğeler için
YESIL_D = "#E6F4EA"; YESIL_K = "#276749"; MAVI = "#2B6CB0"; MAVI_D = "#E3EEFA"
TURUNCU_D = "#FEEBD6"; GRI_D = "#F7FAFC"; GRI_C = "#CBD5E0"; MOR_D = "#EFE9FB"

def satirlar(s, x, y, liste, boy=12, renk=YAZI, kalin=False, hiza="middle", aralik=None):
    """Alt alta yazı satırları çizer; son satırın altındaki y'yi döndürür."""
    aralik = aralik or round(boy * 1.35)
    for i, t in enumerate(liste):
        s.yazi(x, y + i * aralik, t, boy, renk, kalin=kalin, hiza=hiza)
    return y + len(liste) * aralik

def yuvarlak_kutu(s, x, y, g, y_, dolgu, cizgi_, kal=1.6, rx=10):
    s.ekle('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="%s" stroke="%s" stroke-width="%s"/>' % (x, y, g, y_, rx, dolgu, cizgi_, kal))

def cift_ok(s, x1, y1, x2, y2, renk=SONUK, kal=1.6):
    s.ok(x1, y1, x2, y2, renk, kal); s.ok(x2, y2, x1, y1, renk, kal)

# ---------------------------------------------------------------- 1) organik dünya görüşü ve 17. asır
s = Sekil(360, 372, "1500 öncesi organik dünya görüşü ve 17. asırdan sonraki yang'cı düşünce")
yuvarlak_kutu(s, 10, 10, 340, 196, YESIL_D, YESIL_K)
s.yazi(180, 36, "1500'lü yıllardan önce", 13, SONUK)
s.yazi(180, 58, "Organik dünya görüşü", 16, YESIL_K, kalin=True)
s.yazi(180, 82, "fikirler «yin» paralelinde", 13, YAZI, kalin=True)
satirlar(s, 180, 108, ["Bilim, «Tanrı'nın yüce şanı için» ya da",
                       "«doğal düzenin yolunda gitmek» ve",
                       "«Tao'nun akışını izlemek» için yapılır."], 12)
s.cizgi(40, 156, 320, 156, "#9AE6B4", 1)
satirlar(s, 180, 176, ["Bilimin amacı: doğanın düzenini anlamak",
                       "ve uyum içinde yaşamak"], 12, YESIL_K, kalin=True)
s.ok(180, 212, 180, 246, SONUK, 2)
s.yazi(194, 234, "17. asırdan sonra", 12, SONUK, hiza="start")
yuvarlak_kutu(s, 10, 252, 340, 110, TURUNCU_D, VURGU)
s.yazi(180, 280, "17. asır paradigması", 16, VURGU, kalin=True)
s.yazi(180, 304, "düşünce «yang»cı oldu", 13, YAZI, kalin=True)
satirlar(s, 180, 328, ["Görselde: doğayı fethetmek ve kontrol etmek,",
                       "bilimin yeni amacı"], 12, SONUK)
s.kaydet("organik-mekanik.svg")

# ---------------------------------------------------------------- 2) kainatın bütünü
s = Sekil(360, 488, "Kainatın bütünü: sonsuz madde dolaşımı")
cx, cy, r = 180, 150, 104
s.ekle('<circle cx="%d" cy="%d" r="46" fill="%s" stroke="%s" stroke-width="1.6"/>' % (cx, cy, YESIL_D, YESIL_K))
s.yazi(cx, cy - 4, "Kainatın", 14, YESIL_K, kalin=True)
s.yazi(cx, cy + 14, "bütünü", 14, YESIL_K, kalin=True)
# öğeler tek halka üzerinde, yönsüz (slaytta dolaşımın sırası belirtilmez)
s.ekle('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="2"/>' % (cx, cy, r, MAVI))
dugum = [("Hava", -90), ("Canlı madde", 0), ("Mineraller", 90), ("Su", 180)]
for ad, aci in dugum:
    a = math.radians(aci)
    x, y = cx + r * math.cos(a), cy + r * math.sin(a)
    g = len(ad) * 7.6 + 22
    yuvarlak_kutu(s, x - g / 2, y - 14, g, 28, YESIL_D if ad == "Canlı madde" else MAVI_D, YESIL_K if ad == "Canlı madde" else MAVI, 1.4, 14)
    s.yazi(x, y + 5, ad, 13, YAZI, kalin=True)
s.yazi(cx, 286, "sonsuz madde dolaşımı (döngü)", 13, MAVI, kalin=True)
kutular = [("Canlı varlıkların uyumu", ["ortama uyum sağlama"], YESIL_D, YESIL_K),
           ("Etkileşim ağları", ["besin zinciri, enerji akışı; birbirleriyle", "ve çevreleriyle etkileşim"], MAVI_D, MAVI),
           ("Yaşam için mücadele", ["rekabet"], TURUNCU_D, VURGU)]
y = 302
for bas, ic, d, c in kutular:
    yk = 30 + 17 * len(ic)
    yuvarlak_kutu(s, 10, y, 340, yk, d, c, 1.4)
    s.yazi(22, y + 21, bas, 13, c, kalin=True, hiza="start")
    satirlar(s, 22, y + 39, ic, 12, YAZI, hiza="start", aralik=17)
    y += yk + 8
s.kaydet("kainat-butunu.svg")

# ---------------------------------------------------------------- 3) oikos ağacı
s = Sekil(360, 330, "Oikos kökünden ekoloji ve ekonomi")
yuvarlak_kutu(s, 70, 10, 220, 66, GRI_D, SONUK)
s.yazi(180, 34, "Oikos", 17, YAZI, kalin=True)
s.yazi(180, 56, "«ev, eve ait»: yaşanılan yer, çevre", 12, SONUK)
s.ok(140, 76, 92, 116, SONUK, 1.8)
s.ok(220, 76, 268, 116, SONUK, 1.8)
for x, bas, form, parca, anlam, d, c in (
        (10, "EKOLOJİ", "oikos + logos", "logos: «bilim, çalışma,", ["araştırma»"], YESIL_D, YESIL_K),
        (186, "EKONOMİ", "oikos + nomicus", "nomicus: yönetim", [], MAVI_D, MAVI)):
    yuvarlak_kutu(s, x, 120, 164, 126, d, c)
    s.yazi(x + 82, 146, bas, 15, c, kalin=True)
    s.yazi(x + 82, 168, form, 13, YAZI, kalin=True)
    satirlar(s, x + 82, 192, [parca] + anlam, 12, SONUK)
satirlar(s, 92, 226, ["yaşanılan yer + bilim"], 11, YESIL_K, kalin=True)
satirlar(s, 268, 216, ["yaşanılan yerin", "işlerinin yönetilmesi"], 11, MAVI, kalin=True, aralik=15)
yuvarlak_kutu(s, 10, 262, 340, 58, GRI_D, GRI_C, 1.2)
satirlar(s, 180, 286, ["Aynı dilsel köke sahip,", "birbirini destekleyen iki bilim dalı"], 12, YAZI, kalin=True)
s.kaydet("oikos-agaci.svg")

# ---------------------------------------------------------------- 4) zaman çizelgesi
s = Sekil(360, 500, "Ekoloji biliminin tarihsel gelişimi (slayttaki yıllar)")
olay = [("1807", "Von Humboldt", "Bitki Coğrafyası", YESIL_K),
        ("1840", "Liebig", "Bitki Gelişimini Sınırlayıcı Faktörler", YESIL_K),
        ("1849*", "E. Forbes", "Ege Denizi Hayvan Toplulukları", YESIL_K),
        ("1800'ler sonu", "Türlerin işlevi", "topluluk; her türün bir vazifesi", VURGU),
        ("1924", "Hesse", "temel kitap", MAVI),
        ("1927", "C. Elton", "temel kitap", MAVI),
        ("1935", "\"ekosistem\" terimi", "canlı topluluklar + cansız çevre", VURGU),
        ("1949", "Allee", "temel kitap", MAVI),
        ("1953", "Ekman", "temel kitap", MAVI)]
s.cizgi(108, 22, 108, 448, GRI_C, 2)
for i, (yil, kim, ne, renk) in enumerate(olay):
    y = 30 + i * 47
    s.ekle('<circle cx="108" cy="%d" r="6" fill="%s"/>' % (y, renk))
    s.yazi(96, y + 5, yil, 13 if len(yil) < 6 else 11, renk, kalin=True, hiza="end")
    s.yazi(122, y + 1, kim, 13, YAZI, kalin=True, hiza="start")
    s.yazi(122, y + 18, ne, 12, SONUK, hiza="start")
for k, (t, renk) in enumerate((("19. yy: ilk bilimsel çalışmalar", YESIL_K), ("20. yy: temel kitaplar", MAVI))):
    s.ekle('<rect x="%d" y="466" width="10" height="10" fill="%s"/>' % (10 + k * 190, renk))
    s.yazi(26 + k * 190, 475, t, 11, renk, hiza="start")
s.yazi(10, 494, "* Forbes'un raporu 1843'te sunulmuş, 1844'te basılmıştır.", 11, SONUK, hiza="start")
s.kaydet("ekoloji-zaman-cizelgesi.svg")

# ---------------------------------------------------------------- 5) biyotik ve abiyotik
s = Sekil(360, 250, "Ekolojik diyalektik matrisi: biyotik ilişkiler ve abiyotik çevre")
for x, bas, ic, d, c in ((4, "Biyotik ilişkiler", ["Tür içi yardımlaşma", "Türler arası rekabet", "Av-avcı dinamikleri", "Ortak yaşam (simbiyoz)"], YESIL_D, YESIL_K),
                         (192, "Abiyotik çevre", ["İklim ve sıcaklık", "Su ve nem rejimi", "Toprak mineralleri", "Güneş enerjisi akışı"], MAVI_D, MAVI)):
    yuvarlak_kutu(s, x, 10, 164, 176, d, c)
    s.yazi(x + 82, 38, bas, 14, c, kalin=True)
    for k, t in enumerate(ic):
        s.ekle('<circle cx="%d" cy="%d" r="2.5" fill="%s"/>' % (x + 10, 68 + k * 30, c))
        s.yazi(x + 17, 72 + k * 30, t, 12, YAZI, hiza="start")
cift_ok(s, 170, 98, 190, 98, SONUK, 1.6)
s.yazi(180, 214, "Canlı ve cansız alem", 13, YAZI, kalin=True)
s.yazi(180, 234, "birbirinden ayrılamaz bir bütündür.", 13, YAZI, kalin=True)
s.kaydet("biyotik-abiyotik.svg")

# ---------------------------------------------------------------- 6) ego ve eko
s = Sekil(360, 262, "EGO piramidi ve ECO dairesi")
s.yazi(90, 30, "EGO", 22, YAZI, kalin=True)
s.yazi(270, 30, "ECO", 22, YAZI, kalin=True)
# EGO: insan tepede, öbür canlılar piramidin katlarında
s.ekle('<polygon points="90,52 10,222 170,222" fill="%s" stroke="%s" stroke-width="1.4"/>' % (GRI_D, GRI_C))
katlar = [1, 2, 3, 4, 5]
for k, n in enumerate(katlar):
    y = 66 + k * 36
    for j in range(n):
        x = 90 + (j - (n - 1) / 2) * 28
        if k == 0:
            s.ekle('<circle cx="%.1f" cy="%d" r="9" fill="%s"/>' % (x, y, VURGU))
        else:
            s.ekle('<circle cx="%.1f" cy="%d" r="7" fill="%s"/>' % (x, y, YESIL_K))
s.yazi(110, 70, "insan", 12, VURGU, kalin=True, hiza="start")
# ECO: insan öbür canlıların arasında
s.ekle('<circle cx="270" cy="137" r="85" fill="%s" stroke="%s" stroke-width="1.4"/>' % (GRI_D, GRI_C))
noktalar = [(270, 72), (232, 92), (308, 92), (214, 128), (252, 122), (290, 122), (326, 128),
            (224, 166), (262, 160), (300, 166), (322, 176), (246, 196), (286, 200), (270, 140)]
for i, (x, y) in enumerate(noktalar):
    renk = VURGU if i == 8 else YESIL_K
    s.ekle('<circle cx="%d" cy="%d" r="%s" fill="%s"/>' % (x, y, 9 if i == 8 else 7, renk))
s.yazi(262, 184, "insan", 12, VURGU, kalin=True)
s.ekle('<circle cx="20" cy="246" r="7" fill="%s"/>' % YESIL_K)
s.yazi(32, 250, "öbür canlılar", 12, SONUK, hiza="start")
s.ekle('<circle cx="160" cy="246" r="8" fill="%s"/>' % VURGU)
s.yazi(173, 250, "insan", 12, SONUK, hiza="start")
s.kaydet("ego-eko.svg")

# ---------------------------------------------------------------- 7) on temel ilke
s = Sekil(360, 476, "Ekolojinin on temel ilkesi")
ilkeler = [("a", ["Doğanın bütünlüğü"]), ("b", ["Doğanın sınırlılığı"]), ("c", ["Doğanın özdenetim"]),
           ("d", ["Doğanın çeşitliliği"]), ("e", ["Doğada hiçbir şey yok olmaz"]),
           ("f", ["Doğaya karşı elde edilen her başarının", "bir bedeli vardır"]),
           ("g", ["Doğanın geri tepmesi"]), ("h", ["En uygun çözümü doğa bulmuştur"]),
           ("i", ["Kültürel evrim ve geleneksel", "ekolojiye saygı"]), ("j", ["Doğa ile birlikte gitmek"])]
y = 8
for harf, ad in ilkeler:
    yk = 28 + 17 * (len(ad) - 1) + 6
    yuvarlak_kutu(s, 8, y, 344, yk, MOR_D if harf in "ef" else YESIL_D, GRI_C, 1, 8)
    s.ekle('<circle cx="28" cy="%.1f" r="11" fill="%s"/>' % (y + yk / 2, "#6B46C1" if harf in "ef" else YESIL_K))
    s.yazi(28, y + yk / 2 + 4.5, harf, 13, "#FFFFFF", kalin=True)
    satirlar(s, 48, y + yk / 2 + 4.5 - 8.5 * (len(ad) - 1), [a + (" ilkesi" if i == len(ad) - 1 else "") for i, a in enumerate(ad)], 13, YAZI, hiza="start", aralik=17)
    y += yk + 6
s.yazi(180, y + 12, "e ve f: termodinamik yasalarına dayanan ilkeler", 11, "#6B46C1")
s.kaydet("ekoloji-ilkeleri.svg")

# ---------------------------------------------------------------- 8) hiçbir şey yok olmaz: madde döngüsü
s = Sekil(360, 400, "Doğada hiçbir şey yok olmaz: madde ve enerjinin dönüşümü")
yuvarlak_kutu(s, 110, 8, 140, 34, "#FFF8DB", "#B7791F", 1.4, 17)
s.yazi(180, 30, "Güneş enerjisi", 13, "#975A16", kalin=True)
dugumler = [(10, 76, [("Fotosentez", True), ("bitki büyümesi", False)], YESIL_D, YESIL_K),
            (196, 76, [("Besin zinciri", True), ("(enerji transferi)", False)], YESIL_D, YESIL_K),
            (196, 206, [("Ayrıştırıcılar", True)], TURUNCU_D, VURGU),
            (10, 206, [("Besin maddeleri", True), ("toprağa geri dönüş", False), ("Karbondioksit", True), ("havaya geri dönüş", False)], MAVI_D, MAVI)]
for x, y, sat, d, c in dugumler:
    yuvarlak_kutu(s, x, y, 154, 86, d, c)
    ust = y + 43 - 8 * (len(sat) - 1) + 5
    for i, (t_, kal) in enumerate(sat):
        s.yazi(x + 77, ust + i * 16 + (2 if i and kal else 0), t_, 14 if kal and len(sat) < 4 else 12, c if kal else YAZI, kalin=kal)
s.ok(160, 42, 110, 74, "#B7791F", 2)
s.ok(166, 119, 194, 119, SONUK, 2)
s.ok(273, 164, 273, 204, SONUK, 2)
s.ok(194, 249, 166, 249, SONUK, 2)
s.cizgi(87, 204, 87, 168, SONUK, 2, kesik=True)
s.ekle('<polygon points="87,164 82.5,172 91.5,172" fill="%s"/>' % SONUK)
s.yazi(96, 190, "(Ek)", 11, SONUK, hiza="start")
s.yazi(180, 312, "Su döngüsü · Jeolojik döngü", 13, MAVI, kalin=True)
yuvarlak_kutu(s, 10, 328, 340, 62, GRI_D, GRI_C, 1.2)
satirlar(s, 180, 352, ["Madde ve enerji bir şekilden başka bir şekle", "dönüşür, fakat hiçbir yolla yok olmaz."], 12, YAZI, kalin=True)
s.kaydet("madde-dongusu.svg")

# ---------------------------------------------------------------- 9) enerji dönüşümü (ikinci yasa)
s = Sekil(360, 330, "Her enerji dönüşümünde enerjinin bir kısmı dağınık bir şekle girer")
s.yazi(180, 24, "İkinci termodinamik yasası", 14, "#6B46C1", kalin=True)
yuvarlak_kutu(s, 110, 40, 140, 40, "#FFF8DB", "#B7791F", 1.4)
s.yazi(180, 65, "Girdi enerjisi", 13, "#975A16", kalin=True)
s.ok(180, 80, 180, 110, SONUK, 2)
yuvarlak_kutu(s, 120, 112, 120, 40, MOR_D, "#6B46C1", 1.4)
s.yazi(180, 137, "Dönüşüm", 13, "#6B46C1", kalin=True)
s.ok(150, 152, 92, 194, SONUK, 2)
s.ok(210, 152, 268, 194, SONUK, 2)
yuvarlak_kutu(s, 10, 196, 160, 68, YESIL_D, YESIL_K)
satirlar(s, 90, 224, ["Faydalı iş / düzen"], 13, YESIL_K, kalin=True)
yuvarlak_kutu(s, 190, 196, 160, 68, TURUNCU_D, VURGU)
satirlar(s, 270, 218, ["Dağılan ve", "kullanılamayan ısı", "(entropi artışı)"], 12, VURGU, kalin=True, aralik=15)
satirlar(s, 180, 292, ["Enerjinin bir kısmı iş yapamayacak", "kadar dağınık bir şekle girer."], 12, YAZI, kalin=True)
s.kaydet("enerji-donusumu.svg")

print("tamam: " + HEDEF)

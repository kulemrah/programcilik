"""Temel Elektrik ve Elektronik ders notlarının SVG şekillerini üretir.

Kullanım:
    python3 araclar/sekiller/elektrik.py icerik/dersler/elektrik/gorseller

Şekiller elle değil bu dosyadan üretilir; bir şekli düzeltmek için burayı değiştirip
yeniden çalıştır. Üstteki renkler ve yardımcılar ekoloji.py'den (o da veritabani.py'den)
aynen alındı; altındaki şekiller bu derse göre yazıldı. Şekiller hocanın slaytlarındaki
şekillerin sadeleştirilmiş hâlidir; adlar ve işaretler slayttaki gibidir.
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


# ================================================================ ORTAK DEVRE SEMBOLLERİ (01-devre.py)
# Birden çok parçanın kullandığı devre sembolleri. İlk P04 yazdı; sonraki parçalar yalnızca EKLER,
# var olan işlevin imzasını ve davranışını değiştirmez.
#
# Ortak kurallar:
#   - İki uçlu her sembol (direnç, pil, lamba, anahtar, sigorta, ölçü aleti) iki uç noktası arasına
#     çizilir: devre_X(s, x1, y1, x2, y2, ...). Uçlar yatay, dikey ya da eğik olabilir. Sembolün
#     gövdesi iki ucun ortasına konur; gövdeyle uçlar arasındaki tel kendiliğinden çizilir.
#     Böylece bir devre, köşe noktaları devre_tel ile, elemanlar uç noktalarıyla çizilir.
#   - Her sembol gövdesinin ortasını (cx, cy) döndürür; etiket (R₁, U, A ...) gerekirse
#     devre_etiket ile ya da s.yazi ile bu noktaya göre yazılır.
#   - "yan" (+1 / -1): eksene dik yön. Eksen u = (x2 - x1, y2 - y1) / boy, dik n = (-uy, ux).
#     Soldan sağa yatay elemanda yan=+1 altı, yan=-1 üstü; yukarıdan aşağı dikey elemanda
#     yan=+1 solu, yan=-1 sağı gösterir.
#   - Çizgi rengi DEVRE_C, kalınlık DEVRE_KAL; yazılar 11 px'ten küçük olmaz (ISLEME.md).
#   - Semboller hocanın slaytlarındaki gibidir: direnç dikdörtgen (slayt 68, 74) ya da zikzak
#     (slayt 99 ve sonrası); pil uzun (+) ve kısa kalın (−) levha (tek hücre: devre_pil, slayt 99;
#     çok hücreli üreteç: devre_batarya, slayt 68 ve 74); lamba daire içinde çarpı.

DEVRE_C = "#1A202C"; DEVRE_KAL = 1.8

def _devre_eksen(x1, y1, x2, y2):
    """Uç noktalardan eksen bilgisi: (boy, p, u, n). p(a, b): ortadan eksen boyunca a,
    dik yönde b kadar ötedeki nokta."""
    boy = math.hypot(x2 - x1, y2 - y1) or 1.0
    ux, uy = (x2 - x1) / boy, (y2 - y1) / boy
    nx, ny = -uy, ux
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    def p(a, b=0.0):
        return (mx + ux * a + nx * b, my + uy * a + ny * b)
    return boy, p, (ux, uy), (nx, ny)

def _devre_cokgen(s, noktalar, dolgu="none", renk=DEVRE_C, kal=DEVRE_KAL):
    s.ekle('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in noktalar), dolgu, renk, kal))

def _devre_uclar(s, x1, y1, x2, y2, govde, renk=DEVRE_C, kal=DEVRE_KAL):
    """Uç noktalardan gövdenin iki kenarına kadar teli çizer (govde: gövdenin eksen boyunca uzunluğu)."""
    boy, p, _, _ = _devre_eksen(x1, y1, x2, y2)
    a, b = p(-govde / 2), p(govde / 2)
    s.cizgi(x1, y1, a[0], a[1], renk, kal)
    s.cizgi(b[0], b[1], x2, y2, renk, kal)

def devre_tel(s, *noktalar, renk=DEVRE_C, kal=DEVRE_KAL):
    """Noktaları sırayla birleştiren tel: devre_tel(s, (x1, y1), (x2, y2), (x3, y3) ...)."""
    s.ekle('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round" stroke-linecap="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in noktalar), renk, kal))

def devre_dugum(s, x, y, r=3.2, renk=DEVRE_C):
    """Tellerin birleştiği düğüm noktası (dolu küçük daire)."""
    s.ekle('<circle cx="%.1f" cy="%.1f" r="%s" fill="%s"/>' % (x, y, r, renk))

def devre_etiket(s, x1, y1, x2, y2, metin, yan=-1, uzaklik=16, boy=12, renk=YAZI, kalin=False):
    """Elemanın ortasından eksene dik yönde 'uzaklik' kadar öteye etiket yazar (yazı döndürülmez)."""
    _, p, _, (nx, ny) = _devre_eksen(x1, y1, x2, y2)
    x, y = p(0, uzaklik * yan)
    hiza = "middle"
    if abs(nx * yan) > 0.7:            # etiket elemanın sağında ya da solunda
        hiza = "start" if nx * yan > 0 else "end"
    s.yazi(x, y + boy * 0.36, metin, boy, renk, kalin=kalin, hiza=hiza)

def devre_direnc(s, x1, y1, x2, y2, bicim="kutu", govde=36, en=12, renk=DEVRE_C, dolgu="#FFFFFF"):
    """Direnç. bicim="kutu": dikdörtgen (slayt 68'deki alıcı gibi); bicim="zikzak": zikzak çizgi."""
    _, p, _, _ = _devre_eksen(x1, y1, x2, y2)
    _devre_uclar(s, x1, y1, x2, y2, govde, renk)
    if bicim == "zikzak":
        n = 6; adim = govde / n
        nok = [p(-govde / 2)] + [p(-govde / 2 + adim * (i + 0.5), (en / 2) * (1 if i % 2 == 0 else -1)) for i in range(n)] + [p(govde / 2)]
        s.ekle('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
            " ".join("%.1f,%.1f" % q for q in nok), renk, DEVRE_KAL))
    else:
        _devre_cokgen(s, [p(-govde / 2, -en / 2), p(govde / 2, -en / 2), p(govde / 2, en / 2), p(-govde / 2, en / 2)], dolgu, renk)
    return p(0)

def devre_pil(s, x1, y1, x2, y2, arti=1, isaret=True, yan=1, uzun=26, kisa=13, ara=7, renk=DEVRE_C):
    """Pil (üreteç): uzun ince levha (+) ve kısa kalın levha (−).
    arti=1: (+) levha (x1, y1) ucuna yakın; arti=-1: (x2, y2) ucuna yakın.
    isaret=True ise levhaların yanına "+" ve "−" yazılır (yan: hangi tarafa)."""
    _, p, _, _ = _devre_eksen(x1, y1, x2, y2)
    _devre_uclar(s, x1, y1, x2, y2, ara, renk)
    ua, ea = -ara / 2 * arti, ara / 2 * arti     # (+) ve (−) levhaların eksendeki yeri
    a1, a2 = p(ua, -uzun / 2), p(ua, uzun / 2)
    b1, b2 = p(ea, -kisa / 2), p(ea, kisa / 2)
    s.cizgi(a1[0], a1[1], a2[0], a2[1], renk, 1.8)
    s.cizgi(b1[0], b1[1], b2[0], b2[1], renk, 4)
    if isaret:
        for a, t in ((ua * 2.6, "+"), (ea * 2.6, "−")):
            x, y = p(a, (uzun / 2 + 7) * yan)
            s.yazi(x, y + 5, t, 14, renk, kalin=True)
    return p(0)

def devre_lamba(s, x1, y1, x2, y2, r=12, renk=DEVRE_C, dolgu="#FFFFFF"):
    """Lamba (ampul): daire içinde çarpı."""
    _, p, _, _ = _devre_eksen(x1, y1, x2, y2)
    _devre_uclar(s, x1, y1, x2, y2, 2 * r, renk)
    cx, cy = p(0)
    s.ekle('<circle cx="%.1f" cy="%.1f" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (cx, cy, r, dolgu, renk, DEVRE_KAL))
    k = r * 0.707
    s.cizgi(cx - k, cy - k, cx + k, cy + k, renk, 1.6)
    s.cizgi(cx - k, cy + k, cx + k, cy - k, renk, 1.6)
    return (cx, cy)

def devre_anahtar(s, x1, y1, x2, y2, kapali=False, govde=30, yan=-1, renk=DEVRE_C):
    """Anahtar: iki kontak (küçük daire) ve dil. kapali=False: dil (x1, y1) yanındaki kontaktan
    eğik yukarı kalkar (açık devre); kapali=True: dil iki kontağı birleştirir. yan: dilin kalktığı taraf."""
    _, p, _, _ = _devre_eksen(x1, y1, x2, y2)
    _devre_uclar(s, x1, y1, x2, y2, govde, renk)
    k1, k2 = p(-govde / 2), p(govde / 2)
    uc = k2 if kapali else p(govde / 2, 13 * yan)
    s.cizgi(k1[0], k1[1], uc[0], uc[1], renk, DEVRE_KAL)
    for k in (k1, k2):
        s.ekle('<circle cx="%.1f" cy="%.1f" r="3" fill="#FFFFFF" stroke="%s" stroke-width="1.5"/>' % (k[0], k[1], renk))
    return p(0)

def devre_sigorta(s, x1, y1, x2, y2, govde=30, en=10, renk=DEVRE_C):
    """Sigorta: dikdörtgen ve içinden geçen tel."""
    _, p, _, _ = _devre_eksen(x1, y1, x2, y2)
    _devre_uclar(s, x1, y1, x2, y2, govde, renk)
    _devre_cokgen(s, [p(-govde / 2, -en / 2), p(govde / 2, -en / 2), p(govde / 2, en / 2), p(-govde / 2, en / 2)], "#FFFFFF", renk)
    a, b = p(-govde / 2), p(govde / 2)
    s.cizgi(a[0], a[1], b[0], b[1], renk, 1.2)
    return p(0)

def devre_olcu(s, x1, y1, x2, y2, harf="A", r=12, renk=DEVRE_C):
    """Ölçü aleti: daire içinde harf (A ampermetre, V voltmetre, Ω ohmmetre)."""
    _, p, _, _ = _devre_eksen(x1, y1, x2, y2)
    _devre_uclar(s, x1, y1, x2, y2, 2 * r, renk)
    cx, cy = p(0)
    s.ekle('<circle cx="%.1f" cy="%.1f" r="%s" fill="#FFFFFF" stroke="%s" stroke-width="%s"/>' % (cx, cy, r, renk, DEVRE_KAL))
    s.yazi(cx, cy + 5, harf, 14, renk, kalin=True)
    return (cx, cy)

def devre_yon_oku(s, x, y, dx, dy, renk=VURGU, boyut=8):
    """Tel üstünde akım yönünü gösteren dolu üçgen; (x, y) ucun yeri, (dx, dy) yön (birim olması gerekmez)."""
    l = math.hypot(dx, dy) or 1.0
    ux, uy = dx / l, dy / l
    nx, ny = -uy, ux
    a = (x - ux * boyut + nx * boyut * 0.55, y - uy * boyut + ny * boyut * 0.55)
    b = (x - ux * boyut - nx * boyut * 0.55, y - uy * boyut - ny * boyut * 0.55)
    s.ekle('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (x, y, a[0], a[1], b[0], b[1], renk))

# ---------------------------------------------------------------- P05 eklemesi
def devre_batarya(s, x1, y1, x2, y2, hucre=3, arti=1, isaret=True, yan=1, uzun=22, kisa=11, ara=6, renk=DEVRE_C):
    """Birden çok hücreli üreteç (batarya): sırayla uzun ince (+) ve kısa kalın (−) levha çiftleri
    (hocanın slayt 68 ve 74'teki üreteç sembolü üç hücrelidir). arti=1: (+) uç (x1, y1) yanında;
    arti=-1: (x2, y2) yanında. isaret=True ise uçlara "+" ve "−" yazılır (yan: hangi tarafa)."""
    _, p, _, _ = _devre_eksen(x1, y1, x2, y2)
    govde = (2 * hucre - 1) * ara
    _devre_uclar(s, x1, y1, x2, y2, govde, renk)
    for i in range(2 * hucre):
        a = (-govde / 2 + i * ara) * arti
        if i % 2 == 0:
            q1, q2 = p(a, -uzun / 2), p(a, uzun / 2); kal = 1.8
        else:
            q1, q2 = p(a, -kisa / 2), p(a, kisa / 2); kal = 4
        s.cizgi(q1[0], q1[1], q2[0], q2[1], renk, kal)
    if isaret:
        for a, t in ((-(govde / 2 + 8) * arti, "+"), ((govde / 2 + 8) * arti, "−")):
            x, y = p(a, (uzun / 2 - 2) * yan)
            s.yazi(x, y + 5, t, 14, renk, kalin=True)
    return p(0)

# ---------------------------------------------------------------- P06 eklemesi
def devre_toprak(s, x, y, en=22, renk=DEVRE_C):
    """Toprak (şase) sembolü: (x, y) noktasındaki telin altına, genişliği azalan üç yatay çizgi
    (hocanın slayt 86–88'deki devre resimlerinde pilin (−) ucu ve lamba bu sembolle toprağa bağlıdır)."""
    for i, k in enumerate((1.0, 0.64, 0.3)):
        yy = y + i * 5
        s.cizgi(x - en / 2 * k, yy, x + en / 2 * k, yy, renk, DEVRE_KAL)

# ---------------------------------------------------------------- P07 eklemesi
def devre_ac_kaynak(s, x1, y1, x2, y2, r=13, renk=DEVRE_C, dolgu="#FFFFFF"):
    """Alternatif gerilim kaynağı: daire içinde bir tam sinüs dalgası (hocanın slayt 98'deki (AC)
    devresi). Daire iki uç noktasının ortasına konur; dalga, eleman eğik ya da dikey olsa da yatay çizilir."""
    _, p, _, _ = _devre_eksen(x1, y1, x2, y2)
    _devre_uclar(s, x1, y1, x2, y2, 2 * r, renk)
    cx, cy = p(0)
    s.ekle('<circle cx="%.1f" cy="%.1f" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (cx, cy, r, dolgu, renk, DEVRE_KAL))
    nok = [(cx - 0.62 * r + 1.24 * r * i / 24, cy - 0.38 * r * math.sin(2 * math.pi * i / 24)) for i in range(25)]
    s.ekle('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5"/>' % (" ".join("%.1f,%.1f" % q for q in nok), renk))
    return (cx, cy)

# ================================================================ P01 (slayt 1–22): tarihçe ve üretim kaynakları

# ---------------------------------------------------------------- P01-1) uretim-nukleer-santral
# Slayt 14'teki şema ("Termik Kaynaklar" slaytında duruyor, ama nükleer santral şeması).
# Adlar slayttaki gibi İngilizce bırakıldı; Türkçeleri notta Ek kutusunda.
s = Sekil(360, 310, "Nükleer santral şeması: koruma yapısı, reaktör kabı, kontrol çubukları, basınçlandırıcı, buhar üreteci, türbin, generatör, kondenser")
KIRMIZI_B = "#C53030"; BUHAR = "#63B3ED"; SU = "#2B6CB0"
# Koruma yapısı (kubbeli bina)
s.ekle('<path d="M 8 296 V 96 Q 8 52 93 52 Q 178 52 178 96 V 296 Z" fill="%s" stroke="%s" stroke-width="1.8"/>' % (GRI_D, SONUK))
s.yazi(93, 42, "Containment Structure", 12, kalin=True)
# Reaktör kabı ve kontrol çubukları
yuvarlak_kutu(s, 20, 150, 50, 110, "#FEFCBF", "#B7791F", rx=14)
for x in (30, 40, 50, 60):
    s.cizgi(x, 128, x, 222, SONUK, 2.2)
s.cizgi(26, 128, 64, 128, SONUK, 2.2)
s.yazi(42, 120, "Control Rods", 11)
s.yazi(45, 276, "Reactor", 11); s.yazi(45, 289, "Vessel", 11)
# Birinci devre (kırmızı) ve pompa; pompalar slayttaki gibi yönsüz çizildi
s.cizgi(70, 172, 120, 172, KIRMIZI_B, 4)
s.cizgi(70, 240, 120, 240, KIRMIZI_B, 4)
s.ekle('<circle cx="95" cy="240" r="9" fill="#FFFFFF" stroke="%s" stroke-width="2"/>' % KIRMIZI_B)
s.cizgi(89, 234, 101, 246, KIRMIZI_B, 1.6)
# Basınçlandırıcı
s.ekle('<rect x="81" y="104" width="16" height="40" rx="8" fill="#F6AD55" stroke="#C05621" stroke-width="1.5"/>')
s.cizgi(89, 144, 89, 172, KIRMIZI_B, 2.5)
s.yazi(89, 96, "Pressurizer", 11)
# Buhar üreteci
yuvarlak_kutu(s, 120, 112, 36, 140, MAVI_D, SU, rx=12)
s.yazi(138, 270, "Steam", 11); s.yazi(138, 283, "Generator", 11)
# Buhar hattı: buhar üreteci → türbin
s.ekle('<polyline points="138,112 138,74 192,74 192,110 204,110" fill="none" stroke="%s" stroke-width="4"/>' % BUHAR)
# Türbin, mil, generatör
s.ekle('<polygon points="204,100 252,88 252,132 204,120" fill="#E2E8F0" stroke="%s" stroke-width="1.6"/>' % SONUK)
s.yazi(228, 80, "Turbine", 11)
s.cizgi(252, 110, 280, 110, SONUK, 3)
yuvarlak_kutu(s, 280, 98, 62, 24, "#EDE4D3", "#8B6B3D", rx=4)
s.yazi(311, 140, "Generator", 11)
# Generatörden iletim direğine hat
s.cizgi(328, 22, 316, 70, SONUK, 1.4); s.cizgi(328, 22, 340, 70, SONUK, 1.4)
s.cizgi(318, 34, 338, 34, SONUK, 1.4); s.cizgi(321, 48, 335, 48, SONUK, 1.4)
s.ekle('<path d="M 342 106 Q 352 70 338 34" fill="none" stroke="%s" stroke-width="1.2"/>' % SONUK)
# Türbinden kondensere, kondenserden pompa ile buhar üretecine
s.cizgi(238, 132, 238, 196, BUHAR, 4)
yuvarlak_kutu(s, 204, 196, 62, 50, "#BEE3F8", SU, rx=6)
s.yazi(235, 262, "Condenser", 11)
s.cizgi(204, 232, 156, 232, SU, 4)
s.ekle('<circle cx="190" cy="232" r="8" fill="#FFFFFF" stroke="%s" stroke-width="2"/>' % SU)
s.cizgi(184, 226, 196, 238, SU, 1.6)
# Kondenserin soğutma suyu (kesik çizgiler) ve pompası
s.cizgi(266, 212, 352, 212, SU, 3, kesik=True)
s.cizgi(266, 230, 352, 230, SU, 3, kesik=True)
s.ekle('<circle cx="312" cy="212" r="8" fill="#FFFFFF" stroke="%s" stroke-width="2"/>' % SU)
s.kaydet("uretim-nukleer-santral.svg")

# ---------------------------------------------------------------- P01-2) uretim-jeotermal-santral
# Slayt 19'daki sağ şema ("Geothermal Energy"). Soldaki numaralı şemanın açıklaması slaytta yok; çizilmedi.
s = Sekil(360, 280, "Jeotermal santral şeması: sıcak su, buhar, türbin ve generatör, soğutma kulesi, enjeksiyon kuyusu")
TURUNCU_B = "#DD6B20"
s.yazi(180, 22, "Geothermal Energy", 14, YESIL_K, kalin=True)
# Toprak, yer altı suyu ve en alttaki sıcak katman
s.ekle('<rect x="0" y="170" width="360" height="56" fill="#E8D9C5"/>')
s.cizgi(0, 170, 360, 170, YESIL, 3)
s.ekle('<rect x="0" y="226" width="360" height="38" fill="#BEE3F8"/>')
s.ekle('<rect x="0" y="264" width="360" height="6" fill="#C53030"/>')
# Üretim kuyusu (sıcak su yukarı)
s.cizgi(50, 246, 50, 150, TURUNCU_B, 4)
s.ok(66, 214, 66, 188, SONUK, 1.5)
s.yazi(74, 206, "Hot Water", 11, hiza="start")
# Buhar ayırıcı
yuvarlak_kutu(s, 34, 118, 32, 32, "#EDF2F7", SONUK, kal=1.4, rx=3)
s.yazi(50, 108, "Steam", 11)
# Buhar hattı → türbin ve generatör
s.cizgi(66, 140, 110, 140, TURUNCU_B, 4)
yuvarlak_kutu(s, 110, 128, 64, 24, "#E2E8F0", SONUK, kal=1.4, rx=3)
s.ekle('<polygon points="118,134 132,130 132,150 118,146" fill="#A0AEC0"/>')
s.cizgi(132, 140, 148, 140, SONUK, 2)
s.ekle('<rect x="148" y="132" width="20" height="16" fill="#A0AEC0"/>')
s.yazi(142, 118, "Turbine & Generator", 11)
# Türbinden yer altından soğutma kulesine
s.ekle('<polyline points="160,152 160,194 232,194 232,165" fill="none" stroke="%s" stroke-width="4"/>' % TURUNCU_B)
# Soğutma kulesi binası ve bacaları
s.ekle('<polygon points="236,110 240,64 248,64 252,110" fill="#CBD5E0" stroke="%s" stroke-width="1.2"/>' % SONUK)
s.ekle('<polygon points="268,110 272,64 280,64 284,110" fill="#CBD5E0" stroke="%s" stroke-width="1.2"/>' % SONUK)
yuvarlak_kutu(s, 220, 110, 82, 55, "#E2E8F0", SONUK, kal=1.4, rx=3)
s.yazi(274, 186, "Cooling Tower", 11)
# Enjeksiyon kuyusu (soğuyan su aşağı)
s.ekle('<polyline points="302,150 318,150 318,246" fill="none" stroke="%s" stroke-width="4"/>' % SU)
s.ok(332, 196, 332, 222, SONUK, 1.5)
s.yazi(310, 210, "Injection", 11, hiza="end")
s.yazi(310, 223, "Well", 11, hiza="end")
s.kaydet("uretim-jeotermal-santral.svg")

# ---------------------------------------------------------------- P01-3) uretim-turkiye-2021
# Slayt 21'deki pasta grafik; renkler ve sıra slayttaki gibi, saat 12'den saat yönünde.
s = Sekil(360, 330, "2021 yılında ülkemizdeki kaynaklara göre elektrik üretimi (pasta grafik)")
s.yazi(180, 22, "2021 Yılında Ülkemizdeki Kaynaklara", 14, kalin=True)
s.yazi(180, 41, "Göre Elektrik Üretimi", 14, kalin=True)
PAYLAR = [("Kömür", "30,9", 30.9, "#5B9BD5"), ("Doğal Gaz", "33,2", 33.2, "#ED7D31"),
          ("Hidrolik", "16,7", 16.7, "#A5A5A5"), ("Rüzgâr", "9,4", 9.4, "#FFC000"),
          ("Güneş", "4,2", 4.2, "#4472C4"), ("Jeotermal", "3,2", 3.2, "#70AD47"),
          ("Diğer Kaynaklar", "2,4", 2.4, "#264478")]
assert abs(sum(p[2] for p in PAYLAR) - 100) < 1e-9
cx, cy, r = 180, 148, 88
aci = -90.0
for ad, yazi_, pay, renk in PAYLAR:
    a1 = math.radians(aci); a2 = math.radians(aci + pay * 3.6)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
    s.ekle('<path d="M %.1f %.1f L %.1f %.1f A %d %d 0 %d 1 %.1f %.1f Z" fill="%s" stroke="#FFFFFF" stroke-width="1.5"/>' % (
        cx, cy, x1, y1, r, r, 1 if pay > 50 else 0, x2, y2, renk))
    if pay >= 9:
        orta = math.radians(aci + pay * 1.8)
        s.yazi(cx + r * 0.62 * math.cos(orta), cy + r * 0.62 * math.sin(orta) + 4, "%" + yazi_, 12, kalin=True)
    aci += pay * 3.6
# Gösterge: iki sütun
for i, (ad, yazi_, pay, renk) in enumerate(PAYLAR):
    x = 30 if i < 4 else 200
    y = 260 + (i % 4) * 18
    s.ekle('<rect x="%d" y="%d" width="11" height="11" fill="%s"/>' % (x, y - 10, renk))
    s.yazi(x + 17, y, "%s %%%s" % (ad, yazi_), 12, hiza="start")
s.kaydet("uretim-turkiye-2021.svg")

# ================================================================ P02 (slayt 23–33, 161–162): atom, iletken, yarı iletken, yalıtkan

def p02_yorunge(s, cx, cy, r, renk="#A0AEC0", kal=1.2):
    s.ekle('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="%s"/>' % (cx, cy, r, renk, kal))

def p02_elektronlar(s, cx, cy, r, n, renk, bas=-90.0, yaricap=4.5):
    """r yarıçaplı yörüngeye n elektronu eşit aralıkla dizer; konumları döndürür."""
    yerler = []
    for i in range(n):
        a = math.radians(bas + 360.0 * i / n)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        s.ekle('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, yaricap, renk))
        yerler.append((x, y))
    return yerler

P02_ELEKTRON = "#2B6CB0"; P02_SON = "#C05621"

# ---------------------------------------------------------------- P02-1) atom-yapisi
# Slayt 25'teki "ATOM" şekli: çekirdekte proton ve nötron, yörüngeler, elektronlar.
# Hocanın şeklinde dış yörüngede sekizden çok elektron çizili; burada 2, 8, 8 diye sadeleştirildi (rapor ve envanter).
s = Sekil(360, 330, "Atomun yapısı: çekirdekte proton ve nötron, çekirdeğin etrafındaki yörüngelerde elektronlar")
s.yazi(180, 24, "ATOM", 15, kalin=True)
cx, cy = 180, 165
for r in (40, 75, 108):
    p02_yorunge(s, cx, cy, r)
p02_elektronlar(s, cx, cy, 40, 2, P02_ELEKTRON, bas=-60)
orta = p02_elektronlar(s, cx, cy, 75, 8, P02_ELEKTRON, bas=-70)
dis = p02_elektronlar(s, cx, cy, 108, 8, P02_ELEKTRON, bas=-30)
# Çekirdek: proton ve nötron
s.ekle('<circle cx="171" cy="160" r="13" fill="#BEE3F8" stroke="%s" stroke-width="1.4"/>' % MAVI)
s.yazi(171, 165, "p⁺", 12, MAVI, kalin=True)
s.ekle('<circle cx="190" cy="174" r="13" fill="#E6F4EA" stroke="%s" stroke-width="1.4"/>' % YESIL_K)
s.yazi(190, 179, "n", 12, YESIL_K, kalin=True)
# Etiketler (sol: Proton, Çekirdek, Yörüngeler; sağ: Elektronlar, Nötron)
s.cizgi(64, 62, 160, 152, SONUK, 1)
s.yazi(14, 58, "Proton", 12, hiza="start")
s.cizgi(64, 196, 159, 168, SONUK, 1)
s.yazi(14, 200, "Çekirdek", 12, hiza="start")
# Üç çizgi üç ayrı yörüngeye, ayrı açılardan (elektronlara değmeyecek açılar)
for r, aci in ((40, 100), (75, 130), (108, 125)):
    a = math.radians(aci)
    s.cizgi(78, 262, cx + r * math.cos(a), cy + r * math.sin(a), SONUK, 1)
s.yazi(14, 276, "Yörüngeler", 12, hiza="start")
s.cizgi(300, 64, dis[1][0] + 4, dis[1][1] - 3, SONUK, 1)
s.cizgi(300, 64, orta[1][0] + 3, orta[1][1] - 3, SONUK, 1)
s.yazi(346, 58, "Elektronlar (e⁻)", 12, hiza="end")
s.cizgi(296, 214, 203, 177, SONUK, 1)
s.yazi(346, 228, "Nötron", 12, hiza="end")
s.yazi(180, 306, "Atomu oluşturan temel tanecikler:", 12)
s.yazi(180, 322, "nötron, proton ve elektronlardır.", 12)
s.kaydet("atom-yapisi.svg")

# ---------------------------------------------------------------- P02-2) atom-elektron-dagilimi
# Slayt 26'daki üç çözüm: 16 S: 2 8 6; 11 Na: 2 8 1; 19 K: 2 8 8 1. Son yörünge turuncu.
s = Sekil(360, 400, "Elektron dağılımı örnekleri: 16 S 2 8 6, 11 Na 2 8 1, 19 K 2 8 8 1; son yörüngedeki elektronlar turuncu")
s.yazi(180, 22, "Elektronların yörüngelere yerleşimi", 14, kalin=True)
ORNEKLER = [("16 S", [2, 8, 6], 6), ("11 Na", [2, 8, 1], 1), ("19 K", [2, 8, 8, 1], 1)]
y0 = 40
for i, (ad, dag, son) in enumerate(ORNEKLER):
    assert sum(dag) == int(ad.split()[0]) and dag[-1] == son
    ust = y0 + i * 120
    kutu(s, 6, ust, 348, 112)
    cx, cy = 76, ust + 56
    s.ekle('<circle cx="%d" cy="%d" r="7" fill="#FED7D7" stroke="%s" stroke-width="1.2"/>' % (cx, cy, KIRMIZI))
    for k, n in enumerate(dag):
        r = 16 + 12 * k
        p02_yorunge(s, cx, cy, r)
        p02_elektronlar(s, cx, cy, r, n, P02_SON if k == len(dag) - 1 else P02_ELEKTRON, bas=-90 + 20 * k, yaricap=3.6)
    s.yazi(150, ust + 32, ad, 15, kalin=True, hiza="start")
    s.yazi(150, ust + 58, "Dağılım: " + " ".join(str(n) for n in dag), 13, hiza="start")
    s.yazi(150, ust + 84, "Son yörüngede %d elektron" % son, 13, P02_SON, kalin=True, hiza="start")
s.kaydet("atom-elektron-dagilimi.svg")

# ---------------------------------------------------------------- P02-3) atom-valans-elektronlari
# Slayt 27'deki şekil: çekirdek "+14", yörüngelerde 2, 8, 4 elektron; etiketler Valans Elektronlar, Çekirdek, Dış Kabuk.
s = Sekil(360, 300, "Valans elektronları: çekirdeği +14 olan atomun dış kabuğundaki 4 elektron valans elektronudur")
cx, cy = 132, 186
for r in (30, 62, 94):
    p02_yorunge(s, cx, cy, r, "#4A5568", 1.4)
s.ekle('<circle cx="%d" cy="%d" r="16" fill="#FFFFFF" stroke="#4A5568" stroke-width="1.2"/>' % (cx, cy))
s.yazi(cx, cy + 4, "+14", 12, KIRMIZI, kalin=True)
p02_elektronlar(s, cx, cy, 30, 2, P02_ELEKTRON)
p02_elektronlar(s, cx, cy, 62, 8, P02_ELEKTRON)
val = p02_elektronlar(s, cx, cy, 94, 4, P02_SON, bas=-125, yaricap=5.5)
# Valans Elektronlar etiketi (dış yörüngedeki elektronlara)
yuvarlak_kutu(s, 40, 16, 150, 30, "#FFFFFF", "#4A5568", kal=1.2, rx=2)
s.yazi(115, 36, "Valans Elektronlar", 13, kalin=True)
s.cizgi(95, 46, val[0][0] + 2, val[0][1] - 5, SONUK, 1)
s.cizgi(150, 46, val[1][0] - 3, val[1][1] - 5, SONUK, 1)
# Çekirdek etiketi
yuvarlak_kutu(s, 262, 250, 84, 28, "#FFFFFF", "#4A5568", kal=1.2, rx=2)
s.yazi(304, 269, "Çekirdek", 13, kalin=True)
s.cizgi(262, 264, cx + 14, cy + 8, SONUK, 1)
# Dış Kabuk etiketi
yuvarlak_kutu(s, 262, 140, 88, 28, "#FFFFFF", "#4A5568", kal=1.2, rx=2)
s.yazi(306, 159, "Dış Kabuk", 13, kalin=True)
s.cizgi(262, 156, cx + 93.1, cy - 13.1, SONUK, 1)
s.kaydet("atom-valans-elektronlari.svg")

# ================================================================ P03 (slayt 34–56): el takımları, elektrik ve mekanik alanında

P03_KOYU = "#2D3748"; P03_MAVI_D = "#BEE3F8"

def p03_kalin_ok(s, x1, y1, kx, ky, x2, y2, dolgu):
    """(x1,y1)'den (x2,y2)'ye, (kx,ky) denetim noktalı eğri, kenarı koyu kalın ok."""
    d = "M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (x1, y1, kx, ky, x2, y2)
    s.ekle('<path d="%s" fill="none" stroke="%s" stroke-width="11" stroke-linecap="butt"/>' % (d, P03_KOYU))
    s.ekle('<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linecap="butt"/>' % (d, dolgu))
    a = math.atan2(y2 - ky, x2 - kx)
    uc = (x2 + 13 * math.cos(a), y2 + 13 * math.sin(a))
    p1 = (x2 + 10 * math.cos(a + math.pi / 2), y2 + 10 * math.sin(a + math.pi / 2))
    p2 = (x2 + 10 * math.cos(a - math.pi / 2), y2 + 10 * math.sin(a - math.pi / 2))
    s.ekle('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>' % (
        uc[0], uc[1], p1[0], p1[1], p2[0], p2[1], dolgu, P03_KOYU))

def p03_circir_kafa(s, cx, yon):
    """Cırcır anahtarın başı ve sapı; yon=-1: dilin pimi sağda, ucu solda (GEVŞETME); +1: tersi (SIKMA)."""
    s.ekle('<path d="M %.1f 112 L %.1f 206 L %.1f 206 L %.1f 112 Z" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % (
        cx - 22, cx - 8, cx + 8, cx + 22, P03_KOYU))
    s.ekle('<circle cx="%.1f" cy="88" r="36" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % (cx, P03_KOYU))
    s.ekle('<circle cx="%.1f" cy="80" r="16" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % (cx, P03_KOYU))
    for dx in (-24, 24):
        s.ekle('<circle cx="%.1f" cy="102" r="5" fill="#FFFFFF" stroke="%s" stroke-width="1.2"/>' % (cx + dx, P03_KOYU))
    # cırcır dili (kilit): pim bir yanda, ucu öteki yanda
    px, ux = cx - 6 * yon, cx + 9 * yon
    s.ekle('<line x1="%.1f" y1="104" x2="%.1f" y2="122" stroke="%s" stroke-width="9" stroke-linecap="round"/>' % (px, ux, P03_KOYU))
    s.ekle('<line x1="%.1f" y1="104" x2="%.1f" y2="122" stroke="%s" stroke-width="6" stroke-linecap="round"/>' % (px, ux, P03_MAVI_D))
    s.ekle('<circle cx="%.1f" cy="104" r="2.5" fill="%s"/>' % (px, P03_KOYU))

# ---------------------------------------------------------------- P03-1) el-takim-circir
# Slayt 44'teki şekil: GEVŞETME ve SIKMA; her birinde bir yön "Kilitli" (mavi ok), öteki "Serbest" (beyaz ok).
# GEVŞETME: sol ok Serbest, sağ ok Kilitli. SIKMA: sol ok Kilitli, sağ ok Serbest (slayttaki gibi).
s = Sekil(360, 250, "Cırcır anahtarda gevşetme ve sıkma: kilitli ve serbest yönler")
for cx, ad, sol, sag, yon in ((90, "GEVŞETME", "Serbest", "Kilitli", -1), (270, "SIKMA", "Kilitli", "Serbest", 1)):
    p03_circir_kafa(s, cx, yon)
    for taraf, etiket in ((-1, sol), (1, sag)):
        dolgu = P03_MAVI_D if etiket == "Kilitli" else "#FFFFFF"
        p03_kalin_ok(s, cx + 28 * taraf, 182, cx + 64 * taraf, 182, cx + 76 * taraf, 128, dolgu)
        s.yazi(cx + 62 * taraf, 102, etiket, 12, P03_KOYU)
    s.yazi(cx, 236, ad, 13, P03_KOYU, kalin=True)
s.cizgi(180, 20, 180, 228, GRI_C, 1, kesik=True)
s.kaydet("el-takim-circir.svg")

# ---------------------------------------------------------------- P03-2) el-takim-torkmetre
# Slayt 48'deki çizim: Döner tutamak, Skala, İbre, Kol, Kafa (adlar slayttaki gibi).
s = Sekil(360, 190, "Torkmetrenin parçaları: döner tutamak, skala, ibre, kol ve kafa")
# Kol
s.ekle('<rect x="66" y="96" width="256" height="12" rx="2" fill="#E2E8F0" stroke="%s" stroke-width="1.6"/>' % P03_KOYU)
# Kafa ve kare uç
s.ekle('<rect x="318" y="88" width="20" height="28" rx="3" fill="#E2E8F0" stroke="%s" stroke-width="1.6"/>' % P03_KOYU)
s.ekle('<rect x="322" y="116" width="12" height="9" fill="#CBD5E0" stroke="%s" stroke-width="1.4"/>' % P03_KOYU)
# Döner tutamak
s.ekle('<rect x="14" y="92" width="53" height="20" rx="9" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % P03_KOYU)
# Skala: kolun üstünde yay ve çizgiler
s.ekle('<path d="M 72 96 A 30 30 0 0 1 132 96" fill="%s" stroke="%s" stroke-width="1.6"/>' % (MAVI_D, P03_KOYU))
for i in range(9):
    a = math.radians(180 + 22.5 * i)
    s.cizgi(102 + 30 * math.cos(a), 96 + 30 * math.sin(a), 102 + 24 * math.cos(a), 96 + 24 * math.sin(a), P03_KOYU, 1)
# İbre: kafadan skalaya uzanan ince çubuk
s.cizgi(318, 90, 104, 74, VURGU, 2.2)
# Etiketler ve okları (slaytta Skala altta; telefonda kol çizgisini kesmesin diye üste alındı)
s.yazi(8, 30, "Döner tutamak", 12, hiza="start")
s.ok(36, 36, 36, 90)
s.yazi(200, 30, "İbre", 12)
s.ok(200, 36, 200, 80)
s.yazi(328, 30, "Kafa", 12)
s.ok(328, 36, 328, 86)
s.yazi(124, 30, "Skala", 12)
s.ok(124, 36, 116, 68)
s.yazi(200, 176, "Kol", 12)
s.ok(200, 162, 200, 110)
s.kaydet("el-takim-torkmetre.svg")

# ================================================================ P04 (slayt 57–67): elektrik yükü, akım, gerilim; iş, güç, direnç

P04_KOYU = "#2D3748"; P04_ELEKTRON = "#3182CE"; P04_SU = "#5A67D8"; P04_SU_D = "#C3DAFE"

def p04_elektron(s, x, y, r=5.5):
    """Kırmızı küçük top: atom şekillerindeki elektron (slayt 59'daki gibi)."""
    s.ekle('<circle cx="%.1f" cy="%.1f" r="%s" fill="#E53E3E" stroke="#9B2C2C" stroke-width="1"/>' % (x, y, r))

def p04_atom(s, cx, cy, p, n, yorungeler, r_ic=24, r_dis=42, bos_aci=None):
    """Çekirdek (p ve n yazılı koyu daire), kesik yörüngeler ve elektronlar.
    yorungeler: her yörüngedeki elektron sayısı (içten dışa). bos_aci: dış yörüngede elektron konmayacak açı (derece)."""
    for i, k in enumerate(yorungeler):
        r = (r_ic, r_dis)[i]
        s.ekle('<circle cx="%.1f" cy="%.1f" r="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="5 4"/>' % (cx, cy, r, P04_KOYU))
        for j in range(k):
            a = math.radians(-90 + 360 * j / max(k, 1) + (0 if i == 0 else 20))
            p04_elektron(s, cx + r * math.cos(a), cy + r * math.sin(a))
    s.ekle('<circle cx="%.1f" cy="%.1f" r="15" fill="%s"/>' % (cx, cy, P04_KOYU))
    s.yazi(cx, cy - 2, "%d p" % p, 11, "#FFFFFF", kalin=True)
    s.yazi(cx, cy + 10, "%d n" % n, 11, "#FFFFFF", kalin=True)

def p04_genis_ok(s, x1, x2, y, dolgu="#ED8936"):
    """Turuncu geniş ok (slayt 59'daki dönüşüm oku)."""
    s.ekle('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="#C05621" stroke-width="1"/>' % (
        x1, y - 5, x2 - 12, y - 5, x2 - 12, y - 10, x2, y, x2 - 12, y + 10, x2 - 12, y + 5, x1, y + 5, dolgu))

def p04_egri_ok(s, x1, y1, kx, ky, x2, y2, renk="#3182CE"):
    """Mavi eğri ok (elektronun ayrılışı ya da gelişi)."""
    s.ekle('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="3.5"/>' % (x1, y1, kx, ky, x2, y2, renk))
    a = math.atan2(y2 - ky, x2 - kx)
    p1 = (x2 - 10 * math.cos(a - 0.5), y2 - 10 * math.sin(a - 0.5))
    p2 = (x2 - 10 * math.cos(a + 0.5), y2 - 10 * math.sin(a + 0.5))
    s.ekle('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (x2 + 3 * math.cos(a), y2 + 3 * math.sin(a), p1[0], p1[1], p2[0], p2[1], renk))

def p04_net_yuk(s, x, y, p, e, net):
    """Şekildeki p, e ve net yük hesabı: p = ..; − e = ..; çizgi; Net yük = .."""
    s.yazi(x + 8, y, "p = %d" % p, 12, egik=True)
    s.yazi(x - 30, y + 17, "−", 12)
    s.yazi(x + 8, y + 17, "e = %d" % e, 12, egik=True)
    s.cizgi(x - 38, y + 23, x + 40, y + 23, YAZI, 1.4)
    s.yazi(x, y + 39, "Net yük = %s" % net, 12, egik=True)

# ---------------------------------------------------------------- P04-1) yuk-iyon-olusumu
# Slayt 59'daki şekil: nötr lityum atomu bir elektron vererek katyon olur (p = 3, e = 2, net yük = +1);
# nötr flor atomu bir elektron alarak anyon olur (p = 9, e = 10, net yük = −1). Yazılar slayttaki gibi.
# Slaytta flor çekirdeğine "9 n" yazılıdır; flor atomunda 10 nötron vardır, burada 10 n çizildi (notun Ek'inde söylenir).
s = Sekil(360, 356, "Nötr lityum atomu elektron vererek katyon, nötr flor atomu elektron alarak anyon olur")
# Lityum: iç yörüngede 2, dış yörüngede 1 elektron (ayrılan)
s.ekle('<circle cx="72" cy="76" r="42" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="5 4"/>' % P04_KOYU)
p04_atom(s, 72, 76, 3, 4, [2])
p04_elektron(s, 72 + 42 * math.cos(math.radians(205)), 76 + 42 * math.sin(math.radians(205)))
p04_egri_ok(s, 30, 52, 20, 30, 14, 14)
p04_genis_ok(s, 124, 166, 76)
p04_atom(s, 214, 76, 3, 4, [2])
p04_net_yuk(s, 306, 54, 3, 2, "+1")
s.yazi(72, 140, "Nötr lityum atomu", 12, egik=True)
s.yazi(214, 122, "Lityum katyonu", 12, egik=True)
s.yazi(180, 162, "Nötr lityum atomu bir elektron vererek katyon olur.", 12, egik=True)
s.cizgi(16, 178, 344, 178, GRI_C, 1)
# Flor: iç yörüngede 2, dış yörüngede 7 elektron + gelen 1 elektron; anyonda dış yörüngede 8
p04_atom(s, 86, 252, 9, 10, [2, 7])
p04_elektron(s, 18, 214)
p04_egri_ok(s, 22, 205, 30, 186, 52, 196)
p04_genis_ok(s, 136, 168, 252)
p04_atom(s, 220, 252, 9, 10, [2, 8])
p04_net_yuk(s, 312, 232, 9, 10, "−1")
s.yazi(52, 314, "Nötr flor atomu", 12, egik=True)
s.yazi(220, 314, "Flor anyonu", 12, egik=True)
s.yazi(180, 342, "Nötr flor atomu bir elektron alarak anyon olur.", 12, egik=True)
s.kaydet("yuk-iyon-olusumu.svg")

# ---------------------------------------------------------------- P04-2) yuk-coulomb-kanunu
# Slayt 60'taki soldaki şekil: "Unlike charges attract." (q1 +, q2 −; aralarında r) ve
# "Like charges repel." (+ + ve − −). Kuvvet okları slayttaki gibi: q1'in yanındaki F21, q2'nin yanındaki F12.

def p04_yuk(s, x, y, isaret):
    koyu = isaret == "−"
    s.ekle('<circle cx="%.1f" cy="%.1f" r="14" fill="%s" stroke="%s" stroke-width="1.4"/>' % (x, y, "#4A5568" if koyu else "#CBD5E0", P04_KOYU))
    renk = "#FFFFFF" if koyu else YAZI
    s.cizgi(x - 6, y, x + 6, y, renk, 2.2)
    if not koyu: s.cizgi(x, y - 6, x, y + 6, renk, 2.2)

def p04_bos_ok(s, x1, x2, y):
    """İçi boş kuvvet oku (slayttaki gibi); x1'den x2'ye."""
    yon = 1 if x2 > x1 else -1
    g = x2 - 9 * yon
    s.ekle('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#FFFFFF" stroke="%s" stroke-width="1.3"/>' % (
        x1, y - 2.5, g, y - 2.5, g, y - 6, x2, y, g, y + 6, g, y + 2.5, x1, y + 2.5, P04_KOYU))

s = Sekil(360, 270, "Coulomb kanunu: farklı yükler birbirini çeker, aynı yükler birbirini iter")
s.yazi(16, 22, "Unlike charges attract.", 12, egik=True, hiza="start")
s.cizgi(110, 42, 250, 42, P04_KOYU, 1.2, kesik=True)
s.cizgi(110, 38, 110, 46, P04_KOYU, 1.2); s.cizgi(250, 38, 250, 46, P04_KOYU, 1.2)
s.ekle('<rect x="172" y="34" width="16" height="16" fill="#FFFFFF"/>')
s.yazi(180, 47, "r", 13, egik=True, kalin=True)
for x, isaret in ((110, "+"), (250, "−")): p04_yuk(s, x, 74, isaret)
p04_bos_ok(s, 40, 95, 74); p04_bos_ok(s, 320, 265, 74)
s.yazi(66, 64, "F₂₁", 12, egik=True, kalin=True); s.yazi(294, 64, "F₁₂", 12, egik=True, kalin=True)
s.yazi(110, 106, "q₁", 12, egik=True); s.yazi(250, 106, "q₂", 12, egik=True)
s.cizgi(16, 122, 344, 122, GRI_C, 1)
s.yazi(16, 144, "Like charges repel.", 12, egik=True, hiza="start")
for y, isaret in ((172, "+"), (228, "−")):
    p04_yuk(s, 110, y, isaret); p04_yuk(s, 250, y, isaret)
    p04_bos_ok(s, 170, 125, y); p04_bos_ok(s, 190, 235, y)
    s.yazi(152, y + 20, "F₂₁", 12, egik=True, kalin=True); s.yazi(210, y + 20, "F₁₂", 12, egik=True, kalin=True)
    s.yazi(110, y + 30, "q₁", 12, egik=True); s.yazi(250, y + 30, "q₂", 12, egik=True)
s.kaydet("yuk-coulomb-kanunu.svg")

# ---------------------------------------------------------------- P04-3) yuk-su-kaplari
# Slayt 62 ve 63'teki su kapları resmi: A ve B kapları altta vanalı bir boruyla bağlı.
# Solda "Vana kapalı iken dolu ve boş kapların durumu" (A dolu, B boş), sağda "Yükseklikleri eşit sıvılar".

def p04_kap(s, x, ust, alt, su_y, g=56):
    """Silindir kap; su_y: su yüzeyinin y'si (alt'a eşitse kap boş)."""
    if su_y < alt:
        s.ekle('<rect x="%.1f" y="%.1f" width="%d" height="%.1f" fill="%s"/>' % (x, su_y, g, alt - su_y, P04_SU_D))
        s.ekle('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="6" fill="#A3BFFA" stroke="%s" stroke-width="1"/>' % (x + g / 2, su_y, g / 2, P04_SU))
    s.ekle('<path d="M %.1f %.1f L %.1f %.1f A %.1f 6 0 0 0 %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>' % (
        x, ust, x, alt, g / 2, x + g, alt, x + g, ust, P04_KOYU))
    s.ekle('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="6" fill="none" stroke="%s" stroke-width="1.6"/>' % (x + g / 2, ust, g / 2, P04_KOYU))

def p04_vana(s, x, y):
    s.ekle('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        x - 7, y - 6, x + 7, y + 6, x + 7, y - 6, x - 7, y + 6, "#718096", P04_KOYU))
    s.cizgi(x, y, x, y - 13, P04_KOYU, 1.6); s.cizgi(x - 5, y - 13, x + 5, y - 13, P04_KOYU, 2.2)

s = Sekil(360, 214, "Su kapları: vana kapalıyken A dolu, B boş; yükseklikleri eşit sıvılar")
for x0, su_a, su_b, satir in ((0, 46, 152, ["Vana kapalı iken dolu ve", "boş kapların durumu"]),
                              (182, 100, 100, ["Yükseklikleri eşit sıvılar"])):
    s.ekle('<rect x="%d" y="141" width="%d" height="7" fill="%s" stroke="%s" stroke-width="1.2"/>' % (x0 + 66, 44, "#A0AEC0", P04_KOYU))
    p04_kap(s, x0 + 12, 40, 152, su_a)
    p04_kap(s, x0 + 110, 40, 152, su_b)
    p04_vana(s, x0 + 88, 144)
    s.yazi(x0 + 40, 26, "A", 12); s.yazi(x0 + 138, 26, "B", 12)
    satirlar(s, x0 + 89, 182, satir, 12, kalin=True)
s.cizgi(180, 20, 180, 200, GRI_C, 1, kesik=True)
s.kaydet("yuk-su-kaplari.svg")

# ---------------------------------------------------------------- P04-4) yuk-elektron-akim-yonu
# Slayt 64'teki iki şekil (slaytta yan yana; telefonda alt alta): pil ve ampulden oluşan devre.
# Soldaki şekil: elektron akışı (−)'den (+)'ya, ok saat yönünün tersine; sağdaki şekil: "conventional current"
# (+)'dan (−)'ye, ok saat yönünde. Pil ve ampul slayttaki resimlerin yerine sembolle (01-devre.py) çizildi.
# İngilizce alt yazılar slayttaki gibi.

def p04_daire_ok(s, cx, cy, r, saat_yonu, renk="#2B6CB0"):
    """Neredeyse tam daire ok; saat_yonu=True ise ok saat yönünde döner."""
    if saat_yonu:
        bas, son = -150, 150      # derece; SVG'de açı saat yönünde artar
    else:
        bas, son = 150, -150
    x1, y1 = cx + r * math.cos(math.radians(bas)), cy + r * math.sin(math.radians(bas))
    x2, y2 = cx + r * math.cos(math.radians(son)), cy + r * math.sin(math.radians(son))
    s.ekle('<path d="M %.1f %.1f A %s %s 0 1 %d %.1f %.1f" fill="none" stroke="%s" stroke-width="4"/>' % (
        x1, y1, r, r, 1 if saat_yonu else 0, x2, y2, renk))
    # uç: dairenin teğeti yönünde
    a = math.radians(son)
    tx, ty = (-math.sin(a), math.cos(a)) if saat_yonu else (math.sin(a), -math.cos(a))
    devre_yon_oku(s, x2 + tx * 7, y2 + ty * 7, tx, ty, renk, 12)

def p04_devre(s, y0, saat_yonu, baslik, alt_yazi):
    sol, sag, ust, alt = 56, 280, y0 + 30, y0 + 150
    s.yazi(180, y0 + 12, baslik, 12, SONUK)
    devre_tel(s, (sol, ust + 34), (sol, ust), (sag, ust), (sag, ust + 42))
    devre_tel(s, (sag, alt - 42), (sag, alt), (sol, alt), (sol, alt - 34))
    devre_pil(s, sol, ust + 34, sol, alt - 34, arti=1, yan=1)
    devre_lamba(s, sag, ust + 42, sag, alt - 42, r=16)
    for i in range(6):
        x = sol + 28 + i * 36
        for y in (ust, alt):
            s.ekle('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="#FFFFFF" stroke-width="1"/>' % (x, y, P04_ELEKTRON))
            s.cizgi(x - 2.2, y, x + 2.2, y, "#FFFFFF", 1.2)
    p04_daire_ok(s, 168, (ust + alt) / 2, 30, saat_yonu)
    satirlar(s, 180, alt + 26, alt_yazi, 12, kalin=True)

s = Sekil(360, 446, "Elektron akış yönü (−)'den (+)'ya; kabul edilen akım yönü (+)'dan (−)'ye")
p04_devre(s, 0, False, "Soldaki şekil", ["In reality, the electron flow", "is from negative to positive"])
s.cizgi(16, 222, 344, 222, GRI_C, 1)
p04_devre(s, 226, True, "Sağdaki şekil", ["Engineers use “conventional current”", "which moves from positive to negative"])
s.kaydet("yuk-elektron-akim-yonu.svg")

# ---------------------------------------------------------------- P04-5) is-guc-mekanik-is
# Slayt 65'teki şekil: M kütlesi A noktasında, F kuvveti sağa; A ile B arasındaki yol ℓ (slaytta "l").
s = Sekil(360, 136, "Mekaniksel iş: M kütlesi F kuvvetiyle A noktasından B noktasına götürülür")
s.ekle('<defs><pattern id="p04tarama" width="6" height="6" patternUnits="userSpaceOnUse">'
       '<path d="M 0 0 L 6 6 M 6 0 L 0 6" stroke="%s" stroke-width="0.8"/></pattern></defs>' % P04_KOYU)
s.cizgi(36, 76, 324, 76, MAVI, 1.6)
s.ekle('<rect x="36" y="44" width="32" height="32" fill="url(#p04tarama)" stroke="%s" stroke-width="1.4"/>' % P04_KOYU)
s.ok(68, 60, 124, 60, YAZI, 1.6)
s.yazi(52, 36, "M", 13, kalin=True)
s.yazi(136, 65, "F", 13, kalin=True)
for x, ad, h in ((36, "A", "end"), (324, "B", "start")):
    s.ekle('<circle cx="%d" cy="76" r="3.5" fill="%s"/>' % (x, MAVI))
    s.yazi(x + (-8 if h == "end" else 8), 81, ad, 13, kalin=True, hiza=h)
    s.cizgi(x, 80, x, 112, SONUK, 1, kesik=True)
s.cizgi(40, 104, 168, 104, SONUK, 1.2, kesik=True); s.cizgi(192, 104, 320, 104, SONUK, 1.2, kesik=True)
devre_yon_oku(s, 36, 104, -1, 0, SONUK, 8); devre_yon_oku(s, 324, 104, 1, 0, SONUK, 8)
s.yazi(180, 109, "ℓ", 14, kalin=True, egik=True)
s.kaydet("is-guc-mekanik-is.svg")

# ================================================================ P05 ŞEKİLLERİ (slayt 68–81)
# Devre sembolleri 01-devre.py'dendir. Yazılar hocanın şekillerindeki gibi küçük harf ve eğik.

def p05_devre(s, sol, sag, ust, alt, etiketler=True, kapali=False, kisa=False):
    """Slayt 68 ve 74'teki devre: solda üreteç ((+) üstte), üstte sigorta ve anahtar, sağda alıcı.
    etiketler=True: sigorta, anahtar, üreteç, alıcı, iletken yazılır; False: yalnızca anahtar.
    kisa=True: anahtarla alıcı arasında iki teli birleştiren kesik çizgi (kısa devre)."""
    orta = (ust + alt) / 2
    sx1, sx2 = sol + 30, sol + 92          # sigorta
    ax1, ax2 = sol + 118, sol + 170        # anahtar
    devre_tel(s, (sol, orta - 26), (sol, ust), (sx1, ust))
    devre_sigorta(s, sx1, ust, sx2, ust, govde=40, en=10)
    devre_tel(s, (sx2, ust), (ax1, ust))
    devre_anahtar(s, ax1, ust, ax2, ust, kapali=kapali, govde=34, yan=-1)
    devre_tel(s, (ax2, ust), (sag, ust), (sag, orta - 26))
    devre_direnc(s, sag, orta - 26, sag, orta + 26, bicim="kutu", govde=40, en=14)
    devre_tel(s, (sag, orta + 26), (sag, alt), (sol, alt), (sol, orta + 26))
    devre_batarya(s, sol, orta - 26, sol, orta + 26, hucre=3, arti=1, yan=-1)
    if kisa:
        kx = (ax2 + sag) / 2 + 4
        s.cizgi(kx, ust, kx, alt, DEVRE_C, 1.8, kesik=True)
    s.yazi((ax1 + ax2) / 2, ust + 22, "anahtar", 13, egik=True)
    if etiketler:
        s.yazi((sx1 + sx2) / 2, ust + 22, "sigorta", 13, egik=True)
        s.yazi(sol + 26, orta + 5, "üreteç", 13, egik=True, hiza="start")
        s.yazi(sag - 16, orta + 5, "alıcı", 13, egik=True, hiza="end")
        s.yazi((sol + sag) / 2, alt - 8, "iletken", 13, egik=True)

# ---------------------------------------------------------------- P05-1) devre-elemanlari
# Slayt 68: elektrik devresi; üreteç, sigorta, anahtar (açık), alıcı ve iletken.
s = Sekil(360, 190, "Elektrik devresi: üreteç, sigorta, anahtar, alıcı ve iletken")
p05_devre(s, 60, 300, 30, 170)
s.kaydet("devre-elemanlari.svg")

# ---------------------------------------------------------------- P05-2) devre-acik-kapali-kisa
# Slayt 74 (ve 81'deki aynı şekiller): Şekil.1 açık devre (bütün etiketler), Şekil.2 kapalı devre,
# Şekil.3 kısa devre (anahtar kapalı, anahtarla alıcı arasında kesik çizgi). Slaytta yan yana; telefonda alt alta.
s = Sekil(360, 600, "Şekil 1 açık devre, Şekil 2 kapalı devre, Şekil 3 kısa devre")
for i, (ad, et, kap, kis) in enumerate((("Açık Devre", True, False, False),
                                         ("Kapalı Devre", False, True, False),
                                         ("Kısa Devre", False, True, True))):
    y0 = i * 200
    p05_devre(s, 60, 300, y0 + 24, y0 + 150, etiketler=et, kapali=kap, kisa=kis)
    s.yazi(180, y0 + 180, "Şekil.%d: %s" % (i + 1, ad), 14, kalin=True)
    if i < 2:
        s.cizgi(16, y0 + 196, 344, y0 + 196, GRI_C, 1)
s.kaydet("devre-acik-kapali-kisa.svg")

# ================================================================ P06 ŞEKİLLERİ (slayt 82–89)
# Devre sembolleri 01-devre.py'dendir (P06 yalnızca devre_toprak'ı ekledi). Slayt 86–88'deki
# resimli devreler (pil, anahtar, sigorta, ampul, ölçü aleti resimleri) sembollerle çizildi;
# şekillerdeki İngilizce adlar slayttaki gibi bırakıldı. Ölçü aletinin uçları (slayt 89'daki gibi) mavi.

OLCU_C = "#2B6CB0"

def p06_ok_cizgisi(s, x1, y1, x2, y2):
    s.cizgi(x1, y1, x2, y2, SONUK, 1)

# ---------------------------------------------------------------- P06-1) olcme-analog-avometre
# Slayt 82, "a) Analog avometre şeması": skala, ibre, S.ayarı, sıfır ayar vidası, kademe anahtarı,
# ölçüm terminali, problar. Slayttaki yazılar Türkçe harflerle yazıldı ("Termina" kesik: terminali).
s = Sekil(360, 310, "Analog avometre şeması: skala, ibre, S.ayarı, sıfır ayar vidası, kademe anahtarı, ölçüm terminali, problar")
s.ekle('<rect x="120" y="20" width="120" height="230" rx="6" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % DEVRE_C)
s.ekle('<rect x="130" y="30" width="100" height="90" fill="#FFFFFF" stroke="%s" stroke-width="1.4"/>' % DEVRE_C)
s.ekle('<path d="M 140 64 Q 180 36 220 64" fill="none" stroke="%s" stroke-width="1.6"/>' % DEVRE_C)
s.cizgi(176, 100, 196, 50, DEVRE_C, 1.6)                      # ibre
s.ekle('<rect x="166" y="94" width="28" height="18" fill="#FFFFFF" stroke="%s" stroke-width="1.4"/>' % DEVRE_C)
s.ekle('<circle cx="180" cy="103" r="4" fill="#FFFFFF" stroke="%s" stroke-width="1.4"/>' % DEVRE_C)
s.ekle('<circle cx="240" cy="124" r="10" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % DEVRE_C)   # sıfır ayar vidası
s.cizgi(120, 132, 230, 132, DEVRE_C, 1.4)
s.ekle('<circle cx="180" cy="178" r="27" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>' % DEVRE_C)  # kademe anahtarı
s.ekle('<rect x="174" y="153" width="12" height="50" rx="3" fill="#FFFFFF" stroke="%s" stroke-width="1.4" transform="rotate(20 180 178)"/>' % DEVRE_C)
for x in (204, 222):                                           # ölçüm terminalleri
    s.ekle('<circle cx="%d" cy="228" r="5" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % (x, DEVRE_C))
devre_tel(s, (204, 233), (204, 262), (102, 262), kal=1.4)
devre_tel(s, (222, 233), (222, 278), (102, 278), kal=1.4)
for y in (262, 278):                                           # problar
    s.ekle('<rect x="42" y="%d" width="60" height="7" rx="2" fill="#FFFFFF" stroke="%s" stroke-width="1.4"/>' % (y - 3.5, DEVRE_C))
    s.cizgi(22, y, 42, y, DEVRE_C, 1.4)
s.yazi(112, 59, "Skala", 13, hiza="end"); p06_ok_cizgisi(s, 114, 55, 152, 55)
s.yazi(112, 84, "ibre", 13, hiza="end"); p06_ok_cizgisi(s, 114, 80, 187, 80)
s.yazi(112, 108, "S.ayarı", 13, hiza="end"); p06_ok_cizgisi(s, 114, 104, 166, 104)
s.yazi(112, 170, "Kademe", 13, hiza="end"); s.yazi(112, 186, "anahtarı", 13, hiza="end")
p06_ok_cizgisi(s, 114, 178, 153, 178)
s.yazi(256, 121, "sıfır ayar", 13, hiza="start"); s.yazi(256, 137, "vidası", 13, hiza="start")
s.yazi(256, 222, "Ölçüm", 13, hiza="start"); s.yazi(256, 238, "terminali", 13, hiza="start")
p06_ok_cizgisi(s, 227, 228, 252, 228)
s.yazi(72, 250, "problar", 13)
s.yazi(180, 302, "a) Analog avometre şeması", 13, kalin=True)
s.kaydet("olcme-analog-avometre.svg")

# ---------------------------------------------------------------- P06-2) olcme-ampermetre
# Slayt 86: solda Battery, Switch, Fuse, Ammeter (2 A), Globe; pilin (−) ucu ve lamba toprağa bağlı.
# Sağda iki 1,5 V'luk pil, ampermetre ve lamba. Slaytta yan yana; telefonda alt alta.
s = Sekil(360, 332, "Ampermetre devreye seri bağlanır: pil, anahtar, sigorta, ampermetre ve lamba aynı yol üzerinde")
devre_tel(s, (40, 86), (40, 40), (70, 40))
devre_anahtar(s, 70, 40, 110, 40, kapali=True, govde=30)
devre_tel(s, (110, 40), (135, 40))
devre_sigorta(s, 135, 40, 185, 40, govde=36)
devre_tel(s, (185, 40), (208, 40))
devre_olcu(s, 208, 40, 252, 40, "A")
devre_tel(s, (252, 40), (300, 40), (300, 90))
devre_lamba(s, 300, 90, 300, 126)
devre_tel(s, (300, 126), (300, 148)); devre_toprak(s, 300, 148)
devre_pil(s, 40, 86, 40, 120, arti=1, yan=1)
devre_tel(s, (40, 120), (40, 148)); devre_toprak(s, 40, 148)
s.yazi(90, 64, "Switch", 12); s.yazi(160, 64, "Fuse", 12); s.yazi(230, 72, "Ammeter", 12)
s.yazi(230, 22, "2 A", 13, renk=KIRMIZI, kalin=True)
s.yazi(60, 108, "Battery", 12, hiza="start"); s.yazi(284, 112, "Globe", 12, hiza="end")
s.cizgi(16, 182, 344, 182, GRI_C, 1)
devre_tel(s, (40, 300), (40, 230), (100, 230))
devre_olcu(s, 100, 230, 140, 230, "A")
devre_tel(s, (140, 230), (200, 230))
devre_lamba(s, 200, 230, 240, 230)
devre_tel(s, (240, 230), (320, 230), (320, 300), (230, 300))
devre_pil(s, 200, 300, 230, 300, arti=1, yan=1)
devre_tel(s, (200, 300), (150, 300))
devre_pil(s, 120, 300, 150, 300, arti=1, yan=1)
devre_tel(s, (120, 300), (40, 300))
s.yazi(120, 212, "Ampermetre", 12)
s.yazi(135, 282, "1,5 V", 12); s.yazi(215, 282, "1,5 V", 12)
s.kaydet("olcme-ampermetre.svg")

# ---------------------------------------------------------------- P06-3) olcme-voltmetre
# Slayt 87: solda voltmetre (12 V) pilin uçlarında; ortada lamba, voltmetre ve pil paralel;
# sağda voltmetre lambanın uçlarında ((−) ucu pilin (−) ucuna, (+) ucu lambanın üst ucuna; pilin
# (−) ucu ve lamba toprağa bağlı). Slaytta yan yana; telefonda alt alta.
s = Sekil(360, 520, "Voltmetre devreye paralel bağlanır: pilin uçlarında, lamba ve pille paralel, lambanın uçlarında")
devre_tel(s, (70, 80), (70, 40), (100, 40))
devre_anahtar(s, 100, 40, 140, 40, kapali=True, govde=30)
devre_tel(s, (140, 40), (170, 40))
devre_sigorta(s, 170, 40, 220, 40, govde=36)
devre_tel(s, (220, 40), (310, 40), (310, 76))
devre_lamba(s, 310, 76, 310, 112)
devre_tel(s, (310, 112), (310, 145), (70, 145), (70, 116))
devre_pil(s, 70, 80, 70, 116, arti=1, yan=1)
devre_tel(s, (70, 64), (26, 64), (26, 78), renk=OLCU_C, kal=1.6)
devre_olcu(s, 26, 78, 26, 122, "V", renk=OLCU_C)
devre_tel(s, (26, 122), (26, 132), (70, 132), renk=OLCU_C, kal=1.6)
devre_dugum(s, 70, 64, renk=OLCU_C); devre_dugum(s, 70, 132, renk=OLCU_C)
s.yazi(26, 52, "12 V", 13, renk=KIRMIZI, kalin=True)
s.yazi(120, 62, "Switch", 12); s.yazi(195, 62, "Fuse", 12)
s.yazi(90, 102, "Battery", 12, hiza="start"); s.yazi(294, 98, "Globe", 12, hiza="end")
s.cizgi(16, 165, 344, 165, GRI_C, 1)
# ortadaki şekil
devre_tel(s, (110, 190), (110, 290)); devre_tel(s, (250, 190), (250, 290))
devre_tel(s, (110, 190), (160, 190)); devre_lamba(s, 160, 190, 200, 190); devre_tel(s, (200, 190), (250, 190))
devre_tel(s, (110, 240), (158, 240)); devre_olcu(s, 158, 240, 202, 240, "V"); devre_tel(s, (202, 240), (250, 240))
devre_tel(s, (110, 290), (165, 290)); devre_pil(s, 165, 290, 195, 290, arti=-1, yan=-1); devre_tel(s, (195, 290), (250, 290))
s.cizgi(16, 320, 344, 320, GRI_C, 1)
# sağdaki şekil
devre_tel(s, (40, 380), (40, 345), (80, 345))
devre_anahtar(s, 80, 345, 120, 345, kapali=True, govde=30)
devre_tel(s, (120, 345), (170, 345))
devre_sigorta(s, 170, 345, 220, 345, govde=36)
devre_tel(s, (220, 345), (310, 345), (310, 385))
devre_lamba(s, 310, 385, 310, 421)
devre_tel(s, (310, 421), (310, 448)); devre_toprak(s, 310, 448)
devre_pil(s, 40, 380, 40, 414, arti=1, yan=1)
devre_tel(s, (40, 414), (40, 448)); devre_toprak(s, 40, 448)
devre_tel(s, (40, 428), (80, 428), (80, 480), (150, 480), renk=OLCU_C, kal=1.6)
devre_olcu(s, 150, 480, 194, 480, "V", renk=OLCU_C)
devre_tel(s, (194, 480), (250, 480), (250, 372), (310, 372), renk=OLCU_C, kal=1.6)
devre_dugum(s, 40, 428, renk=OLCU_C); devre_dugum(s, 310, 372, renk=OLCU_C)
s.yazi(144, 470, "−", 14, renk=OLCU_C, kalin=True); s.yazi(200, 470, "+", 14, renk=OLCU_C, kalin=True)
s.yazi(172, 508, "12 V", 13, renk=KIRMIZI, kalin=True)
s.yazi(100, 367, "Switch", 12); s.yazi(195, 367, "Fuse", 12)
s.yazi(60, 402, "Battery", 12, hiza="start"); s.yazi(294, 410, "Globe", 12, hiza="end")
s.kaydet("olcme-voltmetre.svg")

# ---------------------------------------------------------------- P06-4) olcme-ohmmetre
# Slayt 88, "Measuring resistance of a globe": lambanın iki ucu devreden ayrılmış (tellerde boşluk),
# ohmmetre (6 Ω) lambanın iki ucuna bağlı.
s = Sekil(360, 200, "Lambanın direncinin ölçülmesi: lamba devreden ayrılmış, ohmmetre lambanın iki ucuna bağlı (6 Ω)")
devre_tel(s, (40, 80), (40, 35), (80, 35))
devre_anahtar(s, 80, 35, 120, 35, kapali=True, govde=30)
devre_tel(s, (120, 35), (170, 35))
devre_sigorta(s, 170, 35, 220, 35, govde=36)
devre_tel(s, (220, 35), (300, 35), (300, 62))
devre_lamba(s, 300, 76, 300, 112)
devre_tel(s, (300, 126), (300, 146)); devre_toprak(s, 300, 146)
devre_pil(s, 40, 80, 40, 114, arti=1, yan=1)
devre_tel(s, (40, 114), (40, 146)); devre_toprak(s, 40, 146)
devre_tel(s, (300, 76), (250, 76), renk=OLCU_C, kal=1.6)
devre_olcu(s, 250, 76, 250, 112, "Ω", renk=OLCU_C)
devre_tel(s, (250, 112), (300, 112), renk=OLCU_C, kal=1.6)
devre_dugum(s, 300, 76, renk=OLCU_C); devre_dugum(s, 300, 112, renk=OLCU_C)
s.yazi(234, 99, "6 Ω", 13, renk=KIRMIZI, kalin=True, hiza="end")
s.yazi(100, 57, "Switch", 12); s.yazi(195, 57, "Fuse", 12)
s.yazi(60, 100, "Battery", 12, hiza="start"); s.yazi(316, 99, "Globe", 12, hiza="start")
s.yazi(180, 186, "Measuring resistance of a globe", 12, renk=SONUK, egik=True)
s.kaydet("olcme-ohmmetre.svg")

# ---------------------------------------------------------------- P06-5) olcme-vir-ucgeni
# Slayt 88: üç üçgen; üstte V, altta solda I, sağda R. Her üçgende bulunacak harf daire içinde,
# altında formülü: V = I x R, I = V / R, R = V / I (bölmeler slayttaki gibi kesir çizgisiyle).
s = Sekil(360, 190, "V, I, R üçgenleri: V = I × R, I = V / R, R = V / I")
for i, (cx, bilinmeyen) in enumerate(((62, "V"), (180, "I"), (298, "R"))):
    ust, orta, alt = 14, 58, 102
    _devre_cokgen(s, [(cx, ust), (cx - 22, orta), (cx + 22, orta)], "#FFF7C2", DEVRE_C, 2.4)
    _devre_cokgen(s, [(cx - 22, orta), (cx, orta), (cx, alt), (cx - 44, alt)], "#F9D5D5", DEVRE_C, 2.4)
    _devre_cokgen(s, [(cx, orta), (cx + 22, orta), (cx + 44, alt), (cx, alt)], "#DCDDF7", DEVRE_C, 2.4)
    for harf, x, y in (("V", cx, 51), ("I", cx - 17, 89), ("R", cx + 17, 89)):
        if harf == bilinmeyen:
            s.ekle('<circle cx="%.1f" cy="%.1f" r="11" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % (x, y - 6, DEVRE_C))
        s.yazi(x, y, harf, 17, kalin=True)
    if bilinmeyen == "V":
        s.yazi(cx, 150, "V = I × R", 17, kalin=True)
    else:
        pay, payda = ("V", "R") if bilinmeyen == "I" else ("V", "I")
        s.yazi(cx - 14, 150, bilinmeyen + " =", 17, kalin=True)
        s.yazi(cx + 18, 136, pay, 17, kalin=True)
        s.cizgi(cx + 9, 143, cx + 27, 143, DEVRE_C, 1.6)
        s.yazi(cx + 18, 163, payda, 17, kalin=True)
s.kaydet("olcme-vir-ucgeni.svg")

# ---------------------------------------------------------------- P06-6) olcme-emk
# Slayt 89: Şekil-1 kaynak (E) ve uçlarındaki voltmetre "Kaynağın emk"; Şekil-2 açık devre (S açık, Yük),
# kaynağın uçlarındaki voltmetre "Kaynağın emk"; Şekil-3 kapalı devre (S kapalı), yükün uçlarındaki ve
# kaynağın uçlarındaki voltmetrelerin ikisi de "Kaynağın Gerilimi". Slaytta yan yana; telefonda alt alta.
s = Sekil(360, 610, "EMK: Şekil-1 kaynağın emk'sı, Şekil-2 açık devrede kaynağın emk'sı, Şekil-3 kapalı devrede kaynağın gerilimi")
# Şekil-1
devre_tel(s, (210, 20), (110, 20), (110, 68))
devre_pil(s, 110, 68, 110, 102, arti=1, yan=-1)
devre_tel(s, (110, 102), (110, 150), (210, 150))
devre_tel(s, (210, 20), (210, 63), renk=OLCU_C, kal=1.6)
devre_olcu(s, 210, 63, 210, 107, "V", renk=OLCU_C)
devre_tel(s, (210, 107), (210, 150), renk=OLCU_C, kal=1.6)
devre_dugum(s, 210, 20, renk=OLCU_C); devre_dugum(s, 210, 150, renk=OLCU_C)
s.yazi(86, 80, "E", 15)
s.yazi(230, 80, "Kaynağın", 13, renk=KIRMIZI, hiza="start"); s.yazi(230, 96, "emk", 13, renk=KIRMIZI, hiza="start")
s.yazi(180, 180, "(Şekil-1)", 14)
s.cizgi(16, 194, 344, 194, GRI_C, 1)
# Şekil-2
y0 = 200
devre_tel(s, (165, y0 + 105), (60, y0 + 105), (60, y0 + 25), (130, y0 + 25))
devre_anahtar(s, 130, y0 + 25, 170, y0 + 25, kapali=False, govde=26)
devre_tel(s, (170, y0 + 25), (195, y0 + 25))
devre_direnc(s, 195, y0 + 25, 255, y0 + 25, bicim="kutu", govde=38, en=12)
devre_tel(s, (255, y0 + 25), (300, y0 + 25), (300, y0 + 105), (195, y0 + 105))
devre_pil(s, 165, y0 + 105, 195, y0 + 105, arti=1, yan=-1)
devre_tel(s, (140, y0 + 105), (140, y0 + 150), (158, y0 + 150), renk=OLCU_C, kal=1.6)
devre_olcu(s, 158, y0 + 150, 202, y0 + 150, "V", renk=OLCU_C)
devre_tel(s, (202, y0 + 150), (220, y0 + 150), (220, y0 + 105), renk=OLCU_C, kal=1.6)
devre_dugum(s, 140, y0 + 105, renk=OLCU_C); devre_dugum(s, 220, y0 + 105, renk=OLCU_C)
s.yazi(150, y0 + 10, "S", 14); s.yazi(225, y0 + 50, "Yük", 13)
s.yazi(126, y0 + 92, "E", 15)
s.yazi(232, y0 + 146, "Kaynağın", 13, renk=KIRMIZI, hiza="start"); s.yazi(232, y0 + 162, "emk", 13, renk=KIRMIZI, hiza="start")
s.yazi(180, y0 + 186, "(Şekil-2)", 14)
s.cizgi(16, y0 + 200, 344, y0 + 200, GRI_C, 1)
# Şekil-3
y0 = 406
devre_tel(s, (100, y0 + 112), (30, y0 + 112), (30, y0 + 25), (100, y0 + 25))
devre_anahtar(s, 100, y0 + 25, 140, y0 + 25, kapali=True, govde=26)
devre_tel(s, (140, y0 + 25), (215, y0 + 25), (215, y0 + 50))
devre_direnc(s, 215, y0 + 50, 215, y0 + 88, bicim="kutu", govde=36, en=12)
devre_tel(s, (215, y0 + 88), (215, y0 + 112), (130, y0 + 112))
devre_pil(s, 100, y0 + 112, 130, y0 + 112, arti=1, yan=-1)
devre_tel(s, (215, y0 + 40), (252, y0 + 40), (252, y0 + 47), renk=OLCU_C, kal=1.6)
devre_olcu(s, 252, y0 + 47, 252, y0 + 91, "V", renk=OLCU_C)
devre_tel(s, (252, y0 + 91), (252, y0 + 98), (215, y0 + 98), renk=OLCU_C, kal=1.6)
devre_dugum(s, 215, y0 + 40, renk=OLCU_C); devre_dugum(s, 215, y0 + 98, renk=OLCU_C)
devre_tel(s, (80, y0 + 112), (80, y0 + 155), (93, y0 + 155), renk=OLCU_C, kal=1.6)
devre_olcu(s, 93, y0 + 155, 137, y0 + 155, "V", renk=OLCU_C)
devre_tel(s, (137, y0 + 155), (150, y0 + 155), (150, y0 + 112), renk=OLCU_C, kal=1.6)
devre_dugum(s, 80, y0 + 112, renk=OLCU_C); devre_dugum(s, 150, y0 + 112, renk=OLCU_C)
s.yazi(120, y0 + 10, "S", 14); s.yazi(203, y0 + 74, "Yük", 13, hiza="end")
s.yazi(70, y0 + 99, "E", 15)
s.yazi(270, y0 + 66, "Kaynağın", 13, renk=KIRMIZI, hiza="start"); s.yazi(270, y0 + 82, "Gerilimi", 13, renk=KIRMIZI, hiza="start")
s.yazi(162, y0 + 151, "Kaynağın", 13, renk=KIRMIZI, hiza="start"); s.yazi(162, y0 + 167, "Gerilimi", 13, renk=KIRMIZI, hiza="start")
s.yazi(180, y0 + 196, "(Şekil-3)", 14)
s.kaydet("olcme-emk.svg")

# ================================================================ P07 ŞEKİLLERİ (slayt 96–105)
# Grafikler (slayt 96–97) eğrilerin değerleri 220 dpi resimden okunarak çizildi. Devre sembolleri
# 01-devre.py'dendir (P07 yalnızca devre_ac_kaynak'ı ekledi). Slayt 99 ve sonrasında hoca dirençleri
# zikzak, pili tek hücre (uzun (+) ve kısa (−) levha) olarak çizer. Slaytlarda yan yana duran şekiller
# telefonda alt alta çizildi.

P07_DOLGU = "#9FB3CF"; P07_DALGA = "#2B6CB0"; P07_DALGA_D = "#EEEAF6"; P07_KIRMIZI = "#C53030"

def p07_grafik(s, ox, oy, kx, ky, tmax, ymin, ymax, t_ust=10.8, izgara=False, kesik_dikey=None):
    """i(A)–t(sn) ekseni. (ox, oy): orijin; kx: 1 saniyenin, ky: 1 amperin piksel karşılığı.
    Dönen işlev (t, i) değerini SVG noktasına çevirir."""
    def P(t, i):
        return (ox + t * kx, oy - i * ky)
    if izgara:
        for t in range(1, tmax + 1):
            s.cizgi(P(t, ymin)[0], P(t, ymin)[1], P(t, ymax - 1)[0], P(t, ymax - 1)[1], "#B8C2CF", 0.8, kesik=True)
        for i in range(ymin, ymax):
            if i != 0:
                s.cizgi(P(0, i)[0], P(0, i)[1], P(t_ust - 0.5, i)[0], P(t_ust - 0.5, i)[1], "#B8C2CF", 0.8, kesik=True)
    if kesik_dikey is not None:
        for t in range(1, tmax + 1):
            s.cizgi(P(t, 0)[0], P(t, 0)[1] - 3, P(t, kesik_dikey)[0], P(t, kesik_dikey)[1] + 3, "#9FB3CF", 1, kesik=True)
    # eksenler
    s.ok(P(0, ymin - 0.6)[0], P(0, ymin - 0.6)[1], P(0, ymax + 0.6)[0], P(0, ymax + 0.6)[1], DEVRE_C, 1.6)
    if ymin < 0:
        s.ok(P(0, 0)[0], P(0, 0)[1] + 1, P(0, ymin - 0.6)[0], P(0, ymin - 0.6)[1], DEVRE_C, 1.6)
    s.ok(P(-0.6, 0)[0], P(-0.6, 0)[1], P(t_ust, 0)[0], P(t_ust, 0)[1], DEVRE_C, 1.6)
    for t in range(1, tmax + 1):
        x, y = P(t, 0)
        s.cizgi(x, y - 3, x, y + 3, DEVRE_C, 1.2)
        s.yazi(x, y + 15, str(t), 11)
    for i in range(ymin, ymax + 1):
        if i == 0:
            continue
        x, y = P(0, i)
        s.cizgi(x - 3, y, x + 3, y, DEVRE_C, 1.2)
        s.yazi(x - 6, y + 4, str(i) if i > 0 else "−%d" % -i, 11, hiza="end")
    s.yazi(P(0, ymax + 0.6)[0] + 8, P(0, ymax + 0.6)[1] + 10, "i (A)", 12, hiza="start")
    s.yazi(P(t_ust, 0)[0] + 4, P(t_ust, 0)[1] + 4, "t (sn)", 12, hiza="start")
    return P

def p07_egri(s, P, fonk, t1, t2, n=200, renk=DEVRE_C, kal=2):
    nok = [P(t1 + (t2 - t1) * k / n, fonk(t1 + (t2 - t1) * k / n)) for k in range(n + 1)]
    s.ekle('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in nok), renk, kal))
    return nok

def p07_alt_yazi(s, x, y, kalin_kisim, devami, boy=13):
    """Slayttaki gibi "Şekil (a) Düzgün DC Akım Eğrisi": ilk kısım kalın, hepsi mavi."""
    s.ekle('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" text-anchor="middle">'
           '<tspan font-weight="600">%s</tspan> %s</text>' % (x, y, FONT, boy, CIZGI, esc(kalin_kisim), esc(devami)))

# ---------------------------------------------------------------- P07-1) akim-dc-egrileri
# Slayt 96: Şekil (a) düzgün DC: 0–10 sn boyunca 2 A (her saniyede 2 A'e kadar kesik dikey çizgi).
# "VEYA" ve çift ok. Şekil (b): birinci eğri 1 A ile 3 A arasında dalgalanır (t = 0'da 2 A, tepeler
# yaklaşık 0,8 / 4 / 7,2 sn'de 3 A, çukurlar 2,4 / 5,6 / 8,8 sn'de 1 A); ikinci eğri her 2 saniyede
# −3 A'den −5 A'e iner ve dikey olarak −3 A'e döner (2, 4, 6, 8, 10 sn'de).
s = Sekil(360, 580, "Şekil (a) düzgün DC akım eğrisi: akım her an 2 A; Şekil (b) iki farklı değişken DC akım eğrisi: biri pozitif, biri negatif değerde")
P = p07_grafik(s, 46, 190, 26, 28, 10, 0, 5, kesik_dikey=2)
p07_egri(s, P, lambda t: 2, 0, 10)
s.yazi(P(0, 0)[0] - 6, P(0, 0)[1] + 15, "0", 11, hiza="end")
p07_alt_yazi(s, 180, 232, "Şekil (a)", "Düzgün DC Akım Eğrisi")
s.yazi(180, 268, "VEYA", 14, TURUNCU, kalin=True)
s.ok(180, 274, 180, 290, CIZGI, 2.4); s.ok(180, 258, 180, 246, CIZGI, 2.4)
P = p07_grafik(s, 46, 420, 26, 21, 10, -5, 5)
p07_egri(s, P, lambda t: 2 + math.sin(2 * math.pi * t / 3.2), 0, 10.3)
def _p07_testere(t):
    u = (t % 2.0) / 2.0
    return -3 - 2 * (1 - math.sqrt(max(0.0, 1 - u * u)))
for k in range(5):
    p07_egri(s, P, _p07_testere, 2 * k, 2 * k + 1.999, n=80, kal=2.4)
    a, b = P(2 * k + 2, -5), P(2 * k + 2, -3)
    s.cizgi(a[0], a[1], b[0], b[1], DEVRE_C, 2.4)
p07_egri(s, P, _p07_testere, 10, 10.7, n=20, kal=2.4)
p07_alt_yazi(s, 180, 568, "Şekil (b)", "Farklı Değişken DC Akım Eğrileri")
s.kaydet("akim-dc-egrileri.svg")

# ---------------------------------------------------------------- P07-2) akim-ac-egrisi
# Slayt 97 sağ üst: i = 3 · sin(2π · t / 8): 2 sn'de 3 A, 4 sn'de 0, 6 sn'de −3 A, 8 sn'de 0, 10 sn'de 3 A.
# Eğri ile eksen arası dolu; "Pozitif alternans" çizgisi 2 sn'deki tepeye, "Negatif alternans" 6 sn'deki çukura.
s = Sekil(360, 300, "Alternatif akım eğrisi: akım 0'dan 3 A'e çıkar, 4. saniyede sıfırdan geçer, 6. saniyede −3 A olur; üstteki yarım dalga pozitif alternans, alttaki negatif alternans")
P = p07_grafik(s, 46, 150, 26, 22, 10, -5, 5, izgara=True)
f = lambda t: 3 * math.sin(2 * math.pi * t / 8)
nok = [P(8 * k / 160, f(8 * k / 160)) for k in range(161)]
s.ekle('<polygon points="%.1f,%.1f %s %.1f,%.1f" fill="%s" fill-opacity="0.75" stroke="none"/>' % (
    P(0, 0)[0], P(0, 0)[1], " ".join("%.1f,%.1f" % q for q in nok), P(8, 0)[0], P(8, 0)[1], P07_DOLGU))
p07_egri(s, P, f, 0, 10.5, kal=2.4)
s.cizgi(P(2, 3)[0], P(2, 3)[1], P(2, 4.3)[0], P(2, 4.3)[1], DEVRE_C, 1.4)
s.cizgi(P(2, 3)[0], P(2, 3)[1], P(2, 1.8)[0], P(2, 1.8)[1], DEVRE_C, 1.4)
s.yazi(P(0.5, 4.45)[0], P(0.5, 4.45)[1], "Pozitif alternans", 13, hiza="start")
s.cizgi(P(6, -3)[0], P(6, -3)[1], P(6, -4.4)[0], P(6, -4.4)[1], DEVRE_C, 1.4)
s.cizgi(P(6, -3)[0], P(6, -3)[1], P(6, -1.8)[0], P(6, -1.8)[1], DEVRE_C, 1.4)
s.yazi(P(6, -5.3)[0], P(6, -5.3)[1], "Negatif alternans", 13)
s.yazi(P(0, 0)[0] - 18, P(0, 0)[1] + 4, "0", 11, hiza="end")
s.kaydet("akim-ac-egrisi.svg")

# ---------------------------------------------------------------- P07-3) akim-dalga-bicimleri
# Slayt 97 sağ alt: Sinüs dalgası (iki dalga), Kompleks dalga (bir dalga; tepelerde çukur),
# Üçgen dalga (iki dalga), Kare dalga (iki dalga, +V'den başlar). Eksende +V, 0, −V.
s = Sekil(360, 330, "Dalga biçimleri: sinüs dalgası, kompleks dalga, üçgen dalga, kare dalga")
def _p07_panel(x0, y0, ad, fonk, kare=False):
    g, h = 134, 52            # çizim genişliği, genliğin piksel karşılığı
    s.yazi(x0 + 26 + g / 2, y0 - 6, ad, 12)
    oy = y0 + 62
    s.cizgi(x0 + 26, y0 + 2, x0 + 26, oy + h + 8, SONUK, 1.2)
    s.ok(x0 + 26, oy, x0 + 26 + g + 12, oy, SONUK, 1.2)
    s.yazi(x0 + 20, oy - h + 4, "+V", 11, hiza="end"); s.yazi(x0 + 20, oy + 4, "0", 11, hiza="end")
    s.yazi(x0 + 20, oy + h + 4, "−V", 11, hiza="end")
    if kare:
        nok = [(0, 0), (0, 1), (0.25, 1), (0.25, -1), (0.5, -1), (0.5, 1), (0.75, 1), (0.75, -1), (1, -1), (1, 0)]
    else:
        nok = [(k / 200, fonk(k / 200)) for k in range(201)]
    pts = [(x0 + 26 + g * u, oy - h * v) for u, v in nok]
    s.ekle('<polygon points="%s" fill="%s" stroke="none"/>' % (" ".join("%.1f,%.1f" % q for q in pts + [(x0 + 26 + g, oy)]), P07_DALGA_D))
    s.ekle('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts), P07_DALGA))
_komp_max = max(abs(math.sin(2 * math.pi * k / 400) + 0.28 * math.sin(6 * math.pi * k / 400)) for k in range(401))
_p07_panel(4, 30, "Sinüs dalgası", lambda u: math.sin(4 * math.pi * u))
_p07_panel(180, 30, "Kompleks dalga", lambda u: (math.sin(2 * math.pi * u) + 0.28 * math.sin(6 * math.pi * u)) / _komp_max)
def _p07_ucgen(u):
    v = (8 * u) % 1.0; k = int(8 * u) % 4
    return [v, 1 - v, -v, -1 + v][k] if u < 1 else 0
_p07_panel(4, 190, "Üçgen dalga", _p07_ucgen)
_p07_panel(180, 190, "Kare dalga", None, kare=True)
s.kaydet("akim-dalga-bicimleri.svg")

# ---------------------------------------------------------------- P07-4) akim-uretim-iletim
# Slayt 97 sol alt: SANTRAL → (ALÇAK GERİLİM) → YÜKSELTME TRAFO → YÜKSEK GERİLİM hattı (direkler) →
# DÜŞÜRME TRAFO → (ALÇAK GERİLİM) → EV YA DA İŞ; hat kesik çizgiyle DİĞER KULLANICILAR'a devam eder.
# Yazılar ve renkler slayttaki gibi (YÜKSELTME TRAFO kahverengi, DÜŞÜRME TRAFO yeşil, alt yazı mavi).
def p07_sargi(s, x, y, n, r, dikey, yon=1, renk=DEVRE_C):
    """(x, y)'den başlayan n halkalı sargı; dikey=True ise aşağı doğru, halkalar yon (+1 sağa / −1 sola)
    tarafına; dikey=False ise sağa doğru, halkalar yon (+1 aşağı / −1 yukarı) tarafına."""
    d = "M %.1f %.1f " % (x, y)
    for k in range(n):
        if dikey:
            d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (r, r, 1 if yon > 0 else 0, x, y + 2 * r * (k + 1))
        else:
            d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (r, r, 1 if yon > 0 else 0, x + 2 * r * (k + 1), y)
    s.ekle('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (d, renk))

s = Sekil(360, 400, "Alternatif akımın üretimi ve evlerimize kadar iletimi: santral, yükseltme trafosu, yüksek gerilim hattı, düşürme trafosu, ev ya da iş")
KAHVE = "#8B4513"
# santral (baca + kutu)
s.ekle('<rect x="10" y="62" width="12" height="70" rx="6" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % DEVRE_C)
s.ekle('<rect x="16" y="98" width="58" height="34" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % DEVRE_C)
s.ekle('<polygon points="16,98 30,86 88,86 74,98" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % DEVRE_C)
s.ekle('<polygon points="74,98 88,86 88,120 74,132" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % DEVRE_C)
s.yazi(30, 78, "SANTRAL", 12, hiza="start")
# santral → yükseltme trafosu: iki tel santralden düz çıkıp primer sargının iki ucuna girer;
# primer ve sekonder dikey üçer halkalı sargı, aralarında iki demir çekirdek çizgisi
devre_dugum(s, 82, 96, 2.6); devre_dugum(s, 82, 124, 2.6)
devre_tel(s, (82, 96), (104, 96), kal=1.6)
devre_tel(s, (82, 124), (104, 124), kal=1.6)
p07_sargi(s, 104, 96, 3, 14 / 3, True, 1)
for x in (118, 122):
    s.cizgi(x, 88, x, 132, DEVRE_C, 1.6)
p07_sargi(s, 136, 96, 3, 14 / 3, True, -1)
s.yazi(122, 40, "YÜKSELTME", 12, KAHVE, kalin=True); s.yazi(122, 55, "TRAFO", 12, KAHVE, kalin=True)
s.yazi(64, 160, "ALÇAK GERİLİM", 12)
s.cizgi(80, 148, 94, 128, SONUK, 1)
# direkler ve iki iletken
direk = [170, 238, 306]
for x in direk:
    s.cizgi(x, 70, x, 170, DEVRE_C, 2.4)
    s.cizgi(x - 10, 84, x + 10, 66, DEVRE_C, 1.8)
ust = [(136, 96)] + [(x + 10, 66) for x in direk]
alt = [(136, 124)] + [(x - 10, 84) for x in direk]
for hat in (ust, alt):
    for (xa, ya), (xb, yb) in zip(hat, hat[1:]):
        s.ekle('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>' % (
            xa, ya, (xa + xb) / 2, max(ya, yb) + 12, xb, yb, DEVRE_C))
s.ekle('<path d="M 316 66 Q 334 78 352 74" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="5 4"/>' % DEVRE_C)
s.ekle('<path d="M 296 84 Q 326 98 352 92" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="5 4"/>' % DEVRE_C)
for x in direk:
    devre_dugum(s, x + 10, 66, 2.6); devre_dugum(s, x - 10, 84, 2.6)
s.yazi(236, 24, "YÜKSEK GERİLİM", 12)
s.ok(236, 30, 258, 72, SONUK, 1)
s.yazi(354, 196, "DİĞER", 12, hiza="end"); s.yazi(354, 212, "KULLANICILAR", 12, hiza="end")
s.cizgi(306, 172, 306, 180, DEVRE_C, 2.4)
# hattan düşürme trafosuna (ortadaki direkten aşağı)
devre_tel(s, (228, 84), (222, 96), (222, 222), (226, 222), kal=1.4)
devre_tel(s, (248, 66), (256, 96), (256, 222), (252, 222), kal=1.4)
p07_sargi(s, 226, 222, 3, 4.3, False, 1)
for y in (234, 239):
    s.cizgi(218, y, 260, y, DEVRE_C, 1.6)
p07_sargi(s, 226, 251, 3, 4.3, False, -1)
s.yazi(178, 236, "DÜŞÜRME", 12, YESIL, kalin=True, hiza="end"); s.yazi(178, 252, "TRAFO", 12, YESIL, kalin=True, hiza="end")
# ev ya da iş
devre_tel(s, (226, 251), (218, 260), (218, 300), (228, 318), kal=1.4)
devre_tel(s, (252, 251), (262, 262), (262, 330), (240, 334), kal=1.4)
s.ekle('<rect x="200" y="314" width="40" height="30" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % DEVRE_C)
s.ekle('<polygon points="200,314 210,304 250,304 240,314" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % DEVRE_C)
s.ekle('<polygon points="240,314 250,304 250,334 240,344" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % DEVRE_C)
devre_dugum(s, 228, 318, 2.6); devre_dugum(s, 240, 334, 2.6)
s.yazi(194, 334, "EV YA DA İŞ", 12, hiza="end")
s.yazi(312, 298, "ALÇAK", 12); s.yazi(312, 314, "GERİLİM", 12)
s.ok(300, 284, 268, 268, SONUK, 1)
s.yazi(180, 372, "ALTERNATİF AKIMIN ÜRETİMİ VE", 13, CIZGI)
s.yazi(180, 390, "EVLERİMİZE KADAR İLETİMİ", 13, CIZGI)
s.kaydet("akim-uretim-iletim.svg")

# ---------------------------------------------------------------- P07-5) akim-dc-ac-devre
# Slayt 98: (DC) iki hücreli pil ((+) üstte) ve zikzak direnç; üst telde "→ I", alt telde "I ←".
# (AC) daire içinde sinüs işaretli kaynak ve zikzak direnç; üstte "← I - - →", altta "← - - I →"
# (düz ok bir yönü, kesik ok öteki yönü gösterir).
s = Sekil(360, 200, "Doğru akım devresinde akım tek yönde dolaşır; alternatif akım devresinde akımın yönü sürekli değişir")
def _p07_kesik_ok(x1, y, x2):
    s.cizgi(x1, y, x2 - 6 * (1 if x2 > x1 else -1), y, DEVRE_C, 1.4, kesik=True)
    devre_yon_oku(s, x2, y, x2 - x1, 0, DEVRE_C, 7)
def _p07_duz_ok(x1, y, x2):
    s.cizgi(x1, y, x2, y, DEVRE_C, 1.4)
    devre_yon_oku(s, x2, y, x2 - x1, 0, DEVRE_C, 7)
s.yazi(85, 24, "(DC)", 14)
devre_tel(s, (24, 84), (24, 62), (150, 62), (150, 82))
devre_batarya(s, 24, 84, 24, 118, hucre=2, arti=1, isaret=False, uzun=24, kisa=12, ara=7)
devre_tel(s, (24, 118), (24, 150), (150, 150), (150, 128))
devre_direnc(s, 150, 82, 150, 128, bicim="zikzak", govde=34, en=14)
_p07_duz_ok(66, 46, 88); s.yazi(96, 51, "I", 14, hiza="start")
_p07_duz_ok(102, 168, 80); s.yazi(74, 173, "I", 14, hiza="end")
s.yazi(270, 24, "(AC)", 14)
devre_tel(s, (210, 82), (210, 62), (336, 62), (336, 82))
devre_ac_kaynak(s, 210, 82, 210, 128)
devre_tel(s, (210, 128), (210, 150), (336, 150), (336, 128))
devre_direnc(s, 336, 82, 336, 128, bicim="zikzak", govde=34, en=14)
_p07_duz_ok(258, 46, 228); s.yazi(272, 51, "I", 14)
_p07_kesik_ok(286, 46, 318)
_p07_kesik_ok(258, 168, 228); s.yazi(272, 173, "I", 14)
_p07_duz_ok(286, 168, 318)
s.kaydet("akim-dc-ac-devre.svg")

# ================================================================ Direnç bağlantıları (slayt 99–105)
def p07_r(s, x1, y1, x2, y2, govde=30, en=12):
    return devre_direnc(s, x1, y1, x2, y2, bicim="zikzak", govde=govde, en=en)

def p07_kirmizi_cift_ok(s, x1, x2, y, etiket):
    s.yazi((x1 + x2) / 2, y + 5, etiket, 14, P07_KIRMIZI)
    s.ok((x1 + x2) / 2 - 16, y, x1 + 2, y, P07_KIRMIZI, 1.6)
    s.ok((x1 + x2) / 2 + 16, y, x2 - 2, y, P07_KIRMIZI, 1.6)

# ---------------------------------------------------------------- P07-6) direnc-seri-rt
# Slayt 99 sol alt (zikzaklı çizim; yanındaki direnç fotoğrafları çizilmedi): R1, R2, R3, ···, Rn
# art arda; iki uçtaki dikey çizgiler arasında kırmızı çift ok RT; kutuda RT = R1 + R2 + R3 + ··· + Rn.
s = Sekil(360, 170, "Seri bağlı dirençler: R1, R2, R3 ... Rn art arda; RT = R1 + R2 + R3 + ... + Rn")
x = 20
devre_tel(s, (20, 104), (20, 44), (34, 44))
for ad in ("R₁", "R₂", "R₃"):
    p07_r(s, x + 14, 44, x + 80, 44, govde=44)
    s.yazi(x + 47, 72, ad, 14)
    x += 66
devre_tel(s, (x + 14, 44), (x + 20, 44))
s.ekle('<line x1="%d" y1="44" x2="%d" y2="44" stroke="%s" stroke-width="2.4" stroke-dasharray="2 4" stroke-linecap="round"/>' % (x + 22, x + 44, DEVRE_C))
p07_r(s, x + 46, 44, x + 104, 44, govde=44)
s.yazi(x + 76, 28, "Rn", 14)
devre_tel(s, (x + 104, 44), (x + 112, 44), (x + 112, 104))
p07_kirmizi_cift_ok(s, 20, x + 112, 96, "RT")
s.ekle('<rect x="66" y="122" width="228" height="30" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>' % DEVRE_C)
s.yazi(180, 142, "RT = R₁ + R₂ + R₃ + ··· + Rn", 14)
s.kaydet("direnc-seri-rt.svg")

# ---------------------------------------------------------------- P07-7) direnc-seri-devre
# Slayt 99 orta: U pili ((+) üstte) solda; sağ kolda R1, R2, R3 seri, her birinin yanında U1, U2, U3
# (üst ucu +, alt ucu −); üst telde I oku sağa. "≡" ve eşdeğer devre: U pili ve Reş, üst telde I.
s = Sekil(360, 290, "Seri devre: U geriliminde R1, R2, R3 seri; dirençler üzerinde U1, U2, U3 düşer; eşdeğeri U ve Reş")
devre_tel(s, (40, 128), (40, 30), (150, 30), (150, 46))
devre_pil(s, 40, 128, 40, 150, arti=1, isaret=True, yan=-1, uzun=24, kisa=12)
devre_tel(s, (40, 150), (40, 268), (150, 268), (150, 246))
devre_yon_oku(s, 104, 30, 1, 0, DEVRE_C, 8); s.yazi(92, 52, "I", 15)
s.yazi(24, 144, "U", 15, hiza="end")
for k, (yu, ya) in enumerate(((46, 106), (116, 176), (186, 246))):
    p07_r(s, 150, yu, 150, ya, govde=40, en=14)
    s.yazi(134, (yu + ya) / 2 + 5, "R%s" % "₁₂₃"[k], 15, hiza="end")
    s.yazi(164, (yu + ya) / 2 + 5, "U%s" % "₁₂₃"[k], 15, hiza="start")
    s.yazi(166, yu + 12, "+", 13); s.yazi(166, ya - 2, "−", 13)
    if k < 2:
        devre_tel(s, (150, ya), (150, ya + 10))
s.yazi(212, 156, "≡", 30)
devre_tel(s, (252, 128), (252, 90), (336, 90), (336, 122))
devre_pil(s, 252, 128, 252, 150, arti=1, isaret=True, yan=-1, uzun=24, kisa=12)
devre_tel(s, (252, 150), (252, 196), (336, 196), (336, 168))
p07_r(s, 336, 122, 336, 168, govde=40, en=14)
devre_yon_oku(s, 300, 90, 1, 0, DEVRE_C, 8); s.yazi(290, 110, "I", 15)
s.yazi(240, 144, "U", 15, hiza="end"); s.yazi(322, 150, "Reş", 15, hiza="end")
s.kaydet("direnc-seri-devre.svg")

# ---------------------------------------------------------------- P07-8) direnc-seri-guc
# Slayt 101: üst telde dirençler (üstlerinde P, altlarında R), üçüncüden sonra noktalı tel ve son direnç;
# solda I oku yukarı; altta U pili ((+) solda, (−) sağda). Slayttaki son direnç "P3 / R3" diye
# yazılmıştır; formüldeki Pn'ye uygun olarak burada "Pn / Rn" yazıldı (notta Dikkat kutusunda söylenir).
s = Sekil(360, 210, "Seri devrede güç: R1, R2, R3 ... Rn seri; üstlerinde harcanan güçler P1, P2, P3 ... Pn; U kaynağı ve I akımı")
devre_tel(s, (20, 170), (20, 70), (28, 70))
x = 28
for k in range(3):
    p07_r(s, x, 70, x + 64, 70, govde=40)
    s.yazi(x + 32, 50, "P%s" % "₁₂₃"[k], 15); s.yazi(x + 32, 100, "R%s" % "₁₂₃"[k], 15)
    x += 64
s.ekle('<line x1="%d" y1="70" x2="%d" y2="70" stroke="%s" stroke-width="2.4" stroke-dasharray="2 4" stroke-linecap="round"/>' % (x + 2, x + 34, DEVRE_C))
p07_r(s, x + 36, 70, x + 100, 70, govde=40)
s.yazi(x + 68, 50, "Pn", 15); s.yazi(x + 68, 100, "Rn", 15)
devre_tel(s, (x + 100, 70), (340, 70), (340, 170), (190, 170))
devre_pil(s, 170, 170, 190, 170, arti=1, isaret=True, yan=-1, uzun=24, kisa=12)
devre_tel(s, (170, 170), (20, 170))
s.yazi(180, 202, "U", 15)
devre_yon_oku(s, 20, 118, 0, -1, DEVRE_C, 8); s.yazi(32, 130, "I", 15, hiza="start")
s.kaydet("direnc-seri-guc.svg")

# ---------------------------------------------------------------- P07-9) direnc-paralel-rt
# Slayt 103 sol alt (zikzaklı çizim; direnç fotoğrafları çizilmedi): R1, R2, R3 paralel; en üstte Rn
# noktalı bağlantıyla; dışarı çıkan kalın teller; altta kırmızı çift ok RT.
s = Sekil(360, 280, "Paralel bağlı dirençler: R1, R2, R3 ... Rn karşılıklı uçlarından bağlı; toplam direnç RT")
xs, xd = 130, 230
s.cizgi(xs, 40, xs, 100, DEVRE_C, 1.2, kesik=True); s.cizgi(xd, 40, xd, 100, DEVRE_C, 1.2, kesik=True)
p07_r(s, xs, 40, xd, 40, govde=70, en=16); s.yazi(180, 24, "Rn", 14)
for k, y in enumerate((196, 148, 100)):
    p07_r(s, xs, y, xd, y, govde=70, en=16)
    s.yazi(180, y + 28, "R%s" % "₁₂₃"[k], 14)
s.cizgi(xs, 100, xs, 196, DEVRE_C, DEVRE_KAL); s.cizgi(xd, 100, xd, 196, DEVRE_C, DEVRE_KAL)
devre_tel(s, (40, 256), (40, 100), (xs, 100), kal=3)
devre_tel(s, (320, 256), (320, 100), (xd, 100), kal=3)
p07_kirmizi_cift_ok(s, 40, 320, 246, "RT")
s.kaydet("direnc-paralel-rt.svg")

# ---------------------------------------------------------------- P07-10) direnc-paralel-devre
# Slayt 103 orta: U pili ((+) üstte) solda; üst telde I oku sağa; üç kol: I1, I2, I3 okları aşağı,
# R1, R2, R3 (solda ad, sağda U1, U2, U3; üst +, alt −). "≡" ve eşdeğer devre: U, Reş, I.
# Slaytta yan yana; telefonda eşdeğer devre altta.
s = Sekil(360, 370, "Paralel devre: U geriliminde R1, R2, R3 paralel; kol akımları I1, I2, I3, toplam akım I; dirençlerin gerilimleri U1, U2, U3; eşdeğeri U ve Reş")
devre_tel(s, (34, 112), (34, 40), (320, 40))
devre_pil(s, 34, 112, 34, 134, arti=1, isaret=True, yan=-1, uzun=24, kisa=12)
devre_tel(s, (34, 134), (34, 210), (320, 210))
devre_yon_oku(s, 80, 40, 1, 0, DEVRE_C, 8); s.yazi(76, 62, "I", 15)
s.yazi(18, 128, "U", 15, hiza="end")
for k, x in enumerate((130, 225, 320)):
    devre_tel(s, (x, 40), (x, 100))
    devre_yon_oku(s, x, 72, 0, 1, DEVRE_C, 8)
    s.yazi(x - 8, 70, "I%s" % "₁₂₃"[k], 14, hiza="end")
    p07_r(s, x, 100, x, 150, govde=38, en=14)
    devre_tel(s, (x, 150), (x, 210))
    if k < 2:
        devre_dugum(s, x, 40); devre_dugum(s, x, 210)
    s.yazi(x - 12, 130, "R%s" % "₁₂₃"[k], 14, hiza="end")
    s.yazi(x + 10, 130, "U%s" % "₁₂₃"[k], 14, hiza="start")
    s.yazi(x + 14, 104, "+", 12); s.yazi(x + 14, 162, "−", 12)
s.yazi(120, 302, "≡", 30)
devre_tel(s, (190, 286), (190, 250), (290, 250), (290, 268))
devre_pil(s, 190, 286, 190, 308, arti=1, isaret=True, yan=-1, uzun=24, kisa=12)
devre_tel(s, (190, 308), (190, 346), (290, 346), (290, 322))
p07_r(s, 290, 268, 290, 322, govde=40, en=14)
devre_yon_oku(s, 244, 250, 1, 0, DEVRE_C, 8); s.yazi(236, 272, "I", 15)
s.yazi(174, 302, "U", 15, hiza="end"); s.yazi(276, 300, "Reş", 15, hiza="end")
s.kaydet("direnc-paralel-devre.svg")

# ---------------------------------------------------------------- P07-11) direnc-paralel-guc
# Slayt 105: U pili ((+) üstte) solda; üst telde IT oku sağa; kollar R1/P1, R2/P2, R3/P3 (I1, I2, I3
# okları aşağı), noktalı tellerle son kol Rn/Pn (oksuz).
s = Sekil(360, 240, "Paralel devrede güç: U kaynağı, toplam akım IT; R1, R2, R3 ... Rn paralel kollarda P1, P2, P3 ... Pn güçleri; kol akımları I1, I2, I3")
devre_tel(s, (28, 108), (28, 36), (262, 36))
devre_pil(s, 28, 108, 28, 130, arti=1, isaret=True, yan=-1, uzun=24, kisa=12)
devre_tel(s, (28, 130), (28, 214), (262, 214))
for y in (36, 214):
    s.ekle('<line x1="266" y1="%d" x2="300" y2="%d" stroke="%s" stroke-width="2.4" stroke-dasharray="2 4" stroke-linecap="round"/>' % (y, y, DEVRE_C))
devre_tel(s, (304, 36), (318, 36), (318, 100)); devre_tel(s, (318, 154), (318, 214), (304, 214))
devre_yon_oku(s, 64, 36, 1, 0, DEVRE_C, 8); s.yazi(52, 58, "IT", 14)
s.yazi(14, 124, "U", 15, hiza="end")
for k, x in enumerate((100, 170, 240)):
    devre_tel(s, (x, 36), (x, 100))
    devre_yon_oku(s, x, 76, 0, 1, DEVRE_C, 8)
    s.yazi(x - 8, 74, "I%s" % "₁₂₃"[k], 14, hiza="end")
    p07_r(s, x, 100, x, 154, govde=40, en=14)
    devre_tel(s, (x, 154), (x, 214))
    devre_dugum(s, x, 36); devre_dugum(s, x, 214)
    s.yazi(x - 12, 132, "R%s" % "₁₂₃"[k], 14, hiza="end")
    s.yazi(x + 12, 132, "P%s" % "₁₂₃"[k], 14, hiza="start")
p07_r(s, 318, 100, 318, 154, govde=40, en=14)
s.yazi(306, 132, "Rn", 14, hiza="end"); s.yazi(330, 132, "Pn", 14, hiza="start")
s.kaydet("direnc-paralel-guc.svg")

print("tamam: " + HEDEF)

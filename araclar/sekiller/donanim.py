"""Bilgisayar Donanımı ders notlarının görsellerini üretir.

Kaynak fotoğraflar hocanın sunumundan (donanim_ders_notlari.pptx) çıkarılmıştır
ve araclar/sekiller/donanim-kaynak/ klasöründe durur. İki etiketli anakart resmini
Hamza ayrıca verdi: x58-etiketli-ham.png (hocanın 3. slaytındaki resmin büyük
hâli) ve asus-a8n-etiketli-ham.jpg (ASUS A8N-SLI; üç etiketi burada düzeltilir). Bu betik:
  1) kaynakları uygulamaya uygun adla ve boyutla gorseller/ klasörüne yazar,
  2) anakart fotoğrafında her elemanı kırmızı çerçeveyle işaretler ve
     o elemanın yakın görünümünü (yine işaretli) ayrı bir görsel olarak üretir.
     Sorularda bu ikisi yana kaydırılarak birlikte gösterilir.

Kullanım: python3 araclar/sekiller/donanim.py icerik/dersler/donanim/gorseller
"""
import os
import sys
from PIL import Image, ImageDraw

KAYNAK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "donanim-kaynak")
HEDEF = sys.argv[1]
os.makedirs(HEDEF, exist_ok=True)
KALITE = 78

# kaynak dosya → görsel adı (uzantı .jpg; şeffaflık yok)
KOPYALAR = {
    "s02-Picture_2.jpg": "anakart-genel.jpg",
    "s14-Picture_2.jpg": "anakart-numarali.jpg",
    "s13-arka.jpg": "arka-panel-numarali.jpg",
    "s45-Picture_2.png": "kuzey-guney-koprusu.jpg",
    "s07-Picture_2.jpg": "ilk-anakart.jpg",
    "s09-Picture_2.jpg": "xt-anakart.jpg",
    "s10-Picture_2.jpg": "at-anakart.jpg",
    "s11-Picture_2.jpg": "atx-anakart.jpg",
    "s15-Picture_2.jpg": "ps2-fisler.jpg",
    "s15-Picture_3.jpg": "ps2-takma.jpg",
    "s16-Picture_2.jpg": "paralel-kablo.jpg",
    "s16-Picture_3.jpg": "paralel-port.jpg",
    "s17-Picture_6.jpg": "com-ve-ekran-portu.jpg",
    "s17-Picture_7.jpg": "ekran-kablosu.jpg",
    "s18-Picture_2.jpg": "usb-takma.jpg",
    "s18-Picture_3.jpg": "usb-portlar.jpg",
    "s19-Picture_2.jpg": "lan-port.jpg",
    "s19-Picture_3.jpg": "lan-kasa.jpg",
    "s20-Picture_2.jpg": "pci-yuvalari.jpg",
    "s20-Picture_3.jpg": "pci-yuvalari-yakin.jpg",
    "s21-Picture_5.jpg": "pcie-kart.jpg",
    "s21-Picture_6.jpg": "pcie-yuvalari.jpg",
    "s22-Picture_2.jpg": "pcie-x16-yuvalari.jpg",
    "s22-Picture_3.gif": "yuva-karsilastirma.jpg",
    "s23-Picture_2.jpg": "agp-yuvasi.jpg",
    "s24-Picture_2.jpg": "ide-kablo.jpg",
    "s24-Picture_3.jpg": "ide-yuvasi.jpg",
    "s25-Picture_2.jpg": "sata-kablo.jpg",
    "s25-Picture_3.jpg": "sata-yuvalari.jpg",
    "s26-Picture_3.png": "disket-yuvasi.jpg",
    "s26-Picture_4.jpg": "disket-kablosu.jpg",
    "s27-Picture_3.jpg": "guc-fisi.jpg",
    "s27-Picture_4.png": "guc-yuvasi.jpg",
    "s28-Picture_2.jpg": "ram-modulleri.jpg",
    "s28-Picture_3.jpg": "ram-yuvalari.jpg",
    "s31-Resim_3.jpg": "ddr2.jpg",
    "s32-Resim_3.jpg": "ddr3.jpg",
    "s33-Resim_3.jpg": "ddr4.jpg",
    "s35-Resim_3.jpg": "ilk-ram.jpg",
    "s36-Picture_5.jpg": "rom-bios-yongasi.jpg",
    "s37-Picture_3.jpg": "rom-yongasi.jpg",
    "s38-Picture_2.gif": "eprom.jpg",
    "s39-Picture_2.jpg": "eeprom-bellek-uzerinde.jpg",
    "s39-Picture_3.jpg": "eeprom.jpg",
    "s41-Picture_2.jpg": "islemci-yuvasi.jpg",
    "s41-Picture_3.jpg": "islemciler.jpg",
    "s43-Resim_4.jpg": "intel-4004.jpg",
    "s44-Picture_2.jpg": "bios-pili.jpg",
}


def ac(ad):
    im = Image.open(os.path.join(KAYNAK, ad))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        zemin = Image.new("RGB", im.size, (255, 255, 255))
        zemin.paste(im, mask=im.split()[-1])
        return zemin
    return im.convert("RGB")


def kaydet(im, ad):
    if ad.endswith(".webp"):
        im.save(os.path.join(HEDEF, ad), "WEBP", quality=80, method=6)
    else:
        im.save(os.path.join(HEDEF, ad), "JPEG", quality=KALITE, optimize=True, progressive=True)


for kaynak, ad in KOPYALAR.items():
    kaydet(ac(kaynak), ad)

# ------------------------------------------------------------ işaretli anakart
# Fotoğraf: hocanın 2. slaytındaki Gigabyte GA-8I945P-G anakartı (984 × 744).
# Kutular piksel olarak (sol, üst, sağ, alt); bir elemanın birden çok kutusu olabilir.
ANAKART = "s02-Picture_2.jpg"
ELEMANLAR = {
    "pci": [(50, 148, 222, 428)],
    "pcie-x1": [(250, 168, 284, 256), (316, 168, 350, 256)],
    "pcie-x16": [(372, 168, 404, 496)],
    "ide": [(476, 684, 664, 724), (126, 650, 307, 720)],
    "sata": [(206, 576, 327, 644)],
    "disket": [(662, 686, 832, 724)],
    "guc": [(674, 636, 824, 680)],
    "ram": [(438, 486, 910, 630)],
    "islemci-yuvasi": [(693, 198, 857, 394)],
    "kuzey-koprusu": [(460, 250, 614, 400)],
    "guney-koprusu": [(246, 446, 354, 550)],
    "bios-pili": [(46, 623, 117, 702)],
}
KIRMIZI, BEYAZ = (229, 30, 37), (255, 255, 255)


def isaretle(im, kutular, olcek=1.0, kalin=1.0):
    """Kutular olcek ile büyütülür; çizgi kalınlığı görselin telefonda
    küçültülme oranına göre kalin ile ayarlanır (tam anakartta kalın çizgi)."""
    d = ImageDraw.Draw(im)
    kirmizi = round(5 * kalin * max(1, olcek / 2))
    beyaz = kirmizi + round(4 * kalin)
    for (x0, y0, x1, y1) in kutular:
        k = [round(v * olcek) for v in (x0, y0, x1, y1)]
        bosluk = kirmizi + 2
        d.rounded_rectangle([k[0] - bosluk - 2, k[1] - bosluk - 2, k[2] + bosluk + 2, k[3] + bosluk + 2], radius=12, outline=BEYAZ, width=beyaz)
        d.rounded_rectangle([k[0] - bosluk, k[1] - bosluk, k[2] + bosluk, k[3] + bosluk], radius=10, outline=KIRMIZI, width=kirmizi)
    return im


def yakin_kirp(kutular, gen, yuk, oran=4 / 3, en_az=300):
    x0 = min(k[0] for k in kutular); y0 = min(k[1] for k in kutular)
    x1 = max(k[2] for k in kutular); y1 = max(k[3] for k in kutular)
    w, h = (x1 - x0) * 1.5 + 40, (y1 - y0) * 1.5 + 40
    w = max(w, en_az, h * oran); h = w / oran
    if w > gen: w = gen; h = w / oran
    if h > yuk: h = yuk; w = h * oran
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sol = min(max(0, cx - w / 2), gen - w); ust = min(max(0, cy - h / 2), yuk - h)
    return (round(sol), round(ust), round(sol + w), round(ust + h))


taban = ac(ANAKART)
G, Y = taban.size
for ad, kutular in ELEMANLAR.items():
    kaydet(isaretle(taban.copy(), kutular, 1.0, 1.8), "anakart-isaret-" + ad + ".webp")
    sol, ust, sag, alt = yakin_kirp(kutular, G, Y)
    olcek = 720 / (sag - sol)
    parca = taban.crop((sol, ust, sag, alt)).resize((720, round((alt - ust) * olcek)), Image.LANCZOS)
    kayik = [(a - sol, b - ust, c - sol, e - ust) for (a, b, c, e) in kutular]
    kaydet(isaretle(parca, kayik, olcek), "anakart-isaret-" + ad + "-yakin.webp")

# ------------------------------------------------------------ etiketli iki anakart
from PIL import ImageFilter, ImageFont

# 1) X58: hocanın 3. slaytındaki etiketli resim. Gelen dosya küçük bir resmin
# büyütülmüş hâli; 1800 piksele indirilir (bilgi kaybı olmaz) ve hafifçe keskinleştirilir.
x58 = ac("x58-etiketli-ham.png")
x58 = x58.resize((1800, round(x58.height * 1800 / x58.width)), Image.LANCZOS)
x58 = x58.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=2))
x58.save(os.path.join(HEDEF, "anakart-etiketli.jpg"), "JPEG", quality=86, optimize=True, progressive=True)

# 2) ASUS A8N-SLI: nForce4 tek yongalı bir yonga setidir. Resimdeki "Güney Köprüsü"
# etiketi işlemcinin güç devresinin (MOSFET) soğutucusunu gösteriyordu; fanlı
# yonga da tek başına yonga setidir. Bu iki etiket ve "Sulotları" yazımı düzeltilir.
asus = ac("asus-a8n-etiketli-ham.jpg")
d = ImageDraw.Draw(asus)
yazi = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
for kutu, satirlar in [((1414, 212, 1600, 298), ["Güç devresi", "soğutucusu"]),
                       ((636, 1150, 812, 1245), ["Yonga seti", "(nForce4)"]),
                       ((1416, 848, 1600, 934), ["DDR RAM", "yuvaları"])]:
    d.rectangle(kutu, fill=BEYAZ)
    for i, s in enumerate(satirlar):
        d.text((kutu[0] + 8, kutu[1] + 8 + i * 36), s, font=yazi, fill=(20, 20, 20))
asus.save(os.path.join(HEDEF, "anakart-etiketli-2.jpg"), "JPEG", quality=86, optimize=True, progressive=True)

# 3) Sorular için iki anakarttan yakın görünümler (etiket yazıları kırpılan alanın dışında
# kalır). Kutular o resmin piksel koordinatlarıyla.
YAKINLAR = {
    "asus": (asus, {
        "pci": [(196, 272, 436, 650)],
        "pcie-x1": [(524, 302, 666, 432)],
        "pcie-x16": [(440, 300, 512, 745), (688, 300, 744, 722)],
        "ide": [(746, 1062, 986, 1110)],
        "disket": [(994, 1062, 1218, 1112)],
        "sata": [(328, 780, 412, 1092)],
        "guc": [(994, 1010, 1226, 1060)],
        "ram": [(724, 780, 1362, 988)],
        "islemci-yuvasi": [(956, 434, 1232, 746)],
        "bios-pili": [(214, 638, 322, 742)],
    }),
    "x58": (x58, {
        "pci": [(376, 306, 460, 690)],
        "pcie-x16": [(446, 314, 544, 784), (636, 340, 696, 778)],
        "ide": [(298, 854, 362, 1116)],
        "disket": [(238, 344, 318, 582)],
        "guc": [(848, 1094, 1122, 1172)],
        "ram": [(850, 806, 1476, 1046)],
        "islemci-yuvasi": [(1004, 466, 1346, 722)],
        "kuzey-koprusu": [(758, 516, 962, 798)],
        "guney-koprusu": [(340, 790, 732, 1032)],
    }),
}
# Kırpma bu kart alanlarının dışına çıkmaz: etiket yazıları kartın dışındaki beyaz kenardadır.
KART_ALANI = {"asus": (155, 160, 1368, 1120), "x58": (247, 172, 1478, 1168)}


def kart_ici_kirp(kutular, alan, en_az_g=320, en_az_y=240):
    x0 = min(k[0] for k in kutular); y0 = min(k[1] for k in kutular)
    x1 = max(k[2] for k in kutular); y1 = max(k[3] for k in kutular)
    pay_x = max(60, (x1 - x0) * 0.35); pay_y = max(60, (y1 - y0) * 0.35)
    sol, ust, sag, alt = x0 - pay_x, y0 - pay_y, x1 + pay_x, y1 + pay_y
    if sag - sol < en_az_g: e = (en_az_g - (sag - sol)) / 2; sol -= e; sag += e
    if alt - ust < en_az_y: e = (en_az_y - (alt - ust)) / 2; ust -= e; alt += e
    ax0, ay0, ax1, ay1 = alan
    if sol < ax0: sag += ax0 - sol; sol = ax0
    if sag > ax1: sol -= sag - ax1; sag = ax1
    if ust < ay0: alt += ay0 - ust; ust = ay0
    if alt > ay1: ust -= alt - ay1; alt = ay1
    return (round(max(sol, ax0)), round(max(ust, ay0)), round(min(sag, ax1)), round(min(alt, ay1)))


for kaynak_ad, (resim, kutular_) in YAKINLAR.items():
    for ad, kutular in kutular_.items():
        sol, ust, sag, alt = kart_ici_kirp(kutular, KART_ALANI[kaynak_ad])
        olcek = 720 / (sag - sol)
        parca = resim.crop((sol, ust, sag, alt)).resize((720, round((alt - ust) * olcek)), Image.LANCZOS)
        kayik = [(a_ - sol, b_ - ust, c_ - sol, e_ - ust) for (a_, b_, c_, e_) in kutular]
        kaydet(isaretle(parca, kayik, olcek, 1.7), "anakart-%s-%s.webp" % (kaynak_ad, ad))

print("tamam: " + HEDEF)

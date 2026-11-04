"""Hedef, takvim, çekmece ve hedef sorusu: her temada ekran görüntüsü (GENISLIK, TEMALAR)."""
exec(open("hedef_sina.py", encoding="utf-8").read().split("# =====================================================================\n# 1)")[0])
import os
TEMALAR = os.environ.get("TEMALAR", "gunduz,gece").split(",")
GEN = int(os.environ.get("GENISLIK", "390"))
def resim(s, ad):
    for t_ in TEMALAR:
        s.evaluate("t => moduUygula(t)", t_); s.wait_for_timeout(300)
        s.screenshot(path="goruntu/y%s-%s-%d.png" % (ad, t_, GEN))
D["kayitlar"].clear()
with sync_playwright() as p:
    c, s = cihaz_ac(p, "Y")
    s.set_viewport_size({"width": GEN, "height": 800})
    giris(s)
    s.wait_for_selector(".hedef-perde"); s.wait_for_timeout(300)
    resim(s, "1-hedef-sorusu")
    s.click(".hedef-perde button:has-text('Kaydet')")
D["kayitlar"].clear(); D["yerler"].clear(); D["oturumlar"].clear(); D["profil"] = None
time.sleep(SUNUCU_KOD_ARALIGI)
hazir_kayit("ayar", "hedef", {"gecmis": [{"g": G(120), "gun": 3600, "hafta": 25200}]})
hazir_kayit("ayar", "dondurma", {"gunler": [G(1), G(9)]})
import random
random.seed(4)
for n in range(0, 120):
    if n in (1, 9): continue
    if random.random() < 0.25: continue
    calisma(G(n), {"o": {KA: random.choice([600, 1500, 2400, 3700, 4500, 6000, 8000])}})
with sync_playwright() as p:
    c, s = cihaz_ac(p, "Y")
    s.set_viewport_size({"width": GEN, "height": 800})
    giris(s)
    s.wait_for_selector(".grup-baslik"); s.wait_for_timeout(1200)
    if s.locator(".uyari-perde").count(): s.click(".uyari-perde .hayir")
    resim(s, "2-ana")
    s.click("#hesapDugme"); s.wait_for_timeout(3600)
    resim(s, "3-hedef")
    s.evaluate("() => document.querySelector('.hesap-govde').scrollTo(0, 900)"); s.wait_for_timeout(200)
    resim(s, "4-hedef-alt")
    s.click(".cekmece-sekme[data-ekran=takvim]"); s.wait_for_timeout(300)
    s.click(".takvim-kart:not(.hafta-kart) .hucre[data-gun='%s']" % G(2)); s.wait_for_timeout(200)
    resim(s, "5-takvim")
    s.click(".cekmece-sekme[data-ekran=istatistik]"); s.wait_for_timeout(300)
    resim(s, "6-istatistik")
    print("hatalar:", hatalar[:4])

"""42 Tarzı kartı: gerçek dokunuşla (CDP touch) kaydırma, animasyonlar kapalıyken
dönme ve basılı tutunca yazı seçilmemesi.
ESKI=1 ile kaydırma düzeltmesi geri alınır (hatanın gerçekten bu olduğunu göstermek için)."""
exec(open("vt_taban.py", encoding="utf-8").read())
import os
D["hususi"] = True
ESKI = os.environ.get("ESKI") == "1"

def giris(s):
    s.goto(KOK)
    s.wait_for_selector(".giris-perde")
    kod_iste_ve_gir(s)
    s.wait_for_selector(".sozlesme")
    s.click("text=Okudum, kabul ediyorum")
    s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde")
    s.click("button:has-text('Anladım')")
    s.wait_for_selector(".grup-baslik")

def dokun(cdp, tur, x, y):
    noktalar = [] if tur == "touchEnd" else [{"x": x, "y": y, "id": 1}]
    cdp.send("Input.dispatchTouchEvent", {"type": tur, "touchPoints": noktalar})

def kaydir(s, cdp, x, y, dx, adim=12):
    dokun(cdp, "touchStart", x, y)
    for k in range(1, adim + 1):
        s.wait_for_timeout(16)
        dokun(cdp, "touchMove", x + dx * k / adim, y + 2 * k / adim)
    s.wait_for_timeout(16)
    dokun(cdp, "touchEnd", 0, 0)

with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(service_workers="block", viewport={"width": 390, "height": 820}, device_scale_factor=2,
                      has_touch=True, is_mobile=True, reduced_motion="reduce")
    c.add_init_script("try { localStorage.setItem('pg.kurulum', JSON.stringify('gizli')) } catch (e) {}")
    c.route(SUPA + "/**", isle)
    s = c.new_page()
    s.on("pageerror", lambda e: hatalar.append("pageerror: " + str(e)))
    cdp = c.new_cdp_session(s)
    giris(s)
    bekle_ki(s, lambda: s.locator(".ders-satiri .durum >> nth=0").inner_text() != "yakında")
    kontrol("cihaz animasyonları kapalı (reduced-motion)", s.evaluate("() => matchMedia('(prefers-reduced-motion: reduce)').matches"))

    # --- Yazı seçimi ---
    secim = s.evaluate("""() => ({ satir: getComputedStyle(document.querySelector('.ders-satiri')).userSelect,
                                   govde: getComputedStyle(document.body).userSelect })""")
    kontrol("ders satırında yazı seçilemez", secim["satir"] == "none", secim)

    s.click(".alt-cubuk button >> nth=3")
    s.evaluate("() => { depo.yaz('pg.kartKapsam', Object.fromEntries(Array.from(DERS_KONULARI.keys()).map(d => [d, 'tumu']))); kartSayfasiCiz(); }")
    s.click("text=/kartla çalış/")
    s.wait_for_selector(".deste .kart-yeri:not(.sonraki)")
    if ESKI:
        s.add_style_tag(content=".deste *{touch-action:auto!important}.deste{touch-action:pan-y!important}")
    kontrol("kart yazısında yazı seçilemez",
            s.evaluate("() => getComputedStyle(document.querySelector('.kart-yeri:not(.sonraki) .kart-yuz.on .icerik')).userSelect") == "none")
    kontrol("cevap kutusuna yazı yazılabilir/seçilebilir",
            s.evaluate("() => getComputedStyle(document.querySelector('.kart-cevap textarea')).userSelect") != "none")

    # --- Dönme: dokununca kart yarı yolda görülebilmeli ---
    kutu = s.locator(".kart-yeri:not(.sonraki) .kart-yuz.on .icerik").bounding_box()
    x, y = kutu["x"] + kutu["width"] / 2, kutu["y"] + kutu["height"] / 2
    dokun(cdp, "touchStart", x, y); s.wait_for_timeout(40); dokun(cdp, "touchEnd", 0, 0)
    s.wait_for_timeout(180)
    aci = s.evaluate("""() => { const m = new DOMMatrix(getComputedStyle(document.querySelector('.kart-yeri:not(.sonraki) .kart-ic')).transform);
                               return Math.round(Math.acos(Math.max(-1, Math.min(1, m.m11))) * 180 / Math.PI); }""")
    kontrol("dokunuştan 180 ms sonra kart dönmenin ortasında (0° ile 180° arası)", 5 < aci < 175, aci)
    s.wait_for_timeout(700)
    kontrol("kart çevrildi", s.locator(".kart-yeri:not(.sonraki) .kart-ic.cevrik").count() == 1)
    s.screenshot(path="dokunus-cevrik.png")

    # --- Kaydırma: yazının ortasından sağa ---
    kutu = s.locator(".kart-yeri:not(.sonraki) .kart-yuz.arka .icerik").bounding_box()
    x, y = kutu["x"] + kutu["width"] / 2, kutu["y"] + min(60, kutu["height"] / 2)
    hedef = s.evaluate(f"() => document.elementFromPoint({x}, {y}).className")
    kaydir(s, cdp, x, y, 220)
    s.wait_for_timeout(900)
    bildim = s.locator(".yigin.bildim .sayi").inner_text()
    kontrol("yazının üstünden sağa kaydırınca BİLDİM (dokunulan: %s)" % hedef, bildim == "1", bildim)

    # --- Ön yüzde yazıdan sola kaydırınca kart direnir ve uyarı çıkar ---
    s.wait_for_selector(".deste .kart-yeri:not(.sonraki)")
    kutu = s.locator(".kart-yeri:not(.sonraki) .kart-yuz.on .icerik").bounding_box()
    kaydir(s, cdp, kutu["x"] + kutu["width"] / 2, kutu["y"] + kutu["height"] / 2, -160)
    s.wait_for_timeout(500)
    kontrol("ön yüzde yazıdan kaydırınca 'Önce cevabı görün' uyarısı", "Önce cevabı görün" in s.inner_text(".kart-ipucu"))

    # --- Arka yüz: çevir, sola kaydır ---
    kutu = s.locator(".kart-yeri:not(.sonraki) .kart-yuz.on .icerik").bounding_box()
    dokun(cdp, "touchStart", kutu["x"] + 30, kutu["y"] + 30); s.wait_for_timeout(40); dokun(cdp, "touchEnd", 0, 0)
    s.wait_for_timeout(800)
    kutu = s.locator(".kart-yeri:not(.sonraki) .kart-yuz.arka .icerik").bounding_box()
    kaydir(s, cdp, kutu["x"] + kutu["width"] * 0.6, kutu["y"] + 40, -230)
    s.wait_for_timeout(900)
    kontrol("yazının üstünden sola kaydırınca BİLEMEDİM", s.locator(".yigin.bilemedim .sayi").inner_text() == "1")
    print("hatalar:", hatalar[:5])

gecen = sum(1 for _, k in sonuclar if k)
print("SONUÇ: %d/%d" % (gecen, len(sonuclar)))

exec(open("vt_taban.py", encoding="utf-8").read())
with sync_playwright() as p:
    c, s = cihaz_ac(p, "T")
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    s.evaluate("() => document.querySelector('.giris-perde').style.display='none'")
    for g in (300, 320, 340, 358, 375, 390, 412):
        s.set_viewport_size({"width": g, "height": 700}); s.wait_for_timeout(100)
        r = s.evaluate("() => { const h = document.querySelector('.ust h1'); return [h.scrollWidth, h.clientWidth] }")
        kontrol("%d px: başlık sığıyor" % g, r[0] <= r[1], r)
    for g in (320, 358, 375):
        s.set_viewport_size({"width": g, "height": 700}); s.wait_for_timeout(100)
        for f in ("", "Arial", "Roboto", "Helvetica"):
            r = s.evaluate("""f => { const h = document.querySelector('.ust h1'); if (f) h.style.fontFamily = f; else h.style.fontFamily='';
                const rg = document.createRange(); rg.selectNodeContents(h); const w = rg.getBoundingClientRect().width;
                return [Math.round(w), h.clientWidth, getComputedStyle(h).fontFamily.slice(0,30)] }""", f)
            print(g, f or "öntanımlı", r)

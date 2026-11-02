"""Animasyonlar kapalı cihazda geri sayım saatinin dönmesi (bugün hiç
çalışılmamışken de), sağ kenardan çekilen menünün dışarıya tek dokunuşla
kapanması (dokunuş alttaki ekrana geçmeden) ve takvim çizgilerinin inceliği."""
exec(open("vt_taban.py", encoding="utf-8").read())
D["hususi"] = True

def dokun(cdp, tur, x, y):
    cdp.send("Input.dispatchTouchEvent", {"type": tur, "touchPoints": [] if tur == "touchEnd" else [{"x": x, "y": y, "id": 1}]})

def tikla(s, cdp, x, y):
    dokun(cdp, "touchStart", x, y); s.wait_for_timeout(40); dokun(cdp, "touchEnd", 0, 0)

def kenardan_cek(s, cdp, yer=200, adim=15):
    k = s.locator("#kenarTutamak").bounding_box()
    x, y = k["x"] + k["width"] / 2, k["y"] + yer
    dokun(cdp, "touchStart", x, y)
    for i in range(1, adim + 1):
        s.wait_for_timeout(16); dokun(cdp, "touchMove", x - 20 * i, y + i * 0.4)
    s.wait_for_timeout(16); dokun(cdp, "touchEnd", 0, 0)
    s.wait_for_timeout(500)

AC = """() => new Promise(r => { const l = []; const t0 = performance.now();
  const f = () => { document.querySelectorAll('.saat-kart.donuyor .kanat-ust, .saat-kart.donuyor .kanat-alt').forEach(k => {
      const m = new DOMMatrix(getComputedStyle(k).transform); l.push(Math.round(Math.acos(Math.max(-1, Math.min(1, m.m22))) * 180 / Math.PI)); });
    if (performance.now() - t0 < 3500) requestAnimationFrame(f); else r(l); }; f(); })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(service_workers="block", viewport={"width": 390, "height": 820}, device_scale_factor=2,
                      has_touch=True, is_mobile=True, reduced_motion="reduce")
    c.add_init_script("try { localStorage.setItem('pg.kurulum', JSON.stringify('gizli')) } catch (e) {}")
    c.route(SUPA + "/**", isle)
    s = c.new_page(); cdp = c.new_cdp_session(s)
    s.on("pageerror", lambda e: hatalar.append("pageerror: " + str(e)))
    s.goto(KOK); s.wait_for_selector(".giris-perde"); kod_iste_ve_gir(s)
    s.wait_for_selector(".sozlesme"); s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')"); s.wait_for_selector(".grup-baslik")
    bekle_ki(s, lambda: s.locator(".ders-satiri .durum >> nth=0").inner_text() != "yakında")
    s.wait_for_timeout(800)
    kontrol("cihaz animasyonları kapalı", s.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"))
    kontrol("bugün hiç çalışılmadı", s.evaluate("istatistikTopla(null).gunler.get(gunAnahtari(Date.now()))") in (None, {"o": 0, "t": 0, "k": 0}))

    # ---------- 1) Menü kenardan çekilerek açılır, dışarıya TEK dokunuşla kapanır ----------
    for tur in range(1, 4):
        kenardan_cek(s, cdp)
        kontrol("%d. kez: sağ kenardan çekince menü açıldı" % tur, s.locator(".hesap-sayfa.acik").count() == 1)
        if tur == 1:
            acilar = s.evaluate(AC)
            kontrol("bugün çalışılmamışken de saat kartları açılışta döndü (animasyonlar kapalıyken)",
                    len(acilar) > 20 and max(acilar) >= 60, (len(acilar), sorted(set(acilar))[-5:]))
            saat = s.evaluate("() => Array.from(document.querySelectorAll('.saat-blok')[0].querySelectorAll('.saat-kart .sabit-ust span')).map(e => e.textContent)")
            kontrol("dönüş bitince günlük saat hedefin tamamını gösterir (1 sa → 01:00:00)", saat == ["01", "00", "00"], saat)
        # perdenin ders satırı üstündeki yerine dokun: kapanmalı, alttaki ders açılmamalı
        satir = s.locator(".ders-satiri >> nth=0").bounding_box()
        x, y = 14, satir["y"] + satir["height"] / 2
        kontrol("%d. kez: dokunulan yer menünün dışı" % tur, s.evaluate("([x, y]) => document.elementFromPoint(x, y).className", [x, y]) == "cekmece-perde")
        tikla(s, cdp, x, y)
        s.wait_for_timeout(700)
        kontrol("%d. kez: dışarıya tek dokunuşla kapandı" % tur, s.locator(".hesap-sayfa").count() == 0)
        kontrol("%d. kez: dokunuş alttaki derse geçmedi" % tur, s.locator(".agac").count() == 0 and s.locator(".grup-baslik").count() > 0)
        kontrol("%d. kez: geçmiş yığını boşaldı" % tur, s.evaluate("Object.values(SEKME_GECMISI).reduce((n, y) => n + y.length, 0)") == 0)

    # Telefonda olası arızalar taklit edilir: (a) dokunuştan tıklama hiç doğmaz, (b) tarayıcı geri gitmez
    s.evaluate("() => { window._yut = e => { e.stopImmediatePropagation(); e.preventDefault(); }; window.addEventListener('click', _yut, true); }")
    kenardan_cek(s, cdp)
    satir = s.locator(".ders-satiri >> nth=0").bounding_box()
    tikla(s, cdp, 14, satir["y"] + 10); s.wait_for_timeout(700)
    kontrol("tıklama olayı hiç gelmese de tek dokunuşla kapanır", s.locator(".hesap-sayfa").count() == 0)
    s.evaluate("() => window.removeEventListener('click', _yut, true)")
    s.evaluate("() => { window._geri = history.back; history.back = () => {}; }")
    kenardan_cek(s, cdp)
    tikla(s, cdp, 14, satir["y"] + 10); s.wait_for_timeout(900)
    kontrol("tarayıcı geri gitmese de kapanır ve yığın düzelir", s.locator(".hesap-sayfa").count() == 0 and s.evaluate("Object.values(SEKME_GECMISI).reduce((n, y) => n + y.length, 0)") == 0)
    s.evaluate("() => { history.back = window._geri; }")
    s.go_back(); s.wait_for_timeout(500)   # taklitte kalan geçmiş adımı (gerçekte de geri tuşu sessizce geçer)
    kontrol("artık adımdan geri basınca bir şey bozulmaz", s.locator(".grup-baslik").count() > 0 and s.locator(".hesap-sayfa").count() == 0)

    # Fareyle de (bilgisayar)
    k = s.locator("#kenarTutamak").bounding_box()
    s.mouse.move(k["x"] + 9, k["y"] + 200); s.mouse.down()
    for i in range(1, 16): s.mouse.move(k["x"] + 9 - 20 * i, k["y"] + 200); s.wait_for_timeout(16)
    s.mouse.up(); s.wait_for_timeout(500)
    kontrol("fareyle çekince açıldı", s.locator(".hesap-sayfa.acik").count() == 1)
    s.mouse.click(14, 300); s.wait_for_timeout(700)
    kontrol("fareyle dışarıya tek tıklamayla kapandı", s.locator(".hesap-sayfa").count() == 0 and s.locator(".agac").count() == 0)
    # Kapat düğmesi ve geri tuşu hâlâ çalışıyor
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    s.click(".hesap-kapat"); s.wait_for_timeout(600)
    kontrol("kapat düğmesi çalışıyor", s.locator(".hesap-sayfa").count() == 0 and s.evaluate("Object.values(SEKME_GECMISI).reduce((n, y) => n + y.length, 0)") == 0)
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    s.go_back(); s.wait_for_timeout(600)
    kontrol("telefonun geri tuşu çalışıyor", s.locator(".hesap-sayfa").count() == 0 and s.locator(".grup-baslik").count() > 0)
    # Menü kapandıktan sonra bir sonraki dokunuş normal çalışır (yutulmaz)
    s.wait_for_timeout(800)
    satir = s.locator(".ders-satiri >> nth=0").bounding_box()
    tikla(s, cdp, satir["x"] + 60, satir["y"] + satir["height"] / 2)
    kontrol("sonraki dokunuş normal çalışır (ders açıldı)", bekle_ki(s, lambda: s.locator(".agac").count() == 1, 3))
    s.click(".alt-cubuk button:has-text('Kıraat')")

    # ---------- 2) Takvim çizgileri ince ----------
    cekmece(s, "takvim")
    cizgi = s.evaluate("""() => { const ol = sec => { const e = document.querySelector(sec); if (!e) return null;
        const st = getComputedStyle(e); return [st.vectorEffect, parseFloat(st.strokeWidth)]; };
        return { sinir: ol('.takvim-svg .ay-siniri'), bos: ol('.takvim-svg .hucre.k0'), bugun: ol('.takvim-svg .hucre.bugun') }; }""")
    kontrol("ay sınırı çizgisi 1 px ve SVG büyüdükçe kalınlaşmaz", cizgi["sinir"] == ["non-scaling-stroke", 1], cizgi)
    kontrol("boş gün kenarı 0.75 px", cizgi["bos"] == ["non-scaling-stroke", 0.75], cizgi)
    s.screenshot(path="saat-cekmece-takvim.png")
    print("hatalar:", hatalar[:5])

gecen = sum(1 for _, k in sonuclar if k)
print("SONUÇ: %d/%d" % (gecen, len(sonuclar)))

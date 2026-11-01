"""Görsel dizisi (yana kaydırma), soru görselleri ve büyüteç.
- Notta boş satırsız art arda gelen görseller tek dizi olur; sayaç, oklar, noktalar çalışır.
- Parmakla kaydırınca sayaç güncellenir.
- Görsele dokununca büyüteç açılır; dokunulan yer büyür; geri tuşu ve Kapat kapatır.
- Görselli sorularda dizi soru metninin altında çizilir, açıklama yazısı (cevabı ele verecek) gösterilmez."""
exec(open("vt_taban.py", encoding="utf-8").read())
D["hususi"] = True

KONU = next(k for k in YUK["konular"] if k["id"] == "dn-elemanlar")
satirlar = KONU["metin"].split("\n")
DIZILER = []
i = 0
while i < len(satirlar):
    n = 0
    while i + n < len(satirlar) and re.match(r"^!\[[^\]]*\]\(gorseller/[^)]+\)\s*$", satirlar[i + n]): n += 1
    if n >= 2: DIZILER.append(n)
    i += max(n, 1)
TEK = sum(1 for l in satirlar if l.startswith("![")) - sum(DIZILER)

with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(service_workers="block", viewport={"width": 390, "height": 820}, device_scale_factor=2, has_touch=True, is_mobile=True)
    c.add_init_script("try { localStorage.setItem('pg.kurulum', JSON.stringify('gizli')) } catch (e) {}")
    c.route(SUPA + "/**", isle)
    s = c.new_page()
    s.on("pageerror", lambda e: hatalar.append("pageerror: " + str(e)))
    s.goto(KOK); s.wait_for_selector(".giris-perde"); kod_iste_ve_gir(s)
    s.wait_for_selector(".sozlesme"); s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')"); s.wait_for_selector(".grup-baslik")
    bekle_ki(s, lambda: s.evaluate("KONULAR.size") == len(YUK["konular"]), 20)

    # ---------- 1) Notta diziler ----------
    s.evaluate("id => konuAc(id)", KONU["id"]); s.wait_for_selector(".okuma h2")
    kontrol("%d dizi çizildi (%s görselli)" % (len(DIZILER), DIZILER), s.locator(".okuma .galeri").count() == len(DIZILER))
    kontrol("dizilerdeki görsel sayıları birebir", s.evaluate("() => [...document.querySelectorAll('.okuma .galeri')].map(g => g.querySelectorAll('figure').length)") == DIZILER)
    kontrol("tek görseller dizi dışında (%d)" % TEK, s.evaluate("() => [...document.querySelectorAll('.okuma > figure')].length") == TEK)
    kontrol("bütün not görselleri yüklendi", bekle_ki(s, lambda: s.evaluate("() => [...document.querySelectorAll('.okuma figure img')].every(i => i.complete && i.naturalWidth > 0)"), 10))
    g = s.locator(".okuma .galeri >> nth=2")   # 6 görselli yuva dizisi
    g.scroll_into_view_if_needed()
    n = g.locator("figure").count()
    kontrol("başta sayaç 1 / %d, geri oku gizli" % n, g.locator(".galeri-sayac").inner_text() == "1 / %d" % n and g.locator(".galeri-ok.geri").is_disabled())
    kontrol("görsel ekran genişliğinde (taşma yok)", s.evaluate("() => document.documentElement.scrollWidth <= innerWidth"))
    g.locator(".galeri-ok.ileri").click(); s.wait_for_timeout(700)
    kontrol("ileri okla 2 / %d" % n, g.locator(".galeri-sayac").inner_text() == "2 / %d" % n, g.locator(".galeri-sayac").inner_text())
    kontrol("nokta da ilerledi", g.locator(".galeri-noktalar span >> nth=1").get_attribute("class") == "secili")
    # parmakla kaydırma yerine şeridin kendisi kaydırılır (kaydırma olayı aynı)
    g.locator(".galeri-serit").evaluate("e => e.scrollTo({ left: (e.clientWidth + 10) * (e.children.length - 1) })"); s.wait_for_timeout(500)
    kontrol("sona kaydırınca %d / %d ve ileri oku gizli" % (n, n), g.locator(".galeri-sayac").inner_text() == "%d / %d" % (n, n) and g.locator(".galeri-ok.ileri").is_disabled())
    kontrol("açıklama yazısı görünen görselin altında", g.locator("figure >> nth=%d" % (n - 1)).locator("figcaption").count() == 1)
    s.screenshot(path="galeri-not.png")

    # ---------- 2) Büyüteç ----------
    yigin = s.evaluate("geriYigini.length")
    g.locator("figure >> nth=%d" % (n - 1)).locator("img").click(); s.wait_for_selector(".buyutec")
    kontrol("dokununca büyüteç açıldı", s.locator(".buyutec img").count() == 1)
    gen0 = s.evaluate("() => document.querySelector('.buyutec img').offsetWidth")
    kontrol("başta ekrana sığıyor", gen0 <= 390, gen0)
    s.locator(".buyutec img").click(position={"x": 30, "y": 30}); s.wait_for_timeout(300)
    gen1 = s.evaluate("() => document.querySelector('.buyutec img').offsetWidth")
    kontrol("dokununca 2,5 kat büyüdü", abs(gen1 - gen0 * 2.5) < 2, (gen0, gen1))
    kontrol("büyüyen görsel kaydırılabilir", s.evaluate("() => { const a = document.querySelector('.buyutec-alan'); return a.scrollWidth > a.clientWidth; }"))
    s.screenshot(path="galeri-buyutec.png")
    s.go_back(); s.wait_for_timeout(500)
    kontrol("geri tuşu büyüteci kapattı, not açık kaldı", s.locator(".buyutec").count() == 0 and s.locator(".okuma h2").count() == 1 and s.evaluate("geriYigini.length") == yigin)
    s.locator(".okuma > figure img >> nth=0").click(); s.wait_for_selector(".buyutec")
    s.click(".buyutec-ust button"); s.wait_for_timeout(500)
    kontrol("Kapat düğmesi kapattı", s.locator(".buyutec").count() == 0 and s.evaluate("geriYigini.length") == yigin)

    # ---------- 3) Görselli sorular ----------
    s.click(".alt-cubuk button:has-text('Temrin')")
    gorselli = [q for q in KONU["sorular"] if q.get("gorseller")]
    for q in gorselli:
        s.evaluate("id => { derinlesGit(calisMenusuCiz); oturumBaslat([SORU_HARITASI.get(id)], 'Tek'); }", q["id"])
        s.wait_for_selector(".soru .metin")
        sayi = len(q["gorseller"])
        ok = bekle_ki(s, lambda: s.evaluate("() => { const l = [...document.querySelectorAll('.soru figure img')]; return l.length > 0 && l.every(i => i.complete && i.naturalWidth > 0); }"), 8)
        bilgi = s.evaluate("""() => ({ n: document.querySelectorAll('.soru figure img').length, dizi: document.querySelectorAll('.soru .galeri').length,
            yazi: document.querySelectorAll('.soru figcaption').length,
            once: (() => { const m = document.querySelector('.soru .metin'), f = document.querySelector('.soru figure');
                           return !!(m.compareDocumentPosition(f) & Node.DOCUMENT_POSITION_FOLLOWING); })() })""")
        kontrol(q["id"] + ": %d görsel yüklendi, metnin altında, açıklama yazısı yok" % sayi,
                ok and bilgi["n"] == sayi and bilgi["dizi"] == (1 if sayi > 1 else 0) and bilgi["yazi"] == 0 and bilgi["once"], bilgi)
        s.evaluate("() => geriDon()"); s.wait_for_timeout(250)
    s.evaluate("id => { derinlesGit(calisMenusuCiz); oturumBaslat([SORU_HARITASI.get(id)], 'Tek'); }", gorselli[0]["id"])
    s.wait_for_selector(".soru figure img"); s.wait_for_timeout(500)
    s.screenshot(path="galeri-soru.png")
    s.locator(".soru figure img >> nth=0").click(); s.wait_for_selector(".buyutec")
    kontrol("soru görseline dokununca büyüteç açıldı", s.locator(".buyutec").count() == 1)
    s.go_back(); s.wait_for_timeout(400)
    kontrol("büyüteç kapandı, soru yerinde", s.locator(".buyutec").count() == 0 and s.locator(".soru .metin").count() == 1)
    s.click(".secenekler .secenek >> nth=0")
    kontrol("cevaplandıktan sonra da görseller duruyor", s.locator(".soru figure img").count() == len(gorselli[0]["gorseller"]))
    print("hatalar:", hatalar[:5])
    c.close()

kontrol("sayfa hatası yok", not [h for h in hatalar if "pageerror" in h])
gecen = sum(1 for _, k in sonuclar if k)
print("SONUÇ: %d/%d" % (gecen, len(sonuclar)))

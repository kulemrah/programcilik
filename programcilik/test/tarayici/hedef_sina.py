"""Hedef, seri, dondurma, geri sayan saat, çekmece, takvimler, 3 dk kuralı, göz koruyucu.
Tarihler bugüne göre kurulur (tarayıcı ile aynı saat dilimi)."""
exec(open("vt_taban.py", encoding="utf-8").read())
import datetime as dt
D["hususi"] = True

BUGUN = dt.date.today()
G = lambda n: (BUGUN - dt.timedelta(days=n)).isoformat()
KONULAR_VT = sorted([k for k in YUK["konular"] if k["ders"] == "veritabani"], key=lambda k: k["sira"])
KA, KB = KONULAR_VT[0]["id"], KONULAR_VT[1]["id"]

def calisma(gun, deger, yazici="aaaaaaaaaaaa"):
    hazir_kayit("calisma", gun + "|" + yazici, deger)

def giris(s, not_kapat=True):
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    kod_iste_ve_gir(s)
    s.wait_for_selector(".sozlesme")
    s.click("text=Okudum, kabul ediyorum")
    s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde")
    if not_kapat: s.click("button:has-text('Anladım')")

def dokun(cdp, tur, x, y):
    cdp.send("Input.dispatchTouchEvent", {"type": tur, "touchPoints": [] if tur == "touchEnd" else [{"x": x, "y": y, "id": 1}]})

# =====================================================================
# 1) Yeni hesap: hedef yok → açılışta sorulur
# =====================================================================
D["kayitlar"].clear()
with sync_playwright() as p:
    c, s = cihaz_ac(p, "H")
    giris(s)
    s.wait_for_selector(".hedef-perde", timeout=8000)
    kontrol("hedef yokken açılışta hedef sorusu çıkar", s.locator(".hedef-perde h3:has-text('Çalışma hedefiniz')").count() == 1)
    sec = lambda i: s.locator(".hedef-perde .sure-secici").nth(i).locator("select")
    sec(0).nth(0).select_option("1"); sec(0).nth(1).select_option("30")
    kontrol("günlük 1 sa 30 dk → haftalık otomatik 10 sa 30 dk",
            sec(1).nth(0).input_value() == "10" and sec(1).nth(1).input_value() == "30", (sec(1).nth(0).input_value(), sec(1).nth(1).input_value()))
    sec(1).nth(0).select_option("9")
    s.wait_for_selector(".uyari-perde")
    kontrol("haftalık azaltılınca uygulamanın uyarısı çıkar", "azaltılamaz" in s.inner_text(".uyari-perde"))
    s.click(".uyari-perde .evet")
    kontrol("uyarıdan sonra haftalık 10 sa 30 dk'ya döner", sec(1).nth(0).input_value() == "10" and sec(1).nth(1).input_value() == "30")
    sec(1).nth(0).select_option("12")
    kontrol("haftalık artırılabilir, uyarı yok", s.locator(".uyari-perde").count() == 0)
    s.click(".hedef-perde button:has-text('Kaydet')")
    s.wait_for_selector(".hedef-perde", state="detached")
    bekle_ki(s, lambda: ("ayar", "hedef") in D["kayitlar"])
    h = (D["kayitlar"].get(("ayar", "hedef")) or {}).get("deger", {}).get("gecmis", [])
    kontrol("hedef hesaba yazıldı (bugünden geçerli, 5400 sn / 45000 sn)",
            len(h) == 1 and h[0]["g"] == BUGUN.isoformat() and h[0]["gun"] == 5400 and h[0]["hafta"] == 45000, h)
    s.reload(); s.wait_for_selector(".grup-baslik"); s.wait_for_timeout(1500)
    kontrol("hedef konduktan sonra yeniden sorulmaz", s.locator(".hedef-perde").count() == 0)
    print("hatalar:", hatalar[:5])

# =====================================================================
# 2) Hazır veriyle: takvim, seri, dondurma, saat, çekmece
# =====================================================================
D["kayitlar"].clear(); D["yerler"].clear(); D["oturumlar"].clear(); D["profil"] = None
time.sleep(SUNUCU_KOD_ARALIGI)
hazir_kayit("ayar", "hedef", {"gecmis": [{"g": G(40), "gun": 3600, "hafta": 25200}]})
calisma(G(0), {"o": {KA: 1000}})                          # bugün: 1000 sn (hedef 3600)
                                                          # dün: hiç → kopukluk
calisma(G(2), {"o": {KA: 3600}, "t": {KB: 100}})          # KB 100 sn < 3 dk → sayılmaz; 3600 = hedef → k3, hedefte
calisma(G(3), {"o": {KA: 4000}, "k": {KB: 3300}})         # 7300 → 2 katı üstü → k5
calisma(G(4), {"o": {KA: 1900}})                          # .53 → k2
calisma(G(5), {"o": {KA: 1000}})                          # .28 → k1
calisma(G(6), {"o": {KA: 2000}, "t": {KA: 3500}})         # 5500 → 1.53 → k4
calisma(G(6), {"o": {KB: 170}}, "bbbbbbbbbbbb")           # başka cihaz, KB 170 sn < 3 dk → sayılmaz
calisma(G(7), {"o": {KB: 100}}, "bbbbbbbbbbbb")           # aynı konu iki cihazda: 100 + 100 = 200 ≥ 180 → sayılır
calisma(G(7), {"o": {KB: 100}})
_g40 = dt.date.fromisoformat(G(40))
HAK = 3 * ((BUGUN.year * 12 + BUGUN.month) - (_g40.year * 12 + _g40.month) + 1)   # hedefin ayından bu aya birikmiş haklar
beklenen = {0: ("k1", False), 2: ("k3", True), 3: ("k5", True), 4: ("k2", False), 5: ("k1", False), 6: ("k4", True), 7: ("k1", False)}

with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(service_workers="block", viewport={"width": 390, "height": 820}, device_scale_factor=2, has_touch=True, is_mobile=True)
    c.add_init_script("try { localStorage.setItem('pg.kurulum', JSON.stringify('gizli')) } catch (e) {}")
    c.route(SUPA + "/**", isle)
    s = c.new_page()
    s.on("pageerror", lambda e: hatalar.append("pageerror: " + str(e)))
    s.on("console", lambda m: hatalar.append("console: " + m.text) if m.type == "error" else None)
    cdp = c.new_cdp_session(s)
    giris(s)
    # --- dondurma sorusu: Esc ile kapanırsa sonra yeniden sorulur ---
    s.wait_for_selector(".uyari-perde", timeout=8000)
    s.click(".uyari-perde", position={"x": 5, "y": 5}); s.wait_for_timeout(200)
    kontrol("dondurma sorusu perdeye dokununca kapanmaz", s.locator(".uyari-perde").count() == 1)
    s.keyboard.press("Escape"); s.wait_for_timeout(300)
    kontrol("Esc ile kapanınca 'soruldu' yazılmaz", s.evaluate("() => localStorage.getItem('pg.dondurmaSoruldu')") is None)
    s.reload(); s.wait_for_selector(".grup-baslik")
    s.wait_for_selector(".uyari-perde", timeout=8000)
    metin = s.inner_text(".uyari-perde")
    kontrol("yeniden açılışta yine sorulur; mesajda birikmiş hak (%d)" % HAK, ("%d hakkınız var" % HAK) in metin and "kullanılmayanlar birikir" in metin, metin)
    kontrol("seri koptu → dondurma sorulur (önceki seri 2 gün)", "Seriniz bozuldu" in metin and "2 günlük seriniz" in metin, metin)
    s.click(".uyari-perde .evet")
    bekle_ki(s, lambda: ("ayar", "dondurma") in D["kayitlar"])
    don = (D["kayitlar"].get(("ayar", "dondurma")) or {}).get("deger", {}).get("gunler", [])
    kontrol("dün donduruldu ve hesaba yazıldı", don == [G(1)], don)

    # --- denetim düzeltmeleri: haftalık düşüm ve hedef öncesi günler ---
    hd = s.evaluate("""() => { const pzt = haftaBasi(gunAnahtari(Date.now()));
        const gecmis = [{ g: '2026-01-01', gun: 18000, hafta: 126000 }, { g: gunAnahtari(Date.now()), gun: 3600, hafta: 25200 }];
        return haftaDurumu(new Map(), pzt, gecmis, new Set([pzt])); }""")
    kontrol("haftalık düşüm aynı hedef kaydından: 7 sa − 1×1 sa = 6 sa (eski 5 sa'lik günlükle değil)",
            hd["hedef"] == 21600 and not hd["tamam"] if BUGUN.weekday() > 0 else True, hd)
    on = s.evaluate("([g0, g5]) => gunDurumu(new Map([[g5, { o: 9000, t: 0, k: 0 }]]), g5, [{ g: g0, gun: 600, hafta: 4200 }], new Set())", [G(0), G(5)])
    kontrol("hedef konmadan önceki gün 'hedefe ulaşıldı' sayılmaz", on["tamam"] is False and on["oncesi"] is True, on)

    # --- istatistik çekirdeği tarayıcıda ---
    t = s.evaluate("() => { const ist = istatistikTopla(null); return Object.fromEntries(Array.from(ist.gunler).map(([g, x]) => [g, x.o + x.t + x.k])); }")
    kontrol("3 dk kuralı: konunun günlük süresi 3 dk'dan azsa sayılmaz",
            t.get(G(2)) == 3600 and t.get(G(6)) == 5500 and t.get(G(3)) == 7300, {k: t.get(G(k)) for k in (2, 3, 6)})
    kontrol("3 dk kuralı cihazlar toplanınca uygulanır (100+100 sn sayılır)", t.get(G(7)) == 200, t.get(G(7)))
    seri = s.evaluate("() => seriHesapla(istatistikTopla(null).gunler)")
    kontrol("seri 2 (dondurulan dün köprü olur, uzatmaz; bugün henüz tamam değil)", seri["n"] == 2, seri)

    # --- çekmece: menü düğmesi, hedef ekranı, saat ---
    s.click("#hesapDugme")
    s.wait_for_selector(".hesap-sayfa.acik .cekmece")
    kontrol("menü düğmesi çekmeceyi açar; ilk ekran Hedef", s.locator(".cekmece-sekme.secili").inner_text() == "Hedef")
    s.wait_for_timeout(3500)
    saat = s.evaluate("() => Array.from(document.querySelectorAll('.saat-blok')[0].querySelectorAll('.saat-kart .sabit-ust span')).map(e => e.textContent)")
    kontrol("günlük saat kalan süreyi gösterir (3600-1000=2600 sn → 00:43:20)", saat == ["00", "43", "20"], saat)
    kontrol("saatte ortadan geçen çizgi yok", s.evaluate("() => getComputedStyle(document.querySelector('.saat-kart'), '::after').content") in ("none", "normal"))
    gunler = s.locator(".hafta-gunu").evaluate_all("els => els.map(e => e.className)")
    kontrol("bu haftanın gün yuvarlakları 7", len(gunler) == 7)
    kontrol("dün buz işaretli (bu haftadaysa)", BUGUN.weekday() == 0 or any("donmus" in g for g in gunler), gunler)
    kalan_hak = HAK - 1
    kontrol("dondurma hakkı birikir: %d − 1 kullanılan = %d" % (HAK, kalan_hak),
            s.get_attribute(".buzlar", "aria-label") == "%d dondurma hakkı" % kalan_hak and
            (s.locator(".buzlar .buz.var").count() == kalan_hak if kalan_hak <= 8 else s.inner_text(".buz-sayi") == "× %d" % kalan_hak),
            s.get_attribute(".buzlar", "aria-label"))
    kontrol("dondurma metninde birikme anlatılıyor", "kullanmadıklarınız birikir" in s.inner_text(".dondurma-kart"))
    # Birikme kuralının çekirdeği: ileriki ayların hakkı geçmişe kullanılamaz
    bk = s.evaluate("""([g40, bugun]) => {
        const kume = new Set();
        const basAy = g40.slice(0, 7), buAy = bugun.slice(0, 7);
        const ilkAyGunleri = n => Array.from({ length: n }, (_, i) => basAy + "-" + String(i + 1).padStart(2, "0"));
        const buAyGunleri = n => Array.from({ length: n }, (_, i) => buAy + "-" + String(i + 1).padStart(2, "0"));
        return { ilk3: dondurmaYeterMi(ilkAyGunleri(3), kume), ilk4: dondurmaYeterMi(ilkAyGunleri(4), kume),
                 kalanBuAy: kalanDondurma(buAy, kume), kalanIlkAy: kalanDondurma(basAy, kume),
                 hepsi: dondurmaYeterMi(buAyGunleri(Math.min(28, kalanDondurma(buAy, kume))), kume),
                 fazla: kalanDondurma(buAy, kume) < 28 ? dondurmaYeterMi(buAyGunleri(kalanDondurma(buAy, kume) + 1), kume) : false,
                 once: kalanDondurma("2000-01", kume) };
    }""", [G(40), G(0)])
    kontrol("ilk ayda en çok 3 gün dondurulur (sonraki ayların hakkı geçmişe kullanılamaz)", bk["ilk3"] is True and bk["ilk4"] is False and bk["kalanIlkAy"] == 3, bk)
    kontrol("bu aya kadar birikenin tamamı kullanılabilir, fazlası kullanılamaz", bk["kalanBuAy"] == HAK and bk["hepsi"] is True and bk["fazla"] is False, bk)
    kontrol("hedeften önceki ayda hak yok", bk["once"] == 0, bk)

    # --- takvim ekranı ---
    s.click(".cekmece-sekme[data-ekran=takvim]")
    s.wait_for_selector(".takvim-svg")
    for n, (kd, hedefte) in beklenen.items():
        sinif = s.get_attribute(".takvim-kart:not(.hafta-kart) .hucre[data-gun='%s']" % G(n), "class") or ""
        kontrol("gün -%d: %s%s" % (n, kd, " + yeşil kenar" if hedefte else ""), kd in sinif.split() and (("hedefte" in sinif) == hedefte), sinif)
    sinif = s.get_attribute(".takvim-kart:not(.hafta-kart) .hucre[data-gun='%s']" % G(1), "class") or ""
    kontrol("dün: dondurulmuş (buz)", "donmus" in sinif and s.locator(".buz-isaret").count() >= 1, sinif)
    kontrol("ay sınırı çizgisi var", s.locator(".takvim-kart:not(.hafta-kart) .ay-siniri").count() == 1)
    ay_adlari = s.locator(".takvim-kart:not(.hafta-kart) .eksen-yazi").all_inner_texts()
    kontrol("ay adları yazılı", sum(1 for a in ay_adlari if a not in ("Pzt", "Çar", "Cum", "Paz")) >= 3, ay_adlari)
    AYLAR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
    gelecek_ay = AYLAR[BUGUN.month % 12]
    tum_adlar = s.locator(".takvim-kart .eksen-yazi").all_inner_texts()
    kontrol("henüz gelmemiş ayın adı yazmaz (%s)" % gelecek_ay, gelecek_ay not in tum_adlar, tum_adlar)
    # dokununca ipucu çıkar ve parmak çekilince kalır
    kutu = s.locator(".takvim-kart:not(.hafta-kart) .hucre[data-gun='%s']" % G(2)).bounding_box()
    x, y = kutu["x"] + kutu["width"] / 2, kutu["y"] + kutu["height"] / 2
    dokun(cdp, "touchStart", x, y); s.wait_for_timeout(60); dokun(cdp, "touchEnd", 0, 0); s.wait_for_timeout(400)
    ip = s.locator(".takvim-kart:not(.hafta-kart) .takvim-detay")
    kontrol("dokunulan günün bilgisi parmak çekilince de görünür (takvimin altında)", ip.count() == 1 and ip.is_visible())
    metin = ip.inner_text() if ip.count() else ""
    kontrol("bilgide hedef ve 'hedefe ulaşıldı'", "Günlük hedef: 1 sa" in metin and "hedefe ulaşıldı" in metin, metin)
    ipkutu = ip.bounding_box()
    kontrol("bilgi parmağın altında kalmaz (takvimin altında, dokunulan hücreden aşağıda)", ipkutu and ipkutu["y"] > y + 20, (ipkutu, y))
    s.mouse.move(x, y); s.wait_for_timeout(200)
    kontrol("fareyle üstüne gelince yüzen ipucu da çıkar", s.locator(".takvim-kart:not(.hafta-kart) .viz-ipucu").is_visible())
    # haftalık
    pzt = BUGUN - dt.timedelta(days=BUGUN.weekday())
    bu_hafta = s.get_attribute(".hafta-kart .hucre[data-hafta='%s']" % pzt.isoformat(), "class") or ""
    kontrol("haftalık takvimde bu hafta var", "hucre" in bu_hafta, bu_hafta)
    s.click(".hafta-kart .hucre[data-hafta='%s']" % (pzt - dt.timedelta(days=7 if BUGUN.weekday() > 0 else 0)).isoformat())
    s.wait_for_timeout(300)
    hm = s.inner_text(".hafta-kart .takvim-detay")
    kontrol("haftaya tıklayınca haftalık hedef yazar", "Haftalık hedef" in hm, hm)
    hafta_dun = (BUGUN - dt.timedelta(days=1))
    pzt_dun = hafta_dun - dt.timedelta(days=hafta_dun.weekday())
    s.click(".hafta-kart .hucre[data-hafta='%s']" % pzt_dun.isoformat()); s.wait_for_timeout(300)
    hm = s.inner_text(".hafta-kart .takvim-detay")
    kontrol("dondurulan günün haftası: hedef 7 sa − 1 gün = 6 sa ve '1 gün donduruldu'", "Haftalık hedef: 6 sa" in hm and "1 gün donduruldu" in hm, hm)
    s.click(".cekmece .hesap-ust h2"); s.wait_for_timeout(200)
    kontrol("başka yere dokununca bilgi kapanır", not s.locator(".hafta-kart .takvim-detay").is_visible())

    # --- dar telefonda saat taşmaz ---
    s.click(".cekmece-sekme[data-ekran=hedef]"); s.wait_for_timeout(300)
    for gen in (320, 360):
        s.set_viewport_size({"width": gen, "height": 800}); s.wait_for_timeout(300)
        olc = s.evaluate("() => Array.from(document.querySelectorAll('.saat-satiri')).map(e => [e.scrollWidth, e.clientWidth])")
        kontrol("%d px'te saat satırları taşmaz" % gen, olc and all(a <= b for a, b in olc), olc)
    s.set_viewport_size({"width": 390, "height": 820}); s.wait_for_timeout(200)
    s.keyboard.press("Escape"); s.wait_for_timeout(500)
    kontrol("Esc çekmeceyi kapatır", s.locator(".hesap-sayfa").count() == 0)
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    s.click(".cekmece-sekme[data-ekran=takvim]"); s.wait_for_timeout(300)

    # --- son ekran hatırlanır, kapat/aç ---
    s.click(".hesap-kapat"); s.wait_for_timeout(500)
    kontrol("× çekmeceyi kapatır", s.locator(".hesap-sayfa").count() == 0)
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    kontrol("yeniden açınca son ekran (Takvim)", s.locator(".cekmece-sekme.secili").inner_text() == "Takvim")
    s.go_back(); s.wait_for_timeout(500)
    kontrol("telefonun geri tuşu çekmeceyi kapatır", s.locator(".hesap-sayfa").count() == 0)

    # --- sağ kenardan çekme ---
    kb = s.locator("#kenarTutamak").bounding_box()
    x0, y0 = kb["x"] + kb["width"] - 3, kb["y"] + kb["height"] / 2
    dokun(cdp, "touchStart", x0, y0)
    for k in range(1, 13):
        s.wait_for_timeout(16); dokun(cdp, "touchMove", x0 - 22 * k, y0)
    s.wait_for_timeout(16); dokun(cdp, "touchEnd", 0, 0); s.wait_for_timeout(600)
    kontrol("sağ kenardan sola çekince çekmece açılır", s.locator(".hesap-sayfa.acik").count() == 1)
    # sağa çekip kapat
    pb = s.locator(".cekmece .hesap-ust").bounding_box()
    x1, y1 = pb["x"] + 60, pb["y"] + pb["height"] / 2
    dokun(cdp, "touchStart", x1, y1)
    for k in range(1, 13):
        s.wait_for_timeout(16); dokun(cdp, "touchMove", x1 + 22 * k, y1)
    s.wait_for_timeout(16); dokun(cdp, "touchEnd", 0, 0); s.wait_for_timeout(700)
    kontrol("çekmece sağa çekilince kapanır", s.locator(".hesap-sayfa").count() == 0)
    kisa = s.evaluate("() => { const t = document.getElementById('kenarTutamak').getBoundingClientRect(); return [t.top, t.bottom, innerHeight]; }")
    kontrol("tutamak üst çubuktan alt çubuğa uzanır", kisa[0] > 40 and kisa[1] < kisa[2] - 50, kisa)

    # --- hedefi değiştirme: bugünden geçerli, geçmiş korunur ---
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    s.click(".cekmece-sekme[data-ekran=hedef]")
    s.click(".hedef-kart button:has-text('Değiştir')")
    s.locator(".hedef-kart .sure-secici >> nth=0").locator("select >> nth=0").select_option("2")
    s.locator(".hedef-kart .sure-secici >> nth=0").locator("select >> nth=1").select_option("0")
    s.click(".hedef-kart button:has-text('Kaydet')")
    bekle_ki(s, lambda: len((D["kayitlar"].get(("ayar", "hedef")) or {}).get("deger", {}).get("gecmis", [])) == 2)
    h = D["kayitlar"][("ayar", "hedef")]["deger"]["gecmis"]
    kontrol("yeni hedef bugünden; eskisi geçmişte durur", len(h) == 2 and h[0]["g"] == G(40) and h[1] == {"g": BUGUN.isoformat(), "gun": 7200, "hafta": 50400}, h)
    s.click(".cekmece-sekme[data-ekran=takvim]"); s.wait_for_timeout(300)
    sinif = s.get_attribute(".takvim-kart:not(.hafta-kart) .hucre[data-gun='%s']" % G(2), "class")
    kontrol("geçmiş gün eski hedefle değerlendirilir (G-2 hâlâ hedefte)", "hedefte" in sinif, sinif)
    s.click(".cekmece-sekme[data-ekran=istatistik]"); s.wait_for_timeout(300)
    kontrol("istatistik ekranında halka ve özet var", s.locator(".ist-kutu").count() == 4 and s.locator(".halka-svg").count() == 1)
    s.click(".cekmece-sekme[data-ekran=hesap]"); s.wait_for_timeout(300)
    kontrol("hesap ekranında kimlik ve çıkış", s.locator(".profil-kart").count() == 1 and s.locator("button:has-text('Çıkış yap')").count() == 1)
    s.screenshot(path="goruntu/hedef-hesap.png")
    s.click(".hesap-kapat"); s.wait_for_timeout(500)

    # --- göz koruyucu ---
    oku = lambda: s.evaluate("() => [document.documentElement.dataset.goz || '0', getComputedStyle(document.querySelector('.goz-filtre')).opacity]")
    kademeler = []
    for _ in range(4):
        s.click("#gozDugme"); s.wait_for_timeout(450); kademeler.append(oku())
    kontrol("göz koruyucu 1→2→3→kapalı döner", [k[0] for k in kademeler] == ["1", "2", "3", "0"], kademeler)
    kontrol("kademe arttıkça süzgeç koyulaşır, kapalıyken yok",
            float(kademeler[0][1]) < float(kademeler[1][1]) < float(kademeler[2][1]) and float(kademeler[3][1]) == 0, kademeler)
    s.click("#gozDugme"); s.click("#gozDugme")
    s.reload(); s.wait_for_selector(".grup-baslik")
    kontrol("göz koruyucu kademesi yeniden açılışta kalır (2)", oku()[0] == "2")
    kontrol("süzgeç dokunuşu engellemez", s.evaluate("() => getComputedStyle(document.querySelector('.goz-filtre')).pointerEvents") == "none")
    s.click("#gozDugme"); s.click("#gozDugme")

    # --- çıkış: uygulamanın kendi penceresi ---
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    s.click(".cekmece-sekme[data-ekran=hesap]")
    s.click(".hesap-sayfa button:has-text('Çıkış yap')")
    s.wait_for_selector(".uyari-perde")
    kontrol("çıkışta uygulamanın soru penceresi", "Çıkış yapılsın mı?" in s.inner_text(".uyari-perde"))
    s.click(".uyari-perde .hayir"); s.wait_for_timeout(200)
    kontrol("vazgeçince çıkılmaz", s.locator(".giris-perde").count() == 0 and s.locator(".hesap-sayfa").count() == 1)
    s.click(".hesap-sayfa button:has-text('Çıkış yap')")
    s.click(".uyari-perde .evet")
    s.wait_for_selector(".giris-perde", timeout=8000)
    kontrol("onaylayınca çıkış yapılır", True)
    kontrol("giriş ekranında öğrenci numarası örneği", "ogrenci_no@" in s.get_attribute("#girisEposta", "placeholder"))
    kontrol("giriş ekranında 'Bilgisayar Programcılığı' geçmez", "Programcılığı" not in s.inner_text(".giris-perde"))
    print("hatalar:", hatalar[:5])

gecen = sum(1 for _, k in sonuclar if k)
print("SONUÇ: %d/%d" % (gecen, len(sonuclar)))

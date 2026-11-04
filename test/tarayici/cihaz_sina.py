"""Bu cihaz (Hesap): cihaz türü ve ölçek (yalnızca bu cihazda, hesaba gitmez),
alt çubukta ve çekmecede kaydırarak sekme değiştirme (uçlarda döner),
Bilgisayar modunda Alt kısayolları, geniş ekranda "Derslere göre süre"
listesi, ölçek (zoom) varken ipucu/rozet/editör yerleşimi.
Gerçek şema ve Worker'la (kaynak_taban.py): not editörü de denenir."""
exec(open("kaynak_taban.py", encoding="utf-8").read())
import datetime as dt

BUGUN = dt.date.today()
G = lambda n: (BUGUN - dt.timedelta(days=n)).isoformat()
DERSLER = []
for k in YUK["konular"]:
    if k["ders"] not in [d for d, _ in DERSLER]: DERSLER.append((k["ders"], k["id"]))
# Dört dersten çalışma: halka listesinde dört satır
for i, (d, kid) in enumerate(DERSLER[:4]):
    hazir_kayit("calisma", G(i) + "|aaaaaaaaaaaa", {"o": {kid: 2500 - i * 400}})

def baglam(p, ad, en, boy, dokunmatik):
    b = p.chromium.launch()
    secenek = dict(service_workers="block", viewport={"width": en, "height": boy}, device_scale_factor=2)
    if dokunmatik: secenek.update(has_touch=True, is_mobile=True)
    c = b.new_context(**secenek)
    c.add_init_script("try { localStorage.setItem('pg.kurulum', JSON.stringify('gizli')) } catch (e) {}")
    c.route(SUPA + "/**", isle)
    kaynak_yollari(c)
    s = c.new_page()
    s.on("pageerror", lambda e: hatalar.append(ad + " pageerror: " + str(e)))
    s.on("console", lambda m: hatalar.append(ad + " console." + m.type + ": " + m.text) if m.type == "error" else None)
    return b, c, s

def dokun(cdp, tur, x, y):
    cdp.send("Input.dispatchTouchEvent", {"type": tur, "touchPoints": [] if tur == "touchEnd" else [{"x": x, "y": y, "id": 1}]})

def kaydir(s, cdp, x, y, dx, dy=0, adim=10):
    dokun(cdp, "touchStart", x, y)
    for k in range(1, adim + 1):
        s.wait_for_timeout(16); dokun(cdp, "touchMove", x + dx * k / adim, y + dy * k / adim)
    s.wait_for_timeout(16); dokun(cdp, "touchEnd", 0, 0)
    s.wait_for_timeout(450)

def sekme(s):
    return s.evaluate("() => aktifSekme")

def cubuk_dugme(s, etiket):
    return s.locator(".alt-cubuk button[aria-label='%s']" % etiket).bounding_box()

def cekmece_ekrani(s):
    return s.evaluate("() => (document.querySelector('.cekmece-sekme.secili') || {}).dataset.ekran")

def tasma_yok(s):
    return s.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")

try:
    with sync_playwright() as p:
        # =================================================================
        # 1) Telefon (dokunmatik): kaydırma ve ölçek
        # =================================================================
        b, c, s = baglam(p, "T", 390, 820, True)
        cdp = c.new_cdp_session(s)
        giris(s)
        kontrol("telefonda cihaz türü kendiliğinden Telefon", s.evaluate("() => document.documentElement.dataset.cihaz") == "telefon")

        # --- alt çubuk ---
        k = cubuk_dugme(s, "Kıraat"); orta_y = k["y"] + k["height"] / 2
        kaydir(s, cdp, 200, orta_y, -90)
        kontrol("Kıraat'te parmak sola: en sağdaki Notlar'a döner", sekme(s) == "kaynak", sekme(s))
        kaydir(s, cdp, 200, orta_y, 90)
        kontrol("Notlar'da parmak sağa: en soldaki Kıraat'e döner", sekme(s) == "oku", sekme(s))
        kaydir(s, cdp, 150, orta_y, 90)
        kontrol("Kıraat'te parmak sağa: Ara", sekme(s) == "ara", sekme(s))
        a = cubuk_dugme(s, "Ara")
        # Ara düğmesinin içinde kalan kısa kaydırma: düğmeye tıklama sayılmamalı
        kaydir(s, cdp, a["x"] + a["width"] - 4, orta_y, -42, 0, 6)
        kontrol("Ara'da (düğmenin içinde) sağdan sola kaydırma: Kıraat; tıklama ayrıca Ara'yı açmaz", sekme(s) == "oku", sekme(s))
        for beklenen in ["ara", "calis", "kart", "kaynak", "oku"]:
            kaydir(s, cdp, 200, orta_y, 80)
        kontrol("sağa beş kaydırma: bütün sekmeler dolaşılıp Kıraat'e dönülür", sekme(s) == "oku", sekme(s))
        kaydir(s, cdp, 200, orta_y, 14, -60, 6)
        kontrol("dikey/kısa hareket sekme değiştirmez", sekme(s) == "oku")
        t = cubuk_dugme(s, "Temrin")
        dokun(cdp, "touchStart", t["x"] + t["width"] / 2, orta_y); s.wait_for_timeout(40); dokun(cdp, "touchEnd", 0, 0); s.wait_for_timeout(400)
        kontrol("dokunmak yine sekme açar (Temrin)", sekme(s) == "calis", sekme(s))
        s.wait_for_timeout(800)
        # geri tuşu: kaydırarak geçilen sekmeler de geçmişte
        s.go_back(); s.wait_for_timeout(400)
        kontrol("geri tuşu kaydırmayla gelinen sekmeden Kıraat'e döner", sekme(s) == "oku", sekme(s))

        # --- çekmece ---
        s.evaluate("() => localStorage.setItem('pg.cekmeceEkrani', JSON.stringify('hedef'))")
        s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik"); s.wait_for_timeout(400)
        kontrol("çekmece Hedef'te açıldı", cekmece_ekrani(s) == "hedef")
        g = s.locator(".hesap-govde").bounding_box()
        gy = g["y"] + 160
        kaydir(s, cdp, 300, gy, -120)
        kontrol("Hedef'te parmak sola: sağdaki İstatistik (sayfa çevirir gibi)", cekmece_ekrani(s) == "istatistik", cekmece_ekrani(s))
        kontrol("çekmece açık kalır", s.locator(".hesap-sayfa.acik").count() == 1)
        kaydir(s, cdp, 80, gy, 120)
        kontrol("İstatistik'te parmak sağa: soldaki Hedef", cekmece_ekrani(s) == "hedef", cekmece_ekrani(s))
        kaydir(s, cdp, 80, gy, 120)
        kontrol("Hedef'te parmak sağa: en sağdaki Hesap'a döner (çekmece kapanmaz)", cekmece_ekrani(s) == "hesap" and s.locator(".hesap-sayfa.acik").count() == 1, cekmece_ekrani(s))
        kaydir(s, cdp, 300, gy, -120)
        kontrol("Hesap'ta parmak sola: baştaki Hedef'e döner", cekmece_ekrani(s) == "hedef", cekmece_ekrani(s))
        kaydir(s, cdp, 300, gy, -120)
        kontrol("son bölüm hatırlanır", cekmece_ekrani(s) == "istatistik" and s.evaluate("() => JSON.parse(localStorage.getItem('pg.cekmeceEkrani'))") == "istatistik")
        kaydir(s, cdp, 200, gy, 20, -200)
        kontrol("dikey kaydırma bölüm değiştirmez", cekmece_ekrani(s) == "istatistik")
        kaydir(s, cdp, 200, gy, 30, 0, 4)
        kontrol("kısa yatay hareket bölüm değiştirmez ve içerik yerine döner",
                cekmece_ekrani(s) == "istatistik" and s.evaluate("() => document.querySelector('.hesap-ic').style.transform") == "")
        cip = s.locator(".cekmece .donem-satiri").bounding_box()
        kaydir(s, cdp, cip["x"] + cip["width"] - 20, cip["y"] + cip["height"] / 2, -120)
        kontrol("çip satırında kaydırma bölüm değiştirmez", cekmece_ekrani(s) == "istatistik", cekmece_ekrani(s))
        kaydir(s, cdp, 300, gy, -120)
        kontrol("İstatistik'te parmak sola: Takvim", cekmece_ekrani(s) == "takvim", cekmece_ekrani(s))
        tk = s.locator(".takvim-svg").first.bounding_box()
        kaydir(s, cdp, tk["x"] + 30, tk["y"] + tk["height"] / 2, 140)
        kontrol("takvim çiziminin üstünden de kaydırılır: İstatistik", cekmece_ekrani(s) == "istatistik", cekmece_ekrani(s))
        kaydir(s, cdp, 80, gy, 120)
        kontrol("İstatistik'te parmak sağa: Hedef", cekmece_ekrani(s) == "hedef", cekmece_ekrani(s))
        u = s.locator(".cekmece .hesap-ust").bounding_box()
        kaydir(s, cdp, u["x"] + 60, u["y"] + u["height"] / 2, 260)
        s.wait_for_timeout(400)
        kontrol("başlık satırında sağa çekmek çekmeceyi kapatır", s.locator(".hesap-sayfa").count() == 0)

        # --- Hesap › Bu cihaz ---
        s.evaluate("() => localStorage.setItem('pg.cekmeceEkrani', JSON.stringify('hesap'))")
        s.click("#hesapDugme"); s.wait_for_selector(".cihaz-kart")
        kart = lambda: s.inner_text(".cihaz-kart")
        kontrol("Bu cihaz kartı: Telefon seçili, kendiliğinden seçildiği yazar",
                s.locator(".cihaz-turu.secili").inner_text() == "Telefon" and "kendiliğinden" in kart(), kart())
        kontrol("ölçek %100", s.inner_text(".olcek-deger") == "%100")
        CUBUK_OLC = """() => { const u = document.querySelector('header.ust').getBoundingClientRect(), h = document.querySelector('header.ust h1').getBoundingClientRect(),
            a = document.querySelector('.alt-cubuk').getBoundingClientRect(), b = document.querySelector('.alt-cubuk button').getBoundingClientRect();
            return [u.height, h.height, a.height, b.width, a.top]; }"""
        once = s.evaluate(CUBUK_OLC)
        s.click(".olcek-dugme[aria-label='Büyüt']"); s.wait_for_timeout(150)
        s.click(".olcek-dugme[aria-label='Büyüt']"); s.wait_for_timeout(150)
        kontrol("iki kez büyüt: %120", s.inner_text(".olcek-deger") == "%120", s.inner_text(".olcek-deger"))
        kontrol("390 px'te %120'den fazlası olmaz (sayfa 320 px'in altına inmez)", s.locator(".olcek-dugme[aria-label='Büyüt']").is_disabled())
        z = s.evaluate("() => [document.documentElement.style.zoom, getComputedStyle(document.documentElement).getPropertyValue('--zoom-olcek').trim(), JSON.parse(localStorage.getItem('pg.olcek'))]")
        kontrol("zoom uygulanır ve bu cihazda saklanır", z == ["1.2", "1.2", 1.2], z)
        kontrol("ölçek hesaba gönderilmez", not any("olcek" in str(a) or "cihaz" in str(a) for a in D["kayitlar"]), list(D["kayitlar"])[:8])
        kontrol("%120'de yatay taşma yok", tasma_yok(s))
        sonra = s.evaluate(CUBUK_OLC)
        kontrol("ölçek üst başlığı ve alt çubuğu etkilemez", all(abs(x - y) < 1.5 for x, y in zip(once, sonra)), (once, sonra))
        cr = s.evaluate("() => { const r = document.querySelector('.cekmece').getBoundingClientRect(); return [r.left, r.right, r.top, r.bottom, innerWidth, innerHeight]; }")
        kontrol("çekmece ekrana sığar", cr[0] >= 0 and abs(cr[1] - cr[4]) < 2 and cr[2] <= 1 and abs(cr[3] - cr[5]) < 2, cr)
        s.screenshot(path="cihaz-telefon-olcek.png")
        # çekmece kapat, sayfalar
        s.click(".hesap-kapat"); s.wait_for_timeout(500)
        for ad in ["Ara", "Temrin", "42 Tarzı", "Notlar", "Kıraat"]:
            s.click(".alt-cubuk button[aria-label='%s']" % ad); s.wait_for_timeout(300)
            kontrol("%%120'de %s taşmıyor" % ad, tasma_yok(s))
        ab = s.evaluate("() => { const r = document.querySelector('.alt-cubuk').getBoundingClientRect(); return [r.bottom, innerHeight]; }")
        kontrol("alt çubuk ekranın altında", abs(ab[0] - ab[1]) < 2, ab)
        yer = s.evaluate("""() => { const a = document.querySelector('.alt-cubuk').getBoundingClientRect(), u = document.querySelector('header.ust').getBoundingClientRect(),
            k = document.getElementById('kenarTutamak').getBoundingClientRect(); window.scrollTo(0, 1e6);
            const son = [...document.querySelectorAll('#sayfaOku button')].pop().getBoundingClientRect();
            return [a.top, u.bottom, k.top, k.bottom, son.bottom]; }""")
        kontrol("%120'de kenar tutamağı iki çubuk arasında, sayfanın sonu alt çubuğun altında kalmaz",
                yer[2] >= yer[1] - 2 and yer[3] <= yer[0] + 2 and yer[4] <= yer[0] + 1, yer)
        s.evaluate("() => window.scrollTo(0, 0)")
        # --- güncelleme notu ve Yama Notları ---
        s.evaluate("() => localStorage.removeItem('pg.notSurumu')")
        s.reload(); s.wait_for_selector(".not-perde")
        nt = s.inner_text(".not-perde")
        s.screenshot(path="cihaz-guncelleme-notu.png")
        kontrol("hiç not görmemiş cihazda: hoş geldiniz ve yenilikler birlikte", "hoş geldiniz" in nt and "Temrinde önce kapsam" in nt and "Notlar sekmesi" in nt and "Kaydırarak sekme" in nt and "Yama Notları" in nt, nt[:200])
        kontrol("%120'de not kutusu ekrana sığar", s.evaluate("() => { const r = document.querySelector('.not-kutu').getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; }"))
        s.click(".not-perde button:has-text('Anladım')"); s.wait_for_timeout(300)
        kontrol("Anladım: görülen sürüm 2.3", s.evaluate("() => JSON.parse(localStorage.getItem('pg.notSurumu'))") == "2.3")
        s.reload(); s.wait_for_selector(".grup-baslik"); s.wait_for_timeout(800)
        kontrol("bir kere görünür: yeniden açılışta çıkmaz", s.locator(".not-perde").count() == 0)
        s.evaluate("() => localStorage.setItem('pg.notSurumu', JSON.stringify('2.0'))")
        s.reload(); s.wait_for_selector(".not-perde")
        nt = s.inner_text(".not-perde")
        kontrol("2.0'ı görmüş cihazda yalnızca yenilikler (2.1, 2.2, 2.3)", "Temrinde iyileştirmeler" in nt and "Yenilikler: Notlar ve kaydırma" in nt and "Notlar sekmesi" in nt and "Yenilik: sınav takvimi" in nt and "Temrinde önce kapsam" not in nt, nt[:200])
        s.go_back(); s.wait_for_timeout(400)
        kontrol("geri tuşu notu kapatır", s.locator(".not-perde").count() == 0)
        s.evaluate("() => localStorage.setItem('pg.cekmeceEkrani', JSON.stringify('hesap'))")
        s.click("#hesapDugme"); s.wait_for_selector(".yama-kutusu")
        kontrol("Hesap'ta Yama Notları kutusu", "s2.3" in s.inner_text(".yama-kutusu") and "4 not" in s.inner_text(".yama-kutusu"), s.inner_text(".yama-kutusu"))
        s.click(".yama-kutusu"); s.wait_for_selector(".yama-notlari")
        basliklar = s.evaluate("() => [...document.querySelectorAll('.yama-not .yama-ust h4')].map(e => e.textContent)")
        kontrol("Yama Notları yeniden eskiye", basliklar == ["Temrinde iyileştirmeler", "Yenilik: sınav takvimi", "Yenilikler: Notlar ve kaydırma", "Kostü - Ders'e hoş geldiniz"], basliklar)
        s.screenshot(path="cihaz-yama-notlari.png")
        s.locator(".yama-don").first.click(); s.wait_for_timeout(200)
        kontrol("Hesaba dön", s.locator(".cihaz-kart").count() == 1 and s.locator(".yama-notlari").count() == 0)
        s.click(".hesap-kapat"); s.wait_for_timeout(500)
        # yeniden açılışta ilk boyamadan önce
        s.reload(); s.wait_for_selector(".grup-baslik")
        kontrol("yeniden açılışta %120", s.evaluate("() => document.documentElement.style.zoom") == "1.2")
        # kaydırma zoom'la da çalışır
        k = cubuk_dugme(s, "Kıraat")
        kaydir(s, cdp, 200, k["y"] + k["height"] / 2, -90)
        kontrol("%120'de alt çubuk kaydırması", sekme(s) == "kaynak", sekme(s))
        # Notlar editörü klavyeye sığma hesabı zoom'la
        s.wait_for_selector("#sayfaKaynak .kaynak-fab-ana")
        tasnif_ac(s, "Ölçek")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Ölçek')"); s.wait_for_timeout(300)
        editor_ac_yeni(s); s.wait_for_timeout(300)
        er = s.evaluate("() => { const r = document.querySelector('.not-editor').getBoundingClientRect(); return [r.top, r.bottom, innerHeight]; }")
        kontrol("%120'de not editörü ekranı tam kaplar (taşmaz)", abs(er[0]) < 2 and abs(er[1] - er[2]) < 2, er)
        s.keyboard.type("Ölçek denemesi")
        editor_kapat(s)
        # Tablet ayrı cihaz: kendi ölçeği
        b2, c2, s2 = baglam(p, "TB", 820, 1180, True)
        s2.goto(KOK); s2.wait_for_selector(".giris-perde")
        kontrol("tablette cihaz türü Tablet, ölçek yok (telefonunki geçmez)",
                s2.evaluate("() => [document.documentElement.dataset.cihaz, document.documentElement.style.zoom]") == ["tablet", ""])
        b2.close()
        # Ekran daralınca (döndürme) büyütme sınırlanır, genişleyince geri gelir
        s.evaluate("() => localStorage.setItem('pg.olcek', '1.5')")
        s.set_viewport_size({"width": 900, "height": 820}); s.wait_for_timeout(200)
        s.reload(); s.wait_for_selector(".grup-baslik")
        kontrol("geniş ekranda %150", s.evaluate("() => document.documentElement.style.zoom") == "1.5")
        s.set_viewport_size({"width": 390, "height": 820}); s.wait_for_timeout(300)
        kontrol("daralınca %121'e iner, taşma yok", s.evaluate("() => document.documentElement.style.zoom") == "1.21" and tasma_yok(s),
                s.evaluate("() => document.documentElement.style.zoom"))
        s.click("#hesapDugme"); s.wait_for_selector(".cihaz-kart")
        kontrol("kart sınırı söyler", "en çok %121" in s.inner_text(".cihaz-kart"), s.inner_text(".cihaz-kart"))
        s.click(".olcek-sifirla"); s.wait_for_timeout(200)
        kontrol("%100'e dön: zoom kalkar, kayıt silinir",
                s.evaluate("() => [document.documentElement.style.zoom, localStorage.getItem('pg.olcek')]") == ["", None])
        s.click(".cihaz-turu[data-tur='bilgisayar']"); s.wait_for_timeout(150)
        kontrol("cihaz türü seçilebilir ve saklanır",
                s.evaluate("() => [document.documentElement.dataset.cihaz, JSON.parse(localStorage.getItem('pg.cihazTuru'))]") == ["bilgisayar", "bilgisayar"]
                and "kendiliğinden" not in s.inner_text(".cihaz-kart") and "Alt tuşunu" in s.inner_text(".cihaz-kart"))
        b.close()

        # =================================================================
        # 2) Bilgisayar: halka listesi, Alt kısayolları, zoom'da yerleşim
        # =================================================================
        D["oturumlar"].clear(); D["yerler"].clear(); D["profil"] = None
        time.sleep(SUNUCU_KOD_ARALIGI)
        b, c, s = baglam(p, "B", 1280, 860, False)
        giris(s)
        kontrol("bilgisayarda cihaz türü kendiliğinden Bilgisayar", s.evaluate("() => document.documentElement.dataset.cihaz") == "bilgisayar")
        s.evaluate("() => localStorage.setItem('pg.cekmeceEkrani', JSON.stringify('istatistik'))")
        for en in [1280, 1920]:
            s.set_viewport_size({"width": en, "height": 1000})
            s.click("#hesapDugme"); s.wait_for_selector(".halka-liste .halka-ad"); s.wait_for_timeout(400)
            ad = s.evaluate("() => [...document.querySelectorAll('.halka-liste .halka-ad')].map(e => [e.clientWidth, e.scrollWidth, e.textContent])")
            kontrol("%d px: Derslere göre süre listesinde ders adları sığar" % en,
                    len(ad) == 4 and all(w >= 120 and sw <= w + 1 for w, sw, _ in ad), ad)
            sut = s.evaluate("() => getComputedStyle(document.querySelector('.halka-duzen')).gridTemplateColumns.split(' ').length")
            kontrol("%d px: dar çekmecede halka tek sütun (liste altta)" % en, sut == 1, sut)
            kutu = s.evaluate("() => getComputedStyle(document.querySelector('.ist-kutular')).gridTemplateColumns.split(' ').length")
            kontrol("%d px: özet kutuları ikişerli" % en, kutu == 2, kutu)
            if en == 1920: s.screenshot(path="cihaz-halka-1920.png")
            s.keyboard.press("Escape"); s.wait_for_timeout(500)
        s.set_viewport_size({"width": 1280, "height": 860})

        # --- Alt kısayolları ---
        s.keyboard.down("Alt"); s.wait_for_timeout(100)
        rozet = lambda: s.evaluate("() => [...document.querySelectorAll('.kisayol-rozet')].map(e => e.textContent)")
        harita = s.evaluate("""() => kisayol ? Object.fromEntries(kisayol.liste.map(x => [x.el.getAttribute('aria-label') || x.el.textContent.trim().slice(0, 30), x.kod])) : {}""")
        kontrol("Alt basılıyken rozetler çıkar", len(rozet()) >= 8, rozet())
        s.screenshot(path="cihaz-kisayol.png")
        kontrol("alt çubukta ad harfleri (K, A, T, 4, N)",
                [harita.get(x) for x in ["Kıraat", "Ara", "Temrin", "42 Tarzı", "Notlar"]] == ["K", "A", "T", "4", "N"], harita)
        kontrol("kodlar tekil", len(set(rozet())) == len(rozet()))
        kontrol("D, E, F kullanılmaz", not any(r in ("D", "E", "F") for r in rozet()))
        s.keyboard.press("KeyA"); s.wait_for_timeout(300)
        kontrol("Alt+A: Ara sekmesi", sekme(s) == "ara", sekme(s))
        kontrol("Alt bırakılmadan rozetler yeni ekrana göre yenilenir", len(rozet()) >= 5)
        harita = s.evaluate("""() => Object.fromEntries(kisayol.liste.map(x => [x.el.tagName + ':' + (x.el.getAttribute('aria-label') || x.el.placeholder || x.el.textContent.trim().slice(0, 20)), x.kod]))""")
        girdi = [v for k_, v in harita.items() if k_.startswith("INPUT:")]
        kontrol("arama kutusunun da rozeti var", len(girdi) == 1, harita)
        s.keyboard.press("Key" + girdi[0]); s.wait_for_timeout(200)
        kontrol("Alt+harf yazı kutusuna imleci götürür", s.evaluate("() => document.activeElement.tagName") == "INPUT")
        s.keyboard.press("KeyN"); s.wait_for_timeout(300)
        kontrol("Alt+N: Notlar", sekme(s) == "kaynak", sekme(s))
        s.keyboard.up("Alt"); s.wait_for_timeout(100)
        kontrol("Alt bırakılınca rozetler kalkar", len(rozet()) == 0)
        s.keyboard.press("Alt+K"); s.wait_for_timeout(300)
        kontrol("Alt+K tek hamlede: Kıraat", sekme(s) == "oku", sekme(s))
        # Alt'la açılan çekmecede yalnız çekmecedekiler
        s.keyboard.down("Alt"); s.wait_for_timeout(100)
        menu = s.evaluate("() => kisayol.liste.find(x => x.el.id === 'hesapDugme').kod")
        s.keyboard.press("Key" + menu); s.wait_for_timeout(600)
        kontrol("Alt+harf menüyü açar", s.locator(".hesap-sayfa.acik").count() == 1)
        disarida = s.evaluate("() => kisayol.liste.filter(x => !x.el.closest('.hesap-sayfa')).length")
        kontrol("çekmece açıkken arkadakilere rozet verilmez", disarida == 0, disarida)
        hesap = s.evaluate("() => kisayol.liste.find(x => x.el.dataset.ekran === 'hesap').kod")
        s.keyboard.press("Key" + hesap if hesap.isalpha() else "Digit" + hesap); s.wait_for_timeout(300)
        kontrol("Alt+harf çekmecede Hesap bölümüne geçer", cekmece_ekrani(s) == "hesap")
        s.keyboard.up("Alt")
        # Olmayan harf hiçbir şey yapmaz; iki harfli kodlar
        kodlar = s.evaluate("""() => { const f = n => kisayolKodlari(Array.from({ length: n }, () => ({ el: document.createElement('button') })));
            return [f(33), f(60)]; }""")
        kontrol("33 öğeye tek karakter, hepsi farklı", all(len(x) == 1 for x in kodlar[0]) and len(set(kodlar[0])) == 33, kodlar[0])
        kontrol("60 öğede hepsi iki harf, farklı, D/E/F yok",
                all(len(x) == 2 for x in kodlar[1]) and len(set(kodlar[1])) == 60 and not any(ch in "DEF" for x in kodlar[1] for ch in x))
        s.keyboard.press("Escape"); s.wait_for_timeout(500)
        # iki harfli kullanım: çok sayıda düğme olan ekranda
        s.evaluate("""() => { const k = document.createElement('div'); k.id = 'cokDugme'; k.style.cssText = 'position:fixed;inset:60px 0 auto 0;z-index:5;display:grid;grid-template-columns:repeat(10,1fr);background:#fff';
            for (let i = 0; i < 50; i++) { const b = document.createElement('button'); b.textContent = 'x' + i; b.style.height = '30px'; b.onclick = () => { window.basilan = i; }; k.appendChild(b); }
            document.body.appendChild(k); }""")
        s.keyboard.down("Alt"); s.wait_for_timeout(100)
        hedef = s.evaluate("() => kisayol.liste.find(x => x.el.textContent === 'x37').kod")
        kontrol("çok öğede iki harfli kodlar", len(hedef) == 2, hedef)
        s.keyboard.press("Key" + hedef[0]); s.wait_for_timeout(80)
        soluk = s.evaluate("() => [document.querySelectorAll('.kisayol-rozet.soluk').length, document.querySelectorAll('.kisayol-rozet').length]")
        kontrol("ilk harften sonra uymayanlar soluklaşır", 0 < soluk[0] < soluk[1], soluk)
        s.keyboard.press("Key" + hedef[1]); s.wait_for_timeout(200)
        kontrol("ikinci harf o düğmeye tıklar", s.evaluate("() => window.basilan") == 37)
        s.keyboard.up("Alt")
        s.evaluate("() => document.getElementById('cokDugme').remove()")

        # --- zoom'da rozetler, ipucu ---
        s.evaluate("() => { localStorage.setItem('pg.olcek', '1.3'); }")
        s.reload(); s.wait_for_selector(".grup-baslik")
        s.keyboard.down("Alt"); s.wait_for_timeout(100)
        fark = s.evaluate("""() => kisayol.liste.map(x => { let a = x.el.getBoundingClientRect(); const b = x.rozet.getBoundingClientRect();
            if (a.width / 1.3 > 120) { const i = [...x.el.children].map(e => e.getBoundingClientRect()).find(q => q.width > 2 && q.height > 2); if (i) a = i; }
            return Math.max(Math.abs(b.left - Math.max(4 * 1.3, a.left) + 4 * 1.3), Math.abs(b.top - Math.max(4 * 1.3, a.top) + 4 * 1.3)); })""")
        kontrol("%130'da rozetler öğelerin köşesinde", len(fark) > 5 and max(fark) < 10, max(fark) if fark else None)
        s.keyboard.up("Alt")
        s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
        s.click(".cekmece-sekme[data-ekran=istatistik]"); s.wait_for_timeout(400)
        s.locator(".halka-svg").scroll_into_view_if_needed(); s.wait_for_timeout(200)
        d = s.locator(".halka-svg .ders-dilim").first
        db = d.bounding_box()
        mx, my = db["x"] + db["width"] / 2, db["y"] + db["height"] / 2
        if s.evaluate("([x, y]) => { const e = document.elementFromPoint(x, y); return !e || !e.classList.contains('ders-dilim'); }", [mx, my]):
            pt = s.evaluate("""() => { const p = document.querySelector('.halka-svg .ders-dilim'); const l = p.getTotalLength(); const q = p.getPointAtLength(l / 4);
                const m = p.getScreenCTM(); const r = new DOMPoint(q.x, q.y).matrixTransform(m); return [r.x, r.y]; }""")
            mx, my = pt
        s.mouse.move(mx, my); s.wait_for_timeout(250)
        ip = s.evaluate("() => { const r = document.querySelector('.viz-ipucu').getBoundingClientRect(), k = document.querySelector('.halka-cizim').getBoundingClientRect(); return [r.left, r.right, r.bottom, k.left, k.right]; }")
        kontrol("%130'da ipucu imlecin üstünde ve çizimin içinde", ip[2] <= my and ip[0] >= ip[3] - 1 and ip[1] <= ip[4] + 1 and ip[0] - 200 < mx < ip[1] + 200, (ip, mx, my))
        s.screenshot(path="cihaz-masaustu-olcek.png")
        s.keyboard.press("Escape"); s.wait_for_timeout(400)
        # Telefon modunda Alt bir şey yapmaz
        s.evaluate("() => localStorage.setItem('pg.cihazTuru', JSON.stringify('telefon'))")
        s.reload(); s.wait_for_selector(".grup-baslik")
        s.keyboard.down("Alt"); s.wait_for_timeout(100)
        kontrol("Telefon modunda Alt rozet göstermez", len(rozet()) == 0)
        s.keyboard.press("KeyA"); s.wait_for_timeout(200)
        s.keyboard.up("Alt")
        kontrol("Telefon modunda Alt+A sekme değiştirmez", sekme(s) == "oku")
        b.close()
finally:
    sunucu.terminate()

kontrol("sayfa hatası yok", not [h for h in hatalar if "favicon" not in h], hatalar[:5])
gecen = sum(1 for _, k in sonuclar if k)
print("\n%d/%d geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) else 1)

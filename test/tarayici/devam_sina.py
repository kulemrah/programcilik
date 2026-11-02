"""Yarım kalan temrin ve deste: sekmeye dokununca, geri basınca, yeniden açınca sürer.
Kök ekranda geri tuşu: önce uyarı, ikinci basışta çıkış."""
exec(open("vt_taban.py", encoding="utf-8").read())
D["hususi"] = True
alg = sorted([k for k in YUK["konular"] if k["ders"] == "algoritma"], key=lambda k: k["sira"])
dy_ids = [q["id"] for k in alg for q in k["sorular"] if q["tip"] == "dy"][:3]

def giris(s):
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    s.fill("#girisEposta", EPOSTA); s.click("button:has-text('Kod gönder')")
    s.wait_for_selector("#girisKod"); s.fill("#girisKod", "123456"); s.click("button:has-text('Giriş yap')")
    s.wait_for_selector(".sozlesme")
    s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')")
    s.wait_for_selector(".grup-baslik")

sayac = lambda s: s.locator("#sayfaCalis .ilerleme > span:last-child").inner_text()
TEMRIN, KART = ".alt-cubuk button >> nth=2", ".alt-cubuk button >> nth=3"

with sync_playwright() as p:
    c, s = cihaz_ac(p, "V", kalici=True)
    s.goto("about:blank")
    giris(s)
    # ---------------- Temrin ----------------
    s.click(TEMRIN); s.wait_for_timeout(300)
    s.evaluate("ids => { derinlesGit(calisMenusuCiz); oturumBaslat(ids.map(id => SORU_HARITASI.get(id)), 'Deneme temrini'); }", dy_ids)
    s.wait_for_selector("#sayfaCalis .soru")
    s.click("#sayfaCalis .secenek >> nth=0"); s.click("button:has-text('Sonraki soru')")
    kontrol("2. soruda", sayac(s) == "2/3", sayac(s))
    s.click(TEMRIN); s.wait_for_timeout(400)
    kontrol("Temrin sekmesine dokununca menü ve Devam et (2/3)", s.locator("#sayfaCalis .devam-satiri").count() == 1 and "2/3" in s.inner_text("#sayfaCalis .devam-satiri"))
    s.click("#sayfaCalis .devam")
    kontrol("Devam et 2. sorudan sürdürür", sayac(s) == "2/3")
    s.click("#sayfaCalis .secenek >> nth=1")
    s.go_back(); s.wait_for_timeout(400)
    kontrol("oturumda geri: uygulamadan çıkmaz, menüye döner", s.url.startswith(KOK) and s.locator("#sayfaCalis .devam-satiri").count() == 1)
    kontrol("cevaplanmış soru geçilir: Devam 3/3", "3/3" in s.inner_text("#sayfaCalis .devam-satiri"), s.inner_text("#sayfaCalis .devam-satiri"))
    # Oku'ya gidip dönmek de bozmaz
    s.click(".alt-cubuk button >> nth=0"); s.wait_for_timeout(200); s.click(TEMRIN); s.wait_for_timeout(300)
    kontrol("sekmeler arası gidip gelince Devam et duruyor", s.locator("#sayfaCalis .devam-satiri").count() == 1)
    # Uygulama kapanıp açılınca
    s.reload(); s.wait_for_selector(".grup-baslik")
    s.click(TEMRIN); s.wait_for_timeout(400)
    kontrol("yeniden açılınca Devam et cihazdan gelir (3/3)", "3/3" in s.inner_text("#sayfaCalis .devam-satiri"))
    s.click("#sayfaCalis .devam")
    kontrol("yeniden açılıştan sonra 3. soru", sayac(s) == "3/3")
    s.click("#sayfaCalis .secenek >> nth=0"); s.click("button:has-text('Sonucu gör')")
    kontrol("sonuç ekranında 3 soru sayılır", s.inner_text(".bitis .puan").endswith("/3"))
    s.go_back(); s.wait_for_timeout(300)
    kontrol("bitince Devam et kalkar", s.locator("#sayfaCalis .devam-satiri").count() == 0)
    # ---------------- 42 Tarzı ----------------
    s.click(KART); s.wait_for_selector("#sayfaKart .eylem button.ana")
    s.evaluate("() => { depo.yaz('pg.kartKapsam', { algoritma: 'tumu' }); kartSayfasiCiz(); }"); s.wait_for_timeout(200)
    s.click("#sayfaKart .eylem button.ana"); s.wait_for_selector("#sayfaKart .deste")
    toplam = s.inner_text("#sayfaKart .ilerleme .sayac").split("/")[1]
    for bildi in (True, False):
        s.click("button:has-text('Cevabı göster')"); s.wait_for_timeout(650)
        s.click("button:has-text('Bildim')" if bildi else "button:has-text('Bilemedim')"); s.wait_for_timeout(750)
    kontrol("3. kartta", s.inner_text("#sayfaKart .ilerleme .sayac") == "3/" + toplam)
    s.click("button:has-text('Cevabı göster')"); s.wait_for_timeout(650)
    s.click(KART); s.wait_for_timeout(400)
    kontrol("42 Tarzı sekmesine dokununca Devam et (3/...)", "3/" + toplam in s.inner_text("#sayfaKart .devam-satiri"))
    s.reload(); s.wait_for_selector(".grup-baslik"); s.click(KART); s.wait_for_timeout(400)
    kontrol("yeniden açılınca deste yarımı duruyor", "3/" + toplam in s.inner_text("#sayfaKart .devam-satiri"))
    s.click("#sayfaKart .devam"); s.wait_for_selector("#sayfaKart .deste")
    kontrol("deste 3. karttan sürer, yığınlar 1/1", s.inner_text("#sayfaKart .ilerleme .sayac") == "3/" + toplam and
            s.inner_text(".yigin.bildim .sayi") == "1" and s.inner_text(".yigin.bilemedim .sayi") == "1")
    s.go_back(); s.wait_for_timeout(300)
    s.click("#sayfaKart .devam-birak")
    kontrol("× yarımı bırakır", s.locator("#sayfaKart .devam-satiri").count() == 0 and s.evaluate("() => localStorage.getItem('pg.yarimKart')") is None)
    # ---------------- Kök ekranda geri ----------------
    s.click(".alt-cubuk button >> nth=0"); s.wait_for_timeout(200)
    # Kıraat'in kökü: sekme geçmişi boş; tabanın üstünde en az bir yer tutucu (bekçi) var
    kontrol("kökte bekçi kurulu", s.evaluate("() => sekmeGecmisi('oku').length === 0 && gecmisKonumu >= 1"))
    s.go_back(); s.wait_for_timeout(250)
    kontrol("ilk geri: uyarı, uygulamada kalınır", s.url.startswith(KOK) and s.locator(".kisa-bildirim:has-text('bir daha basın')").count() == 1)
    s.wait_for_timeout(2800)
    kontrol("süre geçince bekçi yeniden kurulur", s.evaluate("() => gecmisKonumu === 1"))
    s.go_back(); s.wait_for_timeout(250)
    kontrol("yine uyarı", s.url.startswith(KOK))
    s.go_back(); s.wait_for_timeout(600)
    kontrol("hemen ikinci geri: uygulamadan çıkılır", s.url == "about:blank", s.url)
    kontrol("sayfa hatası yok", not hatalar, hatalar[:3])
print(sum(1 for _, k in sonuclar if k), "/", len(sonuclar))

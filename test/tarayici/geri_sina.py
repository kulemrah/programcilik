"""Her sekmenin kendi geri geçmişi.
Telefonun geri tuşu da sayfadaki geri düğmeleri de yalnızca bulunulan sekmenin
geçmişinden bir adım geri alır; arada başka sekmeye gidip gelmek bir şey
değiştirmez. Sekmenin kökünde geri → Kıraat; Kıraat'in kökünde geri → çıkış uyarısı.
Sekmeler arası atlama (sorudan "konuda oku"): geri → gelinen yer; atlamadan sonra
başka sekmeye geçilirse açılan konu Kıraat'in kendi ekranı olur."""
exec(open("vt_taban.py", encoding="utf-8").read())

SEKME = "() => aktifSekme"
OKU_ADI = "Kıraat"

def giris(s):
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    kod_iste_ve_gir(s)
    s.wait_for_selector(".sozlesme")
    s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')")
    bekle_ki(s, lambda: s.evaluate("() => KONULAR.size") > 0)

def sekme(s, ad):
    s.click(".alt-cubuk button:has-text('%s')" % ad); s.wait_for_timeout(250)

def konu_secimine_gir(s):
    sekme(s, "Temrin")
    s.click("#sayfaCalis .suzgec-dugme, #sayfaCalis button:has-text('Ders ve konu seç')")
    s.wait_for_selector("#sayfaCalis button:has-text('‹ Temrin yolları')")

def geri(s):
    """Telefonun geri tuşu"""
    s.go_back(); s.wait_for_timeout(350)

def oku_ekrani(s):
    """Kıraat'te ne görünüyor: kök / ders:<id> / konu:<id>"""
    return s.evaluate("() => okuAcik === null ? 'kök' : okuAcik.tur + ':' + (okuAcik.konu || okuAcik.ders || '')")

def temrin_yollarinda_mi(s):
    try:
        s.wait_for_selector("#sayfaCalis .mod-kart", timeout=3000)
    except Exception:
        pass
    return s.evaluate(SEKME) == "calis" and s.locator("#sayfaCalis .mod-kart").count() > 0 and s.locator("#sayfaCalis button:has-text('‹ Temrin yolları')").count() == 0

with sync_playwright() as p:
    c, s = cihaz_ac(p, "G")
    giris(s)

    # 1) Bildirilen akış: konu seçimi → 42 Tarzı → Temrin → "‹ Temrin yolları"
    konu_secimine_gir(s)
    s.click(".kontrol-oge:has-text('Veritabanı') button:not(.kutucuk)")
    s.wait_for_selector("button:has-text('‹ Dersler')")
    s.click(".kontrol .kontrol-oge >> nth=1")
    s.click("button:has-text('‹ Dersler')"); s.wait_for_selector("button:has-text('‹ Temrin yolları')")
    sekme(s, "42 Tarzı")
    sekme(s, "Temrin")
    kontrol("Temrin'e dönünce konu seçimi yerinde durur", s.locator("#sayfaCalis button:has-text('‹ Temrin yolları')").count() == 1)
    s.click("#sayfaCalis button:has-text('‹ Temrin yolları')")
    kontrol("'‹ Temrin yolları' Temrin yollarına götürür (42 Tarzı'na değil)", temrin_yollarinda_mi(s), s.evaluate(SEKME))

    # 2) Aynısı "Tamam" ile; arada 42 Tarzı'nda deste de açılır
    konu_secimine_gir(s)
    sekme(s, "42 Tarzı")
    s.evaluate("() => { depo.yaz('pg.kartKapsam', { algoritma: 'tumu' }); kartSayfasiCiz(); }")
    s.click("#sayfaKart button.ana:has-text('kartla çalış')")
    s.wait_for_selector("#sayfaKart .deste")
    sekme(s, "Temrin")
    s.click("#sayfaCalis .eylem button:has-text('Tamam')")
    kontrol("'Tamam' Temrin yollarına götürür (arada deste açılmışken)", temrin_yollarinda_mi(s), s.evaluate(SEKME))
    sekme(s, "42 Tarzı")
    kontrol("42 Tarzı'na dönünce açık deste yerinde", s.locator("#sayfaKart .deste").count() == 1)
    sekme(s, "42 Tarzı")
    s.wait_for_timeout(300)
    kontrol("42 Tarzı sekmesine yeniden dokununca ana ekranına dönülür", s.evaluate(SEKME) == "kart" and s.locator("#sayfaKart .deste").count() == 0
            and s.locator("#sayfaKart button.ana:has-text('kartla çalış')").count() == 1, s.evaluate(SEKME))

    # 3) Ders konuları → başka sekme → dönüş → "‹ Dersler" → "‹ Temrin yolları"
    konu_secimine_gir(s)
    s.click(".kontrol-oge:has-text('Algoritma') button:not(.kutucuk)")
    s.wait_for_selector("button:has-text('‹ Dersler')")
    sekme(s, OKU_ADI)
    sekme(s, "Temrin")
    s.click("button:has-text('‹ Dersler')")
    s.wait_for_timeout(400)
    kontrol("'‹ Dersler' konu seçimine götürür", s.evaluate(SEKME) == "calis" and s.locator("#sayfaCalis button:has-text('‹ Temrin yolları')").count() == 1, s.evaluate(SEKME))
    s.click("#sayfaCalis button:has-text('‹ Temrin yolları')")
    kontrol("ardından '‹ Temrin yolları' Temrin yollarına götürür", temrin_yollarinda_mi(s), s.evaluate(SEKME))

    # 4) Temrin'in kökünde telefonun geri tuşu → Kıraat (önceki sekme 42 Tarzı olsa da)
    sekme(s, "42 Tarzı"); sekme(s, "Temrin")
    geri(s)
    kontrol("Temrin kökünde geri tuşu Kıraat'e götürür", s.evaluate(SEKME) == "oku", s.evaluate(SEKME))

    # 5) Sıradan durum bozulmadı: doğrudan girilen konu seçiminden geri
    konu_secimine_gir(s)
    s.click("#sayfaCalis button:has-text('‹ Temrin yolları')")
    kontrol("doğrudan girilen konu seçiminden geri: Temrin yolları", temrin_yollarinda_mi(s), s.evaluate(SEKME))

    # 6) Alt çubuk: Oku sekmesinin adı Kıraat
    etiketler = s.locator(".alt-cubuk button span").all_inner_texts()
    kontrol("alt çubuk: Kıraat, Ara, Temrin, 42 Tarzı, Notlar", etiketler == ["Kıraat", "Ara", "Temrin", "42 Tarzı", "Notlar"], etiketler)

    # 7) 42 Tarzı'nın eski çip seçimi bir kez yeni seçime taşınır
    tasi = """([ders, konular]) => { depo.sil('pg.kartKapsam'); depo.yaz('pg.kartDers', ders);
        depo.yaz('pg.kartKonular', konular); kartSayfasiCiz();
        return [JSON.stringify(depo.oku('pg.kartKapsam', null)), depo.oku('pg.kartDers', null), depo.oku('pg.kartKonular', null)]; }"""
    vt = [k["id"] for k in sorted([k for k in YUK["konular"] if k["ders"] == "veritabani"], key=lambda k: k["sira"])]
    r = s.evaluate(tasi, ["veritabani", {"veritabani": vt[:2]}])
    kontrol("eski seçim (ders + 2 konu) taşınır, eski anahtarlar silinir", json.loads(r[0]) == {"veritabani": vt[:2]} and r[1] is None and r[2] is None, r)
    r = s.evaluate(tasi, ["veritabani", {}])
    kontrol("eski seçim (yalnız ders) dersin tamamı olur", json.loads(r[0]) == {"veritabani": "tumu"}, r)
    r = s.evaluate(tasi, ["tumu", {}])
    kartli = sorted({k["ders"] for k in YUK["konular"] if k["kartlar"] and k["ders"] != "born2beroot"})
    kontrol("eski 'Hepsi' kartlı bütün dersler olur", sorted(json.loads(r[0]).keys()) == kartli and set(json.loads(r[0]).values()) == {"tumu"}, r)
    r = s.evaluate("() => { depo.sil('pg.kartKapsam'); depo.sil('pg.kartDers'); kartSayfasiCiz(); return JSON.stringify(depo.oku('pg.kartKapsam', null)); }")
    kontrol("eski seçim yoksa 42 Tarzı seçimsiz başlar", r == "{}", r)

    # 8) Bildirilen akış: Kıraat'te konu → Temrin → Kıraat → geri tuşu → ders listesi → kök → çıkış uyarısı
    VT = sorted([k for k in YUK["konular"] if k["ders"] == "veritabani"], key=lambda k: k["sira"])
    sekme(s, OKU_ADI); sekme(s, OKU_ADI)       # Kıraat'in köküne
    s.click(".ders-satiri:has-text('Veritabanı')"); s.wait_for_selector(".agac .dal")
    s.click(".agac .dal >> nth=2"); s.wait_for_selector(".okuma h2")
    kontrol("Kıraat'te konu açık", oku_ekrani(s) == "konu:" + VT[2]["id"], oku_ekrani(s))
    sekme(s, "Temrin"); sekme(s, "42 Tarzı"); sekme(s, OKU_ADI)
    kontrol("Kıraat'e dönünce konu yerinde", oku_ekrani(s) == "konu:" + VT[2]["id"] and s.locator("#sayfaOku .okuma h2").count() == 1, oku_ekrani(s))
    geri(s)
    kontrol("geri tuşu: Kıraat'in ders listesi (Temrin'e değil)", s.evaluate(SEKME) == "oku" and oku_ekrani(s) == "ders:veritabani", (s.evaluate(SEKME), oku_ekrani(s)))
    geri(s)
    kontrol("geri tuşu: Kıraat'in kökü", s.evaluate(SEKME) == "oku" and oku_ekrani(s) == "kök", oku_ekrani(s))
    geri(s)
    kontrol("Kıraat kökünde geri: çıkış uyarısı, uygulama yerinde", s.evaluate(SEKME) == "oku" and s.evaluate("() => gecmisKonumu") == 0
            and "Çıkmak için" in s.evaluate("() => (document.querySelector('.kisa-bildirim') || {}).textContent || ''"), s.evaluate("() => gecmisKonumu"))
    s.wait_for_timeout(2800)
    kontrol("uyarı süresi geçince bekçi yeniden kurulur", s.evaluate("() => gecmisKonumu") == 1)

    # 9) Aynısı sayfadaki '‹ Geri' düğmesiyle
    s.click(".ders-satiri:has-text('Veritabanı')"); s.wait_for_selector(".agac .dal")
    s.click(".agac .dal >> nth=1"); s.wait_for_selector(".okuma h2")
    sekme(s, "Ara"); sekme(s, OKU_ADI)
    s.click("#sayfaOku button.geri:has-text('‹ Geri')"); s.wait_for_timeout(350)
    kontrol("'‹ Geri' de ders listesine götürür", s.evaluate(SEKME) == "oku" and oku_ekrani(s) == "ders:veritabani", oku_ekrani(s))

    # 10) Her sekme kendi yerinde: Kıraat konu, Temrin konu seçimi; ikisi arasında gidip gelip geri
    s.click(".agac .dal >> nth=3"); s.wait_for_selector(".okuma h2")
    konu_secimine_gir(s)
    sekme(s, OKU_ADI); sekme(s, "Temrin")
    geri(s)
    kontrol("Temrin'de geri tuşu Temrin yollarına (Kıraat'e değil)", temrin_yollarinda_mi(s), s.evaluate(SEKME))
    sekme(s, OKU_ADI)
    geri(s)
    kontrol("Kıraat'te geri tuşu ders listesine", s.evaluate(SEKME) == "oku" and oku_ekrani(s) == "ders:veritabani", oku_ekrani(s))

    # 11) Sorudan 'konuda oku': geri → soru; Kıraat önceki konusuna kavuşur
    s.click(".agac .dal >> nth=4"); s.wait_for_selector(".okuma h2")
    once = oku_ekrani(s)
    sekme(s, "Temrin")
    s.evaluate("() => { kapsamYaz({ veritabani: 'tumu' }); calisMenusuCiz(); }")
    s.click(".mod-kart:has-text('Sınav provası')"); s.wait_for_selector(".ilerleme")
    soru_id = s.evaluate("() => oturum.sorular[oturum.i].id")
    s.evaluate("() => { const s = oturum.sorular[oturum.i]; s.yer = s.yer || null; }")
    s.evaluate("() => document.getElementById('sayfaCalis').appendChild(konudaOkuDugmesi(oturum.sorular[oturum.i], 'test-konuda-oku'))")
    s.click("#sayfaCalis .test-konuda-oku"); s.wait_for_timeout(350)
    hedef = s.evaluate("() => oturum.sorular[oturum.i].konu.id")
    kontrol("'konuda oku' Kıraat'te sorunun konusunu açar", s.evaluate(SEKME) == "oku" and oku_ekrani(s) == "konu:" + hedef, (s.evaluate(SEKME), oku_ekrani(s)))
    geri(s)
    kontrol("geri tuşu soruya döner (aynı soru)", s.evaluate(SEKME) == "calis" and s.evaluate("() => oturum && oturum.sorular[oturum.i].id") == soru_id, s.evaluate(SEKME))
    sekme(s, OKU_ADI)
    kontrol("Kıraat atlamadan önceki konusunda", oku_ekrani(s) == once, (oku_ekrani(s), once))

    # 12) Atlamadan sonra başka sekmeye geçilirse konu Kıraat'in olur: geri → o konunun dersi
    sekme(s, "Temrin")
    s.evaluate("() => document.getElementById('sayfaCalis').appendChild(konudaOkuDugmesi(oturum.sorular[oturum.i], 'test-konuda-oku2'))")
    s.click("#sayfaCalis .test-konuda-oku2"); s.wait_for_timeout(350)
    sekme(s, "42 Tarzı"); sekme(s, OKU_ADI)
    kontrol("sahiplenilen konu Kıraat'te açık", oku_ekrani(s) == "konu:" + hedef, oku_ekrani(s))
    geri(s)
    ders = s.evaluate("(id) => KONULAR.get(id).ders", hedef)
    kontrol("geri tuşu sahiplenilen konunun dersine (Temrin'e değil)", s.evaluate(SEKME) == "oku" and oku_ekrani(s) == "ders:" + ders, (s.evaluate(SEKME), oku_ekrani(s)))

    # 13) Kaplama: çekmece açıkken geri tuşu yalnızca çekmeceyi kapatır
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    geri(s); s.wait_for_timeout(400)
    kontrol("çekmece geri tuşuyla kapanır, ekran yerinde", s.locator(".hesap-sayfa.acik").count() == 0 and oku_ekrani(s) == "ders:" + ders, oku_ekrani(s))

    # 14) 42 Tarzı: deste → Kıraat → 42 Tarzı → geri tuşu → 42 Tarzı ana ekranı
    sekme(s, "42 Tarzı")
    s.evaluate("() => { depo.yaz('pg.kartKapsam', { algoritma: 'tumu' }); kartSayfasiCiz(); }")
    s.click("#sayfaKart button.ana:has-text('kartla çalış')"); s.wait_for_selector("#sayfaKart .deste")
    sekme(s, OKU_ADI); sekme(s, "42 Tarzı")
    geri(s)
    kontrol("destede geri tuşu 42 Tarzı ana ekranına", s.evaluate(SEKME) == "kart" and s.locator("#sayfaKart .deste").count() == 0 and s.locator("#sayfaKart button.ana:has-text('kartla çalış')").count() == 1, s.evaluate(SEKME))
    geri(s)
    kontrol("42 Tarzı kökünde geri tuşu Kıraat'e", s.evaluate(SEKME) == "oku", s.evaluate(SEKME))

kontrol("sayfa hatası yok", not hatalar, hatalar)
gecen = sum(1 for _, k in sonuclar if k)
print("\n%d/%d geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) else 1)

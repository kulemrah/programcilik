"""Sayfa içi geri düğmeleri sekme değiştirince başka sekmeye atmasın.
Hata: Temrin'de konu seçimindeyken 42 Tarzı'na geçip Temrin'e dönülünce
"‹ Temrin yolları" ya da "Tamam" Temrin yollarına değil 42 Tarzı'na atıyordu.
Telefonun geri tuşu ise geçmişi izler (önceki sekmeye dönebilir); bu ayrıca denetlenir."""
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

    # 4) Geçmiş ile yığın aynı hizada kalmalı: telefonun geri tuşu Temrin kökünden önceki sekmeye döner
    sekme(s, "42 Tarzı"); sekme(s, "Temrin")
    s.go_back(); s.wait_for_timeout(400)
    kontrol("telefonun geri tuşu Temrin kökünden önceki sekmeye (42 Tarzı) döner", s.evaluate(SEKME) == "kart", s.evaluate(SEKME))
    hiza = s.evaluate("() => [geriYigini.length, history.state && history.state.pg]")
    kontrol("geçmiş adımı ile yığın aynı hizada", hiza[0] == (hiza[1] or 0), hiza)

    # 5) Sıradan durum bozulmadı: doğrudan girilen konu seçiminden geri
    konu_secimine_gir(s)
    s.click("#sayfaCalis button:has-text('‹ Temrin yolları')")
    kontrol("doğrudan girilen konu seçiminden geri: Temrin yolları", temrin_yollarinda_mi(s), s.evaluate(SEKME))

    # 6) Alt çubuk: Oku sekmesinin adı Kıraat
    etiketler = s.locator(".alt-cubuk button span").all_inner_texts()
    kontrol("alt çubuk: Kıraat, Ara, Temrin, 42 Tarzı", etiketler == ["Kıraat", "Ara", "Temrin", "42 Tarzı"], etiketler)

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

kontrol("sayfa hatası yok", not hatalar, hatalar)
gecen = sum(1 for _, k in sonuclar if k)
print("\n%d/%d geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) else 1)

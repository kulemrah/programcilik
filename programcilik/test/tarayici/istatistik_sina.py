"""Hesap sayfası: ad-soyad, süre ölçümü, istatistik toplama ve çizimler."""
exec(open("vt_taban.py", encoding="utf-8").read())
import os
D["hususi"] = True
G = int(os.environ.get("GENISLIK", "390"))
alg = sorted([k for k in YUK["konular"] if k["ders"] == "algoritma"], key=lambda k: k["sira"])
K1, K2 = alg[0]["id"], alg[1]["id"]
vt = sorted([k for k in YUK["konular"] if k["ders"] == "veritabani"], key=lambda k: k["sira"])[0]["id"]

def giris(s):
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    s.fill("#girisEposta", EPOSTA); s.click("button:has-text('Kod gönder')")
    s.wait_for_selector("#girisKod"); s.fill("#girisKod", "123456"); s.click("button:has-text('Giriş yap')")
    s.wait_for_selector(".sozlesme")
    kontrol("sözleşmede yeni madde (çalışma süreleri, ad soyad)", "çalıştığım süreler" in s.inner_text(".sozlesme") and "adım soyadım" in s.inner_text(".sozlesme"))
    s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')")
    s.wait_for_selector(".grup-baslik")

with sync_playwright() as p:
    c, s = cihaz_ac(p, "T")
    s.set_viewport_size({"width": G, "height": 800})
    giris(s)
    kontrol("profil sözleşme sürümü 2", D["profil"]["sozlesme_surumu"] == "2", D["profil"])
    # ---- Okuma süresi ----
    s.evaluate("id => konuAc(id)", K1); s.wait_for_selector(".okuma h2")
    tik = "n => { for (let i = 0; i < n; i++) { sonTik = Date.now() - 5000; sonDokunus = Date.now(); calismaTiki(); } }"
    s.evaluate(tik, 6)
    o = s.evaluate("id => { const g = calismaBirikimi.get(gunAnahtari(Date.now())); return g && g.o ? g.o[id] : 0 }", K1)
    kontrol("okurken süre birikir (~30 sn)", 29 <= o <= 31, o)
    s.evaluate("() => { sonTik = Date.now() - 5000; sonDokunus = Date.now() - 200000; calismaTiki(); }")
    o2 = s.evaluate("id => calismaBirikimi.get(gunAnahtari(Date.now())).o[id]", K1)
    kontrol("uzun süre dokunulmazsa sayılmaz", abs(o2 - o) < 0.01, (o, o2))
    s.evaluate("() => { sonTik = Date.now() - 60000; sonDokunus = Date.now(); calismaTiki(); }")
    o3 = s.evaluate("id => calismaBirikimi.get(gunAnahtari(Date.now())).o[id]", K1)
    kontrol("telefon uyuduysa aradaki süre sayılmaz", abs(o3 - o) < 0.01, (o, o3))
    s.evaluate("() => sesDurumu = { duraklatildi: false }")
    s.evaluate("() => { sonTik = Date.now() - 5000; sonDokunus = Date.now() - 200000; calismaTiki(); sesDurumu = null; }")
    o4 = s.evaluate("id => calismaBirikimi.get(gunAnahtari(Date.now())).o[id]", K1)
    kontrol("sesli okuma sürerken dokunmadan da sayılır", 4.9 <= o4 - o <= 5.1, (o, o4))
    # Liste ekranında sayılmaz
    s.click("text=‹ Geri"); s.wait_for_selector(".agac .dal")
    s.evaluate(tik, 3)
    o5 = s.evaluate("id => calismaBirikimi.get(gunAnahtari(Date.now())).o[id]", K1)
    kontrol("konu listesinde süre sayılmaz", abs(o5 - o4) < 0.01, (o4, o5))
    # ---- Temrin: süre ve doğru/yanlış ----
    s.click(".alt-cubuk button >> nth=2"); s.wait_for_timeout(300)
    s.evaluate("""id => { const sorular = TUM_SORULAR.filter(x => x.konu.id === id && x.tip === 'dy').slice(0, 2);
                          oturumBaslat(sorular, 'deneme'); }""", K2)
    s.wait_for_selector("#sayfaCalis .soru")
    s.evaluate(tik, 2)
    t = s.evaluate("id => calismaBirikimi.get(gunAnahtari(Date.now())).t[id]", K2)
    kontrol("soru çözerken temrin süresi birikir", 9.9 <= t <= 10.1, t)
    s.evaluate("() => { sonucIsle(oturum.sorular[0], true); oturum.i = 1; sonucIsle(oturum.sorular[1], false); }")
    dy = s.evaluate("id => { const g = calismaBirikimi.get(gunAnahtari(Date.now())); return [g.d[id], g.y[id]] }", K2)
    kontrol("temrinde 1 doğru 1 yanlış sayıldı", dy == [1, 1], dy)
    # ---- Kayda yazım ve hesaba gönderim ----
    s.evaluate("() => calismaYaz()")
    anahtar = s.evaluate("() => gunAnahtari(Date.now()) + '|' + YAZICI")
    deger = s.evaluate("a => kayit('calisma', a)", anahtar)
    kontrol("günlük kayıt yazıldı (tam saniye)", deger and deger["o"][K1] == int(o4) and deger["d"][K2] == 1 and deger["y"][K2] == 1, deger)
    kontrol("kayıt hemen gönderilmez (sessiz)", s.evaluate("a => !KAYITLAR.get('calisma|' + a).gonderildi", anahtar))
    s.evaluate("() => esitle()")
    kontrol("kayıt eşitlemeyle hesaba gitti", bekle_ki(s, lambda: ("calisma", anahtar) in D["kayitlar"]))
    s.evaluate(tik, 2); s.evaluate("() => calismaYaz()")
    deger2 = s.evaluate("a => kayit('calisma', a)", anahtar)
    kontrol("ikinci yazım üstüne eklenir", deger2["t"][K2] == deger["t"].get(K2, 0) + 10, (deger["t"], deger2["t"]))
    # Başka cihazın ve geçmiş günlerin kayıtları
    # Hedef günde 15 dk: bugün (~935 sn), dün (1800), önceki gün (900+400) hedefte → seri 3
    s.evaluate("() => kayitYaz('ayar', 'hedef', { gecmis: [{ g: '2026-01-01', gun: 900, hafta: 6300 }] })")
    s.evaluate("""([k1, vt, k2]) => {
      const bugun = gunAnahtari(Date.now());
      kayitYaz('calisma', bugun + '|baska001', { o: { [k1]: 600 }, k: { [vt]: 300 }, b: { [vt]: 3 }, n: { [vt]: 1 } }, true);
      kayitYaz('calisma', gunEkle(bugun, -1) + '|baska001', { o: { [k1]: 1800 } }, true);
      kayitYaz('calisma', gunEkle(bugun, -2) + '|baska001', { t: { [vt]: 900, [k2]: 400 } }, true);
      kayitYaz('calisma', gunEkle(bugun, -5) + '|baska001', { o: { [vt]: 4000 } }, true);
      kayitYaz('calisma', '2026-01-01|baska001', { o: { 'yok-konu': 500 } }, true);
    }""", [K1, vt, K2])
    ist = s.evaluate("""() => { const i = istatistikTopla(gunEkle(gunAnahtari(Date.now()), -6)); const t = istatistikTopla(null);
      return { alg: i.dersler.get('algoritma'), vt: i.dersler.get('veritabani'), seri: seriHesapla(t.gunler), gun: t.gunler.size } }""")
    kontrol("cihazlar toplanır (algoritma okuma)", ist["alg"]["o"] == int(o4) + 600 + 1800, ist["alg"])
    kontrol("kart sayıları ve süresi toplandı", ist["vt"]["k"] == 300 and ist["vt"]["b"] == 3 and ist["vt"]["n"] == 1, ist["vt"])
    kontrol("seri 3 gün (bugün, dün, önceki gün hedefte)", ist["seri"]["n"] == 3, ist["seri"])
    kontrol("bugünkü temrin süresi (K2 ~20 sn < 3 dk) sayılmaz, doğru/yanlış sayılır",
            ist["alg"].get("t") == 400 and ist["alg"].get("d") == 1 and ist["alg"].get("y") == 1, {k: ist["alg"].get(k) for k in "otdy"})
    # ---- Hesap sayfası ----
    cekmece(s, "hesap")
    kontrol("ad yokken 'Adınızı ekleyin'", "Adınızı ekleyin" in s.inner_text(".profil-ad"))
    kontrol("avatar e-postanın baş harfi", s.inner_text(".profil-avatar") == "O")
    s.click(".profil-duzenle"); s.fill("#kimlikAd", "  Hamza  "); s.fill("#kimlikSoyad", "Topaktaş"); s.click(".profil-form button:has-text('Kaydet')")
    kontrol("ad soyad görünür", s.inner_text(".profil-ad") == "Hamza Topaktaş")
    kontrol("avatar baş harfler HT", s.inner_text(".profil-avatar") == "HT")
    kontrol("kimlik hesaba gitti", bekle_ki(s, lambda: D["kayitlar"].get(("ayar", "kimlik"), {}).get("deger") == {"ad": "Hamza", "soyad": "Topaktaş"} if isinstance(D["kayitlar"].get(("ayar", "kimlik")), dict) else ("ayar", "kimlik") in D["kayitlar"]))
    cekmece(s, "istatistik")
    s.click(".cip:has-text('7 gün')")
    kutular = s.locator(".ist-kutu").all_inner_texts()
    kontrol("4 özet kutusu", len(kutular) == 4, kutular)
    kontrol("seri kutusu 3 gün", "3 gün" in kutular[1], kutular[1])
    kontrol("temrin kutusu %50", "%50" in kutular[2], kutular[2])
    kontrol("42 Tarzı kutusu %75", "%75" in kutular[3], kutular[3])
    kontrol("halka çizildi (ders ve konu dilimleri)", s.locator(".halka-svg .ders-dilim").count() == 2 and s.locator(".halka-svg .konu-dilim").count() >= 3, s.locator(".halka-svg .ders-dilim").count())
    satirlar = s.locator(".halka-satir .halka-ad").all_inner_texts()
    kontrol("listede en çok çalışılan ders önde", satirlar[0].startswith("Veritabanı") or satirlar[0].startswith("Algoritma"), satirlar)
    s.click(".halka-satir >> nth=0 >> .halka-ust")
    kontrol("satıra dokununca konular açılır, öbür dilimler soluklaşır", s.locator(".halka-konular:visible").count() == 1 and s.locator(".halka-svg .dilim.soluk").count() > 0)
    s.click(".halka-suzgec .cip:has-text('42 Tarzı')")
    kontrol("42 Tarzı süzgecinde yalnızca veritabanı", s.locator(".halka-satir").count() == 1 and "Veritabanı" in s.inner_text(".halka-satir"))
    s.click(".halka-suzgec .cip:has-text('Hepsi')")
    kontrol("14 gün çubukları", s.locator(".cubuk-svg .isabet").count() == 14 and s.locator(".cubuk-svg path.cubuk").count() == 4, s.locator(".cubuk-svg path.cubuk").count())
    kontrol("silinmiş konunun süresi dersleri bozmaz", s.locator(".halka-satir").count() == 2)
    s.click(".cip:has-text('Bugün')")
    k1 = s.locator(".ist-kutu >> nth=0").inner_text()
    kontrol("Bugün dönemi bugünü sayar", "bugün" in k1, k1)
    # İpucu
    s.locator(".cubuk-svg").scroll_into_view_if_needed()
    box = s.locator(".cubuk-svg .isabet >> nth=13").bounding_box()
    s.mouse.move(box["x"] + box["width"] / 2, box["y"] + 40)
    kontrol("çubuğun üstünde ipucu", s.locator(".cubuk-cizim .viz-ipucu:visible").count() == 1 and "Okuma" in s.inner_text(".cubuk-cizim .viz-ipucu"))
    # Taşma (her ekranda)
    tasma_bul = "() => { const g = document.querySelector('.hesap-govde'); const r = []; g.querySelectorAll('*').forEach(e => { const b = e.getBoundingClientRect(); if (b.width && b.right > window.innerWidth + 1 && !e.closest('.cip-satiri')) r.push(e.className.baseVal !== undefined ? e.className.baseVal : e.className); }); return r.slice(0, 5) }"
    for ekr in ("hedef", "takvim", "hesap"):
        cekmece(s, ekr); s.wait_for_timeout(200)
        kontrol("%s ekranında yana taşma yok" % ekr, not s.evaluate(tasma_bul), s.evaluate(tasma_bul))
        if ekr == "takvim":
            kontrol("takvimde bugün işaretli (günlük ve haftalık)", s.locator(".takvim-kart:not(.hafta-kart) .hucre.bugun").count() == 1 and s.locator(".hafta-kart .hucre.bugun").count() == 1)
            kontrol("bugün hedefte (yeşil kenar)", "hedefte" in (s.get_attribute(".takvim-kart:not(.hafta-kart) .hucre.bugun", "class") or ""))
        s.screenshot(path="goruntu/ist-%d-%s.png" % (G, ekr))
    cekmece(s, "istatistik")
    tasma = s.evaluate("() => { const g = document.querySelector('.hesap-govde'); const r = []; g.querySelectorAll('*').forEach(e => { const b = e.getBoundingClientRect(); if (b.width && b.right > window.innerWidth + 1 && !e.closest('.cip-satiri')) r.push(e.className.baseVal !== undefined ? e.className.baseVal : e.className); }); return r.slice(0, 5) }")
    kontrol("hesap sayfasında yana taşma yok", not tasma, tasma)
    for t in ["gunduz", "pembe", "gece", "siyah"]:
        s.evaluate("t => moduUygula(t)", t); s.wait_for_timeout(450)
        s.screenshot(path="goruntu/ist-%d-%s-ust.png" % (G, t))
        s.evaluate("() => document.querySelector('.hesap-govde').scrollTop = 620"); s.wait_for_timeout(100)
        s.screenshot(path="goruntu/ist-%d-%s-orta.png" % (G, t))
        s.evaluate("() => document.querySelector('.hesap-govde').scrollTop = 1400"); s.wait_for_timeout(100)
        s.screenshot(path="goruntu/ist-%d-%s-alt.png" % (G, t))
        s.evaluate("() => document.querySelector('.hesap-govde').scrollTop = 0")
    s.click(".hesap-kapat"); s.wait_for_timeout(300)
    kontrol("geri ile hesap sayfası kapanır", s.locator(".hesap-sayfa").count() == 0)
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa")
    s.go_back(); s.wait_for_timeout(300)
    kontrol("telefonun geri tuşu da kapatır", s.locator(".hesap-sayfa").count() == 0 and s.locator(".giris-perde").count() == 0)
    kontrol("sayfa hatası yok", not hatalar, hatalar[:3])
print(sum(1 for _, k in sonuclar if k), "/", len(sonuclar))

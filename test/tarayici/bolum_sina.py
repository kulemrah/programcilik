"""Bölüm doğrulama kodu ve İdare.
Kodsuz hesap: girişten sonra kod ekranı (sözleşmeden önce), yanlış/biçimsiz/
süresi dolmuş/dolu kod, deneme kilidi, doğru kodla bölümün yazılması ve
sözleşme. İdare (yönetici = hususi yetkili): kod üretme, liste, kullananlar,
iptal, hesap bulma, sıfırlama; yönetici olmayan hesapta sekme yok; sıfırlanan
hesabın yeniden kod ekranına düşmesi. Sunucu tarafı test/sql/bolum-deneme.sql'de."""
exec(open("vt_taban.py", encoding="utf-8").read())

def giris_kodla(s):
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    kod_iste_ve_gir(s)

def sozlesme_kabul(s):
    s.wait_for_selector(".sozlesme")
    s.click("text=Okudum, kabul ediyorum")
    s.click("button:has-text('Kabul et ve devam et')")

def cikis(s):
    s.evaluate("() => localStorage.setItem('pg.cekmeceEkrani', JSON.stringify('hesap'))")
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    s.click(".hesap-sayfa button:has-text('Çıkış yap')")
    if s.locator(".uyari-perde").count(): s.click(".uyari-perde .evet")
    s.wait_for_selector(".giris-perde")

def sekmeler(s):
    return s.evaluate("() => [...document.querySelectorAll('.cekmece-sekme')].map(b => b.dataset.ekran)")

def kod_gir(s, kod):
    s.fill("#bolumKodu", kod)
    s.click(".giris-kutu button:has-text('Doğrula')")
    s.wait_for_function("() => !document.querySelector('.giris-kutu button.ana') || document.querySelector('.giris-kutu button.ana').textContent !== 'Doğrulanıyor…'")
    s.wait_for_timeout(150)

def hata_metni(s):
    return s.inner_text(".giris-hata") if s.locator(".giris-hata").count() else ""

def bilgi_metni(s):
    return s.inner_text(".kod-bilgisi") if s.locator(".kod-bilgisi").count() else ""

with sync_playwright() as p:
    c, s = cihaz_ac(p, "B")

    # ===== 1) Yönetici (eski hesap, hususi yetkili): İdare'den kod üretir =====
    D["hususi"] = True
    giris_kodla(s)
    sozlesme_kabul(s)
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')"); s.wait_for_selector(".grup-baslik")
    kontrol("eski hesap: kod sorulmadan sözleşmeye geçti, BP 1. sınıf", D["profil"] == {"program": BP, "sinif": 1, "sozlesme_surumu": "2"}, D["profil"])
    kontrol("üst çubuk: 'Kostü - Ders', altında bölüm adı", s.inner_text(".ust h1") == "Kostü - Ders" and s.inner_text("#ustBolum") == "Bilgisayar Programcılığı", s.inner_text(".ust-baslik"))
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    bekle_ki(s, lambda: "idare" in sekmeler(s))
    kontrol("yönetici çekmecesinde İdare sekmesi son sırada", sekmeler(s) == ["hedef", "istatistik", "takvim", "hesap", "idare"], sekmeler(s))
    s.click(".cekmece-sekme[data-ekran=idare]")
    s.wait_for_selector("#idareProgram")
    kontrol("İdare: bölüm listesi, 2 sınıf, varsayılan 2 saat ve 10 kişi",
            s.evaluate("() => [document.querySelector('#idareProgram').value, document.querySelectorAll('#idareSinif option').length, document.querySelector('#idareSaat').value, document.querySelector('#idareDakika').value, document.querySelector('#idareAzami').value]")
            == [BP, 2, "2", "0", "10"])
    kontrol("İdare: henüz kod yok", "Henüz kod üretilmedi." in s.inner_text(".hesap-ic[data-ekran=idare]"))
    s.fill("#idareSaat", "200"); s.click(".hesap-ic button.ana:has-text('Kod üret')")
    s.wait_for_selector(".hesap-ic .giris-hata")
    kontrol("İdare: 7 günü aşan süre reddedilir", "7 gün" in s.inner_text(".hesap-ic .giris-hata") and not D["kodlar"])
    s.fill("#idareSaat", "1"); s.fill("#idareDakika", "30"); s.fill("#idareAzami", "2")
    s.click(".hesap-ic button.ana:has-text('Kod üret')")
    s.wait_for_selector(".idare-sonuc")
    k0 = D["kodlar"][0]
    kontrol("İdare: kod üretildi (BP1, 90 dakika, 2 kişi)", k0["sinif"] == 1 and k0["azami"] == 2 and abs(k0["bitis"] - time.time() - 5400) < 30, k0)
    kontrol("İdare: 6 rakam ve görünen adı ekranda", s.inner_text(".idare-rakam") == k0["kod"] and s.inner_text(".idare-sonuc .idare-etiket") == "BP1_" + k0["kod"])
    sat = s.inner_text(".idare-kod[data-etiket='BP1_%s']" % k0["kod"])
    kontrol("İdare: listede Etkin; oluşturulma, süre (1 sa 30 dk), kullanım 0 / 2 kişi, bitiş",
            s.locator(".idare-kod[data-etiket='BP1_%s'] .idare-durum.etkin" % k0["kod"]).count() == 1
            and "Oluşturuldu: " in sat and "Süre: 1 sa 30 dk" in sat and "Kullanım: 0 / 2 kişi" in sat and "Bitiş: " in sat, sat)
    s.context.grant_permissions(["clipboard-read", "clipboard-write"], origin=KOK.rstrip("/"))
    s.click(".idare-sonuc .idare-kopya")
    kontrol("İdare: yeni kodun yanındaki Kopyala 6 rakamı panoya yazar",
            s.evaluate("() => navigator.clipboard.readText()") == k0["kod"] and s.inner_text(".idare-sonuc .idare-kopya") == "Kopyalandı")
    s.evaluate("() => navigator.clipboard.writeText('')")
    s.click(".idare-kod[data-etiket='BP1_%s'] .idare-kopya" % k0["kod"])
    kontrol("İdare: listedeki etkin kodun yanında Kopyala", s.evaluate("() => navigator.clipboard.readText()") == k0["kod"])
    ekran(s, "idare-kod-uretildi")
    # 2. sınıf için ikinci kod (sonra iptal edilecek)
    s.select_option("#idareSinif", "2"); s.click(".hesap-ic button.ana:has-text('Kod üret')")
    bekle_ki(s, lambda: len(D["kodlar"]) == 2)
    s.wait_for_selector(".idare-kod[data-etiket^='BP2_']")
    k2 = D["kodlar"][1]
    kontrol("İdare: 2. sınıf kodu BP2_ ile başlar", k2["etiket"].startswith("BP2_") and k2["sinif"] == 2)
    s.click(".idare-kod[data-etiket='%s'] button:has-text('İptal et')" % k2["etiket"]); onayla(s)
    s.wait_for_selector(".idare-kod[data-etiket='%s'] .idare-durum.iptal" % k2["etiket"])
    kontrol("İdare: iptal edilen kod listede 'İptal edildi', iptal ve kopyala düğmesi yok, iptal anı yazar",
            s.locator(".idare-kod[data-etiket='%s'] button:has-text('İptal et')" % k2["etiket"]).count() == 0
            and s.locator(".idare-kod[data-etiket='%s'] .idare-kopya" % k2["etiket"]).count() == 0
            and "İptal: " in s.inner_text(".idare-kod[data-etiket='%s']" % k2["etiket"]))
    # Hesap bul ve sıfırla
    s.fill("#idareEposta", "KODLU"); s.click(".hesap-ic button:has-text('Bul')")
    s.wait_for_selector(".hesap-ic button:has-text('Bölümünü sıfırla')")
    metin = s.inner_text(".hesap-ic[data-ekran=idare]")
    kontrol("hesap bul: yalnızca kullanıcı adı yazılınca okul alanı eklenip arandı", any("idare_hesap_bul" in g for g in D["gunluk"]))
    kontrol("hesap bul: bölüm, sınıf, kod, sözleşme", "Bölüm: Bilgisayar Programcılığı, 1. sınıf" in metin and "Kod: BP1_482913" in metin and "Sözleşme onaylı." in metin)
    s.click(".hesap-ic button:has-text('Bölümünü sıfırla')"); onayla(s)
    bekle_ki(s, lambda: D["sifirlanan"])
    s.wait_for_function("() => (document.querySelector('.hesap-ic .giris-bilgi') || {}).textContent?.includes('sıfırlandı')")
    kontrol("sıfırlama sunucuya gitti, bilgi yazıldı", D["sifirlanan"] == ["22222222-2222-2222-2222-222222222222"] and "sıfırlandı" in s.inner_text(".hesap-ic .giris-bilgi"))
    s.fill("#idareEposta", "yok@kocaelisaglik.edu.tr"); s.click(".hesap-ic button:has-text('Bul')")
    s.wait_for_function("() => document.querySelector('.hesap-ic[data-ekran=idare]').innerText.includes('hesap yok')")
    kontrol("hesap bul: olmayan adres", True)
    # Hibrit kodu: en son kod açıkta, öncekiler Mazi'de
    s.select_option("#idareProgram", HE); s.wait_for_timeout(200)
    kontrol("İdare: Hibrit seçilince 2 sınıf", s.locator("#idareSinif option").count() == 2)
    s.click(".hesap-ic button.ana:has-text('Kod üret')")
    bekle_ki(s, lambda: len(D["kodlar"]) == 3)
    k3 = D["kodlar"][2]
    s.wait_for_selector(".idare-kod[data-etiket='%s']" % k3["etiket"])
    kontrol("Hibrit kodu HE1_ ile başlar, Son kod'da yalnızca o", k3["etiket"].startswith("HE1_") and k3["program"] == HE
            and s.locator(".hesap-ic .idare-kod").count() == 1)
    kontrol("Mazi düğmesi önceki 2 kodu sayar", s.inner_text(".idare-mazi") == "Mazi (2 kod)", s.inner_text(".idare-mazi"))
    s.click(".idare-mazi"); s.wait_for_selector("#maziPerde")
    mz = lambda: s.evaluate("() => [...document.querySelectorAll('#maziPerde .idare-kod')].map(e => e.dataset.etiket)")
    kontrol("Mazi: iki önceki kod, yeniden eskiye", mz() == [k2["etiket"], k0["etiket"]], mz())
    s.select_option("#maziPerde label:has-text('Sınıf') select", "2"); s.wait_for_timeout(150)
    kontrol("Mazi: sınıf süzgeci (2. sınıf)", mz() == [k2["etiket"]], mz())
    s.select_option("#maziPerde label:has-text('Bölüm') select", HE); s.wait_for_timeout(150)
    kontrol("Mazi: bölüm süzgeci (Hibrit: önceki kod yok)", mz() == [] and "Bu süzgece uyan kod yok." in s.inner_text("#maziPerde"), mz())
    s.click("#maziPerde button:has-text('Süzgeci temizle')"); s.wait_for_timeout(150)
    dun = s.evaluate("() => new Date(Date.now() - 86400000).toLocaleDateString('sv-SE', { timeZone: 'Europe/Istanbul' })")
    s.fill("#maziPerde label:has-text('bitiş') input", dun); s.dispatch_event("#maziPerde label:has-text('bitiş') input", "change"); s.wait_for_timeout(150)
    kontrol("Mazi: tarih süzgeci (dün ve öncesi: yok)", mz() == [], mz())
    bugun = s.evaluate("() => new Date().toLocaleDateString('sv-SE', { timeZone: 'Europe/Istanbul' })")
    s.fill("#maziPerde label:has-text('başlangıç') input", bugun); s.dispatch_event("#maziPerde label:has-text('başlangıç') input", "change")
    s.fill("#maziPerde label:has-text('bitiş') input", bugun); s.dispatch_event("#maziPerde label:has-text('bitiş') input", "change"); s.wait_for_timeout(150)
    kontrol("Mazi: tarih süzgeci (bugün: ikisi)", len(mz()) == 2, mz())
    ekran(s, "idare-mazi")
    s.keyboard.press("Escape"); s.wait_for_timeout(200)
    kontrol("Escape Mazi'yi kapatır, çekmece açık kalır", s.locator("#maziPerde").count() == 0 and s.locator(".hesap-sayfa.acik").count() == 1)
    # Siyah temada seçim kutularının yazısı okunur
    s.evaluate("() => document.documentElement.setAttribute('data-mod', 'siyah')"); s.wait_for_timeout(100)
    renk = s.evaluate("() => [getComputedStyle(document.querySelector('#idareProgram')).color, getComputedStyle(document.querySelector('#idareSaat')).color]")
    kontrol("siyah temada Bölüm/Sınıf yazısı Süre kutusuyla aynı (açık) renk", renk[0] == renk[1] and renk[0] != "rgb(0, 0, 0)", renk)
    ekran(s, "idare-siyah")
    s.evaluate("() => document.documentElement.setAttribute('data-mod', 'gunduz')")
    s.set_viewport_size({"width": 358, "height": 800}); s.wait_for_timeout(300)
    tasma = s.evaluate("() => { const g = document.querySelector('.hesap-govde'); return g.scrollWidth - g.clientWidth; }")
    kontrol("358 px'te İdare yatay taşmaz", tasma <= 1, tasma)
    s.evaluate("() => document.querySelector('.hesap-govde').scrollTo(0, 0)")
    ekran(s, "idare-358")
    s.set_viewport_size({"width": 390, "height": 820})
    s.keyboard.press("Escape"); s.wait_for_timeout(400)
    cikis(s)
    kontrol("çıkışta yönetici bilgisi silinir", s.evaluate("() => localStorage.getItem('pg.yonetici')") is None)

    # ===== 2) Yeni öğrenci (kodsuz): kod ekranı sözleşmeden önce =====
    D["hususi"] = False; D["kodsuz"] = True; D["profil"] = None
    D["oturumlar"].clear(); D["yerler"].clear(); time.sleep(SUNUCU_KOD_ARALIGI)
    giris_kodla(s)
    s.wait_for_selector("#bolumKodu")
    kontrol("kod ekranı: başlık ve sözleşme henüz yok",
            s.inner_text(".giris-baslik") == "Bölüm doğrulama kodu" and s.locator(".sozlesme").count() == 0)
    ekran(s, "bolum-kodu")
    kod_gir(s, "12")
    kontrol("biçimsiz kod: 6 rakam uyarısı, sunucuya gitmez", "6 rakam" in hata_metni(s) and D["yanlis"] == 0)
    kod_gir(s, "000001")
    kontrol("yanlış kod: 4 hak kaldı", hata_metni(s) == "Kod yanlış. 4 deneme hakkınız kaldı.", hata_metni(s))
    kod_gir(s, k2["kod"])
    kontrol("iptal edilmiş kod yanlış sayılır (3 hak)", hata_metni(s) == "Kod yanlış. 3 deneme hakkınız kaldı.", hata_metni(s))
    eski_bitis = k0["bitis"]; k0["bitis"] = time.time() - 1
    kod_gir(s, k0["kod"])
    kontrol("süresi dolan kod: bilgilendirici mesaj, hata değil, deneme sayılmaz",
            bilgi_metni(s) == "Bu kodun geçerlilik süresi dolmuş, artık kullanılamaz. Kodu aldığınız kişiden yeni bir kod isteyin." and not hata_metni(s) and D["yanlis"] == 2, (bilgi_metni(s), D["yanlis"]))
    ekran(s, "bolum-suresi-doldu")
    k0["bitis"] = eski_bitis
    D["yanlis"] = 0
    s.reload(); s.wait_for_selector("#bolumKodu")
    kontrol("yenileyince yine kod ekranı (kod girilmeden geçilemez)", s.locator(".sozlesme").count() == 0 and s.locator(".grup-baslik").count() == 0)
    kod_gir(s, " bp1_" + k0["kod"][:3] + " " + k0["kod"][3:])
    s.wait_for_selector(".sozlesme")
    kontrol("doğru kod (yapıştırılmış tam ad): bölüm yazıldı, sözleşmeye geçti",
            D["profil"] == {"program": BP, "sinif": 1, "sozlesme_surumu": None} and "Bilgisayar Programcılığı, 1. sınıf olarak kaydedildiniz." in s.inner_text(".giris-kutu"))
    kontrol("hak düştü (1/2)", k0["kullanim"] == 1)
    ekran(s, "bolum-sozlesme")
    sozlesme_kabul(s)
    s.wait_for_selector(".not-perde, .grup-baslik")   # yama notu bu cihazda ilk oturumda görüldü
    if s.locator(".not-perde").count(): s.click("button:has-text('Anladım')")
    s.wait_for_selector(".grup-baslik")
    kontrol("sözleşme onaylandı, uygulama açıldı", D["profil"]["sozlesme_surumu"] == "2")
    s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik"); s.wait_for_timeout(500)
    kontrol("yönetici olmayan hesapta İdare yok", sekmeler(s) == ["hedef", "istatistik", "takvim", "hesap"], sekmeler(s))
    s.click(".cekmece-sekme[data-ekran=hesap]")
    kontrol("Hesap'ta bölüm ve sınıf", "Bilgisayar Programcılığı, 1. sınıf" in s.inner_text(".profil-kart"))
    s.keyboard.press("Escape"); s.wait_for_timeout(400)

    # ===== 3) Yönetici hesabı sıfırladı: yeniden açılışta kod ekranı =====
    D["profil"] = None
    s.reload()
    s.wait_for_selector("#bolumKodu", timeout=15000)
    kontrol("sıfırlanan hesap: uygulama kapanır, kod ekranı açılır", s.locator(".grup-baslik:visible").count() == 0)
    bekle_ki(s, lambda: s.evaluate("() => KONU_SATIRLARI.size") == 0)
    kontrol("sıfırlanan hesap: eski bölümün konuları ve profili cihazdan silindi",
            s.evaluate("() => KONU_SATIRLARI.size") == 0 and s.evaluate("() => vt.oku('durum', 'profil')") is None and yerel_kayit_sayisi(s) == s.evaluate("() => vt.anahtarlar('kayit').then(a => a.length)"))
    # Dolu kod ve kilit
    k0["kullanim"] = k0["azami"]
    kod_gir(s, k0["kod"])
    kontrol("dolu kod: bilgilendirici mesaj, deneme sayılmaz", bilgi_metni(s).startswith("Bu kodun kişi sınırı dolmuş, artık kullanılamaz.") and D["yanlis"] == 0, (bilgi_metni(s), D["yanlis"]))
    for _ in range(5): kod_gir(s, "000002")
    kontrol("5. yanlışta kilit: dakika uyarısı", hata_metni(s) == "Çok fazla yanlış deneme yapıldı. 15 dakika sonra yeniden deneyin.", hata_metni(s))
    kod_gir(s, "000003")
    kontrol("kilitliyken yine kilit uyarısı", "15 dakika" in hata_metni(s))

    # ===== 4) Hibrit öğrencisi: yalnızca ortak dersler =====
    D["yanlis"] = 0
    kod_gir(s, k3["kod"])
    sozlesme_kabul(s)
    s.wait_for_selector(".not-perde, .grup-baslik")
    if s.locator(".not-perde").count(): s.click("button:has-text('Anladım')")
    s.wait_for_selector(".grup-baslik")
    bekle_ki(s, lambda: s.locator(".ders-satiri").count() >= 2)
    dersler = [d for d in s.evaluate("() => [...document.querySelectorAll('.ders-satiri')].map(e => e.innerText.split('\\n')[0])") if "henüz eklenmedi" not in d]
    kontrol("Hibrit: yalnızca Algoritma ve Temel Elektrik görünür",
            len(dersler) == 2 and any("Algoritma" in d for d in dersler) and any("Elektrik" in d for d in dersler), dersler)
    kontrol("Hibrit: Veritabanı yok, konusu da cihaza inmedi",
            "Veritabanı" not in s.inner_text("#sayfaOku") and s.evaluate("() => [...KONU_SATIRLARI.keys()].every(id => /^(alg|el)-/.test(id))"),
            s.evaluate("() => [...KONU_SATIRLARI.keys()].slice(0, 5)"))
    kontrol("Hibrit: üst çubukta bölüm adı", s.inner_text("#ustBolum") == "Hibrit ve Elektrikli Araçlar Teknolojisi")
    kontrol("Hibrit: sınav takvimi yok (yalnız BP 1. sınıf)", not s.evaluate("() => (AGAC && AGAC.sinavlar || []).length"))
    ekran(s, "hibrit-ana")
    c.close()

for h in hatalar: print("  !", h)
gecen = sum(1 for _, k in sonuclar if k)
print("\nbolum: %d/%d geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) and not [h for h in hatalar if "pageerror" in h] else 1)

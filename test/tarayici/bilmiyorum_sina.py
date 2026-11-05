"""Temrin: Bilmiyorum düğmesi (her soru türü), yazım hoşgörüsü (boşluk doldurma,
klasikteki anahtar kavramlar), ilerleme çubuğu, konu notunda ilgili bölümün
yanıp sönmesi. tum_sorular_sina.py'nin düzeneğini kullanır."""
exec(open("vt_taban.py", encoding="utf-8").read())

D["hususi"] = True
KONULAR_VT = YUK["konular"]
SORULAR = [s for k in KONULAR_VT for s in k["sorular"]]
ilk = lambda tip, f=lambda q: True: next(q for q in SORULAR if q["tip"] == tip and f(q))

def giris(s):
    s.goto(KOK)
    s.wait_for_selector(".giris-perde")
    s.fill("#girisEposta", EPOSTA)
    s.click("button:has-text('Kod gönder')")
    s.wait_for_selector("#girisKod")
    s.fill("#girisKod", "123456")
    s.click("button:has-text('Giriş yap')")
    s.wait_for_selector(".sozlesme")
    s.click("text=Okudum, kabul ediyorum")
    s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde")
    s.click("button:has-text('Anladım')")
    s.wait_for_selector(".grup-baslik")

def tek_soru(s, sid):
    s.evaluate("""(sid) => { derinlesGit(calisMenusuCiz);
      oturumBaslat(TUM_SORULAR.filter(q => q.id === sid).concat(TUM_SORULAR.filter(q => q.id !== sid).slice(0, 3)), 'Deneme'); }""", sid)
    s.wait_for_selector("#sayfaCalis .soru")

def sonuc(s):
    return s.evaluate("() => ({ dogru: oturum.dogru, yanlis: oturum.yanlislar.length, defter: !!kayit('yanlis', oturum.sorular[0].id) })")

with sync_playwright() as p:
    c, s = cihaz_ac(p, "B")
    giris(s)
    bekle_ki(s, lambda: s.locator(".ders-satiri:has-text('Born2beRoot') .durum").inner_text() != "yakında")
    s.click(".alt-cubuk button:has-text('Temrin')")

    # --- Bilmiyorum: her tür ---
    for tip in ("secme", "izleme", "dy", "bosluk", "dizme", "esles", "hesap"):
        q = ilk(tip)
        tek_soru(s, q["id"])
        sayi = s.locator("#sayfaCalis button.bilmiyorum").count()
        kontrol(tip + ": tek Bilmiyorum düğmesi", sayi == 1, sayi)
        if tip in ("secme", "esles", "hesap"): ekran(s, "bilmiyorum-once-" + tip)
        if tip == "esles":   # bir çift doğru eşleşsin, sonra Bilmiyorum
            s.evaluate("""() => { const sol = document.querySelector('.esles-sutun:first-child .esles-oge');
              sol.click(); document.querySelector('.esles-oge.sag[data-cift="' + sol.dataset.cift + '"]').click(); }""")
        s.click("#sayfaCalis button.bilmiyorum")
        r = sonuc(s)
        kontrol(tip + ": yanlış sayıldı, yanlış defterinde", r == {"dogru": 0, "yanlis": 1, "defter": True}, r)
        kontrol(tip + ": izah ve konu bağlantısı çıktı", s.locator(".izah .nereden").count() == 1)
        kontrol(tip + ": Bilmiyorum kalktı, Sonraki soru var",
                s.locator("#sayfaCalis button.bilmiyorum").count() == 0 and s.locator(".eylem button.ana:has-text('Sonraki soru')").count() == 1)
        if tip in ("secme", "izleme", "dy"):
            kontrol(tip + ": doğru şık yeşil, yanlış işaret yok, şıklar kapalı",
                    s.locator(".secenek.dogru").count() == 1 and s.locator(".secenek.yanlis").count() == 0 and
                    s.evaluate("() => [...document.querySelectorAll('.secenek')].every(b => b.disabled)"))
        if tip in ("bosluk", "dizme", "hesap"):
            kontrol(tip + ": Doğrusu yazıyor", "Doğrusu:" in s.inner_text("#sayfaCalis"))
        if tip == "esles":
            n = s.locator(".esles-dogrusu li").count()
            kontrol("esles: bütün çiftler Doğrusu listesinde, öğeler kapalı", n == len(q["ciftler"]) and
                    s.evaluate("() => [...document.querySelectorAll('.esles-oge')].every(b => b.disabled)"), n)
        if tip == "secme": ekran(s, "bilmiyorum-secme")
        if tip == "bosluk": ekran(s, "bilmiyorum-bosluk")
    # Bilmiyorum'dan önce şık seçilince düğme kalkar, sayım bir kez
    q = ilk("secme"); tek_soru(s, q["id"])
    s.click(".secenekler .secenek >> nth=0")
    kontrol("secme: şık seçilince Bilmiyorum kalkar", s.locator("#sayfaCalis button.bilmiyorum").count() == 0)
    # Klasik: Bilemedim zaten var, Bilmiyorum eklenmez
    q = ilk("klasik"); tek_soru(s, q["id"])
    kontrol("klasik: Bilmiyorum yok (Bilemedim var)", s.locator("#sayfaCalis button.bilmiyorum").count() == 0)

    # --- Yazım hoşgörüsü (doğrudan işlevle) ---
    durum = s.evaluate("""() => [
      cevapTutar('ISLEMCI', ['işlemci']), cevapTutar('ilsemci', ['işlemci']), cevapTutar('sutun', ['sütun']),
      cevapTutar('bütün', ['sütun']), cevapTutar('ROM', ['RAM']), cevapTutar('IPv6', ['IPv4']),
      cevapTutar('chmod 754', ['chmod 755']), cevapTutar('derelyici', ['derleyici']), cevapTutar('yorumlayici', ['derleyici']),
      cevapTutar('zamana', ['zamanla']), cevapTutar('isleme', ['işletme']), cevapTutar('EPROM', ['EEPROM']), cevapTutar('derleyicu', ['derleyici']),
      metindeGeciyor('çeşidi', 'eşit'), metindeGeciyor('kaynağın gerilimi', 'kaynak'),
      metindeGeciyor('Islemciye gonderilir', 'işlemci'), metindeGeciyor('islmciye gider', 'işlemci'),
      metindeGeciyor('islem yapar', 'işlemci'), metindeGeciyor('IPv6 kullanir', 'IPv4')]""")
    kontrol("yazım: tam/yakın/ret beklendiği gibi (ek, kısaltma, son harf, kelime ortası korunur; yumuşama bulunur)", durum == ["tam", "yakin", "tam", None, None, None, None, "yakin", None, None, None, None, None, False, True, True, True, False, False], durum)

    # Boşluk doldurma uçtan uca: ilk cevabın ı/i ve harf hatalı hâli
    q = ilk("bosluk", lambda q: len(q["cevaplar"]) == 1 and len(q["cevaplar"][0][0]) >= 8 and re.fullmatch(r"[A-Za-zÇĞİÖŞÜçğıöşü]+", q["cevaplar"][0][0]) and not q["cevaplar"][0][0].isupper() and q["cevaplar"][0][0][1] != q["cevaplar"][0][0][2])
    asil = q["cevaplar"][0][0]
    bozuk = (asil[0] + asil[2] + asil[1] + asil[3:]).upper().replace("I", "i")   # büyük harf + 2. ve 3. harf yer değişmiş
    tek_soru(s, q["id"])
    s.fill(".bosluk-girdi", bozuk)
    s.click(".eylem button:has-text('Kontrol et')")
    r = sonuc(s)
    kontrol("boşluk: '%s' → '%s' doğru sayıldı" % (bozuk, asil), r["dogru"] == 1 and s.locator(".bosluk-girdi.dogru").count() == 1, r)
    kontrol("boşluk: doğru yazımı gösterildi", "Doğru; yazımı:" in s.inner_text("#sayfaCalis") and asil in s.inner_text("#sayfaCalis"))
    tek_soru(s, q["id"])
    s.fill(".bosluk-girdi", asil.lower().replace("ı", "i").replace("ş", "s").replace("ç", "c").replace("ğ", "g").replace("ü", "u").replace("ö", "o"))
    s.click(".eylem button:has-text('Kontrol et')")
    kontrol("boşluk: Türkçe harfsiz tam yazım 'Doğru; yazımı' göstermez", sonuc(s)["dogru"] == 1 and "yazımı" not in s.inner_text("#sayfaCalis"))

    # Klasik: anahtar kavram harf hatasıyla da yeşil
    q = ilk("klasik", lambda q: any(len(a) >= 8 and re.fullmatch(r"[A-Za-zÇĞİÖŞÜçğıöşü]+", a) for a in q.get("anahtarlar", [])))
    a = next(a for a in q["anahtarlar"] if len(a) >= 8 and re.fullmatch(r"[A-Za-zÇĞİÖŞÜçğıöşü]+", a))
    hatali = a[0] + a[2] + a[1] + a[3:]  # 2. ve 3. harf yer değişmiş
    tek_soru(s, q["id"])
    s.fill(".klasik-girdi", "Bence " + hatali.upper() + "lar önemlidir.")
    s.click("button:has-text('Örnek cevabı göster')")
    yesil = s.evaluate("() => [...document.querySelectorAll('.anahtarlar .anahtar.var')].map(e => e.textContent)")
    kontrol("klasik: '%s' yazılınca '%s' yeşil" % (hatali, a), a in yesil, yesil)

    # --- İlerleme çubuğu ---
    s.evaluate("() => { derinlesGit(calisMenusuCiz); oturumBaslat(TUM_SORULAR.filter(q => q.tip === 'dy').slice(0, 4), 'Çubuk'); }")
    s.wait_for_selector("#sayfaCalis .ilerleme .dolu", state="attached")
    olc = lambda: s.evaluate("() => { const c = document.querySelector('#sayfaCalis .ilerleme .cubuk').getBoundingClientRect().width; return Math.round(document.querySelector('#sayfaCalis .ilerleme .dolu').getBoundingClientRect().width / c * 100); }")
    renk = s.evaluate("() => getComputedStyle(document.querySelector('#sayfaCalis .ilerleme .dolu')).display")
    kontrol("çubuk: dolu kısım blok (genişlik uygulanır)", renk == "block", renk)
    kontrol("çubuk: ilk soruda boş", olc() == 0, olc())
    s.click(".dy-dugmeler button >> nth=0"); s.wait_for_timeout(350)
    kontrol("çubuk: cevaplayınca 1/4 dolar", abs(olc() - 25) <= 2, olc())
    s.click(".eylem button.ana:has-text('Sonraki soru')"); s.wait_for_timeout(350)
    kontrol("çubuk: 2. soruda 1/4", abs(olc() - 25) <= 2, olc())
    s.click(".dy-dugmeler button >> nth=0"); s.wait_for_timeout(350)
    kontrol("çubuk: cevaplayınca 2/4", abs(olc() - 50) <= 2, olc())
    ekran(s, "bilmiyorum-cubuk")

    # --- Konu notunda ilgili bölüm yanıp söner ---
    q = ilk("secme", lambda q: q.get("yer"))
    tek_soru(s, q["id"])
    s.click("#sayfaCalis button.bilmiyorum")
    s.click(".izah .nereden")
    s.wait_for_selector(".okuma .baslik-hedef")
    s.wait_for_timeout(150)
    yanan = s.evaluate("() => [...document.querySelectorAll('.okuma .bolum-yanar')].map(e => e.tagName)")
    kontrol("not: başlık ve altındaki metin yanıyor", len(yanan) >= 2 and yanan[0] in ("H3", "H4"), yanan)
    baslik = s.evaluate("() => document.querySelector('.okuma .bolum-yanar').dataset.baslik")
    kontrol("not: yanan başlık sorunun yeri", baslik == q["yer"], [baslik, q["yer"]])
    ust = s.evaluate("() => document.querySelector('.okuma .bolum-yanar').getBoundingClientRect().top - document.querySelector('.ust').getBoundingClientRect().bottom")
    kontrol("not: başlık üst çubuğun altında kalmıyor", ust >= 0, ust)
    ekran(s, "bilmiyorum-yanip-sonme")
    s.wait_for_timeout(2300)
    kontrol("not: 2 sn sonra iz kalmaz", s.locator(".okuma .bolum-yanar").count() == 0)
    c.close()
print("\nbilmiyorum: %d/%d geçti" % (sum(1 for _, k in sonuclar if k), len(sonuclar)))

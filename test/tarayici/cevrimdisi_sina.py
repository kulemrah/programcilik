"""İnternetsiz kullanım: giriş yapılmış cihaz, tarayıcı tamamen kapatılıp
internet yokken sıfırdan açılır (oturum süresi de dolmuş). Uygulama açılmalı,
hiç açılmamış konular ve görselleri okunmalı, temrin/42 Tarzı/menü çalışmalı,
yapılanlar beklemeli ve internet gelince gönderilmeli."""
exec(open("vt_taban.py", encoding="utf-8").read())
import json as _json, re as _re, shutil
D["hususi"] = True
KLASOR = "/tmp/claude-0/pw-cevrimdisi"
GORSEL_SAYISI = len({k["ders"] + "/" + m for k in YUK["konular"] for m in _re.findall(r"gorseller/([^)\s]+)", k.get("metin", ""))} |
                    {k["ders"] + "/" + ad for k in YUK["konular"] for s in k.get("sorular", []) for ad in s.get("gorseller", [])})
GORSELLI = next(k for k in YUK["konular"] if "gorseller/" in k.get("metin", ""))

def ac(p, cevrimdisi):
    c = p.chromium.launch_persistent_context(KLASOR, service_workers="allow", viewport={"width": 390, "height": 820},
                                             offline=cevrimdisi, has_touch=True, is_mobile=True)
    if cevrimdisi:
        c.route(SUPA + "/**", lambda r: r.abort("internetdisconnected"))
    else:
        c.route(SUPA + "/**", isle)
    s = c.pages[0] if c.pages else c.new_page()
    s.on("pageerror", lambda e: hatalar.append("pageerror: " + str(e)))
    return c, s

def vt_say(s, depo):
    return s.evaluate("""d => new Promise(r => { const i = indexedDB.open('programcilik'); i.onsuccess = () => {
        const t = i.result.transaction([d], 'readonly'); t.objectStore(d).count().onsuccess = e => r(e.target.result); }; })""", depo)

shutil.rmtree(KLASOR, ignore_errors=True)
with sync_playwright() as p:
    # ---------------- 1) İnternetliyken giriş ----------------
    c, s = ac(p, False)
    s.add_init_script("try { localStorage.setItem('pg.kurulum', JSON.stringify('gizli')) } catch (e) {}")
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    kod_iste_ve_gir(s)
    s.wait_for_selector(".sozlesme"); s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')"); s.wait_for_selector(".grup-baslik")
    kontrol("bütün konular cihaza indi", bekle_ki(s, lambda: s.evaluate("KONULAR.size") == len(YUK["konular"]), 20), s.evaluate("KONULAR.size"))
    kontrol("bütün görseller konu açılmadan cihaza indi (%d)" % GORSEL_SAYISI, bekle_ki(s, lambda: vt_say(s, "gorsel") == GORSEL_SAYISI, 30), vt_say(s, "gorsel"))
    kontrol("işçi (service worker) sayfayı denetliyor", bekle_ki(s, lambda: s.evaluate("!!navigator.serviceWorker.controller"), 10))
    kontrol("uygulama dosyaları önbellekte", bekle_ki(s, lambda: s.evaluate("caches.keys().then(l => Promise.all(l.map(a => caches.open(a).then(o => o.keys())))).then(x => x.flat().length)") >= 7, 10))
    s.wait_for_timeout(1500)
    # Oturum süresi dolmuş gibi: belirteç yenilenmek isteyecek, internet yok
    s.evaluate("""() => { const k = JSON.parse(localStorage.getItem('pg-oturum'));
                         k.expires_at = Math.floor(Date.now() / 1000) - 600; localStorage.setItem('pg-oturum', JSON.stringify(k)); }""")
    c.close()

    # ---------------- 2) İnternetsiz, sıfırdan açılış ----------------
    c, s = ac(p, True)
    s.goto(KOK)
    kontrol("internetsiz açıldı, giriş istenmedi", bekle_ki(s, lambda: s.locator(".grup-baslik").count() > 0, 15) and s.locator(".giris-perde").count() == 0)
    kontrol("navigator.onLine kapalı", s.evaluate("navigator.onLine") is False)
    kontrol("dersler hazır (yakında değil)", s.locator(".ders-satiri .durum >> nth=0").inner_text() != "yakında")
    s.wait_for_timeout(3000)
    kontrol("süresi dolan oturum internetsizken kapatılmadı", s.locator(".giris-perde").count() == 0 and s.evaluate("!!KULLANICI"))

    # Hiç açılmamış, görselli konu
    s.evaluate("id => konuAc(id)", GORSELLI["id"])
    s.wait_for_selector(".okuma h2")
    kontrol("hiç açılmamış konu internetsiz okunuyor", GORSELLI["baslik"].split()[0] in s.inner_text(".okuma h2"), s.inner_text(".okuma h2"))
    yuklu = bekle_ki(s, lambda: s.evaluate("() => { const l = [...document.querySelectorAll('figure img, img.satir-gorsel')]; return l.length > 0 && l.every(i => i.complete && i.naturalWidth > 0); }"), 8)
    kontrol("konudaki görseller internetsiz görünüyor", yuklu, s.evaluate("[...document.querySelectorAll('figure img, img.satir-gorsel')].map(i => i.naturalWidth)"))
    s.click("text=Okudum olarak işaretle")
    s.wait_for_timeout(500)

    # Temrin
    s.click(".alt-cubuk button:has-text('Temrin')")
    s.evaluate("""() => { const l = TUM_SORULAR.filter(x => x.tip === 'secme').slice(0, 2); derinlesGit(calisMenusuCiz); oturumBaslat(l, 'Deneme'); }""")
    s.wait_for_selector(".secenekler .secenek")
    s.click(".secenekler .secenek >> nth=0")
    kontrol("temrin internetsiz çalışıyor", s.locator(".secenek.dogru, .secenek.yanlis").count() > 0)
    # 42 Tarzı
    s.click(".alt-cubuk button:has-text('42 Tarzı')")
    s.evaluate("() => { depo.yaz('pg.kartKapsam', Object.fromEntries(Array.from(DERS_KONULARI.keys()).map(d => [d, 'tumu']))); kartSayfasiCiz(); }")
    s.click("text=/kartla çalış/")
    kontrol("42 Tarzı internetsiz çalışıyor", bekle_ki(s, lambda: s.locator(".deste .kart-yeri:not(.sonraki)").count() == 1, 5))
    # Menü: hedef ve takvim
    s.click(".alt-cubuk button:has-text('Kıraat')")
    cekmece(s, "hedef")
    kontrol("hedef ekranı internetsiz (saat çiziliyor)", s.locator(".saat-kart").count() >= 6)
    s.click(".cekmece-sekme[data-ekran=takvim]")
    kontrol("takvim internetsiz", s.locator(".takvim-svg .hucre").count() > 50)
    s.click(".hesap-kapat")
    s.wait_for_timeout(600)
    kontrol("bekleyen işaret sunucuya gitmedi (internet yok)", ("okundu", GORSELLI["id"]) not in D["kayitlar"])
    kontrol("hesap düğmesinde bağlantı yok işareti", s.locator("#hesapDugme.cevrimdisi").count() == 1)
    s.screenshot(path="cevrimdisi.png")
    c.close()

    # ---------------- 3) İnternet geldi ----------------
    c, s = ac(p, False)
    s.goto(KOK)
    s.wait_for_selector(".grup-baslik")
    kontrol("internet gelince bekleyen işaret gönderildi", bekle_ki(s, lambda: ("okundu", GORSELLI["id"]) in D["kayitlar"], 15))
    kontrol("oturum yenilendi, giriş istenmedi", s.locator(".giris-perde").count() == 0)
    c.close()

print("hatalar:", [h for h in hatalar if "pageerror" in h][:5])
gecen = sum(1 for _, k in sonuclar if k)
print("SONUÇ: %d/%d" % (gecen, len(sonuclar)))

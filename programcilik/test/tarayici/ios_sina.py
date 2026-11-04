"""iPhone: Safari'de önce ana ekrana ekleme yolu; ana ekrandan açılınca doğrudan giriş."""
exec(open("vt_taban.py", encoding="utf-8").read())
IOS_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1"
with sync_playwright() as p:
    c, s = cihaz_ac(p, "T")
    b = c.browser
    # 1) Safari (kurulmamış)
    c2 = b.new_context(user_agent=IOS_UA, viewport={"width": 390, "height": 800})
    s2 = c2.new_page(); s2.goto(KOK); s2.wait_for_selector(".giris-perde")
    kontrol("Safari: e-posta alanı yerine ana ekrana ekleme yolu", s2.locator("#girisEposta").count() == 0 and s2.locator(".giris-adimlar li").count() == 4, s2.locator(".giris-adimlar li").count())
    kontrol("Safari: adımlarda ••• › Paylaş", "•••" in s2.locator(".giris-adimlar li >> nth=0").inner_text())
    s2.screenshot(path="goruntu/ios-safari.png")
    s2.click("text=Ana ekrana ekleyemiyorum, Safari'de giriş yapacağım")
    kontrol("Safari: devam edince e-posta alanı çıkar", s2.locator("#girisEposta").count() == 1)
    kontrol("Safari: çıkış uyarısı görünür", "Hesap › Çıkış yap" in s2.locator(".giris-kutu").inner_text())
    adim = s2.evaluate("kurulumAdimlari(true)")
    kontrol("Safari oturumu açıkken şeritte çıkış adımı var", len(adim) == 5 and "Çıkış yap" in adim[3], adim)
    # 2) Ana ekrandan açılmış uygulama
    c3 = b.new_context(user_agent=IOS_UA, viewport={"width": 390, "height": 800})
    c3.add_init_script("Object.defineProperty(navigator, 'standalone', { get: () => true })")
    s3 = c3.new_page(); s3.goto(KOK); s3.wait_for_selector(".giris-perde")
    kontrol("Ana ekran uygulaması: doğrudan e-posta alanı", s3.locator("#girisEposta").count() == 1 and s3.locator(".giris-adimlar").count() == 0)
    kontrol("Ana ekran uygulaması: Safari uyarısı yok", "Safari'de giriş yapıyorsunuz" not in s3.locator(".giris-kutu").inner_text())
    # 3) Android/masaüstü etkilenmez
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    kontrol("iPhone dışı: doğrudan e-posta alanı", s.locator("#girisEposta").count() == 1 and s.locator(".giris-adimlar").count() == 0)
print(sum(1 for _, k in sonuclar if k), "/", len(sonuclar))

"""Sunucu, uygulamadan daha uzun bekletirse sayaç sunucunun söylediği süreye uyar."""
exec(open("vt_taban.py", encoding="utf-8").read())
SUNUCU_KOD_ARALIGI = 9
with sync_playwright() as p:
    c, s = cihaz_ac(p, "T")
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    s.fill("#girisEposta", EPOSTA); s.click("button:has-text('Kod gönder')")
    s.wait_for_selector("#girisKod")
    s.wait_for_function("() => [...document.querySelectorAll('.giris-bag')].some(b => b.textContent === 'Yeni kod gönder' && !b.disabled)", timeout=8000)
    s.click("text=Yeni kod gönder")
    s.wait_for_timeout(500)
    t = s.locator("[data-geri-sayim]").inner_text()
    kontrol("sunucu bekletince sayaç onun süresine kurulur", re.search(r"Yeni kod \d+ sn sonra", t) and s.locator("[data-geri-sayim]").is_disabled(), t)
    kontrol("hata mesajı saniye söyler", "saniye sonra" in s.locator(".giris-hata").inner_text())
    sayi = int(re.search(r"(\d+) sn", t).group(1))
    kontrol("kalan süre sunucununkine uygun (3..6 sn)", 3 <= sayi <= 6, sayi)
print(sum(1 for _, k in sonuclar if k), "/", len(sonuclar))

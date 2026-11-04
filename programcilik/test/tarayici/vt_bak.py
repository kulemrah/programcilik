"""SQL konularının okuma sayfaları ve birkaç soru: gözle bakmak için ekran görüntüsü."""
exec(open("vt_taban.py", encoding="utf-8").read())
exec(open("vt_sina.py", encoding="utf-8").read().split("with sync_playwright() as p:")[0].split('exec(open("vt_taban.py"')[1].split("\n", 1)[1])

with sync_playwright() as p:
    c, s = cihaz_ac(p, "V")
    giris(s)
    bekle_ki(s, lambda: s.locator(".ders-satiri:has-text('Veritabanı') .durum").inner_text() != "yakında")
    s.click(".ders-satiri:has-text('Veritabanı')")
    s.wait_for_selector(".agac .dal")
    for i in (11, 12, 13):
        s.click(".agac .dal >> nth=%d" % i)
        s.wait_for_selector(".okuma h2")
        s.wait_for_timeout(800)
        s.screenshot(path="sql-konu-%d.png" % (i + 1), full_page=True)
        s.click("text=‹ Geri")
        s.wait_for_selector(".agac .dal")
    s.click(".alt-cubuk button:has-text('Temrin')")
    s.click("button:has-text('Ders ve konu seç')")
    s.wait_for_selector(".kontrol-oge")
    s.click(".kontrol-oge:has-text('Veritabanı') .kutucuk")
    s.click("button:has-text('Tamam')")
    s.wait_for_selector(".mod-kart")
    for sid in ("vt-sql-select.s19", "vt-sql-komutlar-2.s23", "vt-sql-select.s10", "vt-sql-komutlar-2.s19"):
        s.evaluate("""id => { derinlesGit(calisMenusuCiz); oturumBaslat(kapsamdakiSorular().filter(x => x.id === id), 'Hepsi'); }""", sid)
        s.wait_for_timeout(500)
        s.screenshot(path="soru-%s.png" % sid.replace(".", "-"), full_page=True)
    print("tamam")

"""Notlar — not editörü. Gerçek şema ve Worker'la (kaynak_taban.py).
Biçimler, satır başı kısayolları, geri al / yinele, renk, ara başlık, metnin
arasında resim, yapıştırma süzgeci, kötü niyetli kayıtlı içerik, eski düz
notlar, boş ve çok uzun not, otomatik kayıt, silme (geri alınabilir),
tarihler, klavye açıkken yerleşim."""
exec(open("kaynak_taban.py", encoding="utf-8").read())

F1, B1 = foto("not-resim.jpg", 1600, 1200, 7)

SEC = """(parca) => { const kok = document.querySelector('.not-editor .ne-metin'); kok.focus();
  const w = document.createTreeWalker(kok, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { const i = n.data.indexOf(parca); if (i >= 0) {
    const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + parca.length);
    const s = getSelection(); s.removeAllRanges(); s.addRange(r); return true; } }
  return false; }"""
SONA = """() => { const kok = document.querySelector('.not-editor .ne-metin'); kok.focus();
  const r = document.createRange(); r.selectNodeContents(kok); r.collapse(false);
  const s = getSelection(); s.removeAllRanges(); s.addRange(r); }"""
YAPISTIR = """([html, duz]) => { const kok = document.querySelector('.not-editor .ne-metin');
  const dt = new DataTransfer(); if (html) dt.setData('text/html', html); if (duz) dt.setData('text/plain', duz);
  kok.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true })); }"""

def sec(s, parca):
    return s.evaluate(SEC, parca)
def not_satiri(baslik_=None):
    if baslik_ is None:
        return tek("select id::text, baslik, metin, bicim, olusma::text, guncellendi::text from public.kaynak_oge where tur = 'not' order by olusma desc limit 1")
    return tek("select id::text, baslik, metin, bicim, olusma::text, guncellendi::text from public.kaynak_oge where tur = 'not' and baslik = '%s'" % baslik_.replace("'", "''"))
def not_say():
    return tek("select count(*)::int as n from public.kaynak_oge where tur = 'not'")["n"]
def kart_ac(s, parca):
    s.click("#sayfaKaynak .kaynak-not-kart:has-text('%s')" % parca)
    s.wait_for_selector(".not-editor .ne-metin")
    s.wait_for_timeout(150)

try:
    with sync_playwright() as p:
        c, s = cihaz_ac(p, "E")
        kaynak_yollari(c)
        s.on("dialog", lambda d: (hatalar.append("DİYALOG: " + d.message), d.dismiss()))
        giris(s)
        notlara_git(s)
        tasnif_ac(s, "Veri Yapıları")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Veri Yapıları')")
        kuyruk_bossa(s)

        # ---- Yeni not: başlık, kısayollar, listeler ----
        editor_ac_yeni(s)
        kontrol("yeni notta başlığa odaklanılır", s.evaluate("() => document.activeElement.classList.contains('ne-baslik')"))
        kontrol("açılışta renk seçenekleri ve resim çubuğu görünmez", not s.is_visible(".ne-renkler") and not s.is_visible(".ne-resim-araci"))
        kontrol("üstte geri, geri al, yinele, sil, tamam; altta biçim çubuğu",
                s.locator(".not-editor .ne-ust-dugme").count() == 5 and s.locator(".not-editor .ne-arac-dugme").count() == 9)
        kontrol("boş metinde 'Yazmaya başlayın' yer tutucusu", s.evaluate("() => document.querySelector('.ne-metin').classList.contains('bos')"))
        kontrol("bilgi satırı: tarih · 0 karakter", " · 0 karakter" in s.inner_text(".not-editor .ne-bilgi"), s.inner_text(".not-editor .ne-bilgi"))
        s.keyboard.type("Ders 5: Ağaçlar")
        s.keyboard.press("Enter")
        kontrol("başlıkta Enter metne geçer", s.evaluate("() => document.activeElement.classList.contains('ne-metin')"))
        s.keyboard.type("Giriş paragrafı.")
        s.keyboard.press("Enter")
        s.keyboard.type("- Birinci")
        s.keyboard.press("Enter"); s.keyboard.type("İkinci")
        s.keyboard.press("Enter"); s.keyboard.press("Enter")
        s.keyboard.type("1. Adım bir")
        s.keyboard.press("Enter"); s.keyboard.type("Adım iki")
        s.keyboard.press("Enter"); s.keyboard.press("Enter")
        s.keyboard.type("* Yıldızla madde")
        s.keyboard.press("Enter"); s.keyboard.press("Enter")
        s.keyboard.type("Son satır.")
        h = editor_html(s)
        kontrol("'- ' madde işaretli listeye döner", "<ul><li>Birinci</li><li>İkinci</li></ul>" in h, h)
        kontrol("'1. ' numaralı listeye döner", "<ol><li>Adım bir</li><li>Adım iki</li></ol>" in h, h)
        kontrol("'* ' de madde açar", "<ul><li>Yıldızla madde</li></ul>" in h, h)
        kontrol("boş maddede Enter listeden çıkar", "<p>Son satır.</p>" in h, h)
        sec(s, "Birinci")
        kontrol("madde düğmesi listede etkin görünür", bekle_ki(s, lambda: s.locator(".ne-arac-dugme.madde.etkin").count() == 1, 3))

        # ---- Biçimler ----
        sec(s, "Giriş"); s.click(".ne-arac-dugme.kalin")
        sec(s, "paragrafı"); s.click(".ne-arac-dugme.italik")
        sec(s, "Adım bir"); s.click(".ne-arac-dugme.alti")
        sec(s, "Adım iki"); s.click(".ne-arac-dugme.ustu")
        h = editor_html(s)
        kontrol("kalın, italik, altı çizili, üstü çizili", "<b>Giriş</b>" in h and "<i>paragrafı</i>" in h and "<u>Adım bir</u>" in h and ("<strike>Adım iki</strike>" in h or "<s>Adım iki</s>" in h), h)
        sec(s, "Giriş")
        kontrol("imleç kalın yazıdayken B düğmesi etkin (aria-pressed)", bekle_ki(s, lambda: s.get_attribute(".ne-arac-dugme.kalin", "aria-pressed") == "true", 3))
        sec(s, "İkinci"); s.keyboard.press("Control+b")
        kontrol("Ctrl+B de kalın yapar", "<b>İkinci</b>" in editor_html(s), editor_html(s))
        # Renk
        sec(s, "Son")
        s.click(".ne-arac-dugme.renk")
        kontrol("A: renk seçenekleri açılır (varsayılan + 5 renk)", s.is_visible(".ne-renkler") and s.locator(".ne-renkler .ne-renk").count() == 6)
        s.click(".ne-renk[aria-label='Kırmızı']")
        kontrol("renk seçilince seçenekler kapanır, yazı kırmızı", not s.is_visible(".ne-renkler") and
                s.evaluate("() => { const r = getSelection().getRangeAt(0); const e = r.startContainer.parentElement; return getComputedStyle(e).color; }") == "rgb(229, 72, 77)")
        sec(s, "satır.")
        s.click(".ne-arac-dugme.renk"); s.click(".ne-renk[aria-label='Mavi']")
        sec(s, "satır.")
        s.click(".ne-arac-dugme.renk"); s.click(".ne-renk[aria-label='Varsayılan renk']")
        # Ara başlık
        sec(s, "Giriş"); s.click(".ne-arac-dugme.baslik")
        kontrol("H: paragraf ara başlık olur", "<h3><b>Giriş</b> <i>paragrafı</i>.</h3>" in editor_html(s) or "<h3><b>Giriş</b>&nbsp;<i>paragrafı</i>.</h3>" in editor_html(s), editor_html(s))
        kontrol("H düğmesi etkin", s.locator(".ne-arac-dugme.baslik.etkin").count() == 1)
        # Geri al / yinele
        s.click(".ne-ust-dugme.geriAl")
        kontrol("geri al: ara başlık kalkar", "<h3>" not in editor_html(s), editor_html(s))
        s.click(".ne-ust-dugme.yinele")
        kontrol("yinele: ara başlık döner", "<h3>" in editor_html(s), editor_html(s))
        kontrol("karakter sayısı yazılanı izler", int(s.inner_text(".not-editor .ne-bilgi").split(" · ")[1].split(" ")[0]) > 40, s.inner_text(".not-editor .ne-bilgi"))
        s.screenshot(path="not-editor.png")
        editor_kapat(s)
        kuyruk_bossa(s)
        r = not_satiri("Ders 5: Ağaçlar")
        m = r["metin"] if r else ""
        kontrol("kaydedildi: başlık, biçimli metin", r and r["bicim"] == "html", r)
        kontrol("saklanan biçim yalnızca izinli etiketler (font/style/class yok)", m and not re.search(r"<(font|div|strike|strong|em|span(?! data-renk))|style=|class=|color=", m), m)
        kontrol("saklananda listeler, ara başlık, kalın, italik, altı/üstü çizili", all(x in m for x in ["<ul><li>Birinci</li>", "<ol><li><u>Adım bir</u></li><li><s>Adım iki</s></li></ol>", "<h3><b>Giriş</b>", "<i>paragrafı</i>"]), m)
        kontrol("kırmızı 'data-renk=kirmizi' olarak saklanır; maviden varsayılana döndürülen renksiz", '<span data-renk="kirmizi">Son</span>' in m and 'data-renk="mavi"' not in m, m)

        # Kayıtlı (yeniden açılmış) kırmızı yazıyı varsayılana döndürmek
        kart_ac(s, "Ders 5")
        sec(s, "Son")
        s.click(".ne-arac-dugme.renk"); s.click(".ne-renk[aria-label='Varsayılan renk']")
        kontrol("kayıtlı renkli yazı varsayılan renge döner", s.evaluate("() => { const e = getSelection().getRangeAt(0).startContainer.parentElement; return getComputedStyle(e).color === getComputedStyle(document.querySelector('.ne-metin')).color; }"))
        editor_kapat(s); kuyruk_bossa(s)
        m = not_satiri("Ders 5: Ağaçlar")["metin"]
        kontrol("saklananda o yazı artık kırmızı değil", re.search(r'<span data-renk="kirmizi">Son</span>', m) is None and re.search(r'data-renk="kirmizi"><span data-renk="yok">Son', m) or "kirmizi" not in m, m)
        s.click(".not-editor .ne-ust-dugme.tamam") if s.locator(".not-editor").count() else None

        # ---- Kutucuk ----
        kart = s.locator("#sayfaKaynak .kaynak-not-kart").first
        kontrol("kutucukta başlık ve metnin başı (maddeler '• ' ile)", "Ders 5: Ağaçlar" in kart.inner_text() and "• Birinci" in kart.inner_text() and "Bugün" in kart.inner_text(), kart.inner_text())

        # ---- Yeniden açma, otomatik kayıt, telefonun geri tuşu ----
        kart_ac(s, "Ders 5")
        kontrol("yeniden açılınca içerik aynen gelir", "<h3><b>Giriş</b>" in editor_html(s) and "Yıldızla madde" in editor_html(s))
        kontrol("eski notta başlığa odaklanılmaz", not s.evaluate("() => document.activeElement.classList.contains('ne-baslik')"))
        s.evaluate(SONA); s.keyboard.type(" Ek cümle.")
        s.wait_for_timeout(2300)
        kontrol("yazmaya ara verince kendiliğinden kaydedilir (editör açıkken)", kuyruk_bossa(s) and "Ek cümle." in not_satiri("Ders 5: Ağaçlar")["metin"])
        s.evaluate(SONA); s.keyboard.type(" Geri tuşuyla.")
        geri(s)
        kontrol("telefonun geri tuşu editörü kapatır ve kaydeder", s.locator(".not-editor").count() == 0 and kuyruk_bossa(s)
                and "Geri tuşuyla." in not_satiri("Ders 5: Ağaçlar")["metin"] and baslik(s) == "Veri Yapıları")
        kart_ac(s, "Ders 5")
        s.keyboard.press("Escape")
        kontrol("Esc editörü kapatır", bekle_ki(s, lambda: s.locator(".not-editor").count() == 0, 3))

        # ---- Tarihler ----
        # (oluşma anı sunucuda değiştirilemez; deneme için kural bir anlığına kapatılır)
        sql("alter table public.kaynak_oge disable trigger kaynak_oge_denetle")
        sql("update public.kaynak_oge set olusma = now() - interval '3 days', guncellendi = now() - interval '1 day' where baslik = 'Ders 5: Ağaçlar'")
        sql("alter table public.kaynak_oge enable trigger kaynak_oge_denetle")
        s.evaluate("() => kaynakYenile()"); s.wait_for_timeout(600)
        kart_ac(s, "Ders 5")
        b = s.inner_text(".not-editor .ne-bilgi")
        kontrol("bilgi: 'Değiştirildi …' ve 'Oluşturuldu …' (tam tarihle)", "Değiştirildi" in b and "Oluşturuldu" in b and str(datetime.date.today().year) in b, b)
        editor_kapat(s)
        kontrol("kutucukta değiştirilme tarihi ('Dün')", "Dün" in s.locator("#sayfaKaynak .kaynak-not-kart:has-text('Ders 5')").inner_text())

        # ---- Metnin arasında resim ----
        kart_ac(s, "Ders 5")
        sec(s, "Birinci")
        s.evaluate("() => { const s = getSelection(); s.collapseToEnd(); }")
        s.set_input_files(".not-editor input[type=file]", [F1])
        kontrol("resim metne girer (küçültülüp)", bekle_ki(s, lambda: s.locator(".not-editor .ne-metin img[data-resim][src^='blob:']").count() == 1, 30))
        rid = s.get_attribute(".not-editor .ne-metin img", "data-resim")
        editor_kapat(s)
        kuyruk_bossa(s)
        rs = tek("select o.not_id::text, n.baslik, o.en, o.boy from public.kaynak_oge o join public.kaynak_oge n on n.id = o.not_id where o.id = '%s'" % rid)
        kontrol("resim sunucuda, nota bağlı (not_id), 1600×1200 aynen", rs and rs["baslik"] == "Ders 5: Ağaçlar" and (rs["en"], rs["boy"]) == (1600, 1200), rs)
        kontrol("R2'de resim var", any(rid in a for a in r2()))
        m = not_satiri("Ders 5: Ağaçlar")["metin"]
        kontrol("notta yalnızca kimlik saklanır (adres yok)", ('data-resim="%s"' % rid) in m and "blob:" not in m and "src=" not in m, m)
        kart = s.locator("#sayfaKaynak .kaynak-not-kart:has-text('Ders 5')")
        kontrol("kutucukta notun resmi ve resim sayısı", bekle_ki(s, lambda: kart.locator(".kk-resim img[src^='blob:']").count() == 1, 10) and kart.locator(".kk-resim-sayisi").inner_text().strip() == "1")
        kontrol("notun resmi tasnifte ayrı kutucuk olmaz", s.locator("#sayfaKaynak .kaynak-resim-kart").count() == 0)
        # Resmi metinden silme
        kart_ac(s, "Ders 5")
        bekle_ki(s, lambda: s.locator(".not-editor .ne-metin img[src^='blob:']").count() == 1, 10)
        s.click(".not-editor .ne-metin img")
        kontrol("resme dokununca Büyüt / Sil çubuğu", s.is_visible(".ne-resim-araci") and s.locator(".ne-resim-araci button").count() == 2)
        s.click(".ne-resim-araci button:has-text('Büyüt')")
        kontrol("Büyüt: büyüteç açılır", s.locator(".buyutec").count() == 1)
        geri(s)
        kontrol("büyüteç kapanınca editör açık kalır", s.locator(".buyutec").count() == 0 and s.locator(".not-editor").count() == 1)
        s.click(".not-editor .ne-metin img")
        s.click(".ne-resim-araci button:has-text('Sil')")
        kontrol("Sil: resim metinden çıkar, çubuk kapanır", s.locator(".not-editor .ne-metin img").count() == 0 and not s.is_visible(".ne-resim-araci"))
        s.click(".ne-ust-dugme.geriAl")
        kontrol("geri al: resim döner", bekle_ki(s, lambda: s.locator(".not-editor .ne-metin img[src]").count() == 1, 3))
        s.wait_for_timeout(2000)
        s.click(".not-editor .ne-metin img")
        s.click(".ne-resim-araci button:has-text('Sil')")
        s.wait_for_timeout(2000)
        kontrol("otomatik kayıtta resim henüz silinmez (geri alınabilsin diye)", tek("select count(*)::int as n from public.kaynak_oge where id = '%s'" % rid)["n"] == 1)
        editor_kapat(s)
        kuyruk_bossa(s)
        kontrol("kapanınca metinden çıkarılan resim silinir (veritabanı ve R2)", tek("select count(*)::int as n from public.kaynak_oge where id = '%s'" % rid)["n"] == 0
                and not any(rid in a for a in r2()))

        # ---- Yapıştırma süzgeci ----
        editor_ac_yeni(s)
        s.fill(".not-editor .ne-baslik", "Yapıştırma")
        s.evaluate(SONA)
        s.evaluate("() => { const dt = new DataTransfer(); dt.items.add(new File(['x'], 'a.png', { type: 'image/png' })); const e = new DragEvent('dragover', { dataTransfer: dt, bubbles: true, cancelable: true }); document.querySelector('.ne-baslik').dispatchEvent(e); window.__surukleme = e.defaultPrevented; }")
        kontrol("editörün üstüne dosya sürüklenince tarayıcı dosyayı açmaz", s.evaluate("() => window.__surukleme") is True)
        s.evaluate(SONA)
        kotu = ('<h1>Başlık</h1><p style="font-weight:700;color:#e5484d">Kalın kırmızı</p><script>window.__xss=1</script>'
                '<img src="x" onerror="window.__xss=2"><iframe src="javascript:window.__xss=3"></iframe><svg onload="window.__xss=4"><circle/></svg>'
                '<a href="javascript:window.__xss=5" onclick="window.__xss=6">bağlantı</a><span style="color:rgb(1,2,3)">yabancı renk</span>'
                '<img data-resim="00000000-0000-4000-8000-000000000000" src="blob:x"><style>body{display:none}</style><table><tr><td>h1</td><td>h2</td></tr></table>')
        s.evaluate(YAPISTIR, [kotu, "düz"])
        h = editor_html(s)
        kontrol("yapıştırılan: betik, çerçeve, svg, olay öznitelikleri, stil, bağlantı adresi geçmez",
                not re.search(r"<(script|iframe|svg|style|a |a>)|on\w+=|javascript:|href=|style=", h) and s.evaluate("() => window.__xss") is None, h)
        kontrol("yapıştırılan: biçim izinli karşılığına döner (h1 → h3, kalın, palet rengi)", "<h3>Başlık</h3>" in h and '<span data-renk="kirmizi"><b>Kalın kırmızı</b></span>' in h, h)
        kontrol("yapıştırılan: paletsiz renk düşer, yazısı kalır; başka notun resmi alınmaz", "yabancı renk" in h and "rgb(1" not in h and "00000000-0000-4000" not in h, h)
        s.evaluate(YAPISTIR, [None, "satır bir\nsatır <iki>"])
        kontrol("düz yazı satırlarıyla, yazı olarak (etiket değil) yapışır", "<p>satır <iki></iki></p>" not in editor_html(s) and "satır &lt;iki&gt;" in editor_html(s), editor_html(s))
        s.evaluate(SONA)
        s.evaluate(YAPISTIR, ['<meta charset="utf-8"><b style="font-weight:normal;" id="docs-internal-guid-1"><p><span style="font-weight:400">Docs düz</span><span style="font-weight:700">Docs kalın</span></p></b>', "Docs"])
        h = editor_html(s)
        kontrol("Google Docs'tan yapıştırılan bütünüyle kalın olmaz", "<b>Docs düz" not in h and "<b>Docs kalın</b>" in h, h)
        s.focus(".not-editor .ne-baslik")
        once = editor_html(s)
        s.click(".ne-arac-dugme.kalin")
        kontrol("başlıktayken B metne dokunmaz", editor_html(s) == once)
        s.evaluate("() => { const d = document.querySelector('.ne-ust-dugme.tamam'); d.click(); d.click(); }")
        s.wait_for_selector(".not-editor", state="detached")
        s.wait_for_timeout(500)
        kontrol("✓'ye iki kez basmak yalnızca editörü kapatır (tasnifte kalınır)", baslik(s) == "Veri Yapıları", baslik(s))
        kuyruk_bossa(s)
        s.evaluate("() => { kaynakNotAc(KAYNAK.tasnifler.find(t => t.ad === 'Veri Yapıları').id, null); kaynakNotAc(KAYNAK.tasnifler.find(t => t.ad === 'Veri Yapıları').id, null); }")
        s.wait_for_selector(".not-editor")
        s.wait_for_timeout(300)
        kontrol("iki kez dokunulunca tek editör açılır", s.locator(".not-editor").count() == 1)
        editor_kapat(s)
        kontrol("açılıp kapanan editör geçmişte adım bırakmaz (yalnızca tasnif adımı)", s.evaluate("() => sekmeGecmisi().length") == 1, s.evaluate("() => sekmeGecmisi().length"))

        # ---- Aynı tarayıcıda iki sekme: sıralar birbirini ezmez ----
        s2 = c.new_page()
        s2.on("pageerror", lambda e: hatalar.append("E2 " + str(e)))
        s2.goto(KOK); s2.wait_for_selector(".alt-cubuk")
        bekle_ki(s2, lambda: s2.evaluate("() => KAYNAK.yuklendi || (kaynakYukle(), false)"), 10)
        c.set_offline(True)
        for sy in (s, s2): sy.evaluate("() => window.dispatchEvent(new Event('offline'))")
        tid_ = s.evaluate("() => KAYNAK.tasnifler.find(t => t.ad === 'Veri Yapıları').id")
        s.evaluate("(t) => kaynakIsEkle({ tur: 'not_ekle', id: yeniKimlik(), tasnif: t, baslik: 'Sekme bir', metin: '<p>1</p>', bicim: 'html', zaman: new Date().toISOString() })", tid_)
        s2.evaluate("(t) => kaynakIsEkle({ tur: 'not_ekle', id: yeniKimlik(), tasnif: t, baslik: 'Sekme iki', metin: '<p>2</p>', bicim: 'html', zaman: new Date().toISOString() })", tid_)
        s.wait_for_timeout(300)
        kayit = s.evaluate("async () => (await vt.onEkli('kaynak', 'k/')).map(x => x.is.baslik).sort()")
        kontrol("iki sekmenin bekleyen işleri cihazda yan yana durur", kayit == ["Sekme bir", "Sekme iki"], kayit)
        s2.close()
        c.set_offline(False)
        s.evaluate("() => window.dispatchEvent(new Event('online'))")
        kuyruk_bossa(s)
        s.reload(); s.wait_for_selector(".alt-cubuk")
        bekle_ki(s, lambda: s.evaluate("() => KAYNAK.yuklendi && KAYNAK_KUYRUK.length === 0 && !kaynakGonderim"), 30)
        kontrol("kapanan sekmenin işi de gönderilir", tek("select count(*)::int as n from public.kaynak_oge where baslik in ('Sekme bir', 'Sekme iki')")["n"] == 2)
        notlara_git(s)
        s.click(".alt-cubuk button:has-text('Notlar')")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Veri Yapıları')")

        # ---- Veritabanında kötü niyetli içerik: gösterilirken de süzülür ----
        tid = tek("select id::text from public.kaynak_tasnif where ad = 'Veri Yapıları'")["id"]
        sql("""insert into public.kaynak_oge (kullanici, tasnif, tur, baslik, metin, bicim)
               select kullanici, id, 'not', '<img src=x onerror="window.__xss=7">Sızma', '<p>önce<img src=x onerror="window.__xss=8"><script>window.__xss=9</script></p><iframe srcdoc="<script>parent.__xss=10</script>"></iframe><p onclick="window.__xss=11">sonra</p>', 'html'
               from public.kaynak_tasnif where id = '%s'""" % tid)
        sql("""insert into public.kaynak_oge (kullanici, tasnif, tur, metin, bicim)
               select kullanici, id, 'not', E'Eski düz not\\nikinci <b>satır</b>', 'duz' from public.kaynak_tasnif where id = '%s'""" % tid)
        s.evaluate("() => kaynakYenile()"); s.wait_for_timeout(800)
        kart = s.locator("#sayfaKaynak .kaynak-not-kart:has-text('Sızma')")
        kontrol("kötü başlık yazı olarak görünür, kutucukta yalnızca düz yazı", kart.count() == 1 and '<img src=x' in kart.inner_text() and "öncesonra" in kart.inner_text().replace("\n", ""), kart.inner_text() if kart.count() else "")
        kart_ac(s, "Sızma")
        s.wait_for_timeout(500)
        h = editor_html(s)
        kontrol("editörde kötü içerik süzülür, hiçbir betik çalışmaz", "<script" not in h and "onerror" not in h and "onclick" not in h and "iframe" not in h
                and s.evaluate("() => window.__xss") is None and s.locator("iframe").count() == 0, h)
        editor_kapat(s)
        kart_ac(s, "Eski düz not")
        h = editor_html(s)
        kontrol("ilk sürümün düz notu satırlarıyla, etiketler yazı olarak açılır", "<p>Eski düz not</p><p>ikinci &lt;b&gt;satır&lt;/b&gt;</p>" in h, h)
        editor_kapat(s)
        kontrol("değiştirilmeyen düz not olduğu gibi kalır", tek("select bicim from public.kaynak_oge where metin like 'Eski düz not%'")["bicim"] == "duz")
        kart_ac(s, "Eski düz not")
        s.evaluate(SONA); s.keyboard.type(" eklendi")
        editor_kapat(s); kuyruk_bossa(s)
        r = tek("select bicim, metin from public.kaynak_oge where metin like '%Eski düz not%'")
        kontrol("düzenlenen düz not biçimli nota çevrilir (etiketler kaçışlı kalır)", r["bicim"] == "html" and "&lt;b&gt;satır&lt;/b&gt; eklendi" in r["metin"], r)

        # ---- Boş not, boşaltılan not, silme ----
        n = not_say()
        editor_ac_yeni(s)
        editor_kapat(s)
        kontrol("hiçbir şey yazılmayan yeni not kaydedilmez", not_say() == n and kuyruk(s) == 0 and s.locator(".geri-al").count() == 0)
        editor_ac_yeni(s)
        s.click(".not-editor .ne-metin")
        s.keyboard.type("Boşaltılacak")
        s.wait_for_timeout(1900); kuyruk_bossa(s)
        s.evaluate(SEC, "Boşaltılacak"); s.keyboard.press("Delete")
        s.wait_for_timeout(2200)
        kontrol("boşaltılıp beklenince boş hâli kaydedilmez", "Boşaltılacak" in (not_satiri() or {}).get("metin", ""))
        editor_kapat(s)
        kontrol("boşaltılan not: 'Boş not silindi' ve geri al", "Boş not silindi" in (s.inner_text(".geri-al") if s.locator(".geri-al").count() else ""))
        s.click(".geri-al-dugme")
        kontrol("geri al: not son dolu hâliyle döner", s.locator("#sayfaKaynak .kaynak-not-kart:has-text('Boşaltılacak')").count() == 1)
        kart_ac(s, "Boşaltılacak")
        s.click(".ne-ust-dugme.sil")
        s.wait_for_selector(".not-editor", state="detached")
        kontrol("çöp kutusu: editör kapanır, 'Not silindi' geri al", "Not silindi" in s.inner_text(".geri-al") and s.locator("#sayfaKaynak .kaynak-not-kart:has-text('Boşaltılacak')").count() == 0)
        bekle_ki(s, lambda: s.locator(".geri-al").count() == 0, 8); kuyruk_bossa(s)
        kontrol("5 sn sonra not sunucudan silinir", tek("select count(*)::int as n from public.kaynak_oge where metin like '%Boşaltılacak%'")["n"] == 0)
        # Resimli notu silmek resimlerini de siler
        editor_ac_yeni(s)
        s.fill(".not-editor .ne-baslik", "Resimli silinecek")
        s.click(".not-editor .ne-metin")
        s.set_input_files(".not-editor input[type=file]", [F1])
        bekle_ki(s, lambda: s.locator(".not-editor .ne-metin img[src^='blob:']").count() == 1, 30)
        rid2 = s.get_attribute(".not-editor .ne-metin img", "data-resim")
        editor_kapat(s); kuyruk_bossa(s)
        kontrol("resimli not ve resmi sunucuda", tek("select count(*)::int as n from public.kaynak_oge where id = '%s'" % rid2)["n"] == 1)
        kart_ac(s, "Resimli silinecek")
        s.click(".ne-ust-dugme.sil")
        s.wait_for_selector(".not-editor", state="detached")
        bekle_ki(s, lambda: s.locator(".geri-al").count() == 0, 8); kuyruk_bossa(s)
        kontrol("resimli not silinince resmi de silinir (veritabanı ve R2)", tek("select count(*)::int as n from public.kaynak_oge where id = '%s'" % rid2)["n"] == 0
                and not any(rid2 in a for a in r2()))
        # Bağlantısızken eklenip hiç gönderilmemiş resimli not silinirse sunucuya hiçbir şey gitmez
        c.set_offline(True); s.evaluate("() => window.dispatchEvent(new Event('offline'))")
        editor_ac_yeni(s)
        s.fill(".not-editor .ne-baslik", "Gitmeyecek")
        s.click(".not-editor .ne-metin")
        s.set_input_files(".not-editor input[type=file]", [F1])
        bekle_ki(s, lambda: s.locator(".not-editor .ne-metin img[src^='blob:']").count() == 1, 30)
        s.click(".ne-ust-dugme.sil")
        s.wait_for_selector(".not-editor", state="detached")
        s.click(".geri-al-dugme") if False else None
        bekle_ki(s, lambda: s.locator(".geri-al").count() == 0, 8)
        kontrol("gönderilmemiş not silinince sıra boşalır", kuyruk(s) == 0)
        yerel = s.evaluate("async () => (await vt.anahtarlar('kaynak')).filter(a => a.startsWith('r/')).length")
        c.set_offline(False); s.evaluate("() => window.dispatchEvent(new Event('online'))")
        kuyruk_bossa(s)
        kontrol("sunucuya hiçbir şey gitmedi", tek("select count(*)::int as n from public.kaynak_oge where baslik = 'Gitmeyecek'")["n"] == 0)

        # ---- Çok uzun not ----
        editor_ac_yeni(s)
        s.fill(".not-editor .ne-baslik", "Uzun")
        s.evaluate("() => { const m = document.querySelector('.not-editor .ne-metin'); m.innerHTML = '<p>' + 'u'.repeat(61000) + '</p>'; m.dispatchEvent(new Event('input')); }")
        s.wait_for_timeout(1900)
        kontrol("60.000'i aşınca uyarı, kaydedilmez", "çok uzun" in s.inner_text(".not-editor .ne-uyari") and tek("select count(*)::int as n from public.kaynak_oge where baslik = 'Uzun'")["n"] == 0,
                s.inner_text(".not-editor .ne-uyari"))
        editor_kapat(s)
        kontrol("kapanınca yazılan kaybolmaz: cihazda kalır, 'gönderilemedi' gösterilir", bekle_ki(s, lambda: s.locator("#sayfaKaynak .kaynak-not-kart.hata:has-text('Uzun')").count() == 1, 20)
                and "Not çok uzun" in s.inner_text("#sayfaKaynak .kaynak-uyari.hata"), s.inner_text("#sayfaKaynak")[:300])
        kart_ac(s, "Uzun")
        kontrol("açınca neden kaydedilemediği yazar", "çok uzun" in s.inner_text(".not-editor .ne-uyari"))
        s.evaluate("() => { const m = document.querySelector('.not-editor .ne-metin'); m.innerHTML = '<p>kısaldı</p>'; m.dispatchEvent(new Event('input')); }")
        editor_kapat(s)
        kontrol("kısaltınca gönderilir", kuyruk_bossa(s) and tek("select metin from public.kaynak_oge where baslik = 'Uzun'")["metin"] == "<p>kısaldı</p>")

        # ---- Odak kaçmaz; dar ekran; klavye açıkken yerleşim ----
        s.set_viewport_size({"width": 358, "height": 760})
        fab(s, "Not")
        s.click(".not-editor .ne-metin")
        s.keyboard.type("hemen yazdım")
        kontrol("yeni notta hemen metne yazılan başlığa kaçmaz", s.input_value(".not-editor .ne-baslik") == "" and "hemen yazdım" in editor_html(s), editor_html(s))
        tasma = s.evaluate("() => Array.from(document.querySelectorAll('.not-editor *')).filter(e => { const b = e.getBoundingClientRect(); return b.width && b.right > innerWidth + 1 && !e.closest('.ne-arac'); }).map(e => e.className).slice(0, 5)")
        kontrol("358 px'te editör taşmaz", not tasma, tasma)
        sigiyor = s.evaluate("() => { const a = document.querySelector('.ne-arac'); return a.scrollWidth <= a.clientWidth + 1 && Array.from(a.children).every(d => d.getBoundingClientRect().right <= innerWidth); }")
        kontrol("358 px'te biçim çubuğunun dokuz düğmesi de görünür (kaydırmadan)", sigiyor)
        s.set_viewport_size({"width": 358, "height": 420})   # klavye açıldı
        s.wait_for_timeout(300)
        yer = s.evaluate("() => { const a = document.querySelector('.ne-arac').getBoundingClientRect(); return [Math.round(a.bottom), visualViewport.height]; }")
        kontrol("ekranın görünen kısmı küçülünce biçim çubuğu en altta (klavyenin üstünde) kalır", abs(yer[0] - yer[1]) <= 1, yer)
        s.screenshot(path="not-editor-dar.png")
        s.set_viewport_size({"width": 358, "height": 760})
        editor_kapat(s); kuyruk_bossa(s)
        kontrol("panelde resim yok (silinenler gitti)", tek("select count(*)::int as n from public.kaynak_oge where tur = 'resim'")["n"] == 0)
        c.close()
finally:
    sunucu.kill()

# Çok uzun not sunucuda reddedilir (400): beklenen yanıt
kontrol("sayfa hatası ve diyalog yok", not [h for h in hatalar if "favicon" not in h and "status of 400" not in h and "ERR_INTERNET_DISCONNECTED" not in h and "Failed to fetch" not in h and "blob:x" not in h and "ERR_FILE_NOT_FOUND" not in h], hatalar[:5])
gecen = sum(1 for _, k in sonuclar if k)
print("\n%d/%d geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) else 1)

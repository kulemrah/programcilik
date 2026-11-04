"""Notlar sekmesi (iç adı kaynak) — uçtan uca.
Gerçek şema (yerel PostgreSQL) ve gerçek Worker koduyla: tasnifler, + düğmesi,
iki sütunlu kutucuklar, resim yükleme ve küçültme, 5 sn geri alınabilir silme,
bağlantısız çalışma (gönderilecekler sırası), hak sınırı, Hesap › Notlar ve
resim paneli. Editörün ayrıntıları notlar_editor_sina.py'de."""
exec(open("kaynak_taban.py", encoding="utf-8").read())

F1, B1 = foto("kaynak-yatay.jpg", 4000, 3000, 1)
F2, B2 = foto("kaynak-dikey.jpg", 2448, 3264, 2)
F3, B3 = foto("kaynak-ucuncu.jpg", 1600, 1200, 3)

try:
    with sync_playwright() as p:
        c, s = cihaz_ac(p, "K")
        kaynak_yollari(c)
        istekler = []
        s.on("request", lambda r: istekler.append(r.url))
        giris(s)

        etiketler = s.locator(".alt-cubuk button span").all_inner_texts()
        kontrol("alt çubukta Notlar beşinci sekme", etiketler == ["Kıraat", "Ara", "Temrin", "42 Tarzı", "Notlar"], etiketler)
        notlara_git(s)
        kontrol("kökte başlık 'Notlar', boş durum ve hak (0 / 100 MB)", baslik(s) == "Notlar" and "Henüz tasnif yok" in s.inner_text("#sayfaKaynak")
                and "0,0 MB / 100 MB" in s.inner_text("#sayfaKaynak .kaynak-kota-yazi"), s.inner_text("#sayfaKaynak")[:200])
        kontrol("kökte + doğrudan tasnif açar (menüsüz)", s.locator("#sayfaKaynak .kaynak-fab-secenek").count() == 0
                and s.get_attribute("#sayfaKaynak .kaynak-fab-ana", "aria-label") == "Yeni tasnif")

        # ---- Üç kademe tasnif, + menüsü ----
        tasnif_ac(s, "Algoritma")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Algoritma')")
        kontrol("tasnif açılır", baslik(s) == "Algoritma", baslik(s))
        kontrol("tasnif sayfasında MB yazmaz", s.locator("#sayfaKaynak .kaynak-kota").count() == 0)
        s.click("#sayfaKaynak .kaynak-fab-ana")
        secenekler = s.locator("#sayfaKaynak .kaynak-fab-secenek").all_inner_texts()
        kontrol("+ menüsü: Not, Resim, Alt tasnif (simgeli)", [x.strip() for x in secenekler] == ["Not", "Resim", "Alt tasnif"]
                and s.locator("#sayfaKaynak .kaynak-fab-secenek .simge svg").count() == 3, secenekler)
        s.screenshot(path="kaynak-fab.png")
        s.keyboard.press("Escape")
        kontrol("Esc menüyü kapatır", not s.locator("#sayfaKaynak .kaynak-fab.acik").count())
        s.click("#sayfaKaynak .kaynak-fab-ana")
        s.click("#sayfaKaynak .kaynak-fab-perde", position={"x": 20, "y": 200})
        kontrol("perdeye dokununca menü kapanır", not s.locator("#sayfaKaynak .kaynak-fab.acik").count())
        tasnif_ac(s, "3. hafta", True)
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('3. hafta')")
        tasnif_ac(s, "Tahta", True)
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Tahta')")
        s.click("#sayfaKaynak .kaynak-fab-ana")
        kontrol("3. kademede + menüsünde Alt tasnif yok", baslik(s) == "Tahta" and
                [x.strip() for x in s.locator("#sayfaKaynak .kaynak-fab-secenek").all_inner_texts()] == ["Not", "Resim"])
        s.keyboard.press("Escape")
        kontrol("3. kademede yol yazılı", s.inner_text("#sayfaKaynak .kaynak-yol") == "Algoritma › 3. hafta › Tahta", s.inner_text("#sayfaKaynak .kaynak-yol"))
        kuyruk_bossa(s)
        kontrol("veritabanında kademeler 1-2-3 (uygulamanın ürettiği kimliklerle)",
                sql("select array_agg(derinlik order by derinlik)::text as d from public.kaynak_tasnif")[0]["d"] == "{1,2,3}")

        # ---- Resim: küçültme, WebP, kutucuk ----
        resim_ekle(s, [F1, F2])
        kontrol("iki resim yüklenir ve görünür", resim_bekle(s, 2) and kuyruk_bossa(s))
        satirlar = sql("select id::text, bayt, en, boy from public.kaynak_oge where tur = 'resim' order by olusma")
        kontrol("uzun kenar 2048 px'e iner (4000×3000 → 2048×1536, 2448×3264 → 1536×2048)",
                [(x["en"], x["boy"]) for x in satirlar] == [(2048, 1536), (1536, 2048)], satirlar)
        kontrol("WebP çok küçülür (%d KB ve %d KB JPEG'den)" % (B1 // 1024, B2 // 1024),
                all(x["bayt"] < 0.5 * b for x, b in zip(satirlar, [B1, B2])), [(x["bayt"] // 1024, b // 1024) for x, b in zip(satirlar, [B1, B2])])
        anahtarlar = r2()
        kontrol("R2'de iki .webp, uygulamanın kimlikleriyle", len(anahtarlar) == 2 and all(any(x["id"] in a for a in anahtarlar) for x in satirlar), anahtarlar)
        kontrol("canvas WebP verdiği için kodlayıcı inmedi", not any("webp/kodla.js" in u for u in istekler))
        sutunlar = s.evaluate("() => Array.from(document.querySelectorAll('#sayfaKaynak .kaynak-sutun')).map(x => x.children.length)")
        kontrol("kutucuklar iki sütunda, her sütunda biri", sutunlar == [1, 1], sutunlar)

        # ---- iPhone (Safari) yolu: canvas WebP vermez → WebAssembly kodlayıcı ----
        s.evaluate("""() => { const asil = HTMLCanvasElement.prototype.toBlob;
            HTMLCanvasElement.prototype.toBlob = function (cb, tur, q) { return asil.call(this, cb, tur === 'image/webp' ? 'image/png' : tur, q); }; }""")
        resim_ekle(s, [F1])
        kontrol("Safari yolu: resim yine yüklenir", resim_bekle(s, 3, 60) and kuyruk_bossa(s))
        son = sql("select bayt from public.kaynak_oge where tur = 'resim' order by olusma desc limit 1")[0]
        kontrol("Safari yolu: WebAssembly kodlayıcı indi", any("webp/kodla.js" in u for u in istekler) and any("webp_enc.wasm" in u for u in istekler))
        kontrol("Safari yolu: boyut canvas WebP'siyle aynı ölçüde (%d KB)" % (son["bayt"] // 1024), son["bayt"] < 0.5 * B1)
        sira = s.evaluate("() => Array.from(document.querySelectorAll('#sayfaKaynak .kaynak-resim-kart img')).map(i => [i.dataset.sira, i.getAttribute('data-resim')]).sort((a, b) => a[0] - b[0]).map(x => x[1])")
        db_sira = [x["id"] for x in sql("select id::text from public.kaynak_oge where tur = 'resim' order by olusma desc")]
        kontrol("kutucuk sırası: en yeni üstte", sira == db_sira, (sira, db_sira))

        # ---- Büyüteç: dizi ekrandaki sırayla gezilir ----
        ilk_kart = s.evaluate("() => { const i = Array.from(document.querySelectorAll('#sayfaKaynak .kaynak-resim-kart img')).find(x => x.dataset.sira === '0'); return i.getAttribute('data-resim'); }")
        s.click("#sayfaKaynak .kaynak-resim-kart:has(img[data-sira='0']) .kaynak-resim-ac")
        s.wait_for_selector(".buyutec")
        kontrol("büyüteç 1 / 3 ile açılır", s.inner_text(".buyutec-ust span").startswith("1 / 3"), s.inner_text(".buyutec-ust span"))
        s.click(".buyutec-ok.ileri"); s.click(".buyutec-ok.ileri")
        kontrol("ileri: 3 / 3", s.inner_text(".buyutec-ust span").startswith("3 / 3"))
        geri(s)
        kontrol("geri tuşu büyüteci kapatır, tasnif yerinde", s.locator(".buyutec").count() == 0 and baslik(s) == "Tahta")

        # ---- 5 sn geri alınabilir silme (resim) ----
        n_once = len(r2())
        s.click("#sayfaKaynak .kaynak-resim-kart:has(img[data-sira='0']) .kaynak-resim-sil")
        s.wait_for_selector(".geri-al")
        kontrol("silince hemen gizlenir, 'Resim silindi · Geri al (5)'", s.locator("#sayfaKaynak .kaynak-resim-kart").count() == 2
                and "Resim silindi" in s.inner_text(".geri-al") and "(5)" in s.inner_text(".geri-al-dugme"), s.inner_text(".geri-al"))
        s.wait_for_timeout(1300)
        kontrol("geri sayım iner (4 ya da 3)", any(x in s.inner_text(".geri-al-dugme") for x in ("(4)", "(3)")), s.inner_text(".geri-al-dugme"))
        kontrol("+ düğmesi bildirimin üstüne kalkar", s.evaluate("() => document.documentElement.classList.contains('geri-al-var')"))
        s.click(".geri-al-dugme")
        kontrol("Geri al: resim geri gelir, sunucuda dokunulmamış", s.locator("#sayfaKaynak .kaynak-resim-kart").count() == 3 and len(r2()) == n_once
                and s.locator(".geri-al").count() == 0)
        s.wait_for_timeout(5500)
        kontrol("geri alınan resim 5 sn sonra da yerinde", s.locator("#sayfaKaynak .kaynak-resim-kart").count() == 3
                and tek("select count(*)::int as n from public.kaynak_oge where id = '%s'" % ilk_kart)["n"] == 1)
        s.click("#sayfaKaynak .kaynak-resim-kart:has(img[data-sira='0']) .kaynak-resim-sil")
        s.wait_for_timeout(1500)
        kontrol("süre dolmadan sunucuda silinmez", tek("select count(*)::int as n from public.kaynak_oge where id = '%s'" % ilk_kart)["n"] == 1)
        bekle_ki(s, lambda: s.locator(".geri-al").count() == 0, 8)
        kuyruk_bossa(s)
        kontrol("5 sn sonra kalıcı silinir (veritabanı ve R2)", tek("select count(*)::int as n from public.kaynak_oge where id = '%s'" % ilk_kart)["n"] == 0
                and not any(ilk_kart in a for a in r2()))

        # ---- Sekmenin kendi geçmişi ----
        s.click(".alt-cubuk button:has-text('Temrin')"); s.wait_for_timeout(200)
        s.click(".alt-cubuk button:has-text('Notlar')"); s.wait_for_timeout(200)
        kontrol("başka sekmeden dönünce tasnif yerinde", baslik(s) == "Tahta")
        geri(s)
        kontrol("geri: üst tasnif (3. hafta)", baslik(s) == "3. hafta", baslik(s))
        s.click("#sayfaKaynak button.geri")
        s.wait_for_timeout(350)
        kontrol("'‹ Algoritma' düğmesi: Algoritma", baslik(s) == "Algoritma", baslik(s))
        geri(s)
        kontrol("geri: Notlar kökü", baslik(s) == "Notlar", baslik(s))
        kontrol("kökte hak yazısı var", s.locator("#sayfaKaynak .kaynak-kota-yazi").count() == 1)
        geri(s)
        kontrol("kökte geri: Kıraat", s.evaluate("() => aktifSekme") == "oku")

        # ---- Bağlantısız çalışma: değişiklikler cihazda bekler, bağlantı gelince gider ----
        notlara_git(s)
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Algoritma')")
        c.set_offline(True)
        s.evaluate("() => window.dispatchEvent(new Event('offline'))")
        s.wait_for_timeout(200)
        kontrol("bağlantı yokken uyarı: yine de yazılabilir", "Bağlantı yok" in s.inner_text("#sayfaKaynak .kaynak-uyari"), s.inner_text("#sayfaKaynak")[:200])
        tasnif_ac(s, "Çevrimdışı", True)
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Çevrimdışı')")
        resim_ekle(s, [F3])
        bekle_ki(s, lambda: s.locator("#sayfaKaynak .kaynak-resim-kart").count() == 1 and s.locator("#sayfaKaynak .kaynak-is").count() == 0, 30)
        editor_ac_yeni(s)
        s.fill(".not-editor .ne-baslik", "Sınıfta yazıldı")
        s.click(".not-editor .ne-metin"); s.keyboard.type("İnternet yokken.")
        s.wait_for_timeout(200)
        kontrol("editörde: bağlantı yok, cihaza kaydedildi uyarısı", bekle_ki(s, lambda: "Bağlantı yok" in s.inner_text(".not-editor .ne-uyari"), 4),
                s.inner_text(".not-editor .ne-uyari"))
        editor_kapat(s)
        bekleyen = kuyruk(s)
        kontrol("3 iş sırada (tasnif, resim, not; sunucuya hiçbiri gitmedi)", bekleyen == 3 and
                tek("select count(*)::int as n from public.kaynak_tasnif where ad = 'Çevrimdışı'")["n"] == 0, bekleyen)
        kontrol("bekleyen resimde ve notta 'gönderilmeyi bekliyor' işareti", s.locator("#sayfaKaynak .kk-rozet").count() == 2)
        kontrol("uyarı bekleyen değişiklik sayısını söyler", "3 değişiklik bu cihazda" in s.inner_text("#sayfaKaynak .kaynak-uyari"), s.inner_text("#sayfaKaynak .kaynak-uyari"))
        kayitli = s.evaluate("async () => (await vt.onEkli('kaynak', 'k/')).map(x => x.is).sort((a, b) => a.no < b.no ? -1 : 1).map(x => x.tur)")
        kontrol("sıra cihaza yazıldı, her iş ayrı kayıt (uygulama kapansa da kaybolmaz)", kayitli == ["tasnif_ekle", "resim_ekle", "not_ekle"], kayitli)
        cevrimdisi_an = s.evaluate("() => new Date().toISOString()")
        s.wait_for_timeout(2500)
        c.set_offline(False)
        s.evaluate("() => window.dispatchEvent(new Event('online'))")
        kontrol("bağlantı gelince sıra gönderilir", kuyruk_bossa(s, 40))
        r = tek("select o.baslik, o.metin, o.olusma::text, t.ad from public.kaynak_oge o join public.kaynak_tasnif t on t.id = o.tasnif where o.tur = 'not' and o.baslik = 'Sınıfta yazıldı'")
        kontrol("çevrimdışı not sunucuda, kendi tasnifinde", r and r["ad"] == "Çevrimdışı" and "İnternet yokken." in r["metin"], r)
        r2_ = tek("select (extract(epoch from (now() - olusma)))::int as fark from public.kaynak_oge where tur = 'not' and baslik = 'Sınıfta yazıldı'")
        kontrol("notun oluşma anı yazıldığı an (gönderildiği an değil)", r2_ and r2_["fark"] >= 2, r2_)
        kontrol("rozetler kalkar", bekle_ki(s, lambda: s.locator("#sayfaKaynak .kk-rozet").count() == 0, 10))

        # ---- Sıra kalıcı: sunucuya ulaşılamazken sayfa yenilenir, sonra gider ----
        WORKER_KAPALI["evet"] = True
        resim_ekle(s, [F1])
        bekle_ki(s, lambda: s.locator("#sayfaKaynak .kaynak-resim-kart").count() == 2 and s.locator("#sayfaKaynak .kaynak-is").count() == 0, 30)
        s.wait_for_timeout(800)
        kontrol("Worker'a ulaşılamıyor: resim sırada, hata sayılmaz (geçici)", kuyruk(s) == 1 and
                s.evaluate("() => KAYNAK_KUYRUK[0].durum") == "bekliyor")
        WORKER_KAPALI["evet"] = False
        s.reload(); s.wait_for_selector(".alt-cubuk")
        bekle_ki(s, lambda: s.evaluate("() => typeof KAYNAK_KUYRUK !== 'undefined'"), 10)
        kontrol("yeniden açılınca sıra kendiliğinden gönderilir (Notlar açılmadan)", bekle_ki(s, lambda: s.evaluate("() => KAYNAK_KUYRUK.length === 0 && KAYNAK.yuklendi"), 30)
                and tek("select count(*)::int as n from public.kaynak_oge o join public.kaynak_tasnif t on t.id = o.tasnif where o.tur = 'resim' and t.ad = 'Çevrimdışı'")["n"] == 2)

        # ---- Hak sınırı: yer yoksa resim hiç sıraya girmez ----
        notlara_git(s)
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Algoritma')")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Çevrimdışı')")
        sql("update public.kaynak_kota set azami_mb = 0")
        s.evaluate("() => kaynakYenile()"); s.wait_for_timeout(800)
        resim_ekle(s, [F2])
        s.wait_for_selector(".uyari-perde", timeout=40000)
        kontrol("hak dolunca uyarı", "hakkınız doldu" in s.inner_text(".uyari-perde"), s.inner_text(".uyari-perde"))
        s.click(".uyari-perde .evet")
        kontrol("reddedilen resim sırada da cihazda da yok", kuyruk(s) == 0 and s.locator("#sayfaKaynak .kaynak-resim-kart").count() == 2)
        sql("update public.kaynak_kota set azami_mb = 100")
        s.evaluate("() => kaynakYenile()"); s.wait_for_timeout(500)

        # ---- Sunucu reddederse (kalıcı hata) cihazda kalır, gösterilir ----
        sql("update public.kaynak_kota set azami_mb = 0")
        s.evaluate("() => { KAYNAK_SUNUCU.durum = null; kaynakGorunumuKur(); }")   # uygulama hakkı bilmiyor (ör. bağlantısız açıldı)
        resim_ekle(s, [F2])
        kontrol("sunucu reddedince resim kutucuğu 'gönderilemedi' olur", bekle_ki(s, lambda: s.locator("#sayfaKaynak .kaynak-resim-kart.hata").count() == 1, 40))
        kontrol("üstte 'gönderilemedi' uyarısı ve Yeniden dene", "gönderilemedi" in s.inner_text("#sayfaKaynak .kaynak-uyari.hata"), s.inner_text("#sayfaKaynak"))
        sql("update public.kaynak_kota set azami_mb = 100")
        s.click("#sayfaKaynak .kaynak-uyari.hata button")
        kontrol("Yeniden dene: hak açılınca yüklenir", kuyruk_bossa(s, 30) and s.locator("#sayfaKaynak .kaynak-resim-kart.hata").count() == 0
                and s.locator("#sayfaKaynak .kaynak-resim-kart").count() == 3)
        s.evaluate("() => kaynakYenile()"); s.wait_for_timeout(500)

        # ---- Hesap › Notlar: hak ve Resimler kutusu, panel ----
        cekmece(s, "hesap")
        s.wait_for_selector(".kaynak-hesap .kaynak-resim-kutusu")
        n_resim = tek("select count(*)::int as n from public.kaynak_oge where tur = 'resim'")["n"]
        kontrol("Hesap'ta Notlar: hak yazısı ve 'Resimler' kutusu (resimler doğrudan görünmez)",
                s.locator(".kaynak-hesap .kaynak-kota-yazi").count() == 1 and s.locator(".kaynak-hesap .kaynak-hesap-satir").count() == 0
                and ("%d resim" % n_resim) in s.inner_text(".kaynak-resim-kutusu"), s.inner_text(".kaynak-hesap"))
        s.click(".kaynak-resim-kutusu")
        s.wait_for_selector(".kaynak-resim-paneli .kaynak-hesap-satir")
        kontrol("panel açılır: bütün resimler ve yolları", s.locator(".kaynak-resim-paneli .kaynak-hesap-satir").count() == n_resim
                and "Algoritma › Çevrimdışı" in s.inner_text(".kaynak-resim-paneli"), s.inner_text(".kaynak-resim-paneli")[:300])
        s.screenshot(path="kaynak-hesap.png")
        once = s.inner_text(".kaynak-hesap .kaynak-kota-yazi")
        s.click(".kaynak-resim-paneli .kaynak-hesap-satir >> nth=0 >> .kaynak-hesap-sil")
        kontrol("panelden silme: hemen gizlenir, geri al çıkar", s.locator(".kaynak-resim-paneli .kaynak-hesap-satir").count() == n_resim - 1
                and s.locator(".geri-al").count() == 1)
        bekle_ki(s, lambda: s.locator(".geri-al").count() == 0, 8)
        kuyruk_bossa(s)
        kontrol("5 sn sonra silinir (veritabanı)", tek("select count(*)::int as n from public.kaynak_oge where tur = 'resim'")["n"] == n_resim - 1)
        kontrol("Hesap'taki hak yazısı azalır", s.inner_text(".kaynak-hesap .kaynak-kota-yazi") != once, (once, s.inner_text(".kaynak-hesap .kaynak-kota-yazi")))
        geri(s)
        kontrol("geri tuşu yalnızca paneli kapatır", s.locator(".kaynak-resim-paneli").count() == 0 and s.locator(".hesap-sayfa.acik").count() == 1)
        geri(s)
        bekle_ki(s, lambda: s.locator(".hesap-sayfa").count() == 0, 5)

        # ---- Ad değiştirme; içi dolu tasnifi silme (onay + geri al) ----
        notlara_git(s)
        s.click(".alt-cubuk button:has-text('Notlar')")   # köke
        s.wait_for_timeout(200)
        kontrol("etkin Notlar sekmesine yeniden dokununca köke dönülür", baslik(s) == "Notlar", baslik(s))
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Algoritma')")
        s.click("#sayfaKaynak .kaynak-menu button:has-text('Adını değiştir')")
        yaz_ve_onayla(s, "Algoritma ve Programlama", "Kaydet")
        kontrol("ad değişir", bekle_ki(s, lambda: baslik(s) == "Algoritma ve Programlama", 5) and kuyruk_bossa(s)
                and tek("select count(*)::int as n from public.kaynak_tasnif where ad = 'Algoritma ve Programlama'")["n"] == 1)
        s.click("#sayfaKaynak .kaynak-menu button:has-text('Tasnifi sil')")
        s.wait_for_selector(".uyari-perde")
        metin = s.inner_text(".uyari-perde")
        kontrol("silme onayı içindekileri sayar ve geri alınabileceğini söyler", "3 alt tasnif" in metin and "1 not" in metin and "resim" in metin and "5 saniye" in metin, metin)
        s.click(".uyari-perde .evet")
        bekle_ki(s, lambda: baslik(s) == "Notlar")
        kontrol("silinen tasnifin içinden köke çıkılır, tasnif gizlenir", baslik(s) == "Notlar" and s.locator("#sayfaKaynak .kaynak-tasnif").count() == 0)
        s.click(".geri-al-dugme")
        kontrol("Geri al: tasnif bütün içiyle geri gelir", s.locator("#sayfaKaynak .kaynak-tasnif:has-text('Algoritma ve Programlama')").count() == 1)
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Algoritma ve Programlama')")
        s.click("#sayfaKaynak .kaynak-menu button:has-text('Tasnifi sil')")
        onayla(s)
        bekle_ki(s, lambda: s.locator(".geri-al").count() == 0, 8)
        kuyruk_bossa(s)
        kontrol("5 sn sonra tasnif bütün içiyle silinir: tablolar ve R2 boş",
                tek("select count(*)::int as n from public.kaynak_tasnif")["n"] == 0 and tek("select count(*)::int as n from public.kaynak_oge")["n"] == 0
                and len(r2()) == 0, r2())
        kontrol("hak sıfıra döner", "0,0 MB / 100 MB" in s.inner_text("#sayfaKaynak .kaynak-kota-yazi"), s.inner_text("#sayfaKaynak .kaynak-kota-yazi"))

        # ---- Boş tasnif onaysız silinir; uygulama arka plana geçince silme hemen sıraya girer ----
        tasnif_ac(s, "Geçici")
        kuyruk_bossa(s)
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Geçici')")
        s.click("#sayfaKaynak .kaynak-menu button:has-text('Tasnifi sil')")
        kontrol("boş tasnif onaysız silinir (geri al çıkar)", s.locator(".uyari-perde").count() == 0 and s.locator(".geri-al").count() == 1)
        s.evaluate("""() => { Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'hidden' });
            document.dispatchEvent(new Event('visibilitychange')); delete document.visibilityState; }""")
        kontrol("arka plana geçince geri sayım beklenmeden silinir", kuyruk_bossa(s, 10) and s.locator(".geri-al").count() == 0
                and tek("select count(*)::int as n from public.kaynak_tasnif")["n"] == 0)

        # ---- Çıkışta gönderilmemiş değişiklik uyarısı ----
        tasnif_ac(s, "Son")
        kuyruk_bossa(s)
        c.set_offline(True)
        s.evaluate("() => window.dispatchEvent(new Event('offline'))")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Son')")
        editor_ac_yeni(s)
        s.click(".not-editor .ne-metin"); s.keyboard.type("gönderilmedi")
        editor_kapat(s)
        cekmece(s, "hesap")
        s.click(".hesap-sayfa button:has-text('Çıkış yap')")
        s.wait_for_selector(".uyari-perde")
        kontrol("çıkışta Notlar'daki gönderilmemiş değişiklik sayılır", "1 değişiklik henüz hesabınıza gönderilemedi" in s.inner_text(".uyari-perde"), s.inner_text(".uyari-perde"))
        s.click(".uyari-perde .hayir")
        c.set_offline(False)
        s.evaluate("() => window.dispatchEvent(new Event('online'))")
        kuyruk_bossa(s)
        geri(s)

        # ---- Görünüm: 358 px, taşma yok ----
        s.click(".alt-cubuk button:has-text('Notlar')")
        s.wait_for_timeout(200)
        tasnif_ac(s, "Çok uzun bir tasnif adı: Temel Elektrik ve Elektronik 7. hafta tahta resimleri")
        s.set_viewport_size({"width": 358, "height": 760})
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Son')")
        resim_ekle(s, [F2]); resim_bekle(s, 1)
        tasma = s.evaluate("""() => { const r = []; document.querySelectorAll('#sayfaKaynak *, .alt-cubuk *').forEach(e => {
            const b = e.getBoundingClientRect(); if (b.width && b.right > innerWidth + 1) r.push(e.className || e.tagName); }); return r.slice(0, 5); }""")
        kontrol("358 px'te taşma yok (Notlar, kutucuklar, + ve 5 sekmeli alt çubuk)", not tasma, tasma)
        satirlar_ = s.evaluate("() => new Set(Array.from(document.querySelectorAll('.alt-cubuk button')).map(b => Math.round(b.getBoundingClientRect().top))).size")
        kontrol("alt çubuktaki 5 sekme tek satırda", satirlar_ == 1, satirlar_)
        fab_kutu = s.evaluate("() => { const b = document.querySelector('#sayfaKaynak .kaynak-fab-ana').getBoundingClientRect(); const a = document.querySelector('.alt-cubuk').getBoundingClientRect(); return [b.bottom <= a.top, b.right <= innerWidth]; }")
        kontrol("+ düğmesi alt çubuğun üstünde ve ekranın içinde", fab_kutu == [True, True], fab_kutu)
        s.screenshot(path="kaynak-kok.png")
        c.close()
finally:
    sunucu.kill()

# Sunucunun reddettiği resim (hak) ve kapalı Worker isteği tarayıcı konsoluna düşer; beklenen yanıtlardır
kontrol("sayfa hatası yok", not [h for h in hatalar if "favicon" not in h and "status of 413" not in h and "ERR_FAILED" not in h and "Failed to fetch" not in h and "ERR_INTERNET_DISCONNECTED" not in h], hatalar[:5])
gecen = sum(1 for _, k in sonuclar if k)
print("\n%d/%d geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) else 1)

"""Kaynak sekmesi — uçtan uca.
Uygulama gerçek şemaya (yerel PostgreSQL, 01-sema.sql) ve gerçek Worker koduna
(kaynak-worker/worker.js, R2 bellekte) karşı çalışır: istekler taklit sunucuya
(test/kaynak/sahte_sunucu.mjs) aktarılır. PostgreSQL 5499'da çalışıyor olmalı
(DEVIR-NOTU.md, test düzeneği)."""
import subprocess, io, os, sys
exec(open("vt_taban.py", encoding="utf-8").read())
from PIL import Image, ImageDraw
import random

KAYNAK_PORT = 8796
KT = "http://127.0.0.1:%d" % KAYNAK_PORT
KOK_DIZIN = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))

# Veritabanı baştan kurulur, taklit sunucu açılır
subprocess.run(["sh", os.path.join(KOK_DIZIN, "test", "sql", "calistir.sh")], check=True, stdout=subprocess.DEVNULL)
sunucu = subprocess.Popen(["node", os.path.join(KOK_DIZIN, "test", "kaynak", "sahte_sunucu.mjs"), str(KAYNAK_PORT)], stdout=subprocess.PIPE)
sunucu.stdout.readline()
import urllib.request
def sql(q):
    return json.loads(urllib.request.urlopen(urllib.request.Request(KT + "/sql", data=q.encode(), method="POST")).read())
def r2():
    return json.loads(urllib.request.urlopen(KT + "/r2").read())

# Deneme fotoğrafları: tahta fotoğrafına benzer (gürültü + yazı), telefon boyutunda
def foto(ad, en, boy, tohum):
    random.seed(tohum)
    im = Image.effect_noise((en, boy), 40).convert("RGB")
    im = Image.blend(im, Image.linear_gradient("L").resize((en, boy)).convert("RGB"), 0.5)
    d = ImageDraw.Draw(im)
    for i in range(40):
        d.text((random.randint(0, en - 400), random.randint(0, boy - 50)), "R = U / I  Algoritma %d" % i, fill=(20, 20, 20))
    yol = "/tmp/claude-0/" + ad
    im.save(yol, "JPEG", quality=92)
    return yol, os.path.getsize(yol)
F1, B1 = foto("kaynak-yatay.jpg", 4000, 3000, 1)
F2, B2 = foto("kaynak-dikey.jpg", 2448, 3264, 2)

def aktar(route, request):
    """Kaynak isteklerini taklit sunucuya aktarır (CORS'u Worker'ın kendisi yapar)"""
    u = urllib.parse.urlparse(request.url)
    if u.netloc == "kaynak.test":
        hedef = KT + "/worker" + u.path + (("?" + u.query) if u.query else "")
        cevap = route.fetch(url=hedef)
        return route.fulfill(response=cevap)
    # Supabase: kaynak tabloları ve işlevleri
    if request.method == "OPTIONS":
        return route.fulfill(status=204, headers={"access-control-allow-origin": "*", "access-control-allow-methods": "GET,POST,PATCH,DELETE,OPTIONS",
                                                  "access-control-allow-headers": request.headers.get("access-control-request-headers", "*")}, body="")
    cevap = route.fetch(url=KT + u.path + (("?" + u.query) if u.query else ""))
    return route.fulfill(response=cevap, headers={**cevap.headers, "access-control-allow-origin": "*"})

def giris(s):
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    kod_iste_ve_gir(s)
    s.wait_for_selector(".sozlesme")
    s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')")
    bekle_ki(s, lambda: s.evaluate("() => KONULAR.size") > 0)

def yaz_ve_onayla(s, metin, dugme):
    s.wait_for_selector(".uyari-perde .uyari-girdi")
    s.fill(".uyari-perde .uyari-girdi", metin)
    s.click(".uyari-perde button:has-text('%s')" % dugme)
    s.wait_for_selector(".uyari-perde", state="detached")

def baslik(s):
    return s.evaluate("() => (document.querySelector('#sayfaKaynak h2') || {}).textContent || ''")

def geri(s):
    s.go_back(); s.wait_for_timeout(350)

def resim_bekle(s, n, sure=40):
    return bekle_ki(s, lambda: s.locator("#sayfaKaynak .kaynak-resim-ac img[src^='blob:']").count() == n and s.locator("#sayfaKaynak .kaynak-is").count() == 0, sure)

try:
    with sync_playwright() as p:
        c, s = cihaz_ac(p, "K")
        c.route("**/rest/v1/kaynak_**", aktar)
        c.route("**/rest/v1/rpc/kaynak_**", aktar)
        c.route("https://kaynak.test/**", aktar)
        istekler = []
        s.on("request", lambda r: istekler.append(r.url))
        giris(s)

        etiketler = s.locator(".alt-cubuk button span").all_inner_texts()
        kontrol("alt çubukta Kaynak beşinci sekme", etiketler == ["Kıraat", "Ara", "Temrin", "42 Tarzı", "Kaynak"], etiketler)
        s.click(".alt-cubuk button:has-text('Kaynak')")
        s.wait_for_selector("#sayfaKaynak .eylem button:has-text('Yeni tasnif')")
        kontrol("kökte boş durum ve kota (0 / 100 MB)", "Henüz tasnif yok" in s.inner_text("#sayfaKaynak") and "0,0 MB / 100 MB" in s.inner_text("#sayfaKaynak .kaynak-kota-yazi"),
                s.inner_text("#sayfaKaynak")[:200])

        # ---- Üç kademe tasnif ----
        s.click("#sayfaKaynak button:has-text('Yeni tasnif')")
        yaz_ve_onayla(s, "Algoritma", "Oluştur")
        s.wait_for_selector("#sayfaKaynak .kaynak-tasnif:has-text('Algoritma')")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Algoritma')")
        kontrol("tasnif açılır", baslik(s) == "Algoritma", baslik(s))
        s.click("#sayfaKaynak button:has-text('Alt tasnif')")
        yaz_ve_onayla(s, "3. hafta", "Oluştur")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('3. hafta')")
        s.click("#sayfaKaynak button:has-text('Alt tasnif')")
        yaz_ve_onayla(s, "Tahta", "Oluştur")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Tahta')")
        kontrol("3. kademede 'Alt tasnif' düğmesi yok", baslik(s) == "Tahta" and s.locator("#sayfaKaynak button:has-text('Alt tasnif')").count() == 0)
        kontrol("3. kademede yol yazılı", s.inner_text("#sayfaKaynak .kaynak-yol") == "Algoritma › 3. hafta › Tahta", s.inner_text("#sayfaKaynak .kaynak-yol"))
        kontrol("veritabanında kademeler 1-2-3", sql("select array_agg(derinlik order by derinlik)::text as d from public.kaynak_tasnif")[0]["d"] == "{1,2,3}")

        # ---- Resim ekleme: küçültme ve WebP ----
        s.set_input_files("#sayfaKaynak input[type=file]", [F1, F2])
        kontrol("iki resim yüklenir ve görünür", resim_bekle(s, 2))
        satirlar = sql("select bayt, en, boy from public.kaynak_oge where tur = 'resim' order by olusma")
        kontrol("uzun kenar 2048 px'e iner (4000×3000 → 2048×1536, 2448×3264 → 1536×2048)",
                [(x["en"], x["boy"]) for x in satirlar] == [(2048, 1536), (1536, 2048)], satirlar)
        kontrol("WebP çok küçülür (%d KB ve %d KB JPEG'den)" % (B1 // 1024, B2 // 1024),
                all(x["bayt"] < 0.5 * b for x, b in zip(satirlar, [B1, B2])), [(x["bayt"] // 1024, b // 1024) for x, b in zip(satirlar, [B1, B2])])
        anahtarlar = r2()
        kontrol("R2'de iki .webp", len(anahtarlar) == 2 and all(a.endswith(".webp") for a in anahtarlar), anahtarlar)
        kontrol("kota çubuğu güncellendi", "0,0 MB" not in s.inner_text("#sayfaKaynak .kaynak-kota-yazi"), s.inner_text("#sayfaKaynak .kaynak-kota-yazi"))
        kontrol("canvas WebP verdiği için kodlayıcı inmedi", not any("webp/kodla.js" in u for u in istekler))

        # ---- iPhone (Safari) yolu: canvas WebP vermez → WebAssembly kodlayıcı ----
        s.evaluate("""() => { const asil = HTMLCanvasElement.prototype.toBlob;
            HTMLCanvasElement.prototype.toBlob = function (cb, tur, q) { return asil.call(this, cb, tur === 'image/webp' ? 'image/png' : tur, q); }; }""")
        s.set_input_files("#sayfaKaynak input[type=file]", [F1])
        kontrol("Safari yolu: resim yine yüklenir", resim_bekle(s, 3, 60))
        son = sql("select id, bayt from public.kaynak_oge where tur = 'resim' order by olusma desc limit 1")[0]
        kontrol("Safari yolu: WebAssembly kodlayıcı indi", any("webp/kodla.js" in u for u in istekler) and any("webp_enc.wasm" in u for u in istekler))
        kontrol("Safari yolu: boyut canvas WebP'siyle aynı ölçüde (%d KB)" % (son["bayt"] // 1024), son["bayt"] < 0.5 * B1)

        # ---- Not ----
        s.click("#sayfaKaynak button:has-text('Not yaz')")
        yaz_ve_onayla(s, "Hoca: akış şeması sınavda çıkar.\nİkinci satır.", "Kaydet")
        s.wait_for_selector("#sayfaKaynak .kaynak-not")
        sira = s.evaluate("() => Array.from(document.querySelectorAll('#sayfaKaynak .kaynak-izgara, #sayfaKaynak .kaynak-not')).map(e => e.className)")
        kontrol("zaman sırası: önce eklenen resimler, sonra not", sira == ["kaynak-izgara", "kaynak-not"], sira)
        kontrol("not satır sonlarıyla görünür", s.inner_text("#sayfaKaynak .kaynak-not-metin") == "Hoca: akış şeması sınavda çıkar.\nİkinci satır.", s.inner_text("#sayfaKaynak .kaynak-not-metin"))
        s.click("#sayfaKaynak .kaynak-not button:has-text('Düzenle')")
        yaz_ve_onayla(s, "Düzeltilmiş not", "Kaydet")
        kontrol("not düzenlenir", bekle_ki(s, lambda: s.inner_text("#sayfaKaynak .kaynak-not-metin") == "Düzeltilmiş not", 5)
                and sql("select metin from public.kaynak_oge where tur = 'not'")[0]["metin"] == "Düzeltilmiş not")
        s.click("#sayfaKaynak .kaynak-not button:has-text('Düzenle')")
        s.click(".uyari-perde button:has-text('Vazgeç')")
        kontrol("vazgeçince not değişmez", s.inner_text("#sayfaKaynak .kaynak-not-metin") == "Düzeltilmiş not")

        # ---- Büyüteç ----
        s.click("#sayfaKaynak .kaynak-resim-ac >> nth=0")
        s.wait_for_selector(".buyutec")
        geri(s)
        kontrol("resim büyüteçte açılır, geri tuşu kapatır, tasnif yerinde", s.locator(".buyutec").count() == 0 and baslik(s) == "Tahta")

        # ---- Sekmenin kendi geçmişi ----
        s.click(".alt-cubuk button:has-text('Temrin')"); s.wait_for_timeout(200)
        s.click(".alt-cubuk button:has-text('Kaynak')"); s.wait_for_timeout(200)
        kontrol("başka sekmeden dönünce tasnif yerinde", baslik(s) == "Tahta")
        geri(s)
        kontrol("geri: üst tasnif (3. hafta)", baslik(s) == "3. hafta", baslik(s))
        s.click("#sayfaKaynak button.geri")
        s.wait_for_timeout(350)
        kontrol("'‹ Algoritma' düğmesi: Algoritma", baslik(s) == "Algoritma", baslik(s))
        geri(s)
        kontrol("geri: Kaynak kökü", baslik(s) == "Kaynak", baslik(s))
        geri(s)
        kontrol("kökte geri: Kıraat", s.evaluate("() => aktifSekme") == "oku")

        # ---- Hesap ekranı: yedekli resimler ----
        cekmece(s, "hesap")
        s.wait_for_selector(".kaynak-hesap .kaynak-hesap-satir")
        kontrol("Hesap'ta 3 yedekli resim ve yolları", s.locator(".kaynak-hesap .kaynak-hesap-satir").count() == 3
                and "Algoritma › 3. hafta › Tahta" in s.inner_text(".kaynak-hesap"), s.inner_text(".kaynak-hesap")[:300])
        once = s.inner_text(".kaynak-hesap .kaynak-kota-yazi")
        s.click(".kaynak-hesap .kaynak-hesap-satir >> nth=0 >> .kaynak-hesap-sil")
        onayla(s)
        bekle_ki(s, lambda: s.locator(".kaynak-hesap .kaynak-hesap-satir").count() == 2)
        kontrol("Hesap'tan silinir (liste, R2, veritabanı)", s.locator(".kaynak-hesap .kaynak-hesap-satir").count() == 2 and len(r2()) == 2
                and sql("select count(*)::int as n from public.kaynak_oge where tur = 'resim'")[0]["n"] == 2)
        kontrol("kota yazısı azalır", s.inner_text(".kaynak-hesap .kaynak-kota-yazi") != once, (once, s.inner_text(".kaynak-hesap .kaynak-kota-yazi")))
        s.screenshot(path="kaynak-hesap.png")
        geri(s)

        # ---- İnternetsiz görüntüleme ----
        s.click(".alt-cubuk button:has-text('Kaynak')")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Algoritma')")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('3. hafta')")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Tahta')")
        resim_bekle(s, 2)
        c.set_offline(True)
        s.evaluate("() => { kaynakResimAdresleriniBirak(); kaynakCiz(); }")
        kontrol("bağlantı yokken uyarı ve resimler cihazdan", resim_bekle(s, 2, 10) and "Bağlantı yok" in s.inner_text("#sayfaKaynak .kaynak-uyari"))
        s.click("#sayfaKaynak button:has-text('Not yaz')")
        s.wait_for_selector(".uyari-perde")
        kontrol("bağlantı yokken not yazılamaz (uyarı)", "internet" in s.inner_text(".uyari-perde"))
        s.click(".uyari-perde .evet")
        c.set_offline(False)
        s.wait_for_timeout(300)

        # ---- Kota ----
        sql("update public.kaynak_kota set azami_mb = 0")
        s.set_input_files("#sayfaKaynak input[type=file]", [F2])
        s.wait_for_selector(".uyari-perde", timeout=40000)
        kontrol("hak dolunca uyarı", "hakkınız doldu" in s.inner_text(".uyari-perde"), s.inner_text(".uyari-perde"))
        s.click(".uyari-perde .evet")
        kontrol("reddedilen resim R2'de yok", len(r2()) == 2)
        sql("update public.kaynak_kota set azami_mb = 100")

        # ---- Ad değiştirme ve silme ----
        geri(s); geri(s)
        kontrol("Algoritma'ya dönüldü", baslik(s) == "Algoritma", baslik(s))
        s.click("#sayfaKaynak .kaynak-menu button:has-text('Adını değiştir')")
        yaz_ve_onayla(s, "Algoritma ve Programlama", "Kaydet")
        kontrol("ad değişir", bekle_ki(s, lambda: baslik(s) == "Algoritma ve Programlama", 5), baslik(s))
        s.click("#sayfaKaynak .kaynak-menu button:has-text('Tasnifi sil')")
        s.wait_for_selector(".uyari-perde")
        metin = s.inner_text(".uyari-perde")
        kontrol("silme onayı içindekileri sayar", "2 alt tasnif" in metin and "2 resim" in metin and "1 not" in metin, metin)
        s.click(".uyari-perde .evet")
        bekle_ki(s, lambda: baslik(s) == "Kaynak")
        kontrol("resimli tasnif silinir: köke dönülür, R2 ve tablolar boş", baslik(s) == "Kaynak" and len(r2()) == 0
                and sql("select count(*)::int as n from public.kaynak_tasnif")[0]["n"] == 0, (baslik(s), r2()))
        kontrol("kota sıfıra döner", "0,0 MB / 100 MB" in s.inner_text("#sayfaKaynak .kaynak-kota-yazi"), s.inner_text("#sayfaKaynak .kaynak-kota-yazi"))

        # ---- Notlu (resimsiz) tasnif Worker'sız silinir ----
        s.click("#sayfaKaynak button:has-text('Yeni tasnif')")
        yaz_ve_onayla(s, "Notlar", "Oluştur")
        s.click("#sayfaKaynak .kaynak-tasnif:has-text('Notlar')")
        s.click("#sayfaKaynak button:has-text('Not yaz')")
        yaz_ve_onayla(s, "Bir not", "Kaydet")
        n_once = len([u for u in istekler if "kaynak.test/tasnif" in u])
        s.click("#sayfaKaynak .kaynak-menu button:has-text('Tasnifi sil')")
        onayla(s)
        bekle_ki(s, lambda: baslik(s) == "Kaynak")
        kontrol("notlu tasnif kaynak_tasnif_sil ile silinir", sql("select count(*)::int as n from public.kaynak_tasnif")[0]["n"] == 0
                and len([u for u in istekler if "kaynak.test/tasnif" in u]) == n_once)

        # ---- Görünüm: 358 px, taşma yok ----
        s.click("#sayfaKaynak button:has-text('Yeni tasnif')")
        yaz_ve_onayla(s, "Çok uzun bir tasnif adı: Temel Elektrik ve Elektronik 7. hafta tahta fotoğrafları", "Oluştur")
        s.set_viewport_size({"width": 358, "height": 760})
        tasma = s.evaluate("""() => { const r = []; document.querySelectorAll('#sayfaKaynak *, .alt-cubuk *').forEach(e => {
            const b = e.getBoundingClientRect(); if (b.width && b.right > innerWidth + 1) r.push(e.className || e.tagName); }); return r.slice(0, 5); }""")
        kontrol("358 px'te taşma yok (Kaynak ve 5 sekmeli alt çubuk)", not tasma, tasma)
        satirlar_ = s.evaluate("() => new Set(Array.from(document.querySelectorAll('.alt-cubuk button')).map(b => Math.round(b.getBoundingClientRect().top))).size")
        kontrol("alt çubuktaki 5 sekme tek satırda", satirlar_ == 1, satirlar_)
        s.screenshot(path="kaynak-kok.png")
        c.close()
finally:
    sunucu.kill()

# Kota denemesindeki 413 yanıtını tarayıcı konsola yazar; beklenen bir yanıttır
kontrol("sayfa hatası yok", not [h for h in hatalar if "favicon" not in h and "status of 413" not in h], hatalar[:5])
gecen = sum(1 for _, k in sonuclar if k)
print("\n%d/%d geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) else 1)

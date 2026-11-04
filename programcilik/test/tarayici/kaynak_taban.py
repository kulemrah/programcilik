"""Notlar (iç adı kaynak) testlerinin ortak düzeneği.
Uygulama gerçek şemaya (yerel PostgreSQL, 01-sema.sql) ve gerçek Worker koduna
(kaynak-worker/worker.js, R2 bellekte) karşı çalışır: istekler taklit sunucuya
(test/kaynak/sahte_sunucu.mjs) aktarılır. PostgreSQL 5499'da çalışıyor olmalı
(DEVIR-NOTU.md, test düzeneği). Kullanım: exec(open("kaynak_taban.py").read())"""
import subprocess, io, os, sys, random, urllib.request, urllib.parse
exec(open("vt_taban.py", encoding="utf-8").read())
from PIL import Image, ImageDraw

KAYNAK_PORT = 8796
KT = "http://127.0.0.1:%d" % KAYNAK_PORT
KOK_DIZIN = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))

# Veritabanı baştan kurulur, taklit sunucu açılır
subprocess.run(["sh", os.path.join(KOK_DIZIN, "test", "sql", "calistir.sh")], check=True, stdout=subprocess.DEVNULL)
subprocess.run("fuser -k %d/tcp 2>/dev/null" % KAYNAK_PORT, shell=True)
sunucu = subprocess.Popen(["node", os.path.join(KOK_DIZIN, "test", "kaynak", "sahte_sunucu.mjs"), str(KAYNAK_PORT)], stdout=subprocess.PIPE)
sunucu.stdout.readline()

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
    os.makedirs("/tmp/claude-0", exist_ok=True)
    im.save(yol, "JPEG", quality=92)
    return yol, os.path.getsize(yol)

WORKER_KAPALI = {"evet": False}   # True iken Worker'a giden istekler ağ hatasıyla düşer
def aktar(route, request):
    """Notlar isteklerini taklit sunucuya aktarır (CORS'u Worker'ın kendisi yapar)"""
    u = urllib.parse.urlparse(request.url)
    if u.netloc == "kaynak.test":
        if WORKER_KAPALI["evet"]:
            return route.abort()
        hedef = KT + "/worker" + u.path + (("?" + u.query) if u.query else "")
        cevap = route.fetch(url=hedef)
        return route.fulfill(response=cevap)
    if request.method == "OPTIONS":
        return route.fulfill(status=204, headers={"access-control-allow-origin": "*", "access-control-allow-methods": "GET,POST,PATCH,DELETE,OPTIONS",
                                                  "access-control-allow-headers": request.headers.get("access-control-request-headers", "*")}, body="")
    cevap = route.fetch(url=KT + u.path + (("?" + u.query) if u.query else ""))
    return route.fulfill(response=cevap, headers={**cevap.headers, "access-control-allow-origin": "*"})

def kaynak_yollari(c):
    c.route("**/rest/v1/kaynak_**", aktar)
    c.route("**/rest/v1/rpc/kaynak_**", aktar)
    c.route("https://kaynak.test/**", aktar)

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

def notlara_git(s):
    s.click(".alt-cubuk button:has-text('Notlar')")
    s.wait_for_selector("#sayfaKaynak .kaynak-fab-ana")

def fab(s, secenek=None):
    """Sağ alttaki +; secenek verilirse açılan menüden o seçilir"""
    s.click("#sayfaKaynak .kaynak-fab-ana")
    if secenek:
        s.click("#sayfaKaynak .kaynak-fab-secenek:has-text('%s')" % secenek)

def tasnif_ac(s, ad, ust_mu=False):
    if ust_mu: fab(s, "Alt tasnif")
    else: fab(s)
    yaz_ve_onayla(s, ad, "Oluştur")
    s.wait_for_selector("#sayfaKaynak .kaynak-tasnif:has-text('%s')" % ad)

def kuyruk(s):
    return s.evaluate("() => KAYNAK_KUYRUK.length")

def kuyruk_bossa(s, sure=30):
    return bekle_ki(s, lambda: s.evaluate("() => KAYNAK_KUYRUK.length === 0 && !kaynakGonderim"), sure)

def resim_bekle(s, n, sure=40):
    return bekle_ki(s, lambda: s.locator("#sayfaKaynak .kaynak-resim-kart img[src^='blob:']").count() == n and s.locator("#sayfaKaynak .kaynak-is").count() == 0, sure)

def resim_ekle(s, dosyalar):
    s.set_input_files("#sayfaKaynak input[type=file]", dosyalar)

def editor_ac_yeni(s):
    fab(s, "Not")
    s.wait_for_selector(".not-editor .ne-metin")

def editor_kapat(s):
    s.click(".not-editor .ne-ust-dugme.tamam")
    s.wait_for_selector(".not-editor", state="detached")
    s.wait_for_timeout(200)

def editor_html(s):
    return s.evaluate("() => document.querySelector('.not-editor .ne-metin').innerHTML")

def tek(q):
    r = sql(q)
    return r[0] if r else None

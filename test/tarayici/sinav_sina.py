"""Menü › Takvim › Sınavlar: içerikten (agac.json › sinavlar) gelen sınavlar.
Yakından uzağa sıralama, aynı günün sınavlarının tek kutuda olması, LMS
cümlesi, günü geçen sınavın gizlenmesi, saati geçenin sönük durması,
hususi dersin sınavının yetkisiz hesaba gelmemesi, bağlantısız açılış."""
exec(open("vt_taban.py", encoding="utf-8").read())
import datetime as dt, copy

TR = dt.timezone(dt.timedelta(hours=3))
simdi = dt.datetime.now(TR)
def z(gun, saat, dk=0):
    t = (simdi + dt.timedelta(days=gun)).replace(hour=saat, minute=dk, second=0, microsecond=0)
    return t.strftime("%Y-%m-%dT%H:%M+03:00")

# Gerçek aktarıcının yüklediği sınavlar (icerik/agac.json)
genel = next(r for r in YUK["agac"] if r["id"] == 1)
gercek = genel["veri"].get("sinavlar", [])
kontrol("aktarıcı sınavları genel ağaca yazdı (2 sınav, zamana göre)",
        [(x["ders"], x["zaman"]) for x in gercek] == [("veritabani", "2026-11-06T20:30+03:00"), ("aglar", "2026-11-06T21:30+03:00")], gercek)
kontrol("hususi ağaçta sınav alanı yok (42 sınavı yok)", "sinavlar" not in next(r for r in YUK["agac"] if r["id"] == 2)["veri"])

# Deneme verisi: bugüne göre kurulur; sıra karışık verilir (uygulama sıralamalı)
saat_gecen = max(0, simdi.hour - 1)
deneme = [
    {"ders": "ekoloji", "ad": "Vize", "zaman": z(9, 10), "yer": "B-201"},
    {"ders": "veritabani", "ad": "1. Kısa Sınav", "zaman": z(2, 20, 30), "lms": True},
    {"ders": "algoritma", "ad": "Dünkü sınav", "zaman": z(-1, 23, 0), "lms": True},
    {"ders": "aglar", "ad": "1. Kısa Sınav", "zaman": z(2, 21, 30), "lms": True},
    {"ders": "donanim", "ad": "Ödev teslimi", "zaman": z(2, 9, 0), "not": "Ödev kâğıt üzerinde getirilecek."},
    {"ders": "elektrik", "ad": "Saati geçen", "zaman": z(0, saat_gecen, 0)},
]
genel["veri"] = dict(genel["veri"], sinavlar=deneme)
hususi = next(r for r in YUK["agac"] if r["id"] == 2)
hususi["veri"] = dict(hususi["veri"], sinavlar=[{"ders": "born2beroot", "ad": "Savunma", "zaman": z(3, 14), "lms": False}])
for r in YUK["agac"]: r["ozet"] = "deneme-" + str(r["id"])

def gunler(s):
    return s.evaluate("""() => [...document.querySelectorAll('.sinav-kart .sinav-gun')].map(g => ({
        gun: g.dataset.gun, tarih: g.querySelector('.tarih').textContent, kalan: g.querySelector('.kalan').textContent,
        kutu: g.querySelectorAll('.sinav-kutu').length,
        satir: [...g.querySelectorAll('.sinav-satir')].map(x => ({ saat: x.querySelector('.saat').textContent,
            ders: x.querySelector('.ders').textContent, ad: x.querySelector('.ad').textContent,
            lms: !!x.querySelector('p.lms'), metin: x.innerText, gecti: x.classList.contains('gecti') })) }))""")

with sync_playwright() as p:
    c, s = cihaz_ac(p, "S")
    s.goto(KOK); s.wait_for_selector(".giris-perde"); kod_iste_ve_gir(s)
    s.wait_for_selector(".sozlesme"); s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')"); s.wait_for_selector(".grup-baslik")
    bekle_ki(s, lambda: s.evaluate("() => !!(AGAC && AGAC.sinavlar)"))
    s.evaluate("() => localStorage.setItem('pg.cekmeceEkrani', JSON.stringify('takvim'))")
    s.click("#hesapDugme"); s.wait_for_selector(".sinav-kart")
    kontrol("Sınavlar, Takvim ekranında iki takvimin altında",
            s.evaluate("() => { const ic = document.querySelector('.hesap-ic'); const k = [...ic.children]; return k.indexOf(ic.querySelector('.sinav-kart')) === k.length - 1 && k.length >= 3; }"))
    g = gunler(s)
    bugun = simdi.strftime("%Y-%m-%d")
    kontrol("günü geçen sınav gösterilmez", all("Dünkü" not in x["ad"] for d in g for x in d["satir"]), g)
    kontrol("hususi dersin sınavı yetkisiz hesaba gelmez", all(x["ders"] != "Born2beRoot" for d in g for x in d["satir"]))
    kontrol("günler yakından uzağa (bugün, 2 gün sonra, 9 gün sonra)", [d["kalan"] for d in g] == ["Bugün", "2 gün sonra", "9 gün sonra"], [d["kalan"] for d in g])
    iki = g[1]
    kontrol("aynı gündeki üç sınav tek kutuda", iki["kutu"] == 1 and len(iki["satir"]) == 3, iki)
    kontrol("gün içinde saate göre sıralı (09:00, 20:30, 21:30)", [x["saat"] for x in iki["satir"]] == ["09:00", "20:30", "21:30"], [x["saat"] for x in iki["satir"]])
    vt_ = iki["satir"][1]
    kontrol("ders adı tam, sınav adı ayrı", vt_["ders"] == "Veritabanı Yönetimi" and vt_["ad"] == "1. Kısa Sınav", vt_)
    kontrol("LMS sınavında cümle yazar", vt_["lms"] and "Sınav LMS üzerinden çevrimiçi olacak." in vt_["metin"])
    kontrol("LMS olmayan sınavda cümle yok, not yazar", not iki["satir"][0]["lms"] and "Ödev kâğıt üzerinde getirilecek." in iki["satir"][0]["metin"])
    kontrol("yer yazar", "Yer: B-201" in g[2]["satir"][0]["metin"])
    tr_gun = s.evaluate("(z) => new Date(z).toLocaleDateString('tr-TR', { timeZone: 'Europe/Istanbul', day: 'numeric', month: 'long', year: 'numeric', weekday: 'long' })", z(2, 20, 30))
    kontrol("tarih Türkçe ve gün adıyla", iki["tarih"] == tr_gun and any(a in tr_gun for a in ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]), iki["tarih"])
    bg = g[0]["satir"][0]
    kontrol("bugün saati geçen sınav sönük ve 'saati geçti' yazar", bg["gecti"] and "saati geçti" in bg["ad"], bg)
    kontrol("bugün ve yarın vurgulu", s.evaluate("() => document.querySelector('.sinav-gun .kalan').classList.contains('yakin')"))
    # tarayıcının saat dilimi farklı olsa da Türkiye saati
    s.screenshot(path="sinav-takvim.png", full_page=False)
    s.locator(".sinav-kart").screenshot(path="sinav-kart.png")
    s.keyboard.press("Escape"); s.wait_for_timeout(400)

    # Sunucu yanıt vermeden açılış: sınavlar cihazdaki ağaçtan (IndexedDB)
    s.route("**/rest/v1/**", lambda route, req: route.abort())
    s.reload(); s.wait_for_selector(".grup-baslik")
    s.click("#hesapDugme"); s.wait_for_selector(".sinav-kart")
    kontrol("sunucuya ulaşılamadan açılınca da sınavlar görünür", len(gunler(s)) == 3)
    s.unroute("**/rest/v1/**")
    s.keyboard.press("Escape"); s.wait_for_timeout(400)
    kontrol("hata yok", not [h for h in hatalar if "ERR_INTERNET_DISCONNECTED" not in h and "Failed to fetch" not in h and "ERR_FAILED" not in h], hatalar[:4])
    c.close()

    # Başka saat diliminde tarayıcı: saat ve gün Türkiye'ye göre
    b = p.chromium.launch()
    c2 = b.new_context(service_workers="block", viewport={"width": 390, "height": 820}, timezone_id="America/New_York")
    c2.add_init_script("try { localStorage.setItem('pg.kurulum', JSON.stringify('gizli')); localStorage.setItem('pg.notSurumu', JSON.stringify('2.2')) } catch (e) {}")
    c2.route(SUPA + "/**", isle)
    s2 = c2.new_page()
    D["oturumlar"].clear(); D["yerler"].clear(); time.sleep(SUNUCU_KOD_ARALIGI)
    s2.goto(KOK); s2.wait_for_selector(".giris-perde"); kod_iste_ve_gir(s2); s2.wait_for_selector(".grup-baslik")
    bekle_ki(s2, lambda: s2.evaluate("() => !!(AGAC && AGAC.sinavlar)"))
    s2.evaluate("() => localStorage.setItem('pg.cekmeceEkrani', JSON.stringify('takvim'))")
    s2.click("#hesapDugme"); s2.wait_for_selector(".sinav-kart")
    g2 = gunler(s2)
    kontrol("New York saatindeki tarayıcıda da saatler Türkiye saati (20:30)", [x["saat"] for x in g2[1]["satir"]] == ["09:00", "20:30", "21:30"], g2)
    b.close()

gecen = sum(1 for _, k in sonuclar if k)
print("\n%d/%d geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) else 1)

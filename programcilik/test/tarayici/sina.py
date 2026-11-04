"""Programcılık — iki cihazlı tarayıcı testi.
Supabase istekleri Playwright içinde taklit edilir. Oturumlar, tek cihaz kuralı
ve RLS, 01-sema.sql'deki mantıkla aynı biçimde taklit edilir."""
import json, base64, time, sys, re, urllib.parse, datetime, uuid, shutil
from playwright.sync_api import sync_playwright

VERI = json.load(open("veri.json"))
SVG = open("akis-1.svg", "rb").read()
KOK = "http://127.0.0.1:8765/"
SUPA = "https://test.supabase.co"
UID = "11111111-1111-1111-1111-111111111111"
EPOSTA = "ogr@kocaelisaglik.edu.tr"
SUNUCU_KOD_ARALIGI = 5          # taklit Supabase: aynı adrese en çok 5 sn'de bir e-posta

D = {
    "profil": None, "kayitlar": {}, "gunluk": [], "otp": [], "son_otp": 0.0,
    "oturumlar": {},            # oturum id → {"olusma": zaman, "yenileme": belirteç}
    "yerler": {},               # yer tutan oturum id → son görülme
    "azami": 1, "sayac": 0, "devralma": None, "gecmis": [],
    "hususi": True,             # test hesabının hususi yetkisi
}
sonuclar = []
hatalar = []

def cekmece(s, ekran):
    """Çekmeceyi (menü) açar ve verilen ekrana geçer: hedef, istatistik, takvim, hesap"""
    if not s.locator(".hesap-sayfa.acik").count():
        s.click("#hesapDugme"); s.wait_for_selector(".hesap-sayfa.acik")
    s.click(".cekmece-sekme[data-ekran=%s]" % ekran)
    s.wait_for_selector(".hesap-ic[data-ekran=%s]" % ekran)

def onayla(s):
    """Uygulamanın kendi soru penceresinde 'evet'"""
    s.wait_for_selector(".uyari-perde"); s.click(".uyari-perde .evet")

def hazir_kayit(tur, anahtar, deger):
    """Sunucuda önceden duran kayıt (başka cihazdan ya da önceki oturumdan)"""
    z = "2026-01-01T00:00:00+00:00"
    D["kayitlar"][(tur, anahtar)] = {"tur": tur, "anahtar": anahtar, "deger": deger, "silindi": False, "guncellendi": z, "sunucuda": z}
# Test hesaplarının çalışma hedefi önceden konmuştur; açılıştaki hedef sorusu hedef_sina.py'de denenir
hazir_kayit("ayar", "hedef", {"gecmis": [{"g": "2026-01-01", "gun": 3600, "hafta": 25200}]})

def kontrol(ad, kosul, ek=""):
    sonuclar.append((ad, bool(kosul)))
    print(("GEÇTİ " if kosul else "KALDI ") + ad + (("  — " + str(ek)) if ek and not kosul else ""), flush=True)

def b64(d):
    return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()

def oturum_ac():
    sid = str(uuid.uuid4())
    yen = "yen-" + sid
    D["oturumlar"][sid] = {"olusma": time.time(), "yenileme": yen}
    simdi = int(time.time())
    jwt = b64({"alg": "HS256", "typ": "JWT"}) + "." + b64({"sub": UID, "email": EPOSTA, "role": "authenticated",
          "aud": "authenticated", "session_id": sid, "exp": simdi + 3600, "iat": simdi}) + ".imza"
    return {"access_token": jwt, "token_type": "bearer", "expires_in": 3600, "expires_at": simdi + 3600,
            "refresh_token": yen, "user": kullanici()}

def kullanici():
    return {"id": UID, "aud": "authenticated", "role": "authenticated", "email": EPOSTA,
            "email_confirmed_at": "2026-10-05T10:00:00Z", "app_metadata": {"provider": "email"},
            "user_metadata": {}, "created_at": "2026-10-05T10:00:00Z"}

def istek_oturumu(request):
    b = request.headers.get("authorization", "")
    if not b.startswith("Bearer "): return None
    parca = b[7:].split(".")
    if len(parca) != 3: return None
    try:
        y = json.loads(base64.urlsafe_b64decode(parca[1] + "=" * (-len(parca[1]) % 4)))
    except Exception:
        return None
    return y.get("session_id")

def zaman(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()

def simdi_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

# --- 01-sema.sql "Cihaz sınırı" taklidi ---
def temizle():
    for x in [x for x in D["yerler"] if x not in D["oturumlar"]]: D["yerler"].pop(x)
    fazla = sorted(D["yerler"], key=lambda x: D["yerler"][x], reverse=True)[D["azami"]:]
    for x in fazla: D["yerler"].pop(x)

def cihaz_durumu(sid):
    if not sid or sid not in D["oturumlar"]: return "yetkisiz"
    if sid in D["yerler"]: return "bu"
    dolu = len([x for x in D["yerler"] if x in D["oturumlar"]])
    return "bos" if dolu < D["azami"] else "baska"

def uye(sid):
    p = D["profil"]
    return bool(p and p["sozlesme_surumu"] == "2" and sid and sid in D["yerler"] and sid in D["oturumlar"])

def isle(route, request):
    url = urllib.parse.urlparse(request.url)
    yol, q = url.path, urllib.parse.parse_qs(url.query)
    yontem = request.method
    baslik = {"access-control-allow-origin": "*", "access-control-allow-methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
              "access-control-allow-headers": request.headers.get("access-control-request-headers", "*"),
              "access-control-expose-headers": "content-range", "content-type": "application/json"}
    def cevap(govde, kod=200):
        route.fulfill(status=kod, headers=baslik, body=json.dumps(govde) if govde is not None else "")
    if yontem == "OPTIONS":
        return route.fulfill(status=204, headers=baslik, body="")
    sid = istek_oturumu(request)
    D["gunluk"].append(yontem + " " + yol + ("?" + url.query if url.query else ""))
    govde = request.post_data
    tek = "vnd.pgrst.object" in (request.headers.get("accept") or "")

    # ---- Auth ----
    if yol == "/auth/v1/otp":
        e = json.loads(govde)["email"]
        if not e.endswith("@kocaelisaglik.edu.tr"):
            return cevap({"code": 403, "error_code": "hook_error", "msg": "Yalnızca @kocaelisaglik.edu.tr uzantılı okul adresiyle giriş yapılabilir."}, 403)
        gecen = time.time() - D["son_otp"]
        if gecen < SUNUCU_KOD_ARALIGI:
            kalan = int(SUNUCU_KOD_ARALIGI - gecen) + 1
            return cevap({"code": 429, "error_code": "over_email_send_rate_limit",
                          "msg": "For security purposes, you can only request this after %d seconds." % kalan}, 429)
        D["son_otp"] = time.time()
        D["otp"].append(e)
        return cevap({})
    if yol == "/auth/v1/verify":
        d = json.loads(govde)
        if d.get("token") != "123456":
            return cevap({"code": 403, "error_code": "otp_expired", "msg": "Token has expired or is invalid"}, 403)
        return cevap(oturum_ac())
    if yol == "/auth/v1/token":
        d = json.loads(govde or "{}")
        for s_id, o in D["oturumlar"].items():
            if o["yenileme"] == d.get("refresh_token"):
                return cevap(oturum_ac())
        return cevap({"code": 400, "error_code": "refresh_token_not_found", "msg": "Invalid Refresh Token: Refresh Token Not Found"}, 400)
    if yol == "/auth/v1/user":
        if not sid or sid not in D["oturumlar"]:
            return cevap({"code": 403, "error_code": "session_not_found", "msg": "Session from session_id claim in JWT does not exist"}, 403)
        return cevap(kullanici())
    if yol == "/auth/v1/logout":
        kapsam = q.get("scope", ["global"])[0]
        if kapsam == "local":
            D["oturumlar"].pop(sid, None)
        elif kapsam == "others":
            for s_id in [x for x in D["oturumlar"] if x != sid]: D["oturumlar"].pop(s_id)
        else:
            D["oturumlar"].clear()
        return route.fulfill(status=204, headers=baslik, body="")

    # ---- Tek cihaz işlevleri ----
    if yol == "/rest/v1/rpc/cihaz_yokla":
        if cihaz_durumu(sid) == "yetkisiz": return cevap({"durum": "yetkisiz"})
        temizle()
        durum = cihaz_durumu(sid)
        if durum == "bu": D["yerler"][sid] = time.time()
        return cevap({"durum": durum, "azami": D["azami"]})
    if yol == "/rest/v1/rpc/devralma_iste":
        if cihaz_durumu(sid) == "baska":
            if D["oturumlar"][sid]["olusma"] < time.time() - 1800:
                return cevap({"code": "P0001", "message": "Devralma için yeniden giriş gerekli"}, 400)
            D["devralma"] = time.time()
        return route.fulfill(status=204, headers=baslik, body="")
    if yol == "/rest/v1/rpc/cihazi_birak":
        D["gunluk"].append("BIRAK " + str(sid))
        D["yerler"].pop(sid, None)
        return route.fulfill(status=204, headers=baslik, body="")
    if yol == "/rest/v1/rpc/cihazi_sahiplen":
        if cihaz_durumu(sid) == "yetkisiz": return cevap({"code": "P0001", "message": "Yetkisiz"}, 400)
        temizle()
        durum = cihaz_durumu(sid)
        if durum == "bu": return cevap("bu")
        cikan, yol_ = None, "serbest"
        if durum == "baska":
            istek = D["devralma"]
            acilis = D["oturumlar"].get(sid, {}).get("olusma")
            if istek is None or istek < time.time() - 1800 or acilis is None or acilis <= istek:
                return cevap({"code": "P0001", "message": "Bu hesap başka bir cihazda açık"}, 400)
            cikan = min(D["yerler"], key=lambda x: D["yerler"][x])
            D["yerler"].pop(cikan); yol_ = "devralma"
        D["yerler"][sid] = time.time()
        D["sayac"] += 1; D["devralma"] = None
        D["gecmis"].append((yol_, sid, cikan))
        return cevap("bu")

    # ---- Tablolar ----
    if yol == "/rest/v1/programlar":
        return cevap([{"id": "bilgisayar-programciligi", "ad": "Bilgisayar Programcılığı", "sinif_sayisi": 2, "sira": 1}])
    if yol == "/rest/v1/profiller":
        if yontem == "GET":
            p = D["profil"]
            return cevap(p if tek else ([p] if p else []))
        d = json.loads(govde); d = d[0] if isinstance(d, list) else d
        if d["sozlesme_surumu"] != "2":
            return cevap({"message": "Sözleşmenin geçerli sürümü onaylanmalı"}, 400)
        D["profil"] = {"program": d["program"], "sinif": d["sinif"], "sozlesme_surumu": d["sozlesme_surumu"]}
        return cevap(D["profil"] if tek else [D["profil"]], 201)
    if yol == "/rest/v1/agac":
        # 01-sema.sql: satır 1 genel gruplar, satır 2 hususi gruplar (yalnızca yetkiliye)
        if not uye(sid): return cevap([])
        genel = {"gruplar": [g for g in VERI["agac"]["gruplar"] if g["id"] != "42"]}
        hususi = {"gruplar": [dict(g, hususi=True) for g in VERI["agac"]["gruplar"] if g["id"] == "42"]}
        satirlar = [{"id": 1, "veri": genel, "ozet": "agac-1"}]
        if D["hususi"]: satirlar.append({"id": 2, "veri": hususi, "ozet": "agac-2"})
        return cevap(satirlar)
    if yol == "/rest/v1/konular":
        if not uye(sid): return cevap([])
        gorunen = [k for k in VERI["konular"] if D["hususi"] or k["ders"] != "born2beroot"]
        if q.get("select", [""])[0] == "id,ozet":
            return cevap([{"id": k["id"], "ozet": k["ozet"]} for k in gorunen])
        m = re.match(r"in\.\((.*)\)$", q.get("id", [""])[0])
        istenen = set(x.strip('"') for x in m.group(1).split(",")) if m else set()
        return cevap([k for k in gorunen if k["id"] in istenen])
    if yol == "/rest/v1/kayitlar":
        if yontem == "POST":
            if not uye(sid):
                return cevap({"code": "42501", "message": 'new row violates row-level security policy for table "kayitlar"'}, 403)
            kabul = []
            for r in json.loads(govde):
                a = (r["tur"], r["anahtar"])
                r = dict(r)
                # 01-sema.sql kayit_zamani: gelecek zaman sunucu saatine çekilir, eski yazım düşer
                if zaman(r["guncellendi"]) > time.time(): r["guncellendi"] = simdi_iso()
                eski = D["kayitlar"].get(a)
                if eski and zaman(eski["guncellendi"]) > zaman(r["guncellendi"]): continue
                r["sunucuda"] = simdi_iso()
                D["kayitlar"][a] = r
                kabul.append(r)
            istenen = "return=representation" in (request.headers.get("prefer") or "")
            return cevap([{k: r[k] for k in ("tur", "anahtar", "deger", "silindi", "guncellendi")} for r in kabul] if istenen else None, 201)
        if not uye(sid): return cevap([])
        satirlar = list(D["kayitlar"].values())
        if "tur" in q: satirlar = [r for r in satirlar if r["tur"] == q["tur"][0][3:]]
        if "anahtar" in q:
            m = re.match(r"in\.\((.*)\)$", q["anahtar"][0])
            ist = set(x.strip('"') for x in m.group(1).split(",")) if m else set()
            satirlar = [r for r in satirlar if r["anahtar"] in ist]
        if "sunucuda" in q:
            esik = q["sunucuda"][0][3:]
            satirlar = [r for r in satirlar if r["sunucuda"] > esik]
        return cevap(sorted(satirlar, key=lambda r: r["sunucuda"]))
    if yol.startswith("/storage/v1/object/"):
        if not uye(sid): return cevap({"message": "Object not found"}, 400)
        return route.fulfill(status=200, headers={**baslik, "content-type": "image/svg+xml"}, body=SVG)
    print("TAKLİTTE YOK:", yontem, request.url)
    cevap({"message": "yok"}, 404)

def cihaz_ac(p, ad, kalici=False, kurulum_gizli=True):
    secenek = dict(viewport={"width": 390, "height": 820}, device_scale_factor=2)
    if kalici:
        shutil.rmtree("/tmp/claude-0/pw-" + ad, ignore_errors=True)
        c = p.chromium.launch_persistent_context("/tmp/claude-0/pw-" + ad, service_workers="allow", **secenek)
    else:
        b = p.chromium.launch()
        c = b.new_context(service_workers="block", **secenek)
    if kurulum_gizli:
        c.add_init_script("try { localStorage.setItem('pg.kurulum', JSON.stringify('gizli')) } catch (e) {}")
    c.route(SUPA + "/**", isle)
    s = c.pages[0] if c.pages else c.new_page()
    s.on("pageerror", lambda e: hatalar.append(ad + " pageerror: " + str(e)))
    s.on("console", lambda m: hatalar.append(ad + " console." + m.type + ": " + m.text) if m.type == "error" else None)
    return c, s

def ekran(s, ad):
    s.screenshot(path="ekran-" + ad + ".png")

def kod_iste_ve_gir(s):
    s.fill("#girisEposta", EPOSTA)
    s.click("button:has-text('Kod gönder')")
    s.wait_for_selector("#girisKod")
    # sunucu sınırına takılmamak için
    s.fill("#girisKod", "123456")
    s.click("button:has-text('Giriş yap')")

def yerel_kayit_sayisi(s):
    return s.evaluate("""() => new Promise(r => { const i = indexedDB.open('programcilik'); i.onsuccess = () => {
        const db = i.result; if (!db.objectStoreNames.contains('icerik')) { r(0); return; }
        const t = db.transaction(['icerik','kayit'], 'readonly'); let n = 0;
        t.objectStore('icerik').count().onsuccess = e => { n += e.target.result;
          t.objectStore('kayit').count().onsuccess = e2 => r(n + e2.target.result); }; }; })""")

def bekle_ki(s, kosul, sure=10):
    for _ in range(sure * 4):
        if kosul(): return True
        s.wait_for_timeout(250)
    return False

with sync_playwright() as p:
    # =================== A cihazı: ilk giriş ve uygulamanın tamamı ===================
    print("--- A cihazı: ilk giriş", flush=True)
    cA, a = cihaz_ac(p, "A", kalici=True)
    a.goto(KOK)
    a.wait_for_selector(".giris-perde")
    kontrol("giriş ekranı açıldı", a.locator(".giris-baslik").count() == 1)
    ekran(a, "01-giris")
    a.fill("#girisEposta", "ali@gmail.com")
    a.click("button:has-text('Kod gönder')")
    a.wait_for_selector(".giris-hata")
    kontrol("gmail istemcide reddedildi", "kocaelisaglik.edu.tr" in a.inner_text(".giris-hata") and not D["otp"])
    a.fill("#girisEposta", "Ogr@KocaeliSaglik.edu.tr")
    a.click("button:has-text('Kod gönder')")
    a.wait_for_selector("#girisKod")
    kontrol("kod istendi (küçük harfe çevrilmiş)", D["otp"] == [EPOSTA], D["otp"])
    a.fill("#girisKod", "999999")
    a.click("button:has-text('Giriş yap')")
    a.wait_for_selector(".giris-hata")
    kontrol("yanlış kod mesajı", "hatalı" in a.inner_text(".giris-hata"), a.inner_text(".giris-hata"))
    a.fill("#girisKod", "123456")
    a.click("button:has-text('Giriş yap')")
    a.wait_for_selector(".sozlesme")
    kontrol("ilk cihaz devralma sorulmadan yer aldı, sayaç 1", len(D["yerler"]) == 1 and D["sayac"] == 1)
    kontrol("sözleşme 7 madde, cihaz kaydı açıklanmış", a.locator(".sozlesme-maddeleri li").count() == 7 and a.locator("text=cihaz değişikliklerinin sayısı").count() == 1)
    kontrol("tek program varken bölüm sorulmadı", a.locator(".giris-etiket").count() == 0)
    kontrol("onaysız devam kapalı", a.locator("button:has-text('Kabul et ve devam et')").is_disabled())
    a.click("text=Okudum, kabul ediyorum")
    a.click("button:has-text('Kabul et ve devam et')")
    a.wait_for_selector(".not-perde")
    kontrol("profil 1. sınıf BP", D["profil"] == {"program": "bilgisayar-programciligi", "sinif": 1, "sozlesme_surumu": "2"}, D["profil"])
    a.click("button:has-text('Anladım')")
    a.wait_for_selector(".grup-baslik")
    bekle_ki(a, lambda: a.locator(".ders-satiri:has-text('Born2beRoot') .durum").inner_text() != "yakında")
    kontrol("Oku kökünde gruplar", a.locator(".grup-baslik").evaluate_all("els => els.map(e => e.firstChild.textContent)") == ["1. Sınıf", "42"])
    ekran(a, "02-oku-kok")

    a.click(".ders-satiri:has-text('Born2beRoot')")
    a.wait_for_selector(".agac .dal")
    kontrol("Born2beRoot 17 konu", a.locator(".agac .dal").count() == 17)
    a.click(".agac .dal:has-text('Disk Partisyonlama')")
    a.wait_for_selector(".okuma h2")
    a.click("text=Okudum olarak işaretle")
    kontrol("okundu sunucuya gitti", bekle_ki(a, lambda: ("okundu", "b2r-disk") in D["kayitlar"]))
    a.evaluate("""() => { const t = document.querySelector('.okuma p').firstChild;
      const r = document.createRange(); r.setStart(t, 0); r.setEnd(t, 20);
      const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r); }""")
    a.wait_for_selector(".secim-cubugu .boya-dugmesi")
    a.click(".secim-cubugu .boya-dugmesi")
    a.wait_for_selector(".okuma .boyali")
    boyali = a.inner_text(".okuma .boyali")
    kontrol("boya sunucuda", bekle_ki(a, lambda: (D["kayitlar"].get(("boya", "b2r-disk")) or {}).get("deger", [{}])[0].get("alinti") == boyali))

    a.click("text=‹ Geri"); a.click("text=‹ Dersler")
    a.click(".ders-satiri:has-text('Algoritma')")
    a.click(".agac .dal >> nth=0")
    a.wait_for_selector(".okuma table")
    kontrol("tablo, liste, kod çizildi", a.locator(".okuma table").count() == 1 and a.locator(".okuma ul li").count() == 2 and a.locator(".okuma pre").count() == 1)
    a.wait_for_function("() => { const i = document.querySelector('.okuma figure img'); return i && i.src.startsWith('blob:') }", timeout=5000)
    kontrol("görsel indirildi", True)

    a.click(".alt-cubuk button:has-text('Ara')")
    a.fill("#sayfaAra input[type=search]", "lvm")
    a.wait_for_timeout(300)
    kontrol("arama sonuç veriyor", a.locator("#sayfaAra .sonuc-kart").count() > 0)

    a.click(".alt-cubuk button:has-text('Temrin')")
    a.click("button:has-text('Ders ve konu seç')")
    a.wait_for_selector(".kontrol-oge")
    a.click(".kontrol-oge:has-text('Algoritma') .kutucuk")
    a.click("button:has-text('Tamam')")
    a.wait_for_selector(".mod-kart")
    modlar = a.locator(".mod-kart .ad").all_inner_texts()
    kontrol("bütün soru türleri listelendi", all(m in modlar for m in ["Çoktan seçmeli", "Doğru mu, yanlış mı", "Boşluk doldurma", "Sıralama", "Eşleştirme", "İzleme", "Hesaplama", "Klasik", "Kavram kartları"]), modlar)
    mod = lambda ad: ".mod-kart:has(.ad:text-is('%s'))" % ad
    sonuc_ve_don = lambda: (a.click("button:has-text('Sonucu gör')"), a.click(".eylem button:has-text('Temrin yolları')"))
    a.click(mod("Doğru mu, yanlış mı")); a.click(".dy-dugmeler button:has-text('Doğru')")
    kontrol("yanlış cevap deftere yazıldı", bekle_ki(a, lambda: ("yanlis", "alg-kavram.s2") in D["kayitlar"]))
    sonuc_ve_don()
    a.click(mod("Boşluk doldurma")); a.fill(".bosluk-girdi", "SONLU."); a.click("button:has-text('Kontrol et')")
    kontrol("boşluk: büyük harf/nokta kabul", a.locator(".bosluk-girdi.dogru").count() == 1)
    sonuc_ve_don()
    a.click(mod("Hesaplama")); a.fill(".hesap-satir input", "1.000"); a.press(".hesap-satir input", "Enter")
    kontrol("hesap: binlik ayırıcı sorulur", "Binlik" in a.inner_text(".kart-ipucu.uyari"))
    a.fill(".hesap-satir input", "4,0"); a.press(".hesap-satir input", "Enter"); a.wait_for_timeout(300)
    kontrol("hesap: Enter ile 4,0 doğru, sonuç ekranda kalır (soru atlanmaz)", a.locator(".hesap-satir input.dogru").count() == 1 and a.locator("button:has-text('Sonucu gör')").count() == 1)
    sonuc_ve_don()
    a.click(mod("Klasik")); a.fill(".klasik-girdi", "Sonluluk")
    a.click(".alt-cubuk button:has-text('Kıraat')"); a.click(".alt-cubuk button:has-text('Temrin')")
    kontrol("sekme değişince yarım temrin silinmedi", a.locator(".klasik-girdi").count() == 1 and a.input_value(".klasik-girdi") == "Sonluluk")
    a.click("button:has-text('Örnek cevabı göster')")
    a.click(".oz-puan button:has-text('Bildim')")
    kontrol("klasik puanlandı", a.locator("button:has-text('Sonucu gör')").count() == 1)
    sonuc_ve_don()

    a.click(".alt-cubuk button:has-text('42 Tarzı')")
    a.evaluate("() => { depo.yaz('pg.kartKapsam', Object.fromEntries(Array.from(DERS_KONULARI.keys()).map(d => [d, 'tumu']))); kartSayfasiCiz(); }")   # 42 Tarzı'nda bütün dersler seçilir
    a.click("text=/kartla çalış/")
    a.wait_for_selector(".deste .kart-yeri:not(.sonraki)")
    k = a.locator(".deste .kart-yeri:not(.sonraki)").bounding_box()
    cx, cy = k["x"] + k["width"] / 2, k["y"] + k["height"] / 2
    kontrol("ön yüzde cevap alanı var, karşılaştırma kutusu gizli", a.locator(".kart-cevap textarea:visible").count() == 1 and a.locator(".senin-cevabin:visible").count() == 0)
    a.fill(".kart-cevap textarea", "Kendi cevabım\nikinci satır")
    ekran(a, "13-kart-cevap-yaziliyor")
    a.press(".kart-cevap textarea", "Control+Enter"); a.wait_for_timeout(650)
    kontrol("Ctrl+Enter kartı çevirdi; yazılan cevap 'Sizin cevabınız' kutusunda", a.locator(".kart-ic.cevrik").count() == 1 and a.locator(".kart-cevap textarea:visible").count() == 0 and "Kendi cevabım" in a.inner_text(".senin-cevabin") and "Sizin cevabınız" in a.inner_text(".senin-cevabin"))
    ekran(a, "14-kart-cevrik-karsilastir")
    a.mouse.click(cx, cy); a.wait_for_timeout(650)
    kontrol("geri çevirince cevap yeniden düzenlenebilir", a.locator(".kart-ic.cevrik").count() == 0 and a.input_value(".kart-cevap textarea") == "Kendi cevabım\nikinci satır")
    a.mouse.click(cx, cy); a.wait_for_timeout(650)
    kontrol("kart döndü", a.locator(".kart-ic.cevrik").count() == 1)
    a.mouse.move(cx, cy); a.mouse.down()
    for i in range(1, 6): a.mouse.move(cx + i * 24, cy + 2)
    a.wait_for_timeout(100)
    kontrol("sürüklerken eşik geçilince Bildim yığını parlıyor, damga görünüyor", a.locator(".yigin.bildim.yakin").count() == 1 and float(a.evaluate("() => getComputedStyle(document.querySelector('.kart-yeri:not(.sonraki) .damga.bildim')).opacity")) > 0.9)
    ekran(a, "15-kart-surukleniyor")
    for i in range(6, 9): a.mouse.move(cx + i * 22, cy + 2)
    a.mouse.up(); a.wait_for_timeout(230); ekran(a, "16-kart-yigina-ucuyor"); a.wait_for_timeout(570)
    kontrol("kaydırınca sonraki kart", a.inner_text(".ilerleme .sayac").startswith("2/"))
    kontrol("kart Bildim yığınına düştü (1), cevap alanı boşaldı", a.inner_text(".yigin.bildim .sayi") == "1" and a.inner_text(".yigin.bilemedim .sayi") == "0" and a.input_value(".kart-cevap textarea") == "")
    a.click(".deste-eylem button:has-text('Cevabı göster')"); a.wait_for_timeout(650)
    a.mouse.move(cx, cy); a.mouse.down()
    for i in range(1, 4): a.mouse.move(cx - i * 10, cy, steps=4); a.wait_for_timeout(60)
    a.mouse.up(); a.wait_for_timeout(700)
    kontrol("eşiğe varmadan bırakılan kart yaylanarak yerine döndü", a.inner_text(".ilerleme .sayac").startswith("2/") and a.evaluate("() => document.querySelector('.kart-yeri:not(.sonraki)').style.transform") == "")
    a.click(".deste-eylem button:has-text('Bilemedim')"); a.wait_for_timeout(800)
    kontrol("düğmeyle Bilemedim: kart sol yığına düştü", a.inner_text(".ilerleme .sayac").startswith("3/") and a.inner_text(".yigin.bilemedim .sayi") == "1")
    kontrol("iki kart sonucu da hesapta", bekle_ki(a, lambda: len([x for x in D["kayitlar"] if x[0] == "kart"]) == 2))
    kart_sayisi = len([x for x in D["kayitlar"] if x[0] == "kart"])
    a.click(".alt-cubuk button:has-text('Kıraat')")
    a.keyboard.press(" "); a.wait_for_timeout(700); a.keyboard.press("ArrowLeft"); a.wait_for_timeout(2600)
    kontrol("gizli destedeki kart klavyeyle çevrilip işaretlenmedi", len([x for x in D["kayitlar"] if x[0] == "kart"]) == kart_sayisi and a.locator(".kart-ic.cevrik").count() == 0)
    a.click(".alt-cubuk button:has-text('42 Tarzı')")
    kontrol("42 Tarzı'na dönünce deste yerinde", a.inner_text(".ilerleme .sayac").startswith("3/"))
    # Başka bir cihaz bu arada daha yeni bir değer yazmış: A'nın yazımı düşer, A sunucudakini alır
    gelecek = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)).isoformat()
    D["kayitlar"][("yildiz", "deneme")] = {"tur": "yildiz", "anahtar": "deneme", "deger": {"metin": "Sunucu"}, "silindi": False, "guncellendi": gelecek, "sunucuda": simdi_iso(), "kullanici": UID}
    a.evaluate("() => { kayitYaz('yildiz', 'deneme', { metin: 'A' }); return esitle(); }")
    kontrol("sunucunun kabul etmediği yazımda cihaz sunucudakine uydu", bekle_ki(a, lambda: a.evaluate("() => (kayit('yildiz','deneme')||{}).metin") == "Sunucu" and a.evaluate("() => gonderilmemisSayisi()") == 0))
    # İleri tarihli yazım sunucuda kırpılır, cihaz da kırpılmış zamanı alır
    a.evaluate("() => { const r = { k: 'yildiz|ileri', tur: 'yildiz', anahtar: 'ileri', deger: { metin: 'x' }, silindi: false, guncellendi: new Date(Date.now() + 3600e3).toISOString(), gonderildi: false }; KAYITLAR.set(r.k, r); return esitle(); }")
    kontrol("ileri saat: cihazdaki zaman sunucununkine çekildi", bekle_ki(a, lambda: a.evaluate("() => zamanMs(KAYITLAR.get('yildiz|ileri').guncellendi) <= Date.now() + 1000")))
    a.click(".alt-cubuk button:has-text('Kıraat')")
    a.click(".alt-cubuk button:has-text('Kıraat')")
    a.wait_for_selector(".grup-baslik")
    a_oturumu = next(iter(D["yerler"]))

    # =================== Mühim yerler ===================
    print("--- A: mühim yerler", flush=True)
    a.click(".alt-cubuk button:has-text('Kıraat')"); a.click(".alt-cubuk button:has-text('Kıraat')")
    a.wait_for_selector(".grup-baslik")
    ekran(a, "09-muhimler-satiri")
    kontrol("Oku kökünde Mühimmat satırı (önceki boyalı Disk konusu: 1 konu · 1 başlık)", "1 konu · 1 başlık" in a.text_content(".muhimler-giris"), a.text_content(".muhimler-giris"))
    a.click(".ders-satiri:has-text('Algoritma')")
    a.click(".agac .dal >> nth=0")
    a.wait_for_selector(".okuma h3 .muhim-dugme")
    kontrol("konu adında ve her başlıkta mühim düğmesi", a.locator(".okuma h2 .muhim-dugme").count() == 1 and a.locator(".okuma h3 .muhim-dugme, .okuma h4 .muhim-dugme").count() == 2)
    a.click(".okuma h3:has-text('Algoritma nedir') .muhim-dugme")
    a.wait_for_selector(".okuma h3.muhim")
    kontrol("elle işaret: başlık şeritli, hesaba gitti", bekle_ki(a, lambda: ("muhim", "alg-kavram#Algoritma nedir") in D["kayitlar"]))
    kontrol("yalnız bir başlık işaretliyken konu adı düğmesi boş", a.get_attribute(".okuma h2 .muhim-dugme", "aria-pressed") == "false")
    a.evaluate("""() => { const h = [...document.querySelectorAll('.okuma h4')].find(x => x.dataset.baslik === 'Özellikleri');
      const w = document.createTreeWalker(h.nextElementSibling, NodeFilter.SHOW_TEXT); const t = w.nextNode();
      const r = document.createRange(); r.setStart(t, 0); r.setEnd(t, Math.min(8, t.length));
      const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r); }""")
    a.wait_for_selector(".secim-cubugu .boya-dugmesi")
    a.click(".secim-cubugu .boya-dugmesi")
    a.wait_for_selector(".okuma h4.muhim")
    kontrol("boyanan yerin başlığı ve konu adı mühim göründü (konunun tamamı düğmesi boş)", a.locator(".okuma h2.muhim").count() == 1 and a.get_attribute(".okuma h2 .muhim-dugme", "aria-pressed") == "false" and a.locator(".okuma .boyali").count() >= 1)
    a.click(".okuma h2 .muhim-dugme")
    a.wait_for_selector(".okuma h2 .muhim-dugme[aria-pressed=true]")
    kontrol("boya varken de konunun tamamı işaretlenebilir; odak düğmede kalır", bekle_ki(a, lambda: ("muhim", "alg-kavram") in D["kayitlar"]) and a.evaluate("() => document.activeElement && document.activeElement.closest('h2') !== null"))
    a.click(".okuma h2 .muhim-dugme")
    a.wait_for_selector(".okuma h2 .muhim-dugme[aria-pressed=false]")
    kontrol("konunun tamamı işareti kaldırılınca boyalı başlık mühim kalır", a.locator(".okuma h2.muhim").count() == 1 and a.locator(".okuma h4.muhim").count() == 1 and bekle_ki(a, lambda: D["kayitlar"].get(("muhim", "alg-kavram"), {}).get("silindi") is True))
    a.click(".okuma h4 .muhim-dugme")
    a.wait_for_timeout(200)
    kontrol("boyadan gelen işaret dokunarak kalkmaz, açıklama çıkar", "boyalı yer var" in a.inner_text(".kisa-bildirim") and a.locator(".okuma h4.muhim").count() == 1 and ("muhim", "alg-kavram#Özellikleri") not in D["kayitlar"], a.inner_text(".kisa-bildirim"))
    kontrol("boya konumu mühim düğmesinden etkilenmedi (yeniden çizimde aynı yer)", a.locator(".okuma .boyali").count() >= 1)
    a.evaluate("() => window.scrollTo(0, 0)"); a.wait_for_timeout(1500); ekran(a, "11-konu-muhim")
    a.click("text=‹ Geri")
    a.wait_for_selector(".agac .dal")
    kontrol("ders sayfasında konu işaretli, altında 2 mühim başlık", a.locator(".agac .dal .rozet .muhim-imi").count() == 1 and a.locator(".agac .dal-alt").all_inner_texts() == ["│  Algoritma nedir", "│    Özellikleri"] or [t.strip() for t in a.locator(".agac .dal-alt .ad").all_inner_texts()] == ["Algoritma nedir", "Özellikleri"], a.locator(".agac .dal-alt").all_inner_texts())
    ekran(a, "12-ders-muhim")
    a.click("text=‹ Dersler")
    a.wait_for_selector(".muhimler-giris")
    kontrol("Oku kökünde özet: 2 konu · 3 başlık", "2 konu · 3 başlık" in a.text_content(".muhimler-giris"), a.text_content(".muhimler-giris"))
    a.click(".muhimler-giris")
    a.wait_for_selector(".muhim-konu")
    ekran(a, "10-muhimler-ekrani")
    kontrol("Mühimmat ekranı: 2 konu, 3 başlık", "Mühimmat" in a.inner_text(".ders-basligi") and a.locator(".muhim-konu").count() == 2 and a.locator(".muhim-baslik").count() == 3)
    a.click(".muhim-baslik:has-text('Özellikleri')")
    a.wait_for_selector(".okuma h4.baslik-hedef")
    kontrol("mühim başlığa dokununca konu o başlıkta açıldı", True)
    a.click("text=‹ Geri")
    a.wait_for_selector(".muhim-konu")
    kontrol("konudan geri Mühimmat ekranına dönüldü", True)
    birim = a.evaluate("""() => { const k = KONULAR.get('b2r-mac'); const h = k.basliklar.filter(b => b.seviye === 3).map(b => b.metin); const r = [];
      r.push(muhimYerdenMi(k, h[0]) === false && muhimYerdenMi(k, null) === false);
      kayitYaz('muhim', 'b2r-mac#' + h[1], true);
      r.push(muhimYerdenMi(k, h[1]) === true && muhimYerdenMi(k, h[0]) === false && muhimYerdenMi(k, null) === true);
      kayitYaz('muhim', 'b2r-mac', true);
      r.push(muhimYerdenMi(k, h[0]) === true);
      kayitSil('muhim', 'b2r-mac'); kayitSil('muhim', 'b2r-mac#' + h[1]);
      r.push(muhimYerdenMi(k, h[1]) === false && konuMuhimDurumu(k).mi === false);
      kayitYaz('muhim', 'b2r-mac#Notta olmayan başlık', true);
      r.push(konuMuhimDurumu(k).mi === false);
      kayitSil('muhim', 'b2r-mac#Notta olmayan başlık');
      const a = KONULAR.get('alg-kavram'); const d = konuMuhimDurumu(a);
      r.push(muhimYerdenMi(a, 'Algoritma nedir') && muhimYerdenMi(a, 'Özellikleri') && d.basliklar.get('Özellikleri').boyali && !d.basliklar.get('Özellikleri').elle);
      return r; }""")
    kontrol("süzgeç kuralları (başlık, üst/alt başlık, konunun tamamı, notta olmayan başlık)", all(birim), birim)
    a.click(".alt-cubuk button:has-text('Temrin')")
    a.click(".alt-cubuk button:has-text('Temrin')")
    a.wait_for_selector("#sayfaCalis .anahtar-dugme")
    a.click("#sayfaCalis .anahtar-dugme")
    a.wait_for_selector("#sayfaCalis .anahtar-dugme[aria-checked=true]")
    prova = a.inner_text(".mod-kart:has(.ad:text-is('Sınav provası')) .sayi")
    kontrol("mühim süzgeci açık: algoritmanın 8 sorusu geliyor (konu mühim)", prova == "8 soru", prova)
    a.evaluate("() => { kayitSil('muhim', 'alg-kavram#Algoritma nedir'); kayitSil('boya', 'alg-kavram'); calisMenusuCiz(); }")
    kontrol("mühim yer kalmayınca açıklama çıkar, soru türü listelenmez", a.locator("#sayfaCalis p.bos:has-text('mühim yerlerinden soru yok')").count() == 1 and a.locator(".mod-kart:has(.ad:text-is('Sınav provası'))").count() == 0)
    a.click("#sayfaCalis .anahtar-dugme")
    a.wait_for_selector(".mod-kart:has(.ad:text-is('Sınav provası'))")
    a.evaluate("() => kayitYaz('muhim', 'b2r-savunma', true)")
    a.click(".alt-cubuk button:has-text('42 Tarzı')")
    a.click(".alt-cubuk button:has-text('42 Tarzı')")
    a.wait_for_selector("#sayfaKart .anahtarli-satir")
    kontrol("42 Tarzı: mühim kart sayısı (savunma konusu işaretli: 20)", "(20)" in a.inner_text("#sayfaKart .anahtarli-satir >> nth=0"), a.inner_text("#sayfaKart .anahtarli-satir >> nth=0"))
    a.click("#sayfaKart .anahtarli-satir >> nth=0 >> .anahtar-dugme")
    a.wait_for_timeout(200)
    kontrol("42 Tarzı: süzgeç açılınca 20 kartla çalışılır", "20 kartla çalış" in a.inner_text("#sayfaKart"))
    a.click("#sayfaKart .anahtarli-satir >> nth=0 >> .anahtar-dugme")
    a.evaluate("() => kayitSil('muhim', 'b2r-savunma')")
    kontrol("mühim kayıtları hesaba gitti ve silindi işaretlendi", bekle_ki(a, lambda: D["kayitlar"].get(("muhim", "b2r-savunma"), {}).get("silindi") is True))
    a.click(".alt-cubuk button:has-text('Kıraat')")
    kontrol("Oku sekmesine dönünce Mühimmat ekranı hatırlandı", a.locator(".muhim-konu").count() >= 1)
    a.click(".alt-cubuk button:has-text('Kıraat')")
    a.wait_for_selector(".grup-baslik")
    a_oturumu = next(iter(D["yerler"]))

    # =================== B cihazı: devralma ===================
    print("--- B cihazı: aynı hesapla giriş", flush=True)
    cB, b = cihaz_ac(p, "B")
    b.goto(KOK)
    b.wait_for_timeout(SUNUCU_KOD_ARALIGI * 1000)
    kod_iste_ve_gir(b)
    b.wait_for_selector("text=Hesabınız başka bir cihazda açık")
    kontrol("devralma sorusu soruldu", b.locator("text=Diğer cihazınızdan çıkış yapmak için mailinize kod gelsin mi?").count() == 1)
    kontrol("B henüz yer almadı", list(D["yerler"]) == [a_oturumu])
    ekran(b, "03-devralma-soru")
    # Vazgeç: hesap A'da kalır, B'nin ilk oturumu kapanır
    oturum_sayisi = len(D["oturumlar"])
    b.click("button:has-text('Vazgeç')")
    b.wait_for_selector("#girisEposta")
    kontrol("vazgeçince giriş ekranı ve bilgi", "öbür cihazda açık kaldı" in b.inner_text(".giris-bilgi"))
    kontrol("vazgeçince B'nin oturumu kapandı, A sürüyor", len(D["oturumlar"]) == oturum_sayisi - 1 and list(D["yerler"]) == [a_oturumu] and a_oturumu in D["oturumlar"])

    # Yeniden dene ve devral
    b.wait_for_timeout(SUNUCU_KOD_ARALIGI * 1000)
    oturumlar_once = set(D["oturumlar"])
    kod_iste_ve_gir(b)
    b.wait_for_selector("text=Diğer cihazınızdan çıkış yapmak için mailinize kod gelsin mi?")
    b_ilk = (set(D["oturumlar"]) - oturumlar_once).pop()
    gonder = b.locator(".eylem button.ana")
    kontrol("kod düğmesi sayaçla kapalı", gonder.is_disabled() and "sn" in gonder.inner_text(), gonder.inner_text())
    b.wait_for_function("() => !document.querySelector('.giris-kutu .eylem button.ana').disabled", timeout=8000)
    otp_once = len(D["otp"])
    gonder.click()
    # Uygulama 3 sn bekledi, taklit sunucu 5 sn istiyor: önce "N saniye sonra" hatası gelmeli
    b.wait_for_selector(".giris-hata, #devralmaKod")
    if b.locator(".giris-hata").count():
        kontrol("sunucu sınırı mesajı gerçek süreyi söylüyor", re.search(r"\d+ saniye sonra", b.inner_text(".giris-hata")), b.inner_text(".giris-hata"))
        kontrol("sunucunun söylediği süreye göre sayaç kuruldu", b.locator(".eylem button.ana").is_disabled())
        b.wait_for_function("() => !document.querySelector('.giris-kutu .eylem button.ana').disabled", timeout=10000)
        b.click(".eylem button.ana")
    b.wait_for_selector("#devralmaKod")
    kontrol("ikinci kod gönderildi", len(D["otp"]) == otp_once + 1 and D["devralma"] is not None)
    ekran(b, "04-devralma-kod")
    b.fill("#devralmaKod", "111111")
    b.click("button:has-text('Öbür cihazdan çıkar ve gir')")
    b.wait_for_selector(".giris-hata")
    kontrol("ikinci kod gidince B'nin ilk oturumu kapatıldı", b_ilk not in D["oturumlar"])
    kontrol("devralmada yanlış kod reddedildi", "hatalı" in b.inner_text(".giris-hata") and list(D["yerler"]) == [a_oturumu])
    b.fill("#devralmaKod", "123456")
    b.click("button:has-text('Öbür cihazdan çıkar ve gir')")
    b.wait_for_selector(".not-perde")
    kontrol("B yer aldı, A çıkarıldı, sayaç 2", len(D["yerler"]) == 1 and a_oturumu not in D["yerler"] and D["sayac"] == 2, (D["yerler"], D["sayac"]))
    kontrol("A'nın oturumuna istemciden dokunulmadı (sunucu karar verir)", a_oturumu in D["oturumlar"])
    kontrol("onaylı profil: sözleşme yeniden sorulmadı", b.locator(".sozlesme").count() == 0)
    b.click("button:has-text('Anladım')")
    b.wait_for_selector(".ders-satiri")
    bekle_ki(b, lambda: b.locator(".ders-satiri:has-text('Born2beRoot') .durum").inner_text() != "yakında")
    b.click(".ders-satiri:has-text('Born2beRoot')")
    kontrol("A'nın ilerlemesi B'ye geldi", bekle_ki(b, lambda: b.locator(".agac .dal.okundu:has-text('Disk')").count() == 1))
    b.click(".agac .dal:has-text('Disk Partisyonlama')")
    kontrol("A'nın boyası B'de görünüyor", bekle_ki(b, lambda: b.locator(".okuma .boyali").count() >= 1))
    b.click(".alt-cubuk button:has-text('Kıraat')")

    # =================== A cihazı kendini kapatır ===================
    print("--- A cihazı: devredildiğini öğrenir", flush=True)
    a.bring_to_front()
    a.evaluate("() => esitle()")
    a.wait_for_selector(".giris-perde", timeout=8000)
    kontrol("A'da devredildi mesajı", "başka bir cihazda açıldı" in a.inner_text(".giris-bilgi"), a.inner_text(".giris-kutu")[:200])
    kontrol("A'daki yerel veri silindi", yerel_kayit_sayisi(a) == 0)
    ekran(a, "05-A-devredildi")

    # A yeniden girmeye çalışır: B açık olduğu için yine sorulur
    a.wait_for_timeout(SUNUCU_KOD_ARALIGI * 1000)
    kod_iste_ve_gir(a)
    a.wait_for_selector("text=Diğer cihazınızdan çıkış yapmak için mailinize kod gelsin mi?")
    kontrol("A'ya da devralma soruldu", True)
    a.click("button:has-text('Vazgeç')")
    a.wait_for_selector("#girisEposta")

    # =================== B çıkış yapar, A kodsuz girer ===================
    print("--- B çıkış yapar, A serbestçe girer", flush=True)
    b.on("dialog", lambda d: d.accept())
    cekmece(b, "hesap")
    kontrol("hesap panelinde tek cihaz bilgisi", b.locator("text=yalnızca bu cihazda açık olabilir").count() == 1)
    ekran(b, "06-B-hesap")
    b.click(".hesap-sayfa button:has-text('Çıkış yap')")
    onayla(b)
    b.wait_for_selector(".giris-perde")
    kontrol("B çıkınca oturumu kapandı, yer kalmadı", not [x for x in D["yerler"] if x in D["oturumlar"]])
    kontrol("B çıkışta yerini önce bıraktı", any(g.startswith("BIRAK ") for g in D["gunluk"]))
    kontrol("çıkışta son e-posta cihazdan silindi", b.evaluate("() => localStorage.getItem('pg.sonEposta')") is None)
    a.wait_for_timeout(SUNUCU_KOD_ARALIGI * 1000)
    kod_iste_ve_gir(a)
    a.wait_for_selector(".not-perde, .grup-baslik")
    kontrol("öbür cihaz çıkınca devralma sorulmadı, sayaç 3", a.locator("text=Diğer cihazınızdan").count() == 0 and len(D["yerler"]) == 1 and D["sayac"] == 3)
    if a.locator(".not-perde").count(): a.click("button:has-text('Anladım')")
    a.wait_for_selector(".grup-baslik")

    # =================== Sınır 2: C cihazı sorusuz girer, veriler eşitlenir ===================
    print("--- Sınır 2'ye çıkarıldı: C cihazı", flush=True)
    D["azami"] = 2
    cC, c = cihaz_ac(p, "C")
    c.goto(KOK)
    c.wait_for_timeout(SUNUCU_KOD_ARALIGI * 1000)
    kod_iste_ve_gir(c)
    c.wait_for_selector(".not-perde, .giris-baslik:has-text('başka bir cihazda'), .giris-baslik:has-text('Cihaz sınırınız dolu')")
    kontrol("sınır 2: C sorusuz girdi, iki cihaz açık, sayaç 4", c.locator(".not-perde").count() == 1 and len(D["yerler"]) == 2 and D["sayac"] == 4, (len(D["yerler"]), D["sayac"]))
    c.click("button:has-text('Anladım')")
    c.wait_for_selector(".ders-satiri")
    bekle_ki(c, lambda: c.locator(".ders-satiri:has-text('Born2beRoot') .durum").inner_text() != "yakında")
    c.click(".ders-satiri:has-text('Born2beRoot')")
    c.click(".agac .dal:has-text('SSH')")
    c.wait_for_selector(".okuma h2")
    c.click("text=Okudum olarak işaretle")
    kontrol("C'deki işaret sunucuda", bekle_ki(c, lambda: ("okundu", "b2r-ssh") in D["kayitlar"]))
    cekmece(a, "hesap"); a.click("button:has-text('Şimdi eşitle')"); a.wait_for_timeout(1200)
    kontrol("hesap panelinde sınır 2 yazıyor", a.locator("text=en çok 2 cihazda").count() == 1)
    a.click(".hesap-kapat")
    a.wait_for_timeout(500)
    kontrol("çıkıp sayfa yenilenmeden yeniden girince panel kapanıyor", a.locator(".hesap-sayfa").count() == 0)
    a.click(".ders-satiri:has-text('Born2beRoot')")
    kontrol("C'deki işaret A'ya geldi, A hâlâ açık", bekle_ki(a, lambda: a.locator(".agac .dal.okundu:has-text('SSH')").count() == 1) and a.locator(".giris-perde").count() == 0)
    c.evaluate("() => esitle()"); a.evaluate("() => esitle()"); a.wait_for_timeout(1000)
    kontrol("iki cihaz kullanılırken sayaç artmadı", D["sayac"] == 4)
    a.click(".alt-cubuk button:has-text('Kıraat')")

    # Sınır doluyken dördüncü cihaz: "en çok 2" metniyle sorulur
    cD, dd = cihaz_ac(p, "D")
    dd.goto(KOK)
    dd.wait_for_timeout(SUNUCU_KOD_ARALIGI * 1000)
    dd.fill("#girisEposta", EPOSTA); dd.click("button:has-text('Kod gönder')"); dd.wait_for_selector("#girisKod")
    dd.reload(); dd.wait_for_selector(".giris-perde")
    kontrol("kod beklerken yeniden yüklenince kod ekranı geri geldi", dd.locator("#girisKod").count() == 1)
    dd.fill("#girisKod", "123456"); dd.focus("#girisKod"); dd.keyboard.press("Enter"); dd.keyboard.press("Enter")
    dd.wait_for_selector(".giris-baslik:has-text('Cihaz sınırınız dolu')")
    kontrol("sınır doluyken sınır 2 metniyle soruldu", dd.locator("text=en çok 2 cihazda açık olabilir").count() == 1 and dd.locator("text=Çıkarılacak cihazda").count() == 1)
    ekran(dd, "08-sinir-2-soru")
    dd.click("button:has-text('Vazgeç')")
    dd.wait_for_selector("#girisEposta")
    kontrol("vazgeçince iki cihaz yerinde, sayaç 4", len(D["yerler"]) == 2 and D["sayac"] == 4)
    # Sunucuda oturumu kapatılan C cihazı (ör. süresi dolan ya da silinen oturum) kendini kapatır
    c_oturumu = [x for x in D["yerler"] if x != next(x for x in D["yerler"])]
    c_sid = c.evaluate("() => JSON.parse(atob(JSON.parse(localStorage.getItem('pg-oturum')).access_token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/'))).session_id")
    D["oturumlar"].pop(c_sid, None)
    c.evaluate("() => esitle()")
    c.wait_for_selector(".giris-perde", timeout=8000)
    kontrol("oturumu sunucuda kapanan cihaz kendini kapattı", "oturumunuz kapanmış" in c.inner_text(".giris-bilgi") and yerel_kayit_sayisi(c) == 0, c.inner_text(".giris-kutu")[:150])
    cC.close(); cD.close()

    # =================== Çevrimdışı (A, servis çalışanıyla) ===================
    print("--- A: çevrimdışı okuma ve geri bağlanma", flush=True)
    a.evaluate("() => navigator.serviceWorker.ready")
    bekle_ki(a, lambda: a.locator(".ders-satiri:has-text('Born2beRoot') .durum").inner_text() != "yakında")
    a.reload(); a.wait_for_selector(".grup-baslik")
    kontrol("yeniden açılışta giriş istenmedi", a.locator(".giris-perde").count() == 0)
    cA.set_offline(True)
    a.reload(); a.wait_for_selector(".grup-baslik", timeout=8000)
    a.click(".ders-satiri:has-text('Born2beRoot')")
    a.click(".agac .dal >> nth=1")
    a.wait_for_selector(".okuma h2")
    kontrol("çevrimdışı konu okunuyor", "Sanallaştırma" in a.inner_text(".okuma h2"))
    a.click("text=Okudum olarak işaretle")
    a.wait_for_timeout(2500)
    kontrol("çevrimdışı işaret beklemede", a.locator("#hesapDugme.cevrimdisi").count() == 1 and ("okundu", "b2r-sanallastirma") not in D["kayitlar"])
    cA.set_offline(False)
    a.evaluate("() => window.dispatchEvent(new Event('online'))")
    kontrol("bağlanınca işaret gönderildi", bekle_ki(a, lambda: ("okundu", "b2r-sanallastirma") in D["kayitlar"]))
    ekran(a, "07-A-sonra")

    # =================== Hususi yetki ===================
    print("--- A: hususi yetki", flush=True)
    a.click(".alt-cubuk button:has-text('Kıraat')"); a.click(".alt-cubuk button:has-text('Kıraat')")
    a.wait_for_selector(".grup-baslik")
    kontrol("hususi grubun başlığında etiket", a.locator(".grup-baslik:has-text('42') .hususi-etiket").count() == 1)
    b2r_sayisi = "() => Promise.all([Array.from(KONULAR.keys()).filter(k => k.startsWith('b2r-')).length, vt.hepsi('icerik').then(l => l.filter(x => String(x.anahtar).startsWith('konu:b2r-')).length)])"
    D["hususi"] = False
    a.evaluate("() => esitle()")
    kontrol("yetki geri alınınca hususi ders kayboldu, notları cihazdan silindi", bekle_ki(a, lambda: a.locator(".ders-satiri:has-text('Born2beRoot')").count() == 0 and a.evaluate(b2r_sayisi) == [0, 0]), a.evaluate(b2r_sayisi))
    kontrol("hususi olmayan dersler yerinde", a.locator(".ders-satiri:has-text('Algoritma')").count() == 1 and a.locator(".grup-baslik:has-text('42')").count() == 0)
    D["hususi"] = True
    a.evaluate("() => esitle()")
    kontrol("yetki verilince hususi ders kendiliğinden indi ve göründü", bekle_ki(a, lambda: a.locator(".ders-satiri:has-text('Born2beRoot')").count() == 1 and a.evaluate(b2r_sayisi) == [17, 17]), a.evaluate(b2r_sayisi))
    cA.close(); cB.close()

print("\n--- konsol ve sayfa hataları:")
for h in hatalar: print("  ", h)
gecen = sum(1 for _, k in sonuclar if k)
print("\n%d/%d kontrol geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) and not [h for h in hatalar if "pageerror" in h] else 1)

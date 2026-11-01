"""Programcılık — iki cihazlı tarayıcı testi.
Supabase istekleri Playwright içinde taklit edilir. Oturumlar, tek cihaz kuralı
ve RLS, 01-sema.sql'deki mantıkla aynı biçimde taklit edilir."""
import json, base64, time, sys, re, urllib.parse, datetime, uuid, shutil
from playwright.sync_api import sync_playwright

YUK = json.load(open("/home/claude/test/gercek/cikti/yuklenen.json"))
DEPO = "/home/claude/test/gercek/cikti/depo"
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
    "hususi": False,            # test hesabının hususi yetkisi
    "gorsel_istek": [],
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

def oturum_ac(sid=None):
    # Yenilemede (refresh_token) Supabase aynı oturumu sürdürür: session_id
    # aynı kalır, yalnızca belirteçler yenilenir.
    if sid is None:
        sid = str(uuid.uuid4())
        D["oturumlar"][sid] = {"olusma": time.time(), "yenileme": None}
    yen = "yen-" + sid + "-" + uuid.uuid4().hex[:6]
    D["oturumlar"][sid]["yenileme"] = yen
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
                return cevap(oturum_ac(s_id))
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
        if not uye(sid): return cevap([])
        return cevap([r for r in YUK["agac"] if r["id"] == 1 or D["hususi"]])
    if yol == "/rest/v1/konular":
        if not uye(sid): return cevap([])
        gorunen = [k for k in YUK["konular"] if D["hususi"] or not k["hususi"]]
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
        ad = urllib.parse.unquote(yol).split("/gorseller/", 1)[-1]
        D["gorsel_istek"].append(ad)
        try: govde_ = open(DEPO + "/" + ad, "rb").read()
        except OSError: return cevap({"message": "Object not found"}, 400)
        tur = {"svg": "image/svg+xml", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ad.rsplit(".", 1)[-1], "application/octet-stream")
        return route.fulfill(status=200, headers={**baslik, "content-type": tur}, body=govde_)
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


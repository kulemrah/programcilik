"""Programcılık — iki cihazlı tarayıcı testi.
Supabase istekleri Playwright içinde taklit edilir. Oturumlar, tek cihaz kuralı
ve RLS, 01-sema.sql'deki mantıkla aynı biçimde taklit edilir."""
import json, base64, time, sys, re, os, urllib.parse, datetime, uuid, shutil
from playwright.sync_api import sync_playwright

# Taklit sunucuya yüklenen içerik: test/gercek/cikti (testler test/tarayici içinden çalıştırılır)
GERCEK = os.path.join(os.getcwd(), "..", "gercek", "cikti")
YUK = json.load(open(os.path.join(GERCEK, "yuklenen.json")))
DEPO = os.path.join(GERCEK, "depo")
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
    "hususi": False,            # test hesabının hususi yetkisi (yönetici)
    "gorsel_istek": [],
    # Bölüm: profil None iken hesap, bölüm kodundan önce açılmış (BP 1. sınıf,
    # sözleşmesiz) sayılır; kodsuz True ise bölümü yok ve kod ekranı açılır.
    "kodsuz": False, "kodlar": [], "yanlis": 0, "sifirlanan": [],
}
BP = "bilgisayar-programciligi"
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

def profil():
    """01-sema.sql profiller satırı: kodla yazılan ya da (taklitte) eski hesap"""
    if D["profil"] is None and not D["kodsuz"]:
        return {"program": BP, "sinif": 1, "sozlesme_surumu": None}
    return D["profil"]

def uye(sid):
    p = profil()
    return bool(p and p["sozlesme_surumu"] == "2" and sid and sid in D["yerler"] and sid in D["oturumlar"])

def konu_gorunur(k):
    """01-sema.sql konu_gorunur"""
    if k.get("hususi"): return D["hususi"]
    p = profil()
    return bool(p and p["program"] in (k.get("programlar") or []) and k.get("sinif") is not None and p["sinif"] >= k["sinif"])

def kod_isle(girilen):
    """01-sema.sql bolum_kodu_kullan (sadeleştirilmiş: kilit 5 yanlışta)"""
    if profil(): return {"durum": "zaten"}
    m = re.match(r"^\s*[A-Za-z]{2,4}[1-6]\s*[_-]?", girilen or "")
    sade = re.sub(r"\s", "", (girilen or "")[m.end():] if m else (girilen or ""))
    if not re.fullmatch(r"[0-9]{6}", sade): return {"durum": "bicim"}
    if D["yanlis"] >= 5: return {"durum": "kilitli", "saniye": 900}
    k = next((k for k in D["kodlar"] if k["kod"] == sade and not k.get("iptal")), None)
    neden = None
    if not k: neden = "yanlis"
    elif k["bitis"] <= time.time(): neden = "suresi_doldu"
    elif k["kullanim"] >= k["azami"]: neden = "dolu"
    if neden in ("suresi_doldu", "dolu"): return {"durum": neden}   # deneme sayılmaz
    if neden:
        D["yanlis"] += 1
        if D["yanlis"] >= 5: return {"durum": neden, "kalan": 0, "saniye": 900}
        return {"durum": neden, "kalan": 5 - D["yanlis"]}
    k["kullanim"] += 1; D["yanlis"] = 0
    D["profil"] = {"program": k["program"], "sinif": k["sinif"], "sozlesme_surumu": None}
    k.setdefault("kullananlar", []).append({"kullanici": UID, "eposta": EPOSTA, "zaman": simdi_iso()})
    return {"durum": "tamam", "program": k["program"], "programAdi": "Bilgisayar Programcılığı" if k["program"] == BP else k["program"], "sinif": k["sinif"]}

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
    # Kaynak: bu düzenekte boş (Kaynak'ın kendi testi kaynak_sina.py gerçekçi sunucuya aktarır)
    if yol in ("/rest/v1/kaynak_tasnif", "/rest/v1/kaynak_oge") and yontem == "GET":
        return cevap([])
    if yol == "/rest/v1/rpc/kaynak_durum":
        return cevap({"izin": True, "azami_bayt": 52428800, "kullanilan_bayt": 0})
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
    # ---- Bölüm kodu ve İdare (01-sema.sql, 5b) ----
    if yol == "/rest/v1/rpc/hususi_yetkili":
        return cevap(D["hususi"])
    if yol == "/rest/v1/rpc/bolum_kodu_kullan":
        if cihaz_durumu(sid) == "yetkisiz": return cevap({"code": "P0001", "message": "Yetkisiz"}, 400)
        return cevap(kod_isle(json.loads(govde or "{}").get("girilen")))
    if yol.startswith("/rest/v1/rpc/bolum_kodu_") or yol.startswith("/rest/v1/rpc/idare_") or yol == "/rest/v1/rpc/bolum_kodlari_listesi":
        if not D["hususi"]: return cevap({"code": "P0001", "message": "Yetkisiz"}, 400)
        g = json.loads(govde or "{}")
        if yol.endswith("bolum_kodu_uret"):
            sinir = {"bilgisayar-programciligi": 2}.get(g["p_program"])
            if not sinir: return cevap({"code": "P0001", "message": "Bölüm bulunamadı"}, 400)
            if not 1 <= g["p_sinif"] <= sinir: return cevap({"code": "P0001", "message": "Sınıf geçersiz"}, 400)
            kod = "%06d" % (482913 + len(D["kodlar"]))
            k = {"id": str(uuid.uuid4()), "kod": kod, "etiket": "BP%d_%s" % (g["p_sinif"], kod), "program": g["p_program"], "sinif": g["p_sinif"],
                 "bitis": time.time() + g["p_dakika"] * 60, "azami": g["p_azami"], "kullanim": 0, "olusma": time.time(), "kullananlar": []}
            D["kodlar"].append(k)
            return cevap({"id": k["id"], "kod": kod, "etiket": k["etiket"], "bitis": datetime.datetime.fromtimestamp(k["bitis"], datetime.timezone.utc).isoformat(), "azami": k["azami"]})
        if yol.endswith("bolum_kodlari_listesi"):
            iso = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).isoformat()
            def durum(k):
                if k.get("iptal"): return "iptal"
                if k["bitis"] <= time.time(): return "suresi_doldu"
                return "dolu" if k["kullanim"] >= k["azami"] else "etkin"
            return cevap([{"id": k["id"], "etiket": k["etiket"], "program": k["program"], "programAdi": "Bilgisayar Programcılığı", "sinif": k["sinif"],
                           "olusturuldu": iso(k["olusma"]), "bitis": iso(k["bitis"]), "azami": k["azami"], "kullanim": k["kullanim"],
                           "iptal": iso(k["iptal"]) if k.get("iptal") else None, "durum": durum(k), "kullananlar": k["kullananlar"]}
                          for k in sorted(D["kodlar"], key=lambda k: -k["olusma"])])
        if yol.endswith("bolum_kodu_iptal"):
            for k in D["kodlar"]:
                if k["id"] == g["p_id"] and not k.get("iptal"): k["iptal"] = time.time()
            return route.fulfill(status=204, headers=baslik, body="")
        if yol.endswith("idare_hesap_bul"):
            a = g["p_eposta"].strip().lower()
            if a == "kodlu@kocaelisaglik.edu.tr":
                return cevap({"kullanici": "22222222-2222-2222-2222-222222222222", "eposta": a, "program": BP, "programAdi": "Bilgisayar Programcılığı",
                              "sinif": 1, "etiket": "BP1_482913", "sozlesme": True})
            return cevap(None)
        if yol.endswith("idare_hesap_sifirla"):
            if g["p_kullanici"] == UID: return cevap({"code": "P0001", "message": "Kendi hesabınızı sıfırlayamazsınız"}, 400)
            D["sifirlanan"].append(g["p_kullanici"])
            for k in D["kodlar"]: k["kullananlar"] = [u for u in k["kullananlar"] if u["kullanici"] != g["p_kullanici"]]
            return route.fulfill(status=204, headers=baslik, body="")

    # ---- Tablolar ----
    if yol == "/rest/v1/programlar":
        return cevap([{"id": BP, "ad": "Bilgisayar Programcılığı", "sinif_sayisi": 2, "sira": 1}])
    if yol == "/rest/v1/profiller":
        if yontem == "GET":
            p = profil()
            return cevap(p if tek else ([p] if p else []))
        if yontem != "PATCH":   # 01-sema.sql: istemcinin ekleme yetkisi yok
            return cevap({"code": "42501", "message": "permission denied for table profiller"}, 403)
        d = json.loads(govde); d = d[0] if isinstance(d, list) else d
        if set(d) != {"sozlesme_surumu"}:
            return cevap({"code": "42501", "message": "permission denied for table profiller"}, 403)
        p = profil()
        if not p: return cevap({"code": "PGRST116", "message": "JSON object requested, multiple (or no) rows returned"}, 406)
        if d["sozlesme_surumu"] != "2":
            return cevap({"message": "Sözleşmenin geçerli sürümü onaylanmalı"}, 400)
        D["profil"] = dict(p, sozlesme_surumu=d["sozlesme_surumu"])
        return cevap(D["profil"] if tek else [D["profil"]], 200)
    if yol == "/rest/v1/agac":
        if not uye(sid): return cevap([])
        p = profil()
        kitle = "1/%s/%d" % (p["program"], p["sinif"])
        return cevap(sorted([r for r in YUK["agac"] if r["id"] == kitle or (r["id"] == "2/hususi" and D["hususi"])], key=lambda r: r["id"]))
    if yol == "/rest/v1/konular":
        if not uye(sid): return cevap([])
        gorunen = [k for k in YUK["konular"] if konu_gorunur(k)]
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


def kart_kapsam_sina(s, KONULAR_VT, onek):
    """42 Tarzı: ders ve konu seçimi Temrin'deki seçim ekranıyla yapılır (ayrı tutulur).
    Ders testleri (alg, vt, eko, el, ag, dn) bunu kendi dersleriyle çağırır."""
    ders = KONULAR_VT[0]["ders"]
    agac = next(r for r in YUK["agac"] if r["id"] == "1/" + BP + "/1")["veri"]
    dersler = [d for g in agac["gruplar"] if not g.get("hususi") for dn in g.get("donemler", [{"dersler": g.get("dersler", [])}]) for d in dn["dersler"]]
    bilgi = next(d for d in dersler if d["id"] == ders)
    kisa, tam = bilgi.get("kisa", bilgi["ad"]), bilgi["ad"]
    kartli = [k for k in KONULAR_VT if k["kartlar"]]
    kart_top = sum(len(k["kartlar"]) for k in kartli)
    KARTLI_DERSLER = [d["ad"] for d in dersler if any(k["ders"] == d["id"] and k["kartlar"] for k in YUK["konular"])]
    print("--- 42 Tarzı (ders ve konu seçimi)", flush=True)
    temrin_once = s.evaluate("() => JSON.stringify(depo.oku('pg.kapsam', {}))")
    s.click(".alt-cubuk button:has-text('42 Tarzı')")
    s.wait_for_selector("#sayfaKart .suzgec-dugme")
    kontrol("42 Tarzı: ilk açılışta seçim yok", s.inner_text("#sayfaKart .suzgec-dugme .deger") == "Seçilmedi" and s.locator("#sayfaKart .cip").count() == 0)
    s.click("#sayfaKart button:has-text('Ders ve konu seç')")
    s.wait_for_selector("#sayfaKart button:has-text('‹ 42 Tarzı')")
    adlar = s.locator("#sayfaKart .kontrol-oge > button:not(.kutucuk) > span").evaluate_all("els => els.filter(e => !e.classList.contains('ileri')).map(e => e.firstChild.textContent)")
    kontrol("seçim ekranında kartlı dersler sırasıyla", adlar == KARTLI_DERSLER, (adlar, KARTLI_DERSLER))
    s.click("#sayfaKart .kontrol-oge:has-text('%s') .kutucuk" % tam)
    s.click("#sayfaKart .eylem button:has-text('Tamam')")
    s.wait_for_selector("#sayfaKart button.ana:has-text('kartla çalış')")
    kontrol("dersin tamamı: %d kart, özet '%s'" % (kart_top, kisa), ("%d kartla çalış" % kart_top) in s.inner_text("#sayfaKart") and s.inner_text("#sayfaKart .suzgec-dugme .deger") == kisa, s.inner_text("#sayfaKart .suzgec-dugme .deger"))
    kontrol("Temrin seçimi etkilenmedi", s.evaluate("() => JSON.stringify(depo.oku('pg.kapsam', {}))") == temrin_once)
    # İki konu
    s.click("#sayfaKart .suzgec-dugme")
    s.click("#sayfaKart .kontrol-oge:has-text('%s') button:not(.kutucuk)" % tam)
    s.wait_for_selector("#sayfaKart button:has-text('‹ Dersler')")
    kontrol("konu listesi: Tümü + %d kartlı konu" % len(kartli), s.locator("#sayfaKart .kontrol .kontrol-oge").count() == len(kartli) + 1)
    s.click("#sayfaKart .kontrol .kontrol-oge >> nth=0")    # Tümü kalkar
    k6, k7 = kartli[1], kartli[2]
    s.click("#sayfaKart .kontrol .kontrol-oge >> nth=2"); s.click("#sayfaKart .kontrol .kontrol-oge >> nth=3")
    s.click("#sayfaKart button:has-text('‹ Dersler')")
    s.click("#sayfaKart .eylem button:has-text('Tamam')")
    s.wait_for_selector("#sayfaKart button.ana:has-text('kartla çalış')")
    iki = len(k6["kartlar"]) + len(k7["kartlar"])
    kontrol("iki konu: %d kart" % iki, ("%d kartla çalış" % iki) in s.inner_text("#sayfaKart"), s.inner_text("#sayfaKart")[:200])
    kontrol("ana ekranda kart listesi yok", s.locator("#sayfaKart .sonuc-kart").count() == 0)
    s.click("#sayfaKart button:has-text('liste hâlinde oku')")
    s.wait_for_selector("#sayfaKart button:has-text('‹ 42 Tarzı')")
    kontrol("liste ekranı yalnızca o iki konunun kartları", s.locator("#sayfaKart .sonuc-kart").count() == iki)
    s.click("#sayfaKart button:has-text('‹ 42 Tarzı')")
    s.wait_for_selector("#sayfaKart button.ana:has-text('kartla çalış')")
    s.reload(); s.wait_for_selector(".alt-cubuk")
    s.click(".alt-cubuk button:has-text('42 Tarzı')"); s.wait_for_selector("#sayfaKart button.ana:has-text('kartla çalış')")
    kontrol("seçim yenilemeden sonra duruyor", ("%d kartla çalış" % iki) in s.inner_text("#sayfaKart"))
    s.click("#sayfaKart button.ana:has-text('kartla çalış')")
    s.wait_for_selector(".deste .kart-yeri:not(.sonraki)")
    beklenen = "%s · 2 konu" % kisa
    kontrol("deste başlığı '%s'" % beklenen, s.inner_text(".ilerleme span >> nth=0") == beklenen, s.inner_text(".ilerleme span >> nth=0"))
    s.click(".deste-eylem button:has-text('Cevabı göster')"); s.wait_for_timeout(700)
    s.screenshot(path=onek + "-kart-arka.png")
    s.click(".alt-cubuk button:has-text('42 Tarzı')")   # etkin sekmeye dokununca ana ekran
    s.wait_for_selector("#sayfaKart .suzgec-dugme")
    s.click("#sayfaKart .suzgec-dugme")
    s.click("#sayfaKart .eylem button:has-text('Seçimi temizle')")
    s.click("#sayfaKart .eylem button:has-text('Tamam')")
    s.wait_for_selector("#sayfaKart button:has-text('Ders ve konu seç')")
    kontrol("seçim temizlenince 'Seçilmedi'", s.inner_text("#sayfaKart .suzgec-dugme .deger") == "Seçilmedi")
    s.screenshot(path=onek + "-kart-sayfa.png", full_page=False)

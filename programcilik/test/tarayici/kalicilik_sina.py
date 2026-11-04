"""İstatistik verisinin kalıcılığı: yeniden yükleme, çıkış-giriş, sunucuyla tutarlılık."""
exec(open("vt_taban.py", encoding="utf-8").read())
D["hususi"] = True
alg = sorted([k for k in YUK["konular"] if k["ders"] == "algoritma"], key=lambda k: k["sira"])
K1 = alg[0]["id"]
TIK = "n => { for (let i = 0; i < n; i++) { sonTik = Date.now() - 5000; sonDokunus = Date.now(); calismaTiki(); } }"

def giris(s, ilk):
    s.goto(KOK) if ilk else None
    s.wait_for_selector(".giris-perde")
    s.fill("#girisEposta", EPOSTA); s.click("button:has-text('Kod gönder')")
    s.wait_for_selector("#girisKod"); s.fill("#girisKod", "123456"); s.click("button:has-text('Giriş yap')")
    s.wait_for_selector(".sozlesme, .not-perde, .grup-baslik")
    if s.locator(".sozlesme").count():
        s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
        s.wait_for_selector(".not-perde, .grup-baslik")
    if s.locator(".not-perde").count(): s.click("button:has-text('Anladım')")
    s.wait_for_selector(".grup-baslik")

def sunucu(anahtar):
    r = D["kayitlar"].get(("calisma", anahtar))
    return r and r["deger"]

with sync_playwright() as p:
    c, s = cihaz_ac(p, "T", kalici=True)
    s.set_viewport_size({"width": 390, "height": 800})
    s.on("dialog", lambda d: d.accept())
    giris(s, True)
    A = s.evaluate("() => YAZICI")
    kontrol("yazıcı kimliği hazır", isinstance(A, str) and len(A) == 12, A)
    gun = s.evaluate("() => gunAnahtari(Date.now())")
    s.evaluate("id => konuAc(id)", K1); s.wait_for_selector(".okuma h2")
    s.evaluate("() => esitle()")
    bekle_ki(s, lambda: s.evaluate("() => gonderilmemisSayisi()") == 0)
    s.evaluate(TIK, 6); s.evaluate("() => calismaYaz()")
    kontrol("yalnızca süre bekliyorken hesap noktası yanmaz", s.locator("#hesapDugme.bekliyor").count() == 0)
    kontrol("ama bekleyen sayısında görünür (çıkış uyarısı için)", s.evaluate("() => gonderilmemisSayisi()") >= 1)
    s.evaluate("() => esitle()")
    kontrol("30 sn sunucuda", bekle_ki(s, lambda: (sunucu(gun + "|" + A) or {}).get("o", {}).get(K1) == 30), sunucu(gun + "|" + A))
    # ---- Sayfa yeniden yüklenince ----
    s.reload(); s.wait_for_selector(".grup-baslik")
    kontrol("yeniden yüklemede aynı yazıcı", s.evaluate("() => YAZICI") == A)
    kontrol("cihazdaki satır yerinde", s.evaluate("k => (kayit('calisma', k) || {}).o", gun + "|" + A) == {K1: 30})
    s.evaluate("id => konuAc(id)", K1); s.wait_for_selector(".okuma h2")
    s.evaluate(TIK, 2); s.evaluate("() => { calismaYaz(); esitle(); }")
    kontrol("aynı satıra eklendi: 40 sn", bekle_ki(s, lambda: (sunucu(gun + "|" + A) or {}).get("o", {}).get(K1) == 40), sunucu(gun + "|" + A))
    # ---- Çıkış: birikim bir sonraki hesaba geçmez ----
    s.evaluate("id => birikimeEkle('o', id, 77)", K1)
    s.click(".alt-cubuk button >> nth=0")
    cekmece(s, "hesap")
    s.click(".hesap-sayfa button:has-text('Çıkış yap')")
    onayla(s)
    s.wait_for_selector(".giris-perde")
    kontrol("çıkışta yazıcı ve birikim silindi", s.evaluate("() => [YAZICI, calismaBirikimi.size]") == [None, 0])
    kontrol("çıkıştan önce birikim hesaba yazıldı (40+77)", (sunucu(gun + "|" + A) or {}).get("o", {}).get(K1) == 117, sunucu(gun + "|" + A))
    s.evaluate("id => birikimeEkle('o', id, 999)", K1)   # oturumsuzken birikim (olmamalı ama)
    # ---- Aynı gün yeniden giriş: eski satır ezilmez ----
    s.wait_for_timeout(SUNUCU_KOD_ARALIGI * 1000)
    giris(s, False)
    B = s.evaluate("() => YAZICI")
    kontrol("yeniden girişte yeni yazıcı", B and B != A, (A, B))
    s.evaluate("id => konuAc(id)", K1); s.wait_for_selector(".okuma h2")
    s.evaluate(TIK, 2); s.evaluate("() => { calismaYaz(); esitle(); }")
    kontrol("yeni satır açıldı (10 sn)", bekle_ki(s, lambda: (sunucu(gun + "|" + B) or {}).get("o", {}).get(K1) == 10), sunucu(gun + "|" + B))
    kontrol("eski satır ezilmedi (117 sn)", (sunucu(gun + "|" + A) or {}).get("o", {}).get(K1) == 117, sunucu(gun + "|" + A))
    kontrol("oturumsuz birikim yeni hesaba yazılmadı", (sunucu(gun + "|" + B) or {}).get("o", {}).get(K1) == 10)
    kontrol("konuda bugün 3 dk'dan az (127 sn): süre sayılmaz", s.evaluate("() => (istatistikTopla(null).dersler.get('algoritma') || {}).o || 0") == 0)
    s.evaluate("([g, id]) => kayitYaz('calisma', g + '|cccccccccccc', { o: { [id]: 60 } }, true)", [gun, K1])
    kontrol("istatistik üç satırı toplar: 187 sn (3 dk'yı geçince sayılır)", bekle_ki(s, lambda: s.evaluate("() => (istatistikTopla(null).dersler.get('algoritma') || {}).o") == 187))
    # ---- Kaldırılmış konu: toplamlar her yerde aynı ----
    s.evaluate("() => kayitYaz('calisma', '2026-01-01|ffffffffffff', { o: { 'silinmis-konu': 1200 } }, true)")
    s.click(".alt-cubuk button >> nth=0")
    cekmece(s, "istatistik")
    s.click(".donem-satiri .cip:has-text('Tümü')")
    kontrol("Öbür konular listede", s.locator(".halka-satir:has-text('Öbür konular')").count() == 1)
    kutu = s.locator(".ist-kutu >> nth=0 >> .deger").inner_text()
    orta = s.locator(".halka-orta-deger").text_content()
    kontrol("özet kutusu ile halka toplamı aynı", kutu == orta, (kutu, orta))
    s.click(".hesap-kapat")
    kontrol("sayfa hatası yok", not hatalar, hatalar[:3])
print(sum(1 for _, k in sonuclar if k), "/", len(sonuclar))

# ---- İki sekme: aynı satırı paylaşmazlar ----
sonuclar_once = len(sonuclar)
with sync_playwright() as p:
    c, s = cihaz_ac(p, "U", kalici=True)
    s.on("dialog", lambda d: d.accept())
    D["yerler"].clear()
    time.sleep(SUNUCU_KOD_ARALIGI)
    giris(s, True)
    Y1 = s.evaluate("() => YAZICI")
    s2 = c.new_page(); s2.goto(KOK); s2.wait_for_selector(".grup-baslik")
    Y2 = s2.evaluate("() => YAZICI")
    kontrol("ikinci sekme ayrı yazıcıyla çalışır", Y1 and Y2 and Y1 != Y2, (Y1, Y2))
    s2.close(); s.wait_for_timeout(300)
    s3 = c.new_page(); s3.goto(KOK); s3.wait_for_selector(".grup-baslik")
    kontrol("ilk sekme açıkken yeni sekme yine ayrı", s3.evaluate("() => YAZICI") not in (Y1, None))
    s.close(); s3.close(); s.wait_for_timeout(300) if False else None
    s4 = c.new_page(); s4.goto(KOK); s4.wait_for_selector(".grup-baslik")
    kontrol("sekmeler kapanınca kayıtlı yazıcı geri gelir", s4.evaluate("() => YAZICI") == Y1, s4.evaluate("() => YAZICI"))
print(sum(1 for _, k in sonuclar if k), "/", len(sonuclar))

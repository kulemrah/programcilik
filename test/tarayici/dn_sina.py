"""Bilgisayar Donanımı içeriği — uygulamada uçtan uca deneme.
İçerik, gerçek aktarıcının sahte sunucuya yüklediği hâliyle (yuklenen.json + depo) kullanılır.
Hesabın hususi yetkisi yok: 42 grubu görünmemeli."""
exec(open("vt_taban.py", encoding="utf-8").read())

KONULAR_VT = sorted([k for k in YUK["konular"] if k["ders"] == "donanim"], key=lambda k: k["sira"])
SORU = {s["id"]: s for k in KONULAR_VT for s in k["sorular"]}
OKU_SORU = next(s for s in KONULAR_VT[-1]["sorular"] if s["tip"] == "secme" and s.get("yer"))
md_basliklari = lambda m: [re.sub(r"^#+\s*", "", l).strip() for l in m.split("\n") if re.match(r"^#{3,4} ", l)]

def giris(s):
    s.goto(KOK)
    s.wait_for_selector(".giris-perde")
    s.fill("#girisEposta", EPOSTA)
    s.click("button:has-text('Kod gönder')")
    s.wait_for_selector("#girisKod")
    s.fill("#girisKod", "123456")
    s.click("button:has-text('Giriş yap')")
    s.wait_for_selector(".sozlesme")
    s.click("text=Okudum, kabul ediyorum")
    s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde")
    s.click("button:has-text('Anladım')")
    s.wait_for_selector(".grup-baslik")

def tikla_metinle(s, secici, metin):
    """Metni birebir eşleşen ilk görünür öğeye tıklar (alt dize karışıklığı olmasın)."""
    n = s.evaluate("""([sec, m]) => { const els = Array.from(document.querySelectorAll(sec))
        .filter(e => e.offsetParent !== null && !e.disabled && !e.classList.contains('tamam'));
      const e = els.find(x => (x.dataset.t = x.textContent.replace(/\\s+/g, ' ').trim()) === m);
      if (!e) return els.map(x => x.dataset.t).join(' | ');
      e.click(); return ''; }""", [secici, metin])
    if n: raise AssertionError("bulunamadı: " + metin + " — mevcut: " + n)

duz = lambda t: re.sub(r"\s+", " ", t.replace("`", "").replace("**", "")).strip()

with sync_playwright() as p:
    c, s = cihaz_ac(p, "V")
    print("--- giriş", flush=True)
    giris(s)
    bekle_ki(s, lambda: s.locator(".ders-satiri:has-text('Bilgisayar Donanımı') .durum").inner_text() != "yakında")
    gruplar = s.locator(".grup-baslik").evaluate_all("els => els.map(e => e.firstChild.textContent)")
    kontrol("hususi yetkisiz hesapta 42 grubu yok", gruplar == ["1. Sınıf"], gruplar)
    kontrol("Donanım dersi açık (yakında değil)", s.locator(".ders-satiri:has-text('Bilgisayar Donanımı') .durum").inner_text() != "yakında")

    # ---------------- Okuma: 7 konu, başlıklar, görseller ----------------
    s.click(".ders-satiri:has-text('Bilgisayar Donanımı')")
    s.wait_for_selector(".agac .dal")
    dallar = s.locator(".agac .dal").all_inner_texts()
    kontrol("%d konu doğru sırada" % len(KONULAR_VT), len(dallar) == len(KONULAR_VT) and all(k["baslik"] in d for k, d in zip(KONULAR_VT, dallar)), dallar)
    for i, k in enumerate(KONULAR_VT):
        s.click(".agac .dal >> nth=%d" % i)
        s.wait_for_selector(".okuma h2")
        beklenen = md_basliklari(k["metin"])
        cizilen = s.locator(".okuma [data-baslik]").evaluate_all("els => els.map(e => e.dataset.baslik)")
        kontrol(k["id"] + ": %d başlık birebir" % len(beklenen), cizilen == beklenen, (beklenen, cizilen))
        gorsel = len(re.findall(r"^!\[", k["metin"], re.M))
        if gorsel:
            try:
                s.wait_for_function("n => { const g = Array.from(document.querySelectorAll('.okuma figure img'));"
                                    " return g.length === n && g.every(i => i.src.startsWith('blob:') && i.complete && i.naturalWidth > 0) }",
                                    arg=gorsel, timeout=8000)
                kontrol(k["id"] + ": %d görsel yüklendi" % gorsel, True)
            except Exception as e:
                kontrol(k["id"] + ": %d görsel yüklendi" % gorsel, False, s.evaluate("() => Array.from(document.querySelectorAll('.okuma figure img')).map(i => [i.src.slice(0,20), i.naturalWidth])"))
        satirlar_ = k["metin"].split("\n")
        tablo = sum(1 for j, l in enumerate(satirlar_) if l.startswith("|") and (j == 0 or not satirlar_[j - 1].startswith("|")))
        kontrol(k["id"] + ": tablo sayısı %d" % tablo, s.locator(".okuma table").count() == tablo)
        if True:
            s.screenshot(path="dn-konu-%d.png" % (i + 1), full_page=True)
        s.click("text=‹ Geri")
        s.wait_for_selector(".agac .dal")

    # ---------------- Temrin: her soru, içerikteki doğru cevapla doğru sayılmalı ----------------
    print("--- temrin", flush=True)
    s.click(".alt-cubuk button:has-text('Temrin')")
    s.click("button:has-text('Ders ve konu seç')")
    s.wait_for_selector(".kontrol-oge")
    s.click(".kontrol-oge:has-text('Bilgisayar Donanımı') .kutucuk")
    s.click("button:has-text('Tamam')")
    s.wait_for_selector(".mod-kart")
    modlar = dict(zip(s.locator(".mod-kart .ad").all_inner_texts(), s.locator(".mod-kart .sayi").all_inner_texts()))
    from collections import Counter
    sayim = Counter(x["tip"] for x in SORU.values())
    beklenen_mod = {"Çoktan seçmeli": sayim["secme"], "Doğru mu, yanlış mı": sayim["dy"], "Boşluk doldurma": sayim["bosluk"],
                    "Sıralama": sayim["dizme"], "Eşleştirme": sayim["esles"], "Hesaplama": sayim["hesap"], "Klasik": sayim["klasik"]}
    kontrol("mod sayıları içerikle aynı", all(modlar.get(a) == "%d soru" % n for a, n in beklenen_mod.items() if n) and not any(a in modlar for a, n in beklenen_mod.items() if not n), (modlar, beklenen_mod))
    kontrol("konu konu: %d konu; kavram kartları: %d" % (len(KONULAR_VT), sum(len(k["kavramlar"]) for k in KONULAR_VT)),
            modlar.get("Konu konu çalış") == "%d konu" % len(KONULAR_VT) and modlar.get("Kavram kartları") == "%d kart" % sum(len(k["kavramlar"]) for k in KONULAR_VT), modlar)

    s.evaluate("() => { derinlesGit(calisMenusuCiz); oturumBaslat(karistir(kapsamdakiSorular()), 'Hepsi'); }")
    toplam = s.evaluate("() => oturum.sorular.length")
    kontrol("oturumda bütün sorular (%d)" % len(SORU), toplam == len(SORU), toplam)
    yanlis_sayilan = []
    for n in range(toplam):
        sid = s.evaluate("() => oturum.sorular[oturum.i].id")
        q = SORU[sid]; once = s.evaluate("() => oturum.dogru")
        try:
            if q["tip"] in ("secme", "izleme"):
                tikla_metinle(s, ".secenekler .secenek > span:last-child", duz(q["secenekler"][q["dogru"]]))
            elif q["tip"] == "dy":
                s.click(".dy-dugmeler button:has-text('%s')" % ("Doğru" if q["dogru"] else "Yanlış"))
            elif q["tip"] == "bosluk":
                for i, c_ in enumerate(q["cevaplar"]): s.fill(".bosluk-girdi >> nth=%d" % i, c_[0])
                s.click(".eylem button:has-text('Kontrol et')")
            elif q["tip"] == "dizme":
                for parca in q["parcalar"]: tikla_metinle(s, ".havuz .parca", duz(parca))
                s.click(".eylem button:has-text('Kontrol et')")
            elif q["tip"] == "esles":
                for sol, sag in q["ciftler"]:
                    tikla_metinle(s, ".esles-sutun:first-child .esles-oge", duz(sol))
                    tikla_metinle(s, ".esles-oge.sag", duz(sag))
            elif q["tip"] == "hesap":
                s.fill(".hesap-satir input", str(q["cevap"]).replace(".", ","))
                s.click(".eylem button:has-text('Kontrol et')")
            elif q["tip"] == "klasik":
                s.fill(".klasik-girdi", q["cevap"])
                s.click("button:has-text('Örnek cevabı göster')")
                hepsi_, var_ = s.locator(".anahtarlar .anahtar").count(), s.locator(".anahtarlar .anahtar.var").count()
                if hepsi_ != var_: yanlis_sayilan.append(sid + " anahtar %d/%d" % (var_, hepsi_))
                s.click(".oz-puan button:has-text('Bildim')")
        except AssertionError as e:
            yanlis_sayilan.append(sid + " " + str(e)); s.evaluate("() => { oturum.i++; soruCiz(); }"); continue
        if s.evaluate("() => oturum.dogru") != once + 1: yanlis_sayilan.append(sid + " yanlış sayıldı")
        if s.locator(".izah .nereden").count() != 1: yanlis_sayilan.append(sid + " konuda-oku bağlantısı yok")
        elif q.get("yer") and not s.inner_text(".izah .nereden").endswith(q["yer"] + " ›"): yanlis_sayilan.append(sid + " yer: " + s.inner_text(".izah .nereden"))
        s.click(".eylem button.ana >> text=/Sonraki soru|Sonucu gör/")
    kontrol("her soru içerikteki cevapla doğru sayıldı, anahtarlar örnek cevapta, yer bağlantısı doğru", not yanlis_sayilan, yanlis_sayilan)
    kontrol("sonuç ekranı %d/%d" % (toplam, toplam), str(toplam) in s.inner_text("#sayfaCalis"))
    kontrol("yanlış defteri boş", not [x for x in D["kayitlar"] if x[0] == "yanlis" and not D["kayitlar"][x].get("silindi")])

    # Bir sorunun "konuda oku" bağlantısı başlığa götürür
    s.evaluate("() => { oturumBaslat([SORU_HARITASI.get('%s')" % OKU_SORU["id"] + "], 'Tek'); }")
    s.click(".secenekler .secenek >> nth=0")
    s.click(".izah .nereden")
    s.wait_for_selector(".okuma h2")
    s.wait_for_timeout(600)
    ust = s.evaluate("() => document.querySelector('.okuma [data-baslik=\"%s\"]').getBoundingClientRect().top" % OKU_SORU["yer"])
    kontrol("konuda oku: '%s' başlığı ekranın üstünde" % OKU_SORU["yer"], -2 <= ust < 200, ust)

    # ---------------- 42 Tarzı: ders ve konu seçimi ----------------
    print("--- 42 Tarzı", flush=True)
    kart_top = sum(len(k["kartlar"]) for k in KONULAR_VT)
    GENEL = [d["id"] for g in next(r for r in YUK["agac"] if r["id"] == 1)["veri"]["gruplar"] if not g.get("hususi") for dn in g.get("donemler", [{"dersler": g.get("dersler", [])}]) for d in dn["dersler"]]
    hepsi_top = sum(len(k["kartlar"]) for k in YUK["konular"] if k["ders"] in GENEL)
    CIPLER = ["Hepsi"] + [d.get("kisa", d["ad"]) for g in next(r for r in YUK["agac"] if r["id"] == 1)["veri"]["gruplar"] if not g.get("hususi") for dn in g.get("donemler", []) for d in dn["dersler"] if any(k["ders"] == d["id"] for k in YUK["konular"])]
    s.click(".alt-cubuk button:has-text('42 Tarzı')")
    s.wait_for_selector("#sayfaKart .cip-satiri")
    kontrol("ders çipleri: " + " + ".join(CIPLER), s.locator("#sayfaKart .cip-satiri:not(.konu-ciplari) .cip").all_inner_texts() == CIPLER, s.locator("#sayfaKart .cip-satiri:not(.konu-ciplari) .cip").all_inner_texts())
    kontrol("Hepsi seçiliyken konu çipi yok", s.locator(".konu-ciplari").count() == 0)
    kontrol("Hepsi: %d kart" % hepsi_top, ("%d kartla çalış" % hepsi_top) in s.inner_text("#sayfaKart"))
    s.click("#sayfaKart .cip:text-is('Donanım')")
    s.wait_for_selector(".konu-ciplari")
    kontrol("konu çipleri: Bütün konular + %d konu" % len(KONULAR_VT), s.locator(".konu-ciplari .cip").count() == len(KONULAR_VT) + 1 and s.locator(".konu-ciplari .cip.secili").all_inner_texts() == ["Bütün konular"])
    k6, k7 = KONULAR_VT[1], KONULAR_VT[2]
    s.click(".konu-ciplari .cip:has-text('%s')" % k6["baslik"])
    kontrol("tek konu: %d kart" % len(k6["kartlar"]), ("%d kartla çalış" % len(k6["kartlar"])) in s.inner_text("#sayfaKart") and s.locator(".konu-ciplari .cip:has-text('Bütün konular').secili").count() == 0)
    s.click(".konu-ciplari .cip:has-text('%s')" % k7["baslik"])
    iki = len(k6["kartlar"]) + len(k7["kartlar"])
    kontrol("iki konu: %d kart, liste yalnızca o iki konu" % iki, ("%d kartla çalış" % iki) in s.inner_text("#sayfaKart") and s.locator("#sayfaKart .sonuc-kart").count() == iki)
    s.reload(); s.wait_for_selector(".alt-cubuk")
    s.click(".alt-cubuk button:has-text('42 Tarzı')"); s.wait_for_selector(".konu-ciplari")
    kontrol("seçim yenilemeden sonra duruyor", s.locator(".konu-ciplari .cip.secili").count() == 2 and ("%d kartla çalış" % iki) in s.inner_text("#sayfaKart"))
    s.click("text=/kartla çalış/")
    s.wait_for_selector(".deste .kart-yeri:not(.sonraki)")
    kontrol("deste başlığı 'Donanım · 2 konu'", s.inner_text(".ilerleme span >> nth=0") == "Donanım · 2 konu", s.inner_text(".ilerleme span >> nth=0"))
    s.click(".deste-eylem button:has-text('Cevabı göster')"); s.wait_for_timeout(700)
    s.screenshot(path="dn-kart-arka.png")
    s.click("text=‹ Geri") if s.locator("text=‹ Geri").count() else s.go_back()
    s.click(".alt-cubuk button:has-text('42 Tarzı')")
    s.wait_for_selector(".konu-ciplari")
    s.click(".konu-ciplari .cip:has-text('Bütün konular')")
    kontrol("Bütün konular: %d kart" % kart_top, ("%d kartla çalış" % kart_top) in s.inner_text("#sayfaKart") and s.locator(".konu-ciplari .cip.secili").all_inner_texts() == ["Bütün konular"])
    kontrol("depo temizlendi", s.evaluate("() => JSON.stringify(depo.oku('pg.kartKonular', {}))") == "{}")
    s.screenshot(path="dn-kart-sayfa.png", full_page=False)

    c.close()

hatali = [h for h in hatalar if "favicon" not in h]
kontrol("sayfa hatası yok", not hatali, hatali[:5])
print("\n%d/%d geçti" % (sum(1 for _, k in sonuclar if k), len(sonuclar)))
for a, k in sonuclar:
    if not k: print("  KALDI:", a)

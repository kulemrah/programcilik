"""Bütün dersler (hususi dahil) — her soru içerikteki cevapla doğru sayılmalı.
Eski başlık: Veritabanı içeriği — uygulamada uçtan uca deneme.
İçerik, gerçek aktarıcının sahte sunucuya yüklediği hâliyle (yuklenen.json + depo) kullanılır.
Hesabın hususi yetkisi yok: 42 grubu görünmemeli."""
exec(open("vt_taban.py", encoding="utf-8").read())

D["hususi"] = True
KONULAR_VT = YUK["konular"]
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
    c, s = cihaz_ac(p, "Q")
    giris(s)
    bekle_ki(s, lambda: s.locator(".ders-satiri:has-text('Born2beRoot') .durum").inner_text() != "yakında")
    s.click(".alt-cubuk button:has-text('Temrin')")
    s.evaluate("() => { derinlesGit(calisMenusuCiz); oturumBaslat(TUM_SORULAR.slice(), 'Hepsi'); }")
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
    c.close()
print("\ntum_sorular: %d/%d geçti" % (sum(1 for _, k in sonuclar if k), len(sonuclar)))

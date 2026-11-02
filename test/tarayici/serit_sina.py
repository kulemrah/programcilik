"""Yüzen şeritlerin altında düğme kalmaması.
İlk kullanımda "Ana ekrana ekle" şeridi alt çubuğun üstünde durur. Sayfanın alt
boşluğu şeridi hesaba katmazsa en alttaki düğmeler (konu seçimindeki "Tamam")
şeridin altında kalır, dokunulamaz ve temrine geçilemez. Burada şerit açıkken
en alta kaydırılıp düğmelerin gerçekten dokunulabilir olduğu denetlenir."""
exec(open("vt_taban.py", encoding="utf-8").read())

ALTA = "() => window.scrollTo(0, document.documentElement.scrollHeight)"
# Verilen düğme en alta kaydırılınca görünür ve üstünde hiçbir şey yok mu (şerit ve alt çubuğun üstünde mi)
USTTE_MI = """sec => { const d = Array.from(document.querySelectorAll(sec)).filter(e => e.offsetParent !== null).pop();
  if (!d) return 'yok';
  const b = d.getBoundingClientRect(), x = b.left + b.width / 2, y = b.top + b.height / 2;
  if (y < 0 || y > innerHeight) return 'ekran dışında: ' + Math.round(y);
  const e = document.elementFromPoint(x, y);
  return (e === d || d.contains(e)) ? '' : 'üstünde: ' + (e ? (e.className || e.tagName) + ' ' + e.textContent.slice(0, 20) : 'hiçbir şey'); }"""
BOSLUK = "() => getComputedStyle(document.body).paddingBottom"

def dokunulur(s, ad, sec):
    s.evaluate(ALTA); s.wait_for_timeout(150)
    sonuc = s.evaluate(USTTE_MI, sec)
    kontrol(ad, sonuc == "", sonuc)

with sync_playwright() as p:
    c, s = cihaz_ac(p, "S", kurulum_gizli=False)
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    kod_iste_ve_gir(s)
    s.wait_for_selector(".sozlesme")
    s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
    s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')")
    s.wait_for_selector(".kurulum", timeout=8000)
    kontrol("ilk kullanımda kurulum şeridi çıkar", s.locator(".kurulum").count() == 1)
    bekle_ki(s, lambda: s.evaluate("() => KONULAR.size") > 0)
    serit = s.evaluate("() => document.querySelector('.kurulum').offsetHeight")
    bosluk = s.evaluate(BOSLUK)
    kontrol("şerit varken alt boşluk şerit kadar büyür", bosluk == "%dpx" % (64 + serit + 16), (bosluk, serit))

    # --- Bildirilen hata: konu seçimi → Tamam → temrin yolları ---
    s.click(".alt-cubuk button:has-text('Temrin')")
    s.click("button:has-text('Ders ve konu seç')")
    s.wait_for_selector(".kontrol-oge")
    s.click(".kontrol-oge:has-text('Algoritma') button:not(.kutucuk)")
    s.wait_for_selector("button:has-text('‹ Dersler')")
    s.click(".kontrol .kontrol-oge >> nth=1"); s.click(".kontrol .kontrol-oge >> nth=2")
    dokunulur(s, "ders konuları: son konu şeridin altında değil", ".kontrol .kontrol-oge")
    s.click("button:has-text('‹ Dersler')")
    s.wait_for_selector("button:has-text('‹ Temrin yolları')")
    dokunulur(s, "konu seçimi: 'Tamam' şeridin altında değil", "#sayfaCalis .eylem button.ana")
    dokunulur(s, "konu seçimi: 'Seçimi temizle' şeridin altında değil", "#sayfaCalis .eylem button:not(.ana)")
    s.evaluate(ALTA); s.wait_for_timeout(150)
    # Gerçek dokunuş: düğmenin ortasındaki noktaya fareyle basılır (üstünde şerit varsa şeride gider)
    b = s.locator("#sayfaCalis .eylem button.ana").bounding_box()
    s.mouse.click(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
    try:
        s.wait_for_selector(".mod-kart", timeout=3000); gecti = True
    except Exception:
        gecti = False
    kontrol("'Tamam'a dokununca temrin yollarına geçilir", gecti)
    dokunulur(s, "temrin yolları: son yol şeridin altında değil", ".mod-kart")

    # --- Soru ekranı ---
    s.click(".mod-kart:has-text('Sınav provası')")
    s.wait_for_selector(".ilerleme")
    dokunulur(s, "soru ekranı: en alttaki düğme şeridin altında değil", "#sayfaCalis button")

    # --- 42 Tarzı ---
    s.click(".alt-cubuk button:has-text('42 Tarzı')")
    s.evaluate("() => { depo.yaz('pg.kartKapsam', Object.fromEntries(Array.from(DERS_KONULARI.keys()).map(d => [d, 'tumu']))); kartSayfasiCiz(); }")
    s.wait_for_selector("#sayfaKart button.ana")
    dokunulur(s, "42 Tarzı: 'Kartları liste hâlinde oku' şeridin altında değil", "#sayfaKart .eylem button:last-child")
    s.click("#sayfaKart button.ana")
    s.wait_for_selector("#sayfaKart .deste")
    s.wait_for_timeout(400)
    dokunulur(s, "42 Tarzı destesi: en alttaki düğme şeridin altında değil", "#sayfaKart button")

    # --- Oku: ders listesinin son satırı ---
    s.click(".alt-cubuk button:has-text('Kıraat')")
    s.wait_for_timeout(400)
    dokunulur(s, "Oku: son satır şeridin altında değil", "#sayfaOku button, #sayfaOku .ders-satiri")

    # --- Şerit büyüyünce (kurulum adımları) boşluk da büyür ---
    s.click(".kurulum button:has-text('Yükle')")
    s.wait_for_selector(".kurulum .adimlar")
    s.wait_for_timeout(200)
    serit2 = s.evaluate("() => document.querySelector('.kurulum').offsetHeight")
    bosluk2 = s.evaluate(BOSLUK)
    kontrol("kurulum adımları açılınca boşluk yeni yüksekliğe uyar", serit2 > serit and bosluk2 == "%dpx" % (64 + serit2 + 16), (bosluk2, serit2))

    # --- Şerit kapanınca boşluk eski hâline döner ---
    s.click(".kurulum button:has-text('Anladım')")
    s.wait_for_selector(".kurulum", state="detached")
    s.wait_for_timeout(100)
    kontrol("şerit kapanınca alt boşluk 64 px'e döner", s.evaluate(BOSLUK) == "64px", s.evaluate(BOSLUK))

    # --- Okuma çubuğu da aynı kurala uyar (gerçek ses gerekmeden çubuğun yerine geçen öğe) ---
    s.evaluate("() => { const d = document.createElement('div'); d.className = 'oynatma'; d.style.height = '90px'; document.body.appendChild(d); }")
    s.wait_for_timeout(100)
    kontrol("okuma çubuğu varken boşluk büyür", s.evaluate(BOSLUK) == "%dpx" % (64 + 90 + 16), s.evaluate(BOSLUK))
    s.evaluate("() => document.querySelector('.oynatma').remove()")
    s.wait_for_timeout(100)
    kontrol("okuma çubuğu kalkınca boşluk döner", s.evaluate(BOSLUK) == "64px", s.evaluate(BOSLUK))
    s.screenshot(path="serit-son.png")

kontrol("sayfa hatası yok", not hatalar, hatalar)
gecen = sum(1 for _, k in sonuclar if k)
print("\n%d/%d geçti" % (gecen, len(sonuclar)))
sys.exit(0 if gecen == len(sonuclar) else 1)

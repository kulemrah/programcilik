"""Takvim ileriki tarihlerde: bugünden başlayarak 2 yıl (730+ gün) boyunca her
gün için günlük ve haftalık takvim yeniden çizilir ve denetlenir:
- her hücre doğru haftanın gününde (satır = pazartesi..pazar),
- günler kesintisiz, tekrarsız, son hücre bugün,
- ay etiketleri o haftalarda gerçekten başlayan aylar,
- ay sınırı çizgisi görünen aralıkta ay değişiyorsa var.
Artık yıl (29 Şubat 2028) ve yaz saati uygulayan bir saat dilimi de denenir."""
exec(open("vt_taban.py", encoding="utf-8").read())
import datetime as dt, os, sys
D["hususi"] = True
TZ = os.environ.get("TZ_ADI", "Europe/Istanbul")

DENETLE = r"""async ([basYil, basAy, basGun, gunSayisi]) => {
  const asil = Date.now;
  const hatalar = []; let denenen = 0; const ornek = {};
  const ist = istatistikTopla(null);
  const AYLAR = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];
  try {
    for (let i = 0; i < gunSayisi; i++) {
      const t = new Date(basYil, basAy - 1, basGun + i, 12, 0, 0).getTime();
      Date.now = () => t;
      const bugun = new Date(t);
      const bugunAnahtar = bugun.getFullYear() + "-" + String(bugun.getMonth() + 1).padStart(2, "0") + "-" + String(bugun.getDate()).padStart(2, "0");
      for (const tur of ["gun", "hafta"]) {
        const kart = tur === "gun" ? takvimBolumu(ist) : haftaTakvimiBolumu(ist);
        const svg = kart.querySelector("svg");
        const hucreler = [...svg.querySelectorAll("rect.hucre")];
        const etiketler = [...svg.querySelectorAll("text.eksen-yazi")].map(x => x.textContent).filter(x => !["Pzt","Çar","Cum","Paz"].includes(x));
        const sinirVar = !!svg.querySelector(".ay-siniri");
        if (tur === "gun") {
          const gunler = hucreler.map(h => h.dataset.gun);
          if (gunler[gunler.length - 1] !== bugunAnahtar) hatalar.push(bugunAnahtar + " son hücre " + gunler[gunler.length - 1]);
          if (new Set(gunler).size !== gunler.length) hatalar.push(bugunAnahtar + " tekrar eden gün");
          const yler = [...new Set(hucreler.map(h => Number(h.getAttribute("y"))))].sort((a, b) => a - b);
          for (let k = 0; k < gunler.length; k++) {
            const d = new Date(gunler[k] + "T12:00:00");
            const satir = yler.indexOf(Number(hucreler[k].getAttribute("y")));
            if ((d.getDay() + 6) % 7 !== satir) { hatalar.push(bugunAnahtar + " " + gunler[k] + " yanlış satır " + satir); break; }
            if (k > 0) {
              const once = new Date(gunler[k - 1] + "T12:00:00");
              if (Math.round((d - once) / 864e5) !== 1) { hatalar.push(bugunAnahtar + " kesinti " + gunler[k - 1] + "→" + gunler[k]); break; }
            }
          }
          if (new Date(gunler[0] + "T12:00:00").getDay() !== 1) hatalar.push(bugunAnahtar + " ilk hücre pazartesi değil " + gunler[0]);
          /* Görünen aralıkta başlayan aylar (1. günü görünen) etiketlerde olmalı (çok yakın ikisi hariç tutulabilir) */
          const ayBaslari = gunler.filter(g => g.endsWith("-01")).map(g => AYLAR[Number(g.slice(5, 7)) - 1]);
          const eksik = ayBaslari.slice(1).filter(a => !etiketler.includes(a));
          if (eksik.length) hatalar.push(bugunAnahtar + " eksik ay etiketi " + eksik.join(",") + " / " + etiketler.join(","));
          const fazla = etiketler.filter(e => !ayBaslari.includes(e) && e !== AYLAR[Number(gunler[0].slice(5, 7)) - 1]);
          if (fazla.length) hatalar.push(bugunAnahtar + " fazla ay etiketi " + fazla.join(","));
          const ayDegisir = new Set(gunler.map(g => g.slice(0, 7))).size > 1;
          if (ayDegisir !== sinirVar) hatalar.push(bugunAnahtar + " ay sınırı çizgisi " + sinirVar + " beklenen " + ayDegisir);
          if (["2028-02-29", "2028-03-01", "2027-01-01", "2026-12-31"].includes(bugunAnahtar)) ornek[bugunAnahtar] = { son: gunler.slice(-3), etiketler };
        } else {
          if (hucreler.length !== TAKVIM_HAFTA) hatalar.push(bugunAnahtar + " haftalık hücre sayısı " + hucreler.length);
          if (!hucreler[hucreler.length - 1].classList.contains("bugun")) hatalar.push(bugunAnahtar + " haftalıkta bu hafta işaretli değil");
        }
      }
      denenen++;
    }
  } finally { Date.now = asil; }
  return { denenen, hatalar: hatalar.slice(0, 20), hataSayisi: hatalar.length, ornek, hafta: TAKVIM_HAFTA };
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for genislik in (390, 1100):
        time.sleep(SUNUCU_KOD_ARALIGI)
        D["profil"] = None; D["yerler"].clear(); D["oturumlar"].clear()
        c = b.new_context(service_workers="block", viewport={"width": genislik, "height": 820}, timezone_id=TZ, locale="tr-TR")
        c.add_init_script("try { localStorage.setItem('pg.kurulum', JSON.stringify('gizli')) } catch (e) {}")
        c.route(SUPA + "/**", isle)
        s = c.new_page()
        s.on("pageerror", lambda e: hatalar.append("pageerror: " + str(e)))
        s.goto(KOK); s.wait_for_selector(".giris-perde"); kod_iste_ve_gir(s)
        s.wait_for_selector(".sozlesme"); s.click("text=Okudum, kabul ediyorum"); s.click("button:has-text('Kabul et ve devam et')")
        s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')"); s.wait_for_selector(".grup-baslik")
        cekmece(s, "takvim")
        bugun = dt.date.today()
        r = s.evaluate(DENETLE, [bugun.year, bugun.month, bugun.day, 800])
        kontrol("%s, %dpx: %d gün (%d hafta) boyunca takvim hatasız" % (TZ, genislik, r["denenen"], r["hafta"]), r["hataSayisi"] == 0, r["hatalar"])
        o = r["ornek"]
        kontrol("29 Şubat 2028 takvimde (artık yıl)", o.get("2028-02-29", {}).get("son", [None])[-1] == "2028-02-29", o.get("2028-02-29"))
        kontrol("1 Mart 2028'den önceki gün 29 Şubat", o.get("2028-03-01", {}).get("son", [])[-2:] == ["2028-02-29", "2028-03-01"], o.get("2028-03-01"))
        kontrol("yılbaşı: 31 Aralık 2026 → 1 Ocak 2027", o.get("2027-01-01", {}).get("son", [])[-2:] == ["2026-12-31", "2027-01-01"] and "Oca" in o.get("2027-01-01", {}).get("etiketler", []), o.get("2027-01-01"))
        c.close()
    print("hatalar:", hatalar[:5])

gecen = sum(1 for _, k in sonuclar if k)
print("SONUÇ: %d/%d" % (gecen, len(sonuclar)))

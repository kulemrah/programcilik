"""Bütün dersler — telefon genişliğinde (358 px) taşma ve çizim denetimi.
Her konu açılır: sayfa yatay kaymamalı, kaydırma kabı dışında hiçbir öğe okuma
alanından taşmamalı, bütün görseller yüklenmeli, başlıklar birebir çizilmeli.
Ayrıca her konunun her sorusu tek tek çizilir ve taşma aranır."""
exec(open("vt_taban.py", encoding="utf-8").read())
D["hususi"] = True

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

TASMA_JS = """(kapSec) => {
  const sonuc = [];
  const sayfaGenis = document.documentElement.scrollWidth, ekran = window.innerWidth;
  if (sayfaGenis > ekran + 1) sonuc.push('sayfa yatay kayıyor: ' + sayfaGenis + ' > ' + ekran);
  const kap = document.querySelector(kapSec);
  if (!kap) return ['kap yok: ' + kapSec];
  const kr = kap.getBoundingClientRect();
  const kaydirilir = e => { for (let x = e; x && x !== kap; x = x.parentElement) {
      const st = getComputedStyle(x); if (/(auto|scroll)/.test(st.overflowX) && x.scrollWidth > x.clientWidth - 1) return true;
      if (/(auto|scroll|hidden)/.test(st.overflowX) && x !== e) return true; } return false; };
  kap.querySelectorAll('*').forEach(e => {
    const r = e.getBoundingClientRect();
    /* .geri: '‹' işaretini hizalamak için bilinçli margin-left:-2px (taşma değil) */
    if (!r.width || !r.height || e.closest('.muhim-dugme') || e.closest('.geri')) return;
    if ((r.right > kr.right + 1 || r.left < kr.left - 1) && !kaydirilir(e)) {
      sonuc.push((e.tagName + '.' + e.className).slice(0, 40) + ' taşıyor (' + Math.round(r.left) + '..' + Math.round(r.right) + ' / ' + Math.round(kr.left) + '..' + Math.round(kr.right) + '): ' + (e.textContent || '').trim().slice(0, 50));
    }
  });
  return sonuc.slice(0, 6);
}"""

with sync_playwright() as p:
    c, s = cihaz_ac(p, "T")
    import os; s.set_viewport_size({"width": int(os.environ.get("GENISLIK", "358")), "height": 760})
    giris(s)
    for ders in ["algoritma", "veritabani", "ekoloji", "born2beroot", "elektrik"]:
        bekle_ki(s, lambda: True)
        konular = sorted([k for k in YUK["konular"] if k["ders"] == ders], key=lambda k: k["sira"])
        ad = next(d["kisa"] if d.get("kisa") else d["ad"] for g in json.load(open("/home/claude/programcilik/icerik/agac.json"))["gruplar"]
                  for d in ([x for dn in g.get("donemler", []) for x in dn["dersler"]] + g.get("dersler", [])) if d["id"] == ders)
        s.click(".alt-cubuk button >> nth=0")
        s.wait_for_selector(".grup-baslik")
        bekle_ki(s, lambda: s.locator(".ders-satiri:has-text('%s') .durum" % ad).inner_text() != "yakında")
        s.click(".ders-satiri:has-text('%s')" % ad)
        s.wait_for_selector(".agac .dal")
        for i, k in enumerate(konular):
            s.click(".agac .dal >> nth=%d" % i)
            s.wait_for_selector(".okuma h2")
            gorsel = len(re.findall(r"^!\[", k["metin"], re.M))
            if gorsel:
                try:
                    s.wait_for_function("n => { const g = Array.from(document.querySelectorAll('.okuma figure img'));"
                                        " return g.length === n && g.every(i => i.complete && i.naturalWidth > 0) }", arg=gorsel, timeout=8000)
                except Exception:
                    kontrol(k["id"] + ": görseller yüklendi", False)
            cizilen = s.locator(".okuma [data-baslik]").evaluate_all("els => els.map(e => e.dataset.baslik)")
            kontrol(k["id"] + ": başlıklar birebir", cizilen == md_basliklari(k["metin"]), cizilen)
            tasma = s.evaluate(TASMA_JS, ".okuma")
            kontrol(k["id"] + ": okumada taşma yok", not tasma, tasma)
            s.click("text=‹ Geri")
            s.wait_for_selector(".agac .dal")

    # ---------------- Her soru tek tek: çizim ve cevap sonrası taşma ----------------
    s.evaluate("() => sekmeAc('calis', false)")
    kimlikler = [x["id"] for k in YUK["konular"] for x in k["sorular"]]
    kalan = []
    for sid in kimlikler:
        r = s.evaluate("""(id) => { const q = SORU_HARITASI.get(id); if (!q) return 'yok';
            oturumBaslat([q], 'T'); return q.tip; }""", sid)
        if r == "yok": kalan.append(sid + ": uygulamada yok"); continue
        t = s.evaluate(TASMA_JS, "#sayfaCalis")
        if t: kalan.append(sid + " (çizim): " + "; ".join(t))
        # cevapla: seçmede ilk şık, D/Y'de Doğru, diğerlerinde kontrol/göster düğmesi
        s.evaluate("""() => { const p = document.querySelector('#sayfaCalis');
            const b = p.querySelector('.secenekler .secenek, .dy-dugmeler .secenek') || p.querySelector('.eylem .ana');
            if (b) b.click(); const k = p.querySelector('.oz-puan button'); if (k) k.click(); }""")
        t = s.evaluate(TASMA_JS, "#sayfaCalis")
        if t: kalan.append(sid + " (cevap): " + "; ".join(t))
    kontrol("%d sorunun hiçbiri taşmıyor" % len(kimlikler), not kalan, "\n".join(kalan[:20]))

    # ---------------- Kartlar: liste ve deste (iki yüz) ----------------
    s.evaluate("() => { depo.yaz('pg.kartKapsam', Object.fromEntries(Array.from(DERS_KONULARI.keys()).map(d => [d, 'tumu']))); sekmeAc('kart', false); kartListesiCiz(); }")
    t = s.evaluate(TASMA_JS, "#sayfaKart")
    kontrol("kart listesi (%d kart) taşmıyor" % s.evaluate("() => TUM_KARTLAR.length"), not t, t)
    kalan = []
    for kid in [x["id"] for k in YUK["konular"] for x in k["kartlar"]]:
        s.evaluate("""(id) => { const k = TUM_KARTLAR.find(x => x.id === id);
            kartOturumu([k], 'T', document.querySelector('#sayfaKart'), {}); }""", kid)
        t = s.evaluate(TASMA_JS, "#sayfaKart")
        if t: kalan.append(kid + " (ön): " + "; ".join(t))
        s.evaluate("() => document.querySelector('#sayfaKart .deste-eylem .ana').click()")
        s.wait_for_timeout(30)
        t = s.evaluate("""() => { const a = document.querySelector('#sayfaKart .kart-yuz.arka .icerik');
            const r = []; a.querySelectorAll('*').forEach(e => { const st = getComputedStyle(e);
              if (e.scrollWidth > e.clientWidth + 1 && !/(auto|scroll)/.test(st.overflowX) && !e.closest('pre')) r.push(e.tagName + ': ' + e.textContent.slice(0, 40)); });
            if (a.scrollWidth > a.clientWidth + 1) r.push('arka yüz yatay taşıyor');
            return r.slice(0, 4); }""")
        if t: kalan.append(kid + " (arka): " + "; ".join(t))
    kontrol("kartların iki yüzü de taşmıyor", not kalan, "\n".join(kalan[:20]))
    c.close()

gecen = sum(1 for _, k in sonuclar if k)
print("\ntasma_sina: %d/%d geçti" % (gecen, len(sonuclar)))

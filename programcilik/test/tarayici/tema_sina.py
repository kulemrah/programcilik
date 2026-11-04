"""Tema: ilk açılış açık, düğme açık→koyu→simsiyah→açık döner, seçim yeniden açılışta kalır."""
exec(open("vt_taban.py", encoding="utf-8").read())
with sync_playwright() as p:
    c, s = cihaz_ac(p, "T")
    s.set_viewport_size({"width": 320, "height": 700})
    s.goto(KOK); s.wait_for_selector(".giris-perde")
    mod = lambda: s.evaluate("document.documentElement.dataset.mod")
    renk = lambda: s.evaluate("document.querySelector('meta[name=theme-color]').content")
    zemin = lambda: s.evaluate("getComputedStyle(document.body).getPropertyValue('--zemin').trim()")
    kontrol("ilk açılış açık tema", mod() == "gunduz" and renk() == "#F2F2F7" and zemin() == "#F2F2F7", (mod(), renk(), zemin()))
    s.evaluate("() => document.querySelector('.giris-perde').style.display='none'")
    beklenen = ["pembe", "gece", "siyah", "gunduz", "pembe"]
    renkler = {"gece": "#121214", "siyah": "#000000", "gunduz": "#F2F2F7", "pembe": "#FBF2F6"}
    for b in beklenen:
        s.click("#modDugme")
        kontrol("düğme → " + b, mod() == b and renk() == renkler[b] and zemin() == renkler[b], (mod(), renk(), zemin()))
    s.reload(); s.wait_for_selector(".giris-perde")
    kontrol("seçim yeniden açılışta kalır (pembe)", mod() == "pembe", mod())
    s.evaluate("() => localStorage.setItem('pg.mod', JSON.stringify('siyah'))")
    s.reload(); s.wait_for_selector(".giris-perde")
    kontrol("kayıtlı simsiyah açılır", mod() == "siyah", mod())
    s.evaluate("() => localStorage.setItem('pg.mod', JSON.stringify('bozuk'))")
    s.reload(); s.wait_for_selector(".giris-perde")
    kontrol("bilinmeyen değer → açık", mod() == "gunduz", mod())
    kontrol("hata yok", not hatalar, hatalar[:3])
    s.screenshot(path="goruntu/320-giris.png")
print(sum(1 for _, k in sonuclar if k), "/", len(sonuclar))

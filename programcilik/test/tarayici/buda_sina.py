"""Görsel budaması: hiçbir konunun kullanmadığı önbellek görseli silinir, kullanılanlar kalır."""
exec(open("vt_taban.py", encoding="utf-8").read())
D["hususi"] = True
def giris(s):
    s.goto(KOK); s.wait_for_selector(".giris-perde"); s.fill("#girisEposta", EPOSTA)
    s.click("button:has-text('Kod gönder')"); s.wait_for_selector("#girisKod"); s.fill("#girisKod", "123456")
    s.click("button:has-text('Giriş yap')"); s.wait_for_selector(".sozlesme"); s.click("text=Okudum, kabul ediyorum")
    s.click("button:has-text('Kabul et ve devam et')"); s.wait_for_selector(".not-perde"); s.click("button:has-text('Anladım')")
    s.wait_for_selector(".grup-baslik")
with sync_playwright() as p:
    c, s = cihaz_ac(p, "G")
    giris(s)
    bekle_ki(s, lambda: s.locator(".ders-satiri:has-text('Ekoloji') .durum").inner_text() != "yakında")
    s.click(".ders-satiri:has-text('Ekoloji')"); s.wait_for_selector(".agac .dal")
    s.click(".agac .dal >> nth=0"); s.wait_for_selector(".okuma h2")
    s.wait_for_function("() => Array.from(document.querySelectorAll('.okuma figure img')).every(i => i.complete && i.naturalWidth > 0)")
    # Arka plandaki ön indirme (bütün kullanılan görseller) bitsin; sonra budama denenir
    import re as _re
    KULLANILAN = len({k["ders"] + "/" + m for k in YUK["konular"] for m in _re.findall(r"gorseller/([^)\s]+)", k.get("metin", ""))})
    bekle_ki(s, lambda: s.evaluate("async () => !gorselIndirmeSuruyor && (await vt.hepsi('gorsel')).length") == KULLANILAN, 30)
    once = s.evaluate("async () => (await vt.hepsi('gorsel')).map(g => g.yol)")
    s.evaluate("async () => { await vt.yaz('gorsel', { yol: 'ekoloji/0000000000-eski.svg', blob: new Blob(['x']) }); await vt.yaz('gorsel', { yol: 'yokders/1111111111-a.svg', blob: new Blob(['x']) }); }")
    s.evaluate("async () => { await gorselleriBuda(oturumNesli); }")
    sonra = s.evaluate("async () => (await vt.hepsi('gorsel')).map(g => g.yol)")
    kontrol("eski adlı ve dersi kalkmış görsel silindi", "ekoloji/0000000000-eski.svg" not in sonra and "yokders/1111111111-a.svg" not in sonra, sonra)
    kontrol("kullanılan %d görsel yerinde" % len(once), sorted(once) == sorted(sonra) and len(once) > 0, (once, sonra))
    c.close()
print("\nbuda_sina: %d/%d geçti" % (sum(1 for _, k in sonuclar if k), len(sonuclar)))

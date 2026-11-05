"""İçerik aktarıcısını gerçek Supabase yerine bu sunucuya yükletir; yüklenenleri diske yazar.
Kullanım: python3 sahte_supa.py <çıktı klasörü> <port>"""
import json, os, sys, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
CIKTI, PORT = sys.argv[1], int(sys.argv[2])
os.makedirs(os.path.join(CIKTI, "depo"), exist_ok=True)
KONULAR, AGAC, PROGRAMLAR = {}, {}, {}
def kaydet():
    json.dump({"konular": list(KONULAR.values()), "agac": list(AGAC.values()), "programlar": list(PROGRAMLAR.values())},
              open(os.path.join(CIKTI, "yuklenen.json"), "w"), ensure_ascii=False)
class Isleyici(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def cevap(self, kod, govde=None):
        b = b"" if govde is None else json.dumps(govde).encode()
        self.send_response(kod); self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        yol = urllib.parse.urlparse(self.path).path
        if yol == "/rest/v1/konular": return self.cevap(200, [{"id": k["id"], "ozet": k["ozet"], "programlar": k.get("programlar"), "sinif": k.get("sinif")} for k in KONULAR.values()])
        if yol == "/rest/v1/agac": return self.cevap(200, [{"id": a["id"], "ozet": a["ozet"]} for a in AGAC.values()])
        self.cevap(404, {"message": "yok"})
    def do_POST(self):
        u = urllib.parse.urlparse(self.path); yol = u.path
        govde = self.rfile.read(int(self.headers.get("content-length", 0)))
        if yol.startswith("/storage/v1/object/gorseller/"):
            ad = urllib.parse.unquote(yol[len("/storage/v1/object/gorseller/"):])
            hedef = os.path.join(CIKTI, "depo", ad); os.makedirs(os.path.dirname(hedef), exist_ok=True)
            open(hedef, "wb").write(govde); return self.cevap(200, {"Key": ad})
        if yol == "/rest/v1/konular":
            for r in json.loads(govde): KONULAR[r["id"]] = r
            kaydet(); return self.cevap(201)
        if yol == "/rest/v1/agac":
            for r in json.loads(govde): AGAC[r["id"]] = r
            kaydet(); return self.cevap(201)
        if yol == "/rest/v1/programlar":
            for r in json.loads(govde): PROGRAMLAR[r["id"]] = r
            kaydet(); return self.cevap(201)
        self.cevap(404, {"message": "yok"})
    def do_DELETE(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        if u.path == "/rest/v1/agac" and q.get("id", [""])[0].startswith("eq."):
            AGAC.pop(q["id"][0][3:], None); kaydet()
        self.cevap(204)
ThreadingHTTPServer(("127.0.0.1", PORT), Isleyici).serve_forever()

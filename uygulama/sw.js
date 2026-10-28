/* Programcılık — çevrimdışı çalışma katmanı
   Yalnızca uygulamanın kendi dosyaları önbelleğe alınır. Supabase istekleri
   (notlar, giriş, kayıtlar) başka adrese gittiği için buradan hiç geçmez;
   notların çevrimdışı kopyasını uygulama kendisi IndexedDB'de tutar. */
const ON_EK = "programcilik-";
const ONBELLEK = ON_EK + "v8";
const KABUK = new URL("./", self.registration.scope).href;
const DOSYALAR = [
  "./",
  "./manifest.webmanifest",
  "./supabase.js?v=2.117.2",
  "./ikon-192.png",
  "./ikon-512.png",
  "./ikon-maskable-512.png",
  "./apple-touch-icon.png"
];
/* Ağ bu sürede cevap vermezse önbellekteki sürüm açılır */
const AG_SURESI = 4000;

self.addEventListener("install", olay => {
  olay.waitUntil(
    caches.open(ONBELLEK)
      /* cache: "reload": tarayıcının HTTP önbelleğindeki eski kopya alınmasın
         (GitHub Pages dosyaları 10 dakika önbelleklenebilir der) */
      .then(o => o.addAll(DOSYALAR.map(d => new Request(d, { cache: "reload" }))))
      .then(() => self.skipWaiting())
  );
});

/* Eski sürüm önbelleklerini temizle. Önbellek alanı bütün siteyle (aynı
   github.io adresindeki öbür uygulamalarla) ortaktır: yalnızca bu
   uygulamanın adıyla başlayanlara dokunulur. */
self.addEventListener("activate", olay => {
  olay.waitUntil(
    caches.keys()
      .then(adlar => Promise.all(adlar.filter(a => a.startsWith(ON_EK) && a !== ONBELLEK).map(a => caches.delete(a))))
      .then(() => self.clients.claim())
  );
});

/* Gelen sayfa gerçekten bu uygulama mı? Okul ya da kafe Wi-Fi'sinin giriş
   sayfası da 200 döner; onu uygulamanın yerine kaydetmemek gerekir. */
async function kabukMu(cevap) {
  if (!cevap || !cevap.ok || cevap.redirected || cevap.type !== "basic") return false;
  if ((cevap.headers.get("content-type") || "").indexOf("text/html") === -1) return false;
  try { return (await cevap.clone().text()).indexOf('name="programcilik-kabuk"') !== -1; }
  catch (e) { return false; }
}

async function kabuguKaydet(cevap) {
  if (await kabukMu(cevap)) {
    const o = await caches.open(ONBELLEK);
    await o.put(KABUK, cevap.clone());
  }
}

/* Sayfanın kendisi: önce ağ (yeni sürüm hemen gelsin), ağ yavaşsa ya da
   yoksa önbellek. Ağ geç de olsa cevap verirse önbellek tazelenir. */
function sayfaGetir(olay) {
  const agdan = fetch(olay.request);
  /* Kopya hemen alınır: sayfa gövdeyi okumaya başlamadan önce */
  olay.waitUntil(agdan.then(c => kabuguKaydet(c.clone())).catch(() => {}));
  const zamanAsimi = new Promise(coz => setTimeout(coz, AG_SURESI, null));
  return Promise.race([agdan.catch(() => null), zamanAsimi]).then(async cevap => {
    if (cevap && cevap.ok) return cevap;
    const kayitli = await caches.match(KABUK);
    if (kayitli) return kayitli;
    /* Önbellek de boşsa ağı sonuna kadar bekle */
    return cevap || agdan;
  });
}

self.addEventListener("fetch", olay => {
  const istek = olay.request;
  if (istek.method !== "GET" || new URL(istek.url).origin !== self.location.origin) return;

  if (istek.mode === "navigate") {
    olay.respondWith(sayfaGetir(olay));
    return;
  }

  /* Diğer dosyalar: önce önbellek, arka planda tazele */
  olay.respondWith(
    caches.match(istek).then(bulunan => {
      const agdan = fetch(istek);
      /* Önbelleğe yazım da beklenir; yoksa tarayıcı işçiyi yazım bitmeden durdurabilir */
      const kaydet = agdan.then(async cevap => {
        if (cevap && cevap.ok && cevap.type === "basic") {
          /* Kopya hemen alınır: sayfa gövdeyi okumaya başlamadan önce */
          const kopya = cevap.clone();
          const o = await caches.open(ONBELLEK);
          await o.put(istek, kopya);
        }
      }).catch(() => {});
      olay.waitUntil(kaydet);
      return bulunan || agdan;
    })
  );
});

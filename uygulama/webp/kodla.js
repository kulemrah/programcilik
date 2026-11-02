/* WebP kodlayıcı (yalnızca tarayıcısı canvas ile WebP üretemeyenler için; ör. iPhone Safari).
   Kaynak: @jsquash/webp 1.4.0 (Apache-2.0, LICENSE) — libwebp'in WebAssembly derlemesi.
   SIMD'siz sürüm kullanılır: her tarayıcıda çalışır, ayrıca özellik denetimi gerekmez.
   Kullanım: const kodla = (await import("./webp/kodla.js")).default;
             const arabellek = await kodla(imageData, 80);   // kalite 0–100 */
import { defaultOptions } from "./meta.js";
import { initEmscriptenModule } from "./utils.js";
import webpKodlayici from "./webp_enc.js";

let modul = null;
export default async function kodla(veri, kalite) {
  if (!modul) modul = initEmscriptenModule(webpKodlayici);
  const m = await modul;
  const sonuc = m.encode(veri.data, veri.width, veri.height, { ...defaultOptions, quality: kalite });
  if (!sonuc) throw new Error("WebP kodlanamadı");
  return sonuc.buffer;
}

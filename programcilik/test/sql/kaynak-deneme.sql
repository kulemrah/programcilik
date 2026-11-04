-- Kaynak bölümünün (01-sema.sql, 8. bölüm) yerel denemesi.
-- Çalıştırma: test/sql/calistir.sh  (Supabase taklidi + şema + bu dosya)
-- Her denetim başarısızsa "KALDI" ile hata verir; hepsi geçerse "KAYNAK SQL: TAMAM".
\set ON_ERROR_STOP 1
set client_min_messages = warning;

-- İki öğrenci (A, B) ve okul dışı biri (C); A ve B'nin cihaz yeri ve sözleşmesi var
insert into auth.users values
  ('aaaaaaaa-0000-0000-0000-000000000001', 'a@kocaelisaglik.edu.tr', now(), null),
  ('bbbbbbbb-0000-0000-0000-000000000002', 'b@kocaelisaglik.edu.tr', now(), null),
  ('cccccccc-0000-0000-0000-000000000003', 'c@gmail.com', now(), null);
insert into auth.sessions values
  ('aaaaaaaa-1111-0000-0000-000000000001', 'aaaaaaaa-0000-0000-0000-000000000001', 'test'),
  ('bbbbbbbb-1111-0000-0000-000000000002', 'bbbbbbbb-0000-0000-0000-000000000002', 'test');
insert into public.hesap_cihazlari (kullanici, eposta) values
  ('aaaaaaaa-0000-0000-0000-000000000001', 'a@kocaelisaglik.edu.tr'),
  ('bbbbbbbb-0000-0000-0000-000000000002', 'b@kocaelisaglik.edu.tr');
insert into public.cihaz_yerleri (kullanici, oturum) values
  ('aaaaaaaa-0000-0000-0000-000000000001', 'aaaaaaaa-1111-0000-0000-000000000001'),
  ('bbbbbbbb-0000-0000-0000-000000000002', 'bbbbbbbb-1111-0000-0000-000000000002');
insert into public.profiller (kullanici, program, sinif, sozlesme_surumu) values
  ('aaaaaaaa-0000-0000-0000-000000000001', 'bilgisayar-programciligi', 1, '2'),
  ('bbbbbbbb-0000-0000-0000-000000000002', 'bilgisayar-programciligi', 1, '2');

create or replace function pg_temp.denetle(ad text, kosul boolean) returns void language plpgsql as $$
begin
  if not coalesce(kosul, false) then raise exception 'KALDI: %', ad; end if;
  raise notice 'GEÇTİ: %', ad;
end $$;
-- Beklenen hata: verilen SQL hata vermeli ve mesajı "parca" içermeli
create or replace function pg_temp.hata_beklenir(ad text, komut text, parca text) returns void language plpgsql as $$
begin
  execute komut;
  raise exception 'KALDI (hata vermedi): %', ad;
exception when others then
  if sqlerrm like 'KALDI%' then raise; end if;
  if position(parca in sqlerrm) = 0 then raise exception 'KALDI: % — beklenmeyen hata: %', ad, sqlerrm; end if;
  raise notice 'GEÇTİ: % (%)', ad, sqlerrm;
end $$;
set client_min_messages = notice;

-- ===== A olarak =====
set role authenticated;
select set_config('request.jwt.claims', '{"sub":"aaaaaaaa-0000-0000-0000-000000000001","session_id":"aaaaaaaa-1111-0000-0000-000000000001","role":"authenticated"}', false);

select pg_temp.denetle('A üye', public.uye());
select pg_temp.denetle('kaynak_durum: izin, 100 MB, 0 kullanılan',
  (select (d->>'izin')::boolean and (d->>'azami_bayt')::bigint = 104857600 and (d->>'kullanilan_bayt')::bigint = 0 from public.kaynak_durum() d));

insert into public.kaynak_tasnif (id, ad) values ('a0000000-0000-0000-0000-00000000000a', 'Algoritma');
insert into public.kaynak_tasnif (id, ust, ad) values ('a0000000-0000-0000-0000-00000000000b', 'a0000000-0000-0000-0000-00000000000a', '3. hafta');
insert into public.kaynak_tasnif (id, ust, ad) values ('a0000000-0000-0000-0000-00000000000c', 'a0000000-0000-0000-0000-00000000000b', 'Tahta');
select pg_temp.denetle('kademeler 1-2-3',
  (select array_agg(derinlik order by derinlik) = '{1,2,3}' from public.kaynak_tasnif));
select pg_temp.hata_beklenir('4. kademe açılamaz',
  $$insert into public.kaynak_tasnif (ust, ad) values ('a0000000-0000-0000-0000-00000000000c', 'Dördüncü')$$, 'en çok üç kademe');
select pg_temp.hata_beklenir('kademe elle 1 yazılsa da hesaplanır (yine engellenir)',
  $$insert into public.kaynak_tasnif (ust, ad, derinlik) values ('a0000000-0000-0000-0000-00000000000c', 'Hile', 1)$$, 'en çok üç kademe');
select pg_temp.hata_beklenir('boş ad olmaz',
  $$insert into public.kaynak_tasnif (ad) values ('   ')$$, 'check');

update public.kaynak_tasnif set ad = 'Algoritma ve Programlama' where id = 'a0000000-0000-0000-0000-00000000000a';
select pg_temp.denetle('ad değişir', (select ad = 'Algoritma ve Programlama' from public.kaynak_tasnif where id = 'a0000000-0000-0000-0000-00000000000a'));
select pg_temp.hata_beklenir('üst tasnif değiştirilemez (sütun izni yok)',
  $$update public.kaynak_tasnif set ust = null where id = 'a0000000-0000-0000-0000-00000000000c'$$, 'permission denied');

insert into public.kaynak_oge (id, tasnif, tur, metin) values ('a1000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-00000000000b', 'not', 'Hoca: sınavda akış şeması çıkar dedi.');
update public.kaynak_oge set metin = 'Düzeltildi' where id = 'a1000000-0000-0000-0000-000000000001';
select pg_temp.denetle('not eklenir ve düzenlenir', (select metin = 'Düzeltildi' from public.kaynak_oge where id = 'a1000000-0000-0000-0000-000000000001'));
select pg_temp.hata_beklenir('uygulama resim satırı ekleyemez',
  $$insert into public.kaynak_oge (tasnif, tur, bayt) values ('a0000000-0000-0000-0000-00000000000b', 'resim', 10)$$, 'row-level security');
select pg_temp.hata_beklenir('bayt sütunu değiştirilemez',
  $$update public.kaynak_oge set bayt = 1 where id = 'a1000000-0000-0000-0000-000000000001'$$, 'permission denied');
select pg_temp.hata_beklenir('Worker işlevleri öğrenciye kapalı',
  $$select public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', gen_random_uuid(), 'a0000000-0000-0000-0000-00000000000b', 10, 1, 1)$$, 'permission denied');
select pg_temp.hata_beklenir('kota tablosu öğrenciye kapalı',
  $$update public.kaynak_kota set azami_mb = 9999$$, 'permission denied');

-- ===== B olarak: A'nın hiçbir şeyini göremez, A'nın tasnifine yazamaz =====
select set_config('request.jwt.claims', '{"sub":"bbbbbbbb-0000-0000-0000-000000000002","session_id":"bbbbbbbb-1111-0000-0000-000000000002","role":"authenticated"}', false);
select pg_temp.denetle('B, A''nın tasniflerini görmez', (select count(*) = 0 from public.kaynak_tasnif));
select pg_temp.denetle('B, A''nın notunu görmez', (select count(*) = 0 from public.kaynak_oge));
select pg_temp.hata_beklenir('B, A''nın tasnifinin altına tasnif açamaz',
  $$insert into public.kaynak_tasnif (ust, ad) values ('a0000000-0000-0000-0000-00000000000a', 'Sızma')$$, 'Üst tasnif bulunamadı');
select pg_temp.hata_beklenir('B, A''nın tasnifine not koyamaz',
  $$insert into public.kaynak_oge (tasnif, tur, metin) values ('a0000000-0000-0000-0000-00000000000a', 'not', 'x')$$, 'Tasnif bulunamadı');
update public.kaynak_oge set metin = 'B yazdı' where id = 'a1000000-0000-0000-0000-000000000001';
delete from public.kaynak_oge where id = 'a1000000-0000-0000-0000-000000000001';
select pg_temp.hata_beklenir('B, A''nın tasnifini silemez',
  $$select public.kaynak_tasnif_sil('a0000000-0000-0000-0000-00000000000a')$$, 'Tasnif bulunamadı');

-- ===== Okul dışı ve cihazı devredilmiş oturum =====
select set_config('request.jwt.claims', '{"sub":"cccccccc-0000-0000-0000-000000000003","role":"authenticated"}', false);
select pg_temp.denetle('okul dışı: izin yok', (select not (d->>'izin')::boolean from public.kaynak_durum() d));
select set_config('request.jwt.claims', '{"sub":"aaaaaaaa-0000-0000-0000-000000000001","session_id":"aaaaaaaa-9999-0000-0000-000000000001","role":"authenticated"}', false);
select pg_temp.denetle('aktif cihazı olmayan oturum: izin yok, satır görmez',
  (select not (d->>'izin')::boolean from public.kaynak_durum() d) and (select count(*) = 0 from public.kaynak_tasnif));

-- ===== Worker (service_role) =====
reset role;
set role service_role;
select pg_temp.denetle('B yazamadı: A''nın notu yerinde', (select metin = 'Düzeltildi' from public.kaynak_oge where id = 'a1000000-0000-0000-0000-000000000001'));
select pg_temp.denetle('resim eklenir (60 MB)',
  (select (public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', 'a2000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-00000000000c', 60 * 1048576, 2048, 1536)->>'bayt')::bigint = 60 * 1048576));
select pg_temp.hata_beklenir('100 MB aşılamaz (60 + 41)',
  $$select public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', gen_random_uuid(), 'a0000000-0000-0000-0000-00000000000c', 41 * 1048576, 1, 1)$$, 'kota');
select pg_temp.denetle('tam sınıra kadar eklenir (60 + 40)',
  (select public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', 'a2000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-00000000000c', 40 * 1048576, 1, 1) is not null));
select pg_temp.hata_beklenir('B''nin kota satırı yokken resim eklenemez',
  $$select public.kaynak_resim_ekle('bbbbbbbb-0000-0000-0000-000000000002', gen_random_uuid(), 'a0000000-0000-0000-0000-00000000000c', 1, 1, 1)$$, 'Kota satırı yok');

-- Hamza hakkı artırır (Supabase'de, eposta ile)
reset role;
update public.kaynak_kota set azami_mb = 300 where eposta = 'a@kocaelisaglik.edu.tr';
set role service_role;
select pg_temp.denetle('hak 300 MB olunca yeni resim eklenir',
  (select public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', 'a2000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-00000000000b', 5 * 1048576, 1, 1) is not null));

-- ===== A: kullanım, resimli tasnifi silme =====
reset role;
set role authenticated;
select set_config('request.jwt.claims', '{"sub":"aaaaaaaa-0000-0000-0000-000000000001","session_id":"aaaaaaaa-1111-0000-0000-000000000001","role":"authenticated"}', false);
select pg_temp.denetle('kaynak_durum: 300 MB hak, 105 MB kullanılan',
  (select (d->>'azami_bayt')::bigint = 300 * 1048576 and (d->>'kullanilan_bayt')::bigint = 105 * 1048576 from public.kaynak_durum() d));
select pg_temp.denetle('A resim satırlarını görür', (select count(*) = 3 from public.kaynak_oge where tur = 'resim'));
delete from public.kaynak_oge where tur = 'resim';
select pg_temp.denetle('A resim satırını doğrudan silemez (RLS: hiçbiri silinmez)', (select count(*) = 3 from public.kaynak_oge where tur = 'resim'));
select pg_temp.hata_beklenir('resimli tasnif öğrencinin işleviyle silinmez',
  $$select public.kaynak_tasnif_sil('a0000000-0000-0000-0000-00000000000a')$$, 'Tasnifte resim var');

-- Resimsiz (yalnız notlu) tasnif silinir
insert into public.kaynak_tasnif (id, ad) values ('a0000000-0000-0000-0000-00000000000d', 'Notlar');
insert into public.kaynak_tasnif (id, ust, ad) values ('a0000000-0000-0000-0000-00000000000e', 'a0000000-0000-0000-0000-00000000000d', 'Alt');
insert into public.kaynak_oge (tasnif, tur, metin) values ('a0000000-0000-0000-0000-00000000000e', 'not', 'alt not');
select public.kaynak_tasnif_sil('a0000000-0000-0000-0000-00000000000d');
select pg_temp.denetle('notlu tasnif alt tasnifi ve notuyla silindi',
  (select count(*) = 0 from public.kaynak_tasnif where id in ('a0000000-0000-0000-0000-00000000000d', 'a0000000-0000-0000-0000-00000000000e'))
  and (select count(*) = 0 from public.kaynak_oge where metin = 'alt not'));

-- Worker resimli tasnifi siler: önce resimleri listeler (R2'den siler), sonra hepsini
reset role;
set role service_role;
select pg_temp.denetle('tasnifin (alt tasnifler dahil) 3 resmi listelenir',
  (select count(*) = 3 from public.kaynak_tasnif_resimleri('aaaaaaaa-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-00000000000a')));
select pg_temp.denetle('B adına listelenmez', (select count(*) = 0 from public.kaynak_tasnif_resimleri('bbbbbbbb-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-00000000000a')));
select pg_temp.denetle('resim kaydı var', public.kaynak_resim_var('aaaaaaaa-0000-0000-0000-000000000001', 'a2000000-0000-0000-0000-000000000003'));
select pg_temp.denetle('başkası adına resim kaydı yok', not public.kaynak_resim_var('bbbbbbbb-0000-0000-0000-000000000002', 'a2000000-0000-0000-0000-000000000003'));
select pg_temp.denetle('tek resim silinir (true döner)', public.kaynak_resim_sil('aaaaaaaa-0000-0000-0000-000000000001', 'a2000000-0000-0000-0000-000000000003'));
select pg_temp.denetle('iki resim kaldı', (select count(*) = 2 from public.kaynak_oge where tur = 'resim'));
select pg_temp.denetle('olmayan resim silinmez (false)', not public.kaynak_resim_sil('aaaaaaaa-0000-0000-0000-000000000001', 'a2000000-0000-0000-0000-000000000003'));
select pg_temp.denetle('silinen resmin kaydı yok', not public.kaynak_resim_var('aaaaaaaa-0000-0000-0000-000000000001', 'a2000000-0000-0000-0000-000000000003'));
create temp table silinenler as select * from public.kaynak_tasnif_icini_sil('aaaaaaaa-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-00000000000a') as id;
select pg_temp.denetle('tasnif silme silinen 2 resmin kimliğini döndürür (notlar dönmez)',
  (select count(*) = 2 and bool_and(id::text like 'a2000000%') from silinenler));
select pg_temp.denetle('tasnif bütün içiyle silindi', (select count(*) = 0 from public.kaynak_tasnif) and (select count(*) = 0 from public.kaynak_oge));

-- ===== Bağlantısız yazım: istemci kimliği ve anı; biçimli notlar; notun resimleri =====
reset role;
set role authenticated;
select set_config('request.jwt.claims', '{"sub":"aaaaaaaa-0000-0000-0000-000000000001","session_id":"aaaaaaaa-1111-0000-0000-000000000001","role":"authenticated"}', false);
insert into public.kaynak_tasnif (id, ad, olusma) values ('a3000000-0000-0000-0000-000000000001', 'Ağlar', now() - interval '2 hours');
insert into public.kaynak_tasnif (id, ad, olusma) values ('a3000000-0000-0000-0000-000000000002', 'Elektrik', '2020-01-01');
select pg_temp.denetle('cihazın bildirdiği an (2 saat önce) korunur',
  (select abs(extract(epoch from (olusma - (now() - interval '2 hours')))) < 2 from public.kaynak_tasnif where id = 'a3000000-0000-0000-0000-000000000001'));
select pg_temp.denetle('makul aralık dışındaki an (2020) sunucu anıyla değişir',
  (select olusma > now() - interval '1 minute' from public.kaynak_tasnif where id = 'a3000000-0000-0000-0000-000000000002'));
insert into public.kaynak_oge (id, tasnif, tur, baslik, metin, bicim, olusma, guncellendi) values
  ('a4000000-0000-0000-0000-000000000001', 'a3000000-0000-0000-0000-000000000001', 'not', 'OSI katmanları',
   '<p><b>7 katman</b></p><ul><li>Fiziksel</li></ul>', 'html', now() - interval '1 hour', now() - interval '1 hour');
select pg_temp.denetle('biçimli not başlığıyla ve kendi anıyla eklenir',
  (select baslik = 'OSI katmanları' and bicim = 'html' and abs(extract(epoch from (olusma - (now() - interval '1 hour')))) < 2
          and guncellendi = olusma from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000001'));
select pg_temp.hata_beklenir('aynı kimlikle ikinci not açılmaz (yeniden gönderim)',
  $$insert into public.kaynak_oge (id, tasnif, tur, metin) values ('a4000000-0000-0000-0000-000000000001', 'a3000000-0000-0000-0000-000000000001', 'not', 'x')$$, 'duplicate key');
update public.kaynak_oge set baslik = 'OSI', metin = '<p>yeni</p>', guncellendi = now() - interval '30 minutes' where id = 'a4000000-0000-0000-0000-000000000001';
select pg_temp.denetle('bağlantısız düzenleme kendi anıyla gelir',
  (select baslik = 'OSI' and abs(extract(epoch from (guncellendi - (now() - interval '30 minutes')))) < 2 from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000001'));
update public.kaynak_oge set metin = '<p>daha yeni</p>' where id = 'a4000000-0000-0000-0000-000000000001';
select pg_temp.denetle('an verilmeyen düzenlemede değiştirilme anı şimdi',
  (select guncellendi > now() - interval '1 minute' from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000001'));
update public.kaynak_oge set metin = '<p>eski an</p>', guncellendi = now() - interval '5 hours' where id = 'a4000000-0000-0000-0000-000000000001';
select pg_temp.denetle('değiştirilme anı oluşmadan önce olamaz',
  (select guncellendi = olusma from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000001'));
insert into public.kaynak_oge (id, tasnif, tur, metin) values ('a4000000-0000-0000-0000-000000000002', 'a3000000-0000-0000-0000-000000000001', 'not', 'ilk sürümün düz notu');
update public.kaynak_oge set metin = '<p>ilk sürümün düz notu</p>', bicim = 'html' where id = 'a4000000-0000-0000-0000-000000000002';
select pg_temp.denetle('düz not biçimli nota çevrilebilir', (select bicim = 'html' from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000002'));
select pg_temp.hata_beklenir('başlık en çok 200 harf',
  $$update public.kaynak_oge set baslik = repeat('b', 201) where id = 'a4000000-0000-0000-0000-000000000001'$$, 'kaynak_oge_baslik_check');
select pg_temp.hata_beklenir('metin en çok 60000 harf',
  $$update public.kaynak_oge set metin = repeat('m', 60001) where id = 'a4000000-0000-0000-0000-000000000001'$$, 'kaynak_oge_metin_check');
update public.kaynak_oge set metin = repeat('m', 60000) where id = 'a4000000-0000-0000-0000-000000000002';
select pg_temp.denetle('60000 harflik not olur', (select char_length(metin) = 60000 from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000002'));
select pg_temp.hata_beklenir('bilinmeyen biçim olmaz',
  $$update public.kaynak_oge set bicim = 'xml' where id = 'a4000000-0000-0000-0000-000000000001'$$, 'kaynak_oge_bicim_check');
select pg_temp.hata_beklenir('not başka nota bağlanamaz',
  $$insert into public.kaynak_oge (tasnif, tur, metin, not_id) values ('a3000000-0000-0000-0000-000000000001', 'not', 'x', 'a4000000-0000-0000-0000-000000000001')$$, 'kaynak_oge_turu');
select pg_temp.hata_beklenir('bağlı olduğu not değiştirilemez (sütun izni yok)',
  $$update public.kaynak_oge set not_id = null where id = 'a4000000-0000-0000-0000-000000000001'$$, 'permission denied');
insert into public.kaynak_oge (id, tasnif, tur, metin) values ('a4000000-0000-0000-0000-000000000003', 'a3000000-0000-0000-0000-000000000002', 'not', 'Elektrik notu');

reset role;
insert into public.kaynak_kota (kullanici, eposta) values ('bbbbbbbb-0000-0000-0000-000000000002', 'b@kocaelisaglik.edu.tr') on conflict do nothing;
set role service_role;
select pg_temp.denetle('notun içine resim eklenir (kendi anıyla)',
  (select r->>'not_id' = 'a4000000-0000-0000-0000-000000000001'
          and abs(extract(epoch from ((r->>'olusma')::timestamptz - (now() - interval '10 minutes')))) < 2
   from public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', 'a5000000-0000-0000-0000-000000000001', 'a3000000-0000-0000-0000-000000000001',
        1000, 800, 600, 'a4000000-0000-0000-0000-000000000001', now() - interval '10 minutes') r));
select pg_temp.denetle('aynı kimlikle yeniden gönderilen resim ikinci satır açmaz, kotaya iki kez sayılmaz',
  (select (public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', 'a5000000-0000-0000-0000-000000000001', 'a3000000-0000-0000-0000-000000000001', 1000, 800, 600, 'a4000000-0000-0000-0000-000000000001')->>'id')
          = 'a5000000-0000-0000-0000-000000000001')
  and (select count(*) = 1 and sum(bayt) = 1000 from public.kaynak_oge where tur = 'resim'));
select pg_temp.hata_beklenir('başkasının resim kimliğiyle resim eklenemez',
  $$select public.kaynak_resim_ekle('bbbbbbbb-0000-0000-0000-000000000002', 'a5000000-0000-0000-0000-000000000001', 'a3000000-0000-0000-0000-000000000001', 10, 1, 1)$$, 'kimlik');
select pg_temp.hata_beklenir('başka tasnifteki nota resim bağlanamaz',
  $$select public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 10, 1, 1, 'a4000000-0000-0000-0000-000000000003')$$, 'Not bulunamadı');
select pg_temp.hata_beklenir('resim resme bağlanamaz',
  $$select public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 10, 1, 1, 'a5000000-0000-0000-0000-000000000001')$$, 'Not bulunamadı');
select pg_temp.denetle('tasnife doğrudan resim (notsuz)',
  (select (public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', 'a5000000-0000-0000-0000-000000000002', 'a3000000-0000-0000-0000-000000000001', 2000, 1, 1)->>'not_id') is null));
select pg_temp.denetle('resim satırı sahibine döner, başkasına null',
  (public.kaynak_resim_satiri('aaaaaaaa-0000-0000-0000-000000000001', 'a5000000-0000-0000-0000-000000000001')->>'bayt')::int = 1000
  and public.kaynak_resim_satiri('bbbbbbbb-0000-0000-0000-000000000002', 'a5000000-0000-0000-0000-000000000001') is null);

reset role;
set role authenticated;
select pg_temp.hata_beklenir('resimli not doğrudan silinemez (resimler R2''de kalırdı)',
  $$delete from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000001'$$, 'foreign key');
select pg_temp.hata_beklenir('not silme işlevi öğrenciye kapalı',
  $$select public.kaynak_not_sil('aaaaaaaa-0000-0000-0000-000000000001', 'a4000000-0000-0000-0000-000000000001')$$, 'permission denied');
delete from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000003';
select pg_temp.denetle('resimsiz not doğrudan silinir', (select count(*) = 0 from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000003'));

reset role;
set role service_role;
select pg_temp.denetle('B adına A''nın notu silinmez (boş döner)',
  (select count(*) = 0 from public.kaynak_not_sil('bbbbbbbb-0000-0000-0000-000000000002', 'a4000000-0000-0000-0000-000000000001')));
select pg_temp.denetle('A''nın notu yerinde', (select count(*) = 1 from public.kaynak_oge where id = 'a4000000-0000-0000-0000-000000000001'));
create temp table not_silinen as select * from public.kaynak_not_sil('aaaaaaaa-0000-0000-0000-000000000001', 'a4000000-0000-0000-0000-000000000001') as id;
select pg_temp.denetle('not resmiyle silinir, resmin kimliği döner',
  (select count(*) = 1 and bool_and(id = 'a5000000-0000-0000-0000-000000000001') from not_silinen)
  and (select count(*) = 0 from public.kaynak_oge where id in ('a4000000-0000-0000-0000-000000000001', 'a5000000-0000-0000-0000-000000000001')));
select pg_temp.denetle('tasnife doğrudan konan resim yerinde', (select count(*) = 1 from public.kaynak_oge where id = 'a5000000-0000-0000-0000-000000000002'));
select pg_temp.denetle('silinmiş notu yeniden silmek zararsız (boş döner)',
  (select count(*) = 0 from public.kaynak_not_sil('aaaaaaaa-0000-0000-0000-000000000001', 'a4000000-0000-0000-0000-000000000001')));
-- Tasnif, içindeki notun resimleriyle birlikte tek seferde silinir
reset role;
set role authenticated;
insert into public.kaynak_oge (id, tasnif, tur, metin, bicim) values ('a4000000-0000-0000-0000-000000000004', 'a3000000-0000-0000-0000-000000000001', 'not', '<p>resimli</p>', 'html');
reset role;
set role service_role;
select public.kaynak_resim_ekle('aaaaaaaa-0000-0000-0000-000000000001', 'a5000000-0000-0000-0000-000000000003', 'a3000000-0000-0000-0000-000000000001', 10, 1, 1, 'a4000000-0000-0000-0000-000000000004');
create temp table tasnif_silinen as select * from public.kaynak_tasnif_icini_sil('aaaaaaaa-0000-0000-0000-000000000001', 'a3000000-0000-0000-0000-000000000001') as id;
select pg_temp.denetle('tasnif silinince notun resmi ve doğrudan resim birlikte döner',
  (select count(*) = 2 from tasnif_silinen) and (select count(*) = 0 from public.kaynak_oge where tasnif = 'a3000000-0000-0000-0000-000000000001'));
select public.kaynak_tasnif_icini_sil('aaaaaaaa-0000-0000-0000-000000000001', 'a3000000-0000-0000-0000-000000000002');

-- ===== Sınırlar: 300 tasnif, 3000 not, notların toplamı 5 MB =====
reset role;
set role authenticated;
select set_config('request.jwt.claims', '{"sub":"bbbbbbbb-0000-0000-0000-000000000002","session_id":"bbbbbbbb-1111-0000-0000-000000000002","role":"authenticated"}', false);
insert into public.kaynak_tasnif (ad) select 'T' || g from generate_series(1, 300) g;
select pg_temp.hata_beklenir('301. tasnif açılamaz', $$insert into public.kaynak_tasnif (ad) values ('fazla')$$, 'Tasnif sınırına');
select pg_temp.hata_beklenir('toplu eklemede de sınır işler', $$insert into public.kaynak_tasnif (ad) select 'U' || g from generate_series(1, 5) g$$, 'Tasnif sınırına');
insert into public.kaynak_oge (tasnif, tur, metin)
  select (select id from public.kaynak_tasnif where ad = 'T1'), 'not', repeat('x', 60000) from generate_series(1, 87);
insert into public.kaynak_oge (tasnif, tur, metin) values ((select id from public.kaynak_tasnif where ad = 'T2'), 'not', 'kucuk');
select pg_temp.hata_beklenir('notların toplamı 5 MB''ı aşamaz (88 × 60000)',
  $$insert into public.kaynak_oge (tasnif, tur, metin) values ((select id from public.kaynak_tasnif where ad = 'T1'), 'not', repeat('x', 60000))$$, '5 MB');
select pg_temp.hata_beklenir('başlık da toplama sayılır',
  $$insert into public.kaynak_oge (tasnif, tur, baslik, metin) values ((select id from public.kaynak_tasnif where ad = 'T1'), 'not', repeat('b', 200), repeat('x', 22700))$$, '5 MB');
select pg_temp.hata_beklenir('düzenlemeyle de aşılamaz (kısa notu 60000''e büyütmek)',
  $$update public.kaynak_oge set metin = repeat('y', 60000) where id = (select id from public.kaynak_oge where metin = 'kucuk')$$, '5 MB');
update public.kaynak_oge set metin = repeat('y', 60000) where id = (select id from public.kaynak_oge where metin like 'x%' order by olusma limit 1);
select pg_temp.denetle('aynı boyda düzenleme yapılabilir', (select count(*) = 1 from public.kaynak_oge where metin like 'y%'));
delete from public.kaynak_oge where tur = 'not';
insert into public.kaynak_oge (tasnif, tur, metin)
  select (select id from public.kaynak_tasnif where ad = 'T3'), 'not', 'kısa' from generate_series(1, 3000);
select pg_temp.hata_beklenir('3001. not eklenemez', $$insert into public.kaynak_oge (tasnif, tur, metin) values ((select id from public.kaynak_tasnif where ad = 'T3'), 'not', 'bir tane daha')$$, 'Not sınırına');
reset role;
-- Temizlik: deneme satırları sonraki testlere (kaynak_sina.py) karışmasın
delete from public.kaynak_oge; delete from public.kaynak_tasnif; delete from public.kaynak_kota;
select 'KAYNAK SQL: TAMAM' as sonuc;

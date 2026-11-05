-- Bölüm kodları ve bölüme göre içerik süzme (01-sema.sql, 3 ve 5b) yerel denemesi.
-- Çalıştırma: test/sql/calistir.sh  (Supabase taklidi + şema + bu dosya)
-- Her denetim başarısızsa "KALDI" ile hata verir; hepsi geçerse "BÖLÜM SQL: TAMAM".
\set ON_ERROR_STOP 1
set client_min_messages = warning;

-- Y: yönetici (hususi yetkili, BP1); O1, O2: kodu olmayan yeni öğrenciler; H: başka bölüme kodla girecek
insert into auth.users values
  ('a0000000-0000-0000-0000-0000000000a1', 'yonetici@kocaelisaglik.edu.tr', now(), null),
  ('a0000000-0000-0000-0000-0000000000a2', 'o1@kocaelisaglik.edu.tr', now(), null),
  ('a0000000-0000-0000-0000-0000000000a3', 'o2@kocaelisaglik.edu.tr', now(), null),
  ('a0000000-0000-0000-0000-0000000000a4', 'h@kocaelisaglik.edu.tr', now(), null),
  ('a0000000-0000-0000-0000-0000000000a5', 'dis@gmail.com', now(), null);
insert into auth.sessions values
  ('b0000000-0000-0000-0000-0000000000a1', 'a0000000-0000-0000-0000-0000000000a1', 'test'),
  ('b0000000-0000-0000-0000-0000000000a2', 'a0000000-0000-0000-0000-0000000000a2', 'test'),
  ('b0000000-0000-0000-0000-0000000000a3', 'a0000000-0000-0000-0000-0000000000a3', 'test'),
  ('b0000000-0000-0000-0000-0000000000a4', 'a0000000-0000-0000-0000-0000000000a4', 'test');
insert into public.hesap_cihazlari (kullanici, eposta)
  select id, email from auth.users where email like '%@kocaelisaglik.edu.tr';
insert into public.cihaz_yerleri (kullanici, oturum)
  select user_id, id from auth.sessions where user_id::text like 'a0000000%';
insert into public.hususi_yetki (eposta) values ('yonetici@kocaelisaglik.edu.tr');
insert into public.profiller (kullanici, program, sinif, sozlesme_surumu)
  values ('a0000000-0000-0000-0000-0000000000a1', 'bilgisayar-programciligi', 1, '2');

-- İkinci bölüm ve içerik: algoritma iki bölümde, veritabani yalnızca BP'de, 2. sınıf dersi yalnız BP'de
insert into public.programlar (id, ad, sinif_sayisi, sira, kod_oneki) values ('hibrit', 'Hibrit', 2, 2, 'he');
insert into public.konular (id, ders, sira, baslik, metin, ozet, hususi, programlar, sinif) values
  ('alg-1', 'algoritma', 1, 'A', 'a', 'x', false, '{bilgisayar-programciligi,hibrit}', 1),
  ('vt-1', 'veritabani', 1, 'V', 'v', 'x', false, '{bilgisayar-programciligi}', 1),
  ('ileri-1', 'ileri', 1, 'İ', 'i', 'x', false, '{bilgisayar-programciligi}', 2),
  ('b2r-1', 'born2beroot', 1, 'B', 'b', 'x', true, '{}', null);
insert into public.agac (id, veri, ozet) values
  ('1/bilgisayar-programciligi/1', '{"gruplar":[]}', 'bp1'),
  ('1/bilgisayar-programciligi/2', '{"gruplar":[]}', 'bp2'),
  ('1/hibrit/1', '{"gruplar":[]}', 'he1'),
  ('2/hususi', '{"gruplar":[]}', 'hu');
insert into storage.objects (bucket_id, name) values ('gorseller', 'veritabani/ab-er.svg'), ('gorseller', 'algoritma/cd-akis.svg');
grant select on storage.objects to authenticated;   -- Supabase'te öyledir; taklitte yok

create or replace function pg_temp.denetle(ad text, kosul boolean) returns void language plpgsql as $$
begin
  if not coalesce(kosul, false) then raise exception 'KALDI: %', ad; end if;
  raise notice 'GEÇTİ: %', ad;
end $$;
create or replace function pg_temp.hata_beklenir(ad text, komut text, parca text) returns void language plpgsql as $$
begin
  execute komut;
  raise exception 'KALDI (hata vermedi): %', ad;
exception when others then
  if sqlerrm like 'KALDI%' then raise; end if;
  if position(parca in sqlerrm) = 0 then raise exception 'KALDI: % — beklenmeyen hata: %', ad, sqlerrm; end if;
  raise notice 'GEÇTİ: % (%)', ad, sqlerrm;
end $$;
create or replace function pg_temp.olarak(kim text) returns void language plpgsql as $$
begin
  perform set_config('request.jwt.claims', json_build_object('sub', 'a0000000-0000-0000-0000-0000000000' || kim,
    'session_id', 'b0000000-0000-0000-0000-0000000000' || kim, 'role', 'authenticated')::text, false);
end $$;
grant execute on all functions in schema pg_temp to authenticated;
set client_min_messages = notice;
set role authenticated;

-- ===== Yönetici =====
select pg_temp.olarak('a1');
select pg_temp.denetle('yönetici üye ve hususi yetkili', public.uye() and public.hususi_yetkili());
select pg_temp.denetle('yönetici bütün bölümleri görür', (select count(*) from public.programlar) = 2);
select pg_temp.hata_beklenir('sınıf bölümün sınıf sayısını aşamaz', $q$select public.bolum_kodu_uret('bilgisayar-programciligi', 3, 60, 10)$q$, 'Sınıf geçersiz');
select pg_temp.hata_beklenir('süre 7 günü aşamaz', $q$select public.bolum_kodu_uret('bilgisayar-programciligi', 1, 10081, 10)$q$, 'Süre');
select pg_temp.hata_beklenir('kişi sınırı 300ü aşamaz', $q$select public.bolum_kodu_uret('bilgisayar-programciligi', 1, 60, 301)$q$, 'Kişi sınırı');
select pg_temp.hata_beklenir('olmayan bölüm', $q$select public.bolum_kodu_uret('yok', 1, 60, 10)$q$, 'Bölüm bulunamadı');
create temp table kodlar (ad text, veri jsonb);
grant all on kodlar to authenticated;
insert into kodlar select 'bp1', public.bolum_kodu_uret('bilgisayar-programciligi', 1, 120, 2);
insert into kodlar select 'he1', public.bolum_kodu_uret('hibrit', 1, 120, 10);
insert into kodlar select 'bp2', public.bolum_kodu_uret('bilgisayar-programciligi', 2, 120, 10);
select pg_temp.denetle('kod 6 rakam, etiket önek+sınıf+_+kod',
  (select bool_and(veri->>'kod' ~ '^[0-9]{6}$') from kodlar)
  and (select veri->>'etiket' = 'BP1_' || (veri->>'kod') from kodlar where ad = 'bp1')
  and (select veri->>'etiket' = 'HE1_' || (veri->>'kod') from kodlar where ad = 'he1'));
select pg_temp.denetle('etkin kodların rakamları farklı', (select count(distinct veri->>'kod') = 3 from kodlar));
select pg_temp.hata_beklenir('yönetici kendini sıfırlayamaz', $q$select public.idare_hesap_sifirla('a0000000-0000-0000-0000-0000000000a1')$q$, 'Kendi hesabınızı');

-- ===== Öğrenci O1: kodsuz =====
select pg_temp.olarak('a2');
select pg_temp.denetle('kodsuz hesap üye değil', not public.uye());
select pg_temp.denetle('kodsuz hesap bölüm listesini göremez', (select count(*) from public.programlar) = 0);
select pg_temp.denetle('kodsuz hesap ağaç ve konu göremez',
  (select count(*) from public.agac) = 0 and (select count(*) from public.konular) = 0);
select pg_temp.hata_beklenir('öğrenci profil satırı ekleyemez',
  $q$insert into public.profiller (kullanici, program, sinif, sozlesme_surumu) values ('a0000000-0000-0000-0000-0000000000a2', 'bilgisayar-programciligi', 1, '2')$q$, 'permission denied');
select pg_temp.hata_beklenir('öğrenci kod üretemez', $q$select public.bolum_kodu_uret('bilgisayar-programciligi', 1, 60, 10)$q$, 'Yetkisiz');
select pg_temp.hata_beklenir('öğrenci kod listesini göremez', $q$select public.bolum_kodlari_listesi()$q$, 'Yetkisiz');
select pg_temp.hata_beklenir('öğrenci kod tablosunu okuyamaz', $q$select * from public.bolum_kodlari$q$, 'permission denied');
select pg_temp.hata_beklenir('öğrenci hesap arayamaz', $q$select public.idare_hesap_bul('o2@kocaelisaglik.edu.tr')$q$, 'Yetkisiz');
select pg_temp.hata_beklenir('öğrenci hesap sıfırlayamaz', $q$select public.idare_hesap_sifirla('a0000000-0000-0000-0000-0000000000a3')$q$, 'Yetkisiz');
select pg_temp.denetle('biçimsiz kod: bicim, deneme sayılmaz', public.bolum_kodu_kullan('12ab') ->> 'durum' = 'bicim');
-- Kodlar ancak yönetici olarak okunabilir; yanlış kodu bilinenlerden farklı seçeriz
reset role;
create temp table yanlis_kod as
  select lpad(((select max(kod::int) from public.bolum_kodlari) + 1) % 1000000 || '', 6, '0') as kod;
grant select on yanlis_kod to authenticated;
set role authenticated;
select pg_temp.denetle('yanlış kod: 4 hak kaldı', (select public.bolum_kodu_kullan(kod) from yanlis_kod) = '{"durum":"yanlis","kalan":4}'::jsonb);
select public.bolum_kodu_kullan(kod) from yanlis_kod;
select public.bolum_kodu_kullan(kod) from yanlis_kod;
select pg_temp.denetle('4. yanlış: 1 hak kaldı', (select public.bolum_kodu_kullan(kod) ->> 'kalan' from yanlis_kod) = '1');
select pg_temp.denetle('5. yanlış: 15 dakika kilit', (select (public.bolum_kodu_kullan(kod) ->> 'saniye')::int from yanlis_kod) = 900);
select pg_temp.denetle('kilitliyken doğru kod da kabul edilmez',
  (select public.bolum_kodu_kullan(veri->>'kod') ->> 'durum' from kodlar where ad = 'bp1') = 'kilitli');
reset role;
update public.bolum_kodu_denemeleri set kilit = now() - interval '1 second';
set role authenticated;
select pg_temp.denetle('kilit bitince: tam biçimli ad (BP1_…) ile doğru kod girer',
  (select public.bolum_kodu_kullan(veri->>'etiket') from kodlar where ad = 'bp1')
  = '{"durum":"tamam","program":"bilgisayar-programciligi","programAdi":"Bilgisayar Programcılığı","sinif":1}'::jsonb);
select pg_temp.denetle('profil koddan yazıldı, sözleşme henüz onaylı değil',
  (select program = 'bilgisayar-programciligi' and sinif = 1 and sozlesme_surumu is null and bolum_kodu is not null from public.profiller));
select pg_temp.denetle('sözleşmesiz hesap hâlâ üye değil, içerik göremez', not public.uye() and (select count(*) from public.konular) = 0);
select pg_temp.denetle('aynı hesap ikinci kod giremez (zaten)', (select public.bolum_kodu_kullan(veri->>'kod') ->> 'durum' from kodlar where ad = 'he1') = 'zaten');
select pg_temp.hata_beklenir('öğrenci bölümünü değiştiremez', $q$update public.profiller set program = 'hibrit'$q$, 'permission denied');
select pg_temp.hata_beklenir('öğrenci sınıfını değiştiremez', $q$update public.profiller set sinif = 2$q$, 'permission denied');
select pg_temp.hata_beklenir('eski sözleşme sürümü onaylanamaz', $q$update public.profiller set sozlesme_surumu = '1'$q$, 'geçerli sürümü');
update public.profiller set sozlesme_surumu = null;
select pg_temp.denetle('onay boşaltılınca onay anı da boşalır', (select sozlesme_onaylandi is null from public.profiller));
update public.profiller set sozlesme_surumu = '2';
select pg_temp.denetle('sözleşme onaylanınca üye, onay anı yazıldı',
  public.uye() and (select sozlesme_onaylandi is not null from public.profiller));
select pg_temp.denetle('BP1: kendi ağaç satırı', (select array_agg(id) from public.agac) = '{1/bilgisayar-programciligi/1}');
select pg_temp.denetle('BP1: 1. sınıf konuları (2. sınıf ve hususi yok)',
  (select array_agg(id order by id) from public.konular) = '{alg-1,vt-1}');
select pg_temp.denetle('BP1: veritabanı görseli açık', public.gorsel_okunabilir('veritabani/ab-er.svg'));

-- ===== O2: son hak, sonra dolu =====
select pg_temp.olarak('a3');
select pg_temp.denetle('O2 son hakla girer', (select public.bolum_kodu_kullan(veri->>'kod') ->> 'durum' from kodlar where ad = 'bp1') = 'tamam');

-- ===== H: Hibrit 1 =====
select pg_temp.olarak('a4');
select pg_temp.denetle('dolu kod: dolu (bilgi)', (select public.bolum_kodu_kullan(veri->>'kod') from kodlar where ad = 'bp1') = '{"durum":"dolu"}'::jsonb);
reset role;
select pg_temp.denetle('dolu kod deneme sayılmaz', not exists (select 1 from public.bolum_kodu_denemeleri where kullanici = 'a0000000-0000-0000-0000-0000000000a4' and yanlis > 0));
set role authenticated;
select pg_temp.denetle('H Hibrit koduyla girer', (select public.bolum_kodu_kullan(veri->>'kod') ->> 'program' from kodlar where ad = 'he1') = 'hibrit');
update public.profiller set sozlesme_surumu = '2';
select pg_temp.denetle('Hibrit: yalnızca kendi ağaç satırı', (select array_agg(id) from public.agac) = '{1/hibrit/1}');
select pg_temp.denetle('Hibrit: bölüm listesinde yalnızca kendi bölümü', (select array_agg(id) from public.programlar) = '{hibrit}');
select pg_temp.denetle('Hibrit: yalnızca ortak ders (veritabanı yok)', (select array_agg(id) from public.konular) = '{alg-1}');
select pg_temp.denetle('Hibrit: veritabanı görseli kapalı, algoritma görseli açık',
  not public.gorsel_okunabilir('veritabani/ab-er.svg') and public.gorsel_okunabilir('algoritma/cd-akis.svg'));
select pg_temp.denetle('Hibrit: depoda veritabanı nesnesini göremez',
  (select array_agg(name) from storage.objects) = '{algoritma/cd-akis.svg}');

-- ===== Yönetici: liste, iptal, BP2, sıfırlama =====
select pg_temp.olarak('a1');
select pg_temp.denetle('liste: 3 kod, BP1 dolu ve iki kullanan',
  (select jsonb_array_length(public.bolum_kodlari_listesi()) = 3)
  and (select x->>'durum' = 'dolu' and jsonb_array_length(x->'kullananlar') = 2
       from jsonb_array_elements(public.bolum_kodlari_listesi()) x where x->>'etiket' like 'BP1_%'));
select pg_temp.denetle('hesap bul: O1 BP1, sözleşmeli', (select public.idare_hesap_bul('O1@kocaelisaglik.edu.tr ')) @> '{"program":"bilgisayar-programciligi","sinif":1,"sozlesme":true}'::jsonb);
select pg_temp.denetle('hesap bul: olmayan adres boş', public.idare_hesap_bul('yok@kocaelisaglik.edu.tr') is null);
select public.bolum_kodu_iptal((select (veri->>'id')::uuid from kodlar where ad = 'he1'));
select pg_temp.denetle('iptal edilen kod listede iptal', (select x->>'durum' from jsonb_array_elements(public.bolum_kodlari_listesi()) x where x->>'etiket' like 'HE1_%') = 'iptal');
select public.idare_hesap_sifirla('a0000000-0000-0000-0000-0000000000a2');
select pg_temp.denetle('sıfırlanan hesap listeden düşer, hak geri gelmez',
  (select jsonb_array_length(x->'kullananlar') = 1 and (x->>'kullanim')::int = 2
   from jsonb_array_elements(public.bolum_kodlari_listesi()) x where x->>'etiket' like 'BP1_%'));

-- ===== O1 sıfırlandı: içerik kapandı, iptal kod çalışmaz, BP2 koduyla girer =====
select pg_temp.olarak('a2');
select pg_temp.denetle('sıfırlanan hesap içerik göremez', not public.uye() and (select count(*) from public.konular) = 0);
select pg_temp.denetle('iptal edilmiş kod yanlış sayılır', (select public.bolum_kodu_kullan(veri->>'kod') ->> 'durum' from kodlar where ad = 'he1') = 'yanlis');
select pg_temp.denetle('BP2 koduyla girer', (select public.bolum_kodu_kullan(veri->>'kod') ->> 'sinif' from kodlar where ad = 'bp2') = '2');
update public.profiller set sozlesme_surumu = '2';
select pg_temp.denetle('BP2: kendi satırı ve 1.+2. sınıf konuları',
  (select array_agg(id) from public.agac) = '{1/bilgisayar-programciligi/2}'
  and (select array_agg(id order by id) from public.konular) = '{alg-1,ileri-1,vt-1}');

-- ===== Süresi dolan kod =====
reset role;
update public.bolum_kodlari set bitis = now() - interval '1 second' where etiket like 'BP2_%';
set role authenticated;
select pg_temp.olarak('a3');
-- O2 zaten BP1; süresi dolanı yeni bir hesapla değil, durum işleviyle sınarız
reset role;
delete from public.profiller where kullanici = 'a0000000-0000-0000-0000-0000000000a3';
set role authenticated;
select pg_temp.denetle('süresi dolan kod: suresi_doldu', (select public.bolum_kodu_kullan(veri->>'kod') ->> 'durum' from kodlar where ad = 'bp2') = 'suresi_doldu');

-- ===== Okul dışı =====
select set_config('request.jwt.claims', '{"sub":"a0000000-0000-0000-0000-0000000000a5","role":"authenticated"}', false);
select pg_temp.hata_beklenir('okul dışı hesap kod giremez', $q$select public.bolum_kodu_kullan('123456')$q$, 'Yetkisiz');

reset role;
-- Yönetici adresi listede ama e-postası onaylanmamış: yönetici sayılmaz
insert into auth.users values ('a0000000-0000-0000-0000-0000000000a6', 'onaysiz@kocaelisaglik.edu.tr', null, null);
insert into public.hususi_yetki (eposta) values ('onaysiz@kocaelisaglik.edu.tr');
set role authenticated;
select set_config('request.jwt.claims', '{"sub":"a0000000-0000-0000-0000-0000000000a6","role":"authenticated"}', false);
select pg_temp.denetle('onaysız e-postalı adres yönetici değil', not public.hususi_yetkili());
select pg_temp.hata_beklenir('onaysız adres kod üretemez', $q$select public.bolum_kodu_uret('bilgisayar-programciligi', 1, 60, 10)$q$, 'Yetkisiz');
reset role;
select pg_temp.denetle('kod satırında sınır aşılamaz (kullanim <= azami)',
  not exists (select 1 from public.bolum_kodlari where kullanim > azami));
do $$ begin raise notice 'BÖLÜM SQL: TAMAM'; end $$;

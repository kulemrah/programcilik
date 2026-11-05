-- Geçiş denemesi: bölüm kodundan önceki şemada (test/sql/eski/01-sema-bolumsuz.sql)
-- açılmış hesap ve içerik, yeni şema çalıştırılınca bozulmadan geçiyor mu?
\set ON_ERROR_STOP 1
set client_min_messages = warning;
insert into auth.users values ('c0000000-0000-0000-0000-0000000000c1', 'eski@kocaelisaglik.edu.tr', now(), null),
  ('c0000000-0000-0000-0000-0000000000c2', 'yarim@kocaelisaglik.edu.tr', now(), null);
insert into auth.sessions values ('d0000000-0000-0000-0000-0000000000c1', 'c0000000-0000-0000-0000-0000000000c1', 'test');
insert into public.hesap_cihazlari (kullanici, eposta) values ('c0000000-0000-0000-0000-0000000000c1', 'eski@kocaelisaglik.edu.tr');
insert into public.cihaz_yerleri (kullanici, oturum) values ('c0000000-0000-0000-0000-0000000000c1', 'd0000000-0000-0000-0000-0000000000c1');
insert into public.profiller (kullanici, program, sinif, sozlesme_surumu) values ('c0000000-0000-0000-0000-0000000000c1', 'bilgisayar-programciligi', 1, '2');
-- Sözleşmenin eski sürümünü onaylamış hesap (eski tetikleyici bunu artık yazdırmaz; kurulumda kapatılır)
insert into auth.users values ('c0000000-0000-0000-0000-0000000000c3', 'eskisoz@kocaelisaglik.edu.tr', now(), null);
set session_replication_role = replica;
insert into public.profiller (kullanici, program, sinif, sozlesme_surumu) values ('c0000000-0000-0000-0000-0000000000c3', 'bilgisayar-programciligi', 1, '1');
set session_replication_role = origin;
insert into public.konular (id, ders, sira, baslik, metin, ozet) values ('alg-1', 'algoritma', 1, 'A', 'a', 'x');
insert into public.konular (id, ders, sira, baslik, metin, ozet, hususi) values ('b2r-1', 'born2beroot', 1, 'B', 'b', 'x', true);
insert into public.agac (id, veri, ozet) values (1, '{"gruplar":[]}', 'g'), (2, '{"gruplar":[]}', 'h');
-- Notlar hakkı: biri öntanımlıda (100), biri elle artırılmış (300)
insert into public.kaynak_kota (kullanici, eposta) values ('c0000000-0000-0000-0000-0000000000c1', 'eski@kocaelisaglik.edu.tr');
insert into public.kaynak_kota (kullanici, eposta, azami_mb) values ('c0000000-0000-0000-0000-0000000000c2', 'yarim@kocaelisaglik.edu.tr', 300);
\i supabase/01-sema.sql
\i supabase/01-sema.sql
create or replace function pg_temp.denetle(ad text, kosul boolean) returns void language plpgsql as $$
begin
  if not coalesce(kosul, false) then raise exception 'KALDI: %', ad; end if;
  raise notice 'GEÇTİ: %', ad;
end $$;
grant execute on all functions in schema pg_temp to authenticated;
set client_min_messages = notice;
select pg_temp.denetle('geçiş: eski hesap BP1, sözleşmesi duruyor, kod yok',
  (select program = 'bilgisayar-programciligi' and sinif = 1 and sozlesme_surumu = '2' and bolum_kodu is null and bolum_yazildi is not null
   from public.profiller where kullanici = 'c0000000-0000-0000-0000-0000000000c1'));
select pg_temp.denetle('geçiş: eski sözleşmeli hesap da BP1, onayı korundu (yeniden onaylayacak)',
  (select program = 'bilgisayar-programciligi' and sinif = 1 and sozlesme_surumu = '1' and bolum_yazildi is not null
   from public.profiller where kullanici = 'c0000000-0000-0000-0000-0000000000c3'));
select pg_temp.denetle('geçiş: sözleşmeyi hiç onaylamamış (satırı olmayan) hesap kod ister',
  not exists (select 1 from public.profiller where kullanici = 'c0000000-0000-0000-0000-0000000000c2'));
select pg_temp.denetle('geçiş: ağaç kimlikleri metne çevrildi',
  (select array_agg(id order by id) from public.agac) = '{1/bilgisayar-programciligi/1,2/hususi}');
select pg_temp.denetle('geçiş: eski konular BP1, hususi boş',
  (select programlar = '{bilgisayar-programciligi}' and sinif = 1 from public.konular where id = 'alg-1')
  and (select programlar = '{}' and sinif is null from public.konular where id = 'b2r-1'));
select pg_temp.denetle('geçiş: Notlar hakkı 100 → 50, elle artırılan 300 kalır, öntanımlı 50 (ikinci çalıştırmada da)',
  (select array_agg(azami_mb order by eposta) from public.kaynak_kota) = '{50,300}'
  and (select column_default from information_schema.columns where table_name = 'kaynak_kota' and column_name = 'azami_mb') = '50');
select pg_temp.denetle('geçiş: BP öneki bp', (select kod_oneki from public.programlar where id = 'bilgisayar-programciligi') = 'bp');
set role authenticated;
select set_config('request.jwt.claims', '{"sub":"c0000000-0000-0000-0000-0000000000c1","session_id":"d0000000-0000-0000-0000-0000000000c1","role":"authenticated"}', false);
select pg_temp.denetle('geçiş: eski hesap kodsuz üye, ağacını ve konusunu görür',
  public.uye() and (select array_agg(id) from public.agac) = '{1/bilgisayar-programciligi/1}'
  and (select array_agg(id) from public.konular) = '{alg-1}');
select pg_temp.denetle('geçiş: eski hesaba kod sorulmaz (zaten)', public.bolum_kodu_kullan('123456') ->> 'durum' = 'zaten');
reset role;
do $$ begin raise notice 'GEÇİŞ SQL: TAMAM'; end $$;

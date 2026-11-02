-- ==========================================================================
-- Programcılık — veritabanı şeması
-- Supabase SQL Editor'de çalıştırılır. Tekrar çalıştırmak güvenlidir:
-- var olan tablolar ve kayıtlar silinmez, işlevler ve kurallar yenilenir.
-- ==========================================================================

-- --------------------------------------------------------------------------
-- 1) Okul adresi kontrolü
-- --------------------------------------------------------------------------
-- Adresin @'ten sonraki kısmı tam olarak bu olmalı. Alt alan adları
-- (ör. ogr.kocaelisaglik.edu.tr) kabul edilmez.
create or replace function public.okul_adresi_mi(adres text)
returns boolean
language sql
immutable
set search_path = ''
as $$
  select coalesce(lower(adres) ~ '^[^@\s]+@kocaelisaglik\.edu\.tr$', false);
$$;

-- Oturumdaki kullanıcı, adresini kodla doğrulamış bir okul üyesi mi?
-- security definer: auth.users tablosunu okuyabilmek için sahibinin
-- yetkisiyle çalışır; dışarıya yalnızca evet/hayır döner.
create or replace function public.okul_uyesi()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from auth.users u
    where u.id = auth.uid()
      and u.email_confirmed_at is not null
      and public.okul_adresi_mi(u.email)
  );
$$;

revoke execute on function public.okul_uyesi() from public, anon;
grant execute on function public.okul_uyesi() to authenticated;

-- --------------------------------------------------------------------------
-- 2) Kayıt kapısı (Before User Created kancası)
-- --------------------------------------------------------------------------
-- Okul adresi olmayan biri için hesap hiç açılmaz; böylece kod e-postası
-- da gönderilmez ve gönderim kotası kötüye kullanılamaz.
-- Kurulum: Authentication > Hooks > "Before User Created" > Postgres
-- function > public.kayit_kapisi
create or replace function public.kayit_kapisi(event jsonb)
returns jsonb
language plpgsql
set search_path = ''
as $$
begin
  if public.okul_adresi_mi(event->'user'->>'email') then
    return '{}'::jsonb;
  end if;
  return jsonb_build_object(
    'error', jsonb_build_object(
      'http_code', 403,
      'message', 'Yalnızca @kocaelisaglik.edu.tr uzantılı okul adresiyle giriş yapılabilir.'
    )
  );
end;
$$;

grant usage on schema public to supabase_auth_admin;
grant execute on function public.okul_adresi_mi(text) to supabase_auth_admin, authenticated;
grant execute on function public.kayit_kapisi(jsonb) to supabase_auth_admin;
revoke execute on function public.kayit_kapisi(jsonb) from public, anon, authenticated;

-- Parola kapalı: giriş yalnızca e-postaya gelen kodla olur. Supabase'in
-- e-posta girişinde parola ayrıca kapatılamıyor; bir öğrenci uygulama
-- dışından kendine parola koyabilir ve kodsuz giriş yapıp cihaz devralmayı
-- ve hesap paylaşımını kolaylaştırabilirdi. Konulan parola sessizce silinir.
create or replace function public.parola_engeli()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if new.encrypted_password is not null and new.encrypted_password <> '' then
    new.encrypted_password := '';
  end if;
  return new;
end;
$$;

revoke execute on function public.parola_engeli() from public, anon, authenticated;
grant execute on function public.parola_engeli() to supabase_auth_admin;

drop trigger if exists parola_engeli on auth.users;
create trigger parola_engeli
  before insert or update of encrypted_password on auth.users
  for each row execute function public.parola_engeli();

-- --------------------------------------------------------------------------
-- 3) Programlar, profiller ve kullanım sözleşmesi
-- --------------------------------------------------------------------------
-- Okunan bölüm (program). Yeni bir program eklemek için buraya satır eklenir;
-- uygulama listeyi buradan okur, birden fazla program olunca seçtirir.
create table if not exists public.programlar (
  id           text primary key check (id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  ad           text not null,
  sinif_sayisi smallint not null default 2 check (sinif_sayisi between 1 and 6),
  sira         smallint not null default 0
);

insert into public.programlar (id, ad, sinif_sayisi, sira)
values ('bilgisayar-programciligi', 'Bilgisayar Programcılığı', 2, 1)
on conflict (id) do nothing;

-- Geçerli sözleşme sürümü. Sözleşme metni değişince burası ve uygulamadaki
-- SOZLESME.surum birlikte artırılır; herkes yeni metni yeniden onaylar.
create or replace function public.sozlesme_surumu()
returns text
language sql
immutable
set search_path = ''
as $$ select '2'::text $$;

create table if not exists public.profiller (
  kullanici          uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  program            text not null references public.programlar(id),
  sinif              smallint not null check (sinif between 1 and 6),
  sozlesme_surumu    text not null,
  sozlesme_onaylandi timestamptz not null default now(),
  olusturuldu        timestamptz not null default now()
);

-- Onay anını sunucu yazar; yalnızca geçerli sürüm onaylanabilir;
-- sınıf, programın sınıf sayısını aşamaz. security definer: program
-- listesine bakarken okuyanın yetkisine takılmasın (yetki RLS'de denetlenir).
create or replace function public.profil_denetle()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  azami smallint;
begin
  if new.sozlesme_surumu is distinct from public.sozlesme_surumu() then
    raise exception 'Sözleşmenin geçerli sürümü onaylanmalı';
  end if;
  select p.sinif_sayisi into azami from public.programlar p where p.id = new.program;
  if azami is null or new.sinif > azami then
    raise exception 'Program ya da sınıf geçersiz';
  end if;
  if tg_op = 'INSERT' then
    new.sozlesme_onaylandi := now();
    new.olusturuldu := now();
  else
    new.kullanici := old.kullanici;
    new.olusturuldu := old.olusturuldu;
    if new.sozlesme_surumu is distinct from old.sozlesme_surumu then
      new.sozlesme_onaylandi := now();
    else
      new.sozlesme_onaylandi := old.sozlesme_onaylandi;
    end if;
  end if;
  return new;
end;
$$;

drop trigger if exists profil_denetle on public.profiller;
create trigger profil_denetle
  before insert or update on public.profiller
  for each row execute function public.profil_denetle();

alter table public.programlar enable row level security;
alter table public.profiller  enable row level security;

drop policy if exists "okul uyesi okur" on public.programlar;
create policy "okul uyesi okur" on public.programlar
  for select to authenticated
  using ((select public.okul_uyesi()));

drop policy if exists "kendi profilini okur" on public.profiller;
create policy "kendi profilini okur" on public.profiller
  for select to authenticated
  using (kullanici = (select auth.uid()) and (select public.okul_uyesi()));

drop policy if exists "kendi profilini ekler" on public.profiller;
create policy "kendi profilini ekler" on public.profiller
  for insert to authenticated
  with check (kullanici = (select auth.uid()) and (select public.okul_uyesi()));

drop policy if exists "kendi profilini gunceller" on public.profiller;
create policy "kendi profilini gunceller" on public.profiller
  for update to authenticated
  using (kullanici = (select auth.uid()) and (select public.okul_uyesi()))
  with check (kullanici = (select auth.uid()));

revoke all on public.programlar, public.profiller from anon, authenticated;
grant select on public.programlar to authenticated;
grant select, insert, update on public.profiller to authenticated;
grant all on public.programlar, public.profiller to service_role;

-- --------------------------------------------------------------------------
-- 4) Cihaz sınırı
-- --------------------------------------------------------------------------
-- Bir hesap aynı anda en çok "azami_cihaz" kadar cihazda açık olabilir
-- (varsayılan 1; birden fazla cihaz isteyen öğrenci için elle artırılır).
-- Supabase her girişte yeni bir oturum (session) açar. Bir oturumun notlara
-- erişebilmesi için hesabın cihaz yerlerinden birini tutması gerekir:
--   - Boş yer varsa oturum yeri soru sorulmadan alır.
--   - Yerler doluysa devralma gerekir:
--       1. devralma_iste()   → istek anı kaydedilir
--       2. e-postaya ikinci kod gider, kodla YENİ bir oturum açılır
--       3. cihazi_sahiplen() → yalnızca istekten SONRA açılmış oturum kabul
--          edilir; en uzun süredir görülmeyen cihaz yerinden çıkarılır
-- Bir oturum her yer aldığında cihaz_degisim_sayisi bir artar ve olay
-- cihaz_gecmisi'ne yazılır. Bu tablolara istemcinin hiçbir yetkisi yoktur;
-- yalnızca aşağıdaki işlevler dokunur.

-- Önceki sürümün tablosu (tek cihaz, sayaçsız). Yerine aşağıdakiler geldi.
drop table if exists public.aktif_cihazlar;

create table if not exists public.hesap_cihazlari (
  kullanici            uuid primary key references auth.users(id) on delete cascade,
  eposta               text not null,
  azami_cihaz          smallint not null default 1 check (azami_cihaz between 1 and 10),
  cihaz_degisim_sayisi integer not null default 0,
  devralma_istendi     timestamptz,
  devralma_oturumu     uuid
);

-- Önceki sürümden yükseltirken eksik sütun eklenir
alter table public.hesap_cihazlari add column if not exists devralma_oturumu uuid;

create table if not exists public.cihaz_yerleri (
  kullanici    uuid not null references public.hesap_cihazlari(kullanici) on delete cascade,
  oturum       uuid not null,
  sahiplenildi timestamptz not null default now(),
  son_gorulme  timestamptz not null default now(),
  primary key (kullanici, oturum)
);

create table if not exists public.cihaz_gecmisi (
  id        bigint generated always as identity primary key,
  kullanici uuid not null references public.hesap_cihazlari(kullanici) on delete cascade,
  zaman     timestamptz not null default now(),
  yol       text not null check (yol in ('serbest', 'devralma')),
  oturum    uuid not null,
  cikarilan uuid,
  tarayici  text
);

create index if not exists cihaz_gecmisi_kullanici on public.cihaz_gecmisi (kullanici, zaman);

alter table public.hesap_cihazlari enable row level security;
alter table public.cihaz_yerleri   enable row level security;
alter table public.cihaz_gecmisi   enable row level security;
revoke all on public.hesap_cihazlari, public.cihaz_yerleri, public.cihaz_gecmisi from anon, authenticated;
grant all on public.hesap_cihazlari, public.cihaz_yerleri, public.cihaz_gecmisi to service_role;

-- Oturum kimliği erişim belirtecinin (JWT) session_id alanındadır;
-- belirteç yenilense de aynı kalır.
create or replace function public.oturum_kimligi()
returns uuid
language sql
stable
set search_path = ''
as $$
  select nullif(auth.jwt() ->> 'session_id', '')::uuid;
$$;

-- 'bu'      : bu oturum bir cihaz yeri tutuyor
-- 'bos'     : boş yer var (yer tutan oturumlardan kapanmış olanlar sayılmaz)
-- 'baska'   : yerler dolu
-- 'yetkisiz': okul üyesi değil, oturum kimliği yok ya da oturum kapanmış
--             (çıkış yapılmış oturumun belirteci süresi dolana kadar geçerli
--             kalır; o sürede yer alamasın diye oturum kaydına bakılır)
create or replace function public.cihaz_durumu()
returns text
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  benim uuid := public.oturum_kimligi();
  sinir smallint;
  dolu  integer;
begin
  if auth.uid() is null or benim is null or not public.okul_uyesi()
     or not exists (select 1 from auth.sessions s where s.id = benim and s.user_id = auth.uid()) then
    return 'yetkisiz';
  end if;
  if exists (select 1 from public.cihaz_yerleri y where y.kullanici = auth.uid() and y.oturum = benim) then
    return 'bu';
  end if;
  select h.azami_cihaz into sinir from public.hesap_cihazlari h where h.kullanici = auth.uid();
  select count(*) into dolu from public.cihaz_yerleri y
  where y.kullanici = auth.uid()
    and exists (select 1 from auth.sessions s where s.id = y.oturum and s.user_id = auth.uid());
  if dolu < coalesce(sinir, 1) then return 'bos'; end if;
  return 'baska';
end;
$$;

-- Hesabın satırını açar (yoksa) ve kilitler: aynı hesabın iki cihazı aynı
-- anda yer almaya çalışırsa sırayla işlenir.
create or replace function public.hesabi_kilitle()
returns void
language plpgsql
volatile
security definer
set search_path = ''
as $$
begin
  insert into public.hesap_cihazlari (kullanici, eposta)
  select u.id, lower(u.email) from auth.users u where u.id = auth.uid()
  on conflict (kullanici) do nothing;
  perform 1 from public.hesap_cihazlari h where h.kullanici = auth.uid() for update;
end;
$$;

-- Kapanmış oturumların yerini boşaltır; sınır düşürüldüyse fazla yerleri,
-- en uzun süredir görülmeyenden başlayarak boşaltır.
create or replace function public.cihaz_yerlerini_temizle()
returns void
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  sinir smallint;
begin
  delete from public.cihaz_yerleri y
  where y.kullanici = auth.uid()
    and not exists (select 1 from auth.sessions s where s.id = y.oturum and s.user_id = auth.uid());
  select h.azami_cihaz into sinir from public.hesap_cihazlari h where h.kullanici = auth.uid();
  delete from public.cihaz_yerleri y
  where y.kullanici = auth.uid()
    and y.oturum in (
      select y2.oturum from public.cihaz_yerleri y2
      where y2.kullanici = auth.uid()
      order by y2.son_gorulme desc
      offset coalesce(sinir, 1)
    );
end;
$$;

-- Uygulama her eşitlemede bunu çağırır: durumu ve sınırı döner; bu oturum
-- yer tutuyorsa "son görülme" anını tazeler.
create or replace function public.cihaz_yokla()
returns jsonb
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  durum text;
begin
  if public.cihaz_durumu() = 'yetkisiz' then
    return jsonb_build_object('durum', 'yetkisiz');
  end if;
  perform public.hesabi_kilitle();
  perform public.cihaz_yerlerini_temizle();
  durum := public.cihaz_durumu();
  if durum = 'bu' then
    update public.cihaz_yerleri set son_gorulme = now()
    where kullanici = auth.uid() and oturum = public.oturum_kimligi();
  end if;
  return jsonb_build_object(
    'durum', durum,
    'azami', (select h.azami_cihaz from public.hesap_cihazlari h where h.kullanici = auth.uid())
  );
end;
$$;

-- İstek yalnızca az önce kodla açılmış (30 dakikadan yeni) bir oturumdan
-- kabul edilir. Yoksa eskiden kalmış bir oturum (ör. cihazından çıkarılmış
-- olan) isteği yapar, tek kodla açılan yeni oturum devralırdı; ikinci kod
-- adımı atlanmış olurdu.
create or replace function public.devralma_iste()
returns void
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  benim  uuid := public.oturum_kimligi();
  acilis timestamptz;
begin
  if public.cihaz_durumu() <> 'baska' then
    return;
  end if;
  select s.created_at into acilis from auth.sessions s where s.id = benim and s.user_id = auth.uid();
  if acilis is null or acilis < now() - interval '30 minutes' then
    raise exception 'Devralma için yeniden giriş gerekli';
  end if;
  update public.hesap_cihazlari
  set devralma_istendi = now(), devralma_oturumu = benim
  where kullanici = auth.uid();
end;
$$;

create or replace function public.cihazi_sahiplen()
returns text
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  benim  uuid := public.oturum_kimligi();
  durum  text;
  istek  timestamptz;
  acilis timestamptz;
  cikan  uuid;
  yol    text := 'serbest';
begin
  if public.cihaz_durumu() = 'yetkisiz' then
    raise exception 'Yetkisiz';
  end if;
  perform public.hesabi_kilitle();
  perform public.cihaz_yerlerini_temizle();
  durum := public.cihaz_durumu();
  if durum = 'bu' then
    return 'bu';
  end if;
  if durum = 'baska' then
    select h.devralma_istendi into istek from public.hesap_cihazlari h where h.kullanici = auth.uid();
    select s.created_at into acilis from auth.sessions s where s.id = benim and s.user_id = auth.uid();
    if istek is null or istek < now() - interval '30 minutes' or acilis is null or acilis <= istek
       or benim = (select h.devralma_oturumu from public.hesap_cihazlari h where h.kullanici = auth.uid()) then
      raise exception 'Bu hesap başka bir cihazda açık';
    end if;
    select y.oturum into cikan from public.cihaz_yerleri y
    where y.kullanici = auth.uid()
    order by y.son_gorulme asc
    limit 1;
    delete from public.cihaz_yerleri where kullanici = auth.uid() and oturum = cikan;
    yol := 'devralma';
  end if;
  insert into public.cihaz_yerleri (kullanici, oturum) values (auth.uid(), benim);
  update public.hesap_cihazlari
  set cihaz_degisim_sayisi = cihaz_degisim_sayisi + 1, devralma_istendi = null, devralma_oturumu = null
  where kullanici = auth.uid();
  -- Tarayıcı bilgisi Supabase'in oturum kaydından alınır (yoksa boş kalır)
  insert into public.cihaz_gecmisi (kullanici, yol, oturum, cikarilan, tarayici)
  values (auth.uid(), yol, benim, cikan,
          (select to_jsonb(s) ->> 'user_agent' from auth.sessions s where s.id = benim));
  return 'bu';
end;
$$;

-- Uygulamadan "Çıkış yap": bu oturumun yeri boşaltılır. Uygulama bunu
-- oturumu kapatmadan önce çağırır; bağlantı yoksa çıkışa izin vermeden önce
-- kullanıcıya sorar.
create or replace function public.cihazi_birak()
returns void
language sql
volatile
security definer
set search_path = ''
as $$
  delete from public.cihaz_yerleri
  where kullanici = auth.uid() and oturum = public.oturum_kimligi();
$$;

-- Yönetici sınırı düşürürse fazla yerler hemen boşaltılır (en uzun
-- süredir görülmeyenden başlayarak). Yalnızca uygulamanın kendi yoklamasına
-- bırakılsaydı, yoklama yapmayan bir istemci fazla cihazı açık tutabilirdi.
create or replace function public.sinir_dusunce_temizle()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  -- Önce kapanmış oturumların yerleri: canlı bir cihaz ölü bir yer yüzünden çıkmasın
  delete from public.cihaz_yerleri y
  where y.kullanici = new.kullanici
    and not exists (select 1 from auth.sessions s where s.id = y.oturum and s.user_id = y.kullanici);
  delete from public.cihaz_yerleri y
  where y.kullanici = new.kullanici
    and y.oturum in (
      select y2.oturum from public.cihaz_yerleri y2
      where y2.kullanici = new.kullanici
      order by y2.son_gorulme desc
      offset new.azami_cihaz
    );
  return null;
end;
$$;

revoke execute on function public.sinir_dusunce_temizle() from public, anon, authenticated;

drop trigger if exists sinir_dusunce_temizle on public.hesap_cihazlari;
create trigger sinir_dusunce_temizle
  after update of azami_cihaz on public.hesap_cihazlari
  for each row when (new.azami_cihaz < old.azami_cihaz)
  execute function public.sinir_dusunce_temizle();

create or replace function public.bu_cihaz_aktif()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.cihaz_yerleri y
    join auth.sessions s on s.id = y.oturum and s.user_id = y.kullanici
    where y.kullanici = auth.uid() and y.oturum = public.oturum_kimligi()
  );
$$;

-- Uygulamanın çağırdığı dört işlev dışındakiler yalnızca içeriden kullanılır
revoke execute on function public.oturum_kimligi(), public.cihaz_durumu(), public.hesabi_kilitle(),
  public.cihaz_yerlerini_temizle(), public.bu_cihaz_aktif(), public.cihaz_yokla(),
  public.devralma_iste(), public.cihazi_sahiplen(), public.cihazi_birak() from public, anon, authenticated;
grant execute on function public.cihaz_yokla(), public.devralma_iste(), public.cihazi_sahiplen(),
  public.cihazi_birak() to authenticated;

-- Notlara erişim: okul üyesi olmak yetmez; geçerli sözleşmeyi onaylamış ve
-- hesabın aktif cihazında olmak gerekir.
create or replace function public.uye()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select public.okul_uyesi() and public.bu_cihaz_aktif() and exists (
    select 1 from public.profiller p
    where p.kullanici = auth.uid()
      and p.sozlesme_surumu = public.sozlesme_surumu()
  );
$$;

revoke execute on function public.uye() from public, anon;
grant execute on function public.uye() to authenticated;

-- --------------------------------------------------------------------------
-- 5) İçerik tabloları — yalnızca GitHub Action (gizli anahtar) yazar
-- --------------------------------------------------------------------------
-- Ağaç: Sınıf > Dönem > Ders yapısı. İki satır:
--   id 1: herkesin gördüğü gruplar
--   id 2: hususi gruplar (agac.json'da "hususi": true) — yalnızca hususi
--         yetkisi olan hesaplar görür
create table if not exists public.agac (
  id          smallint primary key default 1,
  veri        jsonb not null,
  ozet        text not null,
  guncellendi timestamptz not null default now()
);

-- Önceki sürümde kural tek satıra izin veriyordu (adsız; Postgres adı agac_id_check)
alter table public.agac drop constraint if exists agac_id_check;
alter table public.agac add constraint agac_id_check check (id in (1, 2));

create table if not exists public.konular (
  id          text primary key,
  ders        text not null,
  sira        integer not null,
  baslik      text not null,
  metin       text not null,
  kavramlar   jsonb not null default '[]'::jsonb,
  sorular     jsonb not null default '[]'::jsonb,
  kartlar     jsonb not null default '[]'::jsonb,
  ozet        text not null,
  guncellendi timestamptz not null default now()
);

-- Hususi grubun konuları: yalnızca hususi yetkisi olan hesaplar okur
alter table public.konular add column if not exists hususi boolean not null default false;
create index if not exists konular_ders on public.konular (ders);

-- Hususi yetki: bu tabloya okul adresi eklenen hesap hususi dersleri görür.
-- Yalnızca yönetici (SQL Editor / Table Editor) yazar; uygulamanın yetkisi yok.
create table if not exists public.hususi_yetki (
  eposta  text primary key check (eposta = lower(eposta)),
  verildi timestamptz not null default now()
);
alter table public.hususi_yetki enable row level security;
revoke all on public.hususi_yetki from anon, authenticated;
grant all on public.hususi_yetki to service_role;

create or replace function public.hususi_yetkili()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.hususi_yetki y
    join auth.users u on lower(u.email) = y.eposta
    where u.id = auth.uid()
  );
$$;

revoke execute on function public.hususi_yetkili() from public, anon;
grant execute on function public.hususi_yetkili() to authenticated;

alter table public.agac    enable row level security;
alter table public.konular enable row level security;

drop policy if exists "okul uyesi okur" on public.agac;
create policy "okul uyesi okur" on public.agac
  for select to authenticated
  using ((select public.uye()) and (id = 1 or (select public.hususi_yetkili())));

drop policy if exists "okul uyesi okur" on public.konular;
create policy "okul uyesi okur" on public.konular
  for select to authenticated
  using ((select public.uye()) and (not hususi or (select public.hususi_yetkili())));

-- Yetkiler açıkça verilir; projenin varsayılan yetki ayarına güvenilmez.
revoke all on public.agac, public.konular from anon, authenticated;
grant select on public.agac, public.konular to authenticated;
grant all    on public.agac, public.konular to service_role;

-- --------------------------------------------------------------------------
-- 6) Kullanıcı kayıtları: okundu, boya, yıldız, yanlış, kart, ayar, yer, mühim, çalışma
--    ayar/kimlik: isteğe bağlı ad ve soyad. calisma/"GG|cihaz": o cihazın o günkü
--    çalışma süreleri ve sonuç sayıları (her cihaz kendi satırını yazar).
-- --------------------------------------------------------------------------
-- Her kayıt (tür, anahtar) çiftiyle tekildir. Silme yoktur; "silindi"
-- işaretlenir ki öteki cihaz da silindiğini öğrensin.
-- guncellendi: kaydı yazan cihazın saati (hangisi yeni, ona göre).
-- sunucuda  : sunucunun kaydı kabul ettiği an (cihazlar bundan sonrasını çeker).
create table if not exists public.kayitlar (
  kullanici   uuid not null default auth.uid() references auth.users(id) on delete cascade,
  tur         text not null,
  anahtar     text not null check (char_length(anahtar) between 1 and 300),
  deger       jsonb,
  silindi     boolean not null default false,
  guncellendi timestamptz not null,
  sunucuda    timestamptz not null default now(),
  primary key (kullanici, tur, anahtar),
  constraint deger_boyutu check (deger is null or pg_column_size(deger) <= 65536)
);

create index if not exists kayitlar_cekme on public.kayitlar (kullanici, sunucuda);

-- Kayıt türleri. Kural tablodan ayrı tanımlanır ki yeni tür eklenince
-- (ör. "muhim") var olan tabloda da güncellensin. Önceki sürümde kural
-- tablo içinde adsız tanımlıydı; Postgres ona kayitlar_tur_check adını verir.
alter table public.kayitlar drop constraint if exists kayitlar_tur_check;
alter table public.kayitlar add constraint kayitlar_tur_check
  check (tur in ('okundu','boya','yildiz','yanlis','kart','ayar','yer','muhim','calisma'));

-- Eski bir yazım yenisinin üstüne yazamaz. Gelecek zaman sunucu saatine
-- çekilir (pay bırakılmaz): saati ileride olan cihaz, sonraki gerçek
-- yazımları "eski" saydırıp sessizce düşürtmesin. Uygulama gönderdiği
-- satırların sunucudaki zamanını geri okuyup kendi kopyasına yazar.
create or replace function public.kayit_zamani()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.guncellendi := least(new.guncellendi, clock_timestamp());
  if tg_op = 'UPDATE' then
    if new.guncellendi < old.guncellendi then
      return null;   -- daha eski yazım: satır olduğu gibi kalır
    end if;
    new.kullanici := old.kullanici;
  end if;
  new.sunucuda := clock_timestamp();
  return new;
end;
$$;

drop trigger if exists kayit_zamani on public.kayitlar;
create trigger kayit_zamani
  before insert or update on public.kayitlar
  for each row execute function public.kayit_zamani();

alter table public.kayitlar enable row level security;

drop policy if exists "kendi kaydini okur" on public.kayitlar;
create policy "kendi kaydini okur" on public.kayitlar
  for select to authenticated
  using (kullanici = (select auth.uid()) and (select public.uye()));

drop policy if exists "kendi kaydini ekler" on public.kayitlar;
create policy "kendi kaydini ekler" on public.kayitlar
  for insert to authenticated
  with check (kullanici = (select auth.uid()) and (select public.uye()));

drop policy if exists "kendi kaydini gunceller" on public.kayitlar;
create policy "kendi kaydini gunceller" on public.kayitlar
  for update to authenticated
  using (kullanici = (select auth.uid()) and (select public.uye()))
  with check (kullanici = (select auth.uid()));

revoke all on public.kayitlar from anon, authenticated;
grant select, insert, update on public.kayitlar to authenticated;
grant all on public.kayitlar to service_role;

-- --------------------------------------------------------------------------
-- 7) Görseller (akış şeması, devre çizimi vb.) — gizli kova
-- --------------------------------------------------------------------------
insert into storage.buckets (id, name, public)
values ('gorseller', 'gorseller', false)
on conflict (id) do nothing;

-- Görsel yolu "<ders>/<ad>". İzin listesi mantığı: görsel, okuyanın
-- görebildiği bir konusu olan derse aitse okunur. Böylece hususi dersin
-- görselleri yüklenirken (konuları henüz yokken) ya da konuları silindikten
-- sonra da kapalı kalır; var olmayan ders ile hususi ders aynı cevabı verir.
-- security definer: konular tablosuna okuyanın kurallarına takılmadan bakar.
create or replace function public.gorsel_okunabilir(ad text)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select public.uye() and exists (
    select 1 from public.konular k
    where k.ders = split_part(ad, '/', 1)
      and (not k.hususi or public.hususi_yetkili())
  );
$$;

revoke execute on function public.gorsel_okunabilir(text) from public, anon;
grant execute on function public.gorsel_okunabilir(text) to authenticated;

drop policy if exists "okul uyesi gorsel okur" on storage.objects;
create policy "okul uyesi gorsel okur" on storage.objects
  for select to authenticated
  using (bucket_id = 'gorseller' and public.gorsel_okunabilir(name));

-- --------------------------------------------------------------------------
-- 8) Kaynak: öğrencinin kendi ders resimleri ve notları
-- --------------------------------------------------------------------------
-- Her öğrenci kendi tasniflerini (en çok üç kademe iç içe) açar; içlerine
-- resim ve not koyar. Hepsini yalnızca sahibi görür. Resimlerin kendisi
-- Cloudflare R2'dedir (anahtar "<kullanici>/<oge id>.webp"); buradaki satır
-- yalnızca bilgisidir. Resim satırlarını yalnızca R2'ye yükleyen ve R2'den
-- silen Worker (gizli anahtarla) yazar; böylece kota aşılamaz ve R2 ile
-- tablo ayrışmaz. Notları ve tasnifleri uygulama doğrudan yazar.

-- Kişi başı izin. Satır, öğrenci Kaynak'ı ilk açtığında kendiliğinden açılır.
-- Hakkı artırmak (KURULUM.md, "Kaynak hakkı"):
--   update public.kaynak_kota set azami_mb = 300 where eposta = 'ad.soyad@kocaelisaglik.edu.tr';
create table if not exists public.kaynak_kota (
  kullanici uuid primary key references auth.users(id) on delete cascade,
  eposta    text,
  azami_mb  integer not null default 100 check (azami_mb between 0 and 10240),
  olusma    timestamptz not null default now()
);

create table if not exists public.kaynak_tasnif (
  id          uuid primary key default gen_random_uuid(),
  kullanici   uuid not null default auth.uid() references auth.users(id) on delete cascade,
  ust         uuid references public.kaynak_tasnif(id) on delete cascade,
  ad          text not null check (char_length(btrim(ad)) between 1 and 80),
  derinlik    smallint not null default 1 check (derinlik between 1 and 3),
  olusma      timestamptz not null default now(),
  guncellendi timestamptz not null default now()
);
create index if not exists kaynak_tasnif_ust on public.kaynak_tasnif (kullanici, ust);

-- Uygulama değişiklikleri önce cihaza yazar, bağlantı olunca gönderir: bir
-- not internetsiz yazılıp saatler sonra gelebilir. Cihazın bildirdiği an makul
-- aralıktaysa (son 90 gün ile 5 dakika sonrası arası) o kullanılır; değilse
-- (yanlış ayarlı saat) sunucunun anı.
create or replace function public.kaynak_zaman(istenen timestamptz)
returns timestamptz
language sql
stable
set search_path = ''
as $$
  select case when istenen between now() - interval '90 days' and now() + interval '5 minutes'
              then istenen else now() end;
$$;

-- Kademe sunucuda hesaplanır: üst tasnif aynı kişinin olmalı, kademe 3'ü
-- geçemez. Oluştuktan sonra yalnızca adı değişir (yeri ve sahibi değişmez).
create or replace function public.kaynak_tasnif_denetle()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  ust_kademe smallint;
begin
  if tg_op = 'UPDATE' then
    new.kullanici := old.kullanici;
    new.ust := old.ust;
    new.derinlik := old.derinlik;
    new.olusma := old.olusma;
    new.guncellendi := now();
    return new;
  end if;
  /* Kişi başı en çok 300 tasnif (veritabanı doldurulamasın). Aynı kişinin
     eşzamanlı eklemeleri sıraya girer. */
  perform pg_advisory_xact_lock(hashtext('kaynak:' || new.kullanici::text));
  if (select count(*) from public.kaynak_tasnif where kullanici = new.kullanici) >= 300 then
    raise exception 'Tasnif sınırına (300) ulaşıldı.' using errcode = 'P0001';
  end if;
  if new.ust is null then
    new.derinlik := 1;
  else
    select t.derinlik into ust_kademe from public.kaynak_tasnif t
    where t.id = new.ust and t.kullanici = new.kullanici;
    if ust_kademe is null then
      raise exception 'Üst tasnif bulunamadı.' using errcode = 'P0001';
    end if;
    if ust_kademe >= 3 then
      raise exception 'Tasnifler en çok üç kademe iç içe olabilir.' using errcode = 'P0001';
    end if;
    new.derinlik := ust_kademe + 1;
  end if;
  new.olusma := public.kaynak_zaman(new.olusma);
  new.guncellendi := new.olusma;
  return new;
end;
$$;

drop trigger if exists kaynak_tasnif_denetle on public.kaynak_tasnif;
create trigger kaynak_tasnif_denetle
  before insert or update on public.kaynak_tasnif
  for each row execute function public.kaynak_tasnif_denetle();

-- Tasnifin içindekiler: not ya da resim (R2'deki dosyanın bilgisi).
--   not:   baslik (boş olabilir) ve metin. bicim 'duz' ise metin düz yazıdır
--          (ilk sürümün notları); 'html' ise uygulamanın editörünün ürettiği,
--          izinli birkaç etiketten oluşan biçimli metindir (p, b, i, u, s,
--          h3, ul/ol/li, renk için span[data-renk], img[data-resim]). Uygulama
--          gösterirken yeniden süzer; burada yalnızca metin olarak saklanır.
--   resim: not_id boşsa tasnife doğrudan konmuş resimdir; doluysa o notun
--          metninin arasındaki resimdir (img data-resim="<id>").
-- Tasnif silinirken içinde öğe varsa silinmez (on delete restrict): resimler
-- önce R2'den silinmeli. Notun resimleri varken not tek başına silinemez
-- (not_id dış anahtarı); not resimleriyle birlikte Worker'dan silinir.
-- İstemci kimliği kendisi üretebilir (bağlantısızken açılan not ve resim).
create table if not exists public.kaynak_oge (
  id          uuid primary key default gen_random_uuid(),
  kullanici   uuid not null default auth.uid() references auth.users(id) on delete cascade,
  tasnif      uuid not null references public.kaynak_tasnif(id) on delete restrict,
  tur         text not null check (tur in ('not', 'resim')),
  baslik      text,
  metin       text,
  bicim       text not null default 'duz',
  not_id      uuid references public.kaynak_oge(id),
  bayt        integer check (bayt is null or bayt > 0),
  en          integer,
  boy         integer,
  olusma      timestamptz not null default now(),
  guncellendi timestamptz not null default now()
);
-- İlk sürümden yükseltme: sütunlar ve sınırlar (yeniden çalıştırılabilir)
alter table public.kaynak_oge add column if not exists baslik text;
alter table public.kaynak_oge add column if not exists bicim text not null default 'duz';
alter table public.kaynak_oge add column if not exists not_id uuid references public.kaynak_oge(id);
alter table public.kaynak_oge drop constraint if exists kaynak_oge_metin_check;
alter table public.kaynak_oge add constraint kaynak_oge_metin_check
  check (metin is null or char_length(metin) <= 60000);
alter table public.kaynak_oge drop constraint if exists kaynak_oge_baslik_check;
alter table public.kaynak_oge add constraint kaynak_oge_baslik_check
  check (baslik is null or char_length(baslik) <= 200);
alter table public.kaynak_oge drop constraint if exists kaynak_oge_bicim_check;
alter table public.kaynak_oge add constraint kaynak_oge_bicim_check
  check (bicim in ('duz', 'html'));
alter table public.kaynak_oge drop constraint if exists kaynak_oge_turu;
alter table public.kaynak_oge add constraint kaynak_oge_turu check (
  (tur = 'not' and metin is not null and bayt is null and not_id is null) or
  (tur = 'resim' and bayt is not null and metin is null and baslik is null));
create index if not exists kaynak_oge_tasnif on public.kaynak_oge (kullanici, tasnif);
create index if not exists kaynak_oge_notu on public.kaynak_oge (not_id) where not_id is not null;

-- Uygulama yalnızca not ekler ve notun başlığını, metnini, biçimini
-- değiştirir; satırın sahibi, tasnifi, türü, bağlı olduğu not ve oluşma anı
-- sonradan değişmez.
create or replace function public.kaynak_oge_denetle()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  /* Notlar kişi başı en çok 3000 adet ve toplam 5 MB metin (biçimli
     metinle birkaç bin sayfa): resimler kotaya sayılır, notlar bu sınırla
     veritabanını dolduramaz. Aynı kişinin eşzamanlı yazımları sıraya girer. */
  if (tg_op = 'INSERT' and new.tur = 'not') or (tg_op = 'UPDATE' and old.tur = 'not') then
    perform pg_advisory_xact_lock(hashtext('kaynak:' || coalesce(old.kullanici, new.kullanici)::text));
    if tg_op = 'INSERT' and (select count(*) from public.kaynak_oge where kullanici = new.kullanici and tur = 'not') >= 3000 then
      raise exception 'Not sınırına (3000) ulaşıldı.' using errcode = 'P0001';
    end if;
    if (select coalesce(sum(octet_length(o.metin) + coalesce(octet_length(o.baslik), 0)), 0) from public.kaynak_oge o
        where o.kullanici = coalesce(old.kullanici, new.kullanici) and o.tur = 'not'
          and (tg_op = 'INSERT' or o.id <> old.id))
        + octet_length(new.metin) + coalesce(octet_length(new.baslik), 0) > 5242880 then
      raise exception 'Notların toplam sınırına (5 MB) ulaşıldı.' using errcode = 'P0001';
    end if;
  end if;
  if tg_op = 'UPDATE' then
    new.kullanici := old.kullanici;
    new.tasnif := old.tasnif;
    new.tur := old.tur;
    new.not_id := old.not_id;
    new.bayt := old.bayt;
    new.en := old.en;
    new.boy := old.boy;
    new.olusma := old.olusma;
    /* Bağlantısızken yapılan düzenleme kendi anıyla gelir */
    if new.guncellendi is distinct from old.guncellendi then
      new.guncellendi := greatest(old.olusma, public.kaynak_zaman(new.guncellendi));
    else
      new.guncellendi := now();
    end if;
    return new;
  end if;
  if not exists (select 1 from public.kaynak_tasnif t where t.id = new.tasnif and t.kullanici = new.kullanici) then
    raise exception 'Tasnif bulunamadı.' using errcode = 'P0001';
  end if;
  /* Notun içindeki resim: not aynı kişinin ve aynı tasnifte olmalı */
  if new.not_id is not null and not exists (
      select 1 from public.kaynak_oge n
      where n.id = new.not_id and n.kullanici = new.kullanici and n.tur = 'not' and n.tasnif = new.tasnif) then
    raise exception 'Not bulunamadı.' using errcode = 'P0001';
  end if;
  new.olusma := public.kaynak_zaman(new.olusma);
  new.guncellendi := greatest(new.olusma, public.kaynak_zaman(new.guncellendi));
  return new;
end;
$$;

drop trigger if exists kaynak_oge_denetle on public.kaynak_oge;
create trigger kaynak_oge_denetle
  before insert or update on public.kaynak_oge
  for each row execute function public.kaynak_oge_denetle();

alter table public.kaynak_kota   enable row level security;
alter table public.kaynak_tasnif enable row level security;
alter table public.kaynak_oge    enable row level security;

drop policy if exists "kendi tasnifini okur" on public.kaynak_tasnif;
create policy "kendi tasnifini okur" on public.kaynak_tasnif
  for select to authenticated
  using (kullanici = (select auth.uid()) and (select public.uye()));
drop policy if exists "kendi tasnifini ekler" on public.kaynak_tasnif;
create policy "kendi tasnifini ekler" on public.kaynak_tasnif
  for insert to authenticated
  with check (kullanici = (select auth.uid()) and (select public.uye()));
drop policy if exists "kendi tasnifini gunceller" on public.kaynak_tasnif;
create policy "kendi tasnifini gunceller" on public.kaynak_tasnif
  for update to authenticated
  using (kullanici = (select auth.uid()) and (select public.uye()))
  with check (kullanici = (select auth.uid()));

drop policy if exists "kendi ogesini okur" on public.kaynak_oge;
create policy "kendi ogesini okur" on public.kaynak_oge
  for select to authenticated
  using (kullanici = (select auth.uid()) and (select public.uye()));
drop policy if exists "kendi notunu ekler" on public.kaynak_oge;
create policy "kendi notunu ekler" on public.kaynak_oge
  for insert to authenticated
  with check (kullanici = (select auth.uid()) and tur = 'not' and (select public.uye()));
drop policy if exists "kendi notunu gunceller" on public.kaynak_oge;
create policy "kendi notunu gunceller" on public.kaynak_oge
  for update to authenticated
  using (kullanici = (select auth.uid()) and tur = 'not' and (select public.uye()))
  with check (kullanici = (select auth.uid()) and tur = 'not');
drop policy if exists "kendi notunu siler" on public.kaynak_oge;
create policy "kendi notunu siler" on public.kaynak_oge
  for delete to authenticated
  using (kullanici = (select auth.uid()) and tur = 'not' and (select public.uye()));

revoke all on public.kaynak_kota, public.kaynak_tasnif, public.kaynak_oge from anon, authenticated;
grant select, insert on public.kaynak_tasnif to authenticated;
grant update (ad) on public.kaynak_tasnif to authenticated;
grant select, insert, delete on public.kaynak_oge to authenticated;
grant update (baslik, metin, bicim, guncellendi) on public.kaynak_oge to authenticated;
grant all on public.kaynak_kota, public.kaynak_tasnif, public.kaynak_oge to service_role;

-- Kaynak durumu: kim, izni var mı, hakkı ve kullandığı. Kota satırı yoksa
-- açılır. Uygulama kota çubuğu için, Worker da her istekte belirteci
-- doğrulamak için çağırır (geçersiz belirteçle PostgREST 401 verir).
create or replace function public.kaynak_durum()
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  ben uuid := auth.uid();
  hak integer;
  kullanilan bigint;
begin
  if ben is null or not public.uye() then
    return jsonb_build_object('izin', false);
  end if;
  insert into public.kaynak_kota (kullanici, eposta)
  select ben, lower(u.email) from auth.users u where u.id = ben
  on conflict (kullanici) do nothing;
  select k.azami_mb into hak from public.kaynak_kota k where k.kullanici = ben;
  select coalesce(sum(o.bayt), 0) into kullanilan from public.kaynak_oge o
  where o.kullanici = ben and o.tur = 'resim';
  return jsonb_build_object('izin', true, 'kullanici', ben,
    'azami_bayt', hak::bigint * 1048576, 'kullanilan_bayt', kullanilan);
end;
$$;

-- Yalnızca not içeren (resimsiz) bir tasnifi alt tasnifleriyle siler.
-- İçinde resim varsa silmez: resimli tasnifi Worker siler (önce R2'den).
create or replace function public.kaynak_tasnif_sil(tasnif_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  ben uuid := auth.uid();
begin
  if ben is null or not public.uye() then
    raise exception 'Yetki yok.' using errcode = '42501';
  end if;
  if not exists (select 1 from public.kaynak_tasnif where id = tasnif_id and kullanici = ben) then
    raise exception 'Tasnif bulunamadı.' using errcode = 'P0001';
  end if;
  if exists (
    with recursive alt as (
      select id from public.kaynak_tasnif where id = tasnif_id and kullanici = ben
      union all
      select t.id from public.kaynak_tasnif t join alt on t.ust = alt.id
    )
    select 1 from public.kaynak_oge o join alt on o.tasnif = alt.id where o.tur = 'resim'
  ) then
    raise exception 'Tasnifte resim var.' using errcode = 'P0001';
  end if;
  perform public.kaynak_tasnif_icini_sil(ben, tasnif_id);
end;
$$;

-- ---- Yalnızca Worker'ın (gizli anahtar, service_role) çağırdığı işlevler ----

-- Tasnifin ve alt tasniflerinin içindeki resimler (Worker önce bunları R2'den siler)
create or replace function public.kaynak_tasnif_resimleri(sahip uuid, tasnif_id uuid)
returns setof uuid
language sql
stable
security definer
set search_path = ''
as $$
  with recursive alt as (
    select id from public.kaynak_tasnif where id = tasnif_id and kullanici = sahip
    union all
    select t.id from public.kaynak_tasnif t join alt on t.ust = alt.id
  )
  select o.id from public.kaynak_oge o join alt on o.tasnif = alt.id where o.tur = 'resim';
$$;

-- Tasnifi bütün içiyle siler ve silinen resimlerin kimliklerini döndürür
-- (Worker onları R2'den siler). Kişinin kota satırı kilitlenir: aynı anda
-- süren bir yükleme (kaynak_resim_ekle de kilitler) araya giremez; silmeden
-- önce eklenen resim de silinenler arasında döner, R2'de artık kalmaz.
drop function if exists public.kaynak_tasnif_icini_sil(uuid, uuid);
create function public.kaynak_tasnif_icini_sil(sahip uuid, tasnif_id uuid)
returns setof uuid
language plpgsql
security definer
set search_path = ''
as $$
begin
  perform 1 from public.kaynak_kota where kullanici = sahip for update;
  return query
    with recursive alt as (
      select id from public.kaynak_tasnif where id = tasnif_id and kullanici = sahip
      union all
      select t.id from public.kaynak_tasnif t join alt on t.ust = alt.id
    )
    , silinen as (
      delete from public.kaynak_oge o using alt
      where o.tasnif = alt.id and o.kullanici = sahip
      returning o.id, o.tur
    )
    select silinen.id from silinen where silinen.tur = 'resim';
  delete from public.kaynak_tasnif where id = tasnif_id and kullanici = sahip;
end;
$$;

-- R2'ye yüklenen resmin satırını açar. Kota burada, kişinin satırı
-- kilitlenerek denetlenir (aynı anda iki yükleme sınırı aşamasın).
-- Kimliği uygulama üretir; aynı kimlikle yeniden gönderilirse (cevap yolda
-- kaybolmuştu) ikinci satır açılmaz, var olan döner. not_id: resim bir notun
-- içindeyse o not. zaman: resmin cihazda eklendiği an (bkz. kaynak_zaman).
drop function if exists public.kaynak_resim_ekle(uuid, uuid, uuid, integer, integer, integer);
create or replace function public.kaynak_resim_ekle(sahip uuid, oge_id uuid, tasnif_id uuid, boyut integer,
  genislik integer, yukseklik integer, not_kimligi uuid default null, zaman timestamptz default null)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  hak integer;
  kullanilan bigint;
  satir public.kaynak_oge;
begin
  select k.azami_mb into hak from public.kaynak_kota k where k.kullanici = sahip for update;
  if hak is null then
    raise exception 'Kota satırı yok.' using errcode = 'P0001';
  end if;
  select * into satir from public.kaynak_oge o where o.id = oge_id;
  if found then
    if satir.kullanici = sahip and satir.tur = 'resim' then
      return to_jsonb(satir);
    end if;
    raise exception 'kimlik' using errcode = 'P0001';
  end if;
  select coalesce(sum(o.bayt), 0) into kullanilan from public.kaynak_oge o
  where o.kullanici = sahip and o.tur = 'resim';
  if kullanilan + boyut > hak::bigint * 1048576 then
    raise exception 'kota' using errcode = 'P0001';
  end if;
  insert into public.kaynak_oge (id, kullanici, tasnif, tur, bayt, en, boy, not_id, olusma, guncellendi)
  values (oge_id, sahip, tasnif_id, 'resim', boyut, genislik, yukseklik, not_kimligi,
          coalesce(zaman, now()), coalesce(zaman, now()))
  returning * into satir;
  return to_jsonb(satir);
end;
$$;

-- Resmin satırı (yoksa null): Worker aynı kimlikle gelen resmi R2'ye yeniden
-- yazmadan var olanı döndürür
create or replace function public.kaynak_resim_satiri(sahip uuid, oge_id uuid)
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
  select to_jsonb(o) from public.kaynak_oge o where o.id = oge_id and o.kullanici = sahip and o.tur = 'resim';
$$;

-- Notu, içindeki resimlerle birlikte siler; silinen resimlerin kimliklerini
-- döndürür (Worker onları R2'den siler). Not yoksa boş döner (yeniden
-- gönderilen silme zararsızdır).
create or replace function public.kaynak_not_sil(sahip uuid, not_kimligi uuid)
returns setof uuid
language plpgsql
security definer
set search_path = ''
as $$
begin
  perform 1 from public.kaynak_kota where kullanici = sahip for update;
  return query
    delete from public.kaynak_oge o
    where o.not_id = not_kimligi and o.kullanici = sahip and o.tur = 'resim'
    returning o.id;
  delete from public.kaynak_oge where id = not_kimligi and kullanici = sahip and tur = 'not';
end;
$$;

-- Resmin satırını siler; silindiyse true (Worker sonra R2'den siler)
drop function if exists public.kaynak_resim_sil(uuid, uuid);
create function public.kaynak_resim_sil(sahip uuid, oge_id uuid)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
begin
  perform 1 from public.kaynak_kota where kullanici = sahip for update;
  delete from public.kaynak_oge where id = oge_id and kullanici = sahip and tur = 'resim';
  return found;
end;
$$;

-- Resmin satırı var mı: Worker resmi yalnızca kaydı olan ve sahibine ait
-- olan için verir (R2'de artık kalmış bir dosya okunamaz)
create or replace function public.kaynak_resim_var(sahip uuid, oge_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (select 1 from public.kaynak_oge where id = oge_id and kullanici = sahip and tur = 'resim');
$$;

revoke execute on function public.kaynak_durum(), public.kaynak_tasnif_sil(uuid),
  public.kaynak_tasnif_resimleri(uuid, uuid), public.kaynak_tasnif_icini_sil(uuid, uuid),
  public.kaynak_resim_ekle(uuid, uuid, uuid, integer, integer, integer, uuid, timestamptz), public.kaynak_resim_sil(uuid, uuid),
  public.kaynak_resim_var(uuid, uuid), public.kaynak_resim_satiri(uuid, uuid), public.kaynak_not_sil(uuid, uuid),
  public.kaynak_zaman(timestamptz), public.kaynak_tasnif_denetle(), public.kaynak_oge_denetle()
  from public, anon, authenticated;
grant execute on function public.kaynak_durum(), public.kaynak_tasnif_sil(uuid) to authenticated;
grant execute on function public.kaynak_tasnif_resimleri(uuid, uuid), public.kaynak_tasnif_icini_sil(uuid, uuid),
  public.kaynak_resim_ekle(uuid, uuid, uuid, integer, integer, integer, uuid, timestamptz), public.kaynak_resim_sil(uuid, uuid),
  public.kaynak_resim_var(uuid, uuid), public.kaynak_resim_satiri(uuid, uuid), public.kaynak_not_sil(uuid, uuid)
  to service_role;

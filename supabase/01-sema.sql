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
as $$ select '1'::text $$;

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
-- 6) Kullanıcı kayıtları: okundu, boya, yıldız, yanlış, kart, ayar, yer, mühim
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
  check (tur in ('okundu','boya','yildiz','yanlis','kart','ayar','yer','muhim'));

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

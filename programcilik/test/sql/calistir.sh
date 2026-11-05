#!/bin/sh
# Şemayı yerel bir PostgreSQL'de (Supabase taklidiyle) baştan kurar, iki kez
# çalıştırır (tekrar çalıştırma güvenli mi) ve Kaynak denemesini yapar.
# PostgreSQL 5499 portunda, /tmp soketinde çalışıyor olmalı (DEVIR-NOTU.md, test düzeneği).
set -e
cd "$(dirname "$0")/../.."
P="psql -h /tmp -p 5499 -U postgres -v ON_ERROR_STOP=1 -q"
$P -c "drop database if exists sema_deneme" >/dev/null
$P -c "create database sema_deneme" >/dev/null
$P -d sema_deneme -f test/sql/00-supabase-taklidi.sql >/dev/null
$P -d sema_deneme -f supabase/01-sema.sql 2>&1 | grep -v NOTICE || true
$P -d sema_deneme -f supabase/01-sema.sql 2>&1 | grep -v NOTICE || true
echo "şema iki kez çalıştı"
$P -d sema_deneme -f test/sql/kaynak-deneme.sql 2>&1 | grep -E "GEÇTİ|KALDI|ERROR|TAMAM" | sed 's/^psql:[^ ]* NOTICE:  //'

# Bölüm kodları ve bölüme göre içerik (ayrı, temiz veritabanında)
$P -c "drop database if exists bolum_deneme" >/dev/null
$P -c "create database bolum_deneme" >/dev/null
$P -d bolum_deneme -f test/sql/00-supabase-taklidi.sql >/dev/null
$P -d bolum_deneme -f supabase/01-sema.sql 2>&1 | grep -v NOTICE || true
$P -d bolum_deneme -f test/sql/bolum-deneme.sql 2>&1 | grep -E "GEÇTİ|KALDI|ERROR|TAMAM" | sed 's/^psql:[^ ]* NOTICE:  //'

# Geçiş: bölüm kodundan önceki şema ve verisi üstüne yeni şema (iki kez)
$P -c "drop database if exists gecis_deneme" >/dev/null
$P -c "create database gecis_deneme" >/dev/null
$P -d gecis_deneme -f test/sql/00-supabase-taklidi.sql >/dev/null
$P -d gecis_deneme -f test/sql/eski/01-sema-bolumsuz.sql 2>&1 | grep -v NOTICE || true
$P -d gecis_deneme -f test/sql/gecis-deneme.sql 2>&1 | grep -E "GEÇTİ|KALDI|ERROR|TAMAM" | sed 's/^psql:[^ ]* NOTICE:  //'

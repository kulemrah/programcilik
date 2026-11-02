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

#!/bin/sh
# uygulama/ klasörünü test ayarlarıyla site/ klasörüne kopyalar (gerçek değerler test değerleriyle değişir)
set -e
rm -rf site; cp -r /home/claude/programcilik/uygulama site
sed -i 's|  SUPABASE_URL: "[^"]*",|  SUPABASE_URL: "https://test.supabase.co",|; s|  ANAHTAR: "[^"]*",|  ANAHTAR: "sb_publishable_test",|; s|  TASHIH_EPOSTA: "[^"]*",|  TASHIH_EPOSTA: "tashih@ornek.com",|; s|  KAYNAK_URL: "[^"]*"|  KAYNAK_URL: "https://kaynak.test"|' site/index.html
sed -i "s/^const KOD_ARALIGI = [0-9]*;/const KOD_ARALIGI = 3;/" site/index.html
grep -c 'test.supabase.co\|sb_publishable_test\|tashih@ornek.com\|kaynak.test' site/index.html

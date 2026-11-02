#!/bin/sh
# Bütün tarayıcı testlerini sırayla çalıştırır; her dosyanın sonucu bir satır
cd /home/claude/programcilik/test/tarayici
sh kur.sh >/dev/null
for f in sina.py vt_sina.py kalicilik_sina.py tema_sina.py istatistik_sina.py hedef_sina.py dokunus_sina.py baslik_sina.py tasma_sina.py ios_sina.py alg_sina.py eko_sina.py buda_sina.py aralik_sina.py devam_sina.py el_sina.py tum_sorular_sina.py cevrimdisi_sina.py saat_cekmece_sina.py takvim_gelecek_sina.py ag_sina.py dn_sina.py galeri_sina.py serit_sina.py geri_sina.py kaynak_sina.py notlar_editor_sina.py cihaz_sina.py; do
  sh yardim/sunucu.sh
  timeout 900 python3 $f > /tmp/sonuc-$f.txt 2>&1
  echo "$f çıkış=$? $(grep -E 'SONUÇ|geçti$' /tmp/sonuc-$f.txt | tail -1) kaldı=$(grep -c KALDI /tmp/sonuc-$f.txt)"
done

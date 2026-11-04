#!/bin/sh
# Test sitesini 8765'te sunar; kapalıysa yeniden açar
curl -s -o /dev/null http://127.0.0.1:8765/ || (nohup python3 -m http.server 8765 --directory /home/claude/programcilik/test/tarayici/site > /dev/null 2>&1 &)
sleep 1

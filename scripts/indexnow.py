#!/usr/bin/env python3
"""IndexNow 通知スクリプト（Bing / Yandex / Naver / Seznam などに即時通知）。

sitemap.xml に載っている URL をまとめて api.indexnow.org に送る。
鍵はリポジトリ直下の <key>.txt（中身＝ファイル名の鍵）で、サイトにそのまま公開されていることが前提。
失敗しても deploy は失敗扱いにしない（exit 0）。
"""
import glob, json, re, sys, urllib.request

HOST = "urilabo.com"
keyfiles = [f for f in glob.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}\.txt", f)]
if not keyfiles:
    print("IndexNow: 鍵ファイル（32桁hex.txt）が見つかりません。スキップ"); sys.exit(0)
key = open(keyfiles[0], encoding="utf-8").read().strip()
urls = re.findall(r"<loc>(.*?)</loc>", open("sitemap.xml", encoding="utf-8").read())
if len(sys.argv) > 1:
    extra = [u for u in sys.argv[1:] if u.startswith("https://" + HOST)]
    urls = sorted(set(urls + extra))
payload = {"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls}
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(payload).encode(),
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow: HTTP {r.status} / {len(urls)}件送信: " + ", ".join(urls))
except urllib.error.HTTPError as e:
    print(f"IndexNow: HTTP {e.code} {e.read().decode(errors='ignore')[:200]}")
except Exception as e:
    print("IndexNow: 送信失敗", e)

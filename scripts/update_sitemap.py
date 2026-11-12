#!/usr/bin/env python3
"""sitemap.xml の lastmod を、各ページを最後に直した日（git の記録）に合わせる。

deploy のたびに動かす。日付が取れないページは元の値のまま残す。
"""
import re, subprocess

def last_changed(url):
    path = re.sub(r"^https://urilabo\.com/", "", url) + "index.html"
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path],
                         capture_output=True, text=True).stdout.strip()
    return out

src = open("sitemap.xml", encoding="utf-8").read()
def fix(m):
    return f"<loc>{m.group(1)}</loc><lastmod>{last_changed(m.group(1)) or m.group(2)}</lastmod>"
new = re.sub(r"<loc>(.*?)</loc><lastmod>(.*?)</lastmod>", fix, src)
if new != src:
    open("sitemap.xml", "w", encoding="utf-8").write(new)
print(new)

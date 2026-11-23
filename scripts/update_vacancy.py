#!/usr/bin/env python3
"""うりぼベースの空き状況の「〇年〇月〇日の時点」を、まとめて書き換える。

使い方（リポジトリの一番上で）:
    python3 scripts/update_vacancy.py 2026年11月23日 2026年12月1日
1つ目が今サイトに出ている日付、2つ目が新しい日付。
「空きあり」を「満室」に変えるときは、下の FILES のページを手で直す。
"""
import sys

FILES = [
    "base/index.html",
    "base/aki/index.html",
    "base/tamazato/index.html",
    "base/shimizu/index.html",
    "base/dansei/index.html",
    "llms-full.txt",
]

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    old, new = sys.argv[1], sys.argv[2]
    for path in FILES:
        text = open(path, encoding="utf-8").read()
        n = text.count(old)
        open(path, "w", encoding="utf-8").write(text.replace(old, new))
        print(f"{path}: {n}か所")

if __name__ == "__main__":
    main()

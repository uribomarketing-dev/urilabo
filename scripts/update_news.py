#!/usr/bin/env python3
"""index.html の自動更新ブロックを、noteのRSSと inoya.tokyo/history/ から更新する。

更新対象（index.html 内のマーカーの間だけ書き換える）
  <!--NEWS:START-->…<!--NEWS:END-->        上部「最新の動き」帯（プレスリリース最新1件＋note最新1件）
  <!--HISTORY:START-->…<!--HISTORY:END-->  「うりぼラボの歩み」（ラボ関連のプレスリリース最新6件）

- 標準ライブラリのみ。取得・解析に失敗したブロックは現状維持（壊れた表示を出さない）。
- リンク先は inoya.tokyo/history/ と note.com/inovision/ のURLだけ許可する。
- テスト用: NOTE_RSS_FILE / HISTORY_HTML_FILE でローカルファイルを指定できる。
"""
import html, os, re, sys, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser

RSS_URL = "https://note.com/inovision/rss"
HISTORY_URL = "https://inoya.tokyo/history/"
NOTE_PORTAL = "https://note.com/inovision"
ALLOWED_PRESS = "https://inoya.tokyo/history/"
ALLOWED_NOTE = "https://note.com/inovision/"
LAB_KEYWORD = "ラボ"      # タイトル・要約にこの語を含むリリースを「ラボ関連」とみなす
LAB_COUNT = 6
INDEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
JST = timezone(timedelta(hours=9))
E = html.escape


def fetch(url, env_name):
    path = os.environ.get(env_name)
    if path:
        return open(path, encoding="utf-8").read()
    req = urllib.request.Request(url, headers={"User-Agent": "urilabo-news-bot/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def short_title(t):
    t = re.sub(r"\s+", " ", t).strip()
    # 全体を囲む「」だけ外す（先頭の「が末尾の」と対応している場合のみ）
    if t.startswith("「") and t.endswith("」"):
        depth, wraps = 0, True
        for i, ch in enumerate(t):
            depth += (ch == "「") - (ch == "」")
            if depth == 0 and i < len(t) - 1:
                wraps = False
                break
        if wraps:
            t = t[1:-1]
    # 最初の一文だけ（長い副題を落とす）
    if "。" in t[:-1]:
        t = t.split("。")[0]
    return t.rstrip("。")


class HistoryParser(HTMLParser):
    """li.ev > article の time[datetime]、h3 > a[href]、p.sum を拾う。"""

    def __init__(self):
        super().__init__()
        self.items, self.cur = [], None
        self.in_h3 = self.in_a = self.in_sum = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag == "li" and "ev" in cls:
            self.cur = {"date": None, "href": None, "title": "", "sum": ""}
        elif self.cur is not None:
            if tag == "time" and a.get("datetime"):
                self.cur["date"] = a["datetime"]
            elif tag == "h3":
                self.in_h3 = True
            elif tag == "a" and self.in_h3 and a.get("href"):
                self.cur["href"], self.in_a = a["href"], True
            elif tag == "p" and "sum" in cls:
                self.in_sum = True

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_a = False
        elif tag == "h3":
            self.in_h3 = False
        elif tag == "p":
            self.in_sum = False
        elif tag == "article" and self.cur is not None:
            c, self.cur = self.cur, None
            if c["date"] and c["href"] and c["title"].strip():
                self.items.append(c)

    def handle_data(self, data):
        if self.cur is None:
            return
        if self.in_a:
            self.cur["title"] += data
        elif self.in_sum:
            self.cur["sum"] += data


def date_key(d):
    m = re.fullmatch(r"(\d{4})-(\d{2})(?:-(\d{2}))?", d)
    return (int(m[1]), int(m[2]), int(m[3] or 0)) if m else None


def date_label(k):
    return f"{k[0]}.{k[1]:02d}.{k[2]:02d}" if k[2] else f"{k[0]}.{k[1]:02d}"


def date_iso(k):
    return f"{k[0]}-{k[1]:02d}-{k[2]:02d}" if k[2] else f"{k[0]}-{k[1]:02d}"


def press_items():
    p = HistoryParser()
    p.feed(fetch(HISTORY_URL, "HISTORY_HTML_FILE"))
    out = []
    for it in p.items:
        k = date_key(it["date"])
        if not k:
            continue
        url = it["href"] if it["href"].startswith("http") else HISTORY_URL + it["href"].lstrip("./")
        if not url.startswith(ALLOWED_PRESS):
            continue
        out.append({"key": k, "title": short_title(it["title"]),
                    "sum": re.sub(r"\s+", " ", it["sum"]).strip(), "url": url})
    out.sort(key=lambda x: x["key"], reverse=True)
    return out


def latest_note():
    root = ET.fromstring(fetch(RSS_URL, "NOTE_RSS_FILE"))
    best = None
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = item.findtext("pubDate")
        if not (title and link and pub) or not link.startswith(ALLOWED_NOTE):
            continue
        dt = parsedate_to_datetime(pub).astimezone(JST)
        k = (dt.year, dt.month, dt.day)
        if best is None or k > best["key"]:
            best = {"key": k, "title": title, "url": link}
    return best


def news_row(tag_html, rec, all_url, kind):
    return (
        f'<div class="news-row">{tag_html}<time datetime="{date_iso(rec["key"])}">{date_label(rec["key"])}</time>'
        f'<a class="news-title" href="{E(rec["url"], quote=True)}" target="_blank" rel="noopener" '
        f'data-track="news_{kind}">{E(rec["title"])}</a>'
        f'<a class="news-all" href="{all_url}" target="_blank" rel="noopener">一覧 →</a></div>'
    )


def history_card(it):
    s = f'<p>{E(it["sum"])}</p>' if it["sum"] else ""
    return (
        f'<article class="card history-card"><time datetime="{date_iso(it["key"])}">{date_label(it["key"])}</time>'
        f'<h3><a href="{E(it["url"], quote=True)}" target="_blank" rel="noopener" data-track="history_card">{E(it["title"])}</a></h3>'
        f'{s}<a class="history-more" href="{E(it["url"], quote=True)}" target="_blank" rel="noopener">プレスリリースを読む →</a></article>'
    )


def replace_block(src, name, new_inner):
    pat = re.compile(rf"(<!--{name}:START-->)(.*?)(<!--{name}:END-->)", re.S)
    m = pat.search(src)
    if not m:
        print(f"{name}: markers not found", file=sys.stderr)
        return src, False
    if m.group(2) == new_inner:
        return src, False
    return src[: m.start(2)] + new_inner + src[m.end(2):], True


def old_news_rows(src):
    m = re.search(r"<!--NEWS:START-->(.*?)<!--NEWS:END-->", src, re.S)
    return re.findall(r'<div class="news-row">.*?</div>', m.group(1), re.S) if m else []


def main():
    src = open(INDEX, encoding="utf-8").read()
    changed = False

    try:
        items = press_items()
    except Exception as ex:
        print(f"press: fetch/parse failed ({ex}); keeping current", file=sys.stderr)
        items = []
    try:
        note = latest_note()
    except Exception as ex:
        print(f"note: fetch/parse failed ({ex}); keeping current", file=sys.stderr)
        note = None

    # 1) 最新の動き帯
    old = old_news_rows(src)
    rows = []
    if items:
        rows.append(news_row('<span class="news-tag">最新の動き</span>', items[0], HISTORY_URL, "press"))
    elif old:
        rows.append(old[0])
    if note:
        rows.append(news_row('<span class="news-tag news-tag-note">note</span>', note, NOTE_PORTAL, "note"))
    elif len(old) > 1:
        rows.append(old[1])
    if rows:
        src, c = replace_block(src, "NEWS", "\n      " + "\n      ".join(rows) + "\n      ")
        changed |= c

    # 2) うりぼラボの歩み
    lab = [i for i in items if LAB_KEYWORD in i["title"] + i["sum"]][:LAB_COUNT]
    if lab:
        cards = "\n        ".join(history_card(i) for i in lab)
        src, c = replace_block(src, "HISTORY", "\n        " + cards + "\n        ")
        changed |= c

    if not changed:
        print("no change")
        return 0
    open(INDEX, "w", encoding="utf-8").write(src)
    print("updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""index.html の「最新の動き」帯を、noteのRSSと inoya.tokyo/history/ から自動更新する。

- 標準ライブラリのみ。取得・解析に失敗した行は現状維持（壊れた表示を出さない）。
- index.html 内の <!--NEWS:START--> と <!--NEWS:END--> の間だけを書き換える。
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
ALLOWED = {"press": "https://inoya.tokyo/history/", "note": "https://note.com/inovision/"}
INDEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
JST = timezone(timedelta(hours=9))


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
    """li.ev > article の time[datetime] と h3 > a[href] を拾う。"""

    def __init__(self):
        super().__init__()
        self.items, self.cur = [], None
        self.in_h3 = self.in_a = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "li" and "ev" in (a.get("class") or "").split():
            self.cur = {"date": None, "href": None, "title": ""}
        elif self.cur is not None:
            if tag == "time" and a.get("datetime"):
                self.cur["date"] = a["datetime"]
            elif tag == "h3":
                self.in_h3 = True
            elif tag == "a" and self.in_h3 and a.get("href"):
                self.cur["href"], self.in_a = a["href"], True

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_a = False
        elif tag == "h3":
            self.in_h3 = False
        elif tag == "article" and self.cur is not None:
            c, self.cur = self.cur, None
            if c["date"] and c["href"] and c["title"].strip():
                self.items.append(c)

    def handle_data(self, data):
        if self.cur is not None and self.in_a:
            self.cur["title"] += data


def date_key(d):
    m = re.fullmatch(r"(\d{4})-(\d{2})(?:-(\d{2}))?", d)
    if not m:
        return None
    return (int(m[1]), int(m[2]), int(m[3] or 0))


def date_label(key):
    y, mo, d = key
    return f"{y}.{mo:02d}.{d:02d}" if d else f"{y}.{mo:02d}"


def date_iso(key):
    y, mo, d = key
    return f"{y}-{mo:02d}-{d:02d}" if d else f"{y}-{mo:02d}"


def latest_press():
    p = HistoryParser()
    p.feed(fetch(HISTORY_URL, "HISTORY_HTML_FILE"))
    best = None
    for it in p.items:
        k = date_key(it["date"])
        if not k:
            continue
        url = it["href"] if it["href"].startswith("http") else HISTORY_URL + it["href"].lstrip("./")
        if not url.startswith(ALLOWED["press"]):
            continue
        if best is None or k > best[0]:
            best = (k, short_title(it["title"]), url)
    return best


def latest_note():
    root = ET.fromstring(fetch(RSS_URL, "NOTE_RSS_FILE"))
    best = None
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = item.findtext("pubDate")
        if not (title and link and pub) or not link.startswith(ALLOWED["note"]):
            continue
        dt = parsedate_to_datetime(pub).astimezone(JST)
        k = (dt.year, dt.month, dt.day)
        if best is None or k > best[0]:
            best = (k, title, link)
    return best


def row(tag_html, rec, all_url, all_label):
    k, title, url = rec
    e = html.escape
    return (
        f'<div class="news-row">{tag_html}<time datetime="{date_iso(k)}">{date_label(k)}</time>'
        f'<a class="news-title" href="{e(url, quote=True)}" target="_blank" rel="noopener" '
        f'data-track="news_{"note" if "note.com" in url else "press"}">{e(title)}</a>'
        f'<a class="news-all" href="{all_url}" target="_blank" rel="noopener">{all_label}</a></div>'
    )


def main():
    src = open(INDEX, encoding="utf-8").read()
    m = re.search(r"<!--NEWS:START-->(.*?)<!--NEWS:END-->", src, re.S)
    if not m:
        print("markers not found", file=sys.stderr)
        return 1
    old = m.group(1)
    old_rows = re.findall(r'<div class="news-row">.*?</div>', old, re.S)

    rows = []
    for name, fn, tag, all_url, all_label in [
        ("press", latest_press, '<span class="news-tag">最新の動き</span>', HISTORY_URL, "一覧 →"),
        ("note", latest_note, '<span class="news-tag news-tag-note">note</span>', NOTE_PORTAL, "一覧 →"),
    ]:
        try:
            rec = fn()
        except Exception as ex:  # 取得失敗は現状維持
            print(f"{name}: fetch/parse failed ({ex}); keeping current", file=sys.stderr)
            rec = None
        idx = 0 if name == "press" else 1
        if rec:
            rows.append(row(tag, rec, all_url, all_label))
        elif idx < len(old_rows):
            rows.append(old_rows[idx])
    if not rows:
        print("nothing to write", file=sys.stderr)
        return 0
    new = "\n      " + "\n      ".join(rows) + "\n      "
    if new == old:
        print("no change")
        return 0
    out = src[: m.start(1)] + new + src[m.end(1):]
    open(INDEX, "w", encoding="utf-8").write(out)
    print("updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

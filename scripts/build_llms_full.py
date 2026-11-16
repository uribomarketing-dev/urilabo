#!/usr/bin/env python3
"""llms-full.txt を作る。llms.txt（要約）と、各ページに表示している「よくある質問」をまとめた詳細版。

使い方: python3 scripts/build_llms_full.py   （リポジトリの一番上で実行）
新しい事実はここでは足さない。llms.txt と各ページ（FAQの構造化データ）にある内容だけを集める。
事実を変えたときは、該当ページ・llms.txt を直してからこれを実行する。
"""
import json, re, pathlib, datetime, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = (ROOT / "CNAME").read_text().strip() if (ROOT / "CNAME").exists() else "inoya.tokyo"
SKIP = ("/history/press/", "/docs/", "/.git/", "/easy/", "/ediblespoon/")

def faqs(path):
    s = path.read_text(encoding="utf-8", errors="ignore")
    out = []
    def walk(d):
        if isinstance(d, dict):
            if d.get("@type") == "Question" and d.get("acceptedAnswer"):
                out.append((d["name"].strip(), d["acceptedAnswer"].get("text", "").strip()))
            for v in d.values(): walk(v)
        elif isinstance(d, list):
            for v in d: walk(v)
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: walk(json.loads(m.group(1)))
        except Exception: pass
    return out

parts = [(ROOT / "llms.txt").read_text(encoding="utf-8").rstrip()]
parts[0] = re.sub(r"^# (.*)$", r"# \1（詳細版）", parts[0], count=1, flags=re.M)
hist = ROOT / "history/llms.txt"
if hist.exists():
    h = hist.read_text(encoding="utf-8")
    m = re.search(r"^## お知らせ（時系列）\n(.*?)(?=^## |\Z)", h, re.S | re.M)
    if m: parts.append("## 沿革（社歴・お知らせの全件。古い順）\n" + m.group(1).rstrip())
seen, blocks = set(), []
for p in sorted(ROOT.rglob("*.html")):
    sp = "/" + p.relative_to(ROOT).as_posix()
    if any(k in sp for k in SKIP) or p.name == "404.html": continue
    qa = [(q, a) for q, a in faqs(p) if (q, a) not in seen]
    if not qa: continue
    seen.update(qa)
    url = "https://" + SITE + re.sub(r"index\.html$", "", sp)
    blocks.append("### " + url + "\n" + "\n".join(f"- Q. {q}\n  A. {a}" for q, a in qa))
if blocks:
    parts.append("## よくある質問（各ページに表示しているものと同じ文面）\n" + "\n\n".join(blocks))
body = "\n\n".join(parts) + "\n"
out = ROOT / "llms-full.txt"
old = out.read_text(encoding="utf-8") if out.exists() else ""
strip = lambda t: re.sub(r"^最終更新：.*\n", "", t, flags=re.M)
if strip(old) != strip("最終更新：x\n" + body):
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).date()  # 日本時間
    out.write_text(f"最終更新：{today.year}年{today.month}月{today.day}日\n\n" + body, encoding="utf-8")
    print("llms-full.txt を更新しました")
else:
    print("変更なし")

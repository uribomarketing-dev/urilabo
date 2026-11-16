# urilabo

urilabo.com（うりぼラボ公式サイト）の正本です。運営は合同会社Uribo です。

## 中身

- index.html … うりぼラボ（DX特化型・事業創出型 就労継続支援B型作業所）のトップ
- base/ … うりぼベース玉里・うりぼベース清水（グループホーム）
- uribo/ … 合同会社Uribo の全体紹介
- smaho/ … スマホ見守りサービス「あのね」（新規の受付は一旦止めています）
- ivy/ ・ 1-44/ … IVY と 1-44 by Uribo labo
- about/ ・ work/ ・ kengaku/ ・ kouchin/ ほか … 基本情報と案内のページ

## 反映のしかた

main に入った変更は、GitHub Actions（.github/workflows/deploy.yml）が ConoHa の公開フォルダへ自動でアップロードします。直すときは作業ブランチとプルリクエストで出し、確認してから main に入れます。

トップの「最新の動き」と「うりぼラボの歩み」は scripts/update_news.py が自動で書き換えます。手では直しません。

## 事実（日付・番号・金額・時間）を変えたときに直すファイル

1. 該当ページのHTML（本文と、同じページの構造化データ）
2. llms.txt
3. llms-full.txt（python3 scripts/build_llms_full.py で作り直す）
4. sitemap.xml は deploy のときに自動で日付が入ります

## 関連

- HOUSE OF INOYA（グループ全体）: https://inoya.tokyo/
- 表記と数字の正本: inoya-tokyo リポジトリの data/facts.json

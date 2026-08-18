---
name: human-report-pptx
description: "「AIっぽく整いすぎた」デザインではなく、学生・研究者・社内担当者が自分でExcel/PowerPointだけで作ったような、地に足の着いた報告・研究発表スライド（研究発表、進捗報告、卒論・課題研究発表、社内報告など）を作成するときに使用する。ユーザーが『手作り感のある資料』『地味でいいから読みやすい資料』『学会・学校発表みたいなスライド』『装飾少なめの報告資料』を求めている場合、または通常の pptx スキル（python-pptx / pptx_skill.py）で作ると洒落すぎる・凝りすぎると感じる場合にこのスキルを使う。「.pptx」「スライド」「発表資料」「研究発表」「進捗報告」といった語に加え、上記のような『人間が作った感』への言及がトリガーとなる。python-pptx ベースの pptx スキル（scripts/pptx_skill.py）と同じ関数構成で使える、その"見た目だけ差し替える"追加モジュール。"
---

# 人が作る「地に足の着いた」PowerPoint資料（python-pptx版）

このスキルは、既存の `pptx` スキル（`python-pptx` + `scripts/pptx_skill.py`）の**上に重ねて使う、見た目だけを差し替えるスタイルパック**です。生成の土台（python-pptx、出力先 `/home/z/my-project/download/`、`new_deck` → 各スライド関数 → `save` という流れ）はそのまま。追加した `scripts/human_pptx.py` が `pptx_skill.py` と同じ関数名（`new_deck`, `cover_slide`, `bullet_slide`, `image_text_slide`, `chart_slide`, `table_slide`, `save`）を持つので、インポート元を差し替えるだけでデザインだけが「人が手作りした報告書」風に変わります。

```python
# 通常（pptx_skill.py = 洗練されたデザイン）
from pptx_skill import new_deck, cover_slide, bullet_slide, chart_slide, save

# このスキル（human_pptx.py = 手作り報告書デザイン）
import sys; sys.path.insert(0, "skill/human-report-pptx/scripts")
from human_pptx import new_deck, cover_slide, bullet_slide, chart_slide, diagram_slide, save
```

**重要:** `pptx_skill.py` の「10/20/30ルール」「視覚的階層」「アクセントバー」といったデザイン方針は、通常の"魅せる"資料向けです。このスキルを使うときは、そちらのデザイン指針は適用せず、以下のガイドラインに置き換えてください。技術的な作法（`word_wrap=True`、CJKフォント明示、画像サイズ指定など `pptx_skill.py` の Common Pitfalls）はそのまま有効です。

## このスキルを使う場面

- 研究発表・課題研究・卒業論文発表のスライド
- 部活動・委員会・ゼミの進捗報告
- 社内の週次/月次報告、勉強会資料
- 「かっこよくしないで」「普通でいい」「学校で発表するやつ」と言われたとき

反対に、営業提案・ブランドのピッチデック・展示会用スライドなど"魅せる"資料が目的なら、通常の `pptx_skill.py` を使ってください。

## 参照元となった実例の特徴

日本の学校・大学でよく見る研究発表資料を分析すると、一貫して次の特徴があります:

1. 背景は常に白。グラデーション、色帯、装飾図形が一切ない
2. 各スライドの左上に太字の小さい見出し（例:「背景・目的」「システム構成 – 完成図」）。タイトルスライド以外に大きなタイトルは存在しない
3. 本文は「・」で始まる箇条書き、または短い説明文。フォントサイズは小さめ（14〜18pt程度）で、余白よりも情報密度を優先
4. グラフはExcel/PowerPoint標準のネイティブチャート（既定の配色: 青・オレンジ・グレー・黄・水色・緑）をそのまま使う。凝ったスタイリングをしない
5. 図解（システム構成図など）は、単色の角丸/直角四角形＋白文字＋シンプルな線や矢印。影・グラデーション・アイコンサークルは使わない
6. イラストは「いらすとや」的なシンプルなフラットの人物イラスト、または実物写真（製品写真、食材の写真）をそのまま貼る
7. 強調したい語句だけ蛍光ペン風の黄色ハイライトや太字で、手描き風に指し示す
8. スライドサイズは16:9（13.333"×7.5"）。日本語フォントは既定でメイリオ／游ゴシック系
9. タイトルスライドはごく普通：中央に太字タイトル、その下にサブタイトル（「〜○○〜」のように波ダッシュで挟む）、さらに下に発表者名を並べるだけ

## デザイン原則（`pptx_skill.py` との対比）

| 項目 | `pptx_skill.py`（"魅せる"資料） | `human_pptx.py`（"人が作った"資料） |
|---|---|---|
| 背景 | `COLORS['bg']` = オフホワイト、`section_slide` はダーク背景 | 常に純白 (`FFFFFF`) 一色 |
| タイトル装飾 | 32-44pt＋アクセントバー（`add_rect` で色帯） | 各スライド左上に太字18pt、`add_header` のみ。色帯なし |
| 配色 | `accent`/`sub` など独自パレットを設計 | Office既定のチャート配色（青`4472C4`・オレンジ`ED7D31`・グレー`A5A5A5`・黄`FFC000`・水色`5B9BD5`・緑`70AD47`）をそのまま流用 |
| 箇条書き | `•` バレット、ダッシュのサブ項目 | `・` バレットで統一。因果関係は文中に「→」を書くだけ |
| グラフ | `chart.has_legend = True` 程度で概ね既定通り（実は近い） | 既定のまま。凡例・軸フォントを日本語に合わせる以外は一切カスタマイズしない |
| 図解 | 用意されていない | `add_box` / `add_arrow` で単色四角＋白文字＋直線矢印。`p:style` の既定効果（影）を明示的に除去する |
| イラスト | 用意されていない | `add_photo` でフラットイラスト・実写真をそのまま配置。加工・マスクなし |
| 強調 | サイズ・太字中心 | `highlight_run()` で蛍光ペン風の背景色を文字にのせる |
| 余白 | ゆったり目 | 最小限。情報を詰める（ただしはみ出しはNG） |

## `scripts/human_pptx.py` の関数

`pptx_skill.py` と対になる名前で用意しています。

| 関数 | 役割 |
|---|---|
| `new_deck(widescreen=True)` | 16:9のプレゼン作成（`pptx_skill.py` と同一挙動） |
| `cover_slide(prs, title, subtitle="", authors="")` | 表紙。白背景・中央揃え・装飾なし |
| `bullet_slide(prs, header, bullets, sub_items=None, size=14)` | 見出し＋「・」箇条書き |
| `image_text_slide(prs, header, image_path, text_bullets, image_side="left")` | 見出し＋写真/イラスト＋箇条書きの二分割 |
| `chart_slide(prs, header, categories, series_data, chart_type=..., note="")` | 見出し＋ネイティブチャート（既定配色のまま）＋出典キャプション |
| `table_slide(prs, header, headers, rows)` | 見出し＋表（ヘッダー行のみ薄い青で塗る、Excel既定風） |
| `diagram_slide(prs, header, boxes, arrows=None)` | 見出し＋単色ボックス＋直線矢印のシステム構成図 |
| `add_header(slide, text)` | 各スライド共通のヘッダーだけを個別に足したいときに使う低レベル関数 |
| `add_bullets(slide, left, top, width, height, items, ...)` | `bullet_slide` の中身だけを既存スライドに足したいときに使う |
| `add_box(slide, left, top, width, height, label, fill_color=..., ...)` | 図解の箱を1つ追加。影は自動的に除去される |
| `add_arrow(slide, x1, y1, x2, y2, ...)` | 箱同士をつなぐ直線矢印（先端は三角形） |
| `add_photo(slide, image_path, left, top, width=None, height=None)` | 写真・イラストをそのまま貼るだけ |
| `highlight_run(run, hex_color="FFFF00")` | run単位で蛍光ペン風ハイライトを付ける（python-pptx標準APIには無いためOOXMLを直接操作） |
| `save(prs, filename, out_dir="/home/z/my-project/download")` | `pptx_skill.py` と同じ既定出力先 |

`COLORS` 辞書には `box_blue` / `box_orange` / `box_gray` / `box_gold` / `box_cyan` / `box_green`（Office既定チャート配色）と `table_header_fill`（薄い青）が入っています。`diagram_slide` の `boxes` にこれらを順番に割り当てると、資料全体で配色の一貫性が出ます。

## 具体的な作り方

### 1. スライド全体
- `new_deck()` は16:9（13.333"×7.5"）を既定にする。変更しない
- 背景は常に白。`_set_bg` は既定で `COLORS["bg"]`（純白）を塗るだけなので、呼び出し側で色を変えない
- 全スライドで `add_header` の位置（left=0.45, top=0.3）を統一する。手作業でコピーして作ったような座標の一貫性が重要

### 2. 見出し
- 18pt太字、黒、フォントは `FONT_JP`（メイリオ、既定）
- 見出しの書式は「大分類 - 小分類」または「大分類・小分類」を踏襲してよい（例:「システム構成 – 完成図」「背景・目的」）
- 見出しの下に線・色帯を入れない

### 3. 本文・箇条書き
- 段落先頭は `・`。`add_bullets` の既定
- 本文14-16pt、キャプション9-10pt
- 中央揃えは使わない。すべて左揃え
- 矢印「→」を使った一行の因果関係表現を積極的に使う（例:「指標Xが目標に届いていない　→　特定の条件で不足が大きい」）。専用の矢印図形を作る必要はなく、`add_bullets` の文字列にそのまま書く

### 4. 配色
- パレットを"設計"しない。`COLORS` に定義済みのOffice既定色（`box_blue` など）をそのまま使い回す
- `chart_slide` はシリーズの色を一切指定しない。python-pptxはテーマの既定配色（accent1〜6）を自動で使うので、これが最も"それらしい"見た目になる

### 5. グラフ
- `chart_slide` を使う。`chart_type` は `XL_CHART_TYPE.COLUMN_CLUSTERED` / `LINE` / `PIE` など基本的なものだけ
- 凡例・軸ラベルのフォントだけ日本語に合わせ、色やデータラベル位置は既定のまま
- 出典・注釈は `note=` 引数で1行、9pt程度で入れる（例:「出典：〇〇省 令和〇年度調査」）

### 6. 図解（システム構成図・フロー図など）
- `diagram_slide(prs, header, boxes, arrows)` を使う
- `boxes` は `{"label":..., "left":..., "top":..., "width":..., "height":..., "color": COLORS["box_blue"]}` の並び。単色の角丸四角＋白文字太字になる
- `arrows` は `(x1, y1, x2, y2)` のタプル。直線＋三角矢印のみ
- `add_box` は theme由来の影を自動的に除去する（`<p:style>` を削除）。手動で `add_shape` する場合は同じ処理を忘れないこと（LibreOffice/PowerPointの既定角丸四角には影が付くため、"手作り"の見た目にはノイズになる）

### 7. イラスト・写真
- 人物イラストは image_search でシンプルなフラットデザインの人物クリップアート（医師、食事するイラストなど）を検索し、`add_photo` でそのまま貼る
- 製品・被写体は実写真をそのまま大きく載せる。角丸マスク・枠線・影などの加工をしない

### 8. 強調表現
- 重要な一語・一文だけ `highlight_run(run, "FFFF00")` で蛍光ペン風にする、または `bold=True`
- 数値を目立たせたい場合、その数値だけ `_text` でフォントサイズを上げて別テキストボックスに置く（本文14ptの中で「350g」だけ20pt太字、など）
- 多用しない。1スライドに1箇所程度

### 9. タイトルスライド
- `cover_slide(prs, title, subtitle, authors)` を使う
- 白背景、中央揃え。タイトル30pt太字、サブタイトル17pt（「〜〇〇〜」で挟む形式も可）、発表者名13ptを下部に

## やること / やらないこと 早見表

**やる:**
- 白背景を貫く
- 見出しは全スライド同じ位置・同じ書式（`add_header` を必ず経由する）
- `COLORS` の既定Office配色をそのまま使う
- `chart_slide` のチャート色はカスタマイズしない
- 「・」箇条書き、「→」の因果表現
- 実写真・フラットイラストをそのまま配置
- 情報を詰め込む（ただしはみ出しはNG。`word_wrap=True` を必ず維持する）

**やらない:**
- ダーク背景のタイトル/section_slide
- トピック専用に設計した2-3色パレット
- アイコンを円で囲む・角丸フレームを反復するなどのモチーフ
- `add_box` を経由しない自前の `add_shape` 呼び出し（影が残る）
- 大きな余白でゆったり見せるレイアウト
- 大きな数字だけを見せるスタットコールアウト
- `pptx_skill.py` のアクセントバー（`_rect` を細い帯として使う手法）

## ワークフロー

1. ユーザーの発表内容（見出し構成、データ、図解の内容）を箇条書きで整理する
2. `from human_pptx import new_deck, cover_slide, bullet_slide, image_text_slide, chart_slide, table_slide, diagram_slide, add_bullets, add_box, add_arrow, add_photo, highlight_run, save, COLORS` で必要な関数を読み込む
3. 1スライド1見出しパターンでスクリプトを書き、`save(prs, "output.pptx")` で `/home/z/my-project/download/` に書き出す（`pptx_skill.py` と同じ出力規約）
4. 生成後、`python3 scripts/render_preview.py <出力先pptx>` でスライドをJPEGに変換し、view で1枚ずつ確認する
   - はみ出し・重なり・影の残り（`add_shape` を直接使った箇所）がないか確認する
   - **"整いすぎて見える"場合は、むしろ本スキルの逸脱ではないか疑うこと**（配色を作り込みすぎていないか、モチーフを反復していないか、余白を取りすぎていないか）
5. `python-pptx` で再度開いて `slide.shapes` のテキストを走査するか、目視で文字の抜け・誤字を確認する

## Dependencies

`python-pptx`（pip）
LibreOffice（`soffice`）と Poppler（`pdftoppm`）— `scripts/render_preview.py` によるビジュアルQA用。無ければQAは目視での構成確認のみで進めてよい

## 同梱ファイル

```
human-report-pptx/
  SKILL.md
  scripts/
    pptx_skill.py       # ユーザー提供の元スキル（"魅せる"デザイン版、そのまま同梱）
    human_pptx.py        # 本スキルの本体。"人が作った"デザイン版のビルダー群
    render_preview.py    # pptx → JPEG のQAプレビュー生成
```

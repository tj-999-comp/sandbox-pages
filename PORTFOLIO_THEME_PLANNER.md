# Portfolio Planner Output

## 1. 各ページごとのテーマ定義（1ドキュメント集約）

目的: 各ページで色とフォントの個性を出しつつ、情報設計と操作体験は統一する。

### 共通の統一ルール（全ページ）
- レイアウトグリッド: 12カラム相当、コンテンツ最大幅 1080px
- 余白スケール: 8 / 12 / 16 / 24 / 32 / 48
- 見出し構造: h1 は1ページ1つ、h2で主要セクションを区切る
- ボタン形状: 角丸 10px で統一
- カード形状: 角丸 14px、影は弱めで統一
- アニメーション: 200-300ms、ease-out、要素出現のみ
- トーン: 読みやすさ優先、装飾は情報伝達を邪魔しない

### ページ別テーマ

| ページ | 役割 | カラーテーマ | フォント方針 | モチーフ |
|---|---|---|---|---|
| index.html | ポートフォリオ入口 | Deep Navy + Sky Cyan (#0F172A / #22D3EE / #F8FAFC) | Sans: Noto Sans JP | 信頼感、実績導線、読みやすさ |
| games/trackball-controll-practice.html | 操作練習 | Forest Green + Mint (#14532D / #34D399 / #ECFDF5) | Sans: BIZ UDPGothic | トレーニング、達成感 |
| games/trackball-typing-practice.html | タイピング練習 | Sunset Orange + Warm Gray (#9A3412 / #FB923C / #FAFAF9) | Sans: M PLUS 1p | テンポ感、集中 |
| games/typing-practice-origin.html | 原型ページ、比較 | Slate Blue + Ice (#334155 / #60A5FA / #F1F5F9) | Sans: Noto Sans JP | ベースライン、検証感 |
| keyboards/keychronk2.html | デバイス紹介 | Charcoal + Amber (#1F2937 / #F59E0B / #FFFBEB) | Serif: Noto Serif JP | 製品感、質感、信頼 |
| test/test1.html | UI検証1 | Raspberry + Blush (#881337 / #FB7185 / #FFF1F2) | Sans: Zen Kaku Gothic New | 実験的、軽快 |
| test/test2.html | UI検証2 | Indigo + Lime (#312E81 / #A3E635 / #F7FEE7) | Sans: Shippori Gothic | 比較実験、可読性検証 |

### テーマ運用ルール（ずれ防止）
- 色はページごとに変更して良いが、コントラスト基準は共通にする
- CTAボタンの配置位置は共通化する（ファーストビュー右側 or 直下）
- 主要セクション順は共通化する（概要 -> 実績/機能 -> 補足 -> CTA）
- テキスト密度は見出し:本文 = 1:3 を目安にする

---

## 2. 共通パーツ仕様（ヘッダー、フッター）

目的: ページが変わっても迷わない導線を作る。

### ヘッダー項目（全ページ共通）
- ロゴ or サイト名: Portfolio Lab
- グローバルナビ:
  - Home（index.html）
  - Games（games配下への導線）
  - Keyboards（keyboards配下）
  - Experiments（test配下）
  - Contact（mailto または SNS）
- 右側アクション:
  - Worksを見る（主要CTA）
  - GitHub

### ヘッダー実装ルール
- 高さ: 64px（モバイル 56px）
- 常時上部固定（sticky）
- 現在ページを active 表示
- モバイルはハンバーガーメニュー化
- キーボード操作可能（Tab移動、フォーカス可視化）

### フッター項目（全ページ共通）
- 左カラム:
  - サイト名
  - 1行説明（何を作っているポートフォリオか）
- 中央カラム:
  - Quick Links（Home / Games / Keyboards / Experiments）
- 右カラム:
  - External Links（GitHub / X or LinkedIn / Email）
- 最下段:
  - Copyright
  - Last Updated

### フッター実装ルール
- セクションを3カラム、モバイル時は1カラム縦積み
- 本文文字サイズは最小 14px を維持
- リンクのホバーとフォーカスを明確化

---

## 3. 推奨構成（情報設計と導線）

結論: トップページを案内ハブにし、各サブページの個性を保ちながら共通UIでつなぐ構成が最適。

### 推奨サイト構成
1. index.html
- 強み要約
- 代表実績リンク
- セクション別入口（Games / Keyboards / Experiments）

2. games 配下
- trackball-controll-practice.html
- trackball-typing-practice.html
- typing-practice-origin.html

3. keyboards 配下
- keychronk2.html

4. test 配下
- test1.html
- test2.html

### 導線優先順位
1. Home -> 代表実績（最短導線）
2. Home -> 各カテゴリ一覧
3. 各サブページ -> Home へ戻る
4. 全ページ -> Contact

### UI一貫性チェック項目
- ヘッダー項目の順序が一致している
- フッターの項目と順序が一致している
- CTA文言が共通ルールに沿っている
- モバイルでナビとフッターが崩れない

---

## 4. 次のアクション（Portfolio UI Designer への依頼文）

以下をそのまま依頼文として使用:

あなたは Portfolio UI Designer。
目的: ページごとに色とフォントの個性を保ちながら、ヘッダー/フッターを完全共通化して体験を揃える。
対象:
- index.html
- games/trackball-controll-practice.html
- games/trackball-typing-practice.html
- games/typing-practice-origin.html
- keyboards/keychronk2.html
- test/test1.html
- test/test2.html
前提:
- ページごとのカラーテーマとフォントは維持
- ヘッダーとフッターは全ページで同一仕様
依頼:
1. ヘッダーのUI案を2案（desktop/mobile）
2. フッターのUI案を2案（desktop/mobile）
3. 余白、タイポ、ナビ状態表示（active/hover/focus）のルール定義
4. モバイル時の崩れ防止ルール（折返し、メニュー階層、タップ領域）
5. 最小実装差分で適用するためのCSS設計方針
出力形式:
1. デザイン上の課題
2. 改善方針
3. レイアウト提案
4. モバイル時の注意点
5. 実装メモ

# Portfolio UI Designer 依頼文

あなたは Portfolio UI Designer。
目的: ページごとにカラーテーマとフォントの個性を維持しながら、ヘッダーとフッターを共通化してサイト全体の体験品質を揃える。
対象ページ:
- index.html
- games/trackball-controll-practice.html
- games/trackball-typing-practice.html
- games/typing-practice-origin.html
- keyboards/keychronk2.html
- test/test1.html
- test/test2.html
現状課題:
- カラーのテーマはページごとに差別化できている
- ただし、余白、タイポグラフィ、セクション順序、ナビ導線のテーマがずれている
- ヘッダーとフッターの構造がページ間で揃っていない
前提・制約:
- サイトごとにカラーテーマやフォントは異なるように維持する
- ヘッダー、フッターは全ページで共通仕様にする
- 過剰な装飾は避け、読みやすさと信頼感を優先する

依頼:
- レイアウト改善案を2案提示
- 文字サイズ、余白、コントラストの改善方針を明記
- モバイル表示での崩れ防止ポイントを列挙
- あわせて、以下の共通パーツをUIとして整理
  - ヘッダー項目: Portfolio Lab / Home / Games / Keyboards / Experiments / Contact / Worksを見る / GitHub
  - フッター項目: サイト名、1行説明、Quick Links、External Links、Copyright、Last Updated

補足要件（Planner決定事項）:
- 共通ルール
  - グリッド: 12カラム相当、最大幅1080px
  - 余白スケール: 8 / 12 / 16 / 24 / 32 / 48
  - h1は1ページ1つ、主要セクションはh2
  - ボタン角丸10px、カード角丸14px
  - 動きは200-300ms、ease-out、控えめ
- テーマ運用
  - 色はページごとに変更可。ただしコントラスト基準は共通
  - CTA位置は共通化（ファーストビュー右側 or 直下）
  - 主要セクション順は共通化（概要 -> 実績/機能 -> 補足 -> CTA）

出力形式:
1. デザイン上の課題
2. 改善方針
3. レイアウト提案
4. モバイル時の注意点
5. 実装メモ

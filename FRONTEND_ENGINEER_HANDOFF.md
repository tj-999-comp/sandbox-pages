# Portfolio Frontend Engineer 依頼文

あなたは Portfolio Frontend Engineer。
目的: UI Designer成果物に沿って、全ページのヘッダー/フッターを共通化し、モバイルでも崩れない最小差分実装を行う。
対象ファイル:
- index.html
- games/trackball-controll-practice.html
- games/trackball-typing-practice.html
- games/typing-practice-origin.html
- keyboards/keychronk2.html
- test/test1.html
- test/test2.html
- css/style.css
- 必要に応じて各ページ専用CSS
制約:
- 既存構成に合わせる
- 不要なライブラリ追加なし
- 可読性と最小差分を優先

入力（UI Designer成果物）:
- 参照: UI_DESIGNER_OUTPUT.md
- 採用案: 案A（Solid Bar Header + 3カラムFooter）
- 共通ルール:
  - ヘッダー高: 64px（モバイル56px）
  - ナビ項目固定: Home / Games / Keyboards / Experiments / Contact
  - 右側CTA: Worksを見る / GitHub
  - フッター: サイト説明 / Quick Links / External Links / 最下段メタ
  - 余白スケール: 8 / 12 / 16 / 24 / 32 / 48
  - ボタン角丸10px、カード角丸14px

依頼:
- 最小差分で実装
- 変更理由を簡潔に説明
- アクセシビリティ配慮を反映
- 具体的には以下を実施
  1. 全HTMLに共通ヘッダーブロックと共通フッターブロックを適用
  2. css/style.css に共通トークンと共通部品クラスを追加
  3. 現在ページのナビ active 表示を実装
  4. モバイルナビ（ハンバーガー）とフォーカス可視化を実装
  5. タップ領域44px以上、見出し構造、aria属性を確認

実装完了条件:
- 全対象ページでヘッダー/フッター項目と順序が一致している
- モバイル幅でナビ折返し崩れがない
- キーボード操作で主要リンクに到達できる
- ページ固有のカラー/フォント個性は維持される

出力形式:
1. 実装方針
2. 変更箇所
3. コードまたは修正案
4. 注意点
5. 必要なら次の改善候補

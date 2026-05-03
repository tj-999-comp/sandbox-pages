# Portfolio UI Designer 成果物

## 1. デザイン上の課題
- ページごとに色は差別化されているが、ナビ構造と余白ルールが統一されていない。
- ヘッダーとフッターの項目不一致により、ページ遷移時の学習コストが高い。
- CTA配置と視線誘導がページごとに異なり、主要導線の一貫性が弱い。
- モバイル時にナビ要素が詰まりやすく、タップ領域の不足が発生しやすい。

## 2. 改善方針
- 色とフォントはページ別に維持し、レイアウト骨格と共通UI部品は統一する。
- ヘッダー/フッターを全ページで同一項目・同一順序に固定する。
- 余白スケールを 8 / 12 / 16 / 24 / 32 / 48 に固定し、情報階層を揃える。
- CTAの第一ボタン位置をファーストビュー右側または直下に統一する。
- ナビ状態を active / hover / focus で明示し、キーボード操作を担保する。

## 3. レイアウト提案

### 案A: Solid Bar Header + 3カラムFooter
- ヘッダー:
  - 高さ64px（モバイル56px）
  - 左: Portfolio Lab
  - 中央: Home / Games / Keyboards / Experiments / Contact
  - 右: Worksを見る（Primary） / GitHub（Secondary）
  - sticky + 背景は各テーマ色の濃色トーン
- フッター:
  - 3カラム（左: サイト説明、中: Quick Links、右: External Links）
  - 最下段に Copyright と Last Updated
- 特徴:
  - 情報密度が高いページでも安定しやすく、実装差分が最小

### 案B: Split Header + Divider Footer
- ヘッダー:
  - 左: Portfolio Lab
  - 右: Primary CTA + メニュー開閉
  - デスクトップ時はメニューを右側展開、モバイル時はドロワー
  - sticky + 下線ボーダーで軽量感を演出
- フッター:
  - 上段2カラム（説明 / リンク群）、下段にメタ情報
  - リンクを用途別に分離（Site / Social）
- 特徴:
  - モバイルの可読性が高く、テーマカラー差分を視覚的に活かしやすい

### 採用推奨
- 初回実装は案Aを推奨。
- 理由: 既存静的構成への適用が容易で、全ページ同時反映しやすい。

## 4. モバイル時の注意点
- ヘッダー高は56px固定、タップ領域は最低44pxを確保。
- ハンバーガーメニュー内リンク間隔は12px以上。
- メニューは1階層に制限し、深い階層遷移を避ける。
- CTAは1画面内で視認できる位置に保持する。
- フッターは1カラム縦積み、リンクはカテゴリ見出し付きにする。

## 5. 実装メモ
- 共通CSSトークンを css/style.css に追加:
  - --space-8, --space-12, --space-16, --space-24, --space-32, --space-48
  - --radius-btn: 10px, --radius-card: 14px
  - --header-h-desktop: 64px, --header-h-mobile: 56px
- 共通部品クラス候補:
  - .site-header, .global-nav, .nav-link, .nav-link.is-active
  - .site-footer, .footer-grid, .footer-meta
  - .btn-primary, .btn-secondary
- ページ固有の色・フォントは各ページCSSで上書きする。
- 変更範囲は HTMLの共通ブロック追加 + 共通CSS追記に限定する。

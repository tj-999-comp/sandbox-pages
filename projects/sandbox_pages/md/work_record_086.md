# 作業記録 086: Issue #92 作業記録ページの構成とrecord間リンクを実装
作成日: 2026-09-06

## 概要

- 課題: GitHub Issue #92「作業記録ページの構成とrecord間リンクを実装する」。
- 目的: 既存URLを維持したまま、global index、project index、個別recordを相互に辿れる共通navigationを実装する。
- 完了条件: 日付降順・同日番号降順の前後順、project/global導線、source_htmlとa_renderedの相対URL、キーボードフォーカス、リンク切れ・自己リンク・孤立recordの検証を確定する。

## 適用した役割

### Portfolio Planner

- 入力: Issue #92の完了条件、親Issue #89、#90・#91の成果、既存のindex generator、provenance、公開HTML。
- 実施内容: 既存indexの一覧導線は維持し、個別recordへ共通navigationを追加する範囲へ分解した。前後順は既存indexと同じ日付降順、同日なら番号降順と定義した。metadataに明示的な関連性がないproject間リンクは生成しない。
- 成果物: project/global indexの既存URLと公開件数を基準にしたrecord navigation仕様。
- 検証結果: 現行provenanceの5project、公開record126件、source_html/a_renderedの両方式を対象範囲として確定した。
- 未解決事項: 未公開過去recordのPages反映は#93、全体運用受入は#94の対象。
- 次工程への引き継ぎ: #93へnavigation付き公開HTMLと更新provenance、#94へリンク到達性・ブラウザ確認結果を渡す。

### Portfolio UI Designer

- 入力: `DESIGN.md`、`projects/progress-index.css`、`projects/sandbox_pages/work_record.css`、既存recordページの構造。
- 実施内容: 上部にproject/globalのcontext link、同一project内の前後link、現在位置を置くnavigationを設計した。前後端は無効表示とし、自己リンクや非公開recordへのリンクを作らない。320pxでは1列に切り替え、リンクのフォーカスリングを既存CSSの方針に合わせた。
- 成果物: `record-navigation`のHTML/CSS構造。
- 検証結果: B_Stats_Siteのa_renderedページとsandbox_pagesのsource_htmlページで、PC・モバイルとも横overflowなしを確認した。
- 未解決事項: project間の関連recordは対応表またはmetadataが追加されるまで表示しない。
- 次工程への引き継ぎ: Frontend Engineerが同一markupをrendererとsource_html受入へ接続する。

### Portfolio Frontend Engineer

- 入力: `scripts/publish/index_generator.py`、`scripts/publish/rendered_renderer.py`、`scripts/publish/apply_engine.py`、`scripts/publish/content_safety.py`、5projectの最新provenance。
- 実施内容: `scripts/publish/record_navigation.py`を追加し、provenanceのpublish:true recordだけから安全な相対URLを決定的に生成するようにした。a_rendered rendererにはnavigation引数を追加し、apply時に生成する。source_htmlはapply時に同じnavigationを装飾する。既存公開HTMLは本文を再rendererせず、HEAD版へnavigationだけを注入した。
- 成果物: 共通navigation module、renderer/apply engine連携、source HTML allowlist、progress-index/work_record CSS、5projectの更新provenance、公開済み126件のnavigation付きHTML。
- 検証結果: 各projectの最新provenanceと公開ツリーのdigest driftがなく、project/global indexの生成checkに合格した。B_Stats_Siteのrecord 026で本文差分が発生しないことも確認した。
- 未解決事項: #93で未公開recordを追加する際は、同じrenderer/apply経路で前後リンクとmanifestを更新する。
- 次工程への引き継ぎ: ReviewerとTesterへ、両HTML方式・既存URL・公開件数・リンク検証の結果を引き継ぐ。

### Portfolio Reviewer

- 入力: Issue #92、実装差分、5projectのprovenance、公開HTML、index generator、navigation tests。
- 実施内容: scope外の本文改変、番号変更、自己リンク、非公開recordへのリンク、project間の推測リンク、未manifest公開を確認した。既存HTMLはnavigation追加だけであることを差分確認した。
- 成果物: 重大な未解決事項なしの事前レビュー結果。
- 検証結果: 115 unittest、index生成check、全公開recordのnavigation・リンク解決テスト、5projectのprovenance drift確認に合格した。
- 未解決事項: なし。#93で増えるrecordはbackfillの対象として別途検証する。
- 次工程への引き継ぎ: Testerの実ブラウザ結果を確認後、課題ブランチへscoped commit・pushし、PR作成へ進める。

### Portfolio Performance & Accessibility Tester

- 入力: global index、B_Stats_Siteのa_rendered record、sandbox_pagesのsource_html record、共通CSS。
- 実施内容: 1280px、900px、640px、320pxで表示し、横overflow、console/page error、failed requestを確認した。navigation linkへTabでフォーカスを移し、project indexからrecordへclick遷移するシナリオを実行した。
- 成果物: Playwright reportとシナリオ結果。
- 検証結果: 3ページ×4 viewportでHTTP 200、横overflowなし、console/page errorなし、failed requestなし。Bとsandbox_pagesの両recordでキーボードfocusとproject indexへのclick遷移に合格した。
- 未解決事項: assistive technologyそのものの実機検証は本作業範囲外だが、navigationの`aria-label`とdisabled状態をDOMで確認した。
- 次工程への引き継ぎ: #94でPages公開後の同一URLと全体リンク到達性を再確認する。

## 主要な判断

- 判断: 前後リンクは同一projectのpublish:true recordだけを対象にし、並びは日付降順、同日なら番号降順とする。
- 理由: global/project indexの既存順序と一致させ、欠番・非公開record・別projectへの誤遷移を防ぐため。
- 判断: project/global indexへの導線は全recordに表示し、関連recordのproject横断リンクは生成しない。
- 理由: 全recordに共通の戻り先を提供しつつ、明示的なmetadataまたは対応表なしの関連付けを避けるため。
- 判断: 既存公開HTMLはMarkdownから再生成せず、navigationのみを注入する。
- 理由: 過去の受入時点と現在のMarkdownが異なるrecordの本文を、Issue #92で意図せず変更しないため。

## 最終結果

- 解決したこと: global/project indexの既存導線を非回帰で維持し、公開済み126件の個別recordへproject/global・同一project前後・現在位置navigationを追加した。a_renderedとsource_htmlの両方式を同じ仕様で受入できるようにした。
- 変更ファイル: `scripts/publish/record_navigation.py`、`scripts/publish/rendered_renderer.py`、`scripts/publish/apply_engine.py`、`scripts/publish/content_safety.py`、共通CSS 3ファイル、navigation tests、公開済みrecord HTML 126件、5projectの更新provenance、本作業記録一式。
- 検証結果: 115 unittest、`python3 -m scripts.publish.index_generator --check`、`python3 scripts/dev/convert_work_records_to_html.py --check`、`python3 scripts/dev/validate_work_record_filenames.py`、`git diff --check`、5projectのprovenance drift確認に合格。ブラウザはglobal index、B_Stats_Site、sandbox_pagesを1280/900/640/320pxで確認し、HTTP 200・横overflowなし・console/page errorなし・failed requestなし。キーボードfocusとclick遷移も合格した。
- 未解決事項: #92の範囲に重大な未解決事項はない。未公開過去recordのmanifest付きPages反映は#93、全体公開後の受入は#94で実施する。
- 次アクション: #93で固定SHA・対象basename・navigation付きHTML・provenance・indexを同一backfill単位として反映する。

## GitHub Issue状況

確認日時（JST）: 2026-09-06 21:35:10
取得範囲: `tj-999-comp/sandbox-pages` のOpen Issue全件（Pull Request除外）

### 親子関係

```text
#89
├── #90
├── #91
├── #92
├── #93
└── #94
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#94 Verify/Operations 過去分公開とrecord間リンクの全体受入・運用引き継ぎ](https://github.com/tj-999-comp/sandbox-pages/issues/94) | 未完了（state reason: null） | #89の子。#92・#93完了後に全体受入を行う。 |
| 2 | P1 | [#93 Publish 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | 未完了（state reason: null） | #89の子。#90の対応表と#91・#92の整備結果を入力にする。 |
| 3 | P1 | [#92 UI/Index 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | 未完了（state reason: null） | #89の子。本作業でnavigation実装を完了し、完了コメント後に状態確認する。 |
| 4 | P2 | [#91 Migration 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | 未完了（state reason: null） | #89の子。source契約の整備済み成果を#92・#93へ引き継ぐ。 |
| 5 | P2 | [#90 Inventory 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | 未完了（state reason: null） | #89の子。対応表を#91〜#94へ引き継ぐ。 |
| 6 | P2 | [#89 Epic 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | 未完了（state reason: null） | 親Issue。#90〜#94の完了後に全体完了を判定する。 |

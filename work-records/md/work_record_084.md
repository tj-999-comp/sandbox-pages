# 作業記録 084: Issue #90 過去作業記録の棚卸しと公開対応表
作成日: 2026-09-06

## 概要

- 課題: 登録済み5生成元に存在する過去作業記録について、公開対象・除外対象・公開先の対応が一つの確定版一覧になっていなかった。
- 目的: 各生成元の固定`main` commitを基準に、Markdown・metadata・HTMLの対応、title/date、公開可否、公開側ファイル、provenanceを照合する。
- 完了条件: 全recordの対応表、補助文書・除外対象の区分、未公開候補、後続Issueへ引き継ぐ固定SHAを記録する。

## 適用した役割

### Portfolio Frontend Engineer相当

- 入力: Issue #90の完了条件、`config/sources.json`、公開側の`projects/`と`provenance/`、5生成元の`main`。
- 実施内容: 5生成元の固定SHAを取得し、source側のrecord Markdown・metadata・HTMLをbasename単位で照合した。metadataの`title`・`date`・`publish`、Markdownの見出し・作成日、公開側のMarkdown/HTML、最新provenanceを対応表へ整理した。補助文書とB側のignored HTMLもrecordから分離した。
- 成果物: [`docs/work_record_inventory.md`](../../docs/work_record_inventory.md) に166件の確定版対応表を追加した。
- 検証結果: source record 166件、公開済み126件、未公開候補40件、`publish: false`の非公開15件。全recordでMarkdownとmetadataのbasename対応、metadataとMarkdownのtitle/date一致を確認した。5生成元の固定SHAは対応表に記録した。
- 未解決事項: 未公開候補の実公開判断とPages反映は後続Issueの対象であり、本Issueでは実施していない。
- 次工程への引き継ぎ: #91は対応表の未公開候補とmetadataを入力にする。#92は公開済み126件のURLとrecord順を入力にする。#93は対応表に記録した固定SHAと公開可否を使用する。

### Portfolio Reviewer

- 入力: 対応表、source registry、公開側ファイル、provenance manifest、Issue #90の完了条件。
- 実施内容: 生成元と公開側のproject境界、補助文書の除外、`a_rendered`でのsource HTMLの扱い、公開済みrecordとprovenanceの対応、未公開候補の分類を確認した。
- 成果物: 対応表の整合性レビュー結果。
- 検証結果: 5生成元すべてでMarkdown/metadataの対応は合格。`B_Stats_Site`は31件中18件、`tech_article_nortification`は17件中2件、`NBA_Draft_DB`は1件中1件、`query_learning_BB`は34件中34件、`sandbox_pages`は83件中71件が公開側のMarkdown/HTMLと一致した。未公開候補は推測で公開せず、対応表へ明記した。
- 未解決事項: なし（Issue #90の棚卸し範囲）。
- 次工程への引き継ぎ: 後続工程は対応表を変更せず、必要なrecordだけを固定SHA・公開可否と照合して扱う。

## 主要な判断

- 判断: 生成元の現在`main` SHAをproject単位の棚卸し基準として記録し、recordごとのlast modified commitを対応表の基準にはしない。
- 理由: 同一時点のrecord・metadata・公開状態を再現可能にし、後続の固定SHA受入へ直接引き継ぐため。
- 判断: `a_rendered`生成元にsource HTMLが存在しても、A側で使用しないファイルとして明示する。
- 理由: Bの既存HTMLはsource registryのignored filesであり、tech/NBA/queryはA側rendererがHTMLを生成する契約だから。
- 判断: `publish: true`で公開側にないrecordは未公開候補として残し、`publish: false`は非公開として分離する。
- 理由: 公開可否を履歴やタイトルから推測せず、metadataと現行公開物の事実を後続判断へ渡すため。

## 最終結果

- 解決したこと: 5生成元・166件のrecordについて、固定SHA、basename、日付、title、source側ファイル、metadataの公開可否、公開側MD/HTML、provenanceを一覧化した。補助文書・除外対象と、後続工程へ渡す未公開候補を分離した。
- 変更ファイル: [`docs/work_record_inventory.md`](../../docs/work_record_inventory.md)、本作業記録のMarkdown・metadata・生成HTML。
- 検証結果: `git diff --check`、対応表の機械生成時のbasename/title/date整合チェック、公開側ファイルとprovenanceの照合に合格。HTML生成後に1280px、900px、640px、320pxでブラウザ確認する。
- 作業ブランチ: `codex/090-inventory-work-records`
- コミット: 本作業記録とIssue #90対応表を含むdocs-only commit
- PR: docs-onlyのため作成しない。最新`main`へ対象ファイルのみ直接pushする。
- PRレビュー・CI: commit前レビューとローカル検証を実施する。PR/CIは作成しない。
- 未解決事項: 未公開候補40件の公開判断・遡及反映、record間リンクの実装、Pages上の全体受入は#91〜#94の対象。
- 次アクション: 対応表を入力として#91のmetadata・HTML整備へ進む。

## GitHub Issue状況

確認日時（JST）: 2026-09-06 20:43
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue（Pull Requestを除外）。GitHub APIで6件を取得し、#89のsub-issues APIで親子関係を確認した。全件の`state_reason`は`null`。
取得件数: 6（一覧行数: 6）

### 親子関係

```text
#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する [Open / state reason: null]
├── #90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する [Open / state reason: null]
├── #91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する [Open / state reason: null]
├── #92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する [Open / state reason: null]
├── #93 [Publish] 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する [Open / state reason: null]
└── #94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う [Open / state reason: null]
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open（state reason: null） | 全体Epic。#90〜#94の完了を追跡する。 |
| 2 | 未設定 | [#90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open（state reason: null） | #89の子Issue。今回の対象。 |
| 3 | 未設定 | [#91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open（state reason: null） | #89の子Issue。対応表確定後。 |
| 4 | 未設定 | [#92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open（state reason: null） | #89の子Issue。公開対象metadata確定後。 |
| 5 | 未設定 | [#93 [Publish] 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | Open（state reason: null） | #89の子Issue。#91/#92の受入後。 |
| 6 | 未設定 | [#94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open（state reason: null） | #89の子Issue。#90〜#93の完了後。 |

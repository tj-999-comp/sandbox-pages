# 作業記録 072: Issue #84 sandbox_pages disabled受入dry-runの修復
作成日: 2026-08-31

## 概要

- 課題: GitHub Issue #84「sandbox_pagesのdisabled受入dry-runとno-opを検証する」で実workflowを実行したところ、既存作業記録のURLとHTML構文がA側validatorに拒否された。
- 目的: `enabled: false`のままsource受入条件を満たし、公開先・provenance・Pages・Slackへ副作用を発生させないno-op検証へ進める。
- 完了条件: 既存sourceの許可path、metadata、HTML/CSS/URL安全性、固定SHA、公開ツリーdrift、既存indexを検証し、実workflowでdry-run成功とapply no-opを確認する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: GitHub Issue #84、実workflow run `33398918931`、`content_safety`の失敗ログ、`work_record_005`、初期provenance manifest。
- 実施内容: `work_record_005`にあったsource directory外への相対リンクを、同一repositoryのGitHub HTTPSリンクへ変更した。Markdownの水平線が生成HTMLの`<hr>`として受入パーサーで未対応のstack要素になるため削除した。生成HTMLと公開コピーを同期し、修正後の公開digestを`operation: update`、`notify: false`のrepair manifestへ記録した。全source HTMLを対象にしたcontent safety回帰テストとrepair manifestのdriftテストを追加した。
- 成果物: `work-records/md/work_record_005.md`、`work-records/work_record_005.html`、`projects/sandbox_pages/md/work_record_005.md`、`projects/sandbox_pages/work_record_005.html`、`provenance/sandbox_pages/repair-20260831-work-record-005-links.json`、回帰テスト。
- 検証結果: sandbox_pagesのsource inventory 216件、HTML 71件のcontent safety、公開ファイル143件とrepair manifestのdriftがすべて合格した。全108テスト、index generator、HTML converter、filename validatorに合格した。
- 未解決事項: 実workflowは修正前のrunで失敗しており、修正後のmainを対象にした成功runはPRマージ後に実施する。
- 次工程への引き継ぎ: PRマージ後、最新mainの固定SHAと単一basename `work_record_072`でworkflowを再実行し、applyがno-op、deploy/Slackがskipされることを確認する。

### Portfolio Reviewer

- 入力: Issue #84の完了条件、失敗runのログ、修正差分、repair manifest、既存initial manifest、source registry、回帰テスト。
- 実施内容: 修正範囲を既存record 005のリンクとHTML構文に限定し、初期manifestを上書きせずrepair manifestを追加する方針を確認した。公開先のmetadata除外、公開ファイル件数、既存project/global index、`notify: false`を照合した。
- 成果物: 差分レビュー、source safety検証、公開digest照合結果。
- 検証結果: 修正後の全71 HTMLがA側content safetyを通過し、公開先143ファイルはrepair manifestと一致した。初期bootstrapの履歴と修復後状態は別manifestで保持されている。
- 未解決事項: GitHub Actions上の修正後dry-run/no-op、実runのartifactとworkflow URLは未取得。
- 次工程への引き継ぎ: #84の実workflow再実行結果を作業記録へ追記し、成功後にIssueを完了クローズする。

### Portfolio Performance & Accessibility Tester

- 入力: 修正後の作業記録HTML、公開コピー、受入パーサー結果。
- 実施内容: 修正対象HTMLをPCと320px幅で表示し、横overflow、console error、failed request、外部HTTPSリンクの到達形式を確認する。
- 成果物: ブラウザ確認結果。
- 検証結果: `work_record_005.html`と本作業記録HTMLを1280px、640px、320pxで確認し、HTTP 200、横overflowなし、console/page errorなし、failed requestなしを確認した。
- 未解決事項: GitHub Actionsの実workflow成功結果はPRマージ後に確認する。
- 次工程への引き継ぎ: 実workflow成功後に、no-op時のdeploy/Slack skipをrun結果で照合する。

## 主要な判断

- 判断: 既存の相対リンクをvalidatorの例外扱いにせず、GitHubのHTTPSリンクへ正規化した。
- 理由: `work-records/`の受入範囲外へ出る相対URLを許可すると、source registryで定めた境界と公開先のURL解決が不一致になるため。
- 判断: `<hr>`をHTML安全validatorへ追加許可せず、歴史的作業記録から水平線を除去した。
- 理由: 受入HTMLのallowlistとパーサーの構造解釈を広げず、表示上不要な装飾を最小差分で除去するため。
- 判断: `initial.json`は変更せず、修正後の公開状態を別のrepair manifestで記録した。
- 理由: #83の初期bootstrap時点の固定SHAとdigestを履歴として保持しつつ、現在の公開ツリーを次回受入の直前状態として照合できるようにするため。

## 最終結果

- 解決したこと: #84の初回実workflowで判明した`work_record_005`のsource directory外URLとHTML構文不備を修正し、A側の全source HTML安全検証と公開digest照合を通過させた。
- 変更ファイル: `work-records/md/work_record_005.md`、`work-records/work_record_005.html`、`projects/sandbox_pages/md/work_record_005.md`、`projects/sandbox_pages/work_record_005.html`、`provenance/sandbox_pages/repair-20260831-work-record-005-links.json`、`tests/test_content_safety.py`、`tests/test_sandbox_pages_bootstrap.py`、本作業記録のMarkdown/metadata/HTML、`projects/README.md`。
- 検証結果: 修正前workflow run [#33398918931](https://github.com/tj-999-comp/sandbox-pages/actions/runs/33398918931)はA-04 URL検証で失敗した。修正後は全108テスト、sandbox_pages content safety 71 HTML、source inventory 216件、published files 143件、repair manifest drift、index generator、converter、filename validator、ブラウザ確認に合格した。
- 作業ブランチ: `codex/072-issue-84-disabled-e2e`
- コミット: `63e8124d5017b0de204abdb270072d3efb1c984a`（修正本体）
- PR: 作成後にURLを追記する。
- PRレビュー・CI: 作成後に確認する。修正後の実workflow dry-run/no-opはPRマージ後に実施する。
- 未解決事項: 修正後のmainを対象にしたGitHub Actions実workflow成功、apply no-op、deploy/Slack skip、workflow artifact URL。
- 次アクション: PRをレビュー・マージ後、`source_commit_sha`をマージ済みmainの固定SHAへ更新して#84 workflowを再実行し、成功結果をIssueと本記録へ反映する。

## GitHub Issue状況

確認日時（JST）: 2026-08-31 22:54
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue（Pull Requestを除外）12件。GitHub App tokenで取得し、#79・#89のsub-issues APIも確認した。#83はPR #107のマージにより`CLOSED / COMPLETED`となったため一覧から除外した。state reasonはOpen Issue全件でnull。

### 親子関係

```text
#79 [Epic] sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する [Open]
（GitHub sub-issues API上の子Issueなし。#84〜#87の本文にはParent: #79があるため、着手条件欄へ記録）

#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する [Open]
├── #90 各生成元の過去作業記録を棚卸しし公開対応表を確定する [Open]
├── #91 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する [Open]
├── #92 作業記録ページの構成とrecord間リンクを実装する [Open]
├── #93 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する [Open]
└── #94 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う [Open]
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#79 [Epic] sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する](https://github.com/tj-999-comp/sandbox-pages/issues/79) | Open（state_reason: null） | 親Epic。#84〜#87の本文は#79を親としているが、sub-issues API上の子登録は確認できない。 |
| 2 | 未設定 | [#84 [E2E] sandbox_pagesのdisabled受入dry-runとno-opを検証する](https://github.com/tj-999-comp/sandbox-pages/issues/84) | Open（state_reason: null） | 本作業。#83完了後。修正後の実workflow成功とno-op確認が着手条件。 |
| 3 | 未設定 | [#85 [Activation] sandbox_pagesを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/85) | Open（state_reason: null） | #79配下。#84のレビューと明示承認後。 |
| 4 | 未設定 | [#86 [E2E] sandbox_pagesの新規作業記録をPages公開しSlack通知まで確認する](https://github.com/tj-999-comp/sandbox-pages/issues/86) | Open（state_reason: null） | #79配下。#85完了後。 |
| 5 | 未設定 | [#87 [Operations] sandbox_pagesの公開・停止・再通知手順を引き継ぐ](https://github.com/tj-999-comp/sandbox-pages/issues/87) | Open（state_reason: null） | #79配下。#86完了後。 |
| 6 | 未設定 | [#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open（state_reason: null） | 独立Epic。#90〜#94を追跡する。 |
| 7 | 未設定 | [#90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open（state_reason: null） | #89の子Issue。 |
| 8 | 未設定 | [#91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open（state_reason: null） | #89の子Issue。 |
| 9 | 未設定 | [#92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open（state_reason: null） | #89の子Issue。 |
| 10 | 未設定 | [#93 [Publish] 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | Open（state_reason: null） | #89の子Issue。 |
| 11 | 未設定 | [#94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open（state_reason: null） | #89の子Issue。 |
| 12 | 未設定 | [#102 [Operations] 作業記録のIssue状況を該当リポジトリ単位で全生成元へ統一する](https://github.com/tj-999-comp/sandbox-pages/issues/102) | Open（state_reason: null） | 独立。 |

# 作業記録 075: Issue #87 sandbox_pages公開運用の引き継ぎ
作成日: 2026-09-01

## 概要

- 課題: GitHub Issue #87「sandbox_pagesの公開・停止・再通知手順を引き継ぐ」。
- 目的: #86のE2E証跡を基に、承認、固定SHA公開、緊急停止、rollback、再開、Slack再通知の責任境界を運用可能な手順として文書化する。
- 完了条件: 固定SHA・単一basename・registry・acceptance・provenanceの確認、`publish: true`の扱い、`enabled: false`停止、Pagesを巻き戻さない通知再実行、通知対象外契約、恒久自動公開の別Issue条件を定義する。source registryの有効化とPages公開は行わない。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: Issue #87、#86のE2E結果、`accept-source.yml`、`withdraw.yml`、`slack_notification.py`、registry、provenance、既存のActions運用規約。
- 実施内容: `docs/SANDBOX_PAGES_OPERATIONS.md`へ責任境界、承認チェック、通常公開、停止、rollback、再開、通知対象外、恒久自動公開の条件を整理した。既存の受入workflowを再実行すると新しいpublication IDが発行されるため、固定apply commitと既存create manifestだけを検証してSlack通知を再実行する手動workflowを追加した。Pages公開やsource registryの値は変更していない。
- 成果物: `docs/SANDBOX_PAGES_OPERATIONS.md`、`.github/workflows/notify-publication.yml`、既存運用文書へのリンク・再通知契約の更新、workflow契約テスト。
- 検証結果: 全109テスト、workflow YAML構文、`git diff --check`に合格した。再通知workflowがPages write・OIDC・contents writeを持たず、create manifest以外を拒否することを静的確認した。
- 未解決事項: GitHub Actions上での再通知workflowの実送信は、Slackの外部副作用を伴うため今回実行していない。
- 次工程への引き継ぎ: PR反映後にCIでworkflow契約と作業記録生成物を確認し、Issue #87のmerge・closeは明示承認後に行う。

### Portfolio Reviewer

- 入力: Issue #87の完了条件、#86の初回create・再実行no-op・最終update証跡、公開・停止workflow、provenance契約。
- 実施内容: #86のrun、apply commit、publication ID、Pages URL確認結果を照合し、既存の通常受入workflowでは同一publication IDの通知だけを再実行できない差分を特定した。停止時の自動削除禁止、withdrawの明示承認、update/no-op/withdraw/bootstrapの通知抑制、恒久自動公開の別Issue条件をレビューした。
- 成果物: 運用手順のレビュー観点、再通知workflowの入力・権限境界。
- 検証結果: #86の初回runは`operation=create`、`no_op=false`、`notify=true`でPages・Slack成功、同一要求の再実行は`no_op=true`でcommit・deploy・通知なし、最終同期は`operation=update`かつ`notify=false`であることを確認した。重大な未解決事項はない。
- 未解決事項: なし。
- 次工程への引き継ぎ: GitHub上のPR差分とCI結果を再照合する。

### Portfolio Performance & Accessibility Tester

- 入力: 新規作業記録HTMLと既存のwork-record表示基準。
- 実施内容: 作業記録HTML生成後、PCと320px幅で表示、横overflow、console/page error、failed requestを確認する。
- 成果物: `work_record_075.html`の表示確認結果。
- 検証結果: 生成後に1280pxと320pxで確認し、HTTP 200、横overflowなし、console/page errorなし、failed requestなしであることを確認した。
- 未解決事項: なし。
- 次工程への引き継ぎ: HTML生成物をMarkdownと同じPRへ含める。

## 主要な判断

- 判断: 通常の`accept-source.yml`再実行を通知再送手順にせず、`notify-publication.yml`を追加する。
- 理由: 通常workflowのpublication IDはrun IDから生成されるため、再実行で同じIDを維持できず、Pages・provenanceの再処理と通知重複を招くため。
- 判断: 再通知workflowは`operation=create`かつ`notify=true`の既存manifestだけを受け付け、固定apply commitをcheckoutする。
- 理由: update、no-op、withdraw、bootstrap/backfillを通知対象外とする既存契約を、運用経路でも強制するため。
- 判断: Webhook送信結果が不明なtimeoutは、Slack到着を目視確認してから再送する。
- 理由: Incoming Webhookには通知済み判定がなく、成功済み送信の再実行は重複通知になるため。

## 最終結果

- 解決したこと: sandbox_pagesの公開承認、固定SHA・単一basename確認、停止、rollback、再開、Pagesを巻き戻さない同一publication IDのSlack再通知、通知対象外、恒久自動公開の承認条件を文書化した。再通知専用workflowを追加し、既存運用文書の誤解を招く表現も更新した。
- 変更ファイル: `.github/workflows/notify-publication.yml`、`docs/SANDBOX_PAGES_OPERATIONS.md`、`docs/ACTIONS_MAIN_POLICY.md`、`projects/README.md`、`tests/test_pages_workflow.py`、本作業記録とmetadata・生成HTML。
- 検証結果: 全109テスト、workflow YAML構文、`git diff --check`、作業記録converter、filename validator、index generator、1280px/320pxブラウザ確認に合格した。#86の実E2E証跡は運用文書へ転記し、今回のPages公開・Slack実送信は非対象として実行していない。
- 作業ブランチ: `codex/075-issue-87-operations-handoff`
- コミット: 作業中（PR作成前）。
- PR: 作業中（Issue #87と1対1で作成予定）。
- PRレビュー・CI: 作業中。
- 未解決事項: 再通知workflowの実送信は外部Slack副作用を伴うため未実行。通常運用では送信step失敗を確認したケースに限定して実行する。
- 次アクション: PRのCIとGitHub上の差分を確認し、明示承認後にmerge・Issue closeする。

## GitHub Issue状況

確認日時（JST）: 2026-09-01 00:24
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue（Pull Requestを除外）9件。GitHub App tokenで取得し、#79・#89のsub-issues APIも確認した。state reasonはOpen Issue全件でnull。

### 親子関係

```text
#79 [Epic] sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する [Open]
（GitHub sub-issues API上の子Issueなし。#87本文にはParent: #79がある）

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
| 1 | 未設定 | [#79 [Epic] sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する](https://github.com/tj-999-comp/sandbox-pages/issues/79) | Open（state_reason: null） | 親Epic。#87本文は#79を親としているが、sub-issues API上の子登録は確認できない。 |
| 2 | 未設定 | [#87 [Operations] sandbox_pagesの公開・停止・再通知手順を引き継ぐ](https://github.com/tj-999-comp/sandbox-pages/issues/87) | Open（state_reason: null） | #79配下。#86完了後。本作業。 |
| 3 | 未設定 | [#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open（state_reason: null） | 独立Epic。#90〜#94を追跡する。 |
| 4 | 未設定 | [#90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open（state_reason: null） | #89の子Issue。 |
| 5 | 未設定 | [#91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open（state_reason: null） | #89の子Issue。 |
| 6 | 未設定 | [#92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open（state_reason: null） | #89の子Issue。 |
| 7 | 未設定 | [#93 [Publish] 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | Open（state_reason: null） | #89の子Issue。 |
| 8 | 未設定 | [#94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open（state_reason: null） | #89の子Issue。 |
| 9 | 未設定 | [#102 [Operations] 作業記録のIssue状況を該当リポジトリ単位で全生成元へ統一する](https://github.com/tj-999-comp/sandbox-pages/issues/102) | Open（state_reason: null） | 独立。 |

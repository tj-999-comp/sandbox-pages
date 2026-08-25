# 作業記録 053: Issue #54 Slack投稿内容と対象作業記録URLの修正
作成日: 2026-08-25

## 概要
- 課題: Slack通知jobは成功しているが、投稿本文の情報が不足し、サイトトップURLが通知されていた。
- 目的: provenanceの対象recordに基づくタイトルと対象作業記録URLをSlackへ通知する。
- 完了条件: 投稿本文へタイトル、project、対象basename、publication_id、対象作業記録URLを含め、固定commitの公開URLを検証してから送信できる。既存のcreate専用通知とno-op非通知を維持する。

## 適用した役割
### Portfolio Frontend Engineer相当
- 入力: Issue #54、既存の`notify` job、`scripts.publish.slack_notification`、Issue #23のE2E結果。
- 実施内容: apply済み固定commitのprovenance manifestから対象recordを一意に解決し、タイトルとrecord pathを取得する処理を追加した。Pages deployのoriginとmanifest pathを結合して完全URLを作り、公開確認とSlack送信へ渡すようworkflowを変更した。Slack本文へタイトル、project、対象basenameを追加し、運用文書とテストを更新した。
- 成果物: `.github/workflows/accept-source.yml`、`scripts/publish/slack_notification.py`、`tests/test_pages_workflow.py`、`tests/test_slack_notification.py`、`docs/ACTIONS_MAIN_POLICY.md`、`projects/README.md`。
- 検証結果: 全75テスト、workflow YAML構文、URL変換、作業記録生成チェックに合格した。
- 未解決事項: GitHub Actions上の新規createによるSlack本文・リンクの実動確認はPR反映後に必要。
- 次工程への引き継ぎ: Reviewer確認後にcommit・pushし、PR作成とCI、main反映後のcreate E2EでSlack投稿本文と対象record URLを確認する。

### Portfolio Reviewer相当
- 入力: Issue #54の完了条件、実装差分、ローカルテスト結果。
- 実施内容: 通知jobがサイトトップURLを直接送信しないこと、固定commitのmanifestを参照すること、外部URLをrecord pathとして受け付けないこと、既存の通知条件を維持することを確認した。
- 成果物: 差分レビュー結果と残件判定。
- 検証結果: 重大・中・軽微の未解決事項なし。実動E2Eは未確認として扱った。
- 未解決事項: PR反映後のGitHub ActionsおよびSlack実投稿。
- 次工程への引き継ぎ: CIと実動E2Eの結果を確認し、本文・URLが期待値と一致すればIssue #54を完了扱いにする。

## 主要な判断
- 判断: 通知jobは`needs.apply.outputs.commit_sha`をcheckoutし、そのcommit内の`provenance/<project_id>/<publication_id>.json`を正本として通知情報を解決する。
- 理由: deploy対象と通知対象のmanifestを同一commitへ固定し、mainの後続変更やサイトトップURLへの依存を避けるため。
- 判断: manifestのrecord pathとPages deployのoriginを`resolve-url`で結合する。
- 理由: provenanceの`public_url`は`/sandbox-pages/projects/...`というサイト内パスであり、HTTPS検証とSlackリンクにはorigin付きの完全URLが必要なため。外部URLやquery、fragmentは拒否する。

## 最終結果
- 解決したこと: Slack本文に作業記録タイトル、project、対象basename、publication_id、対象作業記録URLを含める実装へ変更した。通知URLは固定commitの対象recordから作り、送信前に同じURLを検証する。
- 変更ファイル: `.github/workflows/accept-source.yml`、`scripts/publish/slack_notification.py`、`tests/test_pages_workflow.py`、`tests/test_slack_notification.py`、`docs/ACTIONS_MAIN_POLICY.md`、`projects/README.md`、本作業記録。
- 検証結果:
  - `python3 -m unittest discover -s tests -p 'test_*.py'`: 75件成功。
  - `python3 -m scripts.publish.slack_notification resolve-url ...`: `https://tj-999-comp.github.io/sandbox-pages/projects/B_Stats_Site/work_record_037.html`を確認。
  - Ruby YAML parserによる`.github/workflows/accept-source.yml`、`deploy-pages.yml`の構文確認: 成功。
  - `python3 scripts/dev/convert_work_records_to_html.py --check`: 成功。
  - `python3 scripts/dev/validate_work_record_filenames.py`: 52件の検証に成功。
  - `git diff --check`: 成功。
- 作業ブランチ: `codex/053-slack-record-notification`
- コミット: 作成前
- PR: 未作成
- PRレビュー・CI: 未実施
- 未解決事項: GitHub Actions上の新規create E2E、Slack実投稿内容、対象record URLのクリック先確認。
- 次アクション: 対象差分をcommit・pushし、PR作成後にCIと実動E2Eを確認する。

## GitHub Issue状況
確認日時（JST）: 2026-08-25 14:26
取得範囲: `tj-999-comp/sandbox-pages` のIssue #54、親Issue #5、関連Issue #20・#23、および同リポジトリの全Open Issue一覧。

### 親子関係
```text
#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する (CLOSED)
└── #54 [Notification] Slack投稿内容と対象作業記録URLを正しく反映する (OPEN)
```

関連Issue: #20（CLOSED、Slack通知job実装）、#23（CLOSED、受入・Pages・公開URL・SlackのE2E確認）。

### 優先順位順の未完了一覧
| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#54 Slack投稿内容と対象作業記録URLを正しく反映する](https://github.com/tj-999-comp/sandbox-pages/issues/54) | OPEN | 本作業の対象。PR反映後にCIと新規create E2Eを確認する。 |
| 2 | P1 | [#24 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | OPEN | 本作業とは独立したcritical path外の運用課題。 |
| 3 | P1 | [#13 a_rendered用の決定的rendererを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/13) | OPEN | 本作業とは独立したcritical path外のrenderer課題。 |

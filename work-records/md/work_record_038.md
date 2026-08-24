# 作業記録 038: apply時のPython bytecode生成によるE2E失敗を修正
作成日: 2026-08-24

## 概要

- 課題: A側の実publish E2Eで、apply jobが`__pycache__`を作業ツリーの変更として検出して停止した。
- 目的: Git作業ツリーのclean検査を壊さず、検証済みB sourceをAへ反映できるようにする。
- 完了条件: apply jobだけでPython bytecodeを生成しない設定を追加し、既存テスト・Workflow構文・作業記録生成を成功させる。修正をPR化し、merge後にB→A→Pages→Slackの再確認へ引き継ぐ。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: A側run #32714174339のapply jobログ、B側run #32712590804、`accept-source.yml`、`apply_engine.py`、関連テスト。
- 実施内容: `accept-source.yml`のapply stepへ`PYTHONDONTWRITEBYTECODE=1`を追加し、apply engineのimport時にRepository Aの`__pycache__`が生成されないようにした。Workflow契約テストへ設定の存在確認を追加した。
- 成果物: `.github/workflows/accept-source.yml`、`tests/test_pages_workflow.py`。
- 検証結果: unittest 73件成功、Python compile成功、Ruby YAML parser成功、`git diff --check`成功。
- 未解決事項: GitHub Actions上の修正後E2E、Pages公開、Slack受信は未確認。
- 次工程への引き継ぎ: PRをレビュー・merge後、B側#31の`work_record_026`要求を再実行してA側runを確認する。

### Portfolio Reviewer

- 入力: A側apply jobの失敗ログと最小修正差分。
- 実施内容: 失敗原因が外部sourceやSecretではなく、Python import時に生成されたRepository A内の`__pycache__`であることを確認した。設定をapply stepだけに限定し、通知Secretやdeploy jobの境界を変更していないことを確認した。
- 成果物: `tests/test_pages_workflow.py`の回帰検証。
- 検証結果: 重大な未解決事項なし。実Workflow再実行は修正PRのmerge待ち。
- 未解決事項: 修正後の実E2E。
- 次工程への引き継ぎ: PR作成後、CI成功を確認してmergeし、A側accept-source runのapply・deploy・notifyを順に確認する。

## 主要な判断

- 判断: `apply_engine.py`のclean検査を緩めず、Workflowのapply stepへ`PYTHONDONTWRITEBYTECODE=1`を設定した。
- 理由: `__pycache__`以外の意図しない変更を見逃さず、実行時に生成されるbytecodeだけを抑制する最小変更とするため。

## 最終結果

- 解決したこと: apply engineのimportでRepository Aがdirtyになる問題への修正を実装した。
- 変更ファイル:
  - `.github/workflows/accept-source.yml`
  - `tests/test_pages_workflow.py`
  - `work-records/md/work_record_038.md`
- 検証結果: `PYTHONPYCACHEPREFIX=/tmp/issue38_pycache python3 -m unittest discover -s tests -p 'test_*.py'`（73件成功）、Python compile（成功）、Ruby YAML parser（成功）、`git diff --check`（成功）。
- 作業ブランチ: `codex/038-fix-apply-pycache`
- コミット: `ad6cbf6 fix: prevent apply bytecode in repository worktree`
- PR: [#41 E2E再実行のためapply時の__pycache__生成を防止](https://github.com/tj-999-comp/sandbox-pages/pull/41)（Draft / OPEN）。
- PRレビュー・CI: ローカル事前レビュー合格。GitHub Actions Validate [run #32714793120](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32714793120)はSUCCESS。
- 未解決事項: 修正後のA側apply、Pages deploy、公開URL、Slack通知、no-op再実行の実確認。
- 次アクション: PR #41のレビュー・merge後、B側#31のpublish要求を再実行して実E2Eを確認する。mergeは自動実行しない。

## GitHub Issue状況

確認日時（JST）: 2026-08-24 19:01
取得範囲: `tj-999-comp/sandbox-pages`の#20・#23・#24、および`tj-999-comp/B_Stats_Site`の#30〜#32。今回のE2Eと修正の依存関係にあるIssueを個別取得した。

### 親子関係

```text
sandbox-pages #5
├── sandbox-pages #20（Closed / completed）
└── sandbox-pages #23（Open、今回の実E2E）

B_Stats_Site #30（Closed / completed）
└── B_Stats_Site #31（Open / reopened、work_record_026のpublish要求）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open | 修正PRのmerge後、B側#31のpublish要求を再実行して確認する。 |
| 2 | 未設定 | [B_Stats_Site #31 [E2E] 新規作業記録1件を手動publish要求する](https://github.com/tj-999-comp/B_Stats_Site/issues/31) | Open / reopened | `work_record_026`のA側publishが今回の修正後に未完了。 |
| 3 | 未設定 | [#24 [Operations] 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | Open | 今回のE2Eとは独立。 |
| 4 | 未設定 | [B_Stats_Site #32 [Automation] main更新時の公開要求triggerを有効化する](https://github.com/tj-999-comp/B_Stats_Site/issues/32) | Open | #23完了後の自動化課題。 |

### 完了済みの関連Issue

| GitHub Issue | 状態 | 本作業との関係 |
| --- | --- | --- |
| [#20 [Notification] deploy成功後のSlack通知jobを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/20) | Closed / completed | 通知jobの実装は完了済み。 |
| [B_Stats_Site #30 [Actions] 手動公開要求workflowとdispatch権限を設定する](https://github.com/tj-999-comp/B_Stats_Site/issues/30) | Closed / completed | BからAをdispatchする前提。 |

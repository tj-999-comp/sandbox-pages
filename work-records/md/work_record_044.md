# 作業記録 044: Issue #23 no-op入力のworkflow_call検証修正
作成日: 2026-08-25

## 概要

- 課題: PR #45 merge後のno-op E2EでもA側accept-source runがfailureとなり、called workflowのjobが生成されなかった。
- 目的: no-op時に空のcommit SHAを渡してもreusable workflowの入力検証で失敗せず、no-op完了jobを実行できるようにする。
- 完了条件: `workflow_call.commit_sha`の任意入力化、CI、no-op実E2E、commit・Pages deploy・Slack通知なしを確認する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: PR #45 merge commit `cd8d0cc78a37e2b04eb412bd3569ceb884188064`、B側run #32797343514、A側run #32797547899、accept-source apply logic。
- 実施内容: `deploy-pages.yml`の`workflow_call.commit_sha`を`required: false`・空defaultへ変更した。no-op時はapplyが空SHAを渡して完了jobへ進み、create時はbuild jobの既存完全SHA検証で不正入力を拒否する。workflow契約テストとActions方針を更新した。
- 成果物: `.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: unit test 73件、Python構文、両workflow YAML構文、`git diff --check`に合格した。
- 未解決事項: 修正後CI、no-op実E2E、create実E2Eは未確認。
- 次工程への引き継ぎ: PR merge後に同じ固定SHAでno-op runを再実行し、called workflow jobの成功とdeploy・通知なしを確認する。

### Portfolio Reviewer

- 入力: A側run #32797547899のjob構成、A側mainの`accept-source.yml`と`deploy-pages.yml`。
- 実施内容: strict comparison修正後もcalled workflowのjobが生成されなかった事実を確認した。apply artifactではno-op時の`commit_sha`が空であり、`workflow_call.commit_sha required: true`によるjob生成前の入力検証失敗と切り分けた。
- 成果物: 入力契約の原因分析と最小差分レビュー。
- 検証結果: 修正範囲はPages workflow、契約テスト、運用方針、作業記録に限定した。
- 未解決事項: GitHub Actions上での入力任意化確認。
- 次工程への引き継ぎ: CI合格後、同一固定SHAのno-op E2Eを再実行する。

## 主要な判断

- 判断: `workflow_call.commit_sha`だけを任意入力にし、`workflow_dispatch.commit_sha`は必須のまま維持する。
- 理由: no-opのcallerは空SHAを渡す必要がある一方、手動Pages deployとcreate時のbuildは完全SHAを要求するため。create時のSHA検証責務はcalled workflowのbuild jobに残す。
- 判断: no-op時の空SHAをbuild jobで検証しない。
- 理由: `should_deploy != true`のno-op jobだけを成功実行し、Pages artifact・deploy・Slack通知を発生させない設計だから。

## 最終結果

- 解決したこと: no-op時に空commit SHAがreusable workflowの必須入力検証で弾かれ、jobが生成されない経路を修正した。
- 変更ファイル:
  - `.github/workflows/deploy-pages.yml`
  - `tests/test_pages_workflow.py`
  - `docs/ACTIONS_MAIN_POLICY.md`
  - `work-records/md/work_record_044.md`
  - `work-records/work_record_044.html`
- 検証結果: ローカルunit test 73件、Python構文、YAML構文、`git diff --check`に合格。CI・修正後E2Eは継続確認する。
- 作業ブランチ: `codex/044-issue23-noop-input`
- コミット: 作業記録作成時点では未commit。
- PR: 作業記録作成時点では未作成。
- 未解決事項: 修正後no-op受入run、create実publish、Pages公開URL、Slack通知、外部レビュー。
- 次アクション: commit・push・PR作成・merge後、固定SHAで実E2Eを実行し、必要なら修正と再検証を繰り返す。

## GitHub Issue状況

確認日時（JST）: 2026-08-25 10:29
取得範囲: `tj-999-comp/sandbox-pages`の#23・#24、および`tj-999-comp/B_Stats_Site`の#31・#32をGitHub APIで個別取得した時点のsnapshot。

### 親子関係

```text
sandbox-pages #5
├── sandbox-pages #23（Open / reopened、今回のE2E）
└── sandbox-pages #24（Open）

B_Stats_Site #31（Open / reopened、今回のpublish要求）
└── B_Stats_Site #32（Open、後続自動化）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open / reopened | 今回の対象。no-opとcreateの実E2Eを完了する。 |
| 2 | 未設定 | [B_Stats_Site #31 [E2E] 新規作業記録1件を手動publish要求する](https://github.com/tj-999-comp/B_Stats_Site/issues/31) | Open / reopened | #23の固定SHA入力要求。 |
| 3 | 未設定 | [#24 [Operations] 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | Open | #23とは独立した後続運用課題。 |
| 4 | 未設定 | [B_Stats_Site #32 [Automation] main更新時の公開要求triggerを有効化する](https://github.com/tj-999-comp/B_Stats_Site/issues/32) | Open | #23/#31完了後の自動化課題。 |

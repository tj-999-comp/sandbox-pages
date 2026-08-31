# 作業記録 045: Issue #23 should_deploy入力型の安定化
作成日: 2026-08-25

## 概要

- 課題: PR #46 merge後もA側accept-source no-op runがfailureとなり、called Pages workflowのjobが生成されなかった。
- 目的: reusable workflowの`should_deploy`入力をGitHub Actionsの型変換に依存しない形へ変更し、no-op完了jobとcreate deploy jobを確実に分岐させる。
- 完了条件: string入力によるno-op実E2Eの成功、deploy・commit・Slack通知なし、create経路の実行確認。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: PR #46 merge commit `4cac41932b81ee32e14a67398c431777019b1da8`、B側run #32798110397、A側run #32798340012、workflow_call入力定義。
- 実施内容: `should_deploy`のworkflow_call型をbooleanからstringへ変更し、defaultを`"true"`へ設定した。called workflow内部では`'true'`との文字列比較でcreate/no-opを分岐する。`commit_sha`任意入力と空SHA検証のcreate側契約は維持した。
- 成果物: `.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: unit test 73件、Python構文、両workflow YAML構文、`git diff --check`に合格した。
- 未解決事項: 修正後CI、no-op実E2E、create実E2Eは未確認。
- 次工程への引き継ぎ: PR merge後に同じ固定SHAでno-op runを再実行し、called workflowのno-op完了job成功を確認する。

### Portfolio Reviewer

- 入力: A側run #32798340012のjob構成と、PR #46で`commit_sha`任意化後もjobが生成されなかった結果。
- 実施内容: no-op apply自体は成功していたが、reusable workflowがjob生成前に終了していた。commit_sha入力制約解消後も継続したため、callerから渡す`should_deploy`のboolean型変換を次の入力契約境界として切り分け、string比較へ変更した。
- 成果物: 入力型に依存しない分岐方針と差分レビュー。
- 検証結果: 変更範囲はPages workflow、契約テスト、運用方針、作業記録に限定した。
- 未解決事項: GitHub Actions上のstring入力結果。
- 次工程への引き継ぎ: CI後にno-op E2Eを再実行し、job構成と親run結論を照合する。

## 主要な判断

- 判断: `should_deploy`をbooleanではなくstringの`'true'` / `'false'`として扱う。
- 理由: callerのjob outputからworkflow_call inputへの型変換でjob生成前失敗が続いたため。stringとして受け、called workflow内部で明示比較すれば、入力経路の型変換に依存しない。
- 判断: create側は`should_deploy == 'true'`のときだけ完全SHAを検証し、no-op側は`!= 'true'`の完了jobへ進める。
- 理由: no-op時の空SHAをPages buildへ渡さず、create時の固定SHA保護を維持するため。

## 最終結果

- 解決したこと: should_deployのworkflow_call boolean型変換に依存する分岐をstring比較へ変更した。
- 変更ファイル:
  - `.github/workflows/deploy-pages.yml`
  - `tests/test_pages_workflow.py`
  - `docs/ACTIONS_MAIN_POLICY.md`
  - `work-records/md/work_record_045.md`
  - `work-records/work_record_045.html`
- 検証結果: ローカルunit test 73件、Python構文、YAML構文、`git diff --check`に合格。CI・修正後E2Eは継続確認する。
- 作業ブランチ: `codex/045-issue23-string-gate`
- コミット: 作業記録作成時点では未commit。
- PR: 作業記録作成時点では未作成。
- 未解決事項: 修正後no-op受入run、create実publish、Pages公開URL、Slack通知、外部レビュー。
- 次アクション: commit・push・PR作成・merge後、固定SHAで実E2Eを実行し、必要なら修正と再検証を繰り返す。

## GitHub Issue状況

確認日時（JST）: 2026-08-25 10:43
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

# 作業記録 043: Issue #23 should_deploy真偽値判定の修正
作成日: 2026-08-25

## 概要

- 課題: PR #44 merge後のno-op E2Eでもcalled Pages workflowのno-op jobがskipされ、A側accept-source runがfailureになった。
- 目的: `should_deploy`をbooleanとして厳密に判定し、no-op時の完了jobとcreate時のPages deployを正しい分岐で実行する。
- 完了条件: no-op jobが成功し、no-op時にcommit・Pages deploy・Slack通知が発生しないことを実E2Eで確認する。create経路も同一runのdeploy・公開URL・Slackまで確認する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: PR #44 merge commit `9f29f9e1afb1d388f166a2245ec47496561d4329`、B側run #32796301046、A側run #32796503696、A側apply artifact。
- 実施内容: called workflowの条件を`inputs.should_deploy == true`（create時のbuild/deploy）と`inputs.should_deploy != true`（no-op完了job）へ変更した。文字列`"false"`として評価される場合でもno-op側へ収束する。契約テストへ両条件を追加した。
- 成果物: `.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、本作業記録。
- 検証結果: unit test 73件、Python構文、両workflow YAML構文、`git diff --check`に合格した。
- 未解決事項: 修正後CI、no-op実E2E、create実E2Eは未確認。
- 次工程への引き継ぎ: PR merge後に同じ固定SHAでno-op runを再実行し、called workflowの成功とdeploy・通知なしを確認する。

### Portfolio Reviewer

- 入力: A側run #32796503696のjob構成。dry-run・applyは成功、notify jobはskip、called workflowのjobは表面化しなかった。
- 実施内容: PR #44のno-op完了job追加後もno-op jobがskipされたことを確認し、`!inputs.should_deploy`の暗黙真偽値評価を原因候補として切り分けた。strict boolean comparisonへ変更する差分をレビューした。
- 成果物: 再現事実と最小修正方針。
- 検証結果: 変更範囲はPages workflowと契約テスト、作業記録に限定する。
- 未解決事項: GitHub Actions上のstrict comparison結果。
- 次工程への引き継ぎ: CI合格後、no-op実E2Eを再実行し、失敗ならさらにログを確認する。

## 主要な判断

- 判断: `!inputs.should_deploy`ではなく`inputs.should_deploy != true`をno-op条件に使う。
- 理由: reusable workflow inputが文字列`"false"`として渡る場合、非空文字列の否定はfalseになり、no-op jobがskipされる可能性があるため。strict comparisonならboolean falseと文字列falseの双方をdeploy側から排除できる。
- 判断: create側も`== true`へ変更する。
- 理由: no-op入力の型が不確実でも、Pages deployを誤って実行しないことを優先するため。

## 最終結果

- 解決したこと: should_deployの暗黙真偽値評価をstrict comparisonへ変更した。
- 変更ファイル:
  - `.github/workflows/deploy-pages.yml`
  - `tests/test_pages_workflow.py`
  - `work-records/md/work_record_043.md`
  - `work-records/work_record_043.html`
- 検証結果: ローカルunit test 73件、Python構文、YAML構文、`git diff --check`に合格。CI・修正後E2Eは継続確認する。
- 作業ブランチ: `codex/043-issue23-boolean-gate`
- コミット: 作業記録作成時点では未commit。
- PR: 作業記録作成時点では未作成。
- 未解決事項: 修正後no-op受入run、create実publish、Pages公開URL、Slack通知、外部レビュー。
- 次アクション: commit・push・PR作成後、CIと実E2Eを確認し、必要なら修正と再検証を繰り返す。

## GitHub Issue状況

確認日時（JST）: 2026-08-25 10:15
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

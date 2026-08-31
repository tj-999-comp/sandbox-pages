# 作業記録 046: Issue #23 reusable workflow concurrencyの分離
作成日: 2026-08-25

## 概要

- 課題: PR #47 merge後もA側accept-source no-op runがfailureとなり、called Pages workflowのjobが生成されなかった。
- 目的: callerが`pages-production-main`を保持したままcalled workflowを待つ競合を避け、reusable invocationを実行可能にする。
- 完了条件: reusable invocationだけ一意concurrency groupを使い、no-op実E2Eをsuccessにする。push・手動dispatchのPages deployは従来の共有groupを維持する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: PR #47 merge commit `0522cf3f1ff9b24db53633ff41aa6dff15af2b4e`、B側run #32798939197、A側run #32799133601、`accept-source.yml`と`deploy-pages.yml`。
- 実施内容: `deploy-pages.yml`のconcurrency groupを、`workflow_call`時は`pages-production-reusable-${{ github.run_id }}`相当の一意group、push・手動dispatch時は`pages-production-main`へ分岐させた。workflow契約テストとActions方針を更新した。
- 成果物: `.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: unit test 73件、Python構文、両workflow YAML構文、`git diff --check`に合格した。
- 未解決事項: 修正後CI、no-op実E2E、create実E2Eは未確認。
- 次工程への引き継ぎ: PR merge後に同じ固定SHAでno-op runを再実行し、called workflow jobの生成・成功を確認する。

### Portfolio Reviewer

- 入力: A側run #32799133601のjob構成と、PR #47 merge後のmain workflow。
- 実施内容: commit_sha任意化とshould_deploy string化後もcalled workflowのjobが表示されず、caller/apply/notifyだけで親runがfailureになった事実を確認した。callerとcalledが同一concurrency groupを共有しているため、caller保持中にcalledが同groupを要求する境界を修正対象とした。
- 成果物: concurrency分離方針と差分レビュー。
- 検証結果: push・手動dispatchの共有groupを維持し、reusable invocationだけを一意groupへ分離する最小差分であることを確認した。
- 未解決事項: GitHub Actions上のreusable job生成結果。
- 次工程への引き継ぎ: CI後にno-op E2Eを再実行し、job構成・親run結論・外部Pages runの有無を照合する。

## 主要な判断

- 判断: called workflowのconcurrency groupをrun単位で一意化する。
- 理由: callerの受入runが`pages-production-main`を保持したままcalled workflowを待つ競合を避けるため。callerが他の受入・通常Pages処理を直列化する責務は維持する。
- 判断: push・手動dispatchのPages workflowは`pages-production-main`を維持する。
- 理由: 通常の公開経路と手動deployの相互排他を崩さないため。

## 最終結果

- 解決したこと: caller/called間で同一concurrency groupを待ち合わせる可能性を解消した。
- 変更ファイル:
  - `.github/workflows/deploy-pages.yml`
  - `tests/test_pages_workflow.py`
  - `docs/ACTIONS_MAIN_POLICY.md`
  - `work-records/md/work_record_046.md`
  - `work-records/work_record_046.html`
- 検証結果: ローカルunit test 73件、Python構文、YAML構文、`git diff --check`に合格。CI・修正後E2Eは継続確認する。
- 作業ブランチ: `codex/046-issue23-reusable-concurrency`
- コミット: 作業記録作成時点では未commit。
- PR: 作業記録作成時点では未作成。
- 未解決事項: 修正後no-op受入run、create実publish、Pages公開URL、Slack通知、外部レビュー。
- 次アクション: commit・push・PR作成・merge後、固定SHAで実E2Eを実行し、必要なら修正と再検証を繰り返す。

## GitHub Issue状況

確認日時（JST）: 2026-08-25 11:00
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

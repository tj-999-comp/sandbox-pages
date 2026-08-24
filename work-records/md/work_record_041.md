# 作業記録 041: Issue #23 reusable Pages deploy条件の修正
作成日: 2026-08-25

## 概要

- 課題: Issue #23の実publish E2Eで、A側accept-source runのapply成功後にPages deployが同一runで実行されず、Slack通知がskippedになった。
- 目的: GitHub Actionsのreusable workflow呼び出しを正しい条件分岐へ修正し、createとno-opの両方で受入workflowの完了状態を正しくする。
- 完了条件: caller workflowの構文制約に適合し、create時に同一run内の固定SHA Pages deployと公開URL受け渡しが行われ、no-op時にdeploy・通知を行わないことをローカル検証、CI、実E2Eで確認する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: `work_record_039`・`work_record_040`、A側run #32715367822、apply artifact、`.github/workflows/accept-source.yml`、`.github/workflows/deploy-pages.yml`。
- 実施内容: `uses: ./.github/workflows/deploy-pages.yml`のcaller jobから`if`を除去し、`should_deploy` booleanをcalled workflowへ渡す構成へ変更した。called workflow内部でworkflow_call時だけ`should_deploy`を評価し、push・手動dispatchの既存経路は維持した。静的テストへcreate/no-op分岐の契約を追加した。
- 成果物: `accept-source.yml`、`deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: unit test 73件、Python構文、両workflow YAML構文、index生成check、作業記録検証、`git diff --check`に合格した。
- 未解決事項: CIと修正後の実GitHub Actions E2Eは作業記録作成時点で未実行。
- 次工程への引き継ぎ: PRのCI合格後、B側固定SHA `8210edbcd271089d6942ce44371a90261bcfc0a0`・`work_record_026`で受入workflowを再実行し、Pages URL・Slack・同一要求no-opを確認する。

### Portfolio Reviewer

- 入力: 公式GitHub Actionsのreusable workflow仕様、実run #32715367822のjob構成とapply artifact。
- 実施内容: `no_op=false`、`operation=create`、`notify=true`でもcallerの`deploy` child jobが存在せず、push起点の別Pages runだけが成功していたことを照合した。caller jobの`if`を使わず、called workflow内部へ条件を移す差分を確認した。
- 成果物: 原因分析と最小差分レビュー。
- 検証結果: 変更範囲は受入・Pages workflow、workflow契約テスト、運用方針文書に限定され、既存のpublish実装・公開成果物・provenanceを変更していない。
- 未解決事項: 実環境での修正後run確認。
- 次工程への引き継ぎ: CIと実E2Eの結果を作業記録へ追記し、失敗時はworkflowを再修正する。

## 主要な判断

- 判断: caller側のreusable workflow jobに条件を残さず、`should_deploy`をcalled workflow内部のjob条件へ移した。
- 理由: GitHub公式仕様では、reusable workflowを呼ぶjobで使用できるキーが限定され、`if`はcaller側の許可キーに含まれない。実runでも条件が真のapply後にdeploy child jobが生成されず、通知が実行できなかった。
- 判断: no-opでもcalled workflow jobを呼び出し、内部条件でbuild/deployをskipする。
- 理由: caller側で`if`を使わずにno-op時のdeployを止めるため。create時はcalled workflowの`page_url` outputを通知jobへ渡し、no-op時は通知条件もfalseになる。

## 最終結果

- 解決したこと: reusable Pages workflowの条件分岐をGitHub Actionsのcaller契約に適合する形へ修正した。
- 変更ファイル:
  - `.github/workflows/accept-source.yml`
  - `.github/workflows/deploy-pages.yml`
  - `tests/test_pages_workflow.py`
  - `docs/ACTIONS_MAIN_POLICY.md`
  - `work-records/md/work_record_041.md`
  - `work-records/work_record_041.html`
- 検証結果: ローカルunit test 73件、Python構文、YAML構文、index生成check、作業記録・filename検証、`git diff --check`に合格。CI・実E2Eは継続確認する。
- 作業ブランチ: `codex/041-issue23-e2e-fix`
- コミット: 作業記録作成時点では未commit。
- PR: 作業記録作成時点では未作成。
- 未解決事項: 修正後のaccept-source成功、固定SHA Pages deploy、公開URL、Slack通知、同一要求no-op、CI・PRレビュー。
- 次アクション: commit・push・PR作成後、CIと実E2Eを確認し、必要なら修正と再検証を繰り返す。

## GitHub Issue状況

確認日時（JST）: 2026-08-25 08:41
取得範囲: `tj-999-comp/sandbox-pages`の#20・#22〜#24、および`tj-999-comp/B_Stats_Site`の#31をGitHub APIで個別取得した時点のsnapshot。

### 親子関係

```text
sandbox-pages #5
├── sandbox-pages #20（Closed / completed）
├── sandbox-pages #22（Closed / completed）
├── sandbox-pages #23（Open、今回のE2E）
└── sandbox-pages #24（Open、今回とは独立）

B_Stats_Site #31（Open / reopened、今回の入力要求）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open | 今回の対象。修正後CIと実E2Eを完了する。 |
| 2 | 未設定 | [B_Stats_Site #31 [E2E] 新規作業記録1件を手動publish要求する](https://github.com/tj-999-comp/B_Stats_Site/issues/31) | Open / reopened | 固定SHA `8210edb...`の再publish要求。#23の実E2E入力。 |
| 3 | 未設定 | [#24 [Operations] 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | Open | #23とは独立した後続運用課題。 |

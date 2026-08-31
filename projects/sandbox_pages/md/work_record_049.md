# 作業記録 049: Issue #23 no-op時のcaller skip
作成日: 2026-08-25

## 概要
- 課題: PR #50のmainマージ後も、A側runでapply成功後のreusable workflow jobが生成されず、親runがfailureになる。
- 目的: no-op時にreusable workflowを呼ばず、publicationがある場合だけ固定SHA deployを呼ぶ構造へ整理する。
- 完了条件: no-opのB→A実E2Eがsuccessとなり、Pages deployとSlack通知が実行されないことを確認する。

## 適用した役割
### Portfolio Frontend Engineer相当
- 入力: PR #50 merge commit `ea647de9c1435b5e0f6339ad4da4bc32af980395`、B側run #32803076203、A側run #32803266136、GitHub Actions公式のreusable workflow caller仕様。
- 実施内容: `accept-source.yml`のdeploy callerへ`apply.no_op != 'true'`の`if`を戻し、no-op時はcaller自体をskipする。`deploy-pages.yml`はno-op入力とnoop jobを削除し、`workflow_call.commit_sha`をrequiredに戻してpublication時だけbuild/deployする。
- 成果物: `.github/workflows/accept-source.yml`、`.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: 追加修正後のローカル検証とGitHub Actions再実行は未完了。
- 未解決事項: no-op時の親run成功とdeploy caller skipの実動確認。
- 次工程への引き継ぎ: ローカル検証、HTML検証、PR、mainマージ後にB→Aを再実行する。

### Portfolio Reviewer相当
- 入力: A側run #32803266136の全job一覧とapply artifact（`no_op=true`、commit SHAなし）。
- 実施内容: dry-run/applyは成功したが、called workflowのjobが一度も作成されず、入力修正では解消しなかったことを確認した。no-opをcalled workflow内部で扱うより、callerの明示的skipに分離する方針へ差し戻した。
- 成果物: 構造変更方針と再検証条件。
- 検証結果: 修正前runはfailure。Issue #23は未完了として継続する。
- 未解決事項: 構造変更後の実動結果。
- 次工程への引き継ぎ: no-op skipとcreate deployの双方を確認する。

## 主要な判断
- 判断: no-op処理をreusable workflow内の条件分岐からcaller側のjob skipへ移す。
- 理由: no-opではdeployに必要なcommit SHAが存在せず、called workflowのjobを全skipして親runを完了させる構造が実行環境で安定しなかったため。

## 最終結果
- 解決したこと: no-op時に空SHAを渡すreusable invocationを発生させない構成へ変更した。検証は継続中。
- 変更ファイル: `.github/workflows/accept-source.yml`、`.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: 追加修正後は未検証。
- 未解決事項: Issue #23のno-op E2E成功確認とcreate経路確認。
- 次アクション: テスト、作業記録HTML検証、PR作成・マージ、B→A再実行、A側job・artifact・Pages・Slack結果の確認。

## GitHub Issue状況
確認日時（JST）: 2026-08-25 12:00
取得範囲: `tj-999-comp/sandbox-pages` Issue #23、`tj-999-comp/B_Stats_Site` Issue #31、およびIssue #23の受入run。

### 親子関係
```text
親子関係なし
```

### 優先順位順の未完了一覧
| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | OPEN（REOPENED） | 本作業の対象。no-op E2E成功とcreate経路の最終確認が必要。 |
| 2 | P0 | [#31 [E2E] 新規作業記録1件を手動publish要求する](https://github.com/tj-999-comp/B_Stats_Site/issues/31) | OPEN（REOPENED） | B側からの入力供給元。#23の受入再実行に使用。 |

# 作業記録 048: Issue #23 空commit SHA入力の正規化
作成日: 2026-08-25

## 概要
- 課題: Issue #23のA側runでdry-run/applyが成功しても、reusable Pages workflowのjobが生成されず親runがfailureになる。
- 目的: no-op時にapply outputの空commit SHAをreusable workflowのstring inputへ安全に渡す。
- 完了条件: no-opのB→A実E2Eがsuccessとなり、Pages deployとSlack通知が実行されないことを確認する。

## 適用した役割
### Portfolio Frontend Engineer相当
- 入力: PR #49 merge commit `ecce29a4d2c45aa35693dba8545694228355479f`、B側run #32802251667、A側run #32802440311。
- 実施内容: reusable workflow callerの`commit_sha`入力を、`needs.apply.outputs.commit_sha || ''`で空文字へ正規化して渡す。no-op時の`no_op`文字列伝播とcalled workflow内の分岐は維持する。
- 成果物: `.github/workflows/accept-source.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: 追加修正後のローカル検証とGitHub Actions再実行は未完了。
- 未解決事項: A側reusable workflow jobの生成と親run成功。
- 次工程への引き継ぎ: ローカル検証、HTML検証、PR、mainマージ後にB→Aを再実行する。

### Portfolio Reviewer相当
- 入力: A側run #32802440311のjob一覧と、GitHub Actions公式のreusable workflow input仕様。
- 実施内容: dry-run/apply成功、notify skipped、called workflow job未生成という再現結果を確認した。no-opではcommit SHAが空であり、optional string inputへ明示的な空文字を渡す境界を追加する。
- 成果物: 追加修正方針と再検証条件。
- 検証結果: 修正前runはfailure。Issue #23は未完了として継続する。
- 未解決事項: 追加修正後の実動結果。
- 次工程への引き継ぎ: 修正後に同じB入力で再実行し、called workflowの実jobを確認する。

## 主要な判断
- 判断: no-op時の空commit SHAをcallerのexpressionで空文字へ正規化する。
- 理由: `workflow_call`のoptional string inputにnullを渡す境界を避け、no-op jobがcommit SHAなしで成立できる契約を明確にするため。

## 最終結果
- 解決したこと: no-opの空commit SHAをreusable workflowへ渡す入力境界を明示した。検証は継続中。
- 変更ファイル: `.github/workflows/accept-source.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: 追加修正後は未検証。
- 未解決事項: Issue #23のno-op E2E成功確認。
- 次アクション: テスト、作業記録HTML検証、PR作成・マージ、B→A再実行、A側job・artifact・Pages・Slack結果の確認。

## GitHub Issue状況
確認日時（JST）: 2026-08-25 11:00
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

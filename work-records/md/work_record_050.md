# 作業記録 050: Issue #23 called workflow concurrencyの除去
作成日: 2026-08-25

## 概要
- 課題: caller側のno-op skip構造へ変更しても、create経路でreusable Pages workflowのdeploy callerが生成されず親runがfailureになる。
- 目的: reusable invocation時にcallerの共有concurrencyとcalled workflowのworkflow-level concurrencyが競合しない構成にする。
- 完了条件: create経路でcalled workflowのbuild/deployが実行され、Pages公開URL確認とSlack通知までsuccessになる。no-op経路のsuccessも維持する。

## 適用した役割
### Portfolio Frontend Engineer相当
- 入力: PR #51 merge commit `f3336fc5be8ea5f4ba664559a4891e19aad0eb26`、create候補のA側run #32804468437、GitHub Actions公式のreusable workflow仕様。
- 実施内容: `deploy-pages.yml`からworkflow-level `concurrency`を除去し、caller側`accept-source.yml`の`pages-production-main`共有concurrencyだけで受入とPagesの直列化を担保する。workflow_callのbuild/deploy契約は維持する。
- 成果物: `.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: 追加修正後のローカル検証とGitHub Actions再実行は未完了。
- 未解決事項: create経路のcalled workflow job生成、Pages、Slack。
- 次工程への引き継ぎ: ローカル検証、HTML検証、PR、mainマージ後にcreateとno-opを再実行する。

### Portfolio Reviewer相当
- 入力: A側create run #32804468437の全job一覧。dry-run/applyはsuccess、deploy caller未生成、notify skipped、親run failure。
- 実施内容: no-op判定、空SHA、caller ifを順に切り分けた結果、createでも同じ未生成症状が残ったため、called workflowのworkflow-level concurrencyを最後の共通要因として差し戻した。
- 成果物: concurrency除去方針と再検証条件。
- 検証結果: 修正前create runはfailure。Issue #23は未完了として継続する。
- 未解決事項: called workflow実動結果。
- 次工程への引き継ぎ: create成功後にno-op非回帰を再確認する。

## 主要な判断
- 判断: reusable workflow側のworkflow-level concurrencyを除去し、caller側だけで直列化する。
- 理由: GitHub Actions上でcaller jobが保持する共有groupとcalled workflow側groupを複数層に定義すると、called jobが生成されない症状がcreate/no-op双方で再現したため。

## 最終結果
- 解決したこと: called workflowが独自にconcurrency groupを要求しない構成へ変更した。検証は継続中。
- 変更ファイル: `.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: 追加修正後は未検証。
- 未解決事項: Issue #23のcreate/no-op E2E最終確認。
- 次アクション: テスト、作業記録HTML検証、PR作成・マージ、create経路、no-op経路、Pages公開URL、Slack通知結果の確認。

## GitHub Issue状況
確認日時（JST）: 2026-08-25 12:20
取得範囲: `tj-999-comp/sandbox-pages` Issue #23、`tj-999-comp/B_Stats_Site` Issue #31、およびIssue #23の受入run。

### 親子関係
```text
親子関係なし
```

### 優先順位順の未完了一覧
| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | OPEN（REOPENED） | 本作業の対象。create E2Eとno-op非回帰の最終確認が必要。 |
| 2 | P0 | [#31 [E2E] 新規作業記録1件を手動publish要求する](https://github.com/tj-999-comp/B_Stats_Site/issues/31) | OPEN（REOPENED） | B側からの入力供給元。B側checkout停滞時はA側を直接dispatchして検証。 |

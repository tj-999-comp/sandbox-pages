# 作業記録 047: Issue #23 no-op入力の文字列伝播を固定
作成日: 2026-08-25

## 概要
- 課題: Issue #23の受入workflowで、apply成功後にreusable Pages workflowのdeployジョブが生成されず、親runがfailureになる。
- 目的: no-op判定値をcallerからcalled workflowへ型変換なしで伝播し、no-op時に成功する完了jobを実行できるようにする。
- 完了条件: no-opのB→A実E2Eが成功し、deploy・Pages更新・Slack通知が実行されないことを確認する。

## 適用した役割
### Portfolio Frontend Engineer相当
- 入力: PR #48 merge commit `42909d81c11d5c25c2cc2d61dbc7b0430ffe7f1e`、B側run #32800412633、A側run #32800676465、GitHub Actions公式仕様。
- 実施内容: `should_deploy`の真偽比較式をcallerの`with`へ渡す方式から、applyの`no_op`文字列出力を`no_op`入力へそのまま渡す方式へ変更した。called workflow内で`'true'`ならno-op job、それ以外ならbuild/deployを選択する。
- 成果物: `.github/workflows/accept-source.yml`、`.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`。
- 検証結果: 変更後のローカルテストとGitHub Actionsは実行中。
- 未解決事項: main反映後のno-op E2E再実行が未完了。
- 次工程への引き継ぎ: ローカル検証、HTML生成、事前レビュー、PR、mainマージ後にB→Aを再実行する。

### Portfolio Reviewer相当
- 入力: PR #48のマージ後に確認したA側run #32800676465。
- 実施内容: dry-run/applyは成功したが、deploy callerとcalled workflowのjobが生成されず、notifyがskippedとなった事実を確認した。公式仕様上、reusable workflow callerの`with`入力は宣言型と一致させる必要があるため、比較式のboolean結果をstring入力へ渡さず、文字列outputを直接渡す修正方針とした。
- 成果物: 追加修正方針と再検証条件。
- 検証結果: 追加修正前のA側runはfailure。重大な未解決事項として差し戻した。
- 未解決事項: 追加修正後のGitHub上の実動結果。
- 次工程への引き継ぎ: Frontend Engineer修正後に再レビューする。

## 主要な判断
- 判断: `should_deploy`の否定条件をcaller側で評価せず、`no_op` outputを同名のstring inputへ直接渡す。
- 理由: `workflow_call`の入力型とcallerのexpression結果の型変換に依存せず、called workflowが受け取った文字列だけで分岐できるため。

## 最終結果
- 解決したこと: reusable workflowへ渡すno-op判定の型境界を単純化した。PR作成・mainマージ後の追加修正と検証は継続中。
- 変更ファイル: `.github/workflows/accept-source.yml`、`.github/workflows/deploy-pages.yml`、`tests/test_pages_workflow.py`、`docs/ACTIONS_MAIN_POLICY.md`、本作業記録。
- 検証結果: 追加修正後の検証は未完了。
- 未解決事項: Issue #23のno-op E2E成功確認。
- 次アクション: テスト、HTML検証、PR作成・マージ、B→A再実行、A側job・artifact・Pages・Slack結果の確認。

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

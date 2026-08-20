# 作業記録 032: Issue #18 許可範囲限定の同期apply engine
作成日: 2026-08-20

## 概要

- 課題: Issue #5のPhase 4として、検証済み受入payloadを公開リポジトリへ反映するapply engineが未実装だった。
- 目的: A側で受入payload、source inventory、直前provenance、公開ファイル、生成indexを再照合し、対象projectだけを安全に反映できるようにする。
- 完了条件: 許可範囲外差分、manifest drift、payload改ざん、no-op、競合、削除・改名を拒否または安全に扱い、対象projectの公開ファイル・provenance・indexを一貫して更新する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: GitHub Issue #18、`scripts/publish/read_only_acceptance.py`、`scripts/publish/provenance.py`、`scripts/publish/index_generator.py`、`docs/ACTIONS_MAIN_POLICY.md`。
- 実施内容: `apply_engine.py`を追加し、read-only acceptance JSONの厳格なfield検証、registry照合、source固定SHA・branch来歴確認、source inventoryとtarget digestの再照合、metadata再検証、直前manifest drift検査、生成indexの事前検査を実装した。公開ツリーは一時ディレクトリで組み立て、metadataを公開せず、対象projectの通常ファイルだけを上書きし、manifestとglobal/project indexを同時に反映する。`publish:false`、`withdraw`、`a_rendered`、自動削除・改名は専用workflowへ分離して拒否した。
- 成果物: `scripts/publish/apply_engine.py`、`tests/test_apply_engine.py`。
- 検証結果: create、metadata改ざん、manifest drift、余計な公開ファイル、別project redirect、no-op、競合retryのテストを追加し、全61件のunit testに合格した。
- 未解決事項: GitHub Actions上での実apply、commit・固定SHA deploy、Bの実sourceを使った手動E2EはIssue #19以降の工程で実施する。
- 次工程への引き継ぎ: Issue #19でworkflowからengineを呼び出し、最新mainの再checkout・commit・Pages deployへ接続する。

### Portfolio Reviewer

- 入力: #18の完了条件、apply engineと専用テスト、既存のprovenance/index実装。
- 実施内容: 対象project以外への書き込み境界、直前manifestとの差分、同一run payloadのdigest、index生成、no-op、競合retry、危険な削除・改名の扱いをレビューした。サブエージェントを利用できないため、主担当がReviewer基準で差分を再確認した。
- 成果物: commit前レビュー結果。
- 検証結果: 重大0件。`git diff --check`、Python構文確認、全unit test合格を確認した。
- 未解決事項: GitHub Actionsの実workflowと外部PRレビューは未実施。
- 次工程への引き継ぎ: Issue #19のworkflow実装時に、clean worktree、expected main SHA、bounded retryをworkflow境界でも再確認する。

## 主要な判断

- 判断: 実ファイルへの書き込み前に一時destinationで公開ファイル、manifest、indexを組み立てる。
- 理由: driftやpayload不一致の途中で公開ツリーだけが更新される状態を避けるため。
- 判断: `provenance/<project_id>/`の直前manifestと公開ファイルを完全比較し、extra・missing・changedのいずれも自動修復しない。
- 理由: 手動変更や別工程の破損をapplyが上書きせず、監査可能な復旧へ戻すため。
- 判断: `apply_with_bounded_retry`の再試行上限を1回に固定する。
- 理由: main進行時に対象projectだけを最新SHAへ再適用できる一方、再競合を無制限に繰り返さないため。

## 最終結果

- 解決したこと: #18のA側apply engineと再現可能な安全性テストを実装した。検証済みpayloadの再照合、対象project限定反映、provenance manifest更新、global/project index再生成、no-op、drift拒否、競合上限をコード化した。
- 変更ファイル: `scripts/publish/apply_engine.py`、`tests/test_apply_engine.py`、本作業記録のMarkdown原本と対応HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（61件合格）、Python構文確認（合格）、`git diff --check`（合格）。表示コード変更はないためブラウザ確認は対象外。
- 作業ブランチ: `codex/032-issue-18-apply-engine`
- コミット: `34095b0`（apply engine・テスト・作業記録）。PR情報追記は後続commitで反映する。
- PR: [#36 Issue #18: 許可範囲限定の同期apply engineを実装](https://github.com/tj-999-comp/sandbox-pages/pull/36)（Draft、base `main`、head `codex/032-issue-18-apply-engine`）。
- PRレビュー・CI: GitHub上の差分は4ファイルで意図した#18対応のみ。`validate` run `32351101736`はpass。外部レビューは未実施。
- 未解決事項: #19で受入workflowへ接続し、GitHub Actionsの実apply・commit・固定SHA deployを確認する必要がある。
- 次アクション: Draft PR #36の外部レビューを確認し、#19のActions接続へ進む。

## GitHub Issue状況

確認日時（JST）: 2026-08-20 17:46
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue。Issue一覧APIは9件の番号・タイトル・状態を取得できた。個別Issue本文の再取得はGitHub API接続が断続的に失敗したため、#5と#18のみ本作業中に取得できた本文で関係を確認し、その他の親子関係は未確認と記録する。

### 親子関係

```text
sandbox-pages #5が親Epic。
sandbox-pages #18はIssue本文のParent: #5参照を取得済み。
#13、#19、#20、#21、#22、#23、#24の個別本文は今回の再取得に失敗したため、関係未確認。
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | Open | 親Epic。critical path全体を追跡 |
| 2 | P1 | [#18 [Publish] 許可範囲限定の同期apply engineを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/18) | Open | Phase 4。#10、#16、#17完了後。今回の対象 |
| 3 | P1 | [#19 [Actions] 受入workflowへcommit・固定SHA deployを接続する](https://github.com/tj-999-comp/sandbox-pages/issues/19) | Open | #18完了後の次工程。個別本文は未再取得 |
| 4 | P1 | [#20 [Notification] deploy成功後のSlack通知jobを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/20) | Open | #19後の通知工程。個別本文は未再取得 |
| 5 | P1 | [#21 [E2E] disabled sourceでBの受入dry-runを実行する](https://github.com/tj-999-comp/sandbox-pages/issues/21) | Open | #18とB側準備完了後。個別本文は未再取得 |
| 6 | P1 | [#22 [Activation] B sourceを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/22) | Open | #19、#21完了後。個別本文は未再取得 |
| 7 | P1 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open | #20とB側準備完了後。個別本文は未再取得 |
| 8 | P2 | [#13 [Renderer] a_rendered用の決定的rendererを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/13) | Open | Phase 6。critical path外。個別本文は未再取得 |
| 9 | P2 | [#24 [Operations] 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | Open | Phase 6。critical path外。個別本文は未再取得 |

# 作業記録 027: Issue #12 既存Bのno-op同期dry-run
作成日: 2026-08-20

## 概要

- 課題: GitHub Issue #12（既存Bのno-op同期dry-run）
- 目的: #11で登録した初期provenance manifestを基準に、生成元と公開先を変更せず完全照合する読み取り専用dry-runを追加する。
- 完了条件: source/publicのpath・size・SHA-256がmanifestと一致した場合に変更0件のno-opを返し、欠落・余剰・変更・symlinkを検出した場合は停止する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: #10のprovenance API、#11の`provenance/B_Stats_Site/initial.json`、`config/sources.json`、公開ツリー。
- 実施内容: source treeとpublished treeを再帰的にinventory化し、初期manifestの`source_files`・`published_files`と完全比較する`run_noop_dry_run` APIとCLIを追加した。bootstrap時点ではsource側metadataが未導入のため、source validatorは将来publishのゲートとして残し、今回のdry-runは#11で受入済みのdigest inventoryを比較する構成とした。差分がある場合は同期処理へ進まず例外で停止する。
- 成果物: `scripts/publish/sync_dry_run.py`、`tests/test_sync_dry_run.py`。
- 検証結果: 正常系25ファイルのno-op、公開先の余剰ファイル、sourceの変更をテストし、全44件合格した。
- 未解決事項: 外部BリポジトリからAを起動するGitHub Actions workflow、通常publish、Pages deploy、Slack通知は後続課題である。
- 次工程への引き継ぎ: workflowからmanifest、登録source、公開先を指定してdry-run API/CLIを呼び出し、no-op時にcommit・deploy・通知を実行しない契約へ接続する。

### Portfolio Reviewer

- 入力: dry-run実装、manifest、テスト、Issue #12の完了条件。
- 実施内容: source/public双方の完全一致、変更時の早期停止、読み取り専用性、bootstrapの`notify: false`を確認した。
- 成果物: no-op判定と差分停止のレビュー結果。
- 検証結果: 重大・中・軽微の未解決事項はない。
- 未解決事項: GitHub Actions workflowへの接続、外部B checkoutを使ったE2E、通常publish・Pages deploy・Slack通知は後続課題である。
- 次工程への引き継ぎ: workflow実装時に、dry-run成功後の副作用が発生しないことをActions fixtureまたは実環境で再確認する。

## 主要な判断

- 判断: dry-runはmanifestに対するsource/publicの完全一致だけを判定し、ファイルコピーやmanifest更新を行わない。
- 理由: 初回同期では既存公開物を上書きせず、digest driftがある場合に自動publishを停止する必要があるため。
- 判断: symlinkと非通常ファイルを拒否する。
- 理由: manifestの対象範囲を通常ファイルに限定し、公開先の意図しない参照や差し替えを防ぐため。

## 最終結果

- 解決したこと: #11の25ファイルbaselineに対してsource/publicのno-opを判定し、missing・extra・changed・symlinkを検出して停止できるようにした。
- 変更ファイル: `scripts/publish/sync_dry_run.py`、`tests/test_sync_dry_run.py`、本作業記録のMarkdownと生成HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（44件合格）、`PYTHONPYCACHEPREFIX=/tmp/codex-sandbox-pages-pycache python3 -m py_compile scripts/publish/sync_dry_run.py`、CLIのfixture相当API検証に合格した。
- 未解決事項: GitHub Actions workflowへの接続、外部B checkoutを使ったE2E、通常publish・Pages deploy・Slack通知は未実施。
- 次アクション: #12のdry-runをA側workflowへ接続し、実際のB基準commitをcheckoutしたno-op E2Eを確認する。

## GitHub Issue状況

確認日時（JST）: 2026-08-20 15:01
取得範囲: `tj-999-comp/sandbox-pages` のIssue #5・#11・#12

### 親子関係

```text
Issue #5
├── Issue #11（完了）
└── Issue #12（本作業）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P1 | [#12 既存Bのno-op同期dry-runを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/12) | Open | 本作業の対象。#10/#11の後続。workflow接続・E2Eは後続 |
| 2 | P0 | [#5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | Open | 親Epic。dry-run後のworkflow・公開導線を含む |
| 3 | P1 | [#11 B既存001〜010の初期provenance manifestを登録する](https://github.com/tj-999-comp/sandbox-pages/issues/11) | Closed（completed） | 本作業の前提。初期manifest登録済み |

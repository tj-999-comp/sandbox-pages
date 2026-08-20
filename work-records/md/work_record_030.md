# 作業記録 030: Issue #17 read-only受入workflowのdry-run
作成日: 2026-08-20

## 概要

- 課題: GitHub Issue #17「[Actions] read-only受入workflowをdry-runで実装する」、およびIssue #25の完了処理。
- 目的: 公開リポジトリAのsource registryだけを信頼し、生成元の固定commitをread-onlyで取得して、A所有の受入validatorを実行する手動dry-run入口を追加する。#25は解決済みとしてクローズする。
- 完了条件: 入力を`project_id`・固定source commit SHA・対象basenameへ限定し、登録sourceのrepository/ref/directory/public path、branch上のSHA来歴、許可ファイルのinventory・digest、正規化metadataを検証結果へ渡せること。`enabled: false`以外へapply処理を進めず、生成元コードを実行しないこと。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: Issue #17、`config/sources.json`、`scripts/publish`のA-02〜A-04 validator、既存Actionsの権限方針。
- 実施内容: `.github/workflows/accept-source.yml`を追加し、手動入力を3項目へ限定した。A側checkout後、registryから解決した生成元repository/refをSHA固定・sparse checkoutし、指定SHAが登録branchの祖先かつ直前provenance SHAと同一または子孫であることを確認する。source-side scriptやActionを実行せず、A所有のPython validatorだけを実行する構成にした。`enabled: false`をdry-run専用条件として拒否的に検証し、全accepted inventoryと対象basenameのsupport file、Markdown、metadata、HTMLのSHA-256、正規化metadataを`acceptance.json`へ保存し、artifactへ渡すようにした。
- 成果物: `.github/workflows/accept-source.yml`、`scripts/publish/read_only_acceptance.py`、`tests/test_read_only_acceptance.py`、`tests/test_pages_workflow.py`の受入workflow検査。
- 検証結果: 生成元ファイルを実行しない固定SHA来歴検証、A-02 metadata、A-03 acceptance file、source_html時のA-04 content safety、dry-run出力をfixtureで確認した。
- 未解決事項: GitHub Actions上での実際のworkflow dispatchと、生成元Bの実SHAを使ったE2E実行はpush・PR作成後に確認する。
- 次工程への引き継ぎ: Reviewerへworkflow権限、入力境界、外部コード非実行、固定SHA検証、artifact内容の確認を引き継ぐ。

### Portfolio Reviewer

- 入力: Issue #17の完了条件、追加workflow・Python実装・テスト差分、単体テスト結果。
- 実施内容: `permissions: {}`とjob単位の`contents: read`、`contents: write`不在、`secrets.`不在、main branch guard、SHA固定checkout、workflow_dispatch限定、A所有validator呼び出し、`enabled: false`のapply禁止、固定SHAと直前provenanceのancestor検証、出力artifactを確認した。
- 成果物: 作業記録作成前レビュー。
- 検証結果: 重大な未解決事項は確認されなかった。GitHub上の実workflow実行は未確認として残した。
- 未解決事項: push・PR作成前のため、GitHub Actionsの実行結果と外部B repositoryからの取得可否は未確認。
- 次工程への引き継ぎ: 対象ファイルを限定してcommitし、明示承認後にpush・Draft PRへ進む。

## 主要な判断

- 判断: 生成元取得はA所有workflowのSHA固定checkoutで行い、生成元repositoryのworkflow・script・任意commandを実行しない。
- 理由: read-only受入jobへ外部コード実行権限やSecretを持ち込まず、A所有validatorの判定だけを受入結果にするため。
- 判断: `enabled: false`をread-only acceptanceの前提条件にし、成功結果でも`dry_run: true`・`apply: false`を出力する。
- 理由: #17の段階導入では、受入検証と公開反映を分離し、#18以降のapply engineへ意図せず進めないため。
- 判断: 受入inventoryは全体validatorで許可範囲を確認し、全体inventoryと入力basenameのtarget inventoryをartifactへ出力する。
- 理由: source registryとA-03のallowlistを先に適用しつつ、全体digestと対象basenameの結果境界を同時に監査できるため。

## 最終結果

- 解決したこと: #17のread-only受入workflowとA所有のdry-run orchestrationを実装し、固定SHA、branch ancestor、直前provenanceからの同一・子孫検証、registry解決、A-02〜A-04 validator、全inventory/対象digest/metadata artifact、disabled source guardを追加した。GitHub Issue #25を`completed`理由でクローズした。
- 変更ファイル: `.github/workflows/accept-source.yml`、`scripts/publish/read_only_acceptance.py`、`tests/test_read_only_acceptance.py`、`tests/test_pages_workflow.py`、本作業記録と対応HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（54件合格）、`PYTHONPYCACHEPREFIX=/tmp/sandbox-pages-pycache python3 -m py_compile scripts/publish/read_only_acceptance.py`（合格）、workflow YAML parse（合格）、`git diff --check`（合格）。通常のpy_compileは環境側Pythonキャッシュ先の権限で失敗したため、一時キャッシュ先で再実行した。
- 作業ブランチ: `codex/030-issue-17-read-only-acceptance`
- コミット: 実装・記録commit準備中
- PR: 未作成
- PRレビュー・CI: ローカル事前レビュー済み。GitHub上のPRレビュー・CIは未実施。
- 未解決事項: GitHub Actions実環境での手動dispatch、実生成元Bからの固定SHA取得、artifact確認は未実施。PRレビュー・CIも未実施。
- 次アクション: 対象ファイルをcommit・pushし、Draft PRのレビュー・CIへ進む。

## GitHub Issue状況

確認日時（JST）: 2026-08-20 15:55
取得範囲: `tj-999-comp/sandbox-pages` Issue #5〜#10、#17、#25、および`tj-999-comp/B_Stats_Site` Issue #29、#32。各Issueの本文・状態をGitHub APIで取得した時点のスナップショット。

### 親子関係

```text
GitHub sub-issueとしての親子関係は確認できず、sandbox-pages #5〜#10・#17・#25の本文に Parent: #5 の参照あり。
B_Stats_Site #29・#32は本文のParentがsandbox-pages #5。
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | Open | 親Epic。#17の実workflow確認後、#18以降のapply・deploy工程へ進む |
| 2 | P1 | [#32 main更新時の公開要求triggerを有効化する](https://github.com/tj-999-comp/B_Stats_Site/issues/32) | Open | B側の自動trigger。手動E2E・公開workflowの安定確認後 |

### 完了済みの関連Issue

| GitHub Issue | 状態 | 本作業との関係 |
| --- | --- | --- |
| [#6 公開元source登録を設定ファイル化する](https://github.com/tj-999-comp/sandbox-pages/issues/6) | Closed / completed | #17が利用するA所有registry |
| [#7 共通命名・metadata schema validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/7) | Closed / completed | #17のA-02 validator |
| [#8 受入ファイルのpath・種別・容量validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/8) | Closed / completed | #17のA-03 validator |
| [#9 source_html向けHTML・CSS・URL安全validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/9) | Closed / completed | #17のA-04 validator |
| [#10 provenance manifest schemaとdrift検査を実装する](https://github.com/tj-999-comp/sandbox-pages/issues/10) | Closed / completed | #17の固定SHA・digest引き継ぎの前提 |
| [#29 001〜010のmetadataと生成元validator・CIを追加する](https://github.com/tj-999-comp/B_Stats_Site/issues/29) | Closed / completed | #17が取得するB側入力の前提 |
| [#25 dispatch認証をFine-grained PATからGitHub Appへ移行する](https://github.com/tj-999-comp/sandbox-pages/issues/25) | Closed / completed | ユーザー指定により本作業中に完了扱いでクローズ |
| [#17 read-only受入workflowをdry-runで実装する](https://github.com/tj-999-comp/sandbox-pages/issues/17) | Closed / completed | 本作業で実装し、ユーザー指定により完了扱いでクローズ |

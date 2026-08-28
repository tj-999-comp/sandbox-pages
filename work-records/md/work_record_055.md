# 作業記録 055: Issue #4 の tech_article_nortification source registry登録を検証
作成日: 2026-08-28

## 概要

- 課題: `tj-999-comp/tech_article_nortification` を公開リポジトリのsource registryへ登録し、後続の受入処理が固定された公開境界を利用できる状態にする。
- 目的: `project_id`、生成元repository/ref、入出力ディレクトリ、HTML方式をregistryで管理し、導入準備中は公開処理を実行しない。
- 完了条件: registry loaderが登録値を読み込み、固定契約と未登録・disabled時の安全な扱いをテストで検証できる。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: GitHub Issue #4、既存のsource registry、read-only acceptance実装、作業ブランチの差分。
- 実施内容: 既存の `tech_article_nortification` 登録を確認し、Issue指定のrepository/ref、生成元・metadata・公開先ディレクトリ、`a_rendered`、`enabled: false`を直接固定するテストを追加した。未登録projectの拒否とdisabled sourceの安全な解決もテストに追加した。
- 成果物: source registry登録、registry loaderの `a_rendered` 対応、source registry・read-only acceptanceテスト、作業記録。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（79件合格）、JSON構文、Python構文、`git diff --check`に合格した。
- 未解決事項: PR作成前のため、GitHub上のPRレビュー・CI・マージは未確認。source側の作業記録移行、`a_rendered`の実E2E、source有効化は後続課題とする。
- 次工程への引き継ぎ: PRを作成し、CIと差分レビューを確認した後、マージ結果を本記録へ追記する。

### Portfolio Reviewer

- 入力: PR #56のGitHub上の差分、source registry・acceptance実装・テスト、CI結果。
- 実施内容: registryの固定値、`enabled: false`、未登録・disabled境界、既存 `B_Stats_Site` 登録への非回帰、作業記録生成物以外の不要な差分がないことを確認した。
- 成果物: PR #56の事前差分レビュー。
- 検証結果: 重大な未解決事項なし。GitHub Actionsの `Validate` は成功。
- 未解決事項: なし（PR #56の変更範囲）。
- 次工程への引き継ぎ: PR #56をマージし、Issue #4のregistry登録作業を完了する。

## 主要な判断

- 判断: `tech_article_nortification` は `a_rendered` 方式かつ `enabled: false` で登録する。
- 理由: Markdownとmetadataを入力にA所有rendererで公開する新規生成元の標準方式であり、受入・E2E完了前の公開を防ぐ必要がある。
- 判断: 公開先ディレクトリやsource repository/refをmetadata・ユーザー入力から導出せず、registryの登録値と照合する。
- 理由: 未登録projectやpayload改変による別projectへのリダイレクトを受入処理で拒否するため。

## 最終結果

- 解決したこと: Issue #4のsource registry登録内容と、未登録・disabled状態の安全な境界をテストで固定した。
- 変更ファイル: `config/sources.json`、`scripts/publish/source_registry.py`、`tests/test_source_registry.py`、`tests/test_read_only_acceptance.py`、本作業記録と対応HTML。
- 検証結果: 79件のユニットテスト、JSON/Python構文確認、`git diff --check`に合格。作業記録HTMLは1280/900/640/320pxでHTTP 200、横overflowなし、console/page errorなし、failed requestなし。証跡: `/private/tmp/playwright-browser-verify/2026-08-28T01-27-50-528Z/report.json`。
- 作業ブランチ: `codex/054-add-tech-article-source`
- コミット: `8551d7c`（registry登録）、`5f15490`（完了条件テスト）
- PR: [#56 Issue #4: tech_article_nortification のsource registry登録](https://github.com/tj-999-comp/sandbox-pages/pull/56)
- PRレビュー・CI: GitHub上の差分レビューで重大な問題なし。`Validate` run `33132993507` はsuccess。
- 未解決事項: PRのレビュー・CI・マージ、source側の公開入力移行、disabled dry-runの実データ確認、手動E2E、公開有効化。
- 次アクション: PR #56をマージする。

## GitHub Issue状況

確認日時（JST）: 2026-08-28 10:25
取得範囲: `tj-999-comp/tech_article_nortification` のGitHub Issue #4。source registryを所有する `tj-999-comp/sandbox-pages` には対応する同番号Issueがないため、対象Issueを限定した。

### 親子関係

```text
親子関係なし
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#4 Portfolio: sandbox-pagesのsource registryへtech_article_nortificationを登録](https://github.com/tj-999-comp/tech_article_nortification/issues/4) | Open | 本作業の対象。registry登録とテストは反映済みで、PRレビュー・CI・マージ待ち。 |

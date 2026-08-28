# 作業記録 054: tech_article_nortification の生成元導入契約を追加
作成日: 2026-08-27

## 概要

- 課題: 新しい生成元リポジトリ `tech_article_nortification` を公開リポジトリのsource registryへ追加し、生成元へ渡す公開契約を明確にする。
- 目的: 既存の `B_Stats_Site` と同じ公開境界を保ちながら、新規生成元を `a_rendered` 方式で安全に導入できる状態にする。
- 完了条件: registryが新しい `project_id` を検証でき、生成元の入力パス・公開先・公開要求入力・導入前の無効状態が文書化され、既存テストに合格する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: `projects/README.md`、`docs/PORTFOLIO_STANDARD.md`、現行source registry、ローカルの `tech_article_nortification` checkout。
- 実施内容: `tech_article_nortification` を `main` branchの `work-records/` 入力、`projects/tech_article_nortification/` 公開先、`a_rendered`方式として登録した。新規方式でsupport fileを持たないregistryを検証できるよう、A所有rendererのgenerator IDを許可した。生成元checkoutの `README.md` と `AGENTS.md` に同じ固定情報と入力契約を追記した。
- 成果物: `config/sources.json`、`scripts/publish/source_registry.py`、`projects/README.md`、source registryテスト、生成元側の公開連携案内。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（76件合格）、source registryの構文確認、`git diff --check`、作業記録54件の生成・filename検証に合格した。
- 未解決事項: 生成元は現在 `Issues/Issue_###.md` 構成であり、公開契約の `work-records/md/` と `work-records/metadata/` への移行は未実施。A側の `a_rendered` rendererも未実装。
- 次工程への引き継ぎ: 生成元側で公開対象の作業記録を共通命名へ移行し、A側のrenderer実装後にdisabled dry-runと手動E2Eを行う。

### Portfolio Reviewer

- 入力: registry差分、公開契約の追記、source registryテスト結果。
- 実施内容: 新規sourceを有効化せず、公開先をregistryの固定値に限定し、既存のIssue資料を自動受入対象に含めない境界を確認した。
- 成果物: 導入準備中であることと、生成元へ渡す固定情報を `projects/README.md` に記録したレビュー結果。
- 検証結果: 既存Bの登録値を維持し、新規sourceの未移行状態を公開済みと扱わないことを確認した。
- 未解決事項: なし（今回の登録・契約文書の範囲）。
- 次工程への引き継ぎ: 生成元移行とrenderer実装が完了するまで `enabled: false` を維持する。

## 主要な判断

- 判断: `tech_article_nortification` は `project_id` としてリポジトリ名をそのまま使用し、`a_rendered`方式・`enabled: false`で登録する。
- 理由: 新規生成元はA側rendererを使う標準方式とし、現行checkoutに公開契約の入力構成がまだないため、準備完了前の実公開を防ぐ必要がある。
- 判断: 現在の `Issues/Issue_###.md` を公開対象へ自動変換しない。
- 理由: 課題資料と番号付き作業記録は役割が異なり、内容確認とmetadata付与なしに公開履歴へ混入させないため。

## 最終結果

- 解決したこと: `tech_article_nortification` のsource registry登録と、生成元へ渡す公開契約を追加した。
- 変更ファイル: `config/sources.json`、`scripts/publish/source_registry.py`、`projects/README.md`、`tests/test_source_registry.py`、`work-records/work_record.css`、`tech_article_nortification`側の`README.md`・`AGENTS.md`、本作業記録と対応HTML。
- 検証結果: 全76ユニットテスト、`convert_work_records_to_html.py --check`、`validate_work_record_filenames.py`、一時キャッシュ先を指定した`py_compile`、`git diff --check`に合格。ブラウザでは全4 viewportでHTTP 200、横overflowなし、console/page errorなし、failed requestなし。証跡: `/private/tmp/playwright-browser-verify/2026-08-27T09-12-44-156Z/report.json`。
- 未解決事項: 生成元の `work-records/` 移行、A側 `a_rendered` renderer、disabled dry-run、手動E2E、公開有効化。
- 次アクション: 生成元側へ本記録の契約情報を反映し、最初の `work_record_001` とmetadataを用意してから受入検証へ進む。

## GitHub Issue状況

本作業は新規生成元の導入契約を整備する作業であり、対応するGitHub Issueは未登録である。既存Issueの状態変更は行っていない。

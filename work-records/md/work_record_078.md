# 作業記録 078: query_learning_BBの公開側registry導入
作成日: 2026-09-01

## 概要

- 課題: 新しい生成元リポジトリ `tj-999-comp/query_learning_BB` の作業記録を受け入れる公開側registryが未登録だった。
- 目的: `sandbox-pages` のsource registryとregistryテストを更新し、公開側で固定SHAを受け入れる準備を整える。
- 対象範囲: この `sandbox-pages` リポジトリ内の変更のみ。生成元リポジトリの設定、Secret、外部Issue操作はこの記録の対象外とする。

## 実施内容

- `config/sources.json` に `query_learning_BB` のsourceを追加した。
- 生成元refを `refs/heads/main`、入力を `work-records/`、方式を `a_rendered`、generatorを `a-rendered-work-record-v1` とした。
- 公開先を `projects/query_learning_BB/`、public base pathを `/sandbox-pages/projects/query_learning_BB/` とした。
- 新規sourceは受入確認が完了するまで `enabled: false` とした。
- 生成元入力に含まれる `work-records/README.md` を公開対象外として `ignored_files` に登録した。
- `tests/test_source_registry.py` に新しいsourceの固定契約と無効状態の検証を追加した。

## 主要な判断

- 新規sourceは既存の `a_rendered` 契約に合わせ、Markdownとmetadataだけを受け入れる。
- 公開側registryに登録されたpathとgeneratorだけを使用し、生成元入力から任意の公開先やコマンドを組み立てない。
- disabled状態を維持し、registry変更のmerge後に実際の受入確認を行ってから有効化する。

## 検証結果

- 公開側unit test: 109件成功。
- project indexの生成物チェック: 成功。
- 既存77件の作業記録HTMLチェック: 成功。
- 作業記録filename・Markdown・HTML検証: 成功。
- `config/sources.json` のJSON構文、registry loader、`git diff --check`: 成功。

## PR・マージ記録

- PR: [#113 query_learning_BBの公開側source registry登録](https://github.com/tj-999-comp/sandbox-pages/pull/113)
- PR head: `6b7bf5846c469479632281948aeef3fef2a4569e`
- CI: [Validate run](https://github.com/tj-999-comp/sandbox-pages/actions/runs/33476987563) 成功。
- この作業記録はPR #113に含め、PRのmerge後に公開側mainへ反映する。

## 未完了

- PR #113のmerge後に、公開側workflowで実際の受入確認を行う。
- 受入結果を確認してから、registryの `enabled: true` 化を判断する。

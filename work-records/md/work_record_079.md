# 作業記録 079: query_learning_BBの受入baselineを登録
作成日: 2026-09-01

## 概要

- 課題: 新規sourceの受入workflowが参照する初期provenanceが未登録だった。
- 目的: `query_learning_BB` の公開履歴がまだ空であることを明示するbootstrap manifestを公開側へ登録し、disabled dry-runを実行できる状態にする。
- 対象範囲: この `sandbox-pages` リポジトリ内のprovenanceと作業記録の変更のみ。生成元リポジトリの変更やSecret設定は対象外とする。

## 実施内容

- `provenance/query_learning_BB/initial.json` を追加した。
- 初期manifestは `operation: create`、`notify: false`、公開ファイル0件、record 0件とした。
- 初期baselineが参照する生成元を `tj-999-comp/query_learning_BB` の `refs/heads/main`、固定SHA `a0662fc768181a736188c8fd35c7aefd2727ded0` とした。
- 初期manifestは公開済みrecordを表すものではなく、受入前の空の履歴を表す。
- この変更自体を公開側作業記録として追加した。
- source registryに紐づく空のproject indexを生成し、全体indexへprojectを追加した。

## 主要な判断

- 新規sourceの初期provenanceは、公開ファイルとrecordを空にして、通知を抑制する。
- registryは `enabled: false` のまま維持し、初期manifest登録後にdisabled dry-runでsourceを検証する。
- 作業記録には公開側リポジトリ内の変更だけを記載し、生成元の認証設定や外部操作は記載しない。

## 検証結果

- `provenance/query_learning_BB/initial.json` のschema、project_id、public base path、source repository、固定SHAを確認した。
- 公開側unit test 109件、project index、作業記録HTML 79件、filename検証が成功した。
- disabled dry-runの実GitHub実行結果は、manifest反映後に追記する。

## 未完了

- disabled dry-runを実行し、apply・deploy・notifyが行われないことを確認した。
- 実行結果: [accept-source.yml run](https://github.com/tj-999-comp/sandbox-pages/actions/runs/33478093777) はdry-runとapplyが成功し、`enabled: false` によりno-opとなった。deployとnotifyは未実行で、公開側mainも変更されていない。
- PR #114はmerge済み（merge commit: `747b77d8089c00408dfeec9c7c3c6cb7e9ca9d65`）。
- 次のregistry有効化と手動E2Eは、別の作業記録とPRで管理する。

# 作業記録 080: query_learning_BBを手動E2E向けに有効化
作成日: 2026-09-01

## 概要

- 課題: `query_learning_BB` のdisabled dry-runが成功し、公開側の本番手動受入へ進める条件が整った。
- 目的: source registryを手動E2E可能な状態へ変更し、生成元からの公開要求を固定SHAで検証する。
- 対象範囲: この `sandbox-pages` リポジトリ内のregistryと作業記録の変更のみ。生成元のSecretや外部リポジトリの変更は対象外とする。

## 実施内容

- `config/sources.json` の `query_learning_BB` を `enabled: true` に変更する。
- 公開経路を恒久自動triggerではなく、承認済み固定SHAによる手動dispatchに限定する。
- このregistry変更と手動E2Eの実行条件を、公開側作業記録として保存する。

## 主要な判断

- enabled化は、registry登録、初期provenance、A-03/A-04受入、disabled no-op確認が完了した後に行う。
- 受け入れるsourceはregistryで許可した `work-records/` 配下のMarkdownとmetadataだけとし、公開側rendererを使用する。
- この記録には公開側リポジトリの変更だけを残し、認証情報や生成元側の運用情報は記載しない。

## 検証結果

- PR CIでunit test、project index、作業記録HTML、filename検証を実行する。
- merge後、生成元の `Request publish` workflowから `work_record_001` を手動dispatchする。
- 受入、apply、Pages deploy、provenance、公開URLを確認し、結果をこの記録または後続記録へ反映する。

## 未完了

- registry有効化PRのmerge。
- 生成元の固定SHA `a0662fc768181a736188c8fd35c7aefd2727ded0` に対する手動publish要求とPages公開確認。

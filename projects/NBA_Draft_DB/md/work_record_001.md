# 作業記録 001: NBA_Draft_DBを公開作業記録の生成元として整備

作成日: 2026-08-30

## 概要

`NBA_Draft_DB` を `sandbox-pages` の `a_rendered` 方式に対応する生成元リポジトリとして整備した。公開先は `projects/NBA_Draft_DB/`、公開要求は検証済みの固定commitと対象basenameを用いる。

## 適用した役割

### 実際に担当したRole

- データ品質・検証担当
- Web公開・運用担当

## 主要な判断

- Markdownとmetadataを `work-records/md/` と `work-records/metadata/` に分離した。
- metadataは固定schemaだけを受け入れる、標準ライブラリのみのvalidatorを追加した。
- `a_rendered` 方式のため、公開用HTML、CSS、designファイルは生成元に追加しない。
- 既存の `docs/Issue/` は作業記録へ自動変換せず、プロジェクト資料として対象外のまま維持する。
- 人間の明示承認がないため、公開要求可能な作業記録はまだない。

## 最終結果

validator、validatorテスト、通常の検証workflow、公開要求workflowを追加した。公開要求workflowは対象の固定SHAをcheckoutし、対象Markdown・metadata、project_id、`publish: true` を検証した場合だけ `sandbox-pages` の `accept-source.yml` へ3入力をdispatchする。

## GitHub Issue状況

本作業に対応するローカル記録は `docs/Issue/Issue011.md`。GitHub Issueは #11、対応PRは #17と追補PR #18で、2026-08-31に `main` へマージされた。

公開側の正本契約に合わせ、公開要求の認証は旧PAT方式ではなく、GitHub Appの短期Installation token方式を使用する。

2026-08-31に生成元Secret `PUBLISH_APP_ID` と `PUBLISH_APP_PRIVATE_KEY` の登録を、Secretの値を表示せず名前だけ確認した。人間承認前のため、`publish: true`化と公開要求は行っていない。

`publish: false` のため、この記録自体は公開対象外である。

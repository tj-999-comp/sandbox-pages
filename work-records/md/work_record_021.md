# 作業記録 021: 共通命名・metadata schema validatorの実装
作成日: 2026-08-20

## 概要

- 課題: Issue #7「共通命名・metadata schema validatorを実装する」
- 目的: 両HTML modeで共通利用する作業記録の命名、metadata検証、正規化、公開対象判定を実装する。
- 完了条件: Issue #7の命名・schema・登録project・決定的正規化・`publish`判定をテストで固定する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: Issue #7、`projects/README.md`、Issue #6で追加された`config/sources.json`とsource registry。
- 実施内容: YAML metadata loader、schema validator、basename一致検証、決定的正規化、公開対象判定を標準ライブラリだけで実装した。登録済みsourceの`project_id`を参照するloaderと、異常系・除外系fixtureを追加した。
- 成果物: `scripts/publish/metadata_schema.py`、`tests/test_metadata_schema.py`、metadata fixture。
- 検証結果: 命名範囲、case一致、schema version、title、実在日付、project_id、tags、publish、必須field、未知field、未登録project、`publish: false`、metadataなしの判定をテストした。
- 未解決事項: なし。
- 次工程への引き継ぎ: Reviewerへ全テスト結果と差分確認を引き継ぐ。

### Portfolio Reviewer

- 入力: Issue #7の完了条件、実装差分、18件のユニットテスト結果。
- 実施内容: #6のsource registryとの接続、両HTML modeで再利用可能なAPI、公開対象外の安全条件、無関係な公開ファイルやPages設定への変更がないことを確認した。
- 成果物: Issue #7の差し戻し判定。
- 検証結果: 重大0件、中0件、軽微0件。差し戻し不要と判定した。
- 未解決事項: ブラウザ確認はUI変更がないため対象外。
- 次工程への引き継ぎ: Issue #8のpath・種別・容量validatorへ進める。

## 主要な判断

- 判断: 外部YAMLライブラリを追加せず、metadata契約で必要なmapping・scalar・文字列listだけを安全に読む小さなparserを実装した。
- 理由: 既存の標準ライブラリ中心の構成を維持し、受入validatorの実行環境に新しい依存を持ち込まないため。
- 判断: `publish: false`とmetadataなしはエラーではなく、公開候補から除外する結果にした。
- 理由: 共通公開契約が定める「自動削除を行わない」安全条件と整合させるため。

## 最終結果

- 解決したこと: `work_record_001`〜`work_record_999`の命名、同一basenameとcase一致、metadata schema、登録project照合、決定的なtags・title・date正規化、公開候補判定を実装した。
- 変更ファイル: `scripts/publish/metadata_schema.py`、`tests/test_metadata_schema.py`、`tests/fixtures/metadata/invalid_unknown_field.yml`、`tests/fixtures/metadata/work_record_003.yml`、本記録のMarkdownとHTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（18件合格）、`py_compile`、`git diff --check`に合格した。
- 未解決事項: なし。
- 次アクション: Issue #8の受入path・種別・容量validatorを実装する。

## GitHub Issue状況

確認日時（JST）: 2026-08-20 01:27
取得範囲: `tj-999-comp/sandbox-pages`の親Issue #5とPhase 1のIssue #6〜#8

### 親子関係

```text
#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する
├── #6 [Publish] 公開元source登録を設定ファイル化する
├── #7 [Publish] 共通命名・metadata schema validatorを実装する
└── #8 [Publish] 受入ファイルのpath・種別・容量validatorを実装する
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#7 共通命名・metadata schema validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/7) | オープン | 本作業の対象。#6完了を受けて実装したvalidatorのレビュー・反映が着手条件 |
| 2 | P0 | [#8 受入ファイルのpath・種別・容量validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/8) | オープン | #6と#7の完了後に着手 |

### 関連Issueの状態

| GitHub Issue | 状態 | 関係 |
| --- | --- | --- |
| [#5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | オープン | 親Epic |
| [#6 公開元source登録を設定ファイル化する](https://github.com/tj-999-comp/sandbox-pages/issues/6) | クローズ（completed） | #7の依存Issue |

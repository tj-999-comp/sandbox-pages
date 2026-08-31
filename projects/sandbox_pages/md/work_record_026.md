# 作業記録 026: B既存001〜010の初期provenance manifest登録
作成日: 2026-08-20

## 概要

- 課題: GitHub Issue #11（A-06）
- 目的: `B_Stats_Site`の既存公開物を、自動同期開始前のprovenance baselineとして登録する。
- 完了条件: 指定されたB基準commitと公開側確認commitを根拠として、001〜010およびsupport fileのdigestを記録し、公開ファイルを変更せずno-op drift検査に合格させる。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: Issue #11の完了条件、Issue #10で確定したprovenance schema、`config/sources.json`、`projects/B_Stats_Site/`。
- 実施内容: Bの基準commit `0fe9932255ac72e526e84887ee3f209af9f57c61` と公開リポジトリ確認commit `dd4c73c7820171a544d3e9b153904f538961ff80` の対象ツリーを照合し、公開側の25ファイル（support file 3件、Markdown 12件、HTML 10件）をSHA-256でmanifest化した。001〜010のmetadataは基準MarkdownのH1と作成日からbootstrap用に正規化し、後続のmetadata導入とは分離した。
- 成果物: `provenance/B_Stats_Site/initial.json`。
- 検証結果: manifest schemaをロードでき、source/published file 25件、record 10件、`notify: false`、生成元commitの一致を確認した。
- 未解決事項: `B_Stats_Site`のsourceは受入条件が整うまで`enabled: false`のままであり、通常publish・Pages反映・Slack通知は未実施。
- 次工程への引き継ぎ: Issue #12でこのmanifestを基準にno-op同期dry-runへ接続する。

### Portfolio Reviewer

- 入力: manifest、現行公開ファイル、Issue #11完了条件。
- 実施内容: manifestの`published_files`と現行`projects/B_Stats_Site/`をpath・size・SHA-256で完全比較し、指定commit、通知対象外、source無効を確認した。
- 成果物: no-op drift検査結果。
- 検証結果: `missing=()`、`extra=()`、`changed=()`で、重大・中・軽微の未解決事項はない。
- 未解決事項: manifestに公開側確認commit専用のフィールドはないため、本記録へ根拠commitを記録した。
- 次工程への引き継ぎ: Issue #12で受入validator・drift検査・同期dry-runをworkflowへ接続する。

## 主要な判断

- 判断: bootstrap manifestの`source_files`と`published_files`は、指定された基準時点の同一25ファイル集合として記録する。
- 理由: `source_html`方式であり、今回のbootstrapでは生成元HTMLを変換せず、そのまま公開側へ対応付けたため。
- 判断: bootstrapを理由にmetadataファイルや公開ファイルを追加・修正しない。
- 理由: Issue #11の非対象であるmetadata・親リンク修正と初期監査を分離し、既存公開物のbaselineを保持するため。

## 最終結果

- 解決したこと: B基準commit `0fe9932255ac72e526e84887ee3f209af9f57c61` と公開側確認commit `dd4c73c7820171a544d3e9b153904f538961ff80` に対応する既存公開物の初期provenance manifestを登録した。通知は無効、source registryは`enabled: false`のまま維持した。
- 変更ファイル: `provenance/B_Stats_Site/initial.json`、本作業記録のMarkdownと生成HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（41件合格）、manifestロード、no-op drift検査、`git diff --check`に合格した。
- 未解決事項: Issue #12以降のno-op同期workflow、通常publish、Pages deploy、Slack通知は未実施。
- 次アクション: Issue #12で既存Bのno-op同期dry-runを実装する。

## GitHub Issue状況

確認日時（JST）: 2026-08-20 取得範囲: `tj-999-comp/sandbox-pages`の親Issue #5とIssue #10〜#11

### 親子関係

```text
#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する
└── #11 [Bootstrap] B既存001〜010の初期provenance manifestを登録する
    └── 依存: #10 [Publish] provenance manifest schemaとdrift検査を実装する
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | オープン | 親Epic。A/Bの公開導入を追跡 |
| 2 | P1 | [#11 B既存001〜010の初期provenance manifestを登録する](https://github.com/tj-999-comp/sandbox-pages/issues/11) | オープン | 本作業。#10完了後の初期監査 |
```

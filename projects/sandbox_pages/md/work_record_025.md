# 作業記録 025: Issue #10 provenance manifestとdrift検査
作成日: 2026-08-20

## 概要

- 課題: 生成元commit、受入ファイル、公開ファイル、metadata、公開操作、通知対象を監査可能なmanifestとして追跡する。
- 目的: A#8の受入結果とA#9の安全検証を通過した公開物を、後続の同期・更新・取り下げで再照合できるようにする。
- 完了条件: manifestを決定的に生成・検証でき、source digestとpublished digestを記録し、直前manifestとの差分がある場合に自動上書きを停止できること。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: 公開リポジトリ（A）のIssue #10、`projects/README.md`のprovenance契約、A#8の`AcceptedFile`、A#9の安全検証方針。
- 実施内容: `schema_version`、`publication_id`、project、生成元repository/ref/commit SHA、操作種別、UTC受入日時、公開base path、`source_files`、`published_files`、record metadata、metadata digest、通知対象を持つmanifest schemaを追加した。JSONの決定的serialize、未知field・未知schema・不正digest・metadata digest不一致の拒否、missing/extra/changedを返すdrift検査、差分時に例外で停止するAPIを実装した。
- 成果物: `scripts/publish/provenance.py`、`tests/test_provenance.py`、provenanceのsource/published分離とdrift停止条件を追記した`projects/README.md`。
- 検証結果: 正常manifest、決定的serialize、未知schema・未知field、metadata digest不一致、公開URL不一致、missing/extra/changed drift、clean drift、`a_rendered`のA生成HTML分離をテストした。
- 未解決事項: 初期manifestの実ファイル作成、受入workflowからの固定commit取得、公開先の実digest収集、Pages反映、Slack通知は後続Issueの対象である。
- 次工程への引き継ぎ: A#11で既存公開物の初期manifestを作成し、A#12以降でno-op同期とdry-run受入workflowからdrift検査へ接続する。

### Portfolio Reviewer

- 入力: Issue #10の完了条件、manifest schema、serializer、drift検査、fixtureテスト、公開契約。
- 実施内容: source入力とpublished成果物を別digest集合として扱うこと、`a_rendered`でA生成HTMLを追跡できること、drift時に自動上書きしないこと、metadata digestと公開URLを再検証することをレビューした。
- 成果物: A#8・A#9・A#10の責務境界と、後続workflowが利用するmanifest APIのレビュー結果。
- 検証結果: 重大・中・軽微の未解決事項はない。manifest schemaとdrift検査を後続workflowへ接続できる範囲で実装されている。
- 未解決事項: 実際の既存公開ファイルとの初期照合はA#11で行う。
- 次工程への引き継ぎ: A#11で初期provenanceを生成し、公開中ファイルと生成元commitのbyte単位一致を記録する。

## 主要な判断

- 判断: `source_files`と`published_files`を別フィールドにする。
- 理由: `source_html`では生成元HTMLが公開される一方、`a_rendered`ではAがMarkdownからHTMLを生成するため、入力と公開成果物のpath集合が一致しないからである。
- 判断: driftはpath・size・SHA-256の完全比較とし、missing・extra・changedを分類する。
- 理由: ファイルの追加、削除、内容変更を同じ「不一致」として停止しつつ、監査ログと修正判断に必要な差分を失わないためである。
- 判断: manifestは未知fieldと未知schemaを拒否し、JSONをsort key付きで決定的にserializeする。
- 理由: 将来のworkflowやprovenance比較で、入力順や未定義拡張による再現性・監査性の低下を防ぐためである。

## 最終結果

- 解決したこと: A#8の受入元digest、A#9の安全検証後に公開するファイルdigest、record metadataとdigest、公開URL、操作・受入日時・通知対象をmanifestへ正規化できるようにした。直前manifestと公開中ファイルが不一致なら、drift例外を発生させて自動上書きを止める。
- 変更ファイル: `scripts/publish/provenance.py`、`tests/test_provenance.py`、`projects/README.md`、本作業記録のMarkdownと生成HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（41件合格）。正常、drift、未知schemaのJSON fixtureを含む。HTML再生成check、filename validator、`py_compile`、`git diff --check`に合格した。`work_record_025.html`をChromiumで1280×900、900×900、640×900、320×800で確認し、横overflow、console error、page error、failed requestは全条件0件だった。
- 未解決事項: A#10単体では実manifestをまだ配置しない。既存公開物の初期manifestはA#11、no-op同期・受入workflow接続はA#12・A#17以降で実装する。source registryの`enabled: false`も維持する。
- 次アクション: A#11で既存公開物の初期provenance manifestを作成し、A#12でno-op同期dry-runへ接続する。

## GitHub Issue状況

確認日時（JST）: 2026-08-20
取得範囲: `tj-999-comp/sandbox-pages`の親Issue #5とIssue #6〜#11

### 親子関係

```text
#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する
├── #6 [Publish] 公開元source登録を設定ファイル化する
├── #7 [Publish] 共通命名・metadata schema validatorを実装する
└── #8 [Publish] 受入ファイルのpath・種別・容量validatorを実装する
```

### 対象Issue

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#10 provenance manifest schemaとdrift検査を実装する](https://github.com/tj-999-comp/sandbox-pages/issues/10) | 未完了 | 本作業の対象。#8/#9のdigestを来歴へ接続 |
| 2 | P1 | [#11 B既存001〜010の初期provenance manifestを登録する](https://github.com/tj-999-comp/sandbox-pages/issues/11) | 未完了 | #10完了後。既存公開物の初期照合 |
| 3 | P1 | [#12 既存Bのno-op同期dry-runを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/12) | 未完了 | #10/#11の後続 |
| 4 | P1 | [#5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | 未完了 | 親Epic |

### 依存Issue

| GitHub Issue | 状態 | 関係 |
| --- | --- | --- |
| [#6 公開元source登録を設定ファイル化する](https://github.com/tj-999-comp/sandbox-pages/issues/6) | 完了 | source repository/ref/path/容量上限を提供 |
| [#7 共通命名・metadata schema validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/7) | 完了 | record metadataの正規化を提供 |
| [#8 受入ファイルのpath・種別・容量validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/8) | 未完了 | source digestの入力を提供 |
| [#9 source_html向けHTML・CSS・URL安全validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/9) | 未完了 | published digest前の安全検証を提供 |

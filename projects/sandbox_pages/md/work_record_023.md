# 作業記録 023: Issue #8 受入ファイルのpath・種別・容量validator
作成日: 2026-08-20

## 概要

- 課題: 公開リポジトリ（A）が、登録済みsourceから受け取るファイルのpath・種別・容量を独立して検証できるようにする。
- 目的: 作業リポジトリ（B）の自己検証結果だけに依存せず、Aが許可範囲を再導出して安全な受入候補だけを後続の公開処理へ渡せるようにする。
- 完了条件: 登録済みsupport fileと番号付き作業記録だけを受け入れ、symlink・未登録path・不正な種別・容量超過を拒否し、決定的なファイル一覧とSHA-256 digestを返すこと。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: 公開リポジトリ（A）のIssue #8、`config/sources.json`、`scripts/publish/source_registry.py`、`scripts/publish/metadata_schema.py`、`projects/README.md`。
- 実施内容: `source_directory`と`metadata_directory`の登録値から受入対象を導出し、`source_html`ではMarkdown・metadata・同名HTML、登録済みsupport fileだけを検証するvalidatorを追加した。通常ファイル、symlink、許可ディレクトリ、ファイル数、単体サイズ、合計サイズを確認し、受入ファイルを相対POSIX path・サイズ・SHA-256 digestの決定的な一覧へ正規化するようにした。
- 成果物: `scripts/publish/acceptance_files.py`、`tests/test_acceptance_files.py`、責務分担を追記した`projects/README.md`。
- 検証結果: 正常系、欠落、未登録ファイル、未登録ディレクトリ、symlink、容量超過、`a_rendered`の各fixtureを追加し、ユニットテストが全件成功した。
- 未解決事項: workflowからのcommit取得、provenance manifest、HTML・CSS・URL安全validator、公開先への反映は後続Issueの対象である。
- 次工程への引き継ぎ: 後続のA受入workflowは、このvalidatorの結果をmetadata・安全性・provenance・許可範囲差分の検証へ接続する。

### Portfolio Reviewer

- 入力: Issue #8の完了条件、source registry、追加validator、fixtureテスト、公開契約。
- 実施内容: Bの自己検証とAの最終受入を同じ責務として扱っていないこと、Aがsource registryから受入集合を再計算すること、未登録ファイルと容量超過が拒否されることを確認した。
- 成果物: 本作業記録に記載する受入責務の提案とレビュー観点。
- 検証結果: 実装差分、Issue #8の範囲、後続Issueとの責務境界をレビューし、重大・中・軽微の未解決事項はないと判定した。後続のHTML安全validator・workflow接続前の基礎validatorとして範囲は妥当である。
- 未解決事項: 実際のGitHub Actions dispatchから固定commitを取得するE2Eは未実施である。
- 次工程への引き継ぎ: A#9以降でHTML/CSS/URL安全性、provenance、dry-run workflowを追加する。

## 主要な判断

- 判断: Bは公開要求前の自己検証、Aは受入時の独立した最終検証を担当する。
- 理由: B側のvalidatorが誤設定や侵害を含むcommitを誤って通しても、A側でsource registryに基づくpath・種別・容量・digestの検証を再実行できるようにするため。
- 判断: A#8ではHTMLの内容安全性や公開反映まで実装しない。
- 理由: HTML・CSS・URL安全性はA#9、provenanceはA#10、初期同期とworkflowはA#11以降の責務であり、Issue #8のpath・種別・容量検証と分離するため。
- 判断: 番号なし補助HTMLは、source registryのsupport fileに明示されていない限り拒否する。
- 理由: 補助文書を作業記録として誤ってindex・通知・更新対象へ混入させないため。

## 最終結果

- 解決したこと: A側で登録済みsupport file、番号付きMarkdown、metadata、`source_html`の同名HTMLだけを受入対象として導出し、未登録path、未登録ディレクトリ、symlink、欠落record、単体・合計容量超過を拒否できるようにした。受入ファイルは決定的な相対path一覧とSHA-256 digestへ正規化する。
- 変更ファイル: `scripts/publish/acceptance_files.py`、`tests/test_acceptance_files.py`、`projects/README.md`、本作業記録のMarkdownと生成HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（26件合格）。追加fixtureは正常系、欠落、未登録ファイル・ディレクトリ、symlink、単体・合計容量、`a_rendered`を対象とした。`convert_work_records_to_html.py --check`、作業記録filename validator、`py_compile`、`git diff --check`も合格した。追加HTMLはChromiumで1280×900、900×900、640×900、320×800を確認し、横overflow、console error、page error、failed requestは全条件0件だった。
- 未解決事項: A#8のvalidatorを実際の受入workflowへ接続する処理、A#9のHTML・CSS・URL安全validator、provenance、Pages反映、Slack通知は未実装である。source registryの`enabled: false`も維持する。
- 次アクション: A#9のHTML・CSS・URL安全validatorへ進み、その後にA#10〜#12のprovenance・初期同期・dry-run受入workflowを実装する。

## GitHub Issue状況

確認日時（JST）: 2026-08-20
取得範囲: `tj-999-comp/sandbox-pages`のIssue #5〜#10

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
| 1 | P0 | [#8 受入ファイルのpath・種別・容量validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/8) | 未完了 | 本作業の対象。validator実装後、workflow接続が必要 |
| 2 | P1 | [#9 source_html向けHTML・CSS・URL安全validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/9) | 未完了 | #8の後続。Aの内容安全性検証 |
| 3 | P1 | [#10 provenance manifest schemaとdrift検査を実装する](https://github.com/tj-999-comp/sandbox-pages/issues/10) | 未完了 | #8/#9の後続。公開来歴とdigestを管理 |
| 4 | P1 | [#5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | 未完了 | 親Epic |

### 依存Issue

| GitHub Issue | 状態 | 関係 |
| --- | --- | --- |
| [#6 公開元source登録を設定ファイル化する](https://github.com/tj-999-comp/sandbox-pages/issues/6) | 完了 | A#8が参照するsource registryを提供 |
| [#7 共通命名・metadata schema validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/7) | 完了 | A#8がrecord basenameとmetadata配置を前提にする |

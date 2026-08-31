# 作業記録 068: Issue #80 sandbox-pages source registry登録
作成日: 2026-08-31

## 概要

- 課題: GitHub Issue #80「sandbox-pagesをsource registryへ登録し初期公開契約を固定する」。
- 目的: 本リポジトリ自身の`work-records/`を既存の受入pipelineへ登録し、公開先・URL・HTML方式・容量上限・初期無効状態を設定とテストで固定する。
- 完了条件: `sandbox_pages`のsource registry entry、公開契約、初期公開対象67件の引き継ぎ情報を追加し、既存sourceの受入とテストを壊さない。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: GitHub Issue #80、`config/sources.json`、source registry validator、既存projectの公開契約。
- 実施内容: `sandbox_pages`を`source_html`方式のsourceとして登録した。生成元と公開先を分離し、`work-records/`、`work-records/metadata/`、`projects/sandbox_pages/`、公開base path、support file、generator、容量上限、`enabled: false`を固定した。初期公開候補は現在の`work_record_001`〜`work_record_067`全67件として、後続のmetadata整備・初期provenanceへ引き継ぐ契約を追加した。
- 成果物: `config/sources.json`、`projects/README.md`、`tests/test_source_registry.py`。
- 検証結果: registry、受入ファイル、Pages workflowの関連単体テスト27件に合格。JSON構文、作業記録HTMLのcurrent check、filename validator、`git diff --check`に合格した。Chromium表示確認も1280px・900px・640px・320pxで合格した。
- 未解決事項: metadata追加、初期provenance、disabled dry-run、手動E2E、有効化は後続Issue #81〜#86の対象。
- 次工程への引き継ぎ: #81で全67件のmetadataを整備し、人間確認済みの公開対象として受入可能な状態にする。

### Portfolio Reviewer

- 入力: baseとの差分、registry validator、既存sourceの設定、Issue #80の完了条件。
- 実施内容: `sandbox_pages`のproject ID、同一repositoryのsource境界、`source_html`と`b-stats-work-record-v1`の組み合わせ、support file、公開先、容量上限、初期無効状態を照合した。
- 成果物: 差分レビュー結果。
- 検証結果: 重大な範囲外変更なし。既存3sourceのregistry順序・設定と受入workflowの契約に非回帰であることを確認した。
- 未解決事項: GitHub Actions上の実source checkout、Pages、Slackの外部確認は未実施。
- 次工程への引き継ぎ: `enabled: false`を維持したまま#81のmetadata整備へ進む。

## 主要な判断

- 判断: `sandbox_pages`は既存B互換の`source_html`方式で登録し、初期状態を`enabled: false`とした。
- 理由: 本リポジトリのMarkdown・HTML・CSSを既存のsource validatorで受け入れつつ、metadata・provenance・disabled dry-run・既存project非回帰を先に確認し、公開開始を後段へ分離するため。
- 判断: 初期公開候補を現在存在する67件すべてとした。
- 理由: Issue作成時の63件から増えた`work_record_064`〜`067`も作業記録として存在し、ユーザー確認により全件公開扱いと決定したため。
- 判断: `max_files`を256とした。
- 理由: 67件についてMarkdown・metadata・HTMLの201ファイルにsupport file 3件を加えるため、既存の100ファイル上限では不足するため。

## 最終結果

- 解決したこと: `sandbox_pages`を公開pipelineへ登録し、後続Issueが参照する初期公開契約を固定した。
- 変更ファイル: `config/sources.json`、`projects/README.md`、`tests/test_source_registry.py`、本作業記録のMarkdown/HTML。
- 検証結果: registry関連テスト27件、JSON構文、converter check、filename validator、`git diff --check`に合格した。作業記録HTMLをChromiumの1280×900、900×900、640×900、320×800で確認し、全viewportでHTTP 200、横overflowなし、console/page errorなし、failed requestなし。
- 未解決事項: #81〜#87のmetadata整備、初期provenance、dry-run、手動E2E、有効化、運用引き継ぎ。
- 次アクション: #81で`work_record_001`〜`067`のmetadataを追加し、全件のtitle・date・project_id・publishを検証する。

## GitHub Issue状況

確認日時（JST）: 2026-08-31 18:57
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue（Pull Requestを除外）16件。GitHub App CLIはKeychain項目不足で利用できなかったため、公開GitHub Issue画面で現行一覧と各Issueを確認した。16件の状態はすべてOpen、state reasonはすべてnull。

### 親子関係

```text
#79 [Epic] sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する [Open]
├── #80 sandbox-pagesをsource registryへ登録し初期公開契約を固定する [Open]
├── #81 sandbox-pages既存作業記録63件のmetadataを整備する [Open]
├── #82 同一sourceの固定commit・basename限定受入を実装・検証する [Open]
├── #83 sandbox_pages既存作業記録を初期公開状態としてprovenanceへ登録する [Open]
├── #84 sandbox_pagesのdisabled受入dry-runとno-opを検証する [Open]
├── #85 sandbox_pagesを手動E2E可能な状態へ有効化する [Open]
├── #86 sandbox_pagesの新規作業記録をPages公開しSlack通知まで確認する [Open]
└── #87 sandbox_pagesの公開・停止・再通知手順を引き継ぐ [Open]

#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する [Open]
├── #90 各生成元の過去作業記録を棚卸しし公開対応表を確定する [Open]
├── #91 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する [Open]
├── #92 作業記録ページの構成とrecord間リンクを実装する [Open]
├── #93 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する [Open]
└── #94 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う [Open]

#102 [Operations] 作業記録のIssue状況を該当リポジトリ単位で全生成元へ統一する [Open]
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#79 sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する](https://github.com/tj-999-comp/sandbox-pages/issues/79) | Open（state_reason: null） | 親Epic。#80〜#87を依存関係順に完了する。 |
| 2 | 未設定 | [#80 sandbox-pagesをsource registryへ登録し初期公開契約を固定する](https://github.com/tj-999-comp/sandbox-pages/issues/80) | Open（state_reason: null） | 本作業。registryと初期公開契約を固定する。 |
| 3 | 未設定 | [#81 sandbox-pages既存作業記録63件のmetadataを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/81) | Open（state_reason: null） | #80完了後。現行67件へ適用する。 |
| 4 | 未設定 | [#82 同一sourceの固定commit・basename限定受入を実装・検証する](https://github.com/tj-999-comp/sandbox-pages/issues/82) | Open（state_reason: null） | #80・#81完了後。 |
| 5 | 未設定 | [#83 sandbox_pages既存作業記録を初期公開状態としてprovenanceへ登録する](https://github.com/tj-999-comp/sandbox-pages/issues/83) | Open（state_reason: null） | #80〜#82完了後。 |
| 6 | 未設定 | [#84 sandbox_pagesのdisabled受入dry-runとno-opを検証する](https://github.com/tj-999-comp/sandbox-pages/issues/84) | Open（state_reason: null） | #83完了後。 |
| 7 | 未設定 | [#85 sandbox_pagesを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/85) | Open（state_reason: null） | #84のレビューと明示承認後。 |
| 8 | 未設定 | [#86 sandbox_pagesの新規作業記録をPages公開しSlack通知まで確認する](https://github.com/tj-999-comp/sandbox-pages/issues/86) | Open（state_reason: null） | #85完了後。 |
| 9 | 未設定 | [#87 sandbox_pagesの公開・停止・再通知手順を引き継ぐ](https://github.com/tj-999-comp/sandbox-pages/issues/87) | Open（state_reason: null） | #86完了後。 |
| 10 | 未設定 | [#89 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open（state_reason: null） | 独立Epic。#90〜#94を追跡する。 |
| 11 | 未設定 | [#90 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open（state_reason: null） | #89配下。全生成元のrecordを棚卸しする。 |
| 12 | 未設定 | [#91 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open（state_reason: null） | #90完了後。 |
| 13 | 未設定 | [#92 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open（state_reason: null） | #90とmetadata仕様確定後。 |
| 14 | 未設定 | [#93 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | Open（state_reason: null） | #90〜#92完了後。 |
| 15 | 未設定 | [#94 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open（state_reason: null） | #90〜#93完了後。 |
| 16 | 未設定 | [#102 作業記録のIssue状況を該当リポジトリ単位で全生成元へ統一する](https://github.com/tj-999-comp/sandbox-pages/issues/102) | Open（state_reason: null） | 独立した横断運用課題。 |

未完了一覧: 16件（対象リポジトリ`sandbox-pages`のOpen Issueを全件記載）。

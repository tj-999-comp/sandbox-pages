# 作業記録 065: NBA_Draft_DBのsource登録と初期公開状態の準備
作成日: 2026-08-31

## 概要
- 課題: [sandbox-pages #70](https://github.com/tj-999-comp/sandbox-pages/issues/70)の実施順に従い、NBA_Draft_DBを公開受入の対象へ追加する。
- 目的: NBA_Draft_DBの固定commit・単一basenameによる`a_rendered`受入を可能にし、実公開前の安全な初期状態を作る。
- 完了条件: source registry登録、`enabled: false`の初期状態、初期provenance、project/global index、契約テストを整備し、既存projectへ意図しない公開差分を発生させない。

## 適用した役割
### Portfolio Frontend Engineer
- 入力: #70〜#76のIssue本文、`config/sources.json`、受入workflow、source registry・provenance・index generatorの既存実装。
- 実施内容: `NBA_Draft_DB`を`a_rendered`、`a-rendered-work-record-v1`、support fileなし、容量上限付き、`enabled: false`でsource registryへ追加した。生成元mainの取得済みcommitを参照する空のbootstrap provenanceを追加し、公開中レコード0件のproject indexとglobal indexを生成した。契約説明を`projects/README.md`へ追加し、registry解決とsource設定のテストを追加した。
- 成果物: source registry、初期provenance、生成index、公開契約文書、registry/受入解決テスト。
- 検証結果: 全94テスト、registry/provenance検証、index再生成チェック、作業記録ファイル名検証、ブラウザ確認に合格した。
- 未解決事項: 生成元側の承認済み`publish: true`固定commitを使ったfull E2E、`enabled: true`への切替、Slack通知の実確認は未実施。
- 次工程への引き継ぎ: #72の受入異常系、#73のNBA_Draft_DB実sourceによるdisabled dry-run、#74以降の人間承認付き手動E2Eへ進む。

### Portfolio Reviewer
- 入力: 本ブランチのbase（`origin/main`）との差分、テスト結果、生成物、ブラウザ検証結果。
- 実施内容: 既存sourceの公開物を変更していないこと、NBA_Draft_DBだけがindexへ0件のprojectとして追加されていること、`enabled: false`と初期provenanceの整合、3入力受入契約との整合を確認した。
- 成果物: 重大な差分混入なしのレビュー結果。
- 検証結果: `git diff --check`、全テスト、生成物check、1280px/320pxブラウザ確認が合格。
- 未解決事項: GitHub Actions上の実E2EとGitHub Pages/Slackの外部確認。
- 次工程への引き継ぎ: PR作成後にCIとGitHub上の差分を再確認する。

## 主要な判断
- 判断: NBA_Draft_DBは登録直後に`enabled: true`へ変更せず、空の初期provenanceを保存する。
- 理由: 生成元Issue #11の進捗時点で、承認済み`publish: true`固定commitと実公開は未実施であり、#74の明示承認前に公開を開始しないため。
- 判断: 既存の受入workflow・renderer・通知実装は変更せず、既存のsource registry契約へNBA_Draft_DBを追加する。
- 理由: 受入入力、固定SHA検証、`a_rendered`生成、disabled no-op、Pages/Slack境界は既存実装で共通化されているため。

## 最終結果
- 解決したこと: NBA_Draft_DBを公開受入対象へ登録し、公開済みレコードなしの初期状態とproject導線を準備した。
- 変更ファイル: `config/sources.json`、`projects/README.md`、`provenance/NBA_Draft_DB/initial.json`、`projects/NBA_Draft_DB/index.html`、`projects/index.html`、`tests/test_source_registry.py`、`tests/test_read_only_acceptance.py`、本作業記録のMarkdown/HTML。
- 検証結果: `python3 -m unittest discover -s tests -v`（94件合格）、registry/provenance検証（合格）、`python3 -m scripts.publish.index_generator --check`（合格）、`python3 scripts/dev/validate_work_record_filenames.py`（合格）、`git diff --check`（合格）。ブラウザは全project indexとNBA_Draft_DB project indexを1280x900/320x800で確認し、HTTP 200、横overflowなし、console/page errorなし。
- 作業ブランチ: `codex/071-nba-draft-db-public-integration`
- コミット: 本作業記録を含む課題commit
- PR: 未作成（外部公開されるPR作成は明示許可後に実施）
- PRレビュー・CI: ローカルレビュー済み。GitHub上のCIは未実施。
- 未解決事項: #72〜#76の残作業、生成元側の承認、Actions実行、Pages公開URL、Slack通知、運用引き継ぎ。
- 次アクション: #72の受入契約確認後、生成元の固定commitを用意して#73のdisabled dry-runを実施する。

## GitHub Issue状況
確認日時（JST）: 2026-08-31 15:57
取得範囲: `tj-999-comp/sandbox-pages`のNBA_Draft_DB関連Issue全件、および対応する`tj-999-comp/NBA_Draft_DB`のPortfolio関連Issue全件。GitHub CLIで取得した時点のsnapshot。

### 親子関係
```text
#70 NBA_Draft_DBの作業記録をPages公開・Slack通知まで接続する
├── #71 source registry登録・初期状態固定
├── #72 固定commit・basename限定公開要求の受入
├── #73 disabled受入dry-run・no-op検証
├── #74 手動E2E可能状態への有効化
├── #75 Pages公開・Slack通知のfull E2E
└── #76 公開運用・停止手順の引き継ぎ
```

### 優先順位順の未完了一覧
| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [sandbox-pages #70 NBA_Draft_DBの作業記録をPages公開・Slack通知まで接続する](https://github.com/tj-999-comp/sandbox-pages/issues/70) | Open | 親Epic。#71〜#76の完了を追跡する。 |
| 2 | 未設定 | [sandbox-pages #71 NBA_Draft_DBをsource registryへ登録し初期状態を固定する](https://github.com/tj-999-comp/sandbox-pages/issues/71) | Open | 本作業の対象。PRマージ後に完了確認する。 |
| 3 | 未設定 | [sandbox-pages #72 NBA_Draft_DBの固定commit・basename限定公開要求を受け入れる](https://github.com/tj-999-comp/sandbox-pages/issues/72) | Open | #71完了後。3入力、固定SHA、basename、metadata、許可pathを検証する。 |
| 4 | 未設定 | [sandbox-pages #73 NBA_Draft_DBのdisabled受入dry-runとno-opを検証する](https://github.com/tj-999-comp/sandbox-pages/issues/73) | Open | #71/#72と生成元#12/#13完了後。disabled状態でwrite・deploy・通知がないことを確認する。 |
| 5 | 未設定 | [sandbox-pages #74 NBA_Draft_DBを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/74) | Open | #73の結果レビューと明示承認後に`enabled: true`へ変更する。 |
| 6 | 未設定 | [sandbox-pages #75 NBA_Draft_DBの作業記録を公開しSlack通知まで確認する](https://github.com/tj-999-comp/sandbox-pages/issues/75) | Open | #74完了後。承認済み固定commitでPages/URL/Slack/冪等性をE2E確認する。 |
| 7 | 未設定 | [sandbox-pages #76 NBA_Draft_DBの公開運用・停止手順を引き継ぐ](https://github.com/tj-999-comp/sandbox-pages/issues/76) | Open | #75完了後。停止・復旧・通知再送・rollback手順を確定する。 |
| 8 | 未設定 | [NBA_Draft_DB #11 sandbox-pagesへの作業記録公開・Slack通知連携](https://github.com/tj-999-comp/NBA_Draft_DB/issues/11) | Open | 生成元側の親Issue。公開候補とSecret/承認状態を整える。 |
| 9 | 未設定 | [NBA_Draft_DB #15 公開候補1件を承認付きで作成し受入E2Eへ引き渡す](https://github.com/tj-999-comp/NBA_Draft_DB/issues/15) | Open | #72〜#74完了後のfull E2E入力を用意する。 |
| 10 | 未設定 | [NBA_Draft_DB #16 E2E後の公開運用・停止手順を文書化する](https://github.com/tj-999-comp/NBA_Draft_DB/issues/16) | Open | #75完了後。生成元側の運用文書を確定する。 |

生成元側の#12（共通命名・metadata）、#13（validator・CI）、#14（固定commit workflow）は2026-08-31 15:57 JST時点でClosedであり、上表の未完了一覧から除外した。

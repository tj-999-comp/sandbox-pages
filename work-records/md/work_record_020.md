# 作業記録 020: Issue #6 source registryの導入
作成日: 2026-08-19

## 概要

- 課題: 公開元のrepository、配置、mode、generator、support file、容量上限をA側のallowlistとして固定する。
- 目的: 後続のmetadata validator、受入workflow、provenance検証が同じsource登録を参照できる状態にする。
- 完了条件: `B_Stats_Site`を`enabled: false`で登録し、設定loaderが不正なschema、field、path、mode、generator、容量上限を拒否し、決定的な結果を返す。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: GitHub Issue [#6](https://github.com/tj-999-comp/sandbox-pages/issues/6)、`projects/README.md`、`work_record_018`、既存のA側構成。
- 実施内容: A所有のJSON source registry、標準ライブラリだけで動くloader/validator、正常・異常系テストfixtureを追加した。`project_id`、repository/ref、relative path、destination boundary、public path、support file、generator/mode、enabled、容量上限を検証し、sourceと配下の値を決定的に正規化した。
- 成果物: `config/sources.json`、`scripts/publish/__init__.py`、`scripts/publish/source_registry.py`、`tests/test_source_registry.py`、`tests/fixtures/source_registry/invalid_generator_type.json`、契約文書の実装パス追記。
- 検証結果: unittest 10件、Python構文、既存work-record filename validator、HTML再生成check、`git diff --check`に合格した。
- 未解決事項: #6のsource登録は`enabled: false`のため、実際の受入・公開・Pages変更は後続Issueの対象である。
- 次工程への引き継ぎ: #7の共通metadata validatorは本registryの登録`project_id`とallowlistを参照する。

### Portfolio Performance & Accessibility Tester

- 入力: 新規生成した`work_record_020.html`、`work-records/design.md`、共通CSS。
- 実施内容: Playwrightで1280×900px、900×900px、640×900px、320×800pxを表示し、横overflow、console/page error、failed request、focusable要素数を確認した。
- 成果物: `/private/tmp/playwright-browser-verify/2026-08-19T02-13-32-970Z/report.json`と各viewportのスクリーンショット。
- 検証結果: 4 viewportすべてで横overflow、console error、page error、failed requestは0件。320pxを含む全viewportで15個のfocusable要素を取得した。
- 未解決事項: 実スクリーンリーダーによる読み上げ確認は未実施。
- 次工程への引き継ぎ: Reviewer合格後、commit前の最終差分確認へ進む。

### Portfolio Reviewer

- 入力: Issue #6の完了条件、実装差分、テスト結果。
- 実施内容: schema境界、未知field、型、path traversal、project外destination、deterministic normalization、既存公開物への非回帰を確認した。
- 成果物: 初回レビュー指摘を反映したsource registry差分。`generator_id`と`html_mode`の非文字列値を`SourceRegistryError`で拒否するfixtureテストを追加した。
- 検証結果: 再レビューで重大・中・軽微の未解決事項0件を確認した。
- 未解決事項: なし。
- 次工程への引き継ぎ: commit前に最終差分と作業記録HTMLを再確認する。

## 主要な判断

- 判断: source registryは`config/sources.json`としてA側に置く。
- 理由: YAML parserなどの追加依存を避け、標準ライブラリで決定的に読み込めるため。生成元から変更できないA所有の設定として扱う。
- 判断: Bは登録するが`enabled: false`を維持する。
- 理由: metadata、HTML安全性、no-op dry-run、手動E2Eが完了するまで自動公開を有効化しない契約に従うため。
- 判断: destinationとpublic base pathを`project_id`から導出される固定値として検証する。
- 理由: metadataや生成元入力から任意の公開先を組み立てず、project外への書き込み・公開を防ぐため。

## 追加対応: PR記載言語の統一

- 依頼: 今後のPRを必ず日本語で記載する運用ルールを追加し、Issue #6のPR本文も日本語へ統一する。
- 実施内容: `AGENTS.md`のPR作成ルールへ、PRタイトル・本文・レビュー対応コメントを日本語で記載する規則を追加した。現在のPR #27本文も同じ内容へ更新する。
- 検証結果: ルール変更とPR本文更新後に、Markdown/HTML再生成checkと差分確認を行う。
- 未解決事項: PR #27の外部レビューとマージは未完了。

## 最終結果

- 解決したこと: `B_Stats_Site`の公開元、branch、source/metadata/destination path、support file、generator、HTML mode、enabled状態、容量上限をA側のregistryへ登録し、後続処理で利用できる検証済みデータとして読み込めるようにした。
- 変更ファイル: `AGENTS.md`、`config/sources.json`、`scripts/publish/__init__.py`、`scripts/publish/source_registry.py`、`tests/test_source_registry.py`、`tests/fixtures/source_registry/invalid_generator_type.json`、`projects/README.md`、本作業記録と対応HTML。
- 検証結果: `python3 -m unittest discover -s tests -v`（10件合格）、`py_compile`、`python3 scripts/dev/validate_work_record_filenames.py`、`python3 scripts/dev/convert_work_records_to_html.py --check`、`git diff --check`に合格した。Playwrightの1280/900/640/320pxでも横overflowと実行時エラーは0件だった。既存`projects/`公開ファイル、Pages設定、workflow、B_Stats_Site側には変更がない。
- 作業ブランチ: `codex/022-issue-6-source-registry`
- コミット: 最終commitのSHAはGit履歴を参照する。
- PRレビュー・CI: Reviewerの再レビューは重大・中・軽微の未解決事項0件で合格した。CIはPR作成後に確認する。
- 未解決事項: Issue #6の実装範囲ではなし。source有効化、受入、公開は後続Issueの条件を満たすまで行わない。
- 次アクション: #7の共通命名・metadata validatorへ進む。B側では#28の親READMEリンク修正を別ブランチで進める。

## GitHub Issue状況

確認日時（JST）: 2026-08-19 10:58
取得範囲: `tj-999-comp/sandbox-pages` #5、#6、#7、#8、#9、#10、#17、および `tj-999-comp/B_Stats_Site` #28、#29。Pull Requestは対象外。

### 親子関係

```text
#5（sandbox-pagesの親Epic・未完了）
├── sandbox-pages #6（A-01・未完了）
├── sandbox-pages #7（A-02・未完了）
├── sandbox-pages #8（A-03・未完了）
├── sandbox-pages #9（A-04・未完了）
├── sandbox-pages #10（A-05・未完了）
├── sandbox-pages #17（A-12・未完了）
├── B_Stats_Site #28（B-01・未完了）
└── B_Stats_Site #29（B-02・未完了）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [sandbox-pages #6](https://github.com/tj-999-comp/sandbox-pages/issues/6) 公開元source登録を設定ファイル化する | 未完了 | 本作業。A-01。完了後に#7へ進む |
| 2 | P0 | [sandbox-pages #7](https://github.com/tj-999-comp/sandbox-pages/issues/7) 共通命名・metadata schema validatorを実装する | 未完了 | #6完了後 |
| 3 | P0 | [sandbox-pages #8](https://github.com/tj-999-comp/sandbox-pages/issues/8) 受入ファイルのpath・種別・容量validatorを実装する | 未完了 | #6/#7完了後 |
| 4 | P0 | [sandbox-pages #9](https://github.com/tj-999-comp/sandbox-pages/issues/9) source_html向けHTML・CSS・URL安全validatorを実装する | 未完了 | #7/#8完了後 |
| 5 | P0 | [sandbox-pages #10](https://github.com/tj-999-comp/sandbox-pages/issues/10) provenance manifest schemaとdrift検査を実装する | 未完了 | #6〜#8完了後 |
| 6 | P0 | [B_Stats_Site #28](https://github.com/tj-999-comp/B_Stats_Site/issues/28) 親ディレクトリREADMEリンクをproject内リンクへ修正する | 未完了 | #6と並行可能。通常publish有効化前に完了 |
| 7 | P0 | [B_Stats_Site #29](https://github.com/tj-999-comp/B_Stats_Site/issues/29) 001〜010のmetadataと生成元validator・CIを追加する | 未完了 | B-01完了後、Aの#7/#9と連携 |
| 8 | P1 | [sandbox-pages #17](https://github.com/tj-999-comp/sandbox-pages/issues/17) read-only受入workflowをdry-runで実装する | 未完了 | A-01〜05とB-02完了後 |
| 9 | P0 | [sandbox-pages #5](https://github.com/tj-999-comp/sandbox-pages/issues/5) プロジェクト進捗ページの自動公開を段階導入する | 未完了 | 親Epic。全critical pathを追跡 |

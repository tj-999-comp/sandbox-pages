# 作業記録 022: 作業記録HTML上部リンクの撤去
作成日: 2026-08-20

## 概要

- 課題: 既存の作業記録HTML上部リンクを撤去し、B_Stats_Site Issue #28と`design.md`の方針を確認する。
- 目的: 作業記録本文の上部にあるナビゲーションリンクをなくし、記録本文への集中を維持する。
- 完了条件: converterから上部リンクを削除し、既存HTMLを再生成し、PC・320px表示とエラーのないことを確認する。作業記録Markdown/HTMLとPRを作成する。

## 適用した役割

### Portfolio UI Designer

- 入力: `tj-999-comp/B_Stats_Site` Issue #28、`projects/B_Stats_Site/design.md`、既存converterと生成HTML。
- 実施内容: Issue #28が求める親ディレクトリREADMEリンクの解消状況を確認したうえで、今回の明示要件である上部リンク全撤去を適用した。上部のトップページ、運用ルール、デザインガイド、Markdown原本リンクを対象とし、フッターのMarkdown原本リンクは対象外として残した。
- 成果物: 上部`topbar`を生成しないconverterテンプレート。
- 検証結果: 21件の生成HTMLから`topbar`、`wordmark`、`toplinks`を検索し、該当0件を確認した。
- 未解決事項: なし。
- 次工程への引き継ぎ: Frontend Engineerへconverter変更と全HTML再生成を引き継ぐ。

### Portfolio Frontend Engineer

- 入力: `scripts/dev/convert_work_records_to_html.py`、21件の作業記録Markdown/HTML、既存のIssue #7実装。
- 実施内容: converterの上部`topbar`ブロックを削除し、`work_record_001`〜`021`を決定的に再生成した。上部リンク撤去を固定するconverterテストを追加した。
- 成果物: converter、19件のユニットテスト、21件の再生成HTML、本作業記録。
- 検証結果: converter再生成check、既存work-record validator、Python構文、`git diff --check`に合格した。
- 未解決事項: なし。
- 次工程への引き継ぎ: ReviewerとブラウザTesterへ引き継ぐ。

### Portfolio Performance & Accessibility Tester

- 入力: `work_record_001.html`と`work_record_021.html`、PC・スマートフォン表示条件。
- 実施内容: Playwrightで1280×900、900×900、640×900、320×800を表示し、横overflow、console error、page error、failed requestを確認した。
- 成果物: `/private/tmp/playwright-browser-verify/2026-08-19T16-29-28-947Z/report.json`、`/private/tmp/playwright-browser-verify/2026-08-19T16-29-43-883Z/report.json`。
- 検証結果: 両ページの全4viewportで横overflow、console error、page error、failed requestは0件。上部リンクは表示されず、本文下部のMarkdown原本リンクは維持された。
- 未解決事項: スクリーンリーダーによる読み上げ確認は未実施。
- 次工程への引き継ぎ: Reviewerへブラウザ証跡と静的確認を引き継ぐ。

### Portfolio Reviewer

- 入力: Issue #28、`design.md`、converter差分、全21件の生成HTML、テスト結果。
- 実施内容: 上部リンク撤去の要件適合、本文・basename・既存URLを変更していないこと、作業記録のMarkdown/HTML対応、無関係なファイル混入を確認した。
- 成果物: PR作成前レビュー。
- 検証結果: 重大0件、中0件、軽微0件。差し戻し不要と判定した。
- 未解決事項: なし。
- 次工程への引き継ぎ: 対象ファイルをcommitし、Macのキーチェーン資格情報でPush後にPRを作成する。

## 主要な判断

- 判断: Issue #28の最小要件は親READMEリンクの修正だが、今回の明示要件に従い上部リンクをまとめて撤去した。
- 理由: ユーザー指定がIssue本文より具体的であり、`design.md`の「ナビゲーションリンクも原則として通常のテキストリンク」という方針と競合しないため。
- 判断: フッターのMarkdown原本リンクは残した。
- 理由: 上部導線の撤去範囲に含めず、記録原本へ戻る既存の下部導線を維持するため。

## 最終結果

- 解決したこと: 既存21件の作業記録HTMLから上部リンクを撤去し、今後のconverter生成でも上部リンクが復活しない状態にした。
- 変更ファイル: `scripts/dev/convert_work_records_to_html.py`、`tests/test_work_record_converter.py`、`work-records/work_record_001.html`〜`work_record_021.html`、本作業記録のMarkdownとHTML。Issue #7実装の未コミット変更も同じPR対象に含める。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（19件合格）、`py_compile`、converter `--check`、work-record filename validator、上部リンク検索、`git diff --check`、PlaywrightのPC/320px確認に合格した。
- 未解決事項: なし。
- 次アクション: PR #28の外部レビューとマージ判断を待つ。

## GitHub Issue状況

確認日時（JST）: 2026-08-20 01:30
取得範囲: `tj-999-comp/sandbox-pages`の親Issue #5とPhase 1のIssue #6〜#8、および`tj-999-comp/B_Stats_Site` Issue #28

### 親子関係

```text
#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する
├── #6 [Publish] 公開元source登録を設定ファイル化する
├── #7 [Publish] 共通命名・metadata schema validatorを実装する
└── #8 [Publish] 受入ファイルのpath・種別・容量validatorを実装する
```

関連Issue: `B_Stats_Site #28`（親Issueは`sandbox-pages #5`）

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [sandbox-pages #7 共通命名・metadata schema validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/7) | 未完了 | 本ブランチに実装済み。PRレビューと反映が残る |
| 2 | P0 | [sandbox-pages #8 受入ファイルのpath・種別・容量validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/8) | 未完了 | #6と#7の完了後に着手 |

### 関連Issueの状態

| GitHub Issue | 状態 | 関係 |
| --- | --- | --- |
| [sandbox-pages #5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | 未完了 | 親Epic |
| [sandbox-pages #6 公開元source登録を設定ファイル化する](https://github.com/tj-999-comp/sandbox-pages/issues/6) | 完了（completed） | #7の依存Issue |
| [B_Stats_Site #28 親ディレクトリREADMEリンクをproject内リンクへ修正する](https://github.com/tj-999-comp/B_Stats_Site/issues/28) | 完了（completed） | 今回の参照元。上部リンク撤去を追加適用 |

### PR・CI状況

- PR: [sandbox-pages #28 共通metadata validator実装と作業記録上部リンク撤去](https://github.com/tj-999-comp/sandbox-pages/pull/28)
- base: `main`
- head: `codex/023-issue-7-metadata-validator`
- commit: `6399953` および作業記録更新commit
- Push: Macの`osxkeychain`をGit credential helperとして使用して完了
- CI: GitHub status checkは設定されておらず、statusは空。ローカル検証は全件合格

# 作業記録 091: query_learning_BB公開失敗の原因解明と再発防止
作成日: 2026-09-07

## 概要

- 課題: `query_learning_BB`の作業記録公開要求が、検証またはapply段階で失敗した原因を特定し、再発を検出できる状態にする。
- 目的: source側の公開範囲外リンクと、公開側HTML・provenanceのdigest不一致を切り分け、公開済み成果物の整合性をCIで継続確認する。
- 完了条件: 失敗原因を記録し、現行公開状態がprovenanceと一致し、登録済みproject全体のdriftを検出するテストが合格する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: 公開側Actions run `34104776947`、`34108082517`、`34108205737`、`34109950464`、受入validator、apply engine、`query_learning_BB`のprovenance。
- 実施内容: 失敗ログと公開側の実ファイル・最新provenanceを照合した。`query_learning_BB`の既存HTML 34件は、PR #126でfooterのMarkdownリンク表示が変更された一方、当時のprovenance digestが更新されず、次回applyのdrift検査で拒否されていた。先行してマージされたPR #129で全38件・76公開ファイルとprovenanceが再同期済みであることを確認し、登録済み全projectを対象に最新manifestとのdriftを検証する回帰テストを追加した。
- 成果物: `tests/test_published_provenance_integrity.py`、本作業記録のMarkdown・metadata・生成HTML。
- 検証結果: 新規driftテストは合格。現行mainの全projectで公開ファイルと最新provenanceのmissing・extra・changedが0件であることを確認した。
- 未解決事項: なし。
- 次工程への引き継ぎ: 公開HTMLやprovenanceを変更するPRでは、同じdriftテストを必ず通過させる。

### Portfolio Reviewer

- 入力: PR #126のマージ差分、PR #129の修正内容、公開側provenance、Actions失敗ログ。
- 実施内容: source validationの失敗とapply時のprovenance driftを別事象として整理し、PR #129が対象project以外を変更せず全38件を再同期していることを確認した。回帰テストの対象範囲、最新manifestの選択、`index.html`を除く公開ファイルinventoryの照合内容をレビューした。
- 成果物: 原因分類と再発防止判定を本記録へ反映。
- 検証結果: PR #129のValidate checkは成功。新規テストを含むローカル全テストで確認する。
- 未解決事項: なし。
- 次工程への引き継ぎ: PR作成後、GitHub上のCIと公開要求のno-opまたは成功結果を確認する。

## 主要な判断

- 判断: 公開済みHTMLを旧状態へ戻さず、現行HTMLを正としてprovenanceを再同期したPR #129の復旧を採用する。
- 理由: footer変更は共通公開HTMLの意図した変更であり、古いHTMLへ戻すと公開デザインの修正を失うため。provenanceは公開成果物の監査記録として現行ファイルと一致させる必要がある。
- 判断: apply engineのdrift拒否を緩和せず、CIに全registered projectのdrift照合を追加する。
- 理由: provenanceと公開物の不一致を自動上書きで隠すと、意図しない公開成果物の変更を見逃すため。今回のようなmerge時のmanifest漏れを早期に検出する方が安全である。

## 最終結果

- 解決したこと:
  - run `34104776947`と`34108082517`では、`query_learning_BB`の作業記録内に`../../Apps/docs/HOSTING_CLOUDFLARE.md`、`../../README.md`というproject外リンクがあり、A-04 renderer validationで拒否されたことを確認した。source側修正後のdry-runは通過した。
  - run `34108205737`と`34109950464`では、PR #126のfooter変更により`work_record_001.html`〜`work_record_034.html`がprovenanceと不一致となり、applyが安全のため拒否したことを確認した。
  - PR #129で`query_learning_BB`のwork_record_001〜038、76公開ファイル、provenanceを再同期済みであることを確認した。
  - 登録済み全projectの最新provenanceと公開ファイルを照合する回帰テストを追加した。
- 変更ファイル: `tests/test_published_provenance_integrity.py`、`work-records/md/work_record_091.md`、`work-records/metadata/work_record_091.yml`、`work-records/work_record_091.html`。
- 検証結果: 新規driftテスト1件成功。既存テストを含む全テスト、HTML生成・check、filename validator、`git diff --check`をPR工程で確認する。
- 作業ブランチ: `codex/091-repair-query-provenance`。
- コミット: `093d64f`（回帰テストと作業記録）。
- PR: [公開側PR #130](https://github.com/tj-999-comp/sandbox-pages/pull/130)（作業中）。先行復旧PRは[公開側PR #129](https://github.com/tj-999-comp/sandbox-pages/pull/129)（マージ済み）。
- PRレビュー・CI: PR #129のValidate check成功。PR #130で新規driftテストをCI確認する。
- 未解決事項: なし。
- 次アクション: 本作業のPRをmerge後、`query_learning_BB`の作業記録公開要求を再実行し、dry-run・apply・Pages deployの成功またはno-opを確認する。

## GitHub Issue状況

確認日時（JST）: 2026-09-07 22:08
取得範囲: `tj-999-comp/sandbox-pages`のOpen Issue全件（Pull Request除外）
取得件数: 0件（一覧行数: 0件）

### 親子関係

```text
親子関係なし（Open Issueなし）
```

### 優先順位順の未完了一覧

該当Issueなし。

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |

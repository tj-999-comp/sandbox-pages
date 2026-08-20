# 作業記録 029: Issue #14〜#16 Actions方針・Pages deploy・進捗index
作成日: 2026-08-20

## 概要

- 課題: GitHub Issue #14、#15、#16。
- 目的: Actions botの`main`反映方針を確定し、固定commit SHAのGitHub Pages deployと、provenance metadataだけを使うproject/global進捗indexを実装する。
- 完了条件: #14の判断・ruleset・権限・競合・復旧手順が文書化され、#15のworkflowと#16の決定的generatorがテストに合格し、生成indexをPC・320pxの実ブラウザで確認できていること。GitHub上のPages切替とruleset設定は、workflowを`main`へmergeした後に実施する。

## 適用した役割

### Portfolio Planner

- 入力: Issue #14〜#16、`projects/README.md`、GitHub上のruleset・Pages実状態。
- 実施内容: bot直接commit方式、人間変更のPR必須、job別最小permissions、許可差分、競合時の再適用上限、no-op、固定SHA deploy、緊急停止・復旧を決定した。GitHub APIではruleset 0件、Pagesは`main /`のlegacyであることを確認した。
- 成果物: `docs/ACTIONS_MAIN_POLICY.md`。
- 検証結果: #15、#17〜#19のworkflow契約と矛盾せず、sourceを`enabled: false`のまま維持する段階導入になっている。
- 未解決事項: `protect-main` rulesetのActive設定とPagesの`build_type: workflow`切替は、workflowのmerge後にGitHub上で実施する。
- 次工程への引き継ぎ: merge後にruleset証跡を取得し、Pages Actions切替と最初の固定SHA deployへ進む。

### Portfolio UI Designer / Copywriter

- 入力: `DESIGN.md`、Issue #16、既存トップページ、provenanceに保存されたBの10件の正規化metadata。
- 実施内容: 白・parchment・ink・Action Blueを使う低密度の一覧、日付・project・basename・タイトルの視線順、global/project間の短い導線、320pxで1列になるレイアウトを設計した。タイトルや件数は事実だけを短く表示した。
- 成果物: `projects/progress-index.css`、global/project indexのHTML構造、サイトトップのProject progress導線。
- 検証結果: 1280/900/640/320pxで横overflowなし。見出し階層、skip link、リンクfocus、長い日本語タイトルの折り返しを確認した。
- 未解決事項: なし。
- 次工程への引き継ぎ: Frontend Engineerへ決定的HTML生成とgolden testを引き継いだ。

### Portfolio Frontend Engineer

- 入力: #14方針、GitHub公式Pages workflow要件、公式Actionの現行major tag SHA、provenance manifest schema。
- 実施内容: `push`、`workflow_dispatch`、`workflow_call`に対応するPages workflowを追加し、build前とdeploy直前の2回、固定SHAとremote `main`の一致を検査した。公式Actionはcommit SHAへ固定し、buildは`contents: read`、deployは`contents: read`・`pages: write`・`id-token: write`へ分離した。provenance directoryごとの最新manifestを選び、metadataをescapeして日付降順・project ID・record番号降順でglobal/project indexを生成するCLIと`--check`を追加した。
- 成果物: `.github/workflows/deploy-pages.yml`、`.github/workflows/validate.yml`、`scripts/publish/index_generator.py`、`projects/index.html`、`projects/B_Stats_Site/index.html`、golden fixtureとテスト。
- 検証結果: unit test 50件、Python構文、YAML構文、index再生成check、work-record再生成check、filename validator、`git diff --check`に合格した。既存#12 no-opは、A所有project indexを生成元manifestから分離したうえで非回帰を確認した。
- 未解決事項: workflowのGitHub Actions実行、legacyからActionsへのPages設定変更、公開URLの本番確認はmerge前のため未実施。
- 次工程への引き継ぎ: Reviewer、Performance & Accessibility Tester、PR工程へ引き継ぐ。

### Portfolio Performance & Accessibility Tester

- 入力: `projects/index.html`、`projects/B_Stats_Site/index.html`、`index.html`、Playwright Browser Verify。
- 実施内容: 1280x900、900x900、640x900、320x800で表示し、横overflow、console error、page error、failed requestを確認した。Tabでskip linkへfocusし、global indexからproject index、既存`work_record_010.html`へ実リンクで遷移した。
- 成果物: `/private/tmp/playwright-browser-verify/2026-08-20T06-20-06-451Z/report.json`、`/private/tmp/playwright-browser-verify/2026-08-20T06-20-05-544Z/report.json`、`/private/tmp/playwright-browser-verify/2026-08-20T06-20-04-703Z/report.json`、scenario evidence。
- 検証結果: 全viewportで横overflowなし、console/page error・failed request 0件。h1は各ページ1件、skip linkとリンク遷移は期待どおりで合格した。
- 未解決事項: GitHub Pages公開URLはworkflow merge・Pages切替後に再確認する。
- 次工程への引き継ぎ: Reviewerへ静的検証とブラウザ証跡を引き継ぐ。

### Portfolio Reviewer

- 入力: Issue #14〜#16、全差分、unit test、生成check、ブラウザ証跡。
- 実施内容: 要件適合、権限分離、固定SHA照合、外部Action SHA固定、metadata以外を一覧文言へ使用していないこと、legacy補助HTMLを掲載していないこと、#12非回帰、作業記録と生成HTMLの対応を確認した。3ページの全ローカルリンクと変更対象ファイルも照合した。
- 成果物: PR作成前レビュー。
- 検証結果: 重大0件、中0件、軽微0件。差し戻し不要と判定した。
- 未解決事項: commit、push、PR、GitHub Actions CIは未実施。
- 次工程への引き継ぎ: 対象限定commit・push・Draft PRの明示承認後にPR工程へ進む。

## 主要な判断

- 判断: 公開成果物の反映はA所有workflowの直接commit方式とし、人間変更はPR必須とする。
- 理由: 検証、provenance、index、commit、固定SHA deployを同じrunで監査でき、no-opで不要なPRを作らないため。
- 判断: Pages workflowはartifact作成前とdeploy直前にremote `main`を照合する。
- 理由: concurrency待機中に`main`が進んだ場合、古いartifactを公開しないため。
- 判断: project indexはA所有の派生成果物としてsource/published manifest inventoryから分離し、generator `--check`でdriftを検出する。
- 理由: Bへindexの所有を戻さず、bootstrap manifestをA所有派生物で循環更新しないため。生成元の同名`index.html`は引き続き受入対象外である。
- 判断: global indexは既存portfolio rootを置き換えず`projects/index.html`へ生成し、rootから導線を追加する。
- 理由: 既存ゲーム・keyboard導線を維持しつつ、複数projectの進捗一覧を独立して拡張できるため。

## 最終結果

- 解決したこと: #14の運用方針を文書化し、#15の固定SHA Pages workflowと#16のproject/global index generatorをローカル実装・検証した。
- 変更ファイル: `docs/ACTIONS_MAIN_POLICY.md`、`.github/workflows/deploy-pages.yml`、`.github/workflows/validate.yml`、`scripts/publish/index_generator.py`、`projects/progress-index.css`、`projects/index.html`、`projects/B_Stats_Site/index.html`、`index.html`、`projects/README.md`、#12境界修正、テスト・golden fixture、本作業記録と対応HTML。
- 検証結果: unit test 50件合格、Python/YAML構文合格、index/work-record生成check合格、filename validator合格、PC/320pxを含む4 viewportとキーボード操作に合格。
- 作業ブランチ: `codex/029-issues-14-16-pages-index`
- コミット: 実装commit `984b1ee`。PR情報の記録は後続commitで反映する。
- PR: [#33 Issue #14〜#16: Pages Actions移行と進捗indexを実装](https://github.com/tj-999-comp/sandbox-pages/pull/33)（Draft）。base `main`、head `codex/029-issues-14-16-pages-index`。
- PRレビュー・CI: ローカル事前レビューは重大0件、中0件、軽微0件で合格。GitHub Actions CIはPRへの記録更新push後に確認する。
- 未解決事項: `protect-main` ruleset設定、PagesのActions切替、workflow本番実行、公開URLのPC/320px確認はmerge後に必要。sourceは`enabled: false`のまま維持する。
- 次アクション: PR #33のGitHub差分、CI、レビュー指摘を確認する。merge後に#14/#15のGitHub設定と本番Pages確認を完了する。

## GitHub Issue状況

確認日時（JST）: 2026-08-20 15:22
取得範囲: `tj-999-comp/sandbox-pages` Issue #5、#14〜#17。GitHub sub-issue APIでは#14〜#17を#5の子として返さず、各Issue本文の`Parent: #5`参照だけを確認した。

### 親子関係

```text
GitHub sub-issueとしての親子関係なし
#14〜#17のIssue本文にParent: #5の参照あり
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#14 Actions botのmain反映方針とbranch rulesetを確定する](https://github.com/tj-999-comp/sandbox-pages/issues/14) | Open | 方針文書を実装。ruleset設定証跡はmerge後 |
| 2 | P0 | [#15 legacy PagesをカスタムActions deployへ移行する](https://github.com/tj-999-comp/sandbox-pages/issues/15) | Open | workflowを実装。Actions切替と本番deployはmerge後 |
| 3 | P0 | [#16 project・global進捗index generatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/16) | Open | generator・golden test・ブラウザ確認済み。PR反映待ち |
| 4 | P1 | [#17 read-only受入workflowをdry-runで実装する](https://github.com/tj-999-comp/sandbox-pages/issues/17) | Open | #14〜#16反映後の次工程 |
| 5 | P0 | [#5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | Open | 親Epicとして本文から参照。critical path全体を追跡 |

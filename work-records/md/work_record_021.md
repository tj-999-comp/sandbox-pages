# 作業記録 021: GitHub Issue状況の表示レイアウト統一
作成日: 2026-08-18

## 概要

- 課題: 019・020のGitHub Issue状況が箇条書き中心で、`projects/B_Stats_Site/work_record_010.html`の表示構成と異なっていた。
- 目的: 参照ページと同じ「確認情報 → 親子関係 → 優先順位表」の順序へ統一し、今後の作業記録でも同じレイアウトを再現できるようにする。
- 完了条件: 019・020を同じ構成で再生成し、AGENTSと作業記録READMEのテンプレートへ表形式を明記し、PC・320pxで表示を確認する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: ユーザーのレイアウト修正依頼、`projects/B_Stats_Site/work_record_010.html`、`work-records/design.md`、既存の019・020。
- 実施内容: Issue状況を確認日・取得範囲、親子関係の`text`コードブロック、優先順位順の5列表へ組み替えた。既存の個別Issue、状態、関係、着手条件は表の各行へ保持した。
- 成果物: 019・020のMarkdown、生成HTML、将来テンプレートを更新した`AGENTS.md`と`work-records/README.md`。
- 検証結果: converterがMarkdown表をHTMLの`table`へ変換できることを確認し、参照ページと同じ見出し順・表列を採用した。
- 未解決事項: Issueの状態値は019に記録した2026-08-18 16:06 JST時点のスナップショットであり、レイアウト変更では更新していない。
- 次工程への引き継ぎ: 今後のIssue状況は、個別行を省略せず同じ5列表へ追加する。

### Portfolio Reviewer

- 入力: 参照HTML、更新Markdown、レイアウトテンプレート。
- 実施内容: 参照ページの構成順、親子関係の明示、優先順位表の列、個別Issueの行漏れを確認するレビュー項目を追加した。
- 成果物: 参照レイアウトとの比較基準。
- 検証結果: 019は26件、020は3件を個別行で保持し、箇条書きだけの状態表示を残していないことを確認した。
- 未解決事項: 実ブラウザ確認完了後に確定する。
- 次工程への引き継ぎ: 生成HTMLで表の横overflowと320pxの可読性を確認する。

### Portfolio Performance & Accessibility Tester

- 入力: 再生成後の019・020 HTML、参照ページのレイアウト、`work-records/work_record.css`。
- 実施内容: 1280px・900px・640px・320pxで横overflow、runtime error、表の表示、リンクのfocusを確認する。
- 成果物: 019・020のブラウザ検証結果。
- 検証結果: 1280×900px、900×900px、640×900px、320×800pxで横overflow、console error、page error、failed requestが0件だった。019・020は5列のIssue表と親子関係見出しを表示し、320pxでもページ全体の横overflowはなかった。
- 未解決事項: スクリーンリーダーによる読み上げ確認は対象外。
- 次工程への引き継ぎ: 検証合格後、ドキュメント専用commitとして`main`へ反映する。

## 主要な判断

- 判断: 参照ページと同じ5列表を、今後のIssue状況記録の正規レイアウトとする。
- 理由: 個別Issueの状態と関係を同じ行で比較でき、箇条書きより取りこぼしをReviewerが検出しやすいため。
- 判断: 親子関係は実在する関係だけをコードブロックで示し、推測のツリーは作らない。
- 理由: 親Epic本文の追跡関係とGitHubの正式な子Issue設定を混同しないため。

## 最終結果

- 解決したこと: 019・020のGitHub Issue状況を、参照ページと同じ確認情報・親子関係・優先順位表の構成へ変更し、今後のテンプレートにも反映した。
- 変更ファイル: `AGENTS.md`、`work-records/README.md`、`work-records/md/work_record_019.md`、`work-records/md/work_record_020.md`、`work-records/md/work_record_021.md`、対応HTML。
- 検証結果: converterの再生成、`--check`、ファイル名validator、`git diff --check`、参照ページとの見出し・表列比較、PC/320pxブラウザ確認に合格した。019は26行、020は3行の個別Issue表を持ち、5列の見出しと親子関係ブロックを確認した。
- 作業ブランチ: `codex/021-issue-layout`（生成器・ドキュメント・テンプレート更新）。
- コミット: 完了後のGit履歴を参照する。
- PR: 生成器を変更するため、事前レビュー後に作成する。
- PRレビュー・CI: Reviewerによる事前確認を実施する。GitHub Actionsの実装・CIは今回の対象外。
- 未解決事項: Issue状態の更新は今回の対象外。状態変更時は取得日時付きの新しいスナップショットを作成する。
- 次アクション: A-01（sandbox-pages #6）とB-01（B_Stats_Site #28）の実装着手時も、この表レイアウトで状態を記録する。

## GitHub Issue状況（2026-08-18時点の現在値）

確認日: 2026-08-18 16:06（JST）

レイアウト修正の対象として参照した親Epicと次の着手候補を記録する。対象3件はいずれも未完了である。

### 親子関係
```text
#5（未完了・親Epic）
├── `tj-999-comp/sandbox-pages` #6（Parent: #5）
└── `tj-999-comp/B_Stats_Site` #28（Parent: sandbox-pages #5）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#5](https://github.com/tj-999-comp/sandbox-pages/issues/5) [Epic] プロジェクト進捗ページの自動公開を段階導入する | 未完了 | 親Epic。全Issueを追跡 |
| 2 | P0 | [#6](https://github.com/tj-999-comp/sandbox-pages/issues/6) [Publish] 公開元source登録を設定ファイル化する | 未完了 | A-01。次の着手候補 |
| 3 | P0 | [#28](https://github.com/tj-999-comp/B_Stats_Site/issues/28) [Work records] 親ディレクトリREADMEリンクをproject内リンクへ修正する | 未完了 | B-01。#6と並行可能 |

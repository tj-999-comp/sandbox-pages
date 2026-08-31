# 作業記録 031: 未完了一覧のIssueスナップショット再取得ルールを標準化
作成日: 2026-08-20

## 概要

- 課題: 作業記録の未完了一覧が、現在のOpen Issue総数ではなく、過去に限定取得したIssue範囲だけを反映していた。
- 目的: 作業記録ごとに未完了一覧をGitHubから再取得し、集計範囲と一覧の内容を一致させる。
- 完了条件: `docs/PORTFOLIO_STANDARD.md`へ再取得、対象範囲、除外範囲、件数一致のルールを追記し、作業記録と対応HTMLを生成・検証して`main`へpushする。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: `work_record_030`で確認された、現在のOpen Issue数と記録内の未完了一覧の差異。
- 実施内容: Issueスナップショットの標準に、未完了一覧を作業記録ごとにGitHub APIから再取得すること、複数リポジトリ・関連Issueを含む場合の対象範囲明記、限定取得時の理由・除外範囲の記録、件数と行数の一致を追記した。
- 成果物: `docs/PORTFOLIO_STANDARD.md`、本作業記録のMarkdown原本と対応HTML。
- 検証結果: `git diff --check`、作業記録ファイル名検証、HTML生成後の再生成差分検証に合格した。
- 未解決事項: なし。
- 次工程への引き継ぎ: 今後の作業記録では、作成直前のOpen Issue一覧を取得して記録する。

### Portfolio Reviewer

- 入力: 標準文書の追記差分、作業記録テンプレート、HTML生成結果。
- 実施内容: 未完了一覧の再取得条件、対象範囲の記録、件数と一覧行数の一致が明文化され、既存のGitHub API失敗時の扱いと矛盾しないことを確認した。
- 成果物: commit前の差分レビュー。
- 検証結果: 対象ファイル以外の変更がないこと、Markdownと生成HTMLの対応、差分の空白エラーがないことを確認した。
- 未解決事項: なし。
- 次工程への引き継ぎ: `main`への限定commit・pushを行う。

## 主要な判断

- 判断: 未完了一覧は過去の作業記録やIssue本文の一覧を引き継がず、作業記録作成直前のOpen Issueスナップショットから作成する。
- 理由: Issueの追加・状態変更による現在数との乖離を防ぎ、記録時点の対象範囲と一覧内容を追跡可能にするため。
- 判断: 対象範囲を限定する場合は、対象条件と除外範囲を作業記録に残す。
- 理由: 特定リポジトリや親Issue配下だけを集計した場合でも、全体のOpen Issue数と混同しないようにするため。

## 最終結果

- 解決したこと: 未完了一覧を作業記録ごとに再取得するルールと、範囲・件数の整合条件を標準文書へ追加した。
- 変更ファイル: `docs/PORTFOLIO_STANDARD.md`、`work-records/md/work_record_031.md`、`work-records/work_record_031.html`。
- 検証結果: `git diff --check` 合格、`python3 scripts/dev/convert_work_records_to_html.py --check` 合格、`python3 scripts/dev/validate_work_record_filenames.py` 合格。
- 作業ブランチ: `main`（ドキュメントのみのため標準に従い直接push）。
- コミット: 標準文書更新 `9dbb0ee`、作業記録・HTML生成 `5bf12e0`。Issue状況追記と運用規則是正のcommitは完了報告に記載。
- PR: 作成なし。ドキュメント専用の短縮工程を適用。
- PRレビュー・CI: PRなし。ローカル差分・生成物検証を実施。
- 未解決事項: なし。
- 次アクション: 次回以降の作業記録作成時に、GitHubからOpen Issue一覧を都度取得する。

## GitHub Issue状況

確認日時（JST）: 2026-08-20 16:48
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue。Issueに直接関係しない作業だが、作業対象リポジトリのIssue状況を残す標準に従い、作成直前に9件を取得した。`tj-999-comp/B_Stats_Site`は今回の作業対象外のため、このスナップショットには含めていない。

### 親子関係

```text
sandbox-pages #5が親Epic。
sandbox-pages #13、#18、#19、#20、#21、#22、#23、#24は、Issue本文のParent: #5参照で#5に紐づく。
GitHub sub-issueとしての親子関係は別途確認できず、本文記載のParent参照を関係として記録する。
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | Open | 親Epic。個別Issueを依存順に完了し、手動E2Eと公開導線を確認する |
| 2 | P1 | [#18 許可範囲限定の同期apply engineを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/18) | Open | Phase 4。#10、#16、#17完了後に着手するcritical path |
| 3 | P1 | [#19 受入workflowへcommit・固定SHA deployを接続する](https://github.com/tj-999-comp/sandbox-pages/issues/19) | Open | Phase 4。#14、#15、#18完了後に着手するcritical path |
| 4 | P1 | [#20 deploy成功後のSlack通知jobを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/20) | Open | Phase 4。#10、#19完了後に着手する |
| 5 | P1 | [#21 disabled sourceでBの受入dry-runを実行する](https://github.com/tj-999-comp/sandbox-pages/issues/21) | Open | Phase 5。#12、#17、#18、およびB側#28・#29完了後に着手する |
| 6 | P1 | [#22 B sourceを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/22) | Open | Phase 5。#19、#21完了後に限定有効化する |
| 7 | P1 | [#23 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open | Phase 5。#20とB側#31完了後に実施する |
| 8 | P2 | [#13 a_rendered用の決定的rendererを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/13) | Open | Phase 6。初回B公開のcritical path外。#7、#9完了後に着手する |
| 9 | P2 | [#24 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | Open | Phase 6。初回B公開のcritical path外。#16、#18、#19完了後に着手する |

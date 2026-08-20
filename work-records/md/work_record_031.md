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
- コミット: 作業記録・HTML生成後のcommitとして完了報告に記載。
- PR: 作成なし。ドキュメント専用の短縮工程を適用。
- PRレビュー・CI: PRなし。ローカル差分・生成物検証を実施。
- 未解決事項: なし。
- 次アクション: 次回以降の作業記録作成時に、GitHubからOpen Issue一覧を都度取得する。

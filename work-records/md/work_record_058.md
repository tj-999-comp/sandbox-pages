# 作業記録 058: 取り下げdry-runの作業ツリー汚染を修正
作成日: 2026-08-28

## 概要

- 課題: GitHub Issue #24「[Operations] 監査可能な公開取り下げworkflowを実装する」。
- 目的: 公開側mainへ反映した取り下げworkflowの本番dry-runで判明した、preview出力とPython pycacheによる誤検知を修正する。
- 完了条件: dry-runがRepository Aの作業ツリーを汚さず、previewをrunner一時領域へ保存して成功すること。

## 実施内容

- 本番dry-run run `33144942694`の失敗ログを確認した。
- `PYTHONDONTWRITEBYTECODE=1`をdry-run stepにも設定した。
- preview JSONをRepository A直下ではなくrunner一時領域へ出力し、artifactとstep summaryはそこから読むようにした。
- 既存の取り下げテスト、workflow契約テスト、HTML・index・filename検証を再実行する。

## 主要な判断

- 判断: dry-runの成果物はGit管理対象外のrunner一時領域へ置く。
- 理由: dry-runは読み取り専用であり、Repository Aのclean worktree検査へ自己生成ファイルを混入させないため。
- 判断: 実際の取り下げ対象と削除範囲は変更しない。
- 理由: 今回の失敗は実行前のworkflow環境問題であり、対象`B_Stats_Site/work_record_027`の取り下げ判断を再評価する必要はないため。

## 検証結果

- ローカル全91テスト、作業記録HTML・ファイル名検証、indexチェック、`git diff --check`を実行する。
- 公開側dry-runは修正後に再実行し、成功した場合だけ返却されたSHAと最新publication_idを使ってapplyへ進む。
- 失敗したrunでは対象ファイル削除、commit、Pages deploy、Slack通知はいずれも実行されていない。

## GitHub Issue状況

確認日時（JST）: 2026-08-28 14:32
取得範囲: `tj-999-comp/sandbox-pages`のIssue #24とopen Issue一覧をGitHub CLIで再取得した。Issue #24はCLOSED、更新日時は`2026-08-28T05:29:14Z`で、open Issueは0件だった。

### 親子関係

```text
#5
└── #24 [Operations] 監査可能な公開取り下げworkflowを実装する
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |

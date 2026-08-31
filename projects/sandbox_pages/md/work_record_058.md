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
- 既存の取り下げテスト、workflow契約テスト、HTML・index・filename検証を再実行した。

## 主要な判断

- 判断: dry-runの成果物はGit管理対象外のrunner一時領域へ置く。
- 理由: dry-runは読み取り専用であり、Repository Aのclean worktree検査へ自己生成ファイルを混入させないため。
- 判断: 実際の取り下げ対象と削除範囲は変更しない。
- 理由: 今回の失敗は実行前のworkflow環境問題であり、対象`B_Stats_Site/work_record_027`の取り下げ判断を再評価する必要はないため。

## 検証結果

- ローカル全91テスト、作業記録HTML・ファイル名検証、indexチェック、`git diff --check`を実行する。
- 公開側dry-run run `33145317338`は成功し、固定SHA `407482120b3799657784d79e3486664189687613`、最新publication_id `accept-33073917462-1-B_Stats_Site-work_record_029`、対象2ファイル、残り16件を返した。
- apply・Pages deploy run `33145378676`は全job成功し、mainへ固定commit `e9fc4cd401608086ecdfaa321692955755d07ac8`（取り下げcommit）を反映した。
- 失敗したrunでは対象ファイル削除、commit、Pages deploy、Slack通知はいずれも実行されていない。

## 最終結果

- 取り下げmanifest `provenance/B_Stats_Site/withdraw-33145378676-1-B_Stats_Site-work_record_027.json`を作成し、`operation: withdraw`、`notify: false`を記録した。
- `projects/B_Stats_Site/work_record_027.html`と`projects/B_Stats_Site/md/work_record_027.md`だけを削除し、project indexは16件、global indexからも対象リンクが消えた。
- 公開URL `https://tj-999-comp.github.io/sandbox-pages/projects/B_Stats_Site/work_record_027.html`はHTTP 404を返した。
- Slack通知は発生していない。取り下げ前のprovenance manifestは履歴として保持され、復元時は取り下げcommitをrevertする方針を確認した。

## GitHub Issue状況

確認日時（JST）: 2026-08-28 14:48
取得範囲: `tj-999-comp/sandbox-pages`のIssue #24とopen Issue一覧をGitHub CLIで再取得した。Issue #24はCLOSED、更新日時は`2026-08-28T05:29:14Z`で、open Issueは0件だった。

### 親子関係

```text
#5
└── #24 [Operations] 監査可能な公開取り下げworkflowを実装する
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |

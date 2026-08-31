# 作業記録 066: 過去作業記録の遡及公開・record間リンクIssue計画
作成日: 2026-08-31

## 概要

- 課題: 作業記録公開システムの本番実行開始後も過去の作業記録が反映されず、作業記録同士のリンクも整備されていない。
- 目的: 過去作業記録の棚卸しからmetadata・HTML整備、ページ構成変更、Pagesへの遡及反映、全体受入までを一つの親Issueと子Issueで追跡可能にする。
- 完了条件: 親Issue #89と、実施順・依存関係を持つ子Issue #90〜#94を登録し、GitHub上の親子関係と本文を確認する。

## 適用した役割

### Portfolio Planner

- 入力: ユーザー要件、`docs/PORTFOLIO_STANDARD.md`、`projects/README.md`、登録済みsource、既存の導入Epic #70と#79、およびその関連Issue。
- 実施内容: 既存のsource導入課題と重複しない横断Epicとして、過去作業記録の遡及公開とrecord間リンクを親Issue #89へ整理した。棚卸し、metadata・命名・HTML整備、ページ構成・リンク実装、冪等なbootstrap公開、全体受入・運用引き継ぎの5タスクへ分解し、各Issueに完了条件、依存関係、安全条件、非対象を記載した。
- 成果物: [親Issue #89](https://github.com/tj-999-comp/sandbox-pages/issues/89)、子Issue [#90](https://github.com/tj-999-comp/sandbox-pages/issues/90)、[#91](https://github.com/tj-999-comp/sandbox-pages/issues/91)、[#92](https://github.com/tj-999-comp/sandbox-pages/issues/92)、[#93](https://github.com/tj-999-comp/sandbox-pages/issues/93)、[#94](https://github.com/tj-999-comp/sandbox-pages/issues/94)。
- 検証結果: 全Issueの作成URL、タイトル、本文、依存関係を確認した。
- 未解決事項: Issueに定義した実装・遡及公開・ブラウザ受入は後続タスクで実施する。
- 次工程への引き継ぎ: #90で全生成元の過去作業記録と公開先対応表を確定し、その結果を#91〜#94へ引き継ぐ。

### Portfolio Reviewer

- 入力: 作成済みIssueの本文、GitHub Issue一覧、#89の`sub_issues` API結果、既存の#70〜#87。
- 実施内容: #89が既存の#70・#79のsource導入Epicと目的を分けていること、#90〜#94が対象範囲と完了条件を持つこと、本文上の`Parent: #89`とGitHub上の親子関係が一致することを確認した。
- 成果物: #89の子Issue一覧（#90〜#94）と、各IssueがOpenであることの確認結果。
- 検証結果: `gh issue list`で#89〜#94を取得し、`gh api repos/tj-999-comp/sandbox-pages/issues/89/sub_issues`で5件の子Issueを再取得した。作業ツリーにソース変更がないことも確認した。
- 未解決事項: GitHub App tokenはKeychain項目を読み出せず発行できなかったため、Issue取得・登録・親子関係確認には既存の`gh`認証を使用した。
- 次工程への引き継ぎ: 実装を開始する際は#90の対応表を基準に、既存URL・番号・provenanceを維持して進める。

## 主要な判断

- 判断: #89を既存の#70・#79とは別の横断Epicとして作成した。
- 理由: #70・#79は各projectを公開pipelineへ接続する導入課題であり、今回の課題は本番稼働後に残る過去分の遡及公開とrecord間リンクを扱うため。
- 判断: 実装タスクを5件に分割し、公開前の棚卸し・整備と、公開後の受入・運用を分離した。
- 理由: 公開対象の確定、生成物の整備、ページ導線、bootstrap実行、公開後検証を分けることで、未確認recordの公開や一括Slack通知を防ぎ、各段階の完了条件を明確にできるため。
- 判断: 既存URL・採番を維持し、過去分のbootstrapではSlack通知を抑制する方針を親Issueに含めた。
- 理由: 既存公開物の非回帰と、遡及公開による重複通知・意図しない削除の防止を完了条件に含めるため。

## 最終結果

- 解決したこと: 過去作業記録の遡及公開とrecord間リンクをゴールとする親Issue #89を作成し、#90〜#94を実際の子Issueとして登録した。
- 変更ファイル: `work-records/md/work_record_066.md`、`work-records/work_record_066.html`。
- 検証結果: Issue作成、本文、Open状態、親子関係をGitHub上で確認済み。HTML生成後にconverterのcheck、ファイル名検証、Markdown構文確認、ブラウザ確認を行う。
- 作業ブランチ: `codex/066-record-issue-89`
- コミット: `ba89267`（作業記録追加）
- PR: [#96 過去作業記録公開計画の作業記録を追加](https://github.com/tj-999-comp/sandbox-pages/pull/96)
- PRレビュー・CI: GitHub上のPR #96の差分を確認済み。変更は作業記録MD/HTMLの2ファイルのみ。Actionsの`validate`（run `33366906855`）はsuccessし、merge stateは`CLEAN`だった。
- 未解決事項: #90〜#94の実装と受入、関連Issueの完了確認。作業記録PR #96のmergeとmain反映は完了している。
- 次アクション: #90から着手し、過去作業記録の対応表確定後に#91〜#94へ引き継ぐ。

## GitHub Issue状況

確認日時（JST）: 2026-08-31 16:02
取得範囲: `tj-999-comp/sandbox-pages`の今回作成した親Issue #89と子Issue #90〜#94。既存の関連導入Issue #70〜#87は依存関係の参照対象とし、今回の登録対象スナップショットには含めない。

### 親子関係

```text
#89 過去作業記録の遡及公開と作業記録間リンクを整備する
├── #90 過去作業記録を棚卸しし公開対応表を確定する
├── #91 過去作業記録のmetadata・命名・HTMLを整備する
├── #92 作業記録ページの構成とrecord間リンクを実装する
├── #93 過去作業記録をbootstrapでPagesへ遡及反映する
└── #94 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#89 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open | 親Epic。#90〜#94の完了を追跡する。 |
| 2 | 未設定 | [#90 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open | 最初の着手タスク。対象project、公開可否、生成元commit、公開先対応を確定する。 |
| 3 | 未設定 | [#91 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open | #90の棚卸し完了後。公開対象の受入可能な生成物を整備する。 |
| 4 | 未設定 | [#92 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open | #90の対応表とmetadata仕様確定後。index・個別ページの導線を実装する。 |
| 5 | 未設定 | [#93 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | Open | #90・#91・#92の受入後。固定commitとprovenanceで遡及公開する。 |
| 6 | 未設定 | [#94 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open | #90〜#93完了後。件数、リンク、ブラウザ、再実行、運用手順を検証する。 |

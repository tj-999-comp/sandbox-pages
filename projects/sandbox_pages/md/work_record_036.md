# 作業記録 036: Issue #22 B source手動E2E有効化
作成日: 2026-08-24

## 概要

- 課題: GitHub Issue #22「[Activation] B sourceを手動E2E可能な状態へ有効化する」。
- 目的: 自動triggerを追加せず、管理下の手動publishだけを通せる状態へB sourceを移行する。
- 完了条件: sourceを`enabled: true`へ変更し、A受入workflowが手動起動だけであること、Bの`main` pushからA受入を自動起動する連携がないこと、停止・復旧・rollback手順を証跡化する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: `origin/main`の最新commit `a062571`、Issue #22、既存の受入workflow・source registry・運用文書。
- 実施内容: B sourceの`enabled`を有効化し、enabled sourceを検証するテストfixtureを明示的opt-inへ更新した。A受入workflowが`workflow_dispatch`以外のtriggerを持たないことをテストで固定し、現行の手動運用と停止・復旧手順を文書へ追記した。
- 成果物: `config/sources.json`、`projects/README.md`、受入関連テスト、作業記録Markdown/HTML。
- 検証結果: Python unittest 67件が全件成功。JSON構文、`git diff --check`も成功した。
- 未解決事項: 実公開E2EはIssue #23の対象として実施していない。
- 次工程への引き継ぎ: 手動workflowから固定SHAを指定して代表レコードを受入し、commit・Pages・公開URL・Slack通知を確認する。

### Portfolio Reviewer

- 入力: Issue #22の完了条件、A側`.github/workflows/accept-source.yml`、`docs/ACTIONS_MAIN_POLICY.md`、B側`main`のworkflow定義。
- 実施内容: A受入workflowに`push`、`pull_request`、`repository_dispatch`、`schedule`のtriggerがないことを確認した。B側workflowを`main`の現行SHAで確認し、Aの受入を起動する`sandbox-pages`連携がないことを確認した。B側にはPages・検証用の既存push workflowがあるため、「Bの全push workflowがない」とは記録せず、A受入の自動起動がないという範囲で整理した。
- 成果物: Issue #22対応差分のレビュー結果、B workflow確認記録。
- 検証結果: 重大な未解決事項なし。
- 未解決事項: GitHub AppのKeychain認証が利用できず、Issue/PRの操作は未実施。公開GitHub APIによる読み取り確認は実施した。
- 次工程への引き継ぎ: push後にGitHub Actionsのrequired checksとPR差分を確認する。

## 主要な判断

- 判断: `enabled: true`への変更は`config/sources.json`と現行登録例だけに限定し、B側workflowやAのpublish workflowの自動triggerは追加しない。
- 理由: Issue #22は限定的な手動E2Eのための有効化であり、自動公開の有効化ではない。A受入workflowは既存の`workflow_dispatch`を唯一の入口として維持する。
- 判断: 緊急停止・復旧は既存の`docs/ACTIONS_MAIN_POLICY.md`に合わせ、停止、`enabled: false`復帰、provenance照合、レビュー付きrevert、正常SHAのPages再確認を記録する。
- 理由: 公開済み成果物を自動削除せず、監査可能な手順で停止・rollbackする必要があるため。

## 最終結果

- 解決したこと: `B_Stats_Site`を`enabled: true`へ変更し、明示的`--allow-enabled`を使う検証経路と、手動受入のみのtrigger契約をテストで固定した。Bの`main` pushからAの受入を自動起動する連携は設定されていない。
- 変更ファイル:
  - `config/sources.json`
  - `projects/README.md`
  - `tests/test_apply_engine.py`
  - `tests/test_pages_workflow.py`
  - `tests/test_read_only_acceptance.py`
  - `tests/test_source_registry.py`
  - `work-records/md/work_record_036.md`
  - `work-records/work_record_036.html`
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（67件、成功）、JSON構文確認（成功）、`git diff --check`（成功）。
- ブラウザ確認: `work-records/work_record_036.html`をChromiumで1280px、900px、640px、320px幅で確認。全幅でHTTP 200、横overflowなし、console/page errorなし、failed requestなし。
- 作業ブランチ: `codex/035-issue-22-activation`
- コミット: `84e01a7 feat: enable B source for manual E2E`、`838640e docs: record Issue #22 commit`
- PR: [#39 Issue #22: B sourceを手動E2E向けに有効化](https://github.com/tj-999-comp/sandbox-pages/pull/39)（Draft / OPEN）
- PRレビュー・CI: 事前レビューで重大な未解決事項なし。GitHub Actions `validate` は2026-08-24 16:00 JST時点でSUCCESS。
- 未解決事項: Issue #23の実公開E2E、Pages公開URL、Slack通知の確認は未実施。
- 次アクション: commit・push後、PRを作成してGitHub上の差分とCIを確認する。

## GitHub Issue状況

確認日時（JST）: 2026-08-24 15:49
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issueおよび親Issue #5、対象Issue #22をGitHub APIで取得した時点のsnapshot。B側workflowは`tj-999-comp/B_Stats_Site`の`main`（`c4ac9a53058b388f6d85b7f8cc52718a3796601d`）を確認した。

### 親子関係

```text
sandbox-pages #5（親Epic）
└── sandbox-pages #22（Issue本文のParent指定・今回の対象）
```

GitHub APIの`#5/sub_issues`は空だったため、上記はIssue本文の`Parent: #5`に基づく関係として記録する。

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#24 [Operations] 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | Open | 運用拡張。優先度はIssue label未設定。 |
| 2 | 未設定 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open | 本Issueで有効化した手動受入の後工程。 |
| 3 | 未設定 | [#22 [Activation] B sourceを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/22) | Open | 本作業の対象。PRと手動E2E確認が着手条件。 |
| 4 | 未設定 | [#20 [Notification] deploy成功後のSlack通知jobを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/20) | Open | #23の前提となる通知工程。 |
| 5 | 未設定 | [#13 [Renderer] a_rendered用の決定的rendererを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/13) | Open | B sourceの今回の手動E2Eとは別のrenderer工程。 |

### 完了済みの関連Issue

| GitHub Issue | 状態 | 本作業との関係 |
| --- | --- | --- |
| [#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | Closed / completed | 親Epic。 |
| [#21 [E2E] disabled sourceでBの受入dry-runを実行する](https://github.com/tj-999-comp/sandbox-pages/issues/21) | Closed / completed | enabled化の前提となるdisabled source実E2E。 |

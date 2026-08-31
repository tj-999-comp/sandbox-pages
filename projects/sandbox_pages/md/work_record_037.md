# 作業記録 037: Issue #20 deploy後Slack通知job
作成日: 2026-08-24

## 概要

- 課題: GitHub Issue [#20「[Notification] deploy成功後のSlack通知jobを実装する」](https://github.com/tj-999-comp/sandbox-pages/issues/20)。
- 目的: Pages deploy成功後の新規公開だけを、`publication_id`と公開URL付きでSlackへ通知する。
- 完了条件: createかつ非bootstrapだけの通知、公開URLの上限付きretry、no-op・update・withdraw・無関係pushの除外、通知失敗時の非rollback、同一`publication_id`での再送、Secretのjob限定受け渡し、テスト証跡を整える。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: 最新`origin/main`のcommit `37c156a`、Issue #20、既存の`accept-source.yml`・`deploy-pages.yml`・apply engine・provenance契約。
- 実施内容: apply結果へ`operation`、`publication_id`、`notify`を追加し、createだけを通知対象としてprovenanceへ記録するようにした。Pages deploy成功後にだけ動く`notify` jobを追加し、公開URLの確認、Slack payload生成、Incoming Webhook送信を実装した。validation、apply、deployへWebhook Secretを渡さず、通知jobの送信stepだけへ`SLACK_WEBHOOK_URL`を渡す構成にした。
- 成果物: `.github/workflows/accept-source.yml`、`scripts/publish/apply_engine.py`、`scripts/publish/slack_notification.py`、運用文書、テスト。
- 検証結果: Python unittest 73件成功、Python compile成功、Ruby YAML parserによるworkflow構文確認成功、`git diff --check`成功。
- 未解決事項: 実Webhookへの送信確認は未実施。GitHub Secret `SLACK_WEBHOOK_URL`は登録済みとして次工程へ引き継ぐ。
- 次工程への引き継ぎ: Secret登録後、非bootstrapの新規publishでPages deploy・公開URL・Slack通知を実環境確認する。

### Portfolio Reviewer

- 入力: Issue #20の完了条件、変更差分、通知jobの権限・Secret境界、既存のno-op・固定SHA deploy契約。
- 実施内容: deploy成功前に通知jobが実行されないこと、`create`・`no_op=false`・`notify=true`以外を除外すること、同一runの通知job再実行で`publication_id`を引き継げること、Pages失敗時に公開結果を巻き戻さないことを確認した。通知payloadへWebhook URLを含めないこと、既存のvalidation/apply/deploy jobへSecret参照がないことをテストで固定した。
- 成果物: `tests/test_pages_workflow.py`、`tests/test_apply_engine.py`、`tests/test_slack_notification.py`。
- 検証結果: 重大なコード上の未解決事項なし。実Secret・実Slack・GitHub Actions上の実runは未確認。
- 未解決事項: 外部Secret設定と実環境E2E。
- 次工程への引き継ぎ: Secret設定後に実runを確認し、Issue #23のB側#31新規publishへ接続する。

## 主要な判断

- 判断: 通知処理を`accept-source.yml`のdeploy後jobと`slack_notification.py`へ分離した。
- 理由: Pages公開と通知の失敗境界を分け、通知失敗時に公開をrollbackせず、通知jobだけを同じ`publication_id`で再実行できるようにするため。
- 判断: `--notify`を指定しても、apply engineは`operation=create`の場合だけmanifestの`notify`をtrueにする。
- 理由: 初期方針のbootstrap、update、withdraw、no-op除外をA側で強制し、呼び出し側の指定だけで通知対象を拡大しないため。
- 判断: URL確認は5回まで、Slack送信は単発とした。
- 理由: Issueの要求は公開URLの上限付きretryであり、Incoming Webhookの重複送信は同一`publication_id`で識別して再実行できる設計とするため。

## 最終結果

- 解決したこと: deploy成功後のSlack通知job、create限定判定、公開URL確認、payload生成、Secret境界、再送識別、関連テストを実装した。
- 変更ファイル:
  - `.github/workflows/accept-source.yml`
  - `docs/ACTIONS_MAIN_POLICY.md`
  - `projects/README.md`
  - `scripts/publish/apply_engine.py`
  - `scripts/publish/slack_notification.py`
  - `tests/test_apply_engine.py`
  - `tests/test_pages_workflow.py`
  - `tests/test_slack_notification.py`
  - `work-records/md/work_record_037.md`
  - `work-records/work_record_037.html`
- 検証結果: `PYTHONPYCACHEPREFIX=/tmp/issue20_pycache python3 -m unittest discover -s tests -p 'test_*.py'`（73件成功）、Python compile（成功）、Ruby YAML parser（成功）、`git diff --check`（成功）。
- ブラウザ確認: `work_record_037.html`をChromiumで1280px、900px、640px、320px幅にて確認。全幅でHTTP 200、横overflowなし、console/page errorなし、failed requestなし。workflow・運用文書変更自体は表示コードではない。
- 作業ブランチ: `codex/037-issue-20-slack-notification`
- コミット: `009935c feat: add post-deploy Slack notification`、`e847b25 docs: record Issue #20 Slack notification`
- PR: [#40 Issue #20: deploy成功後のSlack通知jobを追加](https://github.com/tj-999-comp/sandbox-pages/pull/40)（Draft / OPEN）。
- PRレビュー・CI: ローカル事前レビュー合格。GitHub Actions Validate [run #32705496102](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32705496102)はSUCCESS。GitHub上の外部レビューは未実施。
- 未解決事項: 実publish run、実Slack通知、B側#31の新規publish要求。
- 次アクション: PR #40のレビュー・merge後、非bootstrapの新規publishでPages deployとSlack通知を実環境確認する。mergeは自動実行しない。

## GitHub Issue状況

確認日時（JST）: 2026-08-24 16:57
取得範囲: `tj-999-comp/sandbox-pages`のOpen Issue全件、および今回の依存・後続にあたる`tj-999-comp/B_Stats_Site`の#30〜#32をGitHub connectorで取得した時点のsnapshot。B側のDB関連Open Issueは今回の公開導線と無関係のため対象外とした。

### 親子関係

```text
sandbox-pages #5（親Epic）
├── sandbox-pages #13（Open）
├── sandbox-pages #20（今回の対象）
├── sandbox-pages #23（後続、#20完了後）
└── sandbox-pages #24（Open）

sandbox-pages #5
├── B_Stats_Site #30（Open、#31の前提）
├── B_Stats_Site #31（Open、#23の前提）
└── B_Stats_Site #32（Open、#23完了後）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#20 [Notification] deploy成功後のSlack通知jobを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/20) | Open | 今回の対象。#10・#19完了済み。Secret設定と実run確認が残る。 |
| 2 | 未設定 | [B_Stats_Site #31 [E2E] 新規作業記録1件を手動publish要求する](https://github.com/tj-999-comp/B_Stats_Site/issues/31) | Open | #23の前提。#30・#20・#22完了後。 |
| 3 | 未設定 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open | #20とB側#31完了後。 |
| 4 | 未設定 | [B_Stats_Site #30 [Actions] 手動公開要求workflowとdispatch権限を設定する](https://github.com/tj-999-comp/B_Stats_Site/issues/30) | Open | #31の前提。B側の手動dispatch経路。 |
| 5 | 未設定 | [B_Stats_Site #32 [Automation] main更新時の公開要求triggerを有効化する](https://github.com/tj-999-comp/B_Stats_Site/issues/32) | Open | #23のE2E合格後。 |
| 6 | 未設定 | [#13 [Renderer] a_rendered用の決定的rendererを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/13) | Open | 初回B公開のcritical path外。 |
| 7 | 未設定 | [#24 [Operations] 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | Open | 初回B公開のcritical path外。 |

### 完了済みの関連Issue

| GitHub Issue | 状態 | 本作業との関係 |
| --- | --- | --- |
| [#10 [Publish] provenance manifest schemaとdrift検査を実装する](https://github.com/tj-999-comp/sandbox-pages/issues/10) | Closed / completed | 通知対象とpublication_idを保持するmanifestの前提。 |
| [#19 [Actions] 受入workflowへcommit・固定SHA deployを接続する](https://github.com/tj-999-comp/sandbox-pages/issues/19) | Closed / completed | deploy成功後jobを接続する前工程。 |
| [#22 [Activation] B sourceを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/22) | Closed / completed | 次の実公開E2Eを可能にした前工程。 |

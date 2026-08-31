# 作業記録 035: Issue #21 disabled source実E2E
作成日: 2026-08-24

## 概要

- 課題: GitHub Issue #21「[E2E] disabled sourceでBの受入dry-runを実行する」。
- 目的: PR #38をmainへ反映した後、B-02固定SHAを使って`work_record_001`〜`010`を実GitHub Actionsで受入し、disabled sourceのread-only受入、apply no-op、Pages deploy skip、A側無変更を確認する。
- 完了条件: 10件すべてでA-02〜A-04が合格し、`enabled=false`、applyがno-op、deployがskip、Aの`main`・Pages・Slackに変更がないことを確認する。

## 適用した役割

### Portfolio Reviewer

- 入力: マージ済みPR #38、A `main`のmerge commit `cc54ce6227830b75b1d365cc7caa7e27cdb55e42`、B-02固定SHA `43ebad8db4eff14c0a8e0d928ad193291fdfd60d`、`accept-source.yml`。
- 実施内容: GitHub App installation tokenをKeychainから再発行し、A `main`からB_Stats_Siteの10対象をdispatchした。concurrencyにより初回同時dispatchの一部がcancelledになったため、残りを1件ずつ完了待ちで再dispatchした。各runのjob、acceptance artifact、apply artifactを取得して内容を照合した。
- 成果物: 10件のGitHub Actions実E2E結果、acceptance/apply artifact、Issue #21完了コメント、Issue #21のcompletedクローズ、作業記録035。
- 検証結果: 最終runは10件すべてでdry-run success、apply success、deploy skipped。全件で`enabled=false`、`dry_run=true`、`apply=false`、固定SHA一致、inventory 45件、target inventory 6件、metadata・acceptance files・content safety passed、`no_op=true`、`commit_sha=null`を確認した。
- 未解決事項: なし。初回同時dispatchでcancelledとなったrunは最終結果に採用せず、対象ごとの再実行successを採用した。
- 次工程への引き継ぎ: #21は完了済み。次は未完了Issue #20、#22、#23の依存条件を確認する。

## 主要な判断

- 判断: concurrencyでcancelledになった初回runを成功扱いにせず、対象basenameごとに完了したrunを再実行して採用する。
- 理由: `pages-production-main`の同一concurrency groupでは同時dispatchを一括投入するとpending runが置き換えられるため、10対象それぞれの実結果を独立して残す必要がある。
- 判断: disabled sourceではapply successをno-op成功として扱い、deploy skippedを合格とする。
- 理由: workflowの設計どおり、受入検証は実行するが、`enabled=false`のsourceをA `main`へ反映せず、Pages公開も実行しないことが今回の受入条件だからである。

## 最終結果

- 解決したこと: B-02固定SHAの001〜010を実workflowで受入し、disabled sourceのA-02〜A-04合格、apply no-op、deploy skip、A側無変更を実証した。
- 実行条件: repository A `tj-999-comp/sandbox-pages`、ref `main`、repository B `tj-999-comp/B_Stats_Site`、source commit `43ebad8db4eff14c0a8e0d928ad193291fdfd60d`。
- run結果:

| 対象 | Run | 結果 |
| --- | ---: | --- |
| `work_record_001` | [32697085244](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697085244) | success / no-op / deploy skipped |
| `work_record_002` | [32697209487](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697209487) | success / no-op / deploy skipped |
| `work_record_003` | [32697213303](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697213303) | success / no-op / deploy skipped |
| `work_record_004` | [32697250925](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697250925) | success / no-op / deploy skipped |
| `work_record_005` | [32697280267](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697280267) | success / no-op / deploy skipped |
| `work_record_006` | [32697302058](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697302058) | success / no-op / deploy skipped |
| `work_record_007` | [32697338632](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697338632) | success / no-op / deploy skipped |
| `work_record_008` | [32697367311](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697367311) | success / no-op / deploy skipped |
| `work_record_009` | [32697400976](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697400976) | success / no-op / deploy skipped |
| `work_record_010` | [32697101368](https://github.com/tj-999-comp/sandbox-pages/actions/runs/32697101368) | success / no-op / deploy skipped |

- 無変更確認: dispatch前後のA `main`は`cc54ce6227830b75b1d365cc7caa7e27cdb55e42`で一致。Pages deploy workflow runはなく、deploy jobは全件skipped。Slack通知も発生していない。
- Issue状態: [#21](https://github.com/tj-999-comp/sandbox-pages/issues/21)へ完了結果をコメントし、`completed`としてクローズした。
- 変更ファイル: 本作業記録と対応HTML。
- 検証結果: 10件のjob・artifact照合、A `main` ref照合、Pages workflow runなしの確認、Issue #21状態照合。
- 未解決事項: なし。
- 次アクション: #20、#22、#23の前提に従って次課題へ進む。

## GitHub Issue状況

確認日時（JST）: 2026-08-24 15:32
取得範囲: `tj-999-comp/sandbox-pages`の#5、#12、#17〜#23、および`tj-999-comp/B_Stats_Site`の#28〜#29をGitHub APIで取得した時点のsnapshot。

### 親子関係

```text
sandbox-pages #5（親Epic）
├── sandbox-pages #12（完了）
├── sandbox-pages #17（完了）
├── sandbox-pages #18（完了）
├── sandbox-pages #19（完了）
├── sandbox-pages #20（未完了）
├── sandbox-pages #21（今回の対象・完了）
├── sandbox-pages #22（未完了）
└── sandbox-pages #23（未完了）

sandbox-pages #5
├── B_Stats_Site #28（完了）
└── B_Stats_Site #29（完了）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P1 | [#20 [Notification] deploy成功後のSlack通知jobを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/20) | Open | #19完了後の通知工程。#23の前提 |
| 2 | P1 | [#22 [Activation] B sourceを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/22) | Open | #19・#21完了後。source有効化前に#21の重大問題0が必要 |
| 3 | P1 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open | #20とB側#31完了後 |

### 完了済みの関連Issue

| GitHub Issue | 状態 | 本作業との関係 |
| --- | --- | --- |
| [#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | Closed / completed | 親Epic |
| [#12 [Bootstrap] 既存Bのno-op同期dry-runを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/12) | Closed / completed | no-op/bootstrap検証の前提 |
| [#17 [Actions] read-only受入workflowをdry-runで実装する](https://github.com/tj-999-comp/sandbox-pages/issues/17) | Closed / completed | 受入workflowの前工程 |
| [#18 [Publish] 許可範囲限定の同期apply engineを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/18) | Closed / completed | apply境界の前工程 |
| [#19 [Actions] 受入workflowへcommit・固定SHA deployを接続する](https://github.com/tj-999-comp/sandbox-pages/issues/19) | Closed / completed | disabled時のapply/deploy skipを含むworkflow |
| [#21 [E2E] disabled sourceでBの受入dry-runを実行する](https://github.com/tj-999-comp/sandbox-pages/issues/21) | Closed / completed | 本作業で実E2E完了 |
| [B_Stats_Site #28 親ディレクトリREADMEリンクをproject内リンクへ修正する](https://github.com/tj-999-comp/B_Stats_Site/issues/28) | Closed / completed | B-01固定commit |
| [B_Stats_Site #29 001〜010のmetadataと生成元validator・CIを追加する](https://github.com/tj-999-comp/B_Stats_Site/issues/29) | Closed / completed | B-02固定commit |

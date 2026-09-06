# 作業記録 087: Issue #93 固定対象の一括bootstrap経路を実装
作成日: 2026-09-06

## 概要

- 課題: GitHub Issue #93「過去作業記録をidempotentなbootstrapでPagesへ遡及反映する」。
- 目的: 固定source commitと対象basename集合を検証し、複数recordを一つの監査可能な反映単位としてPagesへ反映できる経路を追加する。
- 完了条件: dry-runで対象差分を確認でき、通知なしの一括apply、同一入力のno-op、drift・改名・削除防止、固定SHA・provenance・index整合を検証できる状態にする。#93の完了通知は本作業記録`work_record_087`だけを対象にする。

## 適用した役割

### Portfolio Planner

- 入力: Issue #93の完了・安全条件、#90の棚卸し対応表、#91のmetadata整備、#92のrecord navigation、既存の単一record受入workflow。
- 実施内容: 単一recordの通常publishと過去分一括反映を分離し、projectごとに固定SHAと対象basenameをdispatch入力として保持する構成へ分解した。bootstrap対象はsource側のpublish:trueかつ既存provenanceにないrecord集合に限定し、履歴の一括反映は通知しない契約にした。#93の完了通知は作業記録`work_record_087`だけを通常の単一record公開で送る。
- 成果物: `bootstrap_engine` と専用workflowの実装方針。#90時点の候補に加え、#91・#92で追加された`sandbox_pages`の`work_record_084`〜`086`も固定SHAの対象範囲へ含める。
- 検証結果: B_Stats_Siteはsource SHA `14468e72a58a00be29e18d132eda05ba0c1f01d7`で13件、sandbox_pagesは#92 merge SHA `0133974ecbeeada9ef0e8f0a52f9f397fe841fed`で15件の未公開対象を算出した。
- 未解決事項: sandbox_pagesの過去記録反映後に、#93記録だけを単体更新・通知する。
- 次工程への引き継ぎ: `bootstrap.yml`の通知なし反映と、`accept-source.yml`による`work_record_087`単体通知を完了し、#94へ引き継ぐ。

### Portfolio Frontend Engineer

- 入力: `scripts/publish/apply_engine.py`、`scripts/publish/read_only_acceptance.py`、`scripts/publish/provenance.py`、`scripts/publish/index_generator.py`、#92の`record_navigation`。
- 実施内容: `scripts/publish/bootstrap_engine.py`を追加し、source registry、固定SHA、全source inventory、metadata、HTML安全性またはA所有renderer、既存provenance drift、index staleをapply前に検証するようにした。対象recordを同一一時ツリーへ反映し、既存recordのnavigationも更新して、一つのmanifestとindex更新を生成する。既存ファイルの削除・改名は行わず、bootstrapの通知入力とSlack通知jobを廃止した。通常の`update`は通知対象に維持し、失敗時の再通知は単一・複数対象に対応させた。
- 成果物: `.github/workflows/bootstrap.yml`、bootstrap engine、engine/workflowのテスト。
- 検証結果: `source_html`と`a_rendered`の共通処理をfixtureで確認し、create/update通知対象と、create後の同一入力再実行が`no_op: true`、変更pathなしになることを確認した。
- 未解決事項: 過去15件への通知取り消しは実施できない。既送信通知はSlack側での削除・訂正が必要な場合だけ別途判断する。
- 次工程への引き継ぎ: #94でPages全体とrecord間リンクの受入を確認する。

### Portfolio Reviewer

- 入力: Issue #93、bootstrap engine/workflow差分、既存publish workflow、provenance契約、テストfixture。
- 実施内容: 対象集合がpublish:trueかつ未公開recordに限定されること、source SHA・main SHA・既存provenanceを照合すること、通常の単一recordだけを通知対象にし、bootstrapを通知対象外にすること、dry-run artifactをapply入力へbindすることをレビューした。
- 成果物: 通常publishのcreate/update通知経路を維持しつつ、bootstrapの通知入力・通知job・engine引数を削除する更新。
- 検証結果: 実Workflow run `34038486385`はsandbox_pagesの16件反映、Pages deploy、通知jobまで成功したが、当時の`notify=true`入力により16件を通知した。このうち#93で意図した通知は`work_record_087`だけだったため、今回の修正で今後のbootstrap通知を禁止する。
- 未解決事項: 既に送信された15件の通知は取り消せない。追加の履歴bootstrap通知は発生しない。
- 次工程への引き継ぎ: #93の通知方針修正と`work_record_087`単体公開を完了し、#94の全体受入へ引き継ぐ。

## 主要な判断

- 判断: 通常の単一record受入とは別に、複数basenameを一つのbootstrap applyへ渡す。
- 理由: 過去分を個別commit・個別deployすると、同一監査commit、通知抑制、再実行no-opという要件を満たしにくいため。
- 判断: manifestの`operation`は既存provenance schemaの`create` / `update`を使用し、bootstrap識別はpublication_idとworkflowで行う。反映を伴う通常の単一recordの`create`、`update`だけをSlack通知対象とし、bootstrap/backfillは常に通知しない。
- 理由: 履歴一括反映で15件以上の不要な通知を発生させず、作業完了時は対象作業記録1件だけを通知するため。no-opとwithdrawも引き続き通知しない。
- 判断: 対象sourceのpublish:true集合と既存provenanceとの差分を対象集合と一致させる。
- 理由: 対象漏れ、publish:falseの誤公開、対象外recordの混入をapply前に停止するため。

## 最終結果

- 解決したこと: 固定source SHA・対象record集合・既存provenanceを検証し、複数recordを同一commitで反映するbootstrap engineとdry-run/apply/deploy workflowを追加した。通常publishのcreate/updateは通知できる一方、bootstrap/backfillは通知しない契約へ修正した。drift時は停止し、既存公開物を削除せず、同一入力はno-opとして扱う。
- 変更ファイル: `.github/workflows/accept-source.yml`、`.github/workflows/bootstrap.yml`、`.github/workflows/notify-publication.yml`、`docs/SANDBOX_PAGES_OPERATIONS.md`、`scripts/publish/apply_engine.py`、`scripts/publish/bootstrap_engine.py`、`scripts/publish/slack_notification.py`、テスト、本作業記録一式。
- 検証結果: 実Workflow run `34038486385`でsandbox_pagesの16件をPagesへ反映し、Pages deployと16件通知が成功した。通知方針を修正したPR #125（merge commit `7bd516728838b409095fefea3f3d90f92353806a`）をCI合格後にマージし、run `34039530498`で`work_record_087`だけを通常公開した。apply commit `2c08427301df2e77bcce5cf75ea190ea7406ce1b`、provenanceの`notify=true`、Pages HTTP 200、単体Slack通知job成功を確認した。
- ブランチ: `codex/093-single-record-notify`
- commit: `5c67061`（PR #125でmainへマージ済み）
- PR: [#125](https://github.com/tj-999-comp/sandbox-pages/pull/125)（マージ済み）
- 未解決事項: 既送信された15件の通知は撤回できない。今後のbootstrap/backfillでは通知しない。
- 次アクション: #94の全体受入へ進む。

## GitHub Issue状況

確認日時（JST）: 2026-09-06 23:35:35
取得範囲: `tj-999-comp/sandbox-pages` のOpen Issue全件（Pull Request除外、取得件数7・一覧行数7）

### 親子関係

```text
#89
├── #90
├── #91
├── #92
└── #94

#93は#89のsub-issueだがクローズ済みで、Open Issue一覧から除外。
#118・#120は#89のsub-issuesではない
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P2 | [#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open（state reason: null） | 親Issue。#90〜#94の完了後に全体完了を判定する。 |
| 2 | P2 | [#90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open（state reason: null） | #89の子。対応表を#93へ引き継ぐ。 |
| 3 | P2 | [#91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open（state reason: null） | #89の子。コミット`4079439`はmain反映済み。 |
| 4 | P1 | [#92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open（state reason: null） | #89の子。PR #119はmerge済み。 |
| 5 | P0 | [#94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open（state reason: null） | #89の子。#90〜#93完了後に全体受入を行う。 |
| 6 | 未設定 | [#118 自分専用のスポーツ内容確認サイト用リポジトリを作成する](https://github.com/tj-999-comp/sandbox-pages/issues/118) | Open（state reason: null） | #89のsub-issueではない。別project準備の課題。 |
| 7 | 未設定 | [#120 [受入] スポーツサイト生成元リポジトリを公開側へ登録する](https://github.com/tj-999-comp/sandbox-pages/issues/120) | Open（state reason: null） | #89のsub-issueではない。別project受入の課題。 |

# sandbox_pages 公開運用引き継ぎ

更新日: 2026-09-07

対象: `tj-999-comp/sandbox-pages` の `sandbox_pages` project

この文書は、本番運用として手動で承認した作業記録を、固定commit・対象basenameでPagesへ公開し、反映されたcreate/updateを漏れなくSlackへ通知するための運用手順である。公開リポジトリの受入・配信契約は [`projects/README.md`](../projects/README.md)、Actionsの権限境界は [`docs/ACTIONS_MAIN_POLICY.md`](ACTIONS_MAIN_POLICY.md)を正本とする。

## 責任境界

| 担当 | 責任 |
| --- | --- |
| 生成元の作業者 | `work_record_###.md`、同名HTML、metadataを同一のsource commitへ用意する。metadataの`publish: true`は公開要求であり、公開承認そのものではない。 |
| 承認者 | 内容、metadata、対象basename、完全なsource SHA、公開範囲、acceptance結果、最新provenanceを確認し、手動dispatchを承認する。 |
| `sandbox-pages` Actions | registryから許可範囲を再導出し、固定SHAを受入、検証済み差分だけを`main`へcommitし、そのcommitだけをPagesへdeployする。生成元の任意script・Actionは実行しない。 |
| 運用担当 | dispatchの入力を記録し、各job、公開URL、provenance、Slack結果を確認する。停止・rollback・再通知を実行する。 |
| Slack管理者 | `SLACK_WEBHOOK_URL`をSecretとして管理する。Webhook URLやtokenをIssue、PR、作業記録、ログへ記録しない。 |

現在の本番公開入口は `.github/workflows/accept-source.yml` の手動承認 `workflow_dispatch` だけである。push、schedule、repository_dispatchによる恒久自動公開は設定しない。

## 1. 公開前の承認チェック

次の全項目を確認できない場合はdispatchしない。

1. 対象は1件のbasenameだけで、`work_record_###.md`、同名HTML、`metadata/work_record_###.yml`がsource commit内で対応している。
2. metadataはschema、title、date、project_id、tags、`publish: true`を満たしている。`publish: true`は公開要求として扱い、承認者が内容を確認する。
3. source SHAは短縮形でない40桁の小文字SHAで、registryの`refs/heads/main`の祖先である。
4. registryの`project_id`、source repository、source directory、metadata directory、destination directory、HTML方式を確認する。
5. 前回provenanceの対象basename、digest、公開先との差分を確認する。既存recordの変更は`operation=update`となり、初回createとは別扱いである。
6. `acceptance.json`の`project_id`、`source.commit_sha`、`target_basename`がdispatch入力と一致し、metadata・HTML安全性・inventory・provenance検査が成功している。
7. apply結果の`operation`、`no_op`、`commit_sha`、`publication_id`、`notify`を記録できる状態にする。

`sandbox_pages`の現在の登録値は次のとおりである。

| 項目 | 値 |
| --- | --- |
| `project_id` | `sandbox_pages` |
| source | `tj-999-comp/sandbox-pages` / `refs/heads/main` |
| source入力 | `work-records/`、metadata、同名HTML |
| 公開先 | `projects/sandbox_pages/` |
| HTML方式 | `source_html` / `b-stats-work-record-v1` |
| 公開要求 | `project_id`、完全な`source_commit_sha`、単一`target_basename` |
| 上限 | 300ファイル、単体1 MiB、合計10 MiB |

## 2. 通常公開と確認

GitHub Actionsの `Source acceptance and publish` を `main` から手動dispatchし、次の3入力だけを渡す。

```text
project_id: sandbox_pages
source_commit_sha: <承認済み40桁SHA>
target_basename: work_record_###
```

確認順序は `dry-run` → `apply` → 固定apply commitのPages deploy → 条件付きSlack通知である。確認する証跡は次のとおり。

- `dry-run`: 固定source checkout、隔離、credentials残留なし、inventory、metadata・HTML安全性、provenance検査。
- `apply`: `main`のcommit SHA、変更path、`operation`、`no_op`、`publication_id`、`notify`。
- `deploy`: `apply`が返した完全なcommit SHAだけをdeployしていること。`no_op=true`ならcommit・deployしない。
- `provenance`: `provenance/sandbox_pages/<publication_id>.json`のsource SHA、対象basename、digest、operation、notify。
- Pages: manifestの`public_url`をPages originと結合した対象record URLがHTTP 200〜399であること。
- Slack: 通常の単一record公開で`operation=create`または`update`、`no_op=false`、`notify=true`、Pages成功の全条件を満たす場合、タイトル、project、basename、同じ`publication_id`、対象record URLが届くこと。bootstrap/backfillは履歴をまとめて反映するため通知しない。

### #86のE2E証跡レビュー

Issue #86の実E2Eは重大な未解決事項なしと判定した。

- run `33405631634`: source SHA `a407281afb01e54281fa26a7eda89b5b681380b1`、`work_record_074`、`operation=create`、`no_op=false`、`notify=true`。apply commit `6c3c9a7c25f0bc4809329fee92c2dd9d01a21158`、publication ID `accept-33405631634-1-sandbox_pages-work_record_074`。PagesとSlack通知に成功。
- run `33405868613`: 同じ要求の再実行で`operation=update`、`no_op=true`、`notify=false`。commit、deploy、通知は発生しなかった。
- run `33406726036`: 最終source SHA `719a1806492244942c77738d5336865ac8b1c96d`との同期で、`operation=update`、`no_op=false`、`notify=false`。apply commit `597ed80e9609f476a1c13a734aabc39e72251945`、Pages deployに成功。公開URLを1280px幅と320px幅で確認し、HTTP 200、横overflowなし、console/page errorなし。

### #94 全体受入スナップショット（2026-09-07）

生成元の`main`固定SHA、source record件数、公開側の最新provenanceを照合した。公開対象・公開済み・未公開候補・非公開の対応は次のとおりで、合計170件 = 公開142件 + 未公開候補13件 + 非公開15件となる。

| project_id | source SHA | source record | 公開済み | 未公開候補 | 非公開 | 最新公開側provenance |
|---|---|---:|---:|---:|---:|---|
| `B_Stats_Site` | `14468e72a58a00be29e18d132eda05ba0c1f01d7` | 31 | 18 | 13 | 0 | `update-20260907-record-links-B_Stats_Site`（作業ブランチ） |
| `tech_article_nortification` | `c026267696feb6802f83807b76eb499a89e57037` | 17 | 2 | 0 | 15 | `update-20260907-record-links-tech_article_nortification`（作業ブランチ） |
| `NBA_Draft_DB` | `3604ed8680ad02f7e3310ac0b2a1f1f259df7058` | 1 | 1 | 0 | 0 | `update-20260907-record-links-NBA_Draft_DB`（作業ブランチ） |
| `query_learning_BB` | `77eca4f0b1889a41958d7b75d79ef2f6ecbb9aec` | 34 | 34 | 0 | 0 | `update-20260907-record-links-query_learning_BB`（作業ブランチ） |
| `sandbox_pages` | `306d83809be1ea383c7154a56132f16f277bff16` | 87 | 87 | 0 | 0 | `accept-34039818274-1-sandbox_pages-work_record_087` |

リンク巡回では、global index、5つのproject index、公開record 142件を対象に、HTTP status、project境界、record basename、孤立record、横overflowを確認した。現行Pagesで`a_rendered` record本文の`work_record_###.md`リンクが404になる問題を検出したため、rendererで公開HTMLへの正規化、a_rendered footerの非公開Markdownリンク除去、既存55件の公開HTMLとprovenance更新を作業ブランチへ反映した。修正後のローカルPagesは156ページを1280pxで巡回し、404・console/page error・横overflow・誤projectリンクなし。global/project indexと代表recordは1280px・320px、Tab移動とfocus-visibleを確認済み。mainのPagesへ反映するにはPRのmerge後にdeploy結果を再確認する。

bootstrap/backfillの再実行は、古いsource SHAを指定したrun `34040802753`が「previous accepted source commitより古い」として停止した後、最新受入SHA `1147b36c980e192af90cac93d7854905103f9978`でrun `34040858354`を再実行した。dry-run/applyは成功し、`no_op=true`、remote main SHAは`306d83809be1ea383c7154a56132f16f277bff16`のまま、deploy jobはskip、通知jobは存在せず、重複Slack通知なしを確認した。

## 3. 緊急停止

停止は「新規公開を止める」操作であり、公開済みファイルを自動削除する操作ではない。

1. 実行中の `accept-source.yml` をActions画面で停止する。共有concurrencyにより、停止確認が済むまで新しいdispatchを開始しない。
2. 承認済みPRで `config/sources.json` の対象sourceを `enabled: false` に戻す。直接編集・force-pushはしない。
3. 既存のPagesファイル、index、provenanceを自動削除しない。`publish: false`やsource側の削除だけでも削除しない。
4. `main` SHA、最後の正常なapply commit、最新provenance、Pages代表URLを照合する。
5. 取り下げが必要な場合だけ、`.github/workflows/withdraw.yml`を`dry-run`で実行し、対象basename、現在のmain SHA、最新publication ID、digest drift、削除対象を確認する。
6. 承認者が同じSHA・publication IDを指定し、`WITHDRAW`を入力した別dispatchでapplyする。withdrawはSlack通知を行わない。

## 4. rollbackと再開

取り下げ後の復元は、取り下げcommitを人間レビュー付きPRでrevertする。revert後は、復元されたindex・provenance・代表URLを確認し、既知の正常commit SHAを指定してPagesを再deployする。manifestを手編集したり、古いsource SHAを直接再利用したりしない。

再開時は次の順で進める。

1. validator、固定SHAの祖先関係、source inventory、digest drift、Pages URLを再確認する。
2. `enabled: true`への変更をPRでレビューする。
3. `accept-source.yml`を1件・1basenameでdry-runし、`acceptance.json`とprovenanceを確認する。
4. apply、固定SHA deploy、通知条件を確認する。失敗したjobの後続だけを、同じ対象と根拠で再実行する。

## 5. Slack通知失敗時の再通知

Pages deployが成功し、Slackの送信jobだけが失敗した場合、Pagesをrollbackしない。通常の `accept-source.yml` を再実行してはならない。再実行するとapplyが新しいrun由来の `publication_id` を生成し、Pages・provenanceの再処理を誘発するためである。

送信stepまで失敗したことを確認したうえで、`Retry publication notification` を手動dispatchする。`target_basenames`には単一recordまたはカンマ区切りの複数recordを指定する。

```text
project_id: sandbox_pages
target_basenames: work_record_###
publication_id: <失敗したcreateのpublication_id>
commit_sha: <そのprovenanceを含むapply commitの40桁SHA>
```

このworkflowは次だけを行う。

- 指定commitをcheckoutし、`HEAD`と入力SHAが一致することを確認する。
- 同じpublication IDのmanifestが`operation=create`または`update`かつ`notify=true`であること、指定basenameがmanifest内で一意であることを確認する。
- manifestの相対URLを固定Pages originへ結合し、公開URLを再確認する。
- `SLACK_WEBHOOK_URL`を送信stepだけへ渡し、指定対象ごとに同じpublication IDで1回送信する。

この経路にはPages write、id-token、contents writeがなく、公開ファイル・index・provenanceを変更しない。Webhookは通知済み判定を持たないため、送信結果が不明なtimeoutではSlackを目視確認してから再送し、既に届いていれば再送しない。成功済みjobの再実行は通知重複になるため行わない。

## 6. 通知対象の契約

通常の単一record公開で公開反映を伴うcreate/updateは、明示的に`notify=false`とした場合を除き通知する。bootstrap/backfillは既存recordをまとめて反映するため通知しない。作業記録を通知したい場合は、bootstrap完了後に対象の作業記録1件だけを通常の単一record公開として`notify=true`で実行する。

| apply状態 | commit / Pages | Slack |
| --- | --- | --- |
| `create`または`update`、`no_op=false`、`notify=true` | 実行 | 通知する |
| `update`、`notify=false` | 必要に応じて実行 | 通知しない |
| `no_op=true` | 実行しない | 通知しない |
| withdraw | 取り下げcommit後にdeploy | 通知しない |
| bootstrap / backfill | 反映後に対象recordを検証 | 通知しない |

`publish: false`、source側の削除、metadata変更だけを理由に公開済みHTMLやMarkdownを自動削除しない。削除はwithdraw workflowのpreviewと明示承認を経る。

## 7. 恒久自動公開への切り替え条件

push、schedule、repository_dispatchなどの恒久自動公開へ切り替える場合は、#87の範囲外として別Issueを作成し、次を明示承認するまで変更しない。

- trigger、対象branch、対象source、対象basenameの決定方法
- PR承認、ruleset、Actions bypass、権限とSecretの境界
- no-op、withdraw、明示的に抑制したbootstrapの通知抑制
- 競合、rollback、再通知、監査証跡、障害時の停止責任
- 少なくとも新規record 1件の実E2Eと再実行結果

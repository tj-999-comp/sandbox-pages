# sandbox_pages 公開運用引き継ぎ

更新日: 2026-09-01

対象: `tj-999-comp/sandbox-pages` の `sandbox_pages` project

この文書は、本番運用として手動で承認した作業記録1件を、固定commit・単一basenameでPagesへ公開し、必要な場合だけSlackへ通知するための運用手順である。公開リポジトリの受入・配信契約は [`projects/README.md`](../projects/README.md)、Actionsの権限境界は [`docs/ACTIONS_MAIN_POLICY.md`](ACTIONS_MAIN_POLICY.md)を正本とする。

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
| 上限 | 256ファイル、単体1 MiB、合計10 MiB |

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
- Slack: `operation=create`、`no_op=false`、`notify=true`、Pages成功の全条件を満たす場合だけ、タイトル、project、basename、同じ`publication_id`、対象record URLが届くこと。

### #86のE2E証跡レビュー

Issue #86の実E2Eは重大な未解決事項なしと判定した。

- run `33405631634`: source SHA `a407281afb01e54281fa26a7eda89b5b681380b1`、`work_record_074`、`operation=create`、`no_op=false`、`notify=true`。apply commit `6c3c9a7c25f0bc4809329fee92c2dd9d01a21158`、publication ID `accept-33405631634-1-sandbox_pages-work_record_074`。PagesとSlack通知に成功。
- run `33405868613`: 同じ要求の再実行で`operation=update`、`no_op=true`、`notify=false`。commit、deploy、通知は発生しなかった。
- run `33406726036`: 最終source SHA `719a1806492244942c77738d5336865ac8b1c96d`との同期で、`operation=update`、`no_op=false`、`notify=false`。apply commit `597ed80e9609f476a1c13a734aabc39e72251945`、Pages deployに成功。公開URLを1280px幅と320px幅で確認し、HTTP 200、横overflowなし、console/page errorなし。

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

送信stepまで失敗したことを確認したうえで、`Retry publication notification` を手動dispatchする。

```text
project_id: sandbox_pages
target_basename: work_record_###
publication_id: <失敗したcreateのpublication_id>
commit_sha: <そのprovenanceを含むapply commitの40桁SHA>
```

このworkflowは次だけを行う。

- 指定commitをcheckoutし、`HEAD`と入力SHAが一致することを確認する。
- 同じpublication IDのmanifestが`operation=create`かつ`notify=true`であること、basenameが一意であることを確認する。
- manifestの相対URLを固定Pages originへ結合し、公開URLを再確認する。
- `SLACK_WEBHOOK_URL`を送信stepだけへ渡し、同じpublication IDで1回送信する。

この経路にはPages write、id-token、contents writeがなく、公開ファイル・index・provenanceを変更しない。Webhookは通知済み判定を持たないため、送信結果が不明なtimeoutではSlackを目視確認してから再送し、既に届いていれば再送しない。成功済みjobの再実行は通知重複になるため行わない。

## 6. 通知対象外の契約

通知対象は新規createだけである。

| apply状態 | commit / Pages | Slack |
| --- | --- | --- |
| `create`、`no_op=false`、`notify=true` | 実行 | 通知する |
| `update` | 必要に応じて実行 | 通知しない |
| `no_op=true` | 実行しない | 通知しない |
| withdraw | 取り下げcommit後にdeploy | 通知しない |
| bootstrap / backfill | 反映しても通知抑制 | 通知しない |

`publish: false`、source側の削除、metadata変更だけを理由に公開済みHTMLやMarkdownを自動削除しない。削除はwithdraw workflowのpreviewと明示承認を経る。

## 7. 恒久自動公開への切り替え条件

push、schedule、repository_dispatchなどの恒久自動公開へ切り替える場合は、#87の範囲外として別Issueを作成し、次を明示承認するまで変更しない。

- trigger、対象branch、対象source、対象basenameの決定方法
- PR承認、ruleset、Actions bypass、権限とSecretの境界
- update、no-op、withdraw、bootstrapの通知抑制
- 競合、rollback、再通知、監査証跡、障害時の停止責任
- 少なくとも新規record 1件の実E2Eと再実行結果

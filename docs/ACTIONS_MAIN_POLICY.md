# Actions botのmain反映方針

決定日: 2026-08-20
対象: `tj-999-comp/sandbox-pages` GitHub Issue #14

## 結論

公開リポジトリが所有する受入workflowは、検証済みの公開成果物に差分がある場合だけ、`GITHUB_TOKEN`の`contents: write`を使って`main`へ通常commitする。生成元リポジトリ、人間、PATへ`main`の直接push権限を渡さない。

人間によるソース、設定、workflow、文書の変更はPR経由とする。Actions botの直接commitは、受入workflowが生成した公開成果物、project/global index、provenance manifestに限定し、同一commitで反映する。

PR方式を標準採用しない理由は、検証・commit・固定commit SHAのPages deployを同一workflow runで完結させ、no-op時の不要なPRと人手の待機を発生させないためである。

## main branch ruleset

2026-08-20のGitHub API確認では、repository rulesetは未設定だった。workflowを`main`へ反映した後、次のbranch rulesetをActiveで設定してから自動受入を有効化する。

- ruleset名: `protect-main`
- 対象: default branch
- 人間の変更: PR必須、必須validation成功、未解決review threadなし
- 履歴: force push禁止、branch削除禁止、履歴書き換え禁止
- bypass: `GitHub Actions` GitHub AppだけをAlways allowで登録
- repository admin、write/maintain role、個人user、生成元用PATはbypassへ登録しない

rulesetのbypassはactor単位でありworkflow単位ではない。そのため、repositoryのActions既定権限をread-onlyに保ち、write権限はA所有の受入workflowのapply jobへ明示する。GitHub Actions Appをbypassへ登録できない場合は、直接commitを有効化せずPR方式へ切り替える。

## job別permissions

| job | permissions | Secret | 禁止事項 |
| --- | --- | --- | --- |
| validation | `contents: read` | なし | 生成元へwrite権限を渡さない |
| apply | `contents: write` | なし | 生成元のscript、Action、任意commandを実行しない |
| deploy | `contents: read`, `pages: write`, `id-token: write` | なし | 固定SHA以外をdeployしない |
| notification | `contents: read` | `SLACK_WEBHOOK_URL`のみ | deploy成功前に通知しない |

Slack通知jobの実装契約:

- `.github/workflows/accept-source.yml`の`notify` jobは、`apply`とPages `deploy`の成功後、`operation=create`、`no_op=false`、provenanceの`notify=true`を満たす場合だけ実行する。
- `notify` jobはapply済みの固定commitをRepository Aからcheckoutしてから`slack_notification`を実行し、workflow実行環境に依存せず通知用スクリプトをimportできる状態を作る。
- `SLACK_WEBHOOK_URL`は通知jobの送信stepの環境変数へだけ渡し、validation、apply、deployのjobへ渡さない。
- 固定commitのprovenance manifestから対象recordのタイトルと`public_url`を解決し、Pages deployのoriginと結合したrecord URLを5回まで確認してから、タイトル、`publication_id`、project、basename、対象作業記録URLをIncoming Webhookへ送る。Pages環境のサイトトップURL自体は通知URLに使わない。
- 通知jobだけが失敗してもPages公開は巻き戻さない。通常の受入workflowは再実行せず、`.github/workflows/notify-publication.yml`へapply commit、既存`publication_id`、project、basenameを渡し、同じprovenanceを検証して通知だけを再実行する。詳細は[`docs/SANDBOX_PAGES_OPERATIONS.md`](SANDBOX_PAGES_OPERATIONS.md)を参照する。

workflow全体のdefault permissionsは空またはread-onlyとし、必要なjobだけへ明示的に付与する。

## 同一repository sourceの隔離

`source_repository`がRepository A（`tj-999-comp/sandbox-pages`）自身である場合も、受入対象は必ず固定`source_commit_sha`の別checkoutから読み取る。Repository Aのworktreeをsource checkoutとして再利用してはならず、apply開始前にsource checkoutがAのworktreeと重ならないことを検証する。

- dispatch入力は`project_id`、`source_commit_sha`、`target_basename`の3値だけに限定する。
- source checkoutは`persist-credentials: false`で取得し、local git configにcredentialまたはHTTP extraheaderが残っていないことを確認する。
- fixed SHAが登録branchの祖先であること、source inventoryのdigest、metadata・Markdown・HTMLのbasename対応をA側で再検証する。
- applyが変更できるのは検証済みの`projects/<project_id>/`、project/global index、`provenance/<project_id>/`だけとし、`work-records/`を直接編集・削除しない。
- source checkout後のファイル変更、SHA・basename・許可pathの不一致は、書き込み前に失敗させる。

## apply可能な差分

- `projects/<project_id>/`の検証済み公開ファイル
- `projects/index.html`とproject単位の`index.html`
- A所有のindex用stylesheet
- `provenance/<project_id>/`のmanifest

## 監査可能な公開取り下げ

`publish: false`や生成元からのファイル削除を契機にした自動削除は行わない。A管理者が`.github/workflows/withdraw.yml`を`dry-run`で実行し、対象basename、現在の`main` SHA、最新`publication_id`、明示的な削除対象を確認する。applyは別dispatchで同じSHAとpublication_idを再指定し、`WITHDRAW`確認文字列を要求する。

取り下げengineは登録済みprojectの最新manifestに対象basenameが存在すること、公開ファイルのdigest driftがないこと、生成済みindexが最新であることをapply前に検証する。削除は対象basenameのHTMLとMarkdownに限定し、project/global indexとwithdraw操作を記録する新しいprovenance manifestを同じcommitへ反映する。sourceの消失、対象外ファイル、symlink、index drift、mainの更新があれば失敗し、Slack通知は行わない。

取り下げ後のURLは404となる。復元は取り下げcommitをrevertする人間レビュー付きPRで行い、既知の固定SHAを指定してPagesを再deployする。revertで取り下げmanifestを消去・改変せず、復元前後のmanifest、index、代表URLを確認する。

workflow、repository設定、source registry、運用文書、他projectは自動変更しない。許可範囲外の差分、manifest drift、自動削除、自動改名、symlink、force push、`rsync --delete`を拒否する。

## 競合、retry、no-op

- 受入とPages deployは`cancel-in-progress: false`で直列化する。push・手動dispatchのPages workflowは`pages-production-main`を使い、受入workflowのcallerがこの共有groupを保持する。reusable Pages workflow自身にはworkflow-level concurrencyを置かず、callerが同じgroupを保持したままcalled workflowのjob生成を待つ競合を避ける。受入workflowのdeploy callerには`if`を置き、applyの`no_op=true`時はreusable workflow自体を呼ばずにno-opとする。新規publication時だけ完全なcommit SHAをrequiredな`workflow_call.commit_sha`へ渡し、called workflowはbuild/deployを実行する。これによりno-op時の空SHA入力と、called workflow内の全job skipによる親run failureを避ける。
- push直前にremote `main`を再取得し、検証開始時のSHAと一致しなければ自projectの変更だけを再適用する。
- 再適用は1回だけとし、再競合、他projectの変更、manifest driftを検出した場合はcommit・deployせず失敗する。
- 差分0件は成功扱いとし、commit、deploy、Slack通知を行わない。
- commit後のSHAをworkflow outputへ固定し、deploy直前にremote `main`と再照合する。SHAが一致しなければ古いartifactをdeployしない。

## 緊急停止と復旧

1. 実行中の受入workflowを手動停止し、新規実行を無効化する。
2. `config/sources.json`の対象sourceを`enabled: false`へ戻す。
3. 必要に応じて生成元のdispatch tokenを失効する。
4. 公開中ファイルを自動削除せず、最後の正常commitとprovenance manifestを照合する。
5. rollbackが必要な場合は、人間レビュー付きPRで対象commitをrevertし、既知の正常SHAを明示してPagesを再deployする。
6. validator、drift、Pages、代表URLを再確認してから手動受入を再開する。

通常運用開始前に、ruleset設定画面またはAPI結果、workflow run URL、固定SHA、rollback確認結果を作業記録へ残す。

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
- `SLACK_WEBHOOK_URL`は通知jobの送信stepの環境変数へだけ渡し、validation、apply、deployのjobへ渡さない。
- deploy jobから受け取った公開URLを5回まで確認し、公開可能になってから`publication_id`、project、basename、公開URLをIncoming Webhookへ送る。
- 通知jobだけが失敗してもPages公開は巻き戻さない。workflow runを同じ`publication_id`の通知jobとして再実行できるよう、apply結果とprovenanceで識別する。

workflow全体のdefault permissionsは空またはread-onlyとし、必要なjobだけへ明示的に付与する。

## apply可能な差分

- `projects/<project_id>/`の検証済み公開ファイル
- `projects/index.html`とproject単位の`index.html`
- A所有のindex用stylesheet
- `provenance/<project_id>/`のmanifest

workflow、repository設定、source registry、運用文書、他projectは自動変更しない。許可範囲外の差分、manifest drift、自動削除、自動改名、symlink、force push、`rsync --delete`を拒否する。

## 競合、retry、no-op

- 受入とPages deployは共通concurrency groupを使い、`cancel-in-progress: false`で直列化する。受入workflowからreusable Pages workflowを呼ぶjobには`if`を置かず、no-op判定は`should_deploy`文字列入力（`'true'`または`'false'`）を通じてcalled workflow内部で行う。no-op時はapplyのcommit SHAが空になるため、`workflow_call.commit_sha`は任意入力とし、create時のbuild側で完全SHAを検証する。no-op時もcalled workflowに成功する完了jobを置き、親の受入runをfailureにしない。
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

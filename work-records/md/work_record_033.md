# 作業記録 033: Issue #19 受入workflowへのcommit・固定SHA deploy接続
作成日: 2026-08-20

## 概要

- 課題: GitHub Issue #19「[Actions] 受入workflowへcommit・固定SHA deployを接続する」。
- 目的: #17の固定SHA受入結果を#18のapply engineへ渡し、許可範囲だけを`main`へcommitした後、commit SHAを固定してGitHub Pagesへdeployする。
- 完了条件: 検証jobとapply jobを分離し、`contents: write`をapply jobだけへ付与する。差分0件はcommit・deployせず、main競合は1回だけ再checkout・再applyし、commit後の固定SHAをPages workflowへ渡す。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: #18の`apply_engine.py`、#17の`accept-source.yml`、`deploy-pages.yml`、`projects/README.md`、`docs/ACTIONS_MAIN_POLICY.md`。
- 実施内容: `accept-source.yml`を検証・apply・deployのjob構成へ拡張した。検証済みartifactと固定source SHAをapply jobへ引き渡し、補助checkoutをRepository Aのworktree外へ移動してclean worktree契約を維持した。`enabled:false`の場合は検証のみで終了し、明示的な`--allow-enabled`を通った有効sourceだけがapplyへ進む。apply後は許可されたproject、index、provenanceだけをstageして通常commitし、push競合時は1回だけ最新`main`へ再適用する。commit SHAを`deploy-pages.yml`のreusable workflowへ渡す。
- 成果物: `.github/workflows/accept-source.yml`、`scripts/publish/apply_engine.py`、`scripts/publish/read_only_acceptance.py`、関連テスト。
- 検証結果: 64件のunit test、Python構文確認、workflow YAML parse、`git diff --check`に合格した。
- 未解決事項: GitHub Actions上の実dispatch、生成元Bの固定SHA取得、commit・Pages deployの実行は未確認。現行registryは`enabled:false`のため、workflow実行時も検証結果をartifactへ保存してapplyを行わない。
- 次工程への引き継ぎ: #21でdisabled sourceのdry-run、#22でsource有効化後、#23で受入・Pages・公開URL・Slackの一連を実環境で確認する。

### Portfolio Reviewer

- 入力: #19のcommit・固定SHA deploy要件、変更workflow、apply engineのclean worktree・許可範囲・retry契約、unit test結果。
- 実施内容: job単位の権限、固定SHA checkout、artifact境界、disabled sourceのno-op、許可pathだけのstage、push競合のbounded retry、reusable Pages workflowへのSHA受け渡し、no-op時のdeploy skipを確認した。
- 成果物: commit前の差分レビュー。
- 検証結果: 重大な未解決事項は確認されなかった。GitHub Actions実行と外部レビューは未確認として残した。
- 未解決事項: PR、CI、GitHub Actions実行結果はまだ存在せず、外部確認できていない。
- 次工程への引き継ぎ: GitHub接続復旧後にworkflow dispatch、実commit SHA、Pages run、PR差分とCIを確認する。

## 主要な判断

- 判断: `enabled:false`のsourceは同じworkflowで受入検証だけを完了し、apply jobはno-op終了する。
- 理由: #17・#21の段階導入と、#22の手動有効化を分離し、無効sourceからの公開を防ぐため。
- 判断: operationはworkflow入力へ追加せず、直前provenanceのrecord存在から`create`または`update`をA側で推定する。
- 理由: 公開要求の入力を`project_id`、固定source SHA、対象basenameの3項目に保ち、source側から公開先の操作種別を指定させないため。
- 判断: apply準備でmainが進んだ場合の再試行を1回に限定する。
- 理由: 他projectの通常commitを上書きせず、解消できない競合ではcommit・deployを停止するため。

## 最終結果

- 解決したこと: #17のread-only受入結果を#18のapply engineへ接続し、許可範囲限定のcommit、固定SHA Pages deploy、no-op skip、disabled source guard、1回限定のpush retryをworkflowへ追加した。enabled sourceへ切り替える場合も、`--allow-enabled`を明示したworkflow経路だけが進める構成にした。
- 変更ファイル: `.github/workflows/accept-source.yml`、`scripts/publish/apply_engine.py`、`scripts/publish/read_only_acceptance.py`、`tests/test_apply_engine.py`、`tests/test_pages_workflow.py`、`tests/test_read_only_acceptance.py`、本作業記録のMarkdownと対応HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（64件合格）、`PYTHONPYCACHEPREFIX=/tmp/sandbox-pages-pycache python3 -m py_compile ...`（合格）、Ruby YAML parse（合格）、`git diff --check`（合格）。新規HTMLはPlaywrightで確認を試みたが、ChromiumがmacOS Machポート権限エラーで起動せず、実ブラウザ確認は未完了。
- 作業ブランチ: `codex/033-issue-19-actions`
- コミット: commit前のため未確定
- PR: 未作成
- PRレビュー・CI: GitHub API認証障害のため未確認
- 未解決事項: GitHub Actions実環境での外部source checkout、apply commit、固定SHA Pages deploy、ruleset・branch保護、PRレビュー、CIは未確認。Chromium起動環境復旧後にwork_record_033.htmlのPC・320px幅確認も必要。
- 次アクション: GitHub接続復旧後に#19のworkflowを手動dispatchし、現行`enabled:false`ではno-opになることを確認する。#22で有効化した後、テスト用新規recordでcommit・Pages・公開URLを実行する。

## GitHub Issue状況

確認日時（JST）: 2026-08-20 18:17
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue（#13、#18〜#24）と親Epic #5をGitHub connectorで取得した時点のsnapshot。

### 親子関係

```text
#5が親Epic（closed / completed）。#13、#18〜#24はIssue本文の`Parent: #5`で確認した。
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P1 | [#18 [Publish] 許可範囲限定の同期apply engineを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/18) | Open | #19の前工程。完了後に本作業へ着手 |
| 2 | P1 | [#19 [Actions] 受入workflowへcommit・固定SHA deployを接続する](https://github.com/tj-999-comp/sandbox-pages/issues/19) | Open | 本作業の対象。#14、#15、#18に依存 |
| 3 | P1 | [#20 [Notification] deploy成功後のSlack通知jobを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/20) | Open | #19完了後の通知工程 |
| 4 | P1 | [#21 [E2E] disabled sourceでBの受入dry-runを実行する](https://github.com/tj-999-comp/sandbox-pages/issues/21) | Open | #19実装後、現行`enabled:false`経路を実行 |
| 5 | P1 | [#22 [Activation] B sourceを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/22) | Open | #19・#21完了後の限定有効化 |
| 6 | P1 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open | #20とB側準備後のE2E工程 |
| 7 | P2 | [#13 [Renderer] a_rendered用の決定的rendererを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/13) | Open | 初回B公開のcritical path外 |
| 8 | P2 | [#24 [Operations] 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | Open | #16、#18、#19後の運用工程 |

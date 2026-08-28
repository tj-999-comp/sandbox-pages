# 作業記録 059: Issue #60 固定commit・basename限定の受入境界を強化
作成日: 2026-08-28

## 概要

- 課題: GitHub Issue #60「tech_article_nortificationの固定commit・basename限定公開要求を受け入れる」。
- 目的: `tech_article_nortification` からの公開要求を、A側source registryで定めた生成元からの固定commitと単一basenameだけに限定し、検証済み入力だけを既存のapply・Pages処理へ渡せる状態にする。
- 完了条件: dispatch入力が3項目に限定され、固定SHA・basename・registry・metadata・publish条件が検証され、artifact改変や不正入力で公開処理が進まないこと。正常系・異常系のテストとブラウザ確認が成功すること。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: Issue #60、既存の`.github/workflows/accept-source.yml`、`read_only_acceptance.py`、`apply_engine.py`、`config/sources.json`、既存のprovenance・index生成契約。
- 実施内容: apply jobへdispatchの`project_id`・`source_commit_sha`・`target_basename`と受入artifactの値を照合するstepを追加した。apply側でも40桁小文字SHAと`work_record_001`〜`work_record_999`を再検証するようにした。`tech_article_nortification`のremote main固定SHAを空の初期provenanceとして登録し、空のproject indexを生成した。
- 成果物: 受入workflow、apply境界検証、初期provenance、tech project index、正常系・異常系テスト。
- 検証結果: 全93件のPythonユニットテスト、index・作業記録・filename検証、Python AST構文、JSON構文、`git diff --check`に合格した。
- 未解決事項: `publish: false`の生成元を実際に公開する手動E2E、Pages公開URL、Slack通知は安全のため実施していない。
- 次工程への引き継ぎ: 生成元側で公開対象metadataを人間確認付きで`publish: true`にした固定commitを作成後、3入力だけで受入workflowを手動dispatchする。

### Portfolio Reviewer

- 入力: Issue #60の完了条件、workflow・apply engine・provenance・indexの差分、全テスト結果、ブラウザ確認結果。
- 実施内容: 3入力以外のdispatch契約が追加されていないこと、artifactがdispatch入力へ束縛されること、source repository/ref/directoryがregistry由来であること、source checkoutをRepository Aのworktree外へ移動していることを確認した。不正SHA・basename、`publish: false`、未登録projectを拒否する既存境界と、Pages deploy・通知の後段接続も確認した。
- 成果物: Issue #60事前レビュー結果。
- 検証結果: 重大な未解決事項なし。global/project indexをChromiumで1280px、900px、640px、320pxにて確認し、HTTP 200、横overflowなし、console/page errorなし、failed requestなし。
- 未解決事項: 実GitHub Actions手動E2Eと外部PRレビューは未実施。
- 次工程への引き継ぎ: source側のpublish承認後にdisabled状態を維持したままdry-runを実行し、その後に人間承認を得てsource registryの有効化とpublish E2Eへ進む。

## 主要な判断

- 判断: `tech_article_nortification`は初期provenanceを空の公開状態で登録し、source registryの`enabled: false`を維持する。
- 理由: 現時点の生成元metadataは`publish: false`であり、受入経路を準備しても人間確認前の実公開は許可しないため。
- 判断: artifactを信頼してapplyせず、dispatchの3入力と`acceptance.json`内のproject・commit・basenameをapply jobで再照合する。
- 理由: dry-runからapplyへの境界で対象差し替えを検出し、workflow入力と公開対象の識別子を一致させるため。

## 最終結果

- 解決したこと: 固定commit・basename限定の受入要求をworkflowとapply engineの両方で検証できるようにし、`tech_article_nortification`のdisabled dry-runを開始できるA側初期状態を追加した。
- 変更ファイル: `.github/workflows/accept-source.yml`、`scripts/publish/apply_engine.py`、`provenance/tech_article_nortification/initial.json`、`projects/index.html`、`projects/tech_article_nortification/index.html`、関連テスト、作業記録Markdownと対応HTML。
- 検証結果: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'`（93件成功）、`python3 -m scripts.publish.index_generator --check`、`python3 scripts/dev/convert_work_records_to_html.py --check`、`python3 scripts/dev/validate_work_record_filenames.py`、Python AST、JSON、`git diff --check`に合格。Chromium確認証跡はglobal indexが`/private/tmp/playwright-browser-verify/2026-08-28T05-53-35-374Z/report.json`、tech indexが`/private/tmp/playwright-browser-verify/2026-08-28T05-53-46-286Z/report.json`、本作業記録HTMLが`/private/tmp/playwright-browser-verify/2026-08-28T05-55-35-041Z/report.json`。
- 作業ブランチ: `codex/060-fixed-basename-acceptance`
- コミット: 未コミット
- PR: 未作成
- PRレビュー・CI: ローカル事前レビュー合格。push・PR作成・CI確認は未実施。
- 未解決事項: publish承認済みsource固定commitでの実GitHub Actions dry-run、apply、Pages deploy、公開URL、Slack通知、GitHub上の外部レビュー。
- 次アクション: 差分をcommitしてpushし、PR作成後にGitHub Actions `Validate`とPR差分を確認する。Issue #60はPR mergeと手動E2E完了までOpenのままにする。

## GitHub Issue状況

確認日時（JST）: 2026-08-28 14:54
取得範囲: `tj-999-comp/sandbox-pages`のOpen Issue一覧（全件）とIssue #60の詳細、Issue #60のsub-issues。

### 親子関係

```text
親子関係なし
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#60 [Actions] tech_article_nortificationの固定commit・basename限定公開要求を受け入れる](https://github.com/tj-999-comp/sandbox-pages/issues/60) | Open | 本作業の対象。source側のpublish承認済み固定commitによるdry-run・手動E2EとPR工程が未完了。 |

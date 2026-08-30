# 作業記録 061: 生成元テンプレートのGitHub App連携工程を標準化
作成日: 2026-08-30

## 概要

- 課題: 新しい生成元リポジトリを追加する際に、公開リポジトリAとのGitHub App連携と`PUBLISH_APP_PRIVATE_KEY`登録の工程が共通テンプレートへ明記されていなかった。
- 目的: 生成元ごとの導入時に、GitHub Appの利用設定、PEM形式Secretの登録、Secret名確認、旧PAT方式を使わない方針を漏れなく適用できるようにする。
- 完了条件: 共通標準と公開受入ルールへテンプレート工程を追記し、Keychainのbase64化PEMを登録する場合のデコード方法、404時の確認事項、Secret非出力方針を記録・検証する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: `docs/PORTFOLIO_STANDARD.md`、`projects/README.md`、`config/sources.json`、既存のGitHub App認証方針、`tech_article_nortification`のsource登録。
- 実施内容: 生成元READMEまたは運用テンプレートへ記載すべきGitHub App連携工程を共通標準へ追加した。`PUBLISH_APP_PRIVATE_KEY`はbase64文字列ではなくPEMとして登録し、Keychainがbase64化PEMを保持する場合だけ登録時に`base64 -D`する手順を記載した。Secret登録前の`gh repo view`、登録後のSecret名だけの確認、404時の認証・権限確認、旧`SANDBOX_PAGES_DISPATCH_TOKEN`を新規テンプレートへ追加しない方針を明記した。公開受入ルールの認証節もGitHub App前提へ更新した。
- 成果物: `docs/PORTFOLIO_STANDARD.md`、`projects/README.md`、本作業記録と対応HTML。
- 検証結果: `git diff --check`成功。GitHub CLIで対象リポジトリの存在確認とOpen Issueスナップショット取得に成功した。
- 未解決事項: 生成元リポジトリ側の実テンプレートへの反映と、実Secret値を使ったActions E2Eは今回の公開側リポジトリ変更の範囲外。
- 次工程への引き継ぎ: PRの差分・レビュー・CIを確認し、マージ後に共通標準を新規生成元の導入チェックリストとして使用する。

### Portfolio Reviewer

- 入力: 上記2文書の差分、source registry、ユーザー指定のKeychainからGitHub Secretへ登録する工程。
- 実施内容: リポジトリ名・所有者の事前確認を追加し、`gh secret set`の公開鍵取得時点ではPEM形式が未検証であること、404をSecret値の問題と誤認しないことを確認した。旧PAT方式との混在、秘密値のログ・artifact・作業記録への出力を防ぐ記載をレビューした。
- 成果物: 文書差分への事前レビュー結果。
- 検証結果: 重大な未解決事項なし。`tech_article_nortification`の綴りをsource registryと一致させた。
- 未解決事項: なし。
- 次工程への引き継ぎ: HTML生成後の表示確認、全テスト、PR上のCI確認を行う。

## 主要な判断

- 判断: Keychainの保存形式を変更することを必須にせず、base64化PEMを保持している場合はSecret登録時にデコードする手順を標準化した。
- 理由: 既存Keychain項目を変更せず、GitHub Secretへはworkflowが期待する生PEMを登録できるため。
- 判断: GitHub App連携工程を共通標準と`projects/README.md`の両方へ記載した。
- 理由: 共通テンプレートの参照先と、公開受入契約の導入チェックリストの双方から工程を確認できるようにするため。

## 最終結果

- 解決したこと: 新しい生成元リポジトリごとに、GitHub App利用設定、`PUBLISH_APP_PRIVATE_KEY`のPEM形式登録、Keychainからの安全な登録、Secret名確認、旧PAT方式の不使用を確認する工程を標準化した。
- 変更ファイル: `docs/PORTFOLIO_STANDARD.md`、`projects/README.md`、`work-records/md/work_record_061.md`、`work-records/work_record_061.html`。
- 検証結果: `python3 scripts/dev/convert_work_records_to_html.py --check`（61件 current）、`python3 scripts/dev/validate_work_record_filenames.py`、既存unit test（93件成功）、`git diff --check`に合格した。ブラウザ確認では1280px、900px、640px、320pxの全viewportでHTTP 200、横overflowなし、console/page errorなし、failed requestなしを確認した。証跡は`/private/tmp/playwright-browser-verify/2026-08-30T04-41-59-699Z/report.json`。
- 作業ブランチ: `codex/docs-github-app-source-template`
- コミット: PR作成前に確定する。
- PR: PR作成前に確定する。
- PRレビュー・CI: ローカル事前レビューとCI確認をPR工程で実施する。
- 未解決事項: 生成元側の実Secret登録と実workflow E2Eは未実施。
- 次アクション: PR作成後にGitHub上の差分とCIを確認し、問題がなければマージする。

## GitHub Issue状況

確認日時（JST）: 2026-08-30 13:41
取得範囲: `tj-999-comp/sandbox-pages`のOpen Issue全件、および今回の連携工程に関係する`tj-999-comp/tech_article_nortification`のOpen IssueをGitHub CLIで取得した時点のsnapshot。後者の#21（LLM要約）は今回のGitHub App・公開連携と無関係のため一覧から除外した。今回の文書変更に直接対応するIssueは作成していない。

### 親子関係

```text
親子関係なし
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#70 [Epic] NBA_Draft_DBの作業記録をPages公開・Slack通知まで接続する](https://github.com/tj-999-comp/sandbox-pages/issues/70) | Open | 今回の文書変更とは別の後続Epic。 |
| 2 | 未設定 | [#71 [Publish] NBA_Draft_DBをsource registryへ登録し初期状態を固定する](https://github.com/tj-999-comp/sandbox-pages/issues/71) | Open | #70のsource登録工程。 |
| 3 | 未設定 | [#72 [Actions] NBA_Draft_DBの固定commit・basename限定公開要求を受け入れる](https://github.com/tj-999-comp/sandbox-pages/issues/72) | Open | #71完了後の受入workflow工程。 |
| 4 | 未設定 | [#73 [E2E] NBA_Draft_DBのdisabled受入dry-runとno-opを検証する](https://github.com/tj-999-comp/sandbox-pages/issues/73) | Open | #72完了後のdisabled E2E工程。 |
| 5 | 未設定 | [#74 [Activation] NBA_Draft_DBを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/74) | Open | #73完了後の有効化工程。 |
| 6 | 未設定 | [#75 [E2E] NBA_Draft_DBの作業記録を公開しSlack通知まで確認する](https://github.com/tj-999-comp/sandbox-pages/issues/75) | Open | #74完了後のfull E2E工程。 |
| 7 | 未設定 | [#76 [Operations] NBA_Draft_DBの公開運用・停止手順を引き継ぐ](https://github.com/tj-999-comp/sandbox-pages/issues/76) | Open | #75完了後の運用引き継ぎ。 |
| 8 | 未設定 | [tech_article_nortification #2 Portfolio: sandbox-pages受入・work-record公開連携の残りタスク](https://github.com/tj-999-comp/tech_article_nortification/issues/2) | Open | 既存生成元の公開連携残件。今回の共通テンプレート工程を適用する対象。 |
| 9 | 未設定 | [tech_article_nortification #10 Portfolio: E2E完了後のenabled・publish運用切替と引き継ぎ](https://github.com/tj-999-comp/tech_article_nortification/issues/10) | Open | 既存生成元のfull E2E後に運用切替を判断する。 |

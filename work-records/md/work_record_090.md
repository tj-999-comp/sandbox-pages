# 作業記録 090: sport-portal公開受入の有効化と実E2E確認
作成日: 2026-09-07

## 概要

- 課題: `sport-portal`を公開側の生成元として有効化し、生成元から公開ページまでの実E2Eを完了する。
- 目的: `enabled: true`への切り替え後も、固定commit受入、Pages公開、provenance、Slack通知、再実行時のno-opが成立することを確認する。
- 完了条件: 設定変更をマージし、生成元・公開側のActionsが成功し、公開URLが到達可能で、Issue #120を完了として記録・クローズする。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: `sport-portal`の公開受入準備、公開側registry、Issue #120、PR #128。
- 実施内容: `config/sources.json`の`sport-portal`を`enabled: false`から`enabled: true`へ変更し、運用説明と受入テストの期待値を更新した。生成元Actionsに必要な`PUBLISH_APP_ID` Actions variableが未設定だったため、値を補完した。
- 成果物: PR #128、公開側mainへのマージコミット`1a5d634f24c4815e74ac76c8d01170e81ab2a6e0`、公開反映コミット`ef58d9b71b0ed2fb8bb55567e29a9f0b6d773a3a`。
- 検証結果: 公開側テスト121件、index generator、作業記録HTML、ファイル名、差分チェックが成功した。
- 未解決事項: なし。
- 次工程への引き継ぎ: `sport-portal`の通常運用では、生成元側からpublish requestを実行し、公開側の受入runとprovenanceを確認する。

### Portfolio Reviewer

- 入力: PR #128、生成元Actions run、公開側Actions run、Pages公開URL、Issue #120。
- 実施内容: 設定変更のCI、実E2Eの各job、公開反映結果、provenanceの生成元SHA・record basename・公開URL、同一入力の再実行結果を照合した。
- 成果物: Issue #120への完了コメント、Issueの完了クローズ、公開URLとActions runの確認結果。
- 検証結果: 生成元run `34103945295`、公開側run `34103958953`が成功した。公開URLはHTTP 200で、Slack通知も成功した。同一内容の再実行run `34104154093`は成功し、反映no-op、Deploy/Notifyスキップとなった。
- 未解決事項: なし。
- 次工程への引き継ぎ: 今後の生成元record追加時は、同じ受入契約とno-op挙動を継続利用する。

### Portfolio Performance & Accessibility Tester

- 入力: `sport-portal`のglobal index、project index、record page、公開受入後のPages URL。
- 実施内容: Chromiumで1280x900、900x900、640x900、320x800を確認し、HTTP応答、横overflow、console/page error、failed requestを確認した。
- 成果物: `/private/tmp/sport-portal-browser-global/report.json`、`/private/tmp/sport-portal-browser-project/report.json`、`/private/tmp/sport-portal-browser-record/report.json`。
- 検証結果: 全viewportでHTTP 200、横overflowなし、console/page errorなし、failed requestなし。公開record URLもHTTP 200で到達できた。
- 未解決事項: なし。
- 次工程への引き継ぎ: UI変更を伴う公開更新では、同じ4viewport確認を継続する。

## 主要な判断

- 判断: `enabled: true`への切り替えは、生成元mainの固定SHAを使った実E2Eが成功することを確認した後に行った。
- 理由: registryを有効化した状態で、source validation、公開側apply、Pages deploy、provenance、通知までの実運用経路を確認するため。
- 判断: 初回の生成元Actionsが`PUBLISH_APP_ID`未設定で停止したため、既存のGitHub App設定に対応するActions variableを追加して再実行した。
- 理由: 秘密情報を追加せず、workflowが要求する非秘密のApp IDだけを設定する最小対応とした。

## 最終結果

- 解決したこと:
  - `sport-portal`を公開側registryで`enabled: true`に変更し、PR #128をマージした。
  - 生成元run `34103945295`と公開側run `34103958953`で実E2Eを完了した。
  - `provenance/sport-portal/accept-34103958953-1-sport-portal-work_record_001.json`を生成し、source SHA `3dca25cfcb6d86775a99300533ec95bbd14130e5`、record basename、公開URLを固定した。
  - `https://tj-999-comp.github.io/sandbox-pages/projects/sport-portal/work_record_001.html`のHTTP 200、Slack通知成功、同一入力再実行時のno-opを確認した。
  - Issue #120へ結果をコメントし、完了理由`COMPLETED`でクローズした。Issue #118も完了済み。
- 変更ファイル: PR #128で`config/sources.json`、`projects/README.md`、`tests/test_source_registry.py`、`tests/test_read_only_acceptance.py`を変更。本作業記録として`work-records/md/work_record_090.md`、metadata、生成HTMLを追加する。
- 検証結果: 公開側unit test 121件成功、index generator check成功、作業記録HTML check成功、filename validator成功、`git diff --check`成功。生成元・公開側ActionsとPages公開確認も成功。
- 作業ブランチ: PR #128は`codex/120-sport-portal-enable`。本作業記録はdocs-only運用に従い、最新`main`へ直接追加する。
- コミット: PR #128 merge commit `1a5d634f24c4815e74ac76c8d01170e81ab2a6e0`、公開反映コミット`ef58d9b71b0ed2fb8bb55567e29a9f0b6d773a3a`。作業記録のcommitは作成後に追記する。
- PR: [公開側PR #128](https://github.com/tj-999-comp/sandbox-pages/pull/128)（マージ済み）。本作業記録はdocs-onlyのためPRなし。
- PRレビュー・CI: PR #128のValidate check成功。実E2Eの生成元・公開側workflowも成功。
- 未解決事項: なし。
- 次アクション: `sport-portal`で新しい作業記録を追加した際は、生成元workflowのpublish requestを実行し、公開側のprovenanceとPages URLを確認する。

## GitHub Issue状況

確認日時（JST）: 2026-09-07 18:17
取得範囲: `tj-999-comp/sandbox-pages`のOpen Issue全件（Pull Request除外）
取得件数: 0件（一覧行数: 0件）

### 親子関係

```text
親子関係なし（Open Issueなし）
```

### 優先順位順の未完了一覧

該当Issueなし。

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |

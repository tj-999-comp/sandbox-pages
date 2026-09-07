# 作業記録 089: sport-portal生成元の公開受入準備
作成日: 2026-09-07

## 概要

- 課題: `sport-portal`を生成元リポジトリとして作成し、公開側 `sandbox-pages` で受け入れられる状態にする。
- 目的: 固定commit・単一basenameの `a_rendered` 受入契約へ接続し、将来のスポーツ内容確認サイトの作業記録を公開できる導線を用意する。
- 完了条件: 生成元側のproject ID固定、公開側registry登録、初期provenance、index、validator、disabled dry-run、公開ルール、検証記録を揃える。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: GitHub Issue #118・#120、`sport-portal`のテンプレート初期構成、公開側のsource registry・受入validator・renderer・provenance契約。
- 実施内容: 生成元のREADMEと `request-publish.yml` を `sport-portal` 用に更新し、初回作業記録とmetadataを追加した。公開側へ `sport-portal` を `a_rendered`、`enabled: false` で登録し、初期provenance、空のproject index、global index、導入ルール、registryテストを追加した。
- 成果物: 生成元ブランチ `codex/001-sport-portal-source-setup`、公開側ブランチ `codex/120-sport-portal-acceptance`。
- 検証結果: 生成元validatorは1件合格。公開側ユニットテスト121件、index・filename・作業記録HTML検証、固定commit受入dry-runが合格した。
- 未解決事項: GitHub Actions上の実受入、Pages公開、Slack通知、`enabled: true`への切り替えは未実施。
- 次工程への引き継ぎ: 生成元PRをmerge後、source mainの固定SHAで公開側のdisabled dry-runと手動E2Eを実施し、問題がなければregistryを有効化する。

### Portfolio Reviewer

- 入力: 両ブランチの差分、source registry、provenance、生成index、テスト結果。
- 実施内容: `sport-portal` が既存projectと異なるproject ID・公開先を持ち、生成元を公開側の書き込み権限なしで受け入れる構成であることを確認した。
- 成果物: 受入範囲、初期状態、未解決事項をこの記録へ反映した。
- 検証結果: 重大な未解決事項は、実GitHub Actions E2Eを除き確認されなかった。
- 未解決事項: source PRと公開側PRの外部レビュー・merge待ち。
- 次工程への引き継ぎ: PR作成後にGitHub上の差分とCIを確認する。

### Portfolio Performance & Accessibility Tester

- 入力: 追加した `projects/index.html` と `projects/sport-portal/index.html`。
- 実施内容: Chromiumで1280x900、900x900、640x900、320x800を確認した。
- 成果物: `/private/tmp/sport-portal-browser-global/report.json`、`/private/tmp/sport-portal-browser-project/report.json`。
- 検証結果: 全viewportでHTTP 200、横overflowなし、console/page errorなし、failed requestなし。320pxのproject indexも表示を確認した。
- 未解決事項: Pagesへ実デプロイした公開URLの確認は未実施。
- 次工程への引き継ぎ: E2E公開後にPages URLでも同じviewport確認を行う。

## 主要な判断

- 判断: `project_id` はリポジトリ名と同じ `sport-portal` とし、初期登録は `enabled: false` とした。
- 理由: 公開先の識別子を生成元のmetadataから推測せず、公開側registryで不変に管理するため。実GitHub Actions E2EとPages公開を終えるまで本番受入を有効化しないため。
- 判断: 生成元の初回作業記録を `publish: true` で追加した。
- 理由: 固定commit・単一basenameの受入dry-runを実データで検証するため。ただし公開側がdisabledの間は公開処理へ進まない。

## 最終結果

- 解決したこと: `sport-portal`を生成元契約へ接続し、公開側の受入準備を完了した。生成元側のローカル検証と公開側の固定commit受入dry-runで、Markdown・metadata・renderer・provenanceの境界を確認した。
- 変更ファイル: 公開側の `config/sources.json`、`projects/README.md`、`provenance/sport-portal/initial.json`、生成index、テスト、作業記録。生成元側のREADME、`request-publish.yml`、初回作業記録とmetadata。
- 検証結果: 生成元validator 1件成功、公開側ユニットテスト121件成功、index・filename・HTML検証成功、固定commit dry-run成功、Chromium 4 viewport確認成功。
- 作業ブランチ: 公開側 `codex/120-sport-portal-acceptance`、生成元側 `codex/001-sport-portal-source-setup`。
- コミット: 生成元側 `176a2801bcbd85801830cad57e88c55667df64aa`。公開側は作成中。
- PR: 生成元側・公開側とも未作成。
- PRレビュー・CI: 未実施。
- 未解決事項: source mainへのmerge、公開側PRのmerge、GitHub Actions実受入、Pages公開URL・Slack通知の確認、`enabled: true`化。
- 次アクション: 生成元PRをmergeし、公開側PRをmergeした後、`sport-portal`の `work_record_001` を固定SHAで手動E2Eする。合格後に `config/sources.json` の `enabled` を `true` にする。

## GitHub Issue状況

確認日時（JST）: 2026-09-07 17:45
取得範囲: `tj-999-comp/sandbox-pages` のOpen Issue全件（Pull Request除外）
取得件数: 2件（一覧行数: 2件）

### 親子関係

```text
親子関係なし（#118、#120のsub-issues API結果はいずれも空）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#120 [受入] スポーツサイト生成元リポジトリを公開側へ登録する](https://github.com/tj-999-comp/sandbox-pages/issues/120) | OPEN（state reason: null） | 本作業の対象。source main merge後の実E2Eとenabled化が未完了。 |
| 2 | 未設定 | [#118 自分専用のスポーツ内容確認サイト用リポジトリを作成する](https://github.com/tj-999-comp/sandbox-pages/issues/118) | OPEN（state reason: null） | 生成元リポジトリ作成と初期設定は完了。Issueのクローズ判断はユーザー確認後。 |

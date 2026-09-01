# 作業記録 077: 生成元リポジトリ用GitHub Templateを登録
作成日: 2026-09-01

## 概要

- 課題: 新しい生成元リポジトリを毎回手作業で構成する負担を減らす。
- 目的: 作業記録の入力、自己検証、公開要求workflowを含む専用テンプレートを作成し、GitHub Template Repositoryとして利用できる状態にする。
- 完了条件: `work-record-source-template`を公開リポジトリとして作成し、`main`へ初期構成をpushし、Template Repository設定とworkflow登録を確認する。既存の`sandbox-pages`へ無関係な変更を加えない。

## 適用した役割

### Portfolio Planner

- 入力: `sandbox-pages`の公開契約、`projects/README.md`、`docs/PORTFOLIO_STANDARD.md`、ユーザーとの三層構成の合意。
- 実施内容: 公開集約側の`sandbox-pages`と生成元を分離し、生成元専用リポジトリをGitHub Templateとして作成する構成を決定した。新規生成元は`a_rendered`方式とし、Markdownとmetadataを正本入力として扱う方針を採用した。
- 成果物: `tj-999-comp/work-record-source-template`の構成方針。
- 検証結果: 既存の公開リポジトリ、provenance、publish script、既存作業記録をテンプレートへ含めない境界を確認した。
- 未解決事項: 個別生成元を追加するときのsource registry登録と実Secret設定は、各生成元の導入時に行う。
- 次工程への引き継ぎ: 新規生成元はGitHubの「Use this template」から作成し、固有の`project_id`を設定する。

### Portfolio Frontend Engineer

- 入力: 既存の作業記録命名・metadata契約、GitHub App連携方針、GitHub Template Repository機能。
- 実施内容: 専用リポジトリに`work-records/md/`、`work-records/metadata/`、source-side validator、`Validate source` workflow、`Request publish` workflow、運用READMEを作成した。公開要求workflowはPEMをtokenとして直接利用せず、`PUBLISH_APP_ID`と`PUBLISH_APP_PRIVATE_KEY`から短期Installation tokenを発行して、固定SHA・対象basename・project_idだけを`sandbox-pages`へdispatchする構成にした。
- 成果物: `tj-999-comp/work-record-source-template`、初期commit `f4ce2e7d2a67c807f511b490a50ab6c8080e6a9b`。
- 検証結果: source validatorは空の初期状態を`Validated 0 work record(s).`として検証し、GitHub上で2つのworkflowがactiveとして認識された。
- 未解決事項: `request-publish.yml`の`PROJECT_ID`はテンプレート利用時に各生成元の値へ置換する必要がある。GitHub Appの`PUBLISH_APP_ID` variableと`PUBLISH_APP_PRIVATE_KEY` secretも各生成元で設定する。
- 次工程への引き継ぎ: `sandbox-pages`側で生成元ごとのsource registry登録、disabled dry-run、固定commitによる手動E2Eを実施する。

### Portfolio Reviewer

- 入力: GitHub上のテンプレートリポジトリ、初期commit、workflow一覧、Template Repository設定。
- 実施内容: リポジトリが公開、default branchが`main`、Template Repositoryが有効であることを確認した。既存の`sandbox-pages`に変更がないこと、テンプレートに秘密情報・既存公開成果物・公開側の権限付き処理が含まれていないことを確認した。
- 成果物: [work-record-source-template](https://github.com/tj-999-comp/work-record-source-template)の登録確認。
- 検証結果: GitHub APIとCLIで`isTemplate: true`、`isPrivate: false`、`defaultBranch: main`、`Validate source`・`Request publish`のactive状態を確認した。重大な未解決事項はない。
- 未解決事項: 実際の生成元を作成した後のGitHub App secretを使った公開要求E2Eは未実施。
- 次工程への引き継ぎ: 「Use this template」で生成元を作成後、`project_id`置換とsource registryの導入確認を行う。

### Portfolio Performance & Accessibility Tester

- 入力: 生成した`work_record_077.html`、`work-records/design.md`、`work-records/work_record.css`。
- 実施内容: 生成HTMLをPC幅と320px幅の実ブラウザで表示し、ページエラー、console error、横overflow、主要リンクの表示を確認する。
- 成果物: `work-records/work_record_077.html`とブラウザ確認結果。
- 検証結果: 1280pxと320pxでHTTP 200、横overflowなし、console/page errorなし、主要リンク表示を確認した。
- 未解決事項: スクリーンリーダーによる実機検証は未実施。
- 次工程への引き継ぎ: Markdown原本と生成HTMLを同じcommitでmainへ反映する。

## 主要な判断

- 判断: 現在の`sandbox-pages`をそのままTemplate Repositoryにはせず、専用の`work-record-source-template`を新規作成する。
- 理由: `sandbox-pages`には公開成果物、provenance、受入処理、既存作業記録が含まれ、新規生成元へ複製すると責務と履歴が混ざるため。
- 判断: 新規生成元は`a_rendered`方式を標準にする。
- 理由: HTML・CSS・indexの重複管理を避け、公開リポジトリ側のrendererとvalidatorを正本にできるため。
- 判断: GitHub Template Repositoryを使い、Forkは使わない。
- 理由: 各生成元を独立したリポジトリとして扱い、生成元commitとprovenanceの境界を明確にできるため。

## 最終結果

- 解決したこと: 新規生成元の初期構成を再利用できる公開GitHub Template Repositoryを作成・登録した。作業記録入力、metadata、自己検証、固定commitによる公開要求の入口をテンプレートへまとめた。
- 変更ファイル: `work-records/md/work_record_077.md`、`work-records/metadata/work_record_077.yml`、`work-records/work_record_077.html`。別リポジトリに`README.md`、`work-records/README.md`、`scripts/dev/validate_work_records.py`、`.github/workflows/validate.yml`、`.github/workflows/request-publish.yml`を作成した。
- 検証結果: テンプレート側validator、Python構文確認、GitHub Template設定確認、workflow認識確認、作業記録HTML生成・check、filename validator、既存テスト、`git diff --check`、1280px/320pxブラウザ確認に合格した。
- 作業ブランチ: `main`（作業記録のみの変更のため、運用ルールに従い最新mainへ直接反映）
- コミット: 作成後に記載
- PR: なし（作業記録のみの変更）
- PRレビュー・CI: PRなし。ローカル検証とブラウザ確認を実施。push後にmainのCIを確認する。
- 未解決事項: 個別生成元の作成、固有`project_id`への置換、GitHub Appのvariable・secret設定、`sandbox-pages`側source registry登録、実公開E2Eは未実施。
- 次アクション: 必要なプロジェクトでTemplateを利用し、公開リポジトリ側の導入チェックリストに沿ってsource登録と固定SHAの手動E2Eを行う。

## GitHub Issue状況

確認日時（JST）: 2026-09-01 14:49
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue（Pull Requestを除外）。7件をGitHub Appで取得し、#89のsub-issues APIで親子関係を確認した。state reasonは全件null。

### 親子関係

```text
#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する [Open]
├── #90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する [Open]
├── #91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する [Open]
├── #92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する [Open]
├── #93 [Publish] 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する [Open]
└── #94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う [Open]

#102 [Operations] 作業記録のIssue状況を該当リポジトリ単位で全生成元へ統一する [Open]
（親子関係なし）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open（state_reason: null） | 全体Epic。#90〜#94の完了を追跡する。 |
| 2 | 未設定 | [#90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open（state_reason: null） | #89の子Issue。 |
| 3 | 未設定 | [#91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open（state_reason: null） | #89の子Issue。 |
| 4 | 未設定 | [#92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open（state_reason: null） | #89の子Issue。 |
| 5 | 未設定 | [#93 [Publish] 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | Open（state_reason: null） | #89の子Issue。 |
| 6 | 未設定 | [#94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open（state_reason: null） | #89の子Issue。 |
| 7 | 未設定 | [#102 [Operations] 作業記録のIssue状況を該当リポジトリ単位で全生成元へ統一する](https://github.com/tj-999-comp/sandbox-pages/issues/102) | Open（state_reason: null） | #89とは別の独立Issue。 |

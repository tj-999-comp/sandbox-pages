# 作業記録 019: プロジェクト進捗ページ自動公開のIssue分解と登録
作成日: 2026-08-18

## 概要

- 課題: プロジェクト進捗ページの自動公開について、公開契約と既存作業記録を基に、実装・検証・運用を追跡できるGitHub Issueへ小分けにする。
- 目的: `sandbox-pages`（公開側A）と`B_Stats_Site`（生成元B）の所有境界を保ちながら、依存関係、安全条件、着手順を明確にする。
- 完了条件: 親Epicと個別IssueがGitHubへ登録され、各Issueに目的、完了条件、依存関係、安全条件が記録され、次セッションの着手点が一意に分かる。

## 適用した役割

### Portfolio Planner

- 入力: `work_record_016`、`work_record_018`、`projects/README.md`の公開契約、ユーザーの「可能な限りタスクを小分けしてGitHubにIssue登録する」要望。
- 実施内容: A側のsource登録、validator、manifest、Pages、index、workflow、通知、E2E、運用改善と、B側の親リンク修正、metadata、validator、公開要求workflow、自動triggerを、1 PR程度で完結しやすい粒度へ分解した。
- 成果物: 公開側20件、生成元側5件、合計25件の実行Issueと、依存順を集約する親Epic。
- 検証結果: 初回公開のcritical pathと、`a_rendered` renderer、公開取り下げ、GitHub App移行などの後続対応を分離した。
- 未解決事項: 各Issueの実装は未着手であり、公開設定、Secrets、Pages設定は変更していない。
- 次工程への引き継ぎ: A-01とB-01を並行着手できる状態にした。

### Portfolio Frontend Engineer

- 入力: 公開契約、既存GitHub Issue、現在のGit状態。
- 実施内容: `tj-999-comp/sandbox-pages`と`tj-999-comp/B_Stats_Site`の既存Issueを照合し、重複しないことを確認してIssueを登録した。親Epicにはフェーズ別のチェックリストとA/B横断リンクを追加した。
- 成果物:
  - 親Epic: [sandbox-pages #5](https://github.com/tj-999-comp/sandbox-pages/issues/5)
  - 公開側A: [#6](https://github.com/tj-999-comp/sandbox-pages/issues/6)から[#25](https://github.com/tj-999-comp/sandbox-pages/issues/25)までの20件
  - 生成元B: [#28](https://github.com/tj-999-comp/B_Stats_Site/issues/28)から[#32](https://github.com/tj-999-comp/B_Stats_Site/issues/32)までの5件
- 検証結果: A側は親Epicを含む21件、B側は5件がopenであることをGitHub上で再確認した。Issue登録以外の外部設定・デプロイ変更は行っていない。
- 未解決事項: issue label、assignee、milestoneは未設定。実装開始時に必要なら運用方針に従って追加する。
- 次工程への引き継ぎ: まずA-01（source登録）を開始し、B-01（親ディレクトリREADMEリンク修正）は並行して実施する。

### Portfolio Reviewer

- 入力: 公開契約、Issue分解案、依存順、安全条件。
- 実施内容: `enabled: false`からの開始、固定commit SHA、生成元へのContents write権限を渡さないこと、Aの権限付きjobで生成元コードを実行しないこと、manifest drift、no-op、Pages固定SHA、Slack通知、親リンク修正、番号なし補助HTMLの除外を確認した。
- 成果物: bootstrapと通常受入を混同せず、Bのmetadata未導入・親リンク未修正を理由に通常validatorを緩めない依存順。
- 検証結果: 親Epicと各子Issueの目的・完了条件・依存関係に上記の安全条件を反映した。
- 未解決事項: `enabled: false`のまま実公開E2Eを行う契約上の曖昧さは、A-17で手動E2Eに限って有効化し、B-05までpush triggerを有効化しない手順で扱う。
- 次工程への引き継ぎ: A-16のdisabled dry-run合格後にA-17へ進み、手動E2E合格までは自動triggerを有効化しない。

### Portfolio Performance & Accessibility Tester

- 入力: 新規作業記録Markdown、生成HTML、`work-records/design.md`、`work-records/work_record.css`。
- 実施内容: 新規HTMLをPlaywrightで1280×900px、900×900px、640×900px、320×800pxに表示し、横overflow、実行時エラー、リンク、キーボードfocusを確認した。
- 成果物: `work_record_019.html`のブラウザ検証結果。
- 検証結果: 全4 viewportで横overflow、console error、page error、failed requestは0件だった。320pxでは12個のリンクすべてへTab移動でき、各リンクにfocusした。
- 未解決事項: 実スクリーンリーダーでの読み上げ確認は今回の記録更新では対象外。
- 次工程への引き継ぎ: ブラウザ検証が合格したら、ドキュメント専用commitとして最新`main`へpushする。

## 主要な判断

- 判断: 公開側Aと生成元BのIssueを別リポジトリへ登録し、親Epicで横断的に追跡する。
- 理由: source登録、受入validator、manifest、Pages、index、通知はA所有であり、metadata、generator、生成元validator、dispatchはB所有のため。
- 判断: 初回実装はA-01から開始し、B-01を並行可能な独立作業として扱う。
- 理由: A-01は後続の受入基盤の共通依存であり、B-01の親リンク修正はAのsource登録を待たずに進められるため。
- 判断: label、assignee、milestoneは作成時に設定しない。
- 理由: 既存運用との不整合を避け、Issue本文と親Epicの依存関係を正本とするため。

## 最終結果

- 解決したこと: 自動公開の導入順を、親Epic1件と実行Issue25件に分解し、A/Bの責務と安全条件をGitHubへ記録した。
- 変更ファイル: `work-records/md/work_record_019.md`、`work-records/work_record_019.html`。
- 検証結果: GitHub上のIssue件数・open状態、converterの`--check`、ファイル名・H1・日付・対応HTML validator、`git diff --check`に合格した。Playwrightでは1280×900px、900×900px、640×900px、320×800pxの横overflow・runtime errorが0件で、320pxの12リンクへTab移動できた。
- 作業ブランチ: `main`（ドキュメント専用更新）。
- コミット: ドキュメント専用commitとして実施し、SHAはGit履歴を参照する。
- PR: ドキュメント専用更新のため作成しない。
- PRレビュー・CI: Reviewerによる事前確認とローカル検証を実施する。GitHub Actionsの実装・CIは今回の対象外。
- 未解決事項: 自動公開機構そのものは未実装。Issue #6以降で段階的に進める。
- 次アクション: [sandbox-pages #6](https://github.com/tj-999-comp/sandbox-pages/issues/6)を開始し、並行して[B_Stats_Site #28](https://github.com/tj-999-comp/B_Stats_Site/issues/28)へ着手する。`enabled: false`、push trigger未有効、Secrets未作成の状態を維持する。

## GitHub Issue状況

取得日時（JST）: 2026-08-18 16:06
スナップショット: GitHubから取得したこの時点の状態。親Epic1件、公開側Aの実行Issue20件、生成元Bの実行Issue5件はすべてOpenであり、Closedは0件。

### 公開側A: `tj-999-comp/sandbox-pages`

- GitHub Issue [#5](https://github.com/tj-999-comp/sandbox-pages/issues/5): プロジェクト進捗ページの自動公開を段階導入する
  - 関係: 親Epic
  - 状態: Open
- GitHub Issue [#6](https://github.com/tj-999-comp/sandbox-pages/issues/6): 公開元source登録を設定ファイル化する
  - 関係: A-01、次の着手候補
  - 状態: Open
- GitHub Issue [#7](https://github.com/tj-999-comp/sandbox-pages/issues/7): 共通命名・metadata schema validatorを実装する
  - 関係: A-02
  - 状態: Open
- GitHub Issue [#8](https://github.com/tj-999-comp/sandbox-pages/issues/8): 受入ファイルのpath・種別・容量validatorを実装する
  - 関係: A-03
  - 状態: Open
- GitHub Issue [#9](https://github.com/tj-999-comp/sandbox-pages/issues/9): source_html向けHTML・CSS・URL安全validatorを実装する
  - 関係: A-04
  - 状態: Open
- GitHub Issue [#10](https://github.com/tj-999-comp/sandbox-pages/issues/10): provenance manifest schemaとdrift検査を実装する
  - 関係: A-05
  - 状態: Open
- GitHub Issue [#11](https://github.com/tj-999-comp/sandbox-pages/issues/11): B既存001〜010の初期provenance manifestを登録する
  - 関係: A-06
  - 状態: Open
- GitHub Issue [#12](https://github.com/tj-999-comp/sandbox-pages/issues/12): 既存Bのno-op同期dry-runを実装する
  - 関係: A-07
  - 状態: Open
- GitHub Issue [#13](https://github.com/tj-999-comp/sandbox-pages/issues/13): a_rendered用の決定的rendererを実装する
  - 関係: A-08、初回B公開のcritical path外
  - 状態: Open
- GitHub Issue [#14](https://github.com/tj-999-comp/sandbox-pages/issues/14): Actions botのmain反映方針とbranch rulesetを確定する
  - 関係: A-09
  - 状態: Open
- GitHub Issue [#15](https://github.com/tj-999-comp/sandbox-pages/issues/15): legacy PagesをカスタムActions deployへ移行する
  - 関係: A-10
  - 状態: Open
- GitHub Issue [#16](https://github.com/tj-999-comp/sandbox-pages/issues/16): project・global進捗index generatorを実装する
  - 関係: A-11
  - 状態: Open
- GitHub Issue [#17](https://github.com/tj-999-comp/sandbox-pages/issues/17): read-only受入workflowをdry-runで実装する
  - 関係: A-12
  - 状態: Open
- GitHub Issue [#18](https://github.com/tj-999-comp/sandbox-pages/issues/18): 許可範囲限定の同期apply engineを実装する
  - 関係: A-13
  - 状態: Open
- GitHub Issue [#19](https://github.com/tj-999-comp/sandbox-pages/issues/19): 受入workflowへcommit・固定SHA deployを接続する
  - 関係: A-14
  - 状態: Open
- GitHub Issue [#20](https://github.com/tj-999-comp/sandbox-pages/issues/20): deploy成功後のSlack通知jobを実装する
  - 関係: A-15
  - 状態: Open
- GitHub Issue [#21](https://github.com/tj-999-comp/sandbox-pages/issues/21): disabled sourceでBの受入dry-runを実行する
  - 関係: A-16
  - 状態: Open
- GitHub Issue [#22](https://github.com/tj-999-comp/sandbox-pages/issues/22): B sourceを手動E2E可能な状態へ有効化する
  - 関係: A-17
  - 状態: Open
- GitHub Issue [#23](https://github.com/tj-999-comp/sandbox-pages/issues/23): 受入・Pages・公開URL・Slackの一連を検証する
  - 関係: A-18
  - 状態: Open
- GitHub Issue [#24](https://github.com/tj-999-comp/sandbox-pages/issues/24): 監査可能な公開取り下げworkflowを実装する
  - 関係: A-19、初回B公開のcritical path外
  - 状態: Open
- GitHub Issue [#25](https://github.com/tj-999-comp/sandbox-pages/issues/25): dispatch認証をFine-grained PATからGitHub Appへ移行する
  - 関係: A-20、初回B公開のcritical path外
  - 状態: Open

### 生成元B: `tj-999-comp/B_Stats_Site`

- GitHub Issue [#28](https://github.com/tj-999-comp/B_Stats_Site/issues/28): 親ディレクトリREADMEリンクをproject内リンクへ修正する
  - 関係: B-01、次の着手候補
  - 状態: Open
- GitHub Issue [#29](https://github.com/tj-999-comp/B_Stats_Site/issues/29): 001〜010のmetadataと生成元validator・CIを追加する
  - 関係: B-02
  - 状態: Open
- GitHub Issue [#30](https://github.com/tj-999-comp/B_Stats_Site/issues/30): 手動公開要求workflowとdispatch権限を設定する
  - 関係: B-03
  - 状態: Open
- GitHub Issue [#31](https://github.com/tj-999-comp/B_Stats_Site/issues/31): 新規作業記録1件を手動publish要求する
  - 関係: B-04
  - 状態: Open
- GitHub Issue [#32](https://github.com/tj-999-comp/B_Stats_Site/issues/32): main更新時の公開要求triggerを有効化する
  - 関係: B-05
  - 状態: Open

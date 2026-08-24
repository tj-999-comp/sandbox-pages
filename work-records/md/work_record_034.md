# 作業記録 034: Issue #21 disabled source受入dry-run
作成日: 2026-08-20

## 概要

- 課題: GitHub Issue #21「[E2E] disabled sourceでBの受入dry-runを実行する」。
- 目的: B-01/B-02の固定commitを実際のA側受入validatorへ渡し、公開候補、対象外ファイル、予定差分、安全境界をwriteなしで確認する。
- 完了条件: `work_record_001`〜`010`、metadata、登録済みsupport fileだけが候補になり、補助ファイルを除外したうえでA-02〜A-04が合格し、Aの`main`・Pages・Slackが変更されないことを確認する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: Issue #21、A側の`accept-source.yml`、source registry、A-02〜A-04 validator、B-01 merge commit `3c878f9abf1736d274dfc8153b7f648f529e26fd`、B-02 merge commit `43ebad8db4eff14c0a8e0d928ad193291fdfd60d`。
- 実施内容: 固定B-02 commitを一時checkoutし、B現在`main`のancestorであることを確認した。実データでのローカル受入再現時に、A-03がBの既知補助Markdown・補助HTMLを一律拒否し、A-04が既存HTMLの`h4`・`aside`を拒否する問題を発見した。A所有のsource registryへ`ignored_files`を追加し、対象外ファイルをinventory・候補・HTML安全検証から除外した。A-04の静的許可タグへ`h4`・`aside`を追加した。
- 成果物: `config/sources.json`、`scripts/publish/source_registry.py`、`scripts/publish/acceptance_files.py`、`scripts/publish/content_safety.py`、関連テスト、`projects/README.md`。
- 検証結果: 固定B-02 commitに対し`work_record_001`〜`010`を個別に検証し、全件で`dry_run=true`、`apply=false`、`enabled=false`、inventory 45件、target inventory 6件、A-02 metadata・A-03 acceptance file・A-04 content safety合格となった。対象外は`md/phase_1_tasks.md`、`md/scraping_db_automation.md`、`work_record_extra_01.html`、`work_record_extra_02.html`で、inventoryに含まれないことを確認した。
- 未解決事項: GitHub Actions上の実workflow dispatch、artifact取得、apply jobの実run、Aのmain・Pages・SlackのGitHub上での非変更確認は未実施。ローカルApp tokenはKeychain項目を読めず、in-app Browserも利用できなかった。
- 次工程への引き継ぎ: GitHub認証を復旧して`accept-source.yml`を`main`からdispatchし、10件のrun、dry-run artifact、apply no-op、Pages deploy skipを確認する。実workflowが合格するまでIssue #21はクローズしない。

### Portfolio Reviewer

- 入力: Issue #21の完了条件、固定B-02 commitのローカル実行結果、source registryとvalidatorの差分、既存テスト。
- 実施内容: `ignored_files`がA所有の明示的な除外境界であること、未知ファイル・symlink・未登録directoryは従来どおり拒否されること、disabled source時にapply・deployへ進まないworkflow guardが残っていることを確認した。
- 成果物: 本作業記録、差分レビュー結果。
- 検証結果: 重大な未解決事項は、実GitHub Actions実行が未確認である点のみ。ローカルテストは全件合格した。
- 未解決事項: 外部GitHub Actions実行と外部PRレビューは未実施。
- 次工程への引き継ぎ: 認証復旧後の実workflow結果を確認し、問題がなければIssue #21の完了判定とPRレビューへ進む。

## 主要な判断

- 判断: B側の補助ファイルをAの`support_files`へ追加せず、A側registryの`ignored_files`へ明示する。
- 理由: 補助ファイルを公開候補へ昇格させず、既知の対象外だけを除外し、未知のファイルは安全側に拒否するため。
- 判断: `h4`と`aside`だけをA-04の許可タグへ追加する。
- 理由: 固定B-02 commitの既存作業記録で実際に使用されている静的要素であり、scriptや外部実行につながる要素ではないため。
- 判断: 実workflow未実行のため、Issue #21を完了扱いにしない。
- 理由: 完了条件は実際のA/B repository間のworkflow実行とA側無変更確認まで含み、ローカル再現だけでは外部E2Eの証跡を代替できないため。

## 最終結果

- 解決したこと: 固定B-02 commitのローカルread-only受入で発見した対象外ファイルと静的HTML要素の受入不整合を、A側の最小差分で修正した。001〜010の全候補をA-02〜A-04で検証できる状態にした。
- 変更ファイル: `config/sources.json`、`projects/README.md`、`scripts/publish/source_registry.py`、`scripts/publish/acceptance_files.py`、`scripts/publish/content_safety.py`、`tests/fixtures/source_registry/invalid_generator_type.json`、`tests/test_acceptance_files.py`、`tests/test_content_safety.py`、`tests/test_source_registry.py`、本作業記録と対応HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（67件合格）、固定B-02 commitの001〜010ローカルread-only acceptance（10件合格）、B-02 commitがB `main`のancestorであること（合格）、workflow YAMLのdisabled guard・deploy skip確認（合格）、`git diff --check`（合格）。
- 作業ブランチ: `codex/034-issue-21-disabled-e2e`。
- コミット: `342215e49cfa24dbb24a79ea7180b950b64f8f15`（Issue #21のvalidator境界修正・テスト・作業記録）。
- PR: [#38 Issue #21: disabled source受入dry-runの境界を修正](https://github.com/tj-999-comp/sandbox-pages/pull/38)（Draft、base `main`、head `codex/034-issue-21-disabled-e2e`）。
- PRレビュー・CI: Draft PR #38を作成。ローカル事前レビューは重大0件。外部PRレビュー、CI、GitHub Actions実workflow dispatchは未実施。
- 未解決事項: GitHub App tokenのKeychain復旧またはGitHub認証済みブラウザ接続が必要。実workflowのartifact、apply no-op、Pages deploy skip、Aのmain・Pages・Slack無変更を確認するまで、#21は未完了。
- 次アクション: PR #38を確認・マージ後、`accept-source.yml`を固定B-02 SHA `43ebad8db4eff14c0a8e0d928ad193291fdfd60d`、`B_Stats_Site`、`work_record_001`〜`010`で`main`からdispatchする。

## GitHub Issue状況

確認日時（JST）: 2026-08-24 13:29
取得範囲: `tj-999-comp/sandbox-pages`の#5、#12、#17〜#23、および`tj-999-comp/B_Stats_Site`の#28〜#29をGitHub connectorで取得した時点のsnapshot。

### 親子関係

```text
sandbox-pages #5（親Epic）
├── sandbox-pages #12（完了）
├── sandbox-pages #17（完了）
├── sandbox-pages #18（完了）
├── sandbox-pages #19（完了）
├── sandbox-pages #20（未完了）
├── sandbox-pages #21（今回の対象・未完了）
├── sandbox-pages #22（未完了）
└── sandbox-pages #23（未完了）

sandbox-pages #5
├── B_Stats_Site #28（完了）
└── B_Stats_Site #29（完了）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P1 | [#20 [Notification] deploy成功後のSlack通知jobを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/20) | Open | #19完了後の通知工程。#23の前提 |
| 2 | P1 | [#21 [E2E] disabled sourceでBの受入dry-runを実行する](https://github.com/tj-999-comp/sandbox-pages/issues/21) | Open | #12、#17、#18、B側#28・#29完了後。今回の対象。実workflow確認待ち |
| 3 | P1 | [#22 [Activation] B sourceを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/22) | Open | #19・#21完了後。source有効化前に#21の重大問題0が必要 |
| 4 | P1 | [#23 [E2E] 受入・Pages・公開URL・Slackの一連を検証する](https://github.com/tj-999-comp/sandbox-pages/issues/23) | Open | #20とB側#31完了後 |

### 完了済みの関連Issue

| GitHub Issue | 状態 | 本作業との関係 |
| --- | --- | --- |
| [#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | Closed / completed | 親Epic |
| [#12 [Bootstrap] 既存Bのno-op同期dry-runを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/12) | Closed / completed | no-op/bootstrap検証の前提 |
| [#17 [Actions] read-only受入workflowをdry-runで実装する](https://github.com/tj-999-comp/sandbox-pages/issues/17) | Closed / completed | 受入workflowの前工程 |
| [#18 [Publish] 許可範囲限定の同期apply engineを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/18) | Closed / completed | apply境界の前工程 |
| [#19 [Actions] 受入workflowへcommit・固定SHA deployを接続する](https://github.com/tj-999-comp/sandbox-pages/issues/19) | Closed / completed | disabled時のapply/deploy skipを含むworkflow |
| [B_Stats_Site #28 親ディレクトリREADMEリンクをproject内リンクへ修正する](https://github.com/tj-999-comp/B_Stats_Site/issues/28) | Closed / completed | B-01固定commit |
| [B_Stats_Site #29 001〜010のmetadataと生成元validator・CIを追加する](https://github.com/tj-999-comp/B_Stats_Site/issues/29) | Closed / completed | B-02固定commit |

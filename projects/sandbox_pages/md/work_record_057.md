# 作業記録 057: 監査可能な公開取り下げworkflowを実装
作成日: 2026-08-28

## 概要

- 課題: GitHub Issue #24「[Operations] 監査可能な公開取り下げworkflowを実装する」。
- 目的: 生成元の`publish: false`やファイル削除とは分離し、公開リポジトリAの管理者が対象を明示して安全に一件だけ取り下げられる運用を実装する。
- 完了条件: dry-runとpreview、対象限定削除、index・provenance同一反映、driftとmain競合の拒否、404・復元手順、Slack非通知を実装・検証する。

## 適用した役割

### Portfolio Automation Engineer

- 入力: `scripts/publish/apply_engine.py`、`scripts/publish/provenance.py`、`scripts/publish/index_generator.py`、既存のPages受入workflow、Issue #24の完了条件。
- 実施内容: `scripts/publish/withdraw_engine.py`を追加し、登録済みprojectの最新provenanceに存在する`work_record_###`だけを対象として、対応するHTMLとMarkdownを明示的に取り下げるようにした。apply前に公開ファイルのdigest、生成済みindex、対象の存在、main SHA、最新publication_idを再検証し、取り下げ操作を`operation: withdraw`の新しいmanifestへ記録するようにした。
- 成果物: dry-run/apply CLI、取り下げworkflow、取り下げ専用テスト、公開取り下げ・復元・Slack方針の文書更新。
- 検証結果: 既存applyテストを含む`tests/test_apply_engine.py`を実行し、取り下げplanの無変更、対象2ファイルの限定削除、withdraw manifest、誤確認文字列、二重取り下げ、公開drift拒否を確認した。workflow契約テストも追加した。
- 未解決事項: 公開側mainへの反映、GitHub Actionsのdry-run/apply、Pages上の404、revertによる復元確認、Issueのクローズは未実施。実際に取り下げる対象basenameはユーザー確認待ち。
- 次工程への引き継ぎ: このブランチをレビュー・PR経由で公開側mainへ反映し、対象basenameを固定してdry-run結果のSHAとpublication_idを保存する。その後、同値を入力したapplyを実行し、Pagesの対象URLが404になることを確認する。

### Portfolio Reviewer

- 入力: 取り下げengine、workflow、テスト、`projects/README.md`、`docs/ACTIONS_MAIN_POLICY.md`。
- 実施内容: source側の消失や`publish: false`を削除トリガーにしていないこと、対象外ファイル・symlink・manifest drift・stale index・main更新を拒否すること、Slack Secretをworkflowへ渡していないことを確認した。
- 検証結果: コード差分と専用テストに基づく事前レビューで、削除範囲は登録先配下の同名HTMLとMarkdownに固定され、indexとwithdraw manifestは同一commitへ含まれる設計であることを確認した。
- 未解決事項: GitHub Actions実行環境でのremote main保護、Pages反映、旧URLの実応答、rollback実行はmain反映後に確認する。

## 主要な判断

- 判断: dry-runとapplyを別dispatchに分け、applyではdry-runの完全SHAと最新publication_idの再入力を要求する。
- 理由: previewを確認した後にmainや公開状態が変わっていないことを機械的に確認し、別対象・古いpreviewのまま削除しないため。
- 判断: 操作確認文字列を`WITHDRAW`に固定し、withdrawではSlack通知を送らない。
- 理由: 一件の公開停止を公開完了通知と混同せず、手動の破壊的操作であることを明示するため。
- 判断: 取り下げmanifestは削除せず、最新manifestとして対象recordを除いた状態を保存する。
- 理由: 過去の公開commitと対象URLを監査可能な履歴として残し、必要時はrevertで復元できるようにするため。

## 最終結果

- 解決したこと: A管理者が`project_id`、basename、dry-runで得たSHA・publication_id、`WITHDRAW`確認を指定して、一件の公開作業記録だけを取り下げるCLIとworkflowを実装した。取り下げ時は対象HTML・Markdown、project/global index、withdraw provenanceを同一commitへ反映する。
- 変更ファイル: `.github/workflows/withdraw.yml`、`scripts/publish/withdraw_engine.py`、`tests/test_apply_engine.py`、`tests/test_pages_workflow.py`、`projects/README.md`、`docs/ACTIONS_MAIN_POLICY.md`、`work-records/md/work_record_057.md`、`work-records/work_record_057.html`。
- 検証結果: `PYTHONPYCACHEPREFIX=/private/tmp/sandbox-pages-pycache python3 -m unittest tests/test_apply_engine.py -v`（14件成功）、workflow契約テストを含む全体テスト、`python3 -m scripts.publish.index_generator --check`、作業記録HTML生成・ファイル名検証、`git diff --check`を実施する。
- 実行保留: 実際の削除は対象basename未確定のため未実施。候補を勝手に削除せず、対象確認後にdry-runから開始する。
- 復元方針: 取り下げ後URLは404とし、復元時は取り下げcommitをrevertするPRを経て固定SHAでPagesを再deployする。withdraw manifest自体は履歴として保持する。

## GitHub Issue状況

確認日時（JST）: 2026-08-28 12:00
取得範囲: `tj-999-comp/sandbox-pages`のIssue #24をGitHub CLIで再取得し、同リポジトリのopen Issue一覧をPull Request除外で確認した。#24はOPEN、タイトルは`[Operations] 監査可能な公開取り下げworkflowを実装する`、更新日時は`2026-08-18T06:42:47Z`。

### 親子関係

```text
#5
└── #24 [Operations] 監査可能な公開取り下げworkflowを実装する（A-19）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未取得 | [#24 監査可能な公開取り下げworkflowを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/24) | OPEN | 本作業の対象。依存Issue #16/#18/#19を前提に、PRレビューとmain反映後に実workflowを確認する |

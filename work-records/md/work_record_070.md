# 作業記録 070: Issue #82 同一repository source受入隔離
作成日: 2026-08-31

## 概要

- 課題: GitHub Issue #82「同一リポジトリsourceの固定commit・basename限定受入を実装・検証する」。
- 目的: `sandbox-pages`自身をsource repositoryとして受け入れる場合も、sourceと公開成果物を混同せず、固定SHA・単一basename・registry許可範囲に限定する。
- 完了条件: 同一repositoryの別checkout、credential非永続化、固定SHA・basename・path検証、source変更競合、書き込み境界をworkflow・apply engine・テストで固定する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: GitHub Issue #82、`.github/workflows/accept-source.yml`、`scripts/publish/apply_engine.py`、source registry、既存の受入テスト。
- 実施内容: Repository Aの初回checkoutを`persist-credentials: false`へ変更し、source checkout後にcheckout rootの分離とcredential/HTTP extraheader残存を検査するstepをdry-run/applyへ追加した。apply engineではsource checkoutがRepository Aのworktreeと重なる場合を拒否し、同一repositoryでも別checkoutを必須化した。
- 成果物: 同一repository source隔離workflow、apply engineの境界検証、source変更・SHA不一致・不正target path・同一worktree拒否のテスト、運用方針文書。
- 検証結果: 106 tests、workflow YAML構文、index、作業記録HTML、命名、`git diff --check`に合格した。
- 未解決事項: GitHub Actions上の実source checkout、disabled dry-run、Pages反映、運用引き継ぎは後続Issue #83〜#87の対象。
- 次工程への引き継ぎ: #83で現行sandbox_pages作業記録を初期provenanceへ登録する。

### Portfolio Reviewer

- 入力: #82の完了条件、workflow差分、apply engine差分、追加テスト、既存source受入テスト。
- 実施内容: dispatch入力が`project_id`・`source_commit_sha`・`target_basename`の3値に限定されていること、source SHAが登録branchの祖先として検証されること、source checkoutをapply前にworktree外へ移動すること、許可外pathが書き込み前に拒否されることを確認した。
- 成果物: 差分レビュー結果と検証記録。
- 検証結果: 同一repositoryのregistry設定と別checkout導線、credential残存検出、SHA不一致、source変更後digest不一致、basename外path、source checkout重複をテストで確認した。重大な未解決事項はない。
- 未解決事項: 実GitHub Actions runでの同一repository checkoutとsource変更競合の外部確認は後続の手動E2Eで行う。
- 次工程への引き継ぎ: #82の受入境界を#83以降のprovenance・dry-run・E2Eへ引き継ぐ。

## 主要な判断

- 判断: 同一repositoryでもsourceは別checkoutから読み取り、apply engineではRepository Aのworktreeと重なるsource checkoutを拒否する。
- 理由: `work-records/`を公開成果物として直接扱わず、固定SHAのsource入力と`projects/<project_id>/`の生成物を明確に分離するため。
- 判断: dry-run/applyのRepository A checkoutとsource checkoutをcredential非永続化とし、source checkoutのlocal git configを検査する。
- 理由: source認証用tokenやHTTP extraheaderがworktree、artifact、後続処理へ残る経路を最小化するため。
- 判断: source変更後のinventory digest不一致はapply前に失敗させ、sourceを再取得して自動追随しない。
- 理由: dispatch時に指定された固定SHAと検証済みinventoryを、別のsource状態へ差し替えないため。

## 最終結果

- 解決したこと: 同一repository sourceを別checkout・固定SHA・単一basename・許可pathの境界内でのみ受け入れ、Repository Aの`work-records/`をapply対象から除外する保護を追加した。
- 変更ファイル: `.github/workflows/accept-source.yml`、`docs/ACTIONS_MAIN_POLICY.md`、`scripts/publish/apply_engine.py`、`tests/test_apply_engine.py`、`tests/test_pages_workflow.py`、本作業記録のMarkdown/HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（106 tests成功）、workflow YAML parse、`python3 -m scripts.publish.index_generator --check`、作業記録converter check、filename validator、`git diff --check`に合格した。`actionlint`は実行環境に未インストールのため未実施。
- 作業ブランチ: `codex/070-issue-82-fixed-commit`
- commit: `033a1c5`
- PR: [#106 Issue #82: 同一repository source受入を隔離](https://github.com/tj-999-comp/sandbox-pages/pull/106)
- 未解決事項: #83〜#87の初期provenance、disabled no-op、手動E2E、有効化、公開・通知、運用引き継ぎ。
- 次アクション: #82のPRをCI確認し、マージ後に#83へ進む。

## GitHub Issue状況

確認日時（JST）: 2026-08-31 22:21
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue（Pull Requestを除外）14件。GitHub App tokenで取得し、#79・#89のsub-issues APIも確認した。#81はPR #105のマージにより`CLOSED / COMPLETED`となったため一覧から除外した。state reasonはOpen Issue全件でnull。

### 親子関係

```text
#79 [Epic] sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する [Open]
（GitHub sub-issues API上の子Issueなし。#82〜#87の本文にはParent: #79があるため、着手条件欄へ記録）

#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する [Open]
├── #90 各生成元の過去作業記録を棚卸しし公開対応表を確定する [Open]
├── #91 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する [Open]
├── #92 作業記録ページの構成とrecord間リンクを実装する [Open]
├── #93 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する [Open]
└── #94 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う [Open]
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 未設定 | [#79 [Epic] sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する](https://github.com/tj-999-comp/sandbox-pages/issues/79) | Open（state_reason: null） | 親Epic。#82〜#87の本文は#79を親としているが、sub-issues API上の子登録は確認できない。 |
| 2 | 未設定 | [#82 [Actions] 同一リポジトリsourceの固定commit・basename限定受入を実装・検証する](https://github.com/tj-999-comp/sandbox-pages/issues/82) | Open（state_reason: null） | 本作業。#80・#81完了後。 |
| 3 | 未設定 | [#83 [Bootstrap] sandbox_pages既存作業記録を初期公開状態としてprovenanceへ登録する](https://github.com/tj-999-comp/sandbox-pages/issues/83) | Open（state_reason: null） | #80〜#82完了後。 |
| 4 | 未設定 | [#84 [E2E] sandbox_pagesのdisabled受入dry-runとno-opを検証する](https://github.com/tj-999-comp/sandbox-pages/issues/84) | Open（state_reason: null） | #83完了後。 |
| 5 | 未設定 | [#85 [Activation] sandbox_pagesを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/85) | Open（state_reason: null） | #84のレビューと明示承認後。 |
| 6 | 未設定 | [#86 [E2E] sandbox_pagesの新規作業記録をPages公開しSlack通知まで確認する](https://github.com/tj-999-comp/sandbox-pages/issues/86) | Open（state_reason: null） | #85完了後。 |
| 7 | 未設定 | [#87 [Operations] sandbox_pagesの公開・停止・再通知手順を引き継ぐ](https://github.com/tj-999-comp/sandbox-pages/issues/87) | Open（state_reason: null） | #86完了後。 |
| 8 | 未設定 | [#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open（state_reason: null） | 独立Epic。#90〜#94を追跡する。 |
| 9 | 未設定 | [#90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open（state_reason: null） | #89の子Issue。 |
| 10 | 未設定 | [#91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open（state_reason: null） | #89の子Issue。 |
| 11 | 未設定 | [#92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open（state_reason: null） | #89の子Issue。 |
| 12 | 未設定 | [#93 [Publish] 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | Open（state_reason: null） | #89の子Issue。 |
| 13 | 未設定 | [#94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open（state_reason: null） | #89の子Issue。 |
| 14 | 未設定 | [#102 [Operations] 作業記録のIssue状況を該当リポジトリ単位で全生成元へ統一する](https://github.com/tj-999-comp/sandbox-pages/issues/102) | Open（state_reason: null） | 独立。 |

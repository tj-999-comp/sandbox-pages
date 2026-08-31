# 作業記録 071: Issue #83 sandbox_pages初期provenance登録
作成日: 2026-08-31

## 概要

- 課題: GitHub Issue #83「sandbox_pages既存作業記録を初期公開状態としてprovenanceへ登録する」。
- 目的: metadata整備済みの`sandbox_pages`作業記録を、公開URLを変更しない初期公開状態として`projects/sandbox_pages/`とprovenanceへ登録する。
- 完了条件: 固定source SHA、source/published filesのdigest、初期manifest、project/global index、`operation: create`、`notify: false`、既存project非回帰、drift検査を確定する。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: GitHub Issue #83、#82完了直後の`origin/main`、`config/sources.json`、metadata 001〜070、index generator、provenance schema。
- 実施内容: 固定source SHAを`d6c6b29f10844e2a2e52a9b0660b71aba6e5cf2e`とし、`work_record_001`〜`070`のsource inventory 213件から、support file・Markdown・同名HTMLの公開ファイル143件を生成した。metadataは受入検証情報としてsource inventoryへ残し、公開先へコピーしていない。`initial.json`を`operation: create`、`notify: false`で作成し、`projects/sandbox_pages/`とproject/global indexを生成した。
- 成果物: `provenance/sandbox_pages/initial.json`、`projects/sandbox_pages/`の初期公開ファイル、project/global index、bootstrap専用テスト、導入文書の初期SHA記録。
- 検証結果: manifest、公開先inventory、全record公開条件、source registry、index生成結果を照合し、driftなしを確認した。106 testsからbootstrap専用テスト追加後も全テスト合格した。
- 未解決事項: disabled dry-run、手動E2E、source registry有効化、新規recordの公開・通知は後続Issue #84〜#87の対象。
- 次工程への引き継ぎ: #84へ、初期manifestを直前の公開状態として扱い、`enabled: false`のdry-runでwrite/deploy/通知が発生しないことを引き継ぐ。

### Portfolio Reviewer

- 入力: Issue #83の完了条件、固定SHA、`initial.json`、公開先inventory、生成index、bootstrapテスト。
- 実施内容: 固定SHAが同一repositoryの#82完了後mainを指すこと、source/published filesのdigestと件数、records 001〜070のmetadata、`operation: create`と`notify: false`、metadata非公開、既存projectのindex差分がないことをレビューした。
- 成果物: bootstrap差分レビュー結果とdrift検査結果。
- 検証結果: `sandbox_pages`の初期公開対象70件に欠落・余計なrecordはなく、公開先inventoryはmanifestと一致した。Slack通知対象、既存projectの公開ファイル変更、source `work-records/`の自動削除は発生しない構成である。
- 未解決事項: GitHub Actions上のdisabled no-opとPages deploy skipの実動確認は#84で行う。
- 次工程への引き継ぎ: 固定SHA `d6c6b29...`、初期publication `bootstrap-20260831-sandbox-pages`、対象70件を後続の受入検証へ渡す。

## 主要な判断

- 判断: 初期公開対象は固定SHA `d6c6b29f10844e2a2e52a9b0660b71aba6e5cf2e`時点の001〜070全件とした。
- 理由: #82完了直後の同一repository sourceを基準にすることで、manifestが自分自身をsource入力に含める循環を避けながら、当時存在した全recordを欠落なく公開するため。
- 判断: `published_files`にはsupport file、Markdown、同名HTMLだけを含め、metadataは含めない。
- 理由: metadataはA側validatorが受入時に使うsource入力であり、公開URLを持つ成果物ではないため。
- 判断: `operation: create`、`notify: false`とし、既存projectのmanifest・公開ファイル・通知経路を変更しない。
- 理由: 初期bootstrapを公開状態の登録に限定し、Slack通知、Pages deploy、既存projectへの副作用を後続のdisabled dry-runで確認可能にするため。
- 判断: 本作業記録071はbootstrap固定SHAの後に追加されたため、初期manifestの対象外とした。
- 理由: 固定SHAのsource inventoryとmanifestのdigestを一致させるため。071自身はmetadataを`publish: true`で登録し、後続の固定SHA受入対象として引き継ぐ。固定SHA時点の001〜070には初期公開対象外recordはない。

## 最終結果

- 解決したこと: `sandbox_pages`の初期公開状態をprovenanceへ登録し、公開先へ70件を配置した。公開URLは`/sandbox-pages/projects/sandbox_pages/work_record_###.html`の既存命名を維持した。
- 変更ファイル: `provenance/sandbox_pages/initial.json`、`projects/sandbox_pages/`、`projects/index.html`、`projects/sandbox_pages/index.html`、`projects/README.md`、`tests/test_sandbox_pages_bootstrap.py`、本作業記録のMarkdown/metadata/HTML。
- 検証結果: 107 tests、source inventory 213件、published files 143件、records 70件、manifest drift検査、index generator check、作業記録converter check、filename validatorに合格した。`git diff --check`は公開元由来の末尾空白2行を除く対象で合格し、該当空白は固定SHAのdigest一致のため保持した。初期manifestは`operation=create`、`notify=false`で、既存projectの公開ファイル差分はない。
- 作業ブランチ: `codex/071-issue-83-provenance`
- commit: `79ce55a`
- PR: [#107 Issue #83: sandbox_pages初期provenanceを登録](https://github.com/tj-999-comp/sandbox-pages/pull/107)
- 未解決事項: #84〜#87のdisabled no-op、手動E2E、有効化、新規record公開・Slack通知、運用引き継ぎ。
- 次アクション: #83のPRをCI確認し、マージ後に#84へ進む。

## GitHub Issue状況

確認日時（JST）: 2026-08-31 22:38
取得範囲: `tj-999-comp/sandbox-pages`の全Open Issue（Pull Requestを除外）13件。GitHub App tokenで取得し、#79・#89のsub-issues APIも確認した。#82はPR #106のマージにより`CLOSED / COMPLETED`となったため一覧から除外した。state reasonはOpen Issue全件でnull。

### 親子関係

```text
#79 [Epic] sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する [Open]
（GitHub sub-issues API上の子Issueなし。#83〜#87の本文にはParent: #79があるため、着手条件欄へ記録）

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
| 1 | 未設定 | [#79 [Epic] sandbox-pages自身の作業記録をPages公開・Slack通知対象へ接続する](https://github.com/tj-999-comp/sandbox-pages/issues/79) | Open（state_reason: null） | 親Epic。#83〜#87の本文は#79を親としているが、sub-issues API上の子登録は確認できない。 |
| 2 | 未設定 | [#83 [Bootstrap] sandbox_pages既存作業記録を初期公開状態としてprovenanceへ登録する](https://github.com/tj-999-comp/sandbox-pages/issues/83) | Open（state_reason: null） | 本作業。#80〜#82完了後。 |
| 3 | 未設定 | [#84 [E2E] sandbox_pagesのdisabled受入dry-runとno-opを検証する](https://github.com/tj-999-comp/sandbox-pages/issues/84) | Open（state_reason: null） | #83完了後。 |
| 4 | 未設定 | [#85 [Activation] sandbox_pagesを手動E2E可能な状態へ有効化する](https://github.com/tj-999-comp/sandbox-pages/issues/85) | Open（state_reason: null） | #84のレビューと明示承認後。 |
| 5 | 未設定 | [#86 [E2E] sandbox_pagesの新規作業記録をPages公開しSlack通知まで確認する](https://github.com/tj-999-comp/sandbox-pages/issues/86) | Open（state_reason: null） | #85完了後。 |
| 6 | 未設定 | [#87 [Operations] sandbox-pagesの公開・停止・再通知手順を引き継ぐ](https://github.com/tj-999-comp/sandbox-pages/issues/87) | Open（state_reason: null） | #86完了後。 |
| 7 | 未設定 | [#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open（state_reason: null） | 独立Epic。#90〜#94を追跡する。 |
| 8 | 未設定 | [#90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open（state_reason: null） | #89の子Issue。 |
| 9 | 未設定 | [#91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open（state_reason: null） | #89の子Issue。 |
| 10 | 未設定 | [#92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open（state_reason: null） | #89の子Issue。 |
| 11 | 未設定 | [#93 [Publish] 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | Open（state_reason: null） | #89の子Issue。 |
| 12 | 未設定 | [#94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open（state_reason: null） | #89の子Issue。 |
| 13 | 未設定 | [#102 [Operations] 作業記録のIssue状況を該当リポジトリ単位で全生成元へ統一する](https://github.com/tj-999-comp/sandbox-pages/issues/102) | Open（state_reason: null） | 独立。 |

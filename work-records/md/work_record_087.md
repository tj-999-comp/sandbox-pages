# 作業記録 087: Issue #93 固定対象の一括bootstrap経路を実装
作成日: 2026-09-06

## 概要

- 課題: GitHub Issue #93「過去作業記録をidempotentなbootstrapでPagesへ遡及反映する」。
- 目的: 固定source commitと対象basename集合を検証し、複数recordを一つの監査可能な反映単位としてPagesへ反映できる経路を追加する。
- 完了条件: dry-runで対象差分を確認でき、通知付きの一括apply、同一入力のno-op、drift・改名・削除防止、固定SHA・provenance・index整合を検証できる状態にする。

## 適用した役割

### Portfolio Planner

- 入力: Issue #93の完了・安全条件、#90の棚卸し対応表、#91のmetadata整備、#92のrecord navigation、既存の単一record受入workflow。
- 実施内容: 単一recordの通常publishと過去分一括反映を分離し、projectごとに固定SHAと対象basenameをdispatch入力として保持する構成へ分解した。bootstrap対象はsource側のpublish:trueかつ既存provenanceにないrecord集合に限定し、ユーザー要件に合わせて通知を既定有効化した。
- 成果物: `bootstrap_engine` と専用workflowの実装方針。#90時点の候補に加え、#91・#92で追加された`sandbox_pages`の`work_record_084`〜`086`も固定SHAの対象範囲へ含める。
- 検証結果: B_Stats_Siteはsource SHA `14468e72a58a00be29e18d132eda05ba0c1f01d7`で13件、sandbox_pagesは#92 merge SHA `0133974ecbeeada9ef0e8f0a52f9f397fe841fed`で15件の未公開対象を算出した。
- 未解決事項: 実GitHub Actions dispatchによるB・sandbox_pagesのPages反映と、Pages上の全体受入は後続確認が必要。
- 次工程への引き継ぎ: 固定対象を人間確認後、`bootstrap.yml`をprojectごとにdry-run→applyする。

### Portfolio Frontend Engineer

- 入力: `scripts/publish/apply_engine.py`、`scripts/publish/read_only_acceptance.py`、`scripts/publish/provenance.py`、`scripts/publish/index_generator.py`、#92の`record_navigation`。
- 実施内容: `scripts/publish/bootstrap_engine.py`を追加し、source registry、固定SHA、全source inventory、metadata、HTML安全性またはA所有renderer、既存provenance drift、index staleをapply前に検証するようにした。対象recordを同一一時ツリーへ反映し、既存recordのnavigationも更新して、一つのmanifestとindex更新を生成する。既存ファイルの削除・改名は行わず、通知指定時は対象recordごとにPages確認とSlack送信を行う。通常の`update`も通知対象へ拡張し、失敗時の再通知は単一・複数対象に対応させた。
- 成果物: `.github/workflows/bootstrap.yml`、bootstrap engine、engine/workflowのテスト。
- 検証結果: `source_html`と`a_rendered`の共通処理をfixtureで確認し、create/update通知対象と、create後の同一入力再実行が`no_op: true`、変更pathなしになることを確認した。
- 未解決事項: Actions上の実行結果、固定commitのPages URL、複数project一括の運用実績は未取得。
- 次工程への引き継ぎ: apply結果のcommit SHAとbootstrap manifestを#94の受入入力として記録する。

### Portfolio Reviewer

- 入力: Issue #93、bootstrap engine/workflow差分、既存publish workflow、provenance契約、テストfixture。
- 実施内容: 対象集合がpublish:trueかつ未公開recordに限定されること、source SHA・main SHA・既存provenanceを照合すること、create/update/bootstrapの通知経路と自動削除経路が分離されていること、dry-run artifactをapply入力へbindすることをレビューした。
- 成果物: 通知漏れを防ぐ通常publish・bootstrap・再通知Workflowの更新。実環境でのdispatch・Pages公開は実行前確認へ引き継いだ。
- 検証結果: 119 unittest、workflow YAML parse、`git diff --check`に合格した。実Workflow run `34037887369`はbootstrap dry-run開始前に`upload-artifact`の誤ったSHA参照で停止したため、正しい`upload-artifact` SHAへ修正して再実行する。sandbox_pagesの実データ相当一時cloneでは16件の`notify=true` dry-run、apply、再実行no-opを確認した。
- 未解決事項: 実運用のPages・provenance・公開URL確認は未実施。
- 次工程への引き継ぎ: 固定対象とpublication_idを承認してからworkflowを実行する。

## 主要な判断

- 判断: 通常の単一record受入とは別に、複数basenameを一つのbootstrap applyへ渡す。
- 理由: 過去分を個別commit・個別deployすると、同一監査commit、通知抑制、再実行no-opという要件を満たしにくいため。
- 判断: manifestの`operation`は既存provenance schemaの`create` / `update`を使用し、bootstrap識別はpublication_idとworkflowで行う。反映を伴う`create`、`update`、通知指定bootstrapはSlack通知対象とする。
- 理由: 既存manifestの互換性を保ちつつ、push・PR merge後に反映結果だけが通知されるようにするため。no-opとwithdrawは引き続き通知しない。
- 判断: 対象sourceのpublish:true集合と既存provenanceとの差分を対象集合と一致させる。
- 理由: 対象漏れ、publish:falseの誤公開、対象外recordの混入をapply前に停止するため。

## 最終結果

- 解決したこと: 固定source SHA・対象record集合・既存provenanceを検証し、複数recordを同一commitで反映するbootstrap engineとdry-run/apply/deploy workflowを追加した。通常publishのupdateとbootstrapも通知でき、drift時は停止し、既存公開物を削除せず、同一入力はno-opとして扱う。
- 変更ファイル: `.github/workflows/accept-source.yml`、`.github/workflows/bootstrap.yml`、`.github/workflows/notify-publication.yml`、`docs/SANDBOX_PAGES_OPERATIONS.md`、`scripts/publish/apply_engine.py`、`scripts/publish/bootstrap_engine.py`、`scripts/publish/slack_notification.py`、テスト、本作業記録一式。
- 検証結果: 119 unittest、Python AST、YAML、`git diff --check`に合格。sandbox_pagesの固定SHA相当ツリーで未公開15件を算出し、通知指定のdry-run/apply/no-opを確認した。
- ブランチ: `codex/093-bootstrap`
- commit: #93通知経路変更を含めてコミット予定
- PR: 未作成
- 未解決事項: B_Stats_Site 13件とsandbox_pages 16件の実workflow dispatch、Pages公開、manifest digest、Slack受信、既存新規record E2Eの確認が残っている。run `34037887369`の失敗はartifact action SHA修正で対応済み。
- 次アクション: PR反映後、対象SHA・basename・publication_id・`notify=true`を確認し、#93のbootstrap workflowを実行する。

## GitHub Issue状況

確認日時（JST）: 2026-09-06 22:56:02
取得範囲: `tj-999-comp/sandbox-pages` のOpen Issue全件（Pull Request除外、取得件数8・一覧行数8）

### 親子関係

```text
#89
├── #90
├── #91
├── #92
├── #93
└── #94

#118・#120は#89のsub-issuesではない
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P2 | [#89 [Epic] 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | Open（state reason: null） | 親Issue。#90〜#94の完了後に全体完了を判定する。 |
| 2 | P2 | [#90 [Inventory] 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | Open（state reason: null） | #89の子。対応表を#93へ引き継ぐ。 |
| 3 | P2 | [#91 [Migration] 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | Open（state reason: null） | #89の子。コミット`4079439`はmain反映済み。 |
| 4 | P1 | [#92 [UI/Index] 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | Open（state reason: null） | #89の子。PR #119はmerge済み。 |
| 5 | P1 | [#93 [Publish] 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | Open（state reason: null） | #89の子。本作業で通知付きbootstrap経路を整備し、実反映を残課題とする。 |
| 6 | P0 | [#94 [Verify/Operations] 過去分公開とrecord間リンクの全体受入・運用引き継ぎを行う](https://github.com/tj-999-comp/sandbox-pages/issues/94) | Open（state reason: null） | #89の子。#90〜#93完了後に全体受入を行う。 |
| 7 | 未設定 | [#118 自分専用のスポーツ内容確認サイト用リポジトリを作成する](https://github.com/tj-999-comp/sandbox-pages/issues/118) | Open（state reason: null） | #89のsub-issueではない。別project準備の課題。 |
| 8 | 未設定 | [#120 [受入] スポーツサイト生成元リポジトリを公開側へ登録する](https://github.com/tj-999-comp/sandbox-pages/issues/120) | Open（state reason: null） | #89のsub-issueではない。別project受入の課題。 |

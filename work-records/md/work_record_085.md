# 作業記録 085: Issue #91 過去作業記録のmetadata・命名・HTMLを公開契約へ整備
作成日: 2026-09-06

## 概要

- 課題: GitHub Issue #91「過去作業記録のmetadata・命名・HTMLを公開契約へ整備する」。
- 目的: Issue #90の対応表を入力に、登録済み生成元の公開候補がmetadata、共通命名、HTML生成方式、安全性の契約を満たすことを確認する。
- 完了条件: 公開候補の対応関係、publish可否、採番、HTML方式、除外理由を固定し、#93のbootstrap/backfillへ再利用できる状態にする。公開先の未manifestファイルは先行配置しない。

## 適用した役割

### Portfolio Planner

- 入力: Issue #91の完了条件、親Issue #89、後続Issue #92・#93・#94、Issue #90の対応表、`config/sources.json`。
- 実施内容: #91をsource契約の整備・検証、#92をindex/link実装、#93をPages反映、#94を全体受入として分離した。#91の対象を、公開先への反映前に検証できる候補へ限定した。
- 成果物: B_Stats_Siteの011–022、sandbox_pagesの071–073・075–083を公開候補として確定し、tech_article_nortificationのpublish:false 15件とB_Stats_Siteのwithdraw済み027を除外対象として整理した。
- 検証結果: 登録済み5projectのsource SHA、HTML方式、公開先、既存provenanceを対応表と照合した。
- 未解決事項: #93の固定SHA・provenance付きbootstrap/backfillは後続工程。
- 次工程への引き継ぎ: #92へ既存公開URLと採番済みbasename、#93へ公開候補とsource SHA・publish判定、#94へ検証結果を渡す。

### Portfolio Frontend Engineer

- 入力: 5projectのsource registry、B_Stats_Siteの固定SHA `14468e72a58a00be29e18d132eda05ba0c1f01d7`、sandbox_pagesの作業記録source、A側renderer・source_html安全validator。
- 実施内容: Bの公開候補12件についてmetadataをschema検証し、A所有の`a_rendered` rendererで同一入力からHTMLを2回生成した。sandbox_pages候補12件について既存のMarkdown・metadata・source HTMLを同名で確認した。#90の作業記録084に残っていた公開先外相対リンクを、意味を変えない明示HTTPSリンクへ修正した。
- 成果物: `work_record_085`のMarkdown、metadata、生成HTML。公開先のMarkdown・HTML・provenance・indexは#93/#92の責務として変更していない。
- 検証結果: B候補12件のmetadataと決定的HTML生成に合格。sandbox_pagesのsource_html全83件を安全validatorへ通し、候補12件のMarkdown・metadata・HTML対応を確認した。
- 未解決事項: tech_article_nortificationの15件はmetadataの`publish: false`を維持し、内容判断なしに公開しない。Bの027はwithdraw provenanceを維持する。
- 次工程への引き継ぎ: #93ではregistryの固定source SHA・許可path・digestから受入payloadを再構成し、通知なしのbackfillとして実行する。

## 主要な判断

- 判断: #91では公開先へ未manifestの過去recordを配置せず、公開候補を#93のbootstrap入力として扱う。
- 理由: #93の完了条件が、公開先Markdown・HTML・index・manifestを同一監査可能commitへ反映することを定めているため。先行配置するとprovenance driftとindex不整合を生む。
- 判断: B_Stats_Siteの027は公開候補から除外し、source metadataの`publish: true`を変更しない。
- 理由: 既存のwithdraw provenanceが公開除外を記録しており、source側を改変せずに公開側の履歴と安全条件を維持するため。
- 判断: 番号なし補助文書、tech_article_nortificationのpublish:false recordは作業記録公開候補へ含めない。
- 理由: source registryのignored/support契約とmetadataの明示的な公開可否を優先し、推測による再採番・公開を行わないため。

## 最終結果

- 解決したこと: 公開候補24件のmetadata・命名・HTML方式・安全性を確認し、Bのa_rendered候補はA側rendererで再現可能にした。非公開15件、withdraw済み1件、補助文書を公開候補から分離した。
- 変更ファイル: `config/sources.json`、`projects/README.md`、`docs/SANDBOX_PAGES_OPERATIONS.md`、`tests/test_source_registry.py`、`work-records/md/work_record_084.md`、`work-records/metadata/work_record_084.yml`、`work-records/md/work_record_085.md`、`work-records/metadata/work_record_085.yml`、`work-records/work_record_084.html`、`work-records/work_record_085.html`。
- 検証結果: B候補12件のmetadata/schema検証とa_rendered決定性検証、sandbox_pages source_html全83件の安全性検証、Markdown・metadata・HTML対応確認に合格。作業記録HTMLは1280px、900px、640px、320pxで実ブラウザ確認する。
- 未解決事項: #91の範囲に重大な未解決事項はない。未公開候補のPages反映は#93、record間リンクは#92、全体受入は#94で実施する。
- 次アクション: #93で固定SHAと候補basenameを指定した通知なしbackfillを実行し、同一入力のno-opとprovenance/indexの一致を確認する。

## GitHub Issue状況

確認日時（JST）: 2026-09-06 21:01:15
取得範囲: `tj-999-comp/sandbox-pages` のOpen Issue全件（Pull Request除外）

### 親子関係

```text
#89
├── #90
├── #91
├── #92
├── #93
└── #94
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#94 Verify/Operations 過去分公開とrecord間リンクの全体受入・運用引き継ぎ](https://github.com/tj-999-comp/sandbox-pages/issues/94) | 未完了（state reason: null） | #89の子。#92・#93完了後に全体受入を行う。 |
| 2 | P1 | [#93 Publish 過去作業記録をidempotentなbootstrapでPagesへ遡及反映する](https://github.com/tj-999-comp/sandbox-pages/issues/93) | 未完了（state reason: null） | #89の子。#90の対応表と#91のmetadata整備を入力にする。 |
| 3 | P1 | [#92 UI/Index 作業記録ページの構成とrecord間リンクを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/92) | 未完了（state reason: null） | #89の子。公開済み・backfill対象のprovenanceとmetadataを入力にする。 |
| 4 | P1 | [#91 Migration 過去作業記録のmetadata・命名・HTMLを公開契約へ整備する](https://github.com/tj-999-comp/sandbox-pages/issues/91) | 未完了（state reason: null） | #89の子。本作業でsource契約の検証を完了し、完了コメント後に状態確認する。 |
| 5 | P2 | [#90 Inventory 各生成元の過去作業記録を棚卸しし公開対応表を確定する](https://github.com/tj-999-comp/sandbox-pages/issues/90) | 未完了（state reason: null） | #89の子。完了済み成果物を#91〜#94へ引き継ぐ。 |
| 6 | P2 | [#89 Epic 過去作業記録の遡及公開と作業記録間リンクを整備する](https://github.com/tj-999-comp/sandbox-pages/issues/89) | 未完了（state reason: null） | 親Issue。#90〜#94の完了後に全体完了を判定する。 |

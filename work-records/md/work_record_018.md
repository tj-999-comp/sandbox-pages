# 作業記録 018: Issuesからwork-recordsへの移行と次セッションへの引き継ぎ
作成日: 2026-08-18

## 概要

- 課題: ローカル記録が`Issues/Issue_###.md`に残っており、複数プロジェクトで採用する`work_record_###`命名とHTML生成方式に一致していなかった。
- 目的: 既存17件を内容と番号を維持して`work-records/`へ移し、Markdown、HTML、デザイン、生成・検証手順を次のセッションで継続できる状態にする。
- 完了条件: `work_record_001`から`work_record_018`までのMarkdownとHTMLが対応し、現在の運用文書に旧パス参照がなく、再生成検証とPC・スマートフォンのブラウザ確認に合格している。

## 対象と入力

- 公開リポジトリ: `tj-999-comp/sandbox-pages`
- 作業開始時の基準commit: `6900060cf3835777daf72e7870334a2fb485e47b`
- 作業ブランチ: `codex/018-migrate-work-records`
- 既存記録: `work_record_001.md`から`work_record_017.md`
- 旧テンプレート: `Issue_Template.md`（移行後は`work-records/README.md`へ統合）
- デザイン入力: ユーザー指定の作業記録HTMLデザインガイドと共通CSS

## 適用した役割

### Portfolio Frontend Engineer

- 入力: 既存17件のMarkdown、旧テンプレート、リポジトリ内の旧パス参照、Bの既存converterとvalidator、共通公開契約。
- 実施内容: ファイル対応表とGit履歴上の作成日を確認し、ディレクトリ・命名移行、運用文書、converter、validator、全18件のHTML生成を実施した。
- 成果物: `AGENTS.md`、`README.md`、`work-records/`、`scripts/dev/`。
- 検証結果: 18件のファイル対応、再生成差分、相対リンク、安全でないURL schemeとリポジトリ外パスの拒否、Python構文、空白エラーを確認した。
- 未解決事項: 本移行作業にはなし。A側の自動公開機構は次セッションの対象。
- 次工程への引き継ぎ: UI Designerの構造確認、Testerの実ブラウザ確認、Reviewerの差分確認へ引き継いだ。

### Portfolio UI Designer

- 入力: ユーザー指定のデザインガイドとCSS、既存17件の見出し構造、Bの既存作業記録HTML。
- 実施内容: 共通HTML骨格、ナビゲーション、セクション対応、旧テンプレートの扱い、代表確認対象を整理した。
- 成果物: サイトトップ、運用ルール、デザインガイド、Markdown原本へ移動できるHTML構造と、既存内容を欠落させない変換方針。
- 検証結果: `Issue_Template.md`を番号付き記録にせず`work-records/README.md`へ統合すること、指定CSSの実値に合わせて最大幅を`1080px`とすることを確認した。
- 未解決事項: なし。
- 次工程への引き継ぎ: Frontend EngineerへHTML骨格とセクション表示要件を引き継いだ。

### Portfolio Performance & Accessibility Tester

- 入力: 全18件の生成HTML、指定CSS、1280×900pxと320×800pxのブラウザ条件。
- 実施内容: 横overflow、console error、page error、failed request、見出し階層、`aria-labelledby`、ローカルリンク、キーボードfocusを検証した。
- 成果物: 18件×2 viewportの計36条件のPlaywrightレポートと、代表ページの4 viewportスクリーンショット。
- 検証結果: 全36条件で横overflowと実行時エラーは0件、各ページのH1は1件、見出し飛びとリンク切れは0件だった。320pxで全ナビゲーションリンクへTab移動でき、標準focus outlineを確認した。
- 未解決事項: 実スクリーンリーダーによる読み上げ確認は未実施。今回の静的記録移行を妨げる問題はなし。
- 次工程への引き継ぎ: Reviewerへブラウザ証跡と静的検証結果を引き継いだ。

### Portfolio Reviewer

- 入力: `origin/main`との差分、ユーザー要件、生成・検証結果、ブラウザ証跡。
- 実施内容: 移行範囲、命名、既存内容の保持、運用ルール、生成安全性、無関係な変更、作業記録018のテンプレート適合を確認した。
- 成果物: 初回レビューで不足していた本「適用した役割」節の追加指摘と、反映後の最終レビュー結果。
- 検証結果: 重大0件、中0件、軽微0件で、差し戻し不要と判定した。
- 未解決事項: なし。
- 次工程への引き継ぎ: ローカル移行作業は完了。次セッションではA側受入基盤のdry-run実装から開始する。

## 実施内容

- `Issues/`を`work-records/`へ改名した。
- 番号付きMarkdownを`work-records/md/work_record_###.md`へ移した。
- Git履歴の初回追加日を各記録の作成日として追加し、内容に対応するH1を追加した。
- 旧テンプレートを`work-records/README.md`の運用ルールと作業記録テンプレートへ統合した。
- `work-records/design.md`と`work-records/work_record.css`を追加した。
- Python標準ライブラリだけを使うHTML converterとvalidatorを追加した。
- 本作業を`work_record_018`として記録対象へ追加した。

## 主要な判断

- 判断: ユーザーが示した`work_record_##`は番号のプレースホルダーと解釈し、共通公開契約と既存Bに合わせて3桁の`work_record_###`を使う。
- 理由: `B_Stats_Site`の既存`work_record_001`から`010`と公開URLを維持し、プロジェクト間で同じ規則を使うため。
- 判断: 旧`Issue_Template.md`へ番号を割り当てず、`work-records/README.md`へ統合する。
- 理由: 番号付きMarkdownだけをHTML生成対象とし、`work-records/`直下のMarkdownを`README.md`と`design.md`だけに保つため。
- 判断: デザインガイドの最大幅は指定CSSの実値に合わせて`1080px`とする。
- 理由: 入力ガイドの`1280px`と指定CSSの`.shell`最大`1080px`が競合しており、CSS統一の明示指示を優先したため。

## 自動公開機構の現在地

- 共通公開契約と命名規則は`projects/README.md`に確定済み。
- `B_Stats_Site`の既存公開ファイルと同期基準commitは確認済み。
- A側のsource登録、metadata schema、validator、renderer、provenance manifest、index、受入workflowは未実装。
- Aは現在も`main`ルートを公開するlegacy GitHub Pages構成である。
- BからAへの公開要求workflow、Pages公開後のSlack通知、Secrets設定は未実装。
- 本作業で追加するconverterとvalidatorは、このリポジトリ自身の作業記録をローカル生成・検証するためのものであり、将来のA受入workflowそのものではない。

## 次のセッションの開始地点

最初にA側の受入基盤を、公開状態を変えないdry-runとして実装する。

1. A所有のsource登録を作成し、`B_Stats_Site`を`enabled: false`で登録する。
2. metadata schemaと受入validatorを作成する。
3. `B_Stats_Site`の既存`001`から`010`を初期provenance manifestへ登録する。
4. 既存公開ファイルを変えないno-op同期テストを追加する。
5. その後に`a_rendered` renderer、Bのmetadataと親リンク修正、Pages workflow、index、手動dispatch、Slack通知の順で進める。

この段階では、push triggerを有効化せず、Slack Secretやdispatch tokenも作成しない。

## 最終結果

- 解決したこと: ローカル作業記録の命名、配置、HTMLデザイン、生成・検証方法を`work-records/`へ統一した。
- 変更ファイル: `AGENTS.md`、`README.md`、`work-records/`、`scripts/dev/`。
- 検証結果: converterの`--check`、18件のファイル名・H1・日付・対応HTML・再生成内容・ローカルリンクを確認するvalidator、`git diff --check`に合格した。Playwrightで全18件を1280×900pxと320×800pxの計36条件で確認し、横overflow、console error、page error、failed request、見出し階層、リンク切れは0件だった。320pxの`work_record_018.html`で5リンクをTab移動し、すべてにブラウザ標準のfocus outlineが表示された。
- 作業ブランチ: `codex/018-migrate-work-records`
- コミット: 未実施。
- PR: 未作成。
- PRレビュー・CI: Portfolio Reviewerのローカル事前レビューは重大0件、中0件、軽微0件で完了した。PRとCIはローカル限定作業のため未実施。
- 未解決事項: 自動公開機構は「次のセッションの開始地点」に記載した順で未実装。
- 次アクション: 本記録の検証結果を確認してから、A側受入基盤のdry-run実装を開始する。

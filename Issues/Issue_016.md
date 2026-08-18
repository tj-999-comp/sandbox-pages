## 概要
- 課題: 複数の生成元リポジトリから作業記録をGitHub Pagesへ安全に公開する共通ルールが未確定だった。
- 目的: `sandbox-pages`を公開判断と受入処理の正本とし、既存ファイル名・URLを維持した公開契約を`projects/README.md`へ記録する。
- 完了条件: A/Bの現状と最新commitを照合し、責務、所有境界、metadata、受入条件、認証、Pages、Slack、複数生成元の追加手順を矛盾なく定義し、重大なレビュー指摘が0件であること。

## 適用した役割
### Portfolio Frontend Engineer
- 入力: ユーザー提供の調査記録、Repository A/Bの実体、既存の作業記録運用ルール、GitHub公式仕様。
- 実施内容: A/BのGit状態とファイルを再照合し、公開ルールを`projects/README.md`へ再構成した。
- 成果物: 共通公開契約、B_Stats_Siteの登録例と同期baseline、段階導入手順。
- 検証結果: Aに存在するB_Stats_Site公開ファイルがBの`main` commit `0fe9932`とbyte単位で一致し、Bにのみ補助HTMLが2件あることを確認した。Markdown差分の構文・空白検査に合格した。
- 未解決事項: 公開workflow、metadata、validator、provenance manifest、index、Pages移行、Slack通知は今後の実装対象。
- 次工程への引き継ぎ: READMEの導入順に従い、まずA所有のsource登録と受入基盤を実装する。

### Portfolio Reviewer
- 入力: 更新後の`projects/README.md`、ユーザー要件、A/Bの最新状態。
- 実施内容: Aの最終判断が権限設計で担保されること、複数生成元、HTML安全性、競合、drift、通知相関、既存URL非回帰をレビューした。
- 成果物: BへAのContents write tokenを渡さず、A側が固定commitを取得・検証する方式への変更、親ディレクトリリンクと生成元コード実行リスクへの対策。
- 検証結果: 重大0件、中0件、軽微0件で合格。A-side pull、権限分離、source SHA単調性、HTML/CSS allowlist、deploy SHA固定、複数Bの競合制御、baselineの正確さを確認した。
- 未解決事項: 今回の文書化範囲に重大な未解決事項はない。
- 次工程への引き継ぎ: 対象2ファイルだけをcommitし、最新のremote `main`へpushする。

## 主要な判断
- 判断: 共通ルールは`projects/README.md`へ置き、`projects/B_Stats_Site/README.md`はB由来の運用ルールとして維持する。
- 理由: A管理ファイルとB管理ファイルの境界を保ち、次回同期で共通ルールが上書きされることを防ぐため。
- 判断: 標準方式をBからAへの直接pushではなく、Bが`workflow_dispatch`で公開要求し、Aが固定commitを取得する方式へ変更する。
- 理由: Fine-grained PATのContents writeはディレクトリ単位に限定できず、複数Bへ配布するとA全体の書換え権限を渡すことになるため。
- 判断: metadataからHTML・Markdown・公開先パスを自由指定せず、ベース名とA所有のsource登録から導出する。
- 理由: 重複情報のdriftとpath traversalを防ぐため。
- 判断: Aの権限付きjobではBのscriptや任意commandを実行しない。
- 理由: 生成元コードによるAのwrite tokenやSlack Secretの利用を防ぐため。
- 判断: `../README.md`参照は自動publish前にgenerator側で解消する。
- 理由: BとAでリンク先の意味が変わり、project公開ルート外を参照するため。

## 最終結果
- 解決したこと: Aを正本とする複数生成元向けの公開契約、権限境界、安全性、来歴、競合処理、導入順を明文化した。
- 変更ファイル: `projects/README.md`、`Issues/Issue_016.md`。
- 検証結果: `git diff --check`合格。READMEのコードフェンス、Git差分、A/B baseline、公式仕様を確認した。表示コードを変更していないためブラウザ確認は対象外。
- 未解決事項: 今回の文書化範囲は重大指摘0件。公開機構自体は未実装であり、README記載の段階導入が次の課題となる。
- 次アクション: 対象2ファイルだけをcommitし、最新のremote `main`へpushする。

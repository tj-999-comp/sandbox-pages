# 作業記録 092: 全リポジトリの作業記録自動公開とSlack通知の標準化
作成日: 2026-09-08

## 概要
- 課題: sport-portalでmainへの作業記録Push後にSlack通知が届かなかったため、B_Stats_Siteを基準に全生成元リポジトリの公開フローを確認・統一する。
- 目的: 作業記録の自動公開、複数記録の同時Push、Pages公開成功後のSlack通知、手動再公開を全対象で同じ契約にする。
- 完了条件: 全対象リポジトリと公開テンプレートを修正し、CI・Pagesデプロイ・Slack通知を含む実動確認を成功させる。

## 適用した役割
### Portfolio Frontend Engineer
- 入力: B_Stats_Siteの既存公開workflow、登録済みsourceリポジトリ、sandbox-pagesの受入workflowとテンプレート。
- 実施内容: tech_article_nortification、NBA_Draft_DB、query_learning_BB、sport-portalのrequest-publish workflowを標準化した。main Pushの自動公開、複数作業記録の抽出、固定SHAと対象basenameによる手動再公開、source側validator、sandbox-pagesへのdispatchを統一した。sandbox-pagesの受入workflowへ公開run名を追加し、Pages側の同時実行キューで一時キャンセルされた要求を再試行できるようにした。source側の待機ジョブを60分、再試行を最大20回・15秒間隔へ調整し、公開テンプレートにも反映した。
- 成果物: 4 sourceリポジトリのworkflow・validator/helper・READMEまたは運用文書、sandbox-pagesの受入workflow・公開テンプレート・標準文書。
- 検証結果: 各sourceの作業記録validator、workflow/templateのYAML構文、sandbox-pagesの既存テスト121件に合格した。
- 未解決事項: なし。
- 次工程への引き継ぎ: Reviewerによる差分・CI確認後、各PRをマージし、PagesとSlackの実動結果を確認する。

### Portfolio Reviewer
- 入力: 各リポジトリのbaseとの差分、CI結果、Pages受入run、Slack通知jobの実行結果。
- 実施内容: B_Stats_Siteとの要件適合、複数対象処理、固定SHA検証、テンプレート反映、キューキャンセル時の再試行、無関係な変更の混入を確認した。初回の同時実行テストでsource側5分上限による中断を検出し、待機時間修正後に再レビューした。
- 成果物: 修正PRのレビュー・CI確認と、4 sourceリポジトリ同時実行の最終判定。
- 検証結果: 最終E2Eで4件すべてが、source検証、公開要求、固定SHA適用、Pagesデプロイ、Slack通知の全job successとなった。
- 未解決事項: なし。
- 次工程への引き継ぎ: マージ済みのmainと本作業記録を公開する。

## 主要な判断
- 判断: 公開の正本はB_Stats_Siteの構成に合わせ、source側は検証済みの固定SHAをsandbox-pagesへ渡し、sandbox-pages側で適用・Pagesデプロイ・Slack通知を完結させる。
- 理由: Push時点のsource内容を固定し、検証した内容と公開した内容のずれを防ぎながら、手動再公開と複数記録を同じ入口で扱えるため。
- 判断: sandbox-pagesのworkflow-level concurrencyは維持し、キャンセルされた公開要求をsource側で再試行する。
- 理由: Pagesのmain更新と固定SHAデプロイを直列化しつつ、同時Push時に後続要求が失われないようにするため。初回テストで5分上限が不足すると判明したため、待機上限と再試行回数を拡張した。

## 最終結果
- 解決したこと: 全4 sourceリポジトリでmain Pushによる自動公開、複数作業記録対応、手動再公開、Pages公開後Slack通知を統一した。公開テンプレートも同じ仕様へ更新した。
- 変更ファイル: `tech_article_nortification/.github/workflows/request-publish.yml`、`NBA_Draft_DB/.github/workflows/request-publish.yml`、`query_learning_BB/.github/workflows/request-publish.yml`、`sport-portal/.github/workflows/request-publish.yml`、各sourceのvalidator/helper・README/運用文書、`sandbox-pages/.github/workflows/accept-source.yml`、`sandbox-pages/docs/templates/request-publish.yml`、`sandbox-pages/projects/README.md`、`sandbox-pages/docs/PORTFOLIO_STANDARD.md`。
- 検証結果: 4 source validator、workflow/template YAML構文、sandbox-pages既存テスト121件に合格。最終E2Eはtech、query、NBA、sportの全公開runでPagesデプロイとSlack通知を含めsuccess。
- 作業ブランチ: 各リポジトリの`codex/*`課題ブランチ。
- コミット: 各PRのマージコミットとしてmainへ反映。
- PR: [tech_article_nortification #29](https://github.com/tj-999-comp/tech_article_nortification/pull/29)、[NBA_Draft_DB #28](https://github.com/tj-999-comp/NBA_Draft_DB/pull/28)、[query_learning_BB #94](https://github.com/tj-999-comp/query_learning_BB/pull/94)、[sport-portal #18](https://github.com/tj-999-comp/sport-portal/pull/18)、[sandbox-pages #136](https://github.com/tj-999-comp/sandbox-pages/pull/136)。すべてマージ済み。
- PRレビュー・CI: 各PRのCI通過を確認し、初回同時実行テストで検出したsource側待機上限を修正後、再レビュー・再検証した。古い競合PR tech #28、sandbox-pages #135は後続PRへ置き換えたためcloseした。
- 未解決事項: なし。GitHub ActionsにはNode.js 20および`app-id`の非推奨警告が表示されるが、今回の実行結果には影響していない。
- 次アクション: 今後のsource追加時は`sandbox-pages/docs/templates/request-publish.yml`を基準にworkflowを導入する。

## GitHub Issue状況
確認日時（JST）: 2026-09-08 13:25
取得範囲: `tj-999-comp/sandbox-pages`のOpen Issue全件。Pull Requestは除外。
取得件数: 0件（一覧行数: 0行）

### 親子関係
```text
親子関係なし
```

### 優先順位順の未完了一覧
| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |

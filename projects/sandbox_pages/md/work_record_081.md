# 作業記録 081: query_learning_BBの手動公開E2E完了
作成日: 2026-09-01

## 概要

- 課題: `query_learning_BB` の公開側source registry有効化後、固定SHA受入からPages公開までの経路を確認する。
- 目的: 生成元の作業記録が公開側リポジトリへ反映され、公開URLとprovenanceが作成されることを確認する。
- 対象範囲: この `sandbox-pages` リポジトリに反映されたファイル、provenance、公開インデックスの変更のみを記録する。

## 実施内容

- `query_learning_BB` の `work_record_001` を固定元SHA `a0662fc768181a736188c8fd35c7aefd2727ded0` から受け入れた。
- `projects/query_learning_BB/md/work_record_001.md` と `projects/query_learning_BB/work_record_001.html` を公開側へ追加した。
- `provenance/query_learning_BB/accept-33478348608-1-query_learning_BB-work_record_001.json` を追加した。
- 公開インデックスを受入結果に合わせて更新した。

## 検証結果

- 公開側受入run `33478348608` は、固定元SHA検証、A-03受入、apply、Pages artifact生成、Pages deploy、公開URL確認、Slack通知まで成功した。
- provenanceの `publication_id` は `accept-33478348608-1-query_learning_BB-work_record_001` で、公開URLは `/sandbox-pages/projects/query_learning_BB/work_record_001.html` となった。
- 同一対象の再実行run `33478494579` は検証とapplyが成功し、追加の公開コミットを作らず、Pages deployとSlack通知はスキップされた。
- 公開HTMLを実URLから取得し、作業記録本文が表示されることを確認した。

## 対象外

- 認証情報、Secret、token、生成元リポジトリ内の変更はこの記録に保存しない。

## 関連リンク

- 受入・公開run: https://github.com/tj-999-comp/sandbox-pages/actions/runs/33478348608
- 冪等性確認run: https://github.com/tj-999-comp/sandbox-pages/actions/runs/33478494579
- 公開ページ: https://tj-999-comp.github.io/sandbox-pages/projects/query_learning_BB/work_record_001.html

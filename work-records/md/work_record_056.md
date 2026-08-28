# 作業記録 056: Issue #13 a_rendered用の決定的rendererを実装
作成日: 2026-08-28

## 概要

- 課題: GitHub Issue #13「[Renderer] a_rendered用の決定的rendererを実装する」。
- 目的: Markdownとmetadataを入力として、公開リポジトリAが同じHTMLを再現できる`a_rendered`経路を実装する。
- 完了条件: A所有rendererがmetadataを正本として安全なHTMLを生成し、read-only acceptanceとapplyが生成元HTMLなしで動作し、テストで決定性・安全性・provenanceを確認できること。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: `projects/README.md`、`config/sources.json`、既存のacceptance/apply engine、`a_rendered`の公開契約。
- 実施内容: `scripts/publish/rendered_renderer.py`を追加し、metadata由来のタイトル・日付・project ID・タグとMarkdown本文から固定テンプレートを生成するようにした。raw HTMLはエスケープし、HTTPS・fragment・正規化された相対リンクだけを許可した。read-only acceptanceでrenderer検証を行い、apply時に`work_record_###.html`を生成して公開ファイルへ加えるようにした。
- 成果物: A所有の決定的renderer、`a_rendered` acceptance/apply接続、renderer・acceptance・applyのテスト、導入状況の文書更新。
- 検証結果: renderer単体、`a_rendered` dry-run、`a_rendered` applyとprovenance生成を確認した。全85ユニットテスト、index・作業記録・filename検証、`git diff --check`に合格した。
- 未解決事項: GitHub API接続不能のためIssueの最新状態は取得できていない。生成元移行後の実GitHub Actions手動E2Eは未実施。
- 次工程への引き継ぎ: 生成元を`work-records/md/`と`work-records/metadata/`へ移行した後、disabled dry-run、手動apply、Pages公開URLを確認する。

### Portfolio Reviewer

- 入力: renderer実装、受入・apply接続、専用fixture、テスト結果。
- 実施内容: metadataがMarkdown見出しや生成元HTMLに依存しないこと、raw HTMLと危険なリンクが公開HTMLへ混入しないこと、`a_rendered`のsource inventoryがMarkdown・metadataだけで構成され、apply時にHTMLだけが生成されることを差分とテストで確認した。
- 成果物: renderer経路の事前レビュー結果。
- 検証結果: 重大0件。生成HTMLは固定テンプレートで、同じ入力に対して同一出力となることを確認した。
- 未解決事項: GitHub上の外部レビューと実workflowの確認は未実施。
- 次工程への引き継ぎ: commit後にremote差分を確認し、PR作成は明示許可後に行う。

## 主要な判断

- 判断: metadataをタイトル・日付・project ID・タグの正本とし、Markdown先頭のH1と作成日表示は本文から除外する。
- 理由: 公開一覧と個別ページのメタデータを一致させ、生成元Markdownの表記揺れで公開結果が変わらないようにするため。
- 判断: `a_rendered`のsource inventoryにはHTMLを含めず、apply時にA側で生成する。
- 理由: 生成元へHTML・CSS・designを要求せず、A所有のrendererを経由した成果物だけを公開する契約に合わせるため。
- 判断: rendererのMarkdown対応範囲は既存作業記録で使われる見出し、段落、リスト、表、コードブロック、引用、リンク、強調表現に限定する。
- 理由: 変換結果を監査しやすく保ち、任意HTMLや実行可能な機能を受け入れないため。
- 判断: 出力stylesheetはA所有の`../progress-index.css`を参照する。
- 理由: `a_rendered`生成元に表示用ファイルを複製させず、公開先で共通のA所有スタイルを利用するため。

## 最終結果

- 解決したこと: `a_rendered-work-record-v1`向けに、Markdownとmetadataから同じHTMLを生成するrendererを追加した。read-only acceptanceはrenderer検証を行い、applyは同名HTMLを生成してprovenanceの`published_files`へ記録する。
- 変更ファイル: `scripts/publish/rendered_renderer.py`、`scripts/publish/read_only_acceptance.py`、`scripts/publish/apply_engine.py`、`projects/README.md`、`tests/test_rendered_renderer.py`、`tests/test_read_only_acceptance.py`、`tests/test_apply_engine.py`、`work-records/md/work_record_056.md`、`work-records/work_record_056.html`。
- 検証結果: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'`（85件成功）、`python3 -m scripts.publish.index_generator --check`、`python3 scripts/dev/convert_work_records_to_html.py --check`、`python3 scripts/dev/validate_work_record_filenames.py`、`git diff --check`に合格した。
- ブラウザ確認: Chromiumで作業記録HTMLを1280×900、900×900、640×900、320×800で確認し、全viewportでHTTP 200、横overflowなし、console/page errorなし、failed requestなし。証跡: `/private/tmp/playwright-browser-verify/2026-08-28T02-20-47-222Z/report.json`。
- 未解決事項: GitHub APIがKeychain認証失敗と接続エラーで利用できず、Issue #13の最新state・親子関係・Open Issue一覧は未確認。生成元移行後の実workflow、Pages、公開URL、SlackのE2Eも未確認。
- 次アクション: `tech_article_nortification`側の入力移行後に受入を実行し、GitHub接続回復後にIssue状態とPR・CIを確認する。

## GitHub Issue状況

確認日時（JST）: 2026-08-28 11:17
取得範囲: `tj-999-comp/sandbox-pages`のIssue #13、および関連IssueのGitHub API取得を試行したが、GitHub App Keychain項目を読めずAPIへ接続できなかった。

### 親子関係

```text
取得不可（GitHub API接続エラーのため推測記載なし）
```

### 優先順位順の未完了一覧

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | 取得不可 | [#13 a_rendered用の決定的rendererを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/13) | 取得不可 | Issue本文・最新状態をGitHub APIで再取得する必要がある |

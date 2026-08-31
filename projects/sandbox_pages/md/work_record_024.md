# 作業記録 024: Issue #9 HTML・CSS・URL安全validator
作成日: 2026-08-20

## 概要

- 課題: AI生成HTMLを同一GitHub Pages originへ受け入れる前に、A側でHTML・CSS・URL・ローカル依存をallowlist検証する。
- 目的: 作業リポジトリ（B）の自己検証だけに依存せず、公開リポジトリ（A）が危険な実行機能、外部依存、project外参照、依存不足を独立して拒否できるようにする。
- 完了条件: Issue #9に記載された危険HTML要素・属性、危険URL、外部CSS、CSS実行構文、依存不足、`../README.md`を拒否するfixtureがあり、現行の安全な作業記録HTML/CSSを受け入れられること。

## 適用した役割

### Portfolio Frontend Engineer

- 入力: 公開リポジトリ（A）のIssue #9、`projects/README.md`、Issue #8の`acceptance_files`、現行作業記録HTMLと`work_record.css`。
- 実施内容: Python標準ライブラリの`HTMLParser`で要素・属性・構造を検証し、`script`、`iframe`、`object`、`embed`、`form`、`base`、meta refresh、inline event handler、未知属性を拒否するvalidatorを追加した。URLはfragment、project内相対URL、許可HTTPSへ限定し、`..`、絶対path、protocol-relative、危険scheme、認証情報付きHTTPSを拒否するようにした。CSSは`@media`と登録済みpropertyだけを許可し、`@import`、外部・protocol-relative・危険な`url()`、`expression`、`behavior`、`-moz-binding`を拒否するようにした。
- 成果物: `scripts/publish/content_safety.py`、`tests/test_content_safety.py`、A#9の責務・拒否方針を追記した`projects/README.md`。
- 検証結果: 現行`work_record_023.html`とCSS、正常系fixture、危険要素・属性、危険URL、依存不足、CSS攻撃構文、source tree統合のテストが成功した。
- 未解決事項: Aの受入workflowから固定commitを取得して全HTMLへ適用する処理、provenance、Pages反映は後続Issueの対象である。
- 次工程への引き継ぎ: A#10のprovenance manifestで、A#8のファイルdigestとA#9の検証済み依存を記録する。A#17以降でdry-run workflowへ接続する。

### Portfolio Reviewer

- 入力: Issue #9の完了条件、HTML/CSS allowlist、URL解決処理、fixtureテスト、公開契約。
- 実施内容: B側の自己検証とA側の最終受入を分離し、A側が固定commit上のHTML/CSSを再解析する設計、`../README.md`を含むproject外参照拒否、support fileと同名Markdownの依存確認をレビューした。
- 成果物: Aが公開可否の最終判断を保持する責務分担の明文化。
- 検証結果: 重大・中・軽微の未解決事項はない。A#9単体の安全検証として範囲は妥当である。
- 未解決事項: 実際のGitHub Actions dispatch、固定SHA checkout、Pages deployを通したE2Eは未実施である。
- 次工程への引き継ぎ: A#10以降でdigest・検証結果・公開操作をprovenanceへ結び付ける。

## 主要な判断

- 判断: AのHTML安全検証は、既存HTMLが使っている要素・属性・CSS propertyを基準に狭いallowlistで実装する。
- 理由: 同一GitHub Pages originで公開するため、未知のHTML機能や任意CSSを後から許可するより、必要な表示機能だけを固定する方が受入境界を監査しやすいからである。
- 判断: 外部HTTPSは`a`要素のリンクだけ許可し、stylesheetやCSS `url()`では許可しない。
- 理由: 外部CSS・画像は追跡や将来の内容変更を公開成果物へ持ち込むため、公開HTMLの表示依存をsource内のファイルへ限定するからである。
- 判断: Bの安全validatorを再利用せず、A側で同等以上の検証を再実行する。
- 理由: Bは公開要求前の早期検出、Aはsource registryと公開先を所有する最終受入であり、Bの検証結果を信頼境界の代替にしないためである。

## 最終結果

- 解決したこと: A側でHTMLの構造・要素・属性、URL scheme・project内path、CSS at-rule・property・url()、HTML/CSSのローカル依存を検証できるようにした。`../README.md`などの親ディレクトリ参照は拒否し、現行の安全な作業記録HTML/CSSは受け入れる。
- 変更ファイル: `scripts/publish/content_safety.py`、`tests/test_content_safety.py`、`projects/README.md`、本作業記録のMarkdownと生成HTML。
- 検証結果: `python3 -m unittest discover -s tests -p 'test_*.py'`（34件合格）。作業記録HTML再生成check、filename validator、`py_compile`、`git diff --check`に合格した。`work_record_024.html`をChromiumで1280×900、900×900、640×900、320×800で確認し、横overflow、console error、page error、failed requestは全条件0件だった。
- 未解決事項: A#9のvalidatorを受入workflowへ接続する処理、provenance manifest、固定commitの取得、公開先差分検証、Pages deployは未実装である。
- 次アクション: A#10のprovenance manifestとdrift検査へ進み、その後A#11〜#12の初期provenance・no-op同期dry-runへ接続する。

## GitHub Issue状況

確認日時（JST）: 2026-08-20
取得範囲: `tj-999-comp/sandbox-pages`の親Issue #5とIssue #6〜#10

### 親子関係

```text
#5 [Epic] プロジェクト進捗ページの自動公開を段階導入する
├── #6 [Publish] 公開元source登録を設定ファイル化する
├── #7 [Publish] 共通命名・metadata schema validatorを実装する
└── #8 [Publish] 受入ファイルのpath・種別・容量validatorを実装する
```

### 対象Issue

| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#9 source_html向けHTML・CSS・URL安全validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/9) | 未完了 | 本作業の対象。#7/#8完了後に実装 |
| 2 | P1 | [#10 provenance manifest schemaとdrift検査を実装する](https://github.com/tj-999-comp/sandbox-pages/issues/10) | 未完了 | #8/#9の後続。検証済みdigestを来歴へ記録 |
| 3 | P1 | [#5 プロジェクト進捗ページの自動公開を段階導入する](https://github.com/tj-999-comp/sandbox-pages/issues/5) | 未完了 | 親Epic |

### 依存Issue

| GitHub Issue | 状態 | 関係 |
| --- | --- | --- |
| [#6 公開元source登録を設定ファイル化する](https://github.com/tj-999-comp/sandbox-pages/issues/6) | 完了 | A#9が参照するsource registryを提供 |
| [#7 共通命名・metadata schema validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/7) | 完了 | A#9がrecord basenameとmetadata配置を前提にする |
| [#8 受入ファイルのpath・種別・容量validatorを実装する](https://github.com/tj-999-comp/sandbox-pages/issues/8) | 未完了 | A#9が受入済みファイル集合とsource scopeを再利用する |

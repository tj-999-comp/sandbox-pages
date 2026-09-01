# 作業記録の運用ルール

更新日: 2026-09-01

共通のGitHub・Issue・PR・B/C/D適用標準は[`docs/PORTFOLIO_STANDARD.md`](../docs/PORTFOLIO_STANDARD.md)を参照する。この文書は作業記録のMarkdown/HTML作成と表示検証を定める。

このディレクトリには、リポジトリ内で行った調査、実装、判断、検証、残件を保存する。GitHub上のIssueと混同しないよう、ローカルの記録はすべて「作業記録」と呼ぶ。

## 呼称

- `Issue`はGitHub Issueだけを指す。
- リポジトリ内の調査、実行結果、判断経緯は`作業記録`と呼ぶ。
- `ローカルIssue`、`Issueログ`、`Issue記録`という呼称は新規には使わない。
- 2026-08-18以前の作業記録に残る旧呼称は、当時の運用を示す履歴として扱う。

## ディレクトリ構成

```text
work-records/
├── README.md                   # 運用ルールとテンプレート
├── design.md                   # HTMLデザインガイド
├── work_record.css             # HTML共通スタイル
├── work_record_###.html        # 閲覧用HTML
└── md/
    └── work_record_###.md      # Markdown原本
```

- Markdown原本は`work-records/md/`へ置く。
- HTMLは同じベース名で`work-records/`直下へ生成する。
- `work-records/`直下のMarkdownは`README.md`と`design.md`だけとする。
- HTMLは`work_record.css`を参照し、外部ライブラリへ依存しない。
- 共通公開契約の正本は[`projects/README.md`](../projects/README.md)とし、この文書では本リポジトリ固有の作成方法を定める。

## 命名と採番

- 作業記録は`work_record_001`から`work_record_999`までの3桁ゼロ埋め番号を使う。
- Markdownは`work-records/md/work_record_###.md`、HTMLは`work-records/work_record_###.html`とする。
- 新規番号は、現在のファイルとGit履歴で確認できる過去最大番号の次を使う。
- 欠番、削除済み番号、公開取り下げ済み番号を再利用しない。
- 先頭見出しは`# 作業記録 ###: <内容>`とし、番号をファイル名と一致させる。
- 見出し直下に`作成日: YYYY-MM-DD`を記載する。
- すべての作業記録で、本文へGitHub Issue状況のスナップショットを記載する。Issueに直接関係しない作業でも省略しない。作業記録番号をGitHub Issue番号として扱わない。

## 作成・更新手順

1. 最大番号を確認し、`work-records/md/work_record_###.md`を作成する。
2. この文書のテンプレートに沿って、事実、判断、検証結果、残件を記録する。
3. リポジトリルートでHTMLを生成する。
4. ファイル名、見出し、日付、HTML対応、再生成差分を検証する。
5. HTMLをPCとスマートフォンの実ブラウザで確認する。

```bash
python3 scripts/dev/convert_work_records_to_html.py
python3 scripts/dev/convert_work_records_to_html.py --check
python3 scripts/dev/validate_work_record_filenames.py
```

HTMLは生成物であり、通常は直接編集しない。表示変更はMarkdown、converter、`design.md`、`work_record.css`のいずれかへ反映して再生成する。

## HTMLの作成ルール

- [`design.md`](design.md)と[`work_record.css`](work_record.css)を正本とする。
- タイトルや見出しは事実を簡潔に示し、広告的な表現を使わない。
- HTMLから運用ルール、デザインガイド、Markdown原本、サイトトップへ移動できるようにする。
- Markdown内の相対リンクは、HTMLの出力位置を基準にconverterが変換する。
- Markdown内のraw HTMLは実行せず、文字列としてエスケープする。
- 320px幅でもページ全体の横スクロールを発生させない。
- GitHub Issue状況は関連する作業記録の末尾へ入れ、一覧専用の別HTMLを作らない。

### 共通デザインの確認

- `work-records/design.md`とA側renderer/CSSを作業記録HTMLの正本とする。
- 生成元が異なっても、公開HTMLは共通の詳細ページ構造・タイポグラフィ・色・罫線・footerを使用する。生成元ごとのHTML/CSS/designの複製や旧一覧ページ用レイアウトを新規追加しない。
- 新規導入・移行・再生成時は、1280px、900px、640px、320pxのviewportで横overflow、console/page error、failed requestがないことと、生成元間の主要構造・スタイルの一致を確認する。
- デザイン不一致が残る場合は作業記録や生成元の導入を完了扱いにせず、A側renderer/CSSまたは対象projectの担当工程へ差し戻す。

## GitHub Issue状況の記録

すべての作業記録の末尾に`## GitHub Issue状況`を必ず追加する。Issueに直接関係しない作業であっても、作業記録の該当リポジトリの全Open Issueを唯一の基本取得範囲とする。該当リポジトリ以外のIssueは一覧へ掲載しない。外部リポジトリのIssue確認が必要な場合も、一覧とは分離し、本文の補足として必要性・対象・結果を明記する。

- GitHubから状態を取得した日時をJSTで明記し、その時点のスナップショットとして扱う。
- 対象Issueごとに、該当リポジトリ、`GitHub Issue #<番号>`、タイトル、作業記録との関係、状態、state reasonを記載する。Pull Requestは除外し、取得件数と一覧表のIssue行数を一致させる。件数だけの要約、番号範囲、親Epicだけの記載は不可とする。Issue一覧の取得範囲を限定したり、一覧へ外部リポジトリを含めたりしない。
- 表示は[`projects/B_Stats_Site/work_record_010.html`](../projects/B_Stats_Site/work_record_010.html)と同じ順序にする。確認日時と取得範囲を記載し、実在する親子関係は`text`コードブロックで示した後、`順位`、`優先度`、`GitHub Issue`、`状態`、`関係・着手条件`の5列のMarkdown表へ対象Issueを1件ずつ記載する。親子関係がない場合は推測でツリーを作らず、「親子関係なし」とする。
- GitHubへ接続できない場合は状態を推測せず、取得不可の理由と未確認のIssueを記載する。
- 状態は作業記録作成時の記録であり、通常は過去の作業記録を後から最新状態へ書き換えない。記録漏れを是正する場合は理由を明記して追記し、状態更新が必要な場合は新しい作業記録に新しいスナップショットを追加する。
- Reviewerは、記載した番号・関係・状態をGitHubから取得した結果と照合する。欠落、不一致、状態未取得、件数だけの記載はcommit前に修正する。

## 作業記録テンプレート

```md
# 作業記録 ###: <内容>
作成日: YYYY-MM-DD

## 概要
- 課題:
- 目的:
- 完了条件:

## 適用した役割
### Role name
- 入力:
- 実施内容:
- 成果物:
- 検証結果:
- 未解決事項:
- 次工程への引き継ぎ:

## 主要な判断
- 判断:
- 理由:

## 最終結果
- 解決したこと:
- 変更ファイル:
- 検証結果:
- 作業ブランチ:
- コミット:
- PR:
- PRレビュー・CI:
- 未解決事項:
- 次アクション:

## GitHub Issue状況
確認日時（JST）: YYYY-MM-DD HH:MM
取得範囲: <リポジトリと対象条件>
取得件数: <Open Issue件数。Pull Request除外>（一覧行数: <表のIssue行数>）
取得件数: <Open Issue件数。Pull Request除外>

### 親子関係
```text
<親子関係、または親子関係なし>
```

### 優先順位順の未完了一覧
| 順位 | 優先度 | GitHub Issue | 状態 | 関係・着手条件 |
| ---: | --- | --- | --- | --- |
| 1 | P0 | [#<番号> <タイトル>](https://github.com/owner/repository/issues/<番号>) | 未完了（state reason: null） | <関係・着手条件> |
```

未使用の役割欄は作らず、実際に行った作業だけを記録する。

## 次のセッションへの引き継ぎ

今回の移行内容と、自動公開機構の次の着手点は[`md/work_record_018.md`](md/work_record_018.md)に記録する。metadata schema、source登録、provenance manifest、受入workflow、Pages移行、Slack通知はまだ未実装であり、ファイルが存在しないことを完了とみなさない。

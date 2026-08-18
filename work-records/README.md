# 作業記録の運用ルール

更新日: 2026-08-18

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
- GitHub Issueを扱う場合だけ、本文へ`GitHub Issue #<番号>`と関係を明記する。作業記録番号をGitHub Issue番号として扱わない。

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
- GitHub Issue状況が必要な場合は関連する作業記録の末尾へ入れ、一覧専用の別HTMLを作らない。

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
```

未使用の役割欄は作らず、実際に行った作業だけを記録する。

## 次のセッションへの引き継ぎ

今回の移行内容と、自動公開機構の次の着手点は[`md/work_record_018.md`](md/work_record_018.md)に記録する。metadata schema、source登録、provenance manifest、受入workflow、Pages移行、Slack通知はまだ未実装であり、ファイルが存在しないことを完了とみなさない。

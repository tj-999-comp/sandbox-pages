# 作業記録 028: B/C/D作業記録とGitHub運用の標準化
作成日: 2026-08-20

## 概要

- 課題: B、C、Dなど複数の生成元へ作業記録、GitHub、HTML公開の運用を拡張できる共通ガイドを整備する。
- 目的: GitHub接続、Issue・PR状態、Markdown/HTML作業記録、project追加、検証と例外処理を一つの標準へ揃える。
- 完了条件: 共通正本と各既存文書の参照関係が明確で、GitHub App接続設定とヘルパーが再利用でき、作業記録の生成・検証手順が既存テストへ影響しないこと。

## 適用した役割

### Portfolio Planner

- 入力: 既存`AGENTS.md`、`README.md`、`work-records/README.md`、`projects/README.md`、ユーザー要件。
- 実施内容: 複数生成元を前提に、共通標準、Repository Aの公開契約、生成元ごとの作業記録運用、GitHub App認証の責務を分離した。Issue closeはPR merge後または明示承認後とする状態遷移を定義した。
- 成果物: `docs/PORTFOLIO_STANDARD.md`。
- 検証結果: B既存方式を維持し、C/Dは原則`a_rendered`で追加する適用順序を文書化した。
- 未解決事項: C/Dの具体的なsource repositoryとproject_idは未確定であり、registry追加は行っていない。
- 次工程への引き継ぎ: 新しい生成元ごとにregistry、validator fixture、no-op、E2Eを順番に追加する。

### Portfolio Frontend Engineer

- 入力: GitHub AppのApp ID、Client ID、Macキーチェーン項目、既存Issue取得の失敗履歴。
- 実施内容: キーチェーンからPEMを読み、Client IDでJWTを生成し、対象repositoryのInstallation IDを自動発見して短期Installation tokenを発行する`github_app_token.py`と設定ファイルを追加した。秘密鍵・JWT・tokenはリポジトリへ保存しない。
- 成果物: `config/github_app.json`、`scripts/dev/github_app_token.py`、PEM漏洩防止の`.gitignore`設定。
- 検証結果: `py_compile`、ヘルプ表示、ユーザーのMac通常ターミナルでtoken発行とIssue取得の成功を確認した。
- 未解決事項: このsandbox実行環境はMacログインキーチェーンへアクセスできないため、同環境内での再現テストはできない。
- 次工程への引き継ぎ: Issue状況取得時は`GH_TOKEN="$(python3 scripts/dev/github_app_token.py --print-token)" gh ...`を使う。

### Portfolio Reviewer

- 入力: 標準ガイド、既存運用文書、GitHub Appヘルパー。
- 実施内容: 正本文書の分担、Issue状態の推測禁止、HTML生成物の直接編集禁止、B/C/Dの有効化順序、secret非保存を確認した。
- 成果物: 参照関係と例外ルールのレビュー結果。
- 検証結果: 重大・中・軽微の未解決事項はない。
- 未解決事項: PR作成後のGitHub Actions CIは、この標準化変更のpush後に確認する。
- 次工程への引き継ぎ: staged diff、全テスト、作業記録HTML、ブラウザ確認を完了してからPRを作成する。

## 主要な判断

- 判断: 共通詳細は`docs/PORTFOLIO_STANDARD.md`へ集約し、`AGENTS.md`は実行上の必須ルール、`work-records/README.md`は記録生成、`projects/README.md`は公開受入契約に限定する。
- 理由: 同じルールを複数箇所へ全文複製すると、B/C/D追加時に内容が分岐するため。
- 判断: Issue closeはPR merge後または明示承認後とする。
- 理由: PR作成済みでもmainへ反映されていない状態を、公開完了と誤認しないため。
- 判断: GitHub APIには個人OAuth/PATではなく、実行時発行のGitHub App Installation tokenを使う。
- 理由: Macキーチェーンの期限切れ問題を避け、対象repository・権限を限定し、tokenを保存しないため。

## 最終結果

- 解決したこと: B/C/D共通の作業記録・GitHub・HTML・project追加標準を文書化し、既存の正本から参照できるようにした。GitHub AppでIssue/PR/APIを取得するローカルヘルパーを追加し、対象repositoryのInstallation ID自動発見まで実装した。
- 変更ファイル: `docs/PORTFOLIO_STANDARD.md`、`AGENTS.md`、`README.md`、`work-records/README.md`、`projects/README.md`、`.gitignore`、`config/github_app.json`、`scripts/dev/github_app_token.py`、本作業記録のMarkdownと生成HTML。
- 検証結果: helperの`py_compile`、converter check、filename validator、既存unit test、作業記録HTMLのPC/320pxブラウザ確認に合格した。
- 作業ブランチ: `codex/030-standardization-pr`
- コミット: `92f524a`
- PR: [#31 B/C/Dの作業記録とGitHub運用を標準化](https://github.com/tj-999-comp/sandbox-pages/pull/31)（Draft）
- PRレビュー・CI: PR作成済み。CI・外部レビュー待ち
- 未解決事項: C/Dのsource registry登録、公開workflow、Pages deploy、Issue closeの実運用接続は対象外。PRレビュー・CIは未完了。
- 次アクション: PR #31のCIとレビューを確認し、指摘があれば修正する。

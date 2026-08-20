# sandbox-pages
静的ページを適当に遊ぶ用のものを用意しようと思って。

## 課題解決フロー（エージェント運用）

このリポジトリではCodexを主担当エージェントとして利用する。

1. Codexが依頼を分類し、必要な専門役割だけをサブエージェントへ委任
2. 依存する工程は順番に、独立した調査やテストは必要に応じて並列実行
3. ファイル変更では課題用ブランチを作成し、実装・検証・作業記録を実施
4. 変更をcommit・pushしてPRを作成し、差分レビューとCI確認まで実施

補足:
- 役割定義・詳細ルール・テンプレートはAGENTS.mdを参照
- B/C/Dの作業・GitHub・作業記録標準は [docs/PORTFOLIO_STANDARD.md](docs/PORTFOLIO_STANDARD.md) を参照
- UI作業はDESIGN.mdと該当するSkillsを参照
- Markdown原本は `work-records/md/work_record_###.md` で管理する
- 同じ番号のHTMLを `work-records/work_record_###.html` へ生成する
- 作成・生成・検証手順は [work-records/README.md](work-records/README.md) を参照する
- PRのマージとブランチ削除は、ユーザーから明示的な指示がある場合のみ実施する

## 概要
- 課題: 生成元projectごとに作業記録の命名とHTML生成有無が異なり、複数生成元を安全に受け入れる共通識別規則がなかった。
- 目的: 全生成元の公開作業記録を`work_record_###`へ統一し、project単位の採番、metadata、md-only生成元、既存Bとの互換性を公開契約へ追加する。
- 完了条件: 既存のBと公開URLを改名せず、共通命名、採番、識別子、生成mode、legacy文書、既存projectの移行手順を定義し、重大なレビュー指摘が0件であること。

## 適用した役割
### Portfolio Frontend Engineer
- 入力: ユーザーの共通命名要件、`projects/README.md`の公開契約、Bの`work_record_001`〜`010`と3桁validator、他projectはMarkdownのみという現状。
- 実施内容: 共通命名を3桁ゼロ埋めの`work_record_###`として定義し、`a_rendered`と`source_html`の2方式、既存projectの移行手順をREADMEへ追加した。
- 成果物: 全生成元共通のファイル名・採番・一意キー・metadata対応・移行契約。
- 検証結果: Bの既存ファイル名と公開URLを維持し、番号なし補助文書が自動公開の抜け道にならないことを差分で確認した。
- 未解決事項: 他projectの実ファイル棚卸しと改名は各projectの対応表承認後に別課題で行う。
- 次工程への引き継ぎ: READMEを最終レビューし、対象文書だけをcommit・pushする。

### Portfolio Reviewer
- 入力: 更新後の`projects/README.md`、ユーザー要件、A/Bの既存構成。
- 実施内容: 所有境界、3桁非回帰、採番、md-only対応、補助文書、metadata、移行時の参照更新を確認した。
- 成果物: 採番基準を過去最大割当番号の次へ統一し、番号なし文書をsupport file、legacy補助文書、新規作業記録へ分ける修正を反映した。
- 検証結果: 重大0件、中程度0件、軽微0件で合格。Bの既存名・URL、両生成mode、metadata、一意キー、移行手順に矛盾がないことを確認した。
- 未解決事項: 今回の文書化範囲に未解決事項はない。
- 次工程への引き継ぎ: 対象2ファイルだけをcommitし、最新のremote `main`へpushする。

## 主要な判断
- 判断: ユーザー表記の`work_record_##`は番号プレースホルダーと解釈し、既存Bに合わせて`work_record_###`の3桁ゼロ埋めへ統一する。
- 理由: Bの`work_record_001`〜`010`、validator、converter、公開URLを改名せず利用できるため。
- 判断: 採番はprojectごとに`001`から行い、一意キーを`project_id`とベース名の組み合わせにする。
- 理由: 異なるprojectで同じ番号を安全に使用でき、titleや日付をファイル名へ含める必要がないため。
- 判断: Markdownとmetadataを共通の必須入力とし、HTMLは`a_rendered`または`source_html`で扱う。
- 理由: Bの既存運用を保ちながら、HTMLを持たない他projectを共通契約へ参加させるため。
- 判断: 番号なし補助文書は自動publishせず、作業記録として公開する場合だけ番号付きへ移行する。
- 理由: 任意名の公開を許す抜け道を防ぎ、READMEやdesignなどのsupport fileと作業記録を区別するため。

## 最終結果
- 解決したこと: 全生成元共通の`work_record_###`命名と、既存B・md-only projectを両立する公開契約を定義した。
- 変更ファイル: `projects/README.md`、`Issues/Issue_017.md`。
- 検証結果: `git diff --check`合格、Markdownコードフェンス18個の対応、関連記述、Bの3桁validator、Reviewer合格を確認した。表示コードを変更していないためブラウザ確認は対象外。
- 未解決事項: 今回の文書化範囲は重大・中程度・軽微すべて0件。命名validator、renderer、metadata、各projectの移行自体は今後の実装対象。
- 次アクション: 対象2ファイルだけをcommitし、最新のremote `main`へpushする。

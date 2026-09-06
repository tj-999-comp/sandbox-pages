# 過去作業記録棚卸し対応表

更新日: 2026-09-06

## 目的

Issue #90の完了条件に基づき、登録済み5生成元の現在`main`を固定SHAで確認し、Markdown・metadata・HTMLの対応、公開可否、公開先、既存provenance、補助文書を一覧化する。

この表の「生成元SHA」は各生成元の棚卸し基準commitであり、そのprojectの全record行に適用する。source側の先端を後から追跡するのではなく、同一時点の再現可能なスナップショットとして扱う。

## 集計

| project_id | 生成元 | 生成元SHA | HTML方式 | source record | 公開済み | 未公開候補 | 非公開 |
|---|---|---|---|---:|---:|---:|---:|
| `B_Stats_Site` | `tj-999-comp/B_Stats_Site` | `14468e72a58a00be29e18d132eda05ba0c1f01d7` | `a_rendered` | 31 | 18 | 13 | 0 |
| `tech_article_nortification` | `tj-999-comp/tech_article_nortification` | `c026267696feb6802f83807b76eb499a89e57037` | `a_rendered` | 17 | 2 | 0 | 15 |
| `NBA_Draft_DB` | `tj-999-comp/NBA_Draft_DB` | `3604ed8680ad02f7e3310ac0b2a1f1f259df7058` | `a_rendered` | 1 | 1 | 0 | 0 |
| `query_learning_BB` | `tj-999-comp/query_learning_BB` | `77eca4f0b1889a41958d7b75d79ef2f6ecbb9aec` | `a_rendered` | 34 | 34 | 0 | 0 |
| `sandbox_pages` | `tj-999-comp/sandbox-pages` | `4a89737e671f82b25e4f6e7ec80ca2aff59cc289` | `source_html` | 83 | 71 | 12 | 0 |

合計: source record 166件、公開済み126件、未公開候補40件、metadataで`publish: false`の非公開15件。全recordでMarkdownとmetadataのbasename対応、およびmetadataのtitle/dateとMarkdown見出し・作成日の一致を確認した。

公開済みは公開側のMarkdownとHTMLがともに存在するrecord、未公開候補はmetadataが`publish: true`だが公開側の両ファイルがないrecord、非公開はmetadataが`publish: false`のrecordを指す。

## 対応表

### `B_Stats_Site`

- 生成元: `tj-999-comp/B_Stats_Site` / `refs/heads/main`
- 棚卸し基準SHA: `14468e72a58a00be29e18d132eda05ba0c1f01d7`
- 公開先: `projects/B_Stats_Site/`
- HTML方式: `a_rendered`
- provenance: 公開済みrecordについて対応する受入manifestを記載。公開済みでないrecordに過去manifestがある場合も関連manifestとして記載する。

| basename | 日付 | title | source側ファイル | publish | 公開側 MD/HTML | 関連provenance |
|---|---|---|---|---:|---:|---|
| `work_record_001` | 2026-05-26 | 2016-2017 シーズン投入（初回失敗→再チャレンジ成功） | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_002` | 2026-05-26 | players.nationality 追加手順整理とrebuild SQL一本化 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_003` | 2026-05-26 | プロフィール項目（リーグ登録国籍・出身地）取得とUpsert準備 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_004` | 2026-06-02 | playersのbirthplace欠損調査ログ（スレッド分割前サマリ） | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_005` | 2026-08-04 | 2021-22シーズン303試合の日時・year補正 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_006` | 2026-08-05 | game_team_statsの得点誤マッピング補正 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_007` | 2026-08-05 | GitHub Issue #12 players監査・差分補完基盤 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_008` | 2026-08-13 | GitHub Issue #21 欠損プロフィール目視補完・DBパッチ準備 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_009` | 2026-08-13 | 未投入試合データ投入後の選手重複整理・プロフィール補完フロー | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_010` | 2026-08-13 | 作業記録の呼称・配置・表示ルール再編 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_011` | 2026-08-18 | Issue #24 試合データ取得・Live DB投入 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_012` | 2026-08-20 | Issue #25 player_id統合・プロフィール補完 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_013` | 2026-08-20 | Issue #28 作業記録HTMLのヘッダーリンク整理 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_014` | 2026-08-20 | Issue #29 公開前検証と自動公開フローの整理 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_015` | 2026-08-20 | Issue #22 スタッフ相当判定とプロフィール監査除外 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_016` | 2026-08-20 | Issue #23 分割player_idの調査・統合 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_017` | 2026-08-20 | Issue #18 player_id_mapと旧ID名寄せ経路の検証 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_018` | 2026-08-20 | Issue #13 player_slot_category の正規化準備 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_019` | 2026-08-20 | Issue #16 live DB・再構築SQL・テーブル定義の整合 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_020` | 2026-08-20 | Issue #14 attendance欠損14試合の調査 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_021` | 2026-08-22 | Colab版スクレイパーのB2・B3対応 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_022` | 2026-08-24 | 欠落B1試合の子Issue分割と補完候補の確定 | MD + metadata + HTML（A側では不使用） | `true` | — | `—` |
| `work_record_023` | 2026-08-24 | 欠落B1試合40件の取得と月次JSON統合 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_024` | 2026-08-24 | Issue #46 欠落B1試合40件のDB Upsert | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_025` | 2026-08-24 | 固定commitの手動公開要求workflowとdispatch権限 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_026` | 2026-08-24 | 新規作業記録の手動公開要求E2E | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_027` | 2026-08-25 | B_Stats_Site mainへのpush確認テスト | MD + metadata + HTML（A側では不使用） | `true` | — | `accept-33073917462-1-B_Stats_Site-work_record_029.json` / `withdraw-33145378676-1-B_Stats_Site-work_record_027.json` |
| `work_record_028` | 2026-08-27 | Web導入親IssueとMVP子Issueの作成 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_029` | 2026-08-27 | Supabase公開読み取り設定の工程整理 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_030` | 2026-08-28 | 認証方式・Secret名・運用文書の整合確認 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |
| `work_record_031` | 2026-08-29 | Secret登録状態と公開要求認証の段階移行設計 | MD + metadata + HTML（A側では不使用） | `true` | ○ | `migrate-20260831-B_Stats_Site-a-rendered.json` |

整合性確認: **合格**。

### `tech_article_nortification`

- 生成元: `tj-999-comp/tech_article_nortification` / `refs/heads/main`
- 棚卸し基準SHA: `c026267696feb6802f83807b76eb499a89e57037`
- 公開先: `projects/tech_article_nortification/`
- HTML方式: `a_rendered`
- provenance: 公開済みrecordについて対応する受入manifestを記載。公開済みでないrecordに過去manifestがある場合も関連manifestとして記載する。

| basename | 日付 | title | source側ファイル | publish | 公開側 MD/HTML | 関連provenance |
|---|---|---|---|---:|---:|---|
| `work_record_001` | 2026-05-16 | Qiita記事のSlack通知とNotion保存の初期実装 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_002` | 2026-05-16 | READMEマージコンフリクトの解消 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_003` | 2026-05-16 | Qiita記事スナップショットのローカル保存 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_004` | 2026-05-16 | ルールベース要約とGitHub Models APIフォールバックの導入 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_005` | 2026-05-17 | Slack通知整形とメッセージバックアップの改善 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_006` | 2026-05-18 | Step分割パイプラインへの移行 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_007` | 2026-05-18 | Notion送信フローと重複登録防止の実装 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_008` | 2026-05-18 | Qiita取得順位と定期実行設定の見直し | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_009` | 2026-05-19 | GASからのGitHub Actions外部トリガー連携 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_010` | 2026-06-02 | GitHub Actions定期通知の無効化 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_011` | 2026-08-27 | Issue #2のsandbox-pages公開連携タスク分解 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_012` | 2026-08-28 | Issue #3の要約フォールバック堅牢化 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_013` | 2026-08-28 | Issue #5の公開受入契約とsource-side検証 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_014` | 2026-08-28 | Issue #9の手動公開E2E候補 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-33365206310-1-tech_article_nortification-work_record_015.json` |
| `work_record_015` | 2026-08-30 | GAS定期実行とSlack未更新の調査 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-33365206310-1-tech_article_nortification-work_record_015.json` |
| `work_record_016` | 2026-08-30 | GASのGitHub認証復旧 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |
| `work_record_017` | 2026-08-30 | GitHub Models終了に伴う通知workflow復旧 | MD + metadata（HTMLはA側生成） | `false` | — | `—` |

整合性確認: **合格**。

### `NBA_Draft_DB`

- 生成元: `tj-999-comp/NBA_Draft_DB` / `refs/heads/main`
- 棚卸し基準SHA: `3604ed8680ad02f7e3310ac0b2a1f1f259df7058`
- 公開先: `projects/NBA_Draft_DB/`
- HTML方式: `a_rendered`
- provenance: 公開済みrecordについて、対応する最新の受入manifestを記載。

| basename | 日付 | title | source側ファイル | publish | 公開側 MD/HTML | 最新provenance |
|---|---|---|---|---:|---:|---|
| `work_record_001` | 2026-08-30 | NBA_Draft_DBを公開作業記録の生成元として整備 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-33369404796-1-NBA_Draft_DB-work_record_001.json` |

整合性確認: **合格**。

### `query_learning_BB`

- 生成元: `tj-999-comp/query_learning_BB` / `refs/heads/main`
- 棚卸し基準SHA: `77eca4f0b1889a41958d7b75d79ef2f6ecbb9aec`
- 公開先: `projects/query_learning_BB/`
- HTML方式: `a_rendered`
- provenance: 公開済みrecordについて、対応する最新の受入manifestを記載。

| basename | 日付 | title | source側ファイル | publish | 公開側 MD/HTML | 最新provenance |
|---|---|---|---|---:|---:|---|
| `work_record_001` | 2026-09-01 | 公開側リポジトリへの作業記録連携導入準備 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_002` | 2026-09-02 | SQL学習WebサイトMVPの要件整理と残作業Issue作成 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_003` | 2026-09-03 | #10 CSVデータ監査とSQLiteデータセット確定 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_004` | 2026-09-04 | #6 MVPホスティング先とBasic認証方式の決定・受入確認 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_005` | 2026-09-04 | #9 SQL正誤判定・読み取り専用制限の受入確認と基準確定 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_006` | 2026-09-04 | #10 データセット確定と利用条件確認 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_007` | 2026-09-04 | #14 MVP要件定義書の確定と凍結 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_008` | 2026-09-04 | #13 仮問題10問のMVPコンテンツ検証 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_009` | 2026-09-04 | #12 PC・iPad・ブラウザ保存のMVP受入確認 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_010` | 2026-09-04 | #11 Basic認証付き公開環境の最終スモークテスト | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_011` | 2026-09-04 | MVP完了判定と親Issue #8のクローズ | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_012` | 2026-09-04 | バージョン方針の策定と次期改善Issue #26〜#34の起票 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_013` | 2026-09-04 | Issue #27 達成済み表示のコンパクト化 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_014` | 2026-09-04 | Issue #28 前後の問題への移動 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_015` | 2026-09-04 | Issue #29 問題一覧ドロワー化 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_016` | 2026-09-04 | Issue #30 エディタと実行結果の2ペイン化 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_017` | 2026-09-04 | Issue #31 実行結果のペイン内スクロール | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_018` | 2026-09-04 | v0.2.0 学習画面UX改善の完了 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_019` | 2026-09-04 | Issue #41 問題画面の情報配置と操作性改善 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_020` | 2026-09-04 | Issue #41 クローズとv0.2.1改善の完了記録 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_021` | 2026-09-04 | Issue #43 解答例ボタンと結果エリア表示 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_022` | 2026-09-04 | Issue #43 解答例表示のトグル化と整形 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_023` | 2026-09-04 | Issue #32 SQLエディタの高機能化と公開反映 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_024` | 2026-09-04 | Issue #33 SQLiteスキーマ連動SQL補完 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_025` | 2026-09-04 | Issue #34 SQL問題バンクを100問へ拡充 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_026` | 2026-09-05 | Issue #49 進捗・お気に入りの端末間同期 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_027` | 2026-09-05 | Issue #48 クローズとv0.5.1開始画面・問題一覧改善の完了記録 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_028` | 2026-09-05 | Issue #49 v0.6.0進捗同期の本番確認 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_029` | 2026-09-06 | Issue #52 v1.1.1問題仕様と必要カラム表示の本番反映 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_030` | 2026-09-06 | Issue #26 v1.1.0白基調デザイン確定とUI最終調整 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_031` | 2026-09-06 | Issue #55 UI改善案の採用と本番反映 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_032` | 2026-09-06 | Issue #57 問題文の論理整合性と必要カラム表示の全問修正 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_033` | 2026-09-06 | Issue #58 v1.1.2 達成済みマークの枠調整と本番反映 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |
| `work_record_034` | 2026-09-06 | 作業記録の全件自動連携とSlack通知制御の設定 | MD + metadata（HTMLはA側生成） | `true` | ○ | `accept-34029022300-1-query_learning_BB-work_record_034.json` |

整合性確認: **合格**。

### `sandbox_pages`

- 生成元: `tj-999-comp/sandbox-pages` / `refs/heads/main`
- 棚卸し基準SHA: `4a89737e671f82b25e4f6e7ec80ca2aff59cc289`
- 公開先: `projects/sandbox_pages/`
- HTML方式: `source_html`
- provenance: 公開済みrecordについて、対応する最新の受入manifestを記載。

| basename | 日付 | title | source側ファイル | publish | 公開側 MD/HTML | 最新provenance |
|---|---|---|---|---:|---:|---|
| `work_record_001` | 2026-05-04 | ページ別テーマを維持した共通レイアウト設計 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_002` | 2026-05-04 | Hardモードの罫線・角丸・Finish表示修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_003` | 2026-05-04 | 共通ナビゲーションとフッターの整理 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_004` | 2026-05-12 | Trackball Typing PracticeのUI・導線改善 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_005` | 2026-05-19 | Typing Marathonの操作・言語切替・編集画面修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_006` | 2026-05-19 | Typing Marathonの出題モード不一致修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_007` | 2026-07-30 | shadcn/ui Skillsとデザイン定義の導入 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_008` | 2026-07-30 | Codexを中心としたエージェント運用への移行 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_009` | 2026-07-30 | Gitブランチ・PR・レビュー工程の追加 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_010` | 2026-07-30 | Trackball Controll Practiceのデザイン準拠 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_011` | 2026-07-30 | Trackball Controll Practiceの配色・UX調整 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_012` | 2026-07-30 | Trackball Controll Practiceの操作ボタン確定 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_013` | 2026-08-02 | Trackball Controll Practiceのスコア・ゲームフィードバック改善 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_014` | 2026-08-02 | ドキュメント変更時のGit運用簡略化 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_015` | 2026-08-15 | projectsディレクトリの用途と公開構想の記録 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_016` | 2026-08-18 | 複数生成元向け作業記録公開契約の策定 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_017` | 2026-08-18 | 作業記録ファイル名とHTML生成方式の統一 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_018` | 2026-08-18 | Issuesからwork-recordsへの移行と次セッションへの引き継ぎ | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_019` | 2026-08-18 | プロジェクト進捗ページ自動公開のIssue分解と登録 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_020` | 2026-08-19 | Issue #6 source registryの導入 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_021` | 2026-08-20 | 共通命名・metadata schema validatorの実装 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_022` | 2026-08-20 | 作業記録HTML上部リンクの撤去 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_023` | 2026-08-20 | Issue #8 受入ファイルのpath・種別・容量validator | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_024` | 2026-08-20 | Issue #9 HTML・CSS・URL安全validator | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_025` | 2026-08-20 | Issue #10 provenance manifestとdrift検査 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_026` | 2026-08-20 | B既存001〜010の初期provenance manifest登録 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_027` | 2026-08-20 | Issue #12 既存Bのno-op同期dry-run | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_028` | 2026-08-20 | B/C/D作業記録とGitHub運用の標準化 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_029` | 2026-08-20 | Issue #14〜#16 Actions方針・Pages deploy・進捗index | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_030` | 2026-08-20 | Issue #17 read-only受入workflowのdry-run | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_031` | 2026-08-20 | 未完了一覧のIssueスナップショット再取得ルールを標準化 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_032` | 2026-08-20 | Issue #18 許可範囲限定の同期apply engine | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_033` | 2026-08-20 | Issue #19 受入workflowへのcommit・固定SHA deploy接続 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_034` | 2026-08-20 | Issue #21 disabled source受入dry-run | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_035` | 2026-08-24 | Issue #21 disabled source実E2E | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_036` | 2026-08-24 | Issue #22 B source手動E2E有効化 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_037` | 2026-08-24 | Issue #20 deploy後Slack通知job | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_038` | 2026-08-24 | apply時のPython bytecode生成によるE2E失敗を修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_039` | 2026-08-25 | Issue #23実publish E2Eの途中結果 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_040` | 2026-08-25 | PR #42のvalidation失敗修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_041` | 2026-08-25 | Issue #23 reusable Pages deploy条件の修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_042` | 2026-08-25 | Issue #23 no-op受入runの成功化 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_043` | 2026-08-25 | Issue #23 should_deploy真偽値判定の修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_044` | 2026-08-25 | Issue #23 no-op入力のworkflow_call検証修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_045` | 2026-08-25 | Issue #23 should_deploy入力型の安定化 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_046` | 2026-08-25 | Issue #23 reusable workflow concurrencyの分離 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_047` | 2026-08-25 | Issue #23 no-op入力の文字列伝播を固定 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_048` | 2026-08-25 | Issue #23 空commit SHA入力の正規化 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_049` | 2026-08-25 | Issue #23 no-op時のcaller skip | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_050` | 2026-08-25 | Issue #23 called workflow concurrencyの除去 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_051` | 2026-08-25 | Issue #23 Slack通知jobのcheckout追加 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_052` | 2026-08-25 | Issue #23 E2E完了 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_053` | 2026-08-25 | Issue #54 Slack投稿内容と対象作業記録URLの修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_054` | 2026-08-27 | tech_article_nortification の生成元導入契約を追加 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_055` | 2026-08-28 | Issue #4 の tech_article_nortification source registry登録を検証 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_056` | 2026-08-28 | Issue #13 a_rendered用の決定的rendererを実装 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_057` | 2026-08-28 | 監査可能な公開取り下げworkflowを実装 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_058` | 2026-08-28 | 取り下げdry-runの作業ツリー汚染を修正 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_059` | 2026-08-28 | Issue #60 固定commit・basename限定の受入境界を強化 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_060` | 2026-08-28 | Issue #60 disabled dry-run E2E | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_061` | 2026-08-30 | 生成元テンプレートのGitHub App連携工程を標準化 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_062` | 2026-08-31 | tech_article_nortification受入E2E準備 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_063` | 2026-08-31 | tech_article_nortification受入E2E実施 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_064` | 2026-08-31 | PR #65のコンフリクト解消 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_065` | 2026-08-31 | NBA_Draft_DBのsource登録と初期公開状態の準備 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_066` | 2026-08-31 | 過去作業記録の遡及公開・record間リンクIssue計画 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_067` | 2026-08-31 | NBA_Draft_DBの作業記録公開E2Eと運用引き継ぎ | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_068` | 2026-08-31 | Issue #80 sandbox-pages source registry登録 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_069` | 2026-08-31 | Issue #81 sandbox_pages作業記録metadata整備 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_070` | 2026-08-31 | Issue #82 同一repository source受入隔離 | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_071` | 2026-08-31 | Issue #83 sandbox_pages初期provenance登録 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_072` | 2026-08-31 | Issue #84 sandbox_pages disabled受入dry-runの修復 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_073` | 2026-08-31 | Issue #85 sandbox_pages手動E2E有効化 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_074` | 2026-08-31 | Issue #86 sandbox_pages新規作業記録E2E | MD + metadata + HTML | `true` | ○ | `accept-33406726036-1-sandbox_pages-work_record_074.json` |
| `work_record_075` | 2026-09-01 | Issue #87 sandbox_pages公開運用の引き継ぎ | MD + metadata + HTML | `true` | — | `—` |
| `work_record_076` | 2026-09-01 | Issue #79 sandbox_pages本番運用開始確認 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_077` | 2026-09-01 | 生成元リポジトリ用GitHub Templateを登録 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_078` | 2026-09-01 | query_learning_BBの公開側registry導入 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_079` | 2026-09-01 | query_learning_BBの受入baselineを登録 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_080` | 2026-09-01 | query_learning_BBを手動E2E向けに有効化 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_081` | 2026-09-01 | query_learning_BBの手動公開E2E完了 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_082` | 2026-09-01 | 全生成元のIssue状況・HTMLデザイン運用を統一 | MD + metadata + HTML | `true` | — | `—` |
| `work_record_083` | 2026-09-01 | Issue #102完了確認と全生成元公開HTML受入 | MD + metadata + HTML | `true` | — | `—` |

整合性確認: **合格**。

## 補助文書・除外対象

作業記録と混同しない補助文書、およびsource registryで明示的に除外されるファイルは、record対応表へ含めない。

| project_id | 補助文書・除外対象 | 扱い |
|---|---|---|
| `B_Stats_Site` | `README.md`, `design.md`, `md/phase_1_tasks.md`, `md/scraping_db_automation.md`, `work_record.css`, `work_record_001.html`〜`work_record_031.html`, `work_record_extra_01.html`, `work_record_extra_02.html`（HTMLはA側renderer移行後のignored_files） | recordの公開可否・番号対応から除外 |
| `tech_article_nortification` | なし（work-records配下はrecordのMarkdownとmetadataのみ） | recordの公開可否・番号対応から除外 |
| `NBA_Draft_DB` | なし（work-records配下はrecordのMarkdownとmetadataのみ） | recordの公開可否・番号対応から除外 |
| `query_learning_BB` | `README.md`（公開対象外の補助文書） | recordの公開可否・番号対応から除外 |
| `sandbox_pages` | `README.md`, `design.md`, `work_record.css`（source_htmlのsupport files） | recordの公開可否・番号対応から除外 |

## 未公開候補と次工程

- `B_Stats_Site`: `work_record_011`〜`work_record_022`、`work_record_027`の13件はsource側metadataが`publish: true`だが、現行公開先に両ファイルがない。`work_record_027`は`accept-33073917462-1-B_Stats_Site-work_record_029.json`で受入履歴があり、`withdraw-33145378676-1-B_Stats_Site-work_record_027.json`で取り下げられているため、後続工程で再公開可否を判断する。
- `tech_article_nortification`: `work_record_001`〜`work_record_013`、`work_record_016`、`work_record_017`は`publish: false`。公開済みは`014`、`015`のみ。
- `NBA_Draft_DB`: source record 1件と公開側1件が一致する。
- `query_learning_BB`: source record 34件と公開側34件、provenance 34件が一致する。
- `sandbox_pages`: `work_record_071`〜`work_record_073`、`work_record_075`〜`work_record_083`の12件はsource側metadataが`publish: true`だが、現行公開先に両ファイルがない。

この対応表を入力として、Issue #91でmetadata・HTML整備、Issue #92でindexとrecord間リンク、Issue #93で固定SHAの遡及反映、Issue #94でPages上の全体受入を行う。未公開候補は推測で公開せず、固定source commitと公開可否を確認してから後続工程へ渡す。

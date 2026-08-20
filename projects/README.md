# 作業記録の公開ルール

更新日: 2026-08-18

この文書は、AIエージェントなどが生成元リポジトリで作成した作業記録を、公開リポジトリのGitHub Pagesで公開するための受入・配信ルールを定める。

公開リポジトリは `tj-999-comp/sandbox-pages`、生成元リポジトリは `tj-999-comp/B_Stats_Site` などの独立したGitHubリポジトリを指す。生成元は将来複数になることを前提とする。

正本URL: <https://github.com/tj-999-comp/sandbox-pages/blob/main/projects/README.md>

B、C、Dなど生成元ごとの作業・GitHub・作業記録の共通運用は[`docs/PORTFOLIO_STANDARD.md`](../docs/PORTFOLIO_STANDARD.md)を参照する。この文書は公開リポジトリAの受入・配信契約を正本とする。

## この文書の位置付け

- `tj-999-comp/sandbox-pages` にあるこの文書を公開ルールの正本とする。
- 生成元リポジトリへ同じ内容を置く場合、そのコピーは参照用とし、共通ルールの変更は公開リポジトリから行う。
- 生成元ごとの作業記録運用ルールは、この共通ルールと分離する。たとえば `B_Stats_Site/work-records/README.md` はproject固有の内容・Issue記録・生成手順を定める文書であり、この文書で置き換えない。命名が競合する場合は、この共通命名を優先する。
- 実装前の構想ではなく、publish機構が満たすべき契約として扱う。未実装の項目は「実装済み」とみなさない。

## 用語

| 用語 | 意味 |
| --- | --- |
| 公開リポジトリ（Repository A） | 公開可否、配置、index、デプロイ、通知を管理するリポジトリ |
| 生成元リポジトリ（Repository B） | Markdownとmetadataを生成するリポジトリ。`source_html`では同名HTMLも生成する。複数登録できる |
| `project_id` | 公開リポジトリが割り当てる生成元の不変な識別子 |
| 公開要求 | 生成元の `publish: true` とworkflow dispatch。公開承認そのものではない |
| 公開成果物 | 公開リポジトリが受入済みの生成物と、その表示に必要な関連ファイル |
| provenance manifest | 受入元commit、対象ファイル、digest、公開操作を記録する機械可読な来歴情報 |

`publish: true` は生成元からの公開要求である。公開リポジトリの登録内容と受入検証を通過し、GitHub Pagesへのdeployが成功した時点で公開とする。

## 現在のリポジトリ対応

公開URL:

<https://tj-999-comp.github.io/sandbox-pages/>

| `project_id` | 生成元リポジトリ | 生成元branch | 生成元ディレクトリ | 公開先ディレクトリ |
| --- | --- | --- | --- | --- |
| `B_Stats_Site` | `tj-999-comp/B_Stats_Site` | `main` | `work-records/` | `projects/B_Stats_Site/` |

新しい生成元は、公開リポジトリ側で `project_id`、リポジトリ、branch、生成元ディレクトリ、公開先ディレクトリ、support file、generator ID、サイズ上限を登録し、受入テストを通過するまで無効とする。metadataの値から任意の公開先パスを組み立てず、公開リポジトリに登録された対応だけを使う。

この対応は公開リポジトリが所有する`config/sources.json`で管理し、生成元から更新させない。source registryのloaderは`scripts/publish/source_registry.py`である。次は登録エントリの概念例であり、実ファイルではJSONの`schema_version`と`sources`配列に含める。

```yaml
schema_version: 1
project_id: B_Stats_Site
source_repository: tj-999-comp/B_Stats_Site
source_ref: refs/heads/main
source_directory: work-records
metadata_directory: work-records/metadata
destination_directory: projects/B_Stats_Site
public_base_path: /sandbox-pages/projects/B_Stats_Site/
support_files:
  - README.md
  - design.md
  - work_record.css
generator_id: b-stats-work-record-v1
html_mode: source_html
enabled: false
limits:
  max_files: 100
  max_file_size_bytes: 1048576
  max_total_size_bytes: 10485760
```

`generator_id` はAが所有する検証実装へ対応させる識別子であり、生成元から受け取った任意のshell commandとして実行しない。

`html_mode` は `source_html` または `a_rendered` とする。`source_html` は生成元で同名HTMLを管理する互換方式、`a_rendered` は生成元のMarkdownとmetadataからA所有のrendererがHTMLを生成する方式である。新しい生成元は原則として `a_rendered` を使用する。

## 正本と所有境界

| 対象 | 所有者・正本 |
| --- | --- |
| Markdownとmetadataの内容 | 生成元リポジトリの受入対象commit |
| `source_html`における同名HTML | 生成元リポジトリの受入対象commit |
| 共通命名、公開先、URL、受入条件、metadata schema | 公開リポジトリ |
| `a_rendered`におけるHTML templateとrenderer | 公開リポジトリ |
| source登録、validator、workflow、provenance manifest | 公開リポジトリ |
| project index、全体導線、公開サイト側のデザイン | 公開リポジトリ |
| 公開中の受入済みファイル | 公開リポジトリ |
| GitHub Pages、Slack通知、公開停止の判断 | 公開リポジトリ |

公開リポジトリに置いた生成物を通常運用で直接編集しない。修正は生成元へ反映し、検証済みcommitから再publishする。

緊急修正などで公開リポジトリだけを変更した場合は、生成元へ同じ修正を取り込むか、公開リポジトリ側の変更を正式に採用する判断を記録するまで自動publishを停止する。両者が食い違うときは、一方を無条件に上書きせず、直前のprovenance manifest、生成元commit、公開中のdigestを照合する。

### ファイルの管理範囲

生成元が管理するもの:

- 共通命名に従うMarkdownとmetadata
- `source_html`の場合は対応する同名HTML
- 登録済みのproject support file

公開リポジトリが管理するもの:

- `projects/README.md`
- source登録と受入validator
- GitHub Actions workflow
- project/global indexとそのgenerator
- provenance manifest

生成元の処理に公開リポジトリのwrite tokenを渡さず、公開リポジトリが自分のworkflow内で受入・反映する。

## 共通命名規則

すべての生成元で、公開する作業記録のベース名を `work_record_###` に統一する。`###` は `001` から `999` までの3桁ゼロ埋め番号を表す。既存の `B_Stats_Site` と公開URLを維持するため、2桁の `work_record_##` へは変更しない。

必須のファイル名は次のとおりである。

```text
work-records/md/work_record_###.md
work-records/metadata/work_record_###.yml
```

`source_html`では次も必須とする。`a_rendered`ではAが同じ名前で生成する。

```text
work-records/work_record_###.html
```

次のルールを適用する。

- 番号は生成元projectごとに独立して `001` から採番する。
- 番号を一度も割り当てていないprojectは `001`、既存projectは現在のファイル、Git履歴、provenance manifestから確認した「過去に割り当て済みの最大番号」の次を使用する。
- `000` は使用しない。
- 欠番を許容し、削除・公開取り下げ後も番号を再利用しない。
- 公開後の番号変更や連番の詰め直しを行わない。
- `999`へ到達した場合は `work_record_1000`を独断で作らず、A側で命名schema versionの更新を決める。
- 大文字小文字を含め、正規表現 `^work_record_[0-9]{3}$` に一致するベース名だけを受け入れる。
- validatorは正規表現一致に加え、数値部分が `001` から `999` の範囲であることを検証する。
- metadataとHTMLはMarkdownと同じベース名にする。
- recordの一意な識別子は `<project_id>:<ベース名>` とする。異なるprojectで同じ番号を使用してよい。
- title、date、tags、`project_id`はmetadataで管理し、ファイル名へ含めない。
- タイトル由来のslug、日付ディレクトリ、`/ai-sessions/` は導入しない。
- 補助Markdownを作業記録として公開する場合も番号を割り当て、この命名へ移行する。

`work-record-001.md`、`work_record_01.md`、`record_001.md`、タイトル由来の名前など、規則外のファイルは新規作成しない。既存の規則外ファイルは移行が完了するまで自動publishしない。

## 生成元のファイル契約

すべての生成元でMarkdownとmetadataを正本入力とする。HTMLの管理方法はAのsource登録にある `html_mode` で決める。

### `a_rendered`

新しい生成元と、現在Markdownだけを持つ生成元の標準方式とする。

```text
work-records/
├── metadata/
│   └── work_record_###.yml
└── md/
    └── work_record_###.md
```

生成元はHTML、CSS、公開用designを複製しない。Aが登録済みの `generator_id` に対応するrendererとtemplateから `work_record_###.html` を生成する。rendererはMarkdown内のraw HTMLを無効化し、リンクschemeと生成HTMLをAのallowlistで検証する。

### `source_html`

既にMarkdownと同名HTMLを管理している生成元の互換方式とする。現在の `B_Stats_Site` はこの方式に該当する。

`B_Stats_Site` の現在の構成は次のとおりである。

```text
work-records/
├── README.md
├── design.md
├── work_record.css
├── work_record_###.html
├── metadata/                 # metadata導入後
│   └── work_record_###.yml
└── md/
    └── work_record_###.md
```

現在BとAにある番号なしの補助文書はlegacy補助文書として現状維持できるが、新規の独立した作業記録として自動受入、index掲載、Slack通知、自動更新、自動削除の対象にしない。`README.md`、`design.md`などAのsource登録に明示されたsupport fileは作業記録ではなく、表示依存ファイルとして別に扱う。

MarkdownからHTMLへの変換コマンド:

```bash
python -m scripts.dev.convert_work_records_to_html
```

現行HTMLは次の相対リンクを含むため、HTML単体を公開成果物にしてはならない。

- `work_record.css`
- 同じディレクトリの `README.md`
- 同じディレクトリの `design.md`
- `md/<同じベース名>.md`
- `../README.md`

`source_html`の公開先では、生成元の `work-records/README.md`、`design.md`、`work_record.css`、対象HTML、対応Markdown、metadataをproject単位で扱う。

現行の `../README.md` は、生成元ではリポジトリルートREADME、公開先では `projects/README.md` を指し、環境によって意味が変わる。この親ディレクトリ参照を新規・更新成果物では許可しない。自動publishを有効化する前に、generatorをproject内の `README.md` または生成元リポジトリへの明示的なHTTPS URLへ変更する。公開リポジトリの親READMEを生成元ファイルで上書きしてはならない。

## 公開先の配置

`B_Stats_Site` の既存配置とURLを維持する。

```text
projects/B_Stats_Site/
├── README.md
├── design.md
├── work_record.css
├── work_record_###.html
└── md/
    └── work_record_###.md
```

```text
https://tj-999-comp.github.io/sandbox-pages/projects/B_Stats_Site/work_record_###.html
```

既存URLを壊すため、現時点では日付ディレクトリ、タイトル由来のファイル名、`/ai-sessions/` への移動は行わない。将来横断一覧を作る場合も、既存ファイルを移動せず現在のURLへリンクする。

## metadata契約

metadataは公開対象を明示するために使用し、公開リポジトリがschemaを管理する。配置は `<生成元ディレクトリ>/metadata/work_record_###.yml` とする。

```yaml
schema_version: 1
title: 作業記録タイトル
date: "YYYY-MM-DD"
project_id: B_Stats_Site
tags:
  - github-pages
publish: true
```

次のルールを適用する。

- metadataファイル名のベース名から、`work_record_###.html` と `md/work_record_###.md` を導出する。
- `html_file`、`markdown_file`、公開先パスをmetadataへ重複して持たせない。
- `slug` は新規schemaへ追加しない。legacy互換で必要な場合もベース名と完全一致させ、URL変更には使用しない。
- `project_id` は公開リポジトリに登録された値と一致させる。
- `date` は実在する `YYYY-MM-DD`、`tags` は文字列の配列、`publish` は真偽値とする。
- 必須項目不足、未知の項目・schema version、重複ベース名、大小文字だけが異なる名前は受け入れない。
- metadataがないファイルは自動publishしない。既に公開済みの場合も自動削除しない。
- `publish: false` は新規公開・更新の対象外を意味する。公開取り下げは公開リポジトリ側の明示手続きとして別途行う。

番号なしの補助文書は、新規の独立した作業記録として自動受入、index掲載、Slack通知の対象にしない。Aのsource登録に明示されたsupport fileはこの制限の対象外だが、作業記録としてmetadataを付けたりindexへ掲載したりしない。既にAに存在するlegacy補助文書は現状維持とし、自動更新・自動削除しない。独立した作業記録として公開管理へ移行する場合は `work_record_###` を割り当て、Markdownとmetadataを共通配置へ移す。

## 受入条件

生成元からの公開要求は、少なくとも次をすべて満たした場合だけ受け入れる。

1. 公開リポジトリに登録された生成元リポジトリ、branch、`project_id` からの要求である。
2. 対象commit SHAを固定し、そのcommitが登録branchの履歴に存在する。
3. projectの直前受入commitがある場合、対象commitがそれと同一または子孫である。過去commitへのrollbackはA管理者の明示操作だけで行う。
4. pull requestやfork由来など、外部コードへSecretが渡るイベントではない。
5. source側の公開対象commitが、各生成元で定めた人間の確認・branch保護を通過している。
6. Secret、個人情報、契約上非公開のデータを公開成果物に含まない。
7. ファイルが通常ファイルであり、symlink、path traversal、絶対パス、バックスラッシュ、許可範囲外参照を含まない。
8. Markdownとmetadataが `work_record_###` の同じベース名を持ち、許可された配置、拡張子、ファイル数、単体・合計サイズ上限を満たす。`source_html`ではHTMLも同じベース名を持つ。
9. `source_html`では生成元側で登録済みの変換処理を再実行してもcommit済みHTMLに差分がない。`a_rendered`ではAが所有・監査する実装だけでHTMLを生成する。
10. `source_html`ではHTMLが参照するCSS、Markdown、README、designなどの依存ファイルが揃っている。
11. Aがgenerator IDごとに定めたHTML要素・属性・URL属性のallowlistだけを使用している。未知の要素・属性を拒否し、script、inline event handler、iframe、object、embed、form、service worker、`base`、許可外の`meta`、meta refreshなどの能動的な機能を許可しない。
12. URL属性はproject内の相対URL、fragment、または許可したHTTP(S) URLだけを使用し、`javascript:`、危険な`data:`、protocol-relative URL、project外へ抜ける相対URLを拒否する。
13. CSSはAのallowlistを通過し、`@import`、外部・protocol-relative・危険なdata URL、許可外の `url()`、実行・追跡につながる構文を含まない。
14. 公開リポジトリの直前のprovenance manifestと現在のファイルdigestが一致し、未調整の手動変更や別publishとの競合がない。
15. 公開リポジトリの差分が、登録されたproject配下、A所有のindex、provenance manifestなど明示的な許可範囲だけに収まる。

AI生成HTMLを同じGitHub Pages originで公開するため、HTML安全検証は必須とする。登録済み変換処理で再現できない任意HTMLを許容する場合は、このサイトへ直接載せず、別リポジトリ・別originで公開する。

## 納品・publish処理

最終判断を公開リポジトリ側で技術的にも担保するため、標準方式は「生成元から公開リポジトリへ直接push」ではなく、「生成元が公開要求を送り、公開リポジトリが固定commitを取得する」方式とする。

### AIエージェント

- 生成元リポジトリで共通命名に従うMarkdownとmetadataを生成する。`source_html`では同名HTMLも生成する。
- 対応する検証を実行し、生成元リポジトリへcommit/pushするところまでを担当する。
- 公開リポジトリへの反映、GitHub Pages deploy、Slack通知を担当しない。

### 生成元リポジトリのGitHub Actions

1. 実行対象のcommit SHAを固定してcheckoutする。
2. 生成元側の共通命名とmetadataを検証する。`source_html`ではHTML再生成、安全性、依存ファイルも検証する。
3. 公開対象がある場合、公開リポジトリの受入workflowへ `project_id`、commit SHA、対象ベース名だけを `workflow_dispatch` で送る。生成元リポジトリ、branch、各ディレクトリはAのsource登録から決定する。
4. 公開リポジトリのファイルをcheckout、編集、commit、pushしない。

### 公開リポジトリのGitHub Actions

1. dispatch入力を公開リポジトリのsource登録と照合する。
2. 登録された生成元の固定commitから必要な通常ファイルだけを取得し、受入条件をA所有のvalidatorで再検証する。
3. `a_rendered`ではA所有のrendererで同名HTMLを生成する。`source_html`では検証済みHTMLとsupport fileを受け入れる。
4. 公開リポジトリの最新`main`へ、許可された生成物だけを反映する。
5. A所有のgeneratorでproject/global indexを再生成する。
6. 許可範囲外の差分がないことと、直前のprovenance manifestとの整合を確認する。
7. 差分がなければcommit、deploy、通知を行わず成功終了する。
8. 差分がある場合だけprovenance manifestとともに通常commit・pushし、新しいAのcommit SHAをworkflow出力として固定する。
9. deploy jobはそのcommit SHAを明示的にcheckoutしてbuildし、deploy直前にもremote `main`が同じSHAであることを確認する。
10. 同じworkflow runでPagesをdeployし、成功後に通知判定を行う。

公開リポジトリの全受入と通常pushからのPages deployは、workflowをまたいで同じconcurrency groupを使用し、`cancel-in-progress: false` で直列化する。push直前に最新`main`を再取得し、競合時は自projectの変更だけを上限付きで再適用してindexを再生成する。他projectの変更を上書きせず、競合を解消できなければ失敗させる。force push、自動削除、自動改名、`rsync --delete`は行わない。

deploy直前にremote `main`が固定したcommit SHAより進んでいた場合、そのrunは古いartifactをdeployせず終了し、より新しいcommitを対象にしたrunへ引き継ぐ。

公開リポジトリ自身の `GITHUB_TOKEN` で作成したcommitは別のpush workflowやPages buildを起動しないため、受入workflow自身がcommit後のbuild・deployまで完了させる。公開リポジトリへ通常pushされた他の変更は、同じPages処理をpush triggerから実行する。

BからAへ直接pushする方式は、BへA全体のContents write権限を渡し、ディレクトリ単位では制限できないため標準採用しない。どうしても直接納品が必要な場合は、Aの保護branchへ直接pushせずPRを作成し、A側の承認後にmerge・deployする。

Aのwrite tokenやSlack Secretを持つjobでは、生成元リポジトリのscript、Action、任意commandを実行しない。検証、Aへの反映、Pages deploy、Slack通知はjobを分け、検証結果は対象ファイル一覧とdigestで引き渡す。生成元コードの実行が不可欠な検証は、write権限とSecretを持たない隔離jobで行い、その出力もA所有のvalidatorで再検証する。

## provenance manifest

projectごとに公開リポジトリが管理し、少なくとも次を記録する。

- `schema_version`
- 一意な`publication_id`
- `project_id`
- 生成元リポジトリ、branch、commit SHA
- 対象ベース名、公開先相対URL、各ファイルのdigest
- 受入日時
- `create`、`update`、`withdraw`の操作種別
- schemaに従って正規化したtitle、date、tagsなどのindex用metadataと、そのdigest
- Slack通知対象かどうか

公開リポジトリの生成物が記録済みdigestと異なる場合、自動上書きせず停止する。

## indexの生成

- project単位のindexとサイト全体の導線は公開リポジトリが所有する。
- 生成元はindexテンプレートを上書きしない。
- provenance manifestに保存した正規化済みmetadataをHTML escapeし、日付の降順と安定した第二ソートキーで決定的に生成する。
- indexからは既存の公開URLへリンクする。
- 生成元側の「作業記録とは別の一覧HTMLを作らない」という規則と、公開サイト側のindexは責務が異なるため両立する。

## 公開取り下げ

`publish: false` や生成元でのファイル削除だけでは、公開済みファイルを削除しない。

公開取り下げはA管理者による監査可能な操作とし、対象ファイル、project/global index、provenance manifestを同じ変更で更新する。対象URLへの対応方法、Slack通知、復元手順を確認してから実行する。

## GitHub PagesとSlack通知

公開リポジトリは現在、`main` branchのルートを公開するlegacy Pages構成である。自動publishより先に、既存URLを維持したままカスタムGitHub Actions workflowへ移行する。

Pages workflowは、受入workflowまたは公開リポジトリへの通常pushを契機にbuild・deployし、jobごとに必要な `contents`、`pages: write`、`id-token: write` だけを与える。外部Actionは可能ならcommit SHAで固定する。

Slack通知はdeploy成功後にだけ実行する。provenance manifestで通知対象となった公開URLを上限付きretryで確認してから送信する。

初期方針では新規 `create` だけ通知し、`update`、`withdraw`、再実行の通知要否は実装時に別途決める。初回bootstrapと無関係なサイト更新は通知しない。Incoming Webhookは少なくとも一回の配信となり得るため、`publication_id` を通知へ含め、再実行時の重複を識別できるようにする。

Slack通知だけが失敗してもPages公開を巻き戻さない。通知jobの失敗として記録し、同じ `publication_id` で安全に再送できるようにする。

## 認証と権限

初期構成:

- 生成元リポジトリのSecret名: `SANDBOX_PAGES_DISPATCH_TOKEN`
- Fine-grained PATの対象: `tj-999-comp/sandbox-pages` のみ
- PATの権限: Actions write。Contents writeは与えない
- PATの用途: 公開リポジトリの指定した受入workflowを `workflow_dispatch` することだけ
- 公開リポジトリの検証job: `contents: read`。write権限とSecretなし
- 公開リポジトリの反映job: `contents: write`。生成元コードを実行しない
- 公開リポジトリのdeploy job: `contents: read`、`pages: write`、`id-token: write`
- 公開リポジトリの通知job: `contents: read` と `SLACK_WEBHOOK_URL` だけ
- 公開リポジトリのSlack Secret名: `SLACK_WEBHOOK_URL`

Actions writeはdispatch以外のActions APIも利用可能なため、対象を公開リポジトリだけに絞り、有効期限を設定する。公開リポジトリでは手動起動可能なworkflowを最小限にし、入力を必ずA所有の登録情報と照合する。

TokenやWebhook URLをリポジトリ、metadata、ログへ記載しない。Tokenを定期的にローテーションする。

Actionsのpublish automationは、公開リポジトリだけにインストールした必要最小限のGitHub Appと短期installation tokenへ移行する。ローカルのIssue・PR取得も、リポジトリ内の`docs/PORTFOLIO_STANDARD.md`に従い、同じくGitHub App tokenを使う。非公開の生成元を追加する場合は、公開リポジトリ側に生成元read用の別権限を用意し、dispatch tokenと兼用しない。

公開リポジトリのworkflowが`main`へcommitできるよう、branch rulesetとbotの扱いを公開リポジトリ側で明文化する。直接commitを許可しない場合は、A workflowがPRを作成し、承認・merge後にdeployする。

## 現在の同期基準

2026-08-18時点で、以前の未コミット差分は `B_Stats_Site` の`main`へ取り込まれている。

- 生成元基準commit: `0fe9932255ac72e526e84887ee3f209af9f57c61`
- 公開リポジトリ確認commit: `dd4c73c7820171a544d3e9b153904f538961ff80`
- `projects/B_Stats_Site/` に現在存在する全ファイルは、生成元基準commitの対応ファイルとbyte単位で一致する。
- 生成元にのみ存在する `phase_1_tasks.html` と `scraping_db_automation.html` は共通命名に適合せず、公開リポジトリでは未受入である。番号付き作業記録へ移行しない限り、自動追加しない。

最初のpublishでは、この対応を初期provenance manifestとして記録し、既存ファイルが変更されないno-op同期を確認する。初回bootstrapのSlack通知は行わない。

現行HTMLの親ディレクトリ参照は受入条件を満たさないため、generatorと既存HTMLを修正し、公開リポジトリとの意図した差分を確認してから自動publishを有効にする。

## 既存プロジェクトの命名移行

現在、異なる名前や配置でMarkdownを管理しているprojectは、一括自動改名せず、project単位で次の手順に従う。

1. 公開候補のMarkdownを棚卸しし、通常文書と作業記録を分ける。
2. 作成日、Git履歴、既存の並びを根拠に採番案を作り、人間が対応表を確認する。
3. 番号付き作業記録が一度もないprojectだけ `001` から開始する。既に割当実績があるprojectでは、現在のファイル、Git履歴、provenance manifestに記録された過去の最大番号の次から採番し、欠番や過去に使用した番号を割り当てない。
4. `git mv`で `work-records/md/work_record_###.md` へ移し、同じベース名のmetadataを作る。
5. リポジトリ内のリンク、AGENTS.md、README、Issue、workflowなど旧パスへの参照を更新する。
6. `source_html`を使う場合は同名HTMLを生成する。`a_rendered`ではHTMLを生成元へ追加しない。
7. A/B双方のvalidator、dry-run、差分レビューに合格するまでsource登録を `enabled: false` に保つ。

採番のために既存の内容やGit履歴を作り直さない。作成順を確定できない場合は推測で番号を付けず、対応表の承認を得る。既に公開URLがあるファイルを改名する場合は、旧URLの維持またはredirect方針をA側で先に決める。

`B_Stats_Site` の `work_record_001` から `work_record_010` は共通命名に適合済みであり、改名・再採番しない。

## 新しい生成元を追加する手順

1. 公開リポジトリへ不変な `project_id` とsource登録を追加し、`enabled: false` とする。
2. 生成元へこの共通ルールの参照を置き、`work_record_###` の共通命名を採用する。
3. `html_mode`を選び、metadataと生成元側validatorを用意する。`source_html`ではdeterministic generatorも用意する。
4. Aの受入validatorでHTML安全性、依存、パス、サイズ、metadataを検証するfixtureを追加する。
5. 既存公開物がある場合は、生成元commitと公開中ファイルのdigestを照合して初期provenance manifestを作る。
6. dry-runとno-op同期を確認する。
7. 新規1件でcommit、受入、Pages deploy、公開URL、Slack通知をE2E確認する。
8. 問題がなければsource登録を `enabled: true` にする。

## 導入順

1. この文書を公開リポジトリの受入契約として確定する。
2. 公開リポジトリ側でsource登録、metadata schema、validator、provenance manifest、branch rulesetの扱いを実装する。
3. md-only project向けの `a_rendered` rendererと、両modeに共通する命名・metadata検証を追加する。
4. 各既存projectのMarkdownを棚卸しし、承認済み対応表に従って共通命名へ移行する。
5. `B_Stats_Site` の親ディレクトリリンクを解消し、metadataと生成元側検証を追加する。
6. 公開リポジトリをlegacy PagesからカスタムActions Pagesへ移行し、既存ページの非回帰を確認する。
7. 公開リポジトリにproject indexを追加する。
8. 生成元に手動実行可能な公開要求workflow、公開リポジトリにdry-run可能な受入workflowを追加する。
9. 既存分のno-op同期と、新規1件のE2E公開を確認する。
10. 安定後に生成元`main`へのpush triggerを有効化する。
11. 運用安定後に、publish workflowのFine-grained PAT依存もGitHub Appへ移行する。

## 参考資料

- [GitHub Pagesでカスタムworkflowを使用する](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [GitHub Pagesの公開元を設定する](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [GitHub Actionsのworkflow再帰実行に関する制限](https://docs.github.com/en/actions/concepts/security/github_token)
- [workflow dispatchのREST APIと必要権限](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event)
- [Fine-grained personal access tokenを管理する](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [Slack Incoming WebhookをGitHub Actionsから使用する](https://docs.slack.dev/tools/slack-github-action/sending-data-slack-incoming-webhook/)

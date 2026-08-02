## 概要
- 課題: クリアタイムだけでは、ターゲット外クリックの正確さを含めてプレイ結果を比較できない。
- 目的: 速さと正確さを整数ポイントへ換算し、ひと目で好成績を判断できるスコア方式を追加する。
- 完了条件: `Math.round(10000 / Math.max(クリアタイム（秒） + ミス回数 × 2, 0.01))`でスコアを計算し、Finishへ整数`pt`として表示する。Testは同じ中央位置を3回、Easy・Hardは10回でクリアする。開始・再開時は採用したC 葡萄札を単一表示し、3→2→1で数字面の正方形サイズとviewport中央を維持する。Finish内のRetryを操作可能、ランキングを準備中として無効化し、背景難易度は操作可能に保つ。

## 適用した役割
### Portfolio Planner
- 入力: タイムとミスを組み合わせたスコア方式の要望、比較した5案、既存ゲームフロー。
- 実施内容: ユーザー選択の案4を最終仕様とし、調整後タイムの逆数へ10,000を掛けたポイント方式へ整理した。ランキング、ベスト保存、ランク判定は対象外とした。
- 成果物: `10,000 ÷（タイム + ミス1回につき2秒）`を四捨五入した整数ポイントと、高いほど良いという評価ルール。
- 検証結果: タイム短縮とミス削減のどちらも常に得点上昇へつながることを確認した。
- 未解決事項: 得点分布とミス2秒の重みは実プレイデータがないため未評価。
- 次工程への引き継ぎ: 固定ルールで実装し、重みの再調整は別課題とする。

### Portfolio UI Designer
- 入力: `DESIGN.md`、既存の和色UI、viewport中央固定のFinish表示、Finish後も背景操作を可能にする要件。
- 実施内容: Finishはaction colorの2px境界で強調し、モーダルに見えるscrim・blurは削除した。カウントダウンはA丸枠、B二重枠、C角丸枠、D照準枠、E八角枠の5案を同じ数字で並べ、viewport中央へ固定した。初回スクリーンショットで枠内ラベルが数字と競合したためframe下へ分離した。desktopは横5列を維持し、480px以下は6列gridを使った上段3・下段2の中央寄せとした。さらに、背景との重なりで比較しづらかったため、5案全体を半透明白背景と細枠を持つ一枚の比較パネルへまとめた。
- 成果物: desktopの横5案と、mobileで約80pxのframe・10pxラベル・42px数字を両立する和色のカウントダウン比較パネル。
- 検証結果: Chromiumで1280×900と320×568の5案表示を目視し、desktop横5、mobile上段3・下段2、全ラベルの可読性、横overflowなし、viewport中央を確認した。1280×900、640×800、390×844、375×667、320×568ではEasy・Hard・もう一度がすべて実座標クリックに成功し、Finishカードとも非重複だった。
- 未解決事項: なし。
- 次工程への引き継ぎ: Reviewerへ最終差分とブラウザ証跡を渡す。
- 追加対応: F紅白リング、G四季枠、H重ね色、I色札、J祭印を和色のCSS変数と疑似要素で追加した。desktop・480px以下とも5列×2段とし、320pxでは56px以下のframeと10px・最大2行のラベルで全10案をviewport内へ収める。gradient・shadowは使用しない。
- 追加調整: Reviewer指摘を受け、480px以下のラベルを`DESIGN.md`の最小トークンである10pxへ戻し、最大2行の中央揃えで幅を維持した。
- 最新追加設計: A〜Jの造形比較をA〜Hの色比較へ置き換え、全案を同一の色札形状に統一した。共通アクセント`#F6E6A2`、2px境界、左右のアクセント帯、中央の数字面を共通化し、各案はbase・background・border・textの4色だけを変更する。desktop・mobileとも4列×2段とし、320pxでも全8案を同時表示する。最新差分のブラウザ実動確認は次工程で行う。

### Portfolio Copywriter
- 入力: 案4の計算式、整数ポイント、高いほど良いという評価方向、既存の画面文言。
- 実施内容: ヘッダーを「速く正確にクリアする」目的と計算式が短く伝わる文言へ変更した。未確定表示、Finish注記、live regionもポイント方式と高得点評価へ統一した。
- 成果物: 「速く正確にクリアして、高得点を目指そう。スコア = 10,000 ÷（タイム + ミス1回につき2秒）です。」を基準とする表示文言。
- 検証結果: すべての画面文言を整数ポイント単位と高得点評価へ統一した。
- 未解決事項: なし。
- 次工程への引き継ぎ: 実表示で改行と読みやすさを確認する。
- 追加対応: 1行目をTestの3回固定位置とEasy・Hardの10回ルールへ変更し、2行目のスコア説明を維持した。Finishの視覚注記とlive通知末尾の「高いほど好成績です。」は情報統一のため削除した。

### Portfolio Frontend Engineer
- 入力: 案4の確定式、Finish限定のスコア表示、開始・再開カウントダウン、既存のゲーム状態とアクセシビリティ要件。
- 実施内容: TestボタンをEasy前へ追加し、default Easyを維持した。Testの目標数を3、Easy・Hardを10として進捗・残り・progressbarの`aria-valuemax`と`aria-valuetext`を動的化した。Testはターゲットをarena中央へ一度配置し、3クリックの間移動させない。5案はchoice内にframeとlabelを兄弟要素として配置し、数字のNodeListだけを一括更新してclear時も構造を維持する。難易度無効化、Hard専用class・scroll・grid、Finish・score・pause・quitは維持した。
- 成果物: Test／Easy／Hardの3モード、3／10連動進捗、固定位置Test、DOMを維持する同時5案カウントダウン、480px以下の3＋2比較配置。
- 検証結果: `node --check`合格、HTMLの22 ID重複なし・JavaScriptからの21参照解決、5組のchoice／frame／label／数字要素、CSS波括弧、desktop 5列、480px以下の6列・2列span・下段中央配置、320pxでgroup 296px・frame 82pxとなる寸法、全5案維持、`git diff --check`合格を確認した。
- 未解決事項: なし。
- 次工程への引き継ぎ: Reviewerへ最終差分と検証結果を渡す。
- 追加対応: Finishを非モーダルdialogとしてラベル付けし、内側に「もう一度」とnative disabledの「ランキングを見る」を横並びで追加した。Finish時は上部Startを「スタート」へ戻してdisabledとし、Finish Retryへfocusする。Retryは`startGame`へ接続した。操作ボタンはStart＝朱／白太字、Pause＝淡藍／藍、Quit＝淡赤／濃赤、disabled共通低彩度・opacity 0.55へ整理し、hover・activeはenabled時だけに限定した。Finish非表示時は`aria-hidden=true`かつRetry disabled、表示時だけ両方を反転する。
- 追加静的検証: HTMLの24 ID重複なし・JavaScriptからの参照解決、10組のchoice／frame／label／number、非モーダルdialog、disabledランキング、Finish Retry接続、上部Start無効化、背景難易度有効化、F〜J造形とCSS色変数、mobile 5列、Finish pointer制御を確認した。
- 最新追加実装: HTMLのカウントダウンをA 藍札、B 深緑札、C 葡萄札、D 朱札、E 紺札、F 墨札、G 青磁札、H 柿札の8案へ変更した。CSSは共通の`.countdown-frame--color-card`と8つのmodifierへ整理し、指定された4色をCSS custom propertiesへ設定した。JavaScriptは`[data-countdown-number]`を動的取得する既存実装で8案に対応できるため変更していない。
- 最新静的検証: `node --check`、HTMLの25 ID重複なし・JavaScriptからの22参照解決、8組のchoice／frame／label／number、共通アクセント`#F6E6A2`、指定8パレット、2px境界、左右帯、中央数字面、desktop・mobileの4列、desktop幅500px以下、mobile幅304px以下・gap 8px 4px・frame最大58px・ラベル10px/1.1、旧造形selector不在、gradient・shadow不使用、`git diff --check`合格を確認した。
- 採用案実装: ユーザー指定の「3の案」を3番目のC 葡萄札として採用し、比較用の7案と全ラベルを削除した。薄黄色アクセント`#F6E6A2`、葡萄配色、色札形状を維持し、数字面はpaddingではなく固定の`inline-size`／`block-size`とgrid中央配置で正方形にした。表示枠はdesktop 136px以下、480px以下104px以下へ単一案用に調整した。JavaScriptはNodeListの1要素を既存処理できるため変更していない。

### Portfolio Performance & Accessibility Tester
- 入力: 案4へ変更後のHTML、CSS、JavaScript、既存の非回帰条件。
- 実施内容: Playwright確認で、320×568のクリア時にFinishカードがフォーカスされたStartボタンを覆う中問題1件と、live regionが英字の`pt`を読み上げる軽微問題1件を指摘した。カウントダウン追加後のロジックは合格したが、再開始直後にFinishカードの退場transitionが約140ms残り、数字3と視覚的に重なる所見を追加で確認した。
- 成果物: 既存のモバイルフォーカスと読み上げ修正に加え、Finishを非表示時に即時隠す修正。
- 検証結果: 改修前は640px以下でHard中心が固定headerに覆われる不具合を再現した。修正後は5 viewportすべてで`elementFromPoint`がEasy・Hard・もう一度の各ボタンを返し、座標クリック後に難易度選択とカウント開始を確認した。全ボタンとFinishは非重複。総合シナリオでもカウントダウン、スコア、Hard、live regionが合格し、console error・page error・failed requestは0件だった。
- 未解決事項: 実スクリーンリーダーによる音声確認は未実施。重大な未解決事項は0件。
- 次工程への引き継ぎ: Reviewerへ最終結果を渡す。
- 追加所見: 最終PlaywrightシナリオでTestのターゲット座標が3回とも`x=131, y=137`で不変、進捗・ARIAが3へ連動し、Easy・Hardは10回で完了した。視覚5案に対してlive regionは数字を一度だけ通知し、Finishの「高いほど好成績です。」は視覚・通知の両方から消えている。1280×900と320×568の表示、5 viewportのFinish後実座標クリック、console error・page error・failed request各0件を確認した。
- 追加検証: Playwright `scenario-2026-08-02T06-39-21-380Z`で1280×900と320×568の10案5列×2段、viewport中央、横overflowなしを確認した。Testは`x=131, y=137`の固定位置3回、Hardは10回と縦横scrollを維持した。Start／Pause／Quitは初期・countdown中・running中のdisabled属性、背景・枠・文字・opacityが仕様どおり切り替わった。FinishではRetry enabled、Ranking disabled、上部Start disabled、Retry focus、表示／非表示ARIA連動、runtime error 0件を確認した。
- 追加所見: 初回実動で320pxのFinish後に背景難易度がviewport外へ残る回帰を検知したため、640px以下ではcontrol panelを上部へ戻し、Retryを`preventScroll`付きでfocusするよう修正した。`scenario-2026-08-02T06-40-53-781Z`で1280×900、640×800、390×844、375×667、320×568のFinish中央誤差0、Test／Easy／Hard／Retryの実座標クリックを確認した。
- 再検証: ラベル10px化後の`scenario-2026-08-02T06-45-21-971Z`で320×568の10案5列×2段、最大2行ラベル、viewport中央、横overflowなしを目視・座標検証し、総合シナリオも合格した。
- 未解決事項: 実スクリーンリーダー確認は未実施（非ブロッキング）。重大な未解決事項は0件。
- 次工程への引き継ぎ: 最新差分と3つのPlaywright証跡をReviewerへ渡す。
- 最新差分の検証計画: 1280×900と320×568での全8案表示、4列×2段、横overflowなし、viewport中央、視覚表示8個に対するlive通知1回、およびFinish・各操作・Test／Easy／Hardの非回帰を確認する。
- 最新差分の検証結果: Playwright `scenario-2026-08-02T07-13-38-392Z`で1280×900と320×568のA〜H全8案、4列×2段、viewport中央、全要素viewport内、横overflowなしを確認した。スクリーンショットで同一色札形状、各主色、左右の薄黄色アクセント、10pxラベルを目視確認した。単一live regionの通知、Test固定3回、Hard 10回・縦横scroll、Finish Retry／Ranking、操作ボタン状態も合格し、console error・page error・failed requestは0件だった。
- 最新差分の未解決事項: 実スクリーンリーダー確認は未実施（非ブロッキング）。重大な未解決事項は0件。
- 採用案の検証結果: Playwright `scenario-2026-08-02T07-28-57-742Z`で、葡萄札の白系数字面が320×568では3・2・1すべて44×44px、1280×900ではすべて56×56pxで一致することを実測した。葡萄背景`rgb(251, 247, 250)`、左右アクセント`rgb(246, 230, 162)`、viewport中央誤差0、横overflowなしを確認した。Testは同一座標3回、Hardは10回・縦横scrollを維持し、console error・page error・failed requestは0件だった。
- 採用案の未解決事項: 実スクリーンリーダー確認は未実施（非ブロッキング）。重大な未解決事項は0件。
- 外側パネル変更後の検証結果: Playwright `scenario-2026-08-02T07-55-32-663Z`で、`countdown-display`が背景完全透明・borderなし・padding 0pxであること、葡萄札が320×568で104×104px、1280×900で128×128pxへ拡大されたことを実測した。3・2・1の数字面は44×44px／56×56px、viewport中央誤差0、横overflowなしを維持した。Test固定3回、Hard 10回・縦横scroll、runtime error 0件も確認した。
- 外側パネル変更後の未解決事項: 実スクリーンリーダー確認は未実施（非ブロッキング）。重大な未解決事項は0件。

### Portfolio Reviewer
- 入力: 案4へ更新した実装差分、静的検証、今後のPlaywright検証結果、本Issue記録。
- 実施内容: 案4の実装と初回Playwright結果を確認し、モバイルのフォーカス可視性を中1件、live regionの単位表記を軽微1件として差し戻した。追加要件後は最新4ファイル、Issue記録、静的検証、最終Playwrightレポートとスクリーンショットを再レビューした。
- 成果物: モバイルフォーカス、読み上げ単位、Finish残像の修正差分、および追加要件を含むReady判定。
- 検証結果: 最新の実座標クリックで固定headerがモバイルのHardを覆う不具合を確認し、Ready判定を取り下げてpanel単位スクロールへ差し戻した。修正後は5 viewportの実座標クリック、Finish非重複、総合非回帰、エラー0件を確認し、重大・中・軽微0件でReady判定とした。
- 追加対応: 最終レビューでTest選択中だけdisabled指定がactive色を上書きする軽微1件を検出した。`.difficulty-btn.test.is-active`の詳細度をEasy・Hardと揃え、カウント中もTestの選択色を維持した。
- 検証結果: 修正後のPlaywright `scenario-2026-08-02T04-53-08-588Z`で、Testがdisabled・`aria-pressed=true`のまま選択背景`rgb(245, 177, 153)`、Easy・Hardがdisabled背景`rgb(247, 241, 238)`となること、runtime error 0件を確認した。最終再レビューは重大0・中0・軽微0でReady判定。
- 最新追加要件レビュー: 10案、Finish actions、操作ボタン状態、2本のPlaywright証跡を確認し、重大0・中0・軽微2とした。Issueの待ち表記とmobileラベル8pxを指摘し、ラベルは10px・最大2行へ修正、総合ブラウザ検証を再実行した。
- 最終再レビュー: ラベル10px化後の最新4ファイル、Issue記録、`scenario-2026-08-02T06-45-21-971Z`を確認した。320pxで10案5列×2段、最大2行ラベル、非重複、viewport中央、横overflowなしを確認し、重大0・中0・軽微0でReady判定とした。
- 未解決事項: 実スクリーンリーダー確認は未実施（非ブロッキング）。重大な未解決事項は0件。
- 次工程への引き継ぎ: 最終差分は重大0・中0・軽微0のReady判定を完了し、PR #3でマージ済み。
- 最新差分レビュー: 8色札への置換後の最新3ファイル、Issue記録、`scenario-2026-08-02T07-13-38-392Z`とスクリーンショットを確認した。A〜Hの同一色札形状、指定8配色、共通差し色`#F6E6A2`、desktop・mobileの4列×2段、320pxの10pxラベル、非重複、中央、横overflowなし、ゲーム非回帰を確認し、重大0・中0・軽微0でReady判定とした。
- 採用案レビュー: C 葡萄札の単一表示と数字面固定後の最新3ファイル、Issue記録、`scenario-2026-08-02T07-28-57-742Z`とスクリーンショットを確認した。mobileの3・2・1はすべて44×44px、desktopはすべて56×56px、viewport中央、横overflowなし、Test・Hard非回帰、runtime error 0件を確認し、重大0・中0・軽微0でReady判定とした。
- 外側パネル変更後のレビュー: 最新CSS・Issue記録、`scenario-2026-08-02T07-55-32-663Z`とスクリーンショットを確認した。外側透明・無枠・padding 0px、葡萄札104px／128px、数字面44px／56px、中央、横overflowなし、Test・Hard非回帰、runtime error 0件を確認し、重大0・中0・軽微0でReady判定とした。

## 主要な判断
- 判断: スコアは調整後タイムを分母とする整数ポイント方式にする。
- 理由: 速さと正確さを一つの値へまとめ、高得点を目指す一般的なゲーム表現に合わせるため。
- 判断: 分母の下限を0.01秒とし、最後に`Math.round`で整数化する。
- 理由: ゼロ除算を防ぎ、計算途中の精度を保ったまま安定した整数ポイントを表示するため。
- 判断: ミスは`arena`背景のクリックイベントだけで加算する。
- 理由: 操作ボタン、難易度、ナビゲーション、スクロールバーをゲーム上のミスから確実に除外するため。
- 判断: 視覚結果カードとlive regionを分離する。
- 理由: 詳細なカードを視覚表示しながら、支援技術にはまとまった結果を一度だけ通知するため。
- 判断: クリア時は上部Startを「スタート」へ戻して無効化し、Finish内の「もう一度」へフォーカスを移す。640px以下では操作パネルを固定header下へ戻してから、Retryを`preventScroll`付きでfocusする。
- 理由: 結果確認と再試行を同じカード内で完結させながら、モバイルでも背景難易度をviewport内に保つため。
- 判断: 視覚表示は`pt`、live regionは「ポイント」とする。
- 理由: コンパクトな視覚表示を維持しつつ、支援技術で単位を明確に読み上げるため。
- 判断: カウントダウン中はゲーム進行を止め、Quit以外のゲーム操作を無効化する。
- 理由: 数字を確認してから同じ条件で開始・再開でき、中断手段も失わないようにするため。
- 判断: カウントダウンとFinishは`position: fixed`と50%座標でviewport中央へ統一する。
- 理由: desktop・mobile・Hardのスクロール位置にかかわらず、画面全体の厳密な中央へ結果と開始合図を表示するため。
- 判断: Finishは非表示時に即座に`visibility: hidden`とし、表示時だけopacityとscaleをtransitionさせる。
- 理由: Finishの表示開始アニメーションを維持しながら、再開始カウントの数字3との残像重なりを防ぐため。
- 判断: Finishのscrimとblurは削除し、カードの2px境界と`pointer-events: none`を維持する。
- 理由: 背景操作が可能でもモーダルに見えて操作不能と誤解される表現を避け、操作モデルと見た目を一致させるため。
- 判断: Testはarena中央の同一座標で3回、Easy・Hardは10回とする。
- 理由: 固定位置の入力確認を短時間で行えるTestと、従来の練習モードを明確に分離するため。
- 判断: 比較した8色札から3番目のC 葡萄札を採用し、カウントダウンは単一案だけを表示する。
- 理由: ユーザーの選択を反映し、比較用ラベルや未採用案を本番表示へ残さないため。
- 判断: 数字面はdesktop 56px、480px以下44pxの正方形とし、`inline-size`／`block-size`を同値で固定してgrid中央配置する。
- 理由: 3・2・1のglyph幅に左右されず、白系背景の外形と数字の中央位置を各viewport内で一定に保つため。
- 判断: `countdown-display`の境界・背景・余白・角丸を削除して透明な配置要素とし、葡萄色札自体をdesktop 128px、480px以下104pxの正方形へ拡大する。
- 理由: 外側の赤枠と白塗りパネルをなくし、カウントダウンの主役である葡萄色札だけを明確に見せるため。
- 判断: Finishカード自体は`pointer-events: none`、actions内のbuttonだけ`pointer-events: auto`とする。
- 理由: 非モーダルな背景難易度操作を維持しながら、Retryだけをカード内で操作可能にするため。

## PR・マージ記録
- PR: [#3 feat: improve trackball scoring and game feedback](https://github.com/tj-999-comp/sandbox-pages/pull/3)
- base / head: `main` / `codex/013-add-trackball-score`
- 状態: `MERGED`
- マージ日時: 2026-08-02T08:19:52Z（JST 2026-08-02 17:19:52）
- merge commit: `4f09b4fb493551ca58bcf8f455f54498b4893ab7`
- checks: 設定なし
- GitHub上の変更: 4ファイル（`Issues/Issue_013.md`、`games/trackball-controll-practice.html`、`css/trackball-controll-practice.css`、`scripts/trackball-controll-practice.js`）
- Reviewer最終判定: 重大0・中0・軽微0、Ready。

## 最終結果
- 解決したこと: Test／Easy／Hardと動的進捗、Finish内のRetryと準備中Ranking、上部Startと操作ボタンの状態を維持し、比較した8色札からC 葡萄札を単一カウントダウンとして採用した。3→2→1で中央の白系数字面が同じ正方形サイズを維持するよう整え、外側パネルを透明化して葡萄色札をdesktop 128px・mobile 104pxへ拡大した。
- 変更ファイル: `Issues/Issue_013.md`、`games/trackball-controll-practice.html`、`css/trackball-controll-practice.css`、`scripts/trackball-controll-practice.js`。
- 検証結果: `node --check`、外側パネル用のborder・background・padding・border-radius不在、葡萄色札のdesktop 128px・mobile 104px寸法、CSS波括弧、`git diff --check`に合格した。Playwright `scenario-2026-08-02T07-55-32-663Z`で外側透明・無枠・padding 0px、札の拡大、3・2・1の固定数字面、中央、横overflowなし、Test・Hard非回帰、runtime error 0件を確認した。Reviewerは重大0・中0・軽微0でReady判定し、PR #3は`main`へマージ済み。checksは設定されていない。
- 未解決事項: 実スクリーンリーダー確認は未実施（非ブロッキング）。重大な未解決事項は0件。
- 次アクション: 必須なし。ランキング実装とスコア重みの実プレイ評価は別課題とする。

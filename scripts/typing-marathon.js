(() => {
    "use strict";

    const CHALLENGE_DURATION_MS = 120000;
    const SCORE_MISS_PENALTY = 0.5;
    const COMBO_BONUS_STEP = 20;
    const COMBO_BONUS_POINT = 8;
    const STORAGE_KEYS = {
        ranking: "typingMarathon.top10.v4",
        customBank: "typingMarathon.customBank.v3"
    };

    const TEXTS = {
        ja: {
            hero: "30秒または60秒で計測し、苦手な問題を編集しながら繰り返し練習できるタイピングページです。",
            top: "トップメニュー",
            challenge: "計測",
            practice: "反復",
            ranking: "記録",
            editor: "出題編集",
            challengeReady: "計測は30秒または60秒で進みます。",
            practiceReady: "反復は単語と文章をくり返し練習できます。",
            practiceRunning: "練習を開始しました。",
            pause: "一時停止中です。もう一度押すと再開します。",
            resumed: "再開しました。",
            reset: "ラウンドをリセットしました。この結果は保存されません。",
            timeoutSaved: "指定した時間が終了しました。結果を保存しました。",
            noQuestion: "出題候補がありません。出題編集で追加してください。",
            added: "追加しました。",
            edited: "更新しました。",
            deleted: "削除しました。",
            duplicate: "同じ内容がすでにあります。",
            empty: "空欄は登録できません。",
            displayLabelWord: "単語を登録",
            displayLabelSentence: "文章を登録",
            readingLabel: "読み",
            readingHint: "英語は表示と同じで入力します",
            targetReadingPrefix: "読み",
            rankingEmpty: "まだ記録がありません。",
            resetRanking: "ランキングを消去しました。",
            pauseButton: "一時停止",
            resumeButton: "再開",
            inputLabel: "ここに入力",
            topBack: "トップへ戻る",
            results: "結果",
            play: "プレイ",
            challengeDesc: "30秒/60秒で総合スコアとKPSを計測",
            practiceDesc: "単語/文章を反復練習",
            rankingDesc: "歴代Top10を表示",
            editorDesc: "出題候補を追加・編集・削除",
            editWord: "単語",
            editSentence: "文章",
            practiceWord: "単語",
            practiceSentence: "文章",
            practiceMixed: "ミックス",
            confirmRankingReset: "ランキングを消去しますか？",
            editPromptDisplay: "表示する文字を入力",
            editPromptReading: "読みを入力",
            next: "次の問題",
            start: "スタート",
            resetButton: "リセット",
            addButton: "登録",
            clearRankingButton: "ランキングをリセット"
        },
        en: {
            hero: "Type for 30 or 60 seconds, edit weak prompts, and keep practicing with words and sentences.",
            top: "Top menu",
            challenge: "Challenge",
            practice: "Practice",
            ranking: "Ranking",
            editor: "Prompt editor",
            challengeReady: "Challenge runs for 30 or 60 seconds.",
            practiceReady: "Practice lets you repeat words and sentences.",
            practiceRunning: "Practice started.",
            pause: "Paused. Press again to resume.",
            resumed: "Resumed.",
            reset: "Round reset. This result is not saved.",
            timeoutSaved: "The selected time is up. Result saved.",
            noQuestion: "No prompts available. Add items in Prompt Editor.",
            added: "Added.",
            edited: "Updated.",
            deleted: "Deleted.",
            duplicate: "This item already exists.",
            empty: "Empty input is not allowed.",
            displayLabelWord: "Add word",
            displayLabelSentence: "Add sentence",
            readingLabel: "Reading",
            readingHint: "Same as display for English",
            targetReadingPrefix: "Reading",
            rankingEmpty: "No records yet.",
            resetRanking: "Ranking cleared.",
            pauseButton: "Pause",
            resumeButton: "Resume",
            inputLabel: "Type here",
            topBack: "Back to top",
            results: "Results",
            play: "Play",
            challengeDesc: "Measure score and KPS in 30 or 60 seconds",
            practiceDesc: "Repeat words and sentences",
            rankingDesc: "Show top 10 records",
            editorDesc: "Add, edit, and remove prompts",
            editWord: "Word",
            editSentence: "Sentence",
            practiceWord: "Word",
            practiceSentence: "Sentence",
            practiceMixed: "Mixed",
            confirmRankingReset: "Clear ranking?",
            editPromptDisplay: "Enter display text",
            editPromptReading: "Enter reading",
            next: "Next",
            start: "Start",
            resetButton: "Reset",
            addButton: "Add",
            clearRankingButton: "Clear ranking"
        }
    };

    const BUILTIN_BANK = {
        ja: {
            word: [
                { display: "集中", reading: "しゅうちゅう" },
                { display: "改善", reading: "かいぜん" },
                { display: "計測", reading: "けいそく" },
                { display: "整理", reading: "せいり" },
                { display: "信頼", reading: "しんらい" },
                { display: "成果", reading: "せいか" },
                { display: "設計", reading: "せっけい" }
            ],
            sentence: [
                { display: "山道を越えて星空を見上げる", reading: "やまみちをこえてほしぞらをみあげる" },
                { display: "画面の導線を整えて使いやすくする", reading: "がめんのどうせんをととのえてつかいやすくする" },
                { display: "苦手な問題を見直して練習を続ける", reading: "にがてなもんだいをみなおしてれんしゅうをつづける" }
            ]
        },
        en: {
            word: ["focus", "improve", "measure", "clarity", "signal", "design", "steady"].map((word) => ({ display: word, reading: word })),
            sentence: [
                { display: "We keep improving the typing flow.", reading: "We keep improving the typing flow." },
                { display: "Measure the score and the keystrokes.", reading: "Measure the score and the keystrokes." },
                { display: "Edit weak prompts and practice again.", reading: "Edit weak prompts and practice again." }
            ]
        }
    };

    const VOWELS = new Set(["a", "i", "u", "e", "o"]);
    const hiraFromKata = (s) => s.replace(/[ァ-ヶ]/g, (ch) => String.fromCharCode(ch.charCodeAt(0) - 0x60));
    const BASE = {
        "あ": ["a"], "い": ["i"], "う": ["u", "wu"], "え": ["e"], "お": ["o"],
        "か": ["ka"], "き": ["ki"], "く": ["ku"], "け": ["ke"], "こ": ["ko"],
        "さ": ["sa"], "し": ["shi", "si"], "す": ["su"], "せ": ["se"], "そ": ["so"],
        "た": ["ta"], "ち": ["chi", "ti"], "つ": ["tsu", "tu"], "て": ["te"], "と": ["to"],
        "な": ["na"], "に": ["ni"], "ぬ": ["nu"], "ね": ["ne"], "の": ["no"],
        "は": ["ha"], "ひ": ["hi"], "ふ": ["fu", "hu"], "へ": ["he"], "ほ": ["ho"],
        "ま": ["ma"], "み": ["mi"], "む": ["mu"], "め": ["me"], "も": ["mo"],
        "や": ["ya"], "ゆ": ["yu"], "よ": ["yo"],
        "ら": ["ra"], "り": ["ri"], "る": ["ru"], "れ": ["re"], "ろ": ["ro"],
        "わ": ["wa"], "を": ["wo", "o"],
        "が": ["ga"], "ぎ": ["gi"], "ぐ": ["gu"], "げ": ["ge"], "ご": ["go"],
        "ざ": ["za"], "じ": ["ji", "zi"], "ず": ["zu"], "ぜ": ["ze"], "ぞ": ["zo"],
        "だ": ["da"], "ぢ": ["di", "ji"], "づ": ["du", "zu"], "で": ["de"], "ど": ["do"],
        "ば": ["ba"], "び": ["bi"], "ぶ": ["bu"], "べ": ["be"], "ぼ": ["bo"],
        "ぱ": ["pa"], "ぴ": ["pi"], "ぷ": ["pu"], "ぺ": ["pe"], "ぽ": ["po"],
        "ゔ": ["vu"],
        "ぁ": ["a"], "ぃ": ["i"], "ぅ": ["u"], "ぇ": ["e"], "ぉ": ["o"], "ゎ": ["wa"]
    };
    const YOON = {
        "きゃ": ["kya"], "きゅ": ["kyu"], "きょ": ["kyo"],
        "ぎゃ": ["gya"], "ぎゅ": ["gyu"], "ぎょ": ["gyo"],
        "しゃ": ["sha", "sya"], "しゅ": ["shu", "syu"], "しょ": ["sho", "syo"],
        "じゃ": ["ja", "jya", "zya"], "じゅ": ["ju", "jyu", "zyu"], "じょ": ["jo", "jyo", "zyo"],
        "ちゃ": ["cha", "tya", "cya"], "ちゅ": ["chu", "tyu", "cyu"], "ちょ": ["cho", "tyo", "cyo"],
        "にゃ": ["nya"], "にゅ": ["nyu"], "にょ": ["nyo"],
        "ひゃ": ["hya"], "ひゅ": ["hyu"], "ひょ": ["hyo"],
        "びゃ": ["bya"], "びゅ": ["byu"], "びょ": ["byo"],
        "ぴゃ": ["pya"], "ぴゅ": ["pyu"], "ぴょ": ["pyo"],
        "みゃ": ["mya"], "みゅ": ["myu"], "みょ": ["myo"],
        "りゃ": ["rya"], "りゅ": ["ryu"], "りょ": ["ryo"]
    };
    const SMALL = new Set(["ゃ", "ゅ", "ょ", "ぁ", "ぃ", "ぅ", "ぇ", "ぉ"]);
    const SOKUON = "っ";
    const CHOON = "ー";

    const dom = {
        heroText: document.querySelector(".tm-hero p"),
        topHeading: document.querySelector("#tm-screen-top h2"),
        menuCards: Array.from(document.querySelectorAll(".tm-menuCard")),
        screens: Array.from(document.querySelectorAll("[data-screen]")),
        openModeButtons: Array.from(document.querySelectorAll("[data-open-mode]")),
        backTopButtons: Array.from(document.querySelectorAll("[data-back-top]")),
        langButtons: Array.from(document.querySelectorAll("[data-lang]")),
        playTitle: document.getElementById("tm-play-title"),
        playControls: document.getElementById("tm-play-controls"),
        practiceKindWrap: document.getElementById("tm-practice-kind-wrap"),
        practiceKindButtons: Array.from(document.querySelectorAll("[data-practice-kind]")),
        durationButtons: Array.from(document.querySelectorAll("[data-duration]")),
        prompt: document.getElementById("tm-prompt"),
        target: document.getElementById("tm-target"),
        reading: document.getElementById("tm-reading"),
        input: document.getElementById("tm-input"),
        message: document.getElementById("tm-message"),
        time: document.getElementById("tm-time"),
        score: document.getElementById("tm-score"),
        kps: document.getElementById("tm-kps"),
        rScore: document.getElementById("tm-r-score"),
        rKps: document.getElementById("tm-r-kps"),
        rAcc: document.getElementById("tm-r-acc"),
        rKeys: document.getElementById("tm-r-keys"),
        rMiss: document.getElementById("tm-r-miss"),
        screenRankingHeading: document.querySelector("#tm-screen-ranking h2"),
        screenEditorHeading: document.querySelector("#tm-screen-editor h2"),
        resultHeading: document.querySelector(".tm-card--result h3"),
        playHeading: document.querySelector(".tm-card--play h3"),
        startBtn: document.getElementById("tm-start"),
        pauseBtn: document.getElementById("tm-pause"),
        resetBtn: document.getElementById("tm-reset"),
        nextBtn: document.getElementById("tm-next"),
        rankingList: document.getElementById("tm-ranking"),
        rankingSummary: document.getElementById("tm-ranking-summary"),
        clearRankingBtn: document.getElementById("tm-clear-ranking"),
        resultModal: document.getElementById("tm-result-modal"),
        resultRetryBtn: document.getElementById("tm-result-retry"),
        resultCloseBtn: document.getElementById("tm-result-close"),
        editLangButtons: Array.from(document.querySelectorAll("[data-edit-lang]")),
        editKindButtons: Array.from(document.querySelectorAll("[data-edit-kind]")),
        registerForm: document.getElementById("tm-register-form"),
        registerLabel: document.getElementById("tm-register-label"),
        registerDisplay: document.getElementById("tm-register-display"),
        registerReading: document.getElementById("tm-register-reading"),
        customList: document.getElementById("tm-custom-list")
    };

    const state = {
        screen: "top",
        playMode: "challenge",
        practiceKind: "word",
        lang: "ja",
        editLang: "ja",
        editKind: "word",
        isRunning: false,
        isPaused: false,
        timerId: null,
        activeRunStartedAt: 0,
        elapsedMsBeforePause: 0,
        currentPrompt: null,
        targetText: "",
        targetOptions: [],
        typedIndex: 0,
        inputBuffer: "",
        totalKeyCount: 0,
        correctKeyCount: 0,
        missKeyCount: 0,
        combo: 0,
        bestCombo: 0,
        ranking: normalizeRanking(readJson(STORAGE_KEYS.ranking, [])),
        rankingFilterLang: "ja",
        rankingFilterSeconds: 60,
        challengeDurationMs: 60000,
        customBank: normalizeBank(readJson(STORAGE_KEYS.customBank, null) || BUILTIN_BANK)
    };

    if (!readJson(STORAGE_KEYS.customBank, null)) {
        saveJson(STORAGE_KEYS.customBank, state.customBank);
    }

    function readJson(key, fallback) {
        try {
            const raw = localStorage.getItem(key);
            if (!raw) return fallback;
            return JSON.parse(raw);
        } catch (_) {
            return fallback;
        }
    }

    function saveJson(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }

    function normalizeRanking(input) {
        if (!Array.isArray(input)) return [];
        return input.map((entry) => ({
            at: typeof entry?.at === "string" ? entry.at : new Date().toISOString(),
            score: Number(entry?.score) || 0,
            kps: Number(entry?.kps) || 0,
            accuracy: Number(entry?.accuracy) || 0,
            totalKeys: Number(entry?.totalKeys) || 0,
            miss: Number(entry?.miss) || 0,
            lang: entry?.lang === "en" ? "en" : "ja",
            duration: Number(entry?.duration) === 30 ? 30 : 60
        }));
    }

    function normalizeEntry(lang, entry) {
        if (typeof entry === "string") {
            return { display: entry, reading: entry };
        }
        if (!entry || typeof entry !== "object") {
            return null;
        }
        const display = typeof entry.display === "string" ? entry.display.trim() : "";
        const reading = typeof entry.reading === "string" ? entry.reading.trim() : "";
        if (!display) return null;
        if (lang === "ja") {
            return { display, reading: reading || display };
        }
        return { display, reading: reading || display };
    }

    function normalizeBank(input) {
        const blank = { ja: { word: [], sentence: [] }, en: { word: [], sentence: [] } };
        if (!input || typeof input !== "object") return blank;
        ["ja", "en"].forEach((lang) => {
            ["word", "sentence"].forEach((kind) => {
                const list = Array.isArray(input[lang]?.[kind]) ? input[lang][kind] : [];
                blank[lang][kind] = list.map((entry) => normalizeEntry(lang, entry)).filter(Boolean);
            });
        });
        return blank;
    }

    function isLikelySentenceEntry(entry, lang) {
        const text = String(entry?.display || "").trim();
        if (!text) return false;
        if (/[\s\n\r]/.test(text)) return true;
        if (/[。．、,，.!?！？:;；]/.test(text)) return true;
        if (lang === "ja") {
            return text.length >= 8;
        }
        return false;
    }

    function t(key, lang = state.lang) {
        return TEXTS[lang][key] || TEXTS.ja[key] || "";
    }

    function tokenizeKana(hira) {
        const tokens = [];
        for (let i = 0; i < hira.length; i += 1) {
            const c = hira[i];
            const n = hira[i + 1];
            if (c === SOKUON || c === CHOON) {
                tokens.push(c);
                continue;
            }
            if (n && SMALL.has(n) && YOON[c + n]) {
                tokens.push(c + n);
                i += 1;
                continue;
            }
            tokens.push(c);
        }
        return tokens;
    }

    function lastVowelOf(s) {
        for (let i = s.length - 1; i >= 0; i -= 1) {
            const ch = s[i].toLowerCase();
            if (VOWELS.has(ch)) return ch;
        }
        return "";
    }

    function romajiOptionsFromTokens(tokens, opt = { choon: "both" }) {
        const memo = new Map();
        function rec(index, built, lastVowel, geminate) {
            const cacheKey = `${index}|${built}|${lastVowel}|${geminate ? 1 : 0}|${opt.choon}`;
            if (memo.has(cacheKey)) return memo.get(cacheKey);
            if (index >= tokens.length) return [built];
            const token = tokens[index];
            let out = [];
            if (token === CHOON) {
                if (opt.choon === "dash-only") {
                    out = rec(index + 1, `${built}-`, lastVowel, false);
                } else {
                    if (lastVowel) out = out.concat(rec(index + 1, `${built}${lastVowel}`, lastVowel, false));
                    out = out.concat(rec(index + 1, `${built}-`, lastVowel, false));
                }
                memo.set(cacheKey, out);
                return out;
            }
            if (token === SOKUON) {
                out = out.concat(rec(index + 1, built, lastVowel, true));
                out = out.concat(rec(index + 1, `${built}xtu`, "u", false));
                out = out.concat(rec(index + 1, `${built}ltsu`, "u", false));
                memo.set(cacheKey, out);
                return out;
            }
            if (token === "ん") {
                const next = tokens[index + 1];
                const heads = !next || next === CHOON || next === SOKUON ? [] : (YOON[next] || BASE[next] || []).map((s) => s[0].toLowerCase());
                const forms = heads.some((h) => VOWELS.has(h) || h === "y") ? ["n'", "nn"] : ["n", "nn"];
                forms.forEach((form) => {
                    out = out.concat(rec(index + 1, `${built}${form}`, lastVowel, false));
                });
                memo.set(cacheKey, out);
                return out;
            }
            const baseList = YOON[token] || BASE[token] || [];
            baseList.forEach((base) => {
                const withGeminate = geminate ? `${base[0]}${base}` : base;
                out = out.concat(rec(index + 1, `${built}${withGeminate}`, lastVowelOf(withGeminate) || lastVowel, false));
            });
            memo.set(cacheKey, out);
            return out;
        }
        return Array.from(new Set(rec(0, "", "", false)));
    }

    function buildRomajiOptions(kana) {
        const hira = hiraFromKata(kana);
        return romajiOptionsFromTokens(tokenizeKana(hira));
    }

    function chooseCanon(options) {
        return options.slice().sort((a, b) => {
            const ap = (a.match(/[^a-z]/g) || []).length;
            const bp = (b.match(/[^a-z]/g) || []).length;
            if (ap !== bp) return ap - bp;
            if (a.length !== b.length) return a.length - b.length;
            return a.localeCompare(b);
        })[0] || "";
    }

    function buildTargetData(prompt, lang) {
        if (!prompt) return { preview: "", options: [] };
        if (lang === "ja") {
            const options = buildRomajiOptions(prompt.reading);
            return { preview: chooseCanon(options), options };
        }
        return { preview: prompt.reading, options: [prompt.reading] };
    }

    function setScreen(screen) {
        state.screen = screen;
        dom.screens.forEach((node) => {
            const active = node.id === `tm-screen-${screen}`;
            node.hidden = !active;
            node.classList.toggle("is-active", active);
        });
    }

    function hideResultModal() {
        if (!dom.resultModal) return;
        dom.resultModal.hidden = true;
        dom.resultModal.setAttribute("aria-hidden", "true");
    }

    function showResultModal() {
        if (!dom.resultModal) return;
        dom.resultModal.hidden = false;
        dom.resultModal.setAttribute("aria-hidden", "false");
    }

    function goTop() {
        if (state.isRunning) resetRound();
        setScreen("top");
    }

    function openMode(mode) {
        if (mode === "ranking") {
            renderRanking();
            setScreen("ranking");
            return;
        }
        if (mode === "editor") {
            renderEditor();
            setScreen("editor");
            return;
        }
        state.playMode = mode;
        state.practiceKind = mode === "challenge" ? "mixed" : "word";
        dom.playTitle.textContent = mode === "challenge" ? "計測" : "反復";
        dom.practiceKindWrap.hidden = mode === "challenge";
        updatePracticeKindButtons();
        resetRoundUiOnly();
        setMessage(mode === "challenge" ? t("challengeReady") : t("practiceReady"));
        setScreen("play");
    }

    function setLang(lang) {
        state.lang = lang;
        dom.langButtons.forEach((button) => {
            const active = button.dataset.lang === lang;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-pressed", String(active));
        });
        renderStaticText();
        if (state.screen === "play") {
            resetRoundUiOnly();
            setMessage(state.playMode === "challenge" ? t("challengeReady") : t("practiceReady"));
        }
    }

    function updatePracticeKindButtons() {
        dom.practiceKindButtons.forEach((button) => {
            const active = button.dataset.practiceKind === state.practiceKind;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-pressed", String(active));
        });
    }

    function resetStats() {
        state.totalKeyCount = 0;
        state.correctKeyCount = 0;
        state.missKeyCount = 0;
        state.combo = 0;
        state.bestCombo = 0;
        renderLiveStats();
        renderResult();
    }

    function startTimer() {
        stopTimer();
        state.timerId = window.setInterval(updateTimer, 100);
        updateTimer();
    }

    function stopTimer() {
        if (state.timerId) {
            window.clearInterval(state.timerId);
            state.timerId = null;
        }
    }

    function elapsedMsNow() {
        if (!state.isRunning || state.isPaused) return state.elapsedMsBeforePause;
        return state.elapsedMsBeforePause + (Date.now() - state.activeRunStartedAt);
    }

    function getElapsedSeconds() {
        return Math.max(elapsedMsNow(), 1) / 1000;
    }

    function startRound() {
        if (state.isRunning) return;
        state.isRunning = true;
        state.isPaused = false;
        state.elapsedMsBeforePause = 0;
        state.activeRunStartedAt = Date.now();
        resetStats();
        state.inputBuffer = "";
        dom.startBtn.disabled = true;
        dom.pauseBtn.disabled = false;
        dom.pauseBtn.textContent = t("pauseButton");
        dom.resetBtn.disabled = false;
        dom.nextBtn.disabled = state.playMode !== "practice";
        dom.playControls?.classList.add("is-locked");
        hideResultModal();
        pickNextTarget();
        if (state.playMode === "challenge") {
            startTimer();
        } else {
            dom.time.textContent = "--";
            setMessage(t("practiceRunning"));
        }
    }

    function updateTimer() {
        const remain = Math.max(state.challengeDurationMs - elapsedMsNow(), 0);
        dom.time.textContent = `${(remain / 1000).toFixed(1)}s`;
        if (remain <= 0) finishChallenge();
    }

    function finishChallenge() {
        if (!state.isRunning) return;
        state.elapsedMsBeforePause = state.challengeDurationMs;
        stopRound({ persistResult: true, message: t("timeoutSaved") });
    }

    function togglePause() {
        if (!state.isRunning) return;
        if (!state.isPaused) {
            state.elapsedMsBeforePause = elapsedMsNow();
            state.isPaused = true;
            dom.pauseBtn.textContent = t("resumeButton");
            stopTimer();
            setMessage(t("pause"));
            return;
        }
        state.isPaused = false;
        state.activeRunStartedAt = Date.now();
        dom.pauseBtn.textContent = t("pauseButton");
        if (state.playMode === "challenge") startTimer();
        setMessage(t("resumed"));
    }

    function resetRound() {
        stopRound({ persistResult: false, message: t("reset") });
    }

    function stopRound(options) {
        if (!state.isRunning) {
            resetRoundUiOnly();
            return;
        }
        state.elapsedMsBeforePause = elapsedMsNow();
        state.isRunning = false;
        state.isPaused = false;
        stopTimer();
        dom.startBtn.disabled = false;
        dom.pauseBtn.disabled = true;
        dom.pauseBtn.textContent = t("pauseButton");
        dom.resetBtn.disabled = true;
        dom.nextBtn.disabled = true;
        dom.playControls?.classList.remove("is-locked");
        renderLiveStats();
        renderResult();
        if (state.playMode === "challenge" && options.persistResult) {
            saveRanking({
                at: new Date().toISOString(),
                score: calcScore(),
                kps: calcKps(getElapsedSeconds()),
                accuracy: calcAccuracy(),
                totalKeys: state.totalKeyCount,
                miss: state.missKeyCount,
                lang: state.lang,
                duration: state.challengeDurationMs / 1000
            });
            renderRanking();
            showResultModal();
        } else {
            hideResultModal();
        }
        setMessage(options.message || "");
    }

    function resetRoundUiOnly() {
        state.currentPrompt = null;
        state.targetText = "";
        state.targetOptions = [];
        state.typedIndex = 0;
        state.inputBuffer = "";
        state.elapsedMsBeforePause = 0;
        state.activeRunStartedAt = 0;
        state.isRunning = false;
        state.isPaused = false;
        stopTimer();
        resetStats();
        renderTarget();
        dom.startBtn.disabled = false;
        dom.pauseBtn.disabled = true;
        dom.pauseBtn.textContent = t("pauseButton");
        dom.resetBtn.disabled = true;
        dom.nextBtn.disabled = true;
        dom.time.textContent = state.playMode === "challenge" ? `${(state.challengeDurationMs / 1000).toFixed(1)}s` : "--";
        dom.prompt.textContent = t("promptInitial");
        dom.playControls?.classList.remove("is-locked");
        hideResultModal();
    }

    function getPool() {
        const custom = state.customBank[state.lang];
        if (state.practiceKind === "word") {
            const words = custom.word.filter((entry) => !isLikelySentenceEntry(entry, state.lang));
            return words.length ? words : [...custom.word];
        }
        if (state.practiceKind === "sentence") {
            const sentences = [
                ...custom.sentence,
                ...custom.word.filter((entry) => isLikelySentenceEntry(entry, state.lang))
            ];
            return sentences.length ? sentences : [...custom.sentence];
        }
        if (state.playMode === "challenge") {
            return [...custom.word, ...custom.sentence];
        }
        return [...custom.word, ...custom.sentence];
    }

    function pickNextTarget() {
        const pool = getPool();
        if (!pool.length) {
            state.currentPrompt = null;
            state.targetText = "";
            state.typedIndex = 0;
            renderTarget();
            setMessage(t("noQuestion"));
            return;
        }
        state.currentPrompt = pool[Math.floor(Math.random() * pool.length)];
        const targetData = buildTargetData(state.currentPrompt, state.lang);
        state.targetText = targetData.preview;
        state.targetOptions = targetData.options;
        state.typedIndex = 0;
        state.inputBuffer = "";
        renderTarget();
    }

    function buildReadingSegments(reading) {
        const tokens = tokenizeKana(hiraFromKata(reading));
        let offset = 0;
        return tokens.map((token) => {
            let romaji = token;
            if (token === SOKUON) romaji = "xtu";
            else if (token === CHOON) romaji = "-";
            else if (token === "ん") romaji = "n";
            else if (YOON[token]) romaji = YOON[token][0];
            else if (BASE[token]) romaji = BASE[token][0];
            const start = offset;
            const end = offset + romaji.length;
            offset = end;
            const current = state.typedIndex;
            return {
                token,
                romaji,
                start,
                state: current >= end ? "done" : (current >= start ? "active" : "todo")
            };
        });
    }

    function renderReadingSegments() {
        if (!dom.reading) return;
        if (!state.currentPrompt || state.lang !== "ja") {
            dom.reading.innerHTML = "";
            return;
        }
        const segments = buildReadingSegments(state.currentPrompt.reading);
        dom.reading.innerHTML = segments.map((segment) => {
            let romajiHtml;
            if (segment.state === "active") {
                const nextCharIndex = state.typedIndex - segment.start;
                romajiHtml = segment.romaji.split("").map((ch, i) =>
                    i === nextCharIndex
                        ? `<span class="tm-romajiNext">${escapeHtml(ch)}</span>`
                        : escapeHtml(ch)
                ).join("");
            } else {
                romajiHtml = escapeHtml(segment.romaji);
            }
            return `<span class="tm-readingPart" data-state="${segment.state}"><span class="tm-readingPart__romaji">${romajiHtml}</span></span>`;
        }).join("");
    }

    function renderTarget() {
        if (!state.currentPrompt) {
            dom.target.textContent = "---";
            dom.reading.textContent = "";
            return;
        }
        const progressIndex = state.targetText.length > 0
            ? Math.min(state.currentPrompt.display.length, Math.round((state.typedIndex / state.targetText.length) * state.currentPrompt.display.length))
            : 0;
        const done = escapeHtml(state.currentPrompt.display.slice(0, progressIndex));
        const remain = escapeHtml(state.currentPrompt.display.slice(progressIndex));
        dom.target.innerHTML = `<span class="tm-target__done">${done}</span><span class="tm-target__remain">${remain}</span>`;
        renderReadingSegments();
    }

    function onKeydown(event) {
        if (!state.isRunning || state.isPaused) return;
        if (event.key === "Tab") {
            event.preventDefault();
            return;
        }
        if (event.key.length === 1 || event.key === "Backspace") {
            state.totalKeyCount += 1;
        }
        if (event.key === "Backspace") {
            if (state.typedIndex > 0) {
                state.typedIndex -= 1;
                state.inputBuffer = state.inputBuffer.slice(0, -1);
                state.targetOptions = (state.currentPrompt ? buildTargetData(state.currentPrompt, state.lang).options : []).filter((option) => option.toLowerCase().startsWith(state.inputBuffer.toLowerCase()));
                state.combo = 0;
                renderTarget();
            }
            event.preventDefault();
            renderLiveStats();
            return;
        }
        if (event.key.length !== 1) return;
        const nextInput = `${state.inputBuffer}${event.key}`;
        const normalizedInput = nextInput.toLowerCase();
        const matchingOptions = state.targetOptions.filter((option) => option.toLowerCase().startsWith(normalizedInput));
        if (!matchingOptions.length) {
            state.missKeyCount += 1;
            state.combo = 0;
            event.preventDefault();
            renderLiveStats();
            return;
        }
        state.inputBuffer = nextInput;
        state.correctKeyCount += 1;
        state.combo += 1;
        state.bestCombo = Math.max(state.bestCombo, state.combo);
        state.typedIndex = normalizedInput.length;
        state.targetOptions = matchingOptions;
        if (matchingOptions.some((option) => option.toLowerCase() === normalizedInput)) {
            pickNextTarget();
        } else {
            renderTarget();
        }
        event.preventDefault();
        renderLiveStats();
    }

    function calcScore() {
        const comboBonus = Math.floor(state.bestCombo / COMBO_BONUS_STEP) * COMBO_BONUS_POINT;
        return Math.max(Math.round(state.correctKeyCount - state.missKeyCount * SCORE_MISS_PENALTY + comboBonus), 0);
    }

    function calcKps(elapsedSec) {
        if (!Number.isFinite(elapsedSec) || elapsedSec <= 0) return 0;
        return (state.totalKeyCount - state.missKeyCount) / elapsedSec;
    }

    function calcAccuracy() {
        if (state.totalKeyCount <= 0) return 0;
        return (state.correctKeyCount / state.totalKeyCount) * 100;
    }

    function renderLiveStats() {
        dom.score.textContent = String(calcScore());
        dom.kps.textContent = calcKps(getElapsedSeconds()).toFixed(2);
    }

    function renderResult() {
        dom.rScore.textContent = String(calcScore());
        dom.rKps.textContent = calcKps(getElapsedSeconds()).toFixed(2);
        dom.rAcc.textContent = `${calcAccuracy().toFixed(1)}%`;
        dom.rKeys.textContent = String(state.totalKeyCount);
        dom.rMiss.textContent = String(state.missKeyCount);
    }

    function saveRanking(entry) {
        state.ranking = normalizeRanking([...state.ranking, entry]).sort((a, b) => b.score - a.score || b.kps - a.kps).slice(0, 10);
        saveJson(STORAGE_KEYS.ranking, state.ranking);
    }

    function renderRanking() {
        dom.rankingList.innerHTML = "";
        const filtered = state.ranking.filter((row) => row.lang === state.rankingFilterLang && row.duration === state.rankingFilterSeconds);
        if (dom.rankingSummary) {
            dom.rankingSummary.textContent = `${state.rankingFilterLang === "en" ? "English" : "日本語"} / ${state.rankingFilterSeconds}秒`;
        }
        if (!filtered.length) {
            const li = document.createElement("li");
            li.textContent = t("rankingEmpty");
            dom.rankingList.appendChild(li);
            return;
        }
        filtered.forEach((row, index) => {
            const li = document.createElement("li");
            const date = new Date(row.at);
            const langLabel = row.lang === "en" ? "EN" : "JA";
            li.textContent = `${index + 1}位  ${Math.round(row.score)}pt  KPS ${Number(row.kps).toFixed(2)}  正答率 ${Number(row.accuracy).toFixed(1)}%  ${langLabel}  ${row.duration}秒  ${date.toLocaleDateString("ja-JP")}`;
            dom.rankingList.appendChild(li);
        });
    }

    function updateDurationButtons() {
        dom.durationButtons.forEach((button) => {
            const active = Number(button.dataset.duration) === state.challengeDurationMs / 1000;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-pressed", String(active));
        });
    }

    function updateRankingFilterButtons() {
        document.querySelectorAll("[data-ranking-lang]").forEach((button) => {
            const active = button.dataset.rankingLang === state.rankingFilterLang;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-selected", String(active));
        });
        document.querySelectorAll("[data-ranking-seconds]").forEach((button) => {
            const active = Number(button.dataset.rankingSeconds) === state.rankingFilterSeconds;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-selected", String(active));
        });
    }

    function updateEditControls() {
        dom.editLangButtons.forEach((button) => {
            const active = button.dataset.editLang === state.editLang;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-selected", String(active));
        });
        dom.editKindButtons.forEach((button) => {
            const active = button.dataset.editKind === state.editKind;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-selected", String(active));
            button.textContent = button.dataset.editKind === "word" ? t("editWord", state.editLang) : t("editSentence", state.editLang);
        });
        dom.registerLabel.textContent = state.editKind === "word" ? t("displayLabelWord", state.editLang) : t("displayLabelSentence", state.editLang);
        dom.registerDisplay.placeholder = t("editPromptDisplay", state.editLang);
        dom.registerReading.placeholder = t("editPromptReading", state.editLang);
        dom.registerReading.hidden = state.editLang !== "ja";
        dom.registerReading.required = state.editLang === "ja";
    }

    function renderEditor() {
        updateEditControls();
        dom.customList.innerHTML = "";
        const list = state.customBank[state.editLang][state.editKind];
        if (!list.length) {
            const li = document.createElement("li");
            li.textContent = t("rankingEmpty", state.editLang);
            dom.customList.appendChild(li);
            return;
        }
        list.forEach((item) => {
            const li = document.createElement("li");
            const text = document.createElement("span");
            text.className = "tm-itemText";
            text.innerHTML = `${escapeHtml(item.display)}${state.editLang === "ja" ? `<span class="tm-itemMeta">${escapeHtml(item.reading)}</span>` : ""}`;
            const actions = document.createElement("div");
            actions.className = "tm-inlineActions";
            const edit = document.createElement("button");
            edit.type = "button";
            edit.className = "tm-btn";
            edit.textContent = state.editLang === "ja" ? "編集" : "Edit";
            edit.addEventListener("click", () => editItem(item));
            const del = document.createElement("button");
            del.type = "button";
            del.className = "tm-delete";
            del.textContent = state.editLang === "ja" ? "削除" : "Delete";
            del.addEventListener("click", () => removeItem(item));
            actions.appendChild(edit);
            actions.appendChild(del);
            li.appendChild(text);
            li.appendChild(actions);
            dom.customList.appendChild(li);
        });
    }

    function getEditingList() {
        return state.customBank[state.editLang][state.editKind];
    }

    function serializeEntry(entry, lang) {
        return lang === "ja" ? `${entry.display}|${entry.reading}` : entry.display;
    }

    function addItem() {
        const display = dom.registerDisplay.value.trim();
        const reading = (state.editLang === "ja" ? dom.registerReading.value : dom.registerDisplay.value).trim();
        if (!display || !reading) {
            setMessage(t("empty", state.editLang));
            return;
        }
        const list = getEditingList();
        const candidate = normalizeEntry(state.editLang, { display, reading });
        if (list.some((item) => serializeEntry(item, state.editLang) === serializeEntry(candidate, state.editLang))) {
            setMessage(t("duplicate", state.editLang));
            return;
        }
        list.push(candidate);
        saveJson(STORAGE_KEYS.customBank, state.customBank);
        dom.registerDisplay.value = "";
        dom.registerReading.value = "";
        renderEditor();
        setMessage(t("added", state.editLang));
    }

    function editItem(item) {
        const nextDisplay = window.prompt(t("editPromptDisplay", state.editLang), item.display);
        if (typeof nextDisplay !== "string") return;
        const display = nextDisplay.trim();
        const nextReading = state.editLang === "ja" ? window.prompt(t("editPromptReading", state.editLang), item.reading) : nextDisplay;
        if (typeof nextReading !== "string") return;
        const reading = nextReading.trim();
        if (!display || !reading) {
            setMessage(t("empty", state.editLang));
            return;
        }
        const list = getEditingList();
        const idx = list.indexOf(item);
        if (idx < 0) return;
        const candidate = normalizeEntry(state.editLang, { display, reading });
        if (list.some((row, rowIdx) => rowIdx !== idx && serializeEntry(row, state.editLang) === serializeEntry(candidate, state.editLang))) {
            setMessage(t("duplicate", state.editLang));
            return;
        }
        list[idx] = candidate;
        saveJson(STORAGE_KEYS.customBank, state.customBank);
        renderEditor();
        setMessage(t("edited", state.editLang));
    }

    function removeItem(item) {
        state.customBank[state.editLang][state.editKind] = getEditingList().filter((row) => row !== item);
        saveJson(STORAGE_KEYS.customBank, state.customBank);
        renderEditor();
        setMessage(t("deleted", state.editLang));
    }

    function renderStaticText() {
        if (dom.heroText) dom.heroText.textContent = t("hero");
        if (dom.resultHeading) dom.resultHeading.textContent = "結果";
        if (dom.playHeading) dom.playHeading.textContent = "プレイ";
        dom.startBtn.textContent = t("start");
        dom.pauseBtn.textContent = state.isPaused ? t("resumeButton") : t("pauseButton");
        dom.nextBtn.textContent = t("next");
        dom.resetBtn.textContent = t("resetButton");
        dom.registerForm.querySelector("button[type='submit']").textContent = t("addButton", state.editLang);
        dom.clearRankingBtn.textContent = t("clearRankingButton");
        dom.backTopButtons.forEach((button) => { button.textContent = t("topBack"); });
        updatePracticeKindButtons();
        updateDurationButtons();
        updateRankingFilterButtons();
        renderEditor();
        renderRanking();
        if (state.playMode === "challenge") {
            dom.playTitle.textContent = t("challenge");
        } else {
            dom.playTitle.textContent = t("practice");
        }
    }

    function setMessage(text) {
        if (dom.message) dom.message.textContent = text;
    }

    function escapeHtml(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    dom.openModeButtons.forEach((button) => {
        button.addEventListener("click", () => openMode(button.dataset.openMode));
    });
    dom.backTopButtons.forEach((button) => button.addEventListener("click", goTop));
    dom.langButtons.forEach((button) => button.addEventListener("click", () => {
        const lang = button.dataset.lang;
        if (lang && lang !== state.lang) setLang(lang);
    }));
    dom.practiceKindButtons.forEach((button) => button.addEventListener("click", () => {
        const kind = button.dataset.practiceKind;
        if (!kind || kind === state.practiceKind) return;
        state.practiceKind = kind;
        updatePracticeKindButtons();
        if (state.playMode === "practice" && state.isRunning) pickNextTarget();
    }));
    dom.durationButtons.forEach((button) => button.addEventListener("click", () => {
        if (state.isRunning) return;
        const duration = Number(button.dataset.duration);
        if (![30, 60].includes(duration)) return;
        state.challengeDurationMs = duration * 1000;
        updateDurationButtons();
        if (state.playMode === "challenge") {
            dom.time.textContent = `${duration.toFixed(1)}s`;
        }
    }));
    dom.editLangButtons.forEach((button) => button.addEventListener("click", () => {
        const lang = button.dataset.editLang;
        if (!lang || lang === state.editLang) return;
        state.editLang = lang;
        renderEditor();
    }));
    dom.editKindButtons.forEach((button) => button.addEventListener("click", () => {
        const kind = button.dataset.editKind;
        if (!kind || kind === state.editKind) return;
        state.editKind = kind;
        renderEditor();
    }));
    dom.startBtn.addEventListener("click", startRound);
    dom.pauseBtn.addEventListener("click", togglePause);
    dom.resetBtn.addEventListener("click", resetRound);
    dom.nextBtn.addEventListener("click", () => {
        if (state.isRunning && state.playMode === "practice") pickNextTarget();
    });
    document.querySelectorAll("[data-ranking-lang]").forEach((button) => button.addEventListener("click", () => {
        const lang = button.dataset.rankingLang;
        if (!lang || lang === state.rankingFilterLang) return;
        state.rankingFilterLang = lang;
        updateRankingFilterButtons();
        renderRanking();
    }));
    document.querySelectorAll("[data-ranking-seconds]").forEach((button) => button.addEventListener("click", () => {
        const seconds = Number(button.dataset.rankingSeconds);
        if (![30, 60].includes(seconds) || seconds === state.rankingFilterSeconds) return;
        state.rankingFilterSeconds = seconds;
        updateRankingFilterButtons();
        renderRanking();
    }));
    document.addEventListener("keydown", onKeydown);
    dom.clearRankingBtn.addEventListener("click", () => {
        if (!window.confirm(t("confirmRankingReset"))) return;
        state.ranking = [];
        saveJson(STORAGE_KEYS.ranking, []);
        renderRanking();
        setMessage(t("resetRanking"));
    });
    dom.registerForm.addEventListener("submit", (event) => {
        event.preventDefault();
        addItem();
    });
    if (dom.resultRetryBtn) {
        dom.resultRetryBtn.addEventListener("click", () => {
            hideResultModal();
            startRound();
        });
    }
    if (dom.resultCloseBtn) {
        dom.resultCloseBtn.addEventListener("click", hideResultModal);
    }

    renderStaticText();
    setLang("ja");
    setScreen("top");
    resetRoundUiOnly();
})();

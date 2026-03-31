(() => {
    'use strict';
    // ===== Tuning =====
    const LANES = 5, DESCENT = 56, SIZE = 92, BOTTOM_MARGIN = 18, DAMAGE_ON_HIT = 15, HITSTOP = 70;
    const SHIELD_TIME = 1200, SHIELD_CT = 4000;
    const SPRITES = ["👾", "🛸", "🧠", "🦾", "🛰️", "🧬", "🤖"];

    const DIFFICULTY_CONFIGS = {
        "1": {
            key: "1",
            maxEnemies: 5,
            spawnBase: 2200,
            spawnFloor: 950,
            spawnDecay: 8,
            speedStart: 0.62,
            speedAccelEveryMs: 3600,
            speedAccelStep: 0.06,
            speedMax: 3.1,
            hazardChance: 0.22
        },
        "2": {
            key: "2",
            maxEnemies: 6,
            spawnBase: 1900,
            spawnFloor: 820,
            spawnDecay: 10,
            speedStart: 0.72,
            speedAccelEveryMs: 3200,
            speedAccelStep: 0.07,
            speedMax: 4.0,
            hazardChance: 0.34
        },
        "3": {
            key: "3",
            maxEnemies: 8,
            spawnBase: 1700,
            spawnFloor: 700,
            spawnDecay: 12,
            speedStart: 0.8,
            speedAccelEveryMs: 3000,
            speedAccelStep: 0.08,
            speedMax: 5.0,
            hazardChance: 0.45
        }
    };

    // ===== Soft error logger =====
    const errbox = document.getElementById('errlog');
    const logErr = (msg) => { try { errbox.style.display = 'block'; errbox.textContent = String(msg); } catch (_) { } };
    window.addEventListener('error', e => logErr(e.message || e.error));

    // JP words（表示：漢字/カタカナ、入力：柔軟ローマ字）
    const JP_WORDS = [
        { jpDisp: "猫", kana: "ねこ" },
        { jpDisp: "犬", kana: "いぬ" },
        { jpDisp: "光", kana: "ひかり" },
        { jpDisp: "山", kana: "やま" },
        { jpDisp: "川", kana: "かわ" },
        { jpDisp: "空", kana: "そら" },
        { jpDisp: "風", kana: "かぜ" },
        { jpDisp: "星", kana: "ほし" },
        { jpDisp: "月", kana: "つき" },
        { jpDisp: "太陽", kana: "たいよう" },
        { jpDisp: "魔法", kana: "まほう" },
        { jpDisp: "伝説", kana: "でんせつ" },
        { jpDisp: "宝", kana: "たから" },
        { jpDisp: "雷", kana: "かみなり" },
        { jpDisp: "竜", kana: "りゅう" },
        { jpDisp: "桜", kana: "さくら" },
        { jpDisp: "サーバー", kana: "サーバー", opts: { choon: "dash-only" } },
        { jpDisp: "クラス", kana: "クラス" },
        { jpDisp: "バッファ", kana: "バッファ" },
        { jpDisp: "ソケット", kana: "ソケット" }
    ];

    // EN（かんたん英単語）
    const EN_WORDS = [
        "cat", "dog", "sun", "star", "moon", "sky", "sea", "tree", "bird", "fish",
        "red", "blue", "green", "yellow", "black", "white",
        "book", "pen", "car", "bus", "train", "ship", "plane",
        "home", "room", "door", "bed", "food", "cake", "milk", "rice",
        "run", "walk", "jump", "play", "read", "write", "sing", "dance",
        "happy", "sad", "big", "small", "hot", "cold", "fast", "slow",
        "light", "dark", "fire", "rain", "snow", "wind"
    ];

    // ===== Natural mixing（より自然に：最大1種類だけ追加） =====
    const DIGITS = ["2", "3", "4", "8", "16", "32", "64", "128", "256"];
    const SUF_WORDS = ["core", "util", "tmp", "dev", "alpha", "beta", "old", "test", "async", "fast"];
    const JOINS = ["_", "-"];
    function chooseSuffix(useDigits, useSymbols) {
        if (!useDigits && !useSymbols) return "";
        const r = Math.random();
        if (useSymbols && r < 0.06) {
            const punct = Math.random() < 0.7 ? "!" : "?";
            return punct;
        } else if (useSymbols && r < 0.11) {
            const join = JOINS[(Math.random() * JOINS.length) | 0];
            const w = SUF_WORDS[(Math.random() * SUF_WORDS.length) | 0];
            let s = join + w;
            if (useDigits && Math.random() < 0.45) { s += (Math.random() < 0.6 ? "" : "") + DIGITS[(Math.random() * 4) | 0]; }
            return s;
        } else if (useDigits && r < 0.16) {
            const n = DIGITS[(Math.random() * DIGITS.length) | 0];
            return (Math.random() < 0.6 ? "_v" : "v") + n;
        } else if (useDigits && r < 0.20) {
            return DIGITS[(Math.random() * DIGITS.length) | 0];
        }
        return "";
    }

    // ===== Kana -> Romaji options (flexible) =====
    const VOWELS = new Set(["a", "i", "u", "e", "o"]);
    const hiraFromKata = s => s.replace(/[ァ-ヶ]/g, ch => String.fromCharCode(ch.charCodeAt(0) - 0x60));

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
        "わ": ["wa"], "ゐ": ["wi"], "ゑ": ["we"], "を": ["wo", "o"],
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
        "りゃ": ["rya"], "りゅ": ["ryu"], "りょ": ["ryo"],
        "ふぁ": ["fa"], "ふぃ": ["fi"], "ふぇ": ["fe"], "ふぉ": ["fo"], "ふゅ": ["fyu"],
        "しぇ": ["she", "sye"], "じぇ": ["je", "zye", "jye"], "ちぇ": ["che", "tye", "cye"],
        "てぃ": ["ti"], "でぃ": ["di"],
        "つぁ": ["tsa"], "つぃ": ["tsi"], "つぇ": ["tse"], "つぉ": ["tso"],
        "うぃ": ["wi"], "うぇ": ["we"], "うぉ": ["wo"],
        "くぁ": ["kwa", "qwa"], "くぃ": ["kwi", "qwi"], "くぇ": ["kwe", "qwe"], "くぉ": ["kwo", "qwo"],
        "ぐぁ": ["gwa"], "ぐぃ": ["gwi"], "ぐぇ": ["gwe"], "ぐぉ": ["gwo"],
        "ゔぁ": ["va"], "ゔぃ": ["vi"], "ゔぇ": ["ve"], "ゔぉ": ["vo"], "ゔゅ": ["vyu"]
    };

    const SMALL = new Set(["ゃ", "ゅ", "ょ", "ぁ", "ぃ", "ぅ", "ぇ", "ぉ"]);
    const SOKUON = "っ";
    const CHOON = "ー";

    function tokenizeKana(hira) {
        const t = [];
        for (let i = 0; i < hira.length; i++) {
            const c = hira[i], n = hira[i + 1];
            if (c === SOKUON || c === CHOON) { t.push(c); continue; }
            if (n && SMALL.has(n) && YOON[c + n]) { t.push(c + n); i++; continue; }
            t.push(c);
        }
        return t;
    }
    const lastVowelOf = s => { for (let i = s.length - 1; i >= 0; i--) if (VOWELS.has(s[i].toLowerCase())) return s[i].toLowerCase(); return ""; };

    function romajiOptionsFromTokens(tokens, opt = { choon: "both" }) {
        const memo = new Map();
        function key(i, b, lv, gem) { return i + "|" + b.length + "|" + lv + "|" + (gem ? 1 : 0) + "|" + opt.choon; }
        function rec(idx, built, lastV, gem) {
            if (idx >= tokens.length) return [built];
            const mk = key(idx, built, lastV, gem);
            if (memo.has(mk)) return memo.get(mk);
            const t = tokens[idx];
            let out = [];
            if (t === CHOON) {
                if (opt.choon === "dash-only") out = rec(idx + 1, built + "-", lastV, false);
                else {
                    const a = [];
                    if (lastV) a.push(rec(idx + 1, built + lastV, lastV, false));
                    a.push(rec(idx + 1, built + "-", lastV, false));
                    out = a.flat();
                }
                memo.set(mk, out); return out;
            }
            if (t === SOKUON) {
                let a = []; a = a.concat(rec(idx + 1, built, lastV, true)); a = a.concat(rec(idx + 1, built + "xtu", "u", false)); a = a.concat(rec(idx + 1, built + "ltsu", "u", false)); memo.set(mk, a); return a;
            }
            if (t === "ん") {
                const next = tokens[idx + 1];
                const nextHeads = (() => {
                    if (!next || next === CHOON || next === SOKUON) return [];
                    const cand = YOON[next] || BASE[next] || [];
                    return cand.map(s => s[0].toLowerCase());
                })();
                const headsYOrVowel = nextHeads.some(h => VOWELS.has(h) || h === "y");
                const forms = headsYOrVowel ? ["n'", "nn"] : ["n", "nn"];
                let a = []; for (const f of forms) a = a.concat(rec(idx + 1, built + f, lastV, false)); memo.set(mk, a); return a;
            }
            const baseList = YOON[t] || BASE[t] || [];
            let a = [];
            for (const b of baseList) {
                const withGem = gem ? (b[0] + b) : b;
                const newLast = lastVowelOf(withGem) || lastV;
                a = a.concat(rec(idx + 1, built + withGem, newLast, false));
            }
            memo.set(mk, a); return a;
        }
        return Array.from(new Set(rec(0, "", "", false)));
    }

    function buildRomajiOptions(kana, opt) {
        const hira = hiraFromKata(kana);
        const tokens = tokenizeKana(hira);
        return romajiOptionsFromTokens(tokens, opt || { choon: "both" });
    }

    function chooseCanon(opts) {
        return (opts.slice().sort((a, b) => {
            const ap = (a.match(/[^a-z]/gi) || []).length, bp = (b.match(/[^a-z]/gi) || []).length;
            if (ap !== bp) return ap - bp;
            if (a.length !== b.length) return a.length - b.length;
            return a.localeCompare(b);
        })[0]) || "";
    }

    function attachSuffixToAll(opts, suffix) {
        if (!suffix) return { opts, canon: chooseCanon(opts) };
        const out = opts.map(o => o + suffix);
        return { opts: out, canon: chooseCanon(out) };
    }

    // DOM refs
    const game = document.getElementById('game'), lanesEl = document.getElementById('lanes');
    const scoreEl = document.getElementById('score'), comboEl = document.getElementById('combo'), lockWordEl = document.getElementById('lockWord');
    const rtEl = document.getElementById('rt');
    const hpfill = document.getElementById('hpfill'), input = document.getElementById('type');
    const startOverlay = document.getElementById('start'), gameoverOverlay = document.getElementById('gameover');
    const startBtn = document.getElementById('startBtn'), retryBtn = document.getElementById('retryBtn');
    const homeBtn = document.getElementById('homeBtn');
    const topBtn = document.getElementById('topBtn');
    const finalScore = document.getElementById('finalScore'), finalCombo = document.getElementById('finalCombo');
    const finalTime = document.getElementById('finalTime'), finalRank = document.getElementById('finalRank');
    const muteBtn = document.getElementById('muteBtn'), volSlider = document.getElementById('vol');
    const player = document.getElementById('player');
    const gbar = document.getElementById('gbar'), gbtn = document.getElementById('gbtn');
    const optDigits = document.getElementById('optDigits'), optSymbols = document.getElementById('optSymbols');

    // State
    let running = false, health = 100, score = 0, combo = 0, bestCombo = 0;
    let spawnTimer = 0, enemies = [], hazards = [], locked = null, spawnInterval = 1700, speedScale = 0.8;
    let width = game.clientWidth, height = game.clientHeight, timeScale = 1.0;
    let cursorX = window.innerWidth / 2, cursorY = window.innerHeight / 2;
    let shieldCT = 0, shieldOn = false;
    let langMode = "jp";
    let elapsedRealMs = 0;
    let currentDifficulty = DIFFICULTY_CONFIGS["3"];
    let maxEnemies = currentDifficulty.maxEnemies;
    let hazardChance = currentDifficulty.hazardChance;
    let spawnFloor = currentDifficulty.spawnFloor;
    let spawnDecay = currentDifficulty.spawnDecay;
    let accelEveryMs = currentDifficulty.speedAccelEveryMs;
    let accelStep = currentDifficulty.speedAccelStep;
    let speedMax = currentDifficulty.speedMax;

    // Gauge (5 segments)
    const segFills = [0, 0, 0, 0, 0];
    function addGaugeSegment(delta) { let remain = delta; for (let i = 0; i < 5 && remain > 0; i++) { const free = 1 - segFills[i]; const add = Math.min(free, remain); segFills[i] += add; remain -= add; } drawGauge(); }
    function consumeGaugeSegment() { const idx = segFills.findIndex(v => v >= 1 - 1e-6); if (idx === -1) return false; for (let i = 0; i < 4; i++) segFills[i] = segFills[i + 1]; segFills[4] = 0; drawGauge(); return true; }
    function hasFullSegment() { return segFills.some(v => v >= 1 - 1e-6); }
    function drawGauge() { for (let i = 0; i < 5; i++) { const el = document.getElementById('sg' + i); el.style.width = Math.round(segFills[i] * 100) + '%'; } gbar.classList.toggle('ready', hasFullSegment()); }

    // ===== Audio（ノイズ合成） =====
    let actx = null, master = null, muted = false;
    function ensureAudio() { if (actx) return; actx = new (window.AudioContext || window.webkitAudioContext)(); master = actx.createGain(); master.gain.value = muted ? 0 : parseFloat(volSlider.value || "0.7"); master.connect(actx.destination); }
    function setMuted(m) { muted = m; if (master) master.gain.value = muted ? 0 : parseFloat(volSlider.value || "0.7"); muteBtn.textContent = muted ? "🔇 OFF" : "🔈 ON"; }
    muteBtn.addEventListener('click', () => setMuted(!muted));
    volSlider.addEventListener('input', () => { if (master) master.gain.value = muted ? 0 : parseFloat(volSlider.value); });

    function noiseBurst({ t = 0.2, type = "lowpass", freq = 400, q = 0.7, gain = 0.7, startGain = 1.0, endGain = 0.001 } = {}) { try { if (!actx) return; const buf = actx.createBuffer(1, Math.max(1, Math.floor(actx.sampleRate * t)), actx.sampleRate); const data = buf.getChannelData(0); for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1; const src = actx.createBufferSource(); src.buffer = buf; const f = actx.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q; const g = actx.createGain(); const now = actx.currentTime; g.gain.setValueAtTime(Math.min(1, gain * startGain), now); g.gain.exponentialRampToValueAtTime(Math.max(0.0001, gain * endGain), now + t); src.connect(f).connect(g).connect(master); src.start(); } catch (e) { logErr(e.message); } }
    function clickShot({ freq = 2400, t = 0.02, gain = 0.2 } = {}) { try { if (!actx) return; const o = actx.createOscillator(); o.type = "square"; const g = actx.createGain(); const now = actx.currentTime; o.frequency.value = freq; g.gain.value = gain; g.gain.exponentialRampToValueAtTime(0.001, now + t); o.connect(g).connect(master); o.start(); o.stop(now + t); } catch (e) { logErr(e.message); } }
    function thump({ freq = 80, t = 0.25, gain = 0.6, slide = -40 } = {}) { try { if (!actx) return; const o = actx.createOscillator(); o.type = "sine"; const g = actx.createGain(); const now = actx.currentTime; o.frequency.setValueAtTime(freq, now); if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(20, freq + slide), now + t); g.gain.value = gain; g.gain.exponentialRampToValueAtTime(0.001, now + t); o.connect(g).connect(master); o.start(); o.stop(now + t); } catch (e) { logErr(e.message); } }
    const SFX = { shot() { noiseBurst({ t: 0.06, type: "highpass", freq: 1800, q: 0.6, gain: 0.35, startGain: 1.0, endGain: 0.01 }); clickShot({}); }, explosion() { noiseBurst({ t: 0.6, type: "lowpass", freq: 280, q: 0.9, gain: 0.8, startGain: 1.0, endGain: 0.001 }); noiseBurst({ t: 0.35, type: "bandpass", freq: 220, q: 8, gain: 0.35, startGain: 1.0, endGain: 0.1 }); thump({ freq: 90, t: 0.32, gain: 0.7, slide: -55 }); }, damage() { noiseBurst({ t: 0.18, type: "bandpass", freq: 260, q: 6, gain: 0.6, startGain: 1.0, endGain: 0.02 }); thump({ freq: 80, t: 0.18, gain: 0.5, slide: -20 }); }, special() { noiseBurst({ t: 0.5, type: "bandpass", freq: 900, q: 1.2, gain: 0.8, startGain: 1.0, endGain: 0.02 }); noiseBurst({ t: 0.7, type: "lowpass", freq: 260, q: 0.8, gain: 0.9, startGain: 1.0, endGain: 0.001 }); thump({ freq: 120, t: 0.22, gain: 0.7, slide: -70 }); setTimeout(() => thump({ freq: 70, t: 0.35, gain: 0.8, slide: -30 }), 80); }, shield() { noiseBurst({ t: 0.2, type: "highpass", freq: 2000, q: 0.7, gain: 0.4, startGain: 0.8, endGain: 0.02 }); } };

    const laneX = lane => ((lane + 0.5) / LANES) * width;
    const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
    const setHP = v => { hpfill.style.width = clamp(v, 0, 100) + "%"; };
    const randEl = arr => arr[(Math.random() * arr.length) | 0];

    function applyDifficultyFromUI() {
        let selected = "3";
        document.querySelectorAll('input[name="difficulty"]').forEach(i => { if (i.checked) selected = i.value; });
        currentDifficulty = DIFFICULTY_CONFIGS[selected] || DIFFICULTY_CONFIGS["3"];
        maxEnemies = currentDifficulty.maxEnemies;
        hazardChance = currentDifficulty.hazardChance;
        spawnFloor = currentDifficulty.spawnFloor;
        spawnDecay = currentDifficulty.spawnDecay;
        accelEveryMs = currentDifficulty.speedAccelEveryMs;
        accelStep = currentDifficulty.speedAccelStep;
        speedMax = currentDifficulty.speedMax;
    }

    // Build lanes
    lanesEl.innerHTML = ""; for (let i = 0; i < LANES; i++) { const d = document.createElement('div'); d.className = "lane"; lanesEl.appendChild(d); }

    // 単語生成（表示側にも suffix を反映）
    function makeWord() {
        const useDigits = optDigits.checked;
        const useSymbols = optSymbols.checked;
        const suffix = chooseSuffix(useDigits, useSymbols);
        if (langMode === "jp") {
            const base = JP_WORDS[(Math.random() * JP_WORDS.length) | 0];
            const opts0 = buildRomajiOptions(base.kana, base.opts);
            const withSuf = attachSuffixToAll(opts0, suffix);
            const displayMain = base.jpDisp + suffix;
            return { displayMain, romajiOpts: withSuf.opts, canon: withSuf.canon };
        } else {
            const core = randEl(EN_WORDS);
            const typeStr = core + suffix;
            return { displayMain: typeStr, typeStr };
        }
    }

    function makeEnemy() {
        const lane = (Math.random() * LANES) | 0;
        const n = document.createElement('div'); n.className = "enemy";
        n.style.width = SIZE + "px"; n.style.height = SIZE + "px";
        n.style.left = laneX(lane) + "px";
        n._lane = lane; n._x = laneX(lane); n._y = -120; n.style.top = n._y + "px";

        const sprite = document.createElement('div'); sprite.className = "sprite"; sprite.textContent = randEl(SPRITES); n.appendChild(sprite);
        const hp = document.createElement('div'); hp.className = "hp"; hp.innerHTML = '<span style="width:100%"></span>'; n.appendChild(hp);

        const word = makeWord();
        const name = document.createElement('div'); name.className = "name"; name.textContent = word.displayMain; n.appendChild(name);

        const hint = document.createElement('div'); hint.className = "typehint hidden"; hint.textContent = "type:"; n.appendChild(hint); n._hint = hint;

        if (langMode === "jp") { n._romOpts = word.romajiOpts; n._typed = ""; n._current = word.canon; n.dataset.word = word.canon; }
        else { n.dataset.word = word.typeStr; n.dataset.progress = "0"; }

        n.addEventListener('pointerdown', (e) => { e.stopPropagation(); lockEnemy(n); });

        game.appendChild(n); enemies.push(n);
    }

    function makeHazard() {
        const lane = (Math.random() * LANES) | 0;
        const z = document.createElement('div'); z.className = "sweep";
        z.style.left = (lane * (width / LANES)) + "px"; z.style.width = (width / LANES) + "px";
        z._lane = lane; z._y = -20; z.style.top = z._y + "px";
        game.appendChild(z); hazards.push(z);
    }

    function lockEnemy(n) {
        if (locked) { locked.classList.remove('locked'); if (langMode === "jp" && locked._hint) locked._hint.classList.add('hidden'); }
        locked = n; n.classList.add('locked');
        lockWordEl.textContent = n.dataset.word || "---";
        if (langMode === "jp" && n._hint) { n._hint.classList.remove('hidden'); updateTypeHint(n); }
        input.focus(); setTimeout(() => input.focus(), 0);
    }
    function unlockEnemy() { if (locked) { if (langMode === "jp" && locked._hint) { locked._hint.classList.add('hidden'); } locked.classList.remove('locked'); locked = null; } lockWordEl.textContent = "---"; }

    function updateTypeHint(n) { if (langMode !== "jp" || !n || !n._hint) return; const full = n._current || ""; const typed = n._typed || ""; const safe = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;"); const before = `<span style="color:#ffd43b">${safe(typed)}</span>`; const after = safe(full.slice(typed.length)); n._hint.innerHTML = `type: <code>${before}${after}</code>`; }

    function damage(amount) { if (shieldOn) return; health = Math.max(0, health - amount); setHP(health); game.classList.add('shake'); setTimeout(() => game.classList.remove('shake'), 140); SFX.damage(); if (health <= 0) gameOver(); }
    function addScore(base) { const gain = Math.round(base * (1 + combo * 0.12)); score += gain; scoreEl.textContent = score; }
    function popText(x, y, text, color = "#fff") { const p = document.createElement('div'); p.className = "pop"; p.textContent = text; p.style.left = x + "px"; p.style.top = y + "px"; p.style.color = color; game.appendChild(p); setTimeout(() => p.remove(), 650); }
    function muzzlePos() { return { x: cursorX, y: cursorY - 22 }; }
    function beamFromMuzzle(x2, y2) { const m = muzzlePos(); const b = document.createElement('div'); b.className = "beam"; const dx = x2 - m.x, dy = y2 - m.y, dist = Math.hypot(dx, dy), ang = Math.atan2(dy, dx) * 180 / Math.PI; b.style.width = dist + "px"; b.style.left = m.x + "px"; b.style.top = m.y + "px"; b.style.transform = `rotate(${ang}deg)`; game.appendChild(b); setTimeout(() => b.remove(), 150); }
    function boom(x, y) { const e = document.createElement('div'); e.className = "boom"; e.style.left = x + "px"; e.style.top = y + "px"; game.appendChild(e); setTimeout(() => e.remove(), 520); }
    function hitStop(ms = HITSTOP) { timeScale = 0.0001; setTimeout(() => { timeScale = 1.0; }, ms); }

    function activateSpecial() { if (!consumeGaugeSegment()) return; SFX.special(); const origins = [-70, 0, 70].map(dx => ({ x: cursorX + dx, y: cursorY - 20 })); for (const o of origins) { const b = document.createElement('div'); b.className = "beam"; b.style.height = "8px"; b.style.left = o.x + "px"; b.style.top = o.y + "px"; b.style.width = height + "px"; b.style.transform = `rotate(${-90}deg)`; b.style.boxShadow = "0 0 26px #7fffd4aa"; game.appendChild(b); setTimeout(() => b.remove(), 260); } for (const e of [...enemies]) { const tx = e._x, ty = e._y + e.offsetHeight / 2; boom(tx, ty); popText(tx, ty - 16, "OVERDRIVE!", "#7fffd4"); addScore(160); if (locked === e) unlockEnemy(); e.remove(); enemies.splice(enemies.indexOf(e), 1); } combo += 3; bestCombo = Math.max(bestCombo, combo); comboEl.textContent = combo; hitStop(120); }

    game.addEventListener('mousemove', (e) => { cursorX = e.clientX; cursorY = e.clientY; player.style.left = cursorX + "px"; player.style.top = cursorY + "px"; });
    game.addEventListener('wheel', (e) => { if (!running) return; if (e.deltaY < 0 && shieldCT <= 0) { shieldCT = SHIELD_CT; shieldOn = true; player.classList.add('shield'); SFX.shield(); setTimeout(() => { shieldOn = false; player.classList.remove('shield'); }, SHIELD_TIME); } e.preventDefault(); }, { passive: false });
    gbtn.addEventListener('click', activateSpecial);

    function handleChar(ch) {
        if (!locked) return;
        if (langMode === "jp") {
            const t = (locked._typed || "") + ch;
            const matches = (locked._romOpts || []).filter(o => o.toLowerCase().startsWith(t.toLowerCase()));
            if (matches.length) {
                locked._typed = t; matches.sort((a, b) => { if (a.length !== b.length) return a.length - b.length; const ap = (a.match(/[^a-z]/gi) || []).length, bp = (b.match(/[^a-z]/gi) || []).length; if (ap !== bp) return ap - bp; return a.localeCompare(b); }); locked._current = matches[0]; updateTypeHint(locked);
                const hpSpan = locked.querySelector('.hp > span'); const ratio = Math.min(1, (locked._typed.length) / (locked._current.length || 1)); hpSpan.style.width = Math.max(0, 100 - Math.round(100 * ratio)) + "%";
                const tx = locked._x, ty = locked._y + locked.offsetHeight / 2; beamFromMuzzle(tx, ty); popText(tx, ty - 10, "HIT", "#7fffd4"); SFX.shot(); hitStop(50);
                combo++; bestCombo = Math.max(bestCombo, combo); comboEl.textContent = combo; addScore(34); addGaugeSegment(0.015);
                const exact = matches.some(o => o.length === t.length && o.toLowerCase() === t.toLowerCase()); if (exact) { killLocked(tx, ty); }
            } else { combo = 0; comboEl.textContent = combo; game.animate([{ filter: "brightness(1.2)" }, { filter: "brightness(1)" }], { duration: 120 }); }
            return;
        }
        const word = locked.dataset.word; let p = +locked.dataset.progress; const need = word[p] || ""; const equal = (c1, c2) => (/[a-z]/i.test(c1) && /[a-z]/i.test(c2)) ? c1.toLowerCase() === c2.toLowerCase() : (c1 === c2);
        if (need && equal(ch, need)) {
            p++; locked.dataset.progress = String(p); const hp = locked.querySelector('.hp > span'); hp.style.width = Math.max(0, 100 - Math.round(100 * p / word.length)) + "%"; const tx = locked._x, ty = locked._y + locked.offsetHeight / 2; beamFromMuzzle(tx, ty); popText(tx, ty - 10, "HIT", "#7fffd4"); SFX.shot(); hitStop(50);
            combo++; bestCombo = Math.max(bestCombo, combo); comboEl.textContent = combo; addScore(34); addGaugeSegment(0.015); if (p >= word.length) { killLocked(tx, ty); }
        } else { combo = 0; comboEl.textContent = combo; game.animate([{ filter: "brightness(1.2)" }, { filter: "brightness(1)" }], { duration: 120 }); }
    }

    document.getElementById('type').addEventListener('input', function () { const v = this.value; if (!v) return; const ch = v.slice(-1); if (ch >= "!" && ch <= "~") { handleChar(ch); } this.value = ""; });
    window.addEventListener('keydown', (e) => { if (!running) return; if (e.key.length === 1) { const ch = e.key; if (ch >= "!" && ch <= "~") { handleChar(ch); e.preventDefault(); } } });
    document.getElementById('focusBtn')?.addEventListener('click', () => { document.getElementById('type').focus(); setTimeout(() => document.getElementById('type').focus(), 0); });

    function killLocked(tx, ty) { popText(tx, ty - 14, "BREAK!", "#2dd4ff"); boom(tx, ty); addScore(150); SFX.explosion(); hitStop(90); enemies.splice(enemies.indexOf(locked), 1); locked.remove(); unlockEnemy(); addGaugeSegment(0.12); }

    // ===== ランク（スコア基準） =====
    function calcRank(scoreValue) {
        const grades = ["D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S-", "S", "S+", "SS-", "SS", "SS+"];
        const thresholds = [
            0, 7500, 12000, 18000, 25500, 33000, 42000, 52500, 63000, 75000,
            90000, 120000, 150000, 175000, 205000, 240000, 300000, 500000
        ];
        let idx = 0; for (let i = 0; i < thresholds.length; i++) { if (scoreValue >= thresholds[i]) idx = i; }
        return { grade: grades[idx] };
    }

    // ===== 進行 =====
    let lastTs = performance.now();
    let gameTimeMs = 0, nextAccelMs = 3000;
    function formatTime(ms) { const t = Math.max(0, Math.floor(ms / 1000)); const m = Math.floor(t / 60); const s = t % 60; return `${m}:${String(s).padStart(2, '0')}`; }
    function update(ts) {
        try {
            const dtReal = Math.min(0.05, (ts - lastTs) / 1000); lastTs = ts; const dt = dtReal * timeScale; if (!running) { requestAnimationFrame(update); return; }
            elapsedRealMs += dtReal * 1000; rtEl.textContent = formatTime(elapsedRealMs);
            if (shieldCT > 0) { shieldCT -= dt * 1000; if (shieldCT < 0) shieldCT = 0; }
            gameTimeMs += dt * 1000;
            if (gameTimeMs >= nextAccelMs) { speedScale = Math.min(speedMax, speedScale + accelStep); nextAccelMs += accelEveryMs; }
            spawnTimer += dt * 1000;
            if (enemies.length < maxEnemies && spawnTimer >= spawnInterval) { spawnTimer = 0; makeEnemy(); if (Math.random() < hazardChance) makeHazard(); spawnInterval = Math.max(spawnFloor, spawnInterval - spawnDecay); }
            for (const e of [...enemies]) { e._y += DESCENT * speedScale * dt; e.style.top = e._y + "px"; if (e._y + e.offsetHeight >= height - BOTTOM_MARGIN) { if (locked === e) unlockEnemy(); e.remove(); enemies.splice(enemies.indexOf(e), 1); combo = 0; comboEl.textContent = combo; if (!shieldOn) damage(DAMAGE_ON_HIT); } }
            for (const h of [...hazards]) { h._y += (DESCENT * 1.15) * speedScale * dt; h.style.top = h._y + "px"; const laneLeft = h._lane * (width / LANES), laneRight = (h._lane + 1) * (width / LANES); if (cursorX >= laneLeft && cursorX <= laneRight && Math.abs((h._y + 4) - cursorY) <= 8) { if (!shieldOn) damage(12.5); h.remove(); hazards.splice(hazards.indexOf(h), 1); } else if (h._y > height + 20) { h.remove(); hazards.splice(hazards.indexOf(h), 1); } }
            requestAnimationFrame(update);
        } catch (e) { logErr(e.message); requestAnimationFrame(update); }
    }

    function resetFieldState() {
        enemies.forEach(e => e.remove());
        enemies = [];
        hazards.forEach(h => h.remove());
        hazards = [];
        unlockEnemy();
    }

    // ===== Game control =====
    function startGame() {
        try {
            document.querySelectorAll('input[name="lang"]').forEach(i => { if (i.checked) langMode = i.value; });
            applyDifficultyFromUI();

            ensureAudio(); if (actx.resume) { try { actx.resume(); } catch (_) { } }
            running = true; health = 100; setHP(health); score = 0; scoreEl.textContent = score; combo = 0; bestCombo = 0; elapsedRealMs = 0; rtEl.textContent = '0:00';
            segFills.fill(0); drawGauge(); shieldCT = 0; shieldOn = false;
            spawnInterval = currentDifficulty.spawnBase;
            speedScale = currentDifficulty.speedStart;
            resetFieldState();

            startOverlay.style.display = "none";
            gameoverOverlay.style.display = "none";
            document.body.classList.remove('hasOverlay');

            width = game.clientWidth; height = game.clientHeight; document.getElementById('type').focus();
            gameTimeMs = 0; nextAccelMs = accelEveryMs; lastTs = performance.now();
            requestAnimationFrame(update);
        } catch (e) { logErr(e.message); }
    }

    function showTopOverlay() {
        running = false;
        resetFieldState();
        startOverlay.style.display = "flex";
        gameoverOverlay.style.display = "none";
        document.body.classList.add('hasOverlay');
    }

    function gameOver() {
        running = false;
        finalScore.textContent = score;
        finalCombo.textContent = bestCombo;
        finalTime.textContent = formatTime(elapsedRealMs);
        const r = calcRank(score);
        finalRank.textContent = r.grade;
        gameoverOverlay.style.display = "flex";
        document.body.classList.add('hasOverlay');
    }

    startBtn.addEventListener('click', () => startGame());
    retryBtn.addEventListener('click', () => startGame());
    topBtn?.addEventListener('click', () => showTopOverlay());
    homeBtn?.addEventListener('click', () => { window.location.href = '../index.html'; });

    new ResizeObserver(() => { width = game.clientWidth; height = game.clientHeight; }).observe(game);

    const startX = window.innerWidth / 2, startY = window.innerHeight / 2;
    player.style.left = startX + "px"; player.style.top = startY + "px"; cursorX = startX; cursorY = startY;
})();

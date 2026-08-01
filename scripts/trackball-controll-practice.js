const TOTAL_TARGETS = 10;
const SCORE_BASE = 10000;
const MISS_PENALTY_SECONDS = 2;
const SCORE_FORMATTER = new Intl.NumberFormat("ja-JP");

const playfield = document.getElementById("playfield");
const arena = document.getElementById("arena");
const target = document.getElementById("target");
const progress = document.getElementById("progress");
const timer = document.getElementById("timer");
const misses = document.getElementById("misses");
const remaining = document.getElementById("remaining");
const progressBar = document.getElementById("progressBar");
const countdownDisplay = document.getElementById("countdownDisplay");
const countdownAnnouncement = document.getElementById("countdownAnnouncement");
const finishBackdrop = document.getElementById("finishBackdrop");
const finishResult = document.getElementById("finishResult");
const finishScore = document.getElementById("finishScore");
const finishBreakdown = document.getElementById("finishBreakdown");
const finishAnnouncement = document.getElementById("finishAnnouncement");
const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const quitBtn = document.getElementById("quitBtn");
const difficultyEasy = document.getElementById("difficultyEasy");
const difficultyHard = document.getElementById("difficultyHard");

let hitCount = 0;
let missCount = 0;
let startedAt = 0;
let running = false;
let animationFrameId = null;
let currentDifficulty = "easy";
let paused = false;
let elapsedBeforePause = 0;
let finishAnnouncementFrameId = null;
let countdownTimeoutId = null;
let countingDown = false;

function formatSeconds(seconds) {
    return `${seconds.toFixed(2)}s`;
}

function formatJapaneseSeconds(seconds) {
    return `${seconds.toFixed(2)}秒`;
}

function calculateScore(clearTimeSeconds, scoreMissCount) {
    const adjustedTime = Math.max(clearTimeSeconds + scoreMissCount * MISS_PENALTY_SECONDS, 0.01);
    return Math.round(SCORE_BASE / adjustedTime);
}

function formatScore(points) {
    return `${SCORE_FORMATTER.format(points)} pt`;
}

function formatScoreForAnnouncement(points) {
    return `${SCORE_FORMATTER.format(points)}ポイント`;
}

function setDifficultyDisabled(disabled) {
    difficultyEasy.disabled = disabled;
    difficultyHard.disabled = disabled;
}

function hideFinishResult() {
    cancelAnimationFrame(finishAnnouncementFrameId);
    finishAnnouncementFrameId = null;
    finishBackdrop.classList.remove("is-visible");
    finishResult.classList.remove("is-visible");
    finishAnnouncement.textContent = "";
}

function clearCountdown() {
    if (countdownTimeoutId !== null) {
        clearTimeout(countdownTimeoutId);
        countdownTimeoutId = null;
    }

    countingDown = false;
    countdownDisplay.classList.remove("is-visible");
    countdownDisplay.textContent = "";
    countdownAnnouncement.textContent = "";
}

function startCountdown(onComplete) {
    clearCountdown();
    countingDown = true;
    startBtn.disabled = true;
    pauseBtn.disabled = true;
    setDifficultyDisabled(true);
    countdownDisplay.classList.add("is-visible");

    function showCount(value) {
        countdownDisplay.textContent = String(value);
        countdownAnnouncement.textContent = String(value);
        countdownTimeoutId = setTimeout(() => {
            if (value > 1) {
                showCount(value - 1);
                return;
            }

            countdownTimeoutId = null;
            countingDown = false;
            countdownDisplay.classList.remove("is-visible");
            countdownDisplay.textContent = "";
            countdownAnnouncement.textContent = "スタート";
            startBtn.disabled = false;
            pauseBtn.disabled = false;
            onComplete();
        }, 1000);
    }

    showCount(3);
}

function updateTimer() {
    if (!running || paused || countingDown) {
        return;
    }

    const elapsed = elapsedBeforePause + (performance.now() - startedAt) / 1000;
    timer.textContent = formatSeconds(elapsed);
    animationFrameId = requestAnimationFrame(updateTimer);
}

function moveTargetRandomly() {
    const maxX = Math.max(0, arena.clientWidth - target.offsetWidth);
    const topOffset = 52;
    const bottomOffset = 12;
    const minY = Math.min(topOffset, Math.max(0, arena.clientHeight - target.offsetHeight));
    const maxY = Math.max(minY, arena.clientHeight - target.offsetHeight - bottomOffset);

    const x = Math.random() * maxX;
    const y = minY + Math.random() * (maxY - minY);

    target.style.left = `${x}px`;
    target.style.top = `${y}px`;
}

function applyDifficulty() {
    playfield.classList.toggle("hard", currentDifficulty === "hard");

    const isEasy = currentDifficulty === "easy";
    difficultyEasy.classList.toggle("is-active", isEasy);
    difficultyEasy.setAttribute("aria-pressed", String(isEasy));
    difficultyHard.classList.toggle("is-active", !isEasy);
    difficultyHard.setAttribute("aria-pressed", String(!isEasy));

    if (!isEasy) {
        updateGridLines();
    }
}

function updateGridLines() {
    if (!playfield.classList.contains("hard")) {
        return;
    }

    // Grid lines background position を scroll に同期
    const gridX = -playfield.scrollLeft;
    const gridY = -playfield.scrollTop;
    playfield.style.setProperty("--grid-x", `${gridX}px`);
    playfield.style.setProperty("--grid-y", `${gridY}px`);
}

function renderProgress() {
    const percent = (hitCount / TOTAL_TARGETS) * 100;
    progress.textContent = `${hitCount} / ${TOTAL_TARGETS}`;
    const remainingCount = Math.max(0, TOTAL_TARGETS - hitCount);
    remaining.textContent = String(remainingCount);

    const meter = progressBar.parentElement;
    const isHorizontal = window.matchMedia("(max-width: 900px)").matches;
    meter.setAttribute("aria-orientation", isHorizontal ? "horizontal" : "vertical");
    if (isHorizontal) {
        progressBar.style.width = `${percent}%`;
        progressBar.style.height = "100%";
    } else {
        progressBar.style.height = `${percent}%`;
        progressBar.style.width = "100%";
    }

    meter.classList.remove("is-warning", "is-critical");
    if (remainingCount <= 1) {
        meter.classList.add("is-critical");
    } else if (remainingCount <= 3) {
        meter.classList.add("is-warning");
    }
    meter.setAttribute("aria-valuenow", String(hitCount));
    meter.setAttribute("aria-valuetext", `${hitCount} / ${TOTAL_TARGETS}`);
}

function finishGame() {
    clearCountdown();
    running = false;
    paused = false;
    cancelAnimationFrame(animationFrameId);

    const clearTime = elapsedBeforePause + (performance.now() - startedAt) / 1000;
    const missAdjustment = missCount * MISS_PENALTY_SECONDS;
    const finalScore = calculateScore(clearTime, missCount);
    const formattedClearTime = formatJapaneseSeconds(clearTime);
    const formattedMissAdjustment = formatJapaneseSeconds(missAdjustment);
    const formattedScore = formatScore(finalScore);
    const formattedAnnouncementScore = formatScoreForAnnouncement(finalScore);
    const breakdown = `タイム ${formattedClearTime} + ミス補正 ${formattedMissAdjustment}（${missCount}回）`;

    timer.textContent = formatSeconds(clearTime);
    startBtn.textContent = "もう一度";
    startBtn.disabled = false;
    pauseBtn.textContent = "一時停止";
    pauseBtn.disabled = true;
    quitBtn.disabled = true;
    target.classList.remove("is-paused");
    target.style.display = "none";
    startBtn.focus();
    if (window.matchMedia("(max-width: 640px)").matches) {
        startBtn.scrollIntoView({ block: "start", inline: "nearest" });
    }
    setDifficultyDisabled(false);
    finishScore.textContent = `スコア ${formattedScore}`;
    finishBreakdown.textContent = breakdown;
    finishBackdrop.classList.add("is-visible");
    finishResult.classList.add("is-visible");
    finishAnnouncement.textContent = "";
    finishAnnouncementFrameId = requestAnimationFrame(() => {
        finishAnnouncement.textContent = `Finish。スコア ${formattedAnnouncementScore}。タイム ${formattedClearTime}、ミス ${missCount}回、ミス補正 ${formattedMissAdjustment}。高いほど好成績です。`;
        finishAnnouncementFrameId = null;
    });
}

function startGame() {
    clearCountdown();
    hitCount = 0;
    missCount = 0;
    running = false;
    paused = false;
    elapsedBeforePause = 0;
    startedAt = 0;
    cancelAnimationFrame(animationFrameId);

    renderProgress();
    timer.textContent = "0.00s";
    misses.textContent = "0";
    startBtn.textContent = "リスタート";
    pauseBtn.textContent = "一時停止";
    quitBtn.disabled = false;
    hideFinishResult();

    applyDifficulty();
    playfield.scrollTop = 0;
    playfield.scrollLeft = 0;
    updateGridLines();

    target.style.display = "none";
    target.classList.remove("is-paused");
    startCountdown(() => {
        running = true;
        startedAt = performance.now();
        target.style.display = "block";
        moveTargetRandomly();
        animationFrameId = requestAnimationFrame(updateTimer);
    });
}

function togglePause() {
    if (!running) {
        return;
    }

    if (!paused) {
        paused = true;
        elapsedBeforePause += (performance.now() - startedAt) / 1000;
        timer.textContent = formatSeconds(elapsedBeforePause);
        pauseBtn.textContent = "再開";
        target.classList.add("is-paused");
        cancelAnimationFrame(animationFrameId);
        return;
    }

    pauseBtn.textContent = "一時停止";
    target.style.display = "none";
    startCountdown(() => {
        paused = false;
        startedAt = performance.now();
        target.style.display = "block";
        target.classList.remove("is-paused");
        animationFrameId = requestAnimationFrame(updateTimer);
    });
}

function quitGame() {
    clearCountdown();
    running = false;
    paused = false;
    elapsedBeforePause = 0;
    cancelAnimationFrame(animationFrameId);

    hitCount = 0;
    missCount = 0;
    renderProgress();
    timer.textContent = "0.00s";
    misses.textContent = "0";
    target.classList.remove("is-paused");
    target.style.display = "none";
    hideFinishResult();

    playfield.scrollTop = 0;
    playfield.scrollLeft = 0;
    updateGridLines();

    startBtn.textContent = "スタート";
    startBtn.disabled = false;
    pauseBtn.textContent = "一時停止";
    pauseBtn.disabled = true;
    quitBtn.disabled = true;
    setDifficultyDisabled(false);
}

difficultyEasy.addEventListener("click", () => {
    currentDifficulty = "easy";
    applyDifficulty();
});

difficultyHard.addEventListener("click", () => {
    currentDifficulty = "hard";
    applyDifficulty();
    updateGridLines();
});

startBtn.addEventListener("click", startGame);
pauseBtn.addEventListener("click", togglePause);
quitBtn.addEventListener("click", quitGame);

target.addEventListener("click", (event) => {
    event.stopPropagation();

    if (!running || paused || countingDown) {
        return;
    }

    hitCount += 1;
    renderProgress();

    if (hitCount >= TOTAL_TARGETS) {
        finishGame();
        return;
    }

    moveTargetRandomly();
});

playfield.addEventListener("scroll", () => {
    updateGridLines();
});

arena.addEventListener("click", (event) => {
    if (!running || paused || countingDown || event.target === target) {
        return;
    }

    missCount += 1;
    misses.textContent = String(missCount);
});

renderProgress();
applyDifficulty();
window.addEventListener("resize", renderProgress);

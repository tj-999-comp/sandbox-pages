const TOTAL_TARGETS = 10;

const playfield = document.getElementById("playfield");
const arena = document.getElementById("arena");
const target = document.getElementById("target");
const progress = document.getElementById("progress");
const timer = document.getElementById("timer");
const misses = document.getElementById("misses");
const statusText = document.getElementById("status");
const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const quitBtn = document.getElementById("quitBtn");
const difficultyInputs = document.querySelectorAll("input[name='difficulty']");

let hitCount = 0;
let missCount = 0;
let startedAt = 0;
let running = false;
let animationFrameId = null;
let currentDifficulty = "easy";
let paused = false;
let elapsedBeforePause = 0;

function formatSeconds(seconds) {
    return `${seconds.toFixed(2)}s`;
}

function updateTimer() {
    if (!running || paused) {
        return;
    }

    const elapsed = elapsedBeforePause + (performance.now() - startedAt) / 1000;
    timer.textContent = formatSeconds(elapsed);
    animationFrameId = requestAnimationFrame(updateTimer);
}

function moveTargetRandomly() {
    const maxX = Math.max(0, arena.clientWidth - target.offsetWidth);
    const maxY = Math.max(0, arena.clientHeight - target.offsetHeight - 56);

    const x = Math.random() * maxX;
    const y = Math.random() * maxY;

    target.style.left = `${x}px`;
    target.style.top = `${y}px`;
}

function applyDifficulty() {
    playfield.classList.toggle("hard", currentDifficulty === "hard");
}

function finishGame() {
    running = false;
    paused = false;
    cancelAnimationFrame(animationFrameId);

    const clearTime = elapsedBeforePause + (performance.now() - startedAt) / 1000;
    timer.textContent = formatSeconds(clearTime);
    statusText.textContent = `クリア！ タイム: ${formatSeconds(clearTime)}  ミス: ${missCount}`;
    statusText.classList.add("clear");
    startBtn.textContent = "もう一度";
    pauseBtn.textContent = "一時停止";
    pauseBtn.disabled = true;
    quitBtn.disabled = true;
    target.style.display = "none";
}

function startGame() {
    hitCount = 0;
    missCount = 0;
    running = true;
    paused = false;
    elapsedBeforePause = 0;
    startedAt = performance.now();

    progress.textContent = `0 / ${TOTAL_TARGETS}`;
    timer.textContent = "0.00s";
    misses.textContent = "0";
    statusText.textContent = "ターゲットをクリック";
    statusText.classList.remove("clear");
    startBtn.textContent = "リスタート";
    pauseBtn.textContent = "一時停止";
    pauseBtn.disabled = false;
    quitBtn.disabled = false;

    applyDifficulty();
    playfield.scrollTop = 0;
    playfield.scrollLeft = 0;

    target.style.display = "block";
    moveTargetRandomly();

    cancelAnimationFrame(animationFrameId);
    animationFrameId = requestAnimationFrame(updateTimer);
}

function togglePause() {
    if (!running) {
        return;
    }

    if (!paused) {
        paused = true;
        elapsedBeforePause += (performance.now() - startedAt) / 1000;
        timer.textContent = formatSeconds(elapsedBeforePause);
        statusText.textContent = "一時停止中";
        pauseBtn.textContent = "再開";
        cancelAnimationFrame(animationFrameId);
        return;
    }

    paused = false;
    startedAt = performance.now();
    statusText.textContent = "ターゲットをクリック";
    pauseBtn.textContent = "一時停止";
    cancelAnimationFrame(animationFrameId);
    animationFrameId = requestAnimationFrame(updateTimer);
}

function quitGame() {
    running = false;
    paused = false;
    elapsedBeforePause = 0;
    cancelAnimationFrame(animationFrameId);

    hitCount = 0;
    missCount = 0;
    progress.textContent = `0 / ${TOTAL_TARGETS}`;
    timer.textContent = "0.00s";
    misses.textContent = "0";

    statusText.textContent = "中断しました。スタートを押して再開";
    statusText.classList.remove("clear");
    target.style.display = "none";

    playfield.scrollTop = 0;
    playfield.scrollLeft = 0;

    startBtn.textContent = "スタート";
    pauseBtn.textContent = "一時停止";
    pauseBtn.disabled = true;
    quitBtn.disabled = true;
}

difficultyInputs.forEach((input) => {
    input.addEventListener("change", () => {
        if (!input.checked) {
            return;
        }

        currentDifficulty = input.value;

        if (!running) {
            applyDifficulty();
        }
    });
});

startBtn.addEventListener("click", startGame);
pauseBtn.addEventListener("click", togglePause);
quitBtn.addEventListener("click", quitGame);

target.addEventListener("click", (event) => {
    event.stopPropagation();

    if (!running || paused) {
        return;
    }

    hitCount += 1;
    progress.textContent = `${hitCount} / ${TOTAL_TARGETS}`;

    if (hitCount >= TOTAL_TARGETS) {
        finishGame();
        return;
    }

    moveTargetRandomly();
});

playfield.addEventListener("click", (event) => {
    if (!running || paused || event.target === target) {
        return;
    }

    missCount += 1;
    misses.textContent = String(missCount);
});

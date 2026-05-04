(function () {
    var body = document.body;
    if (!body || !body.classList.contains("has-site-layout")) {
        return;
    }

    var nav = document.querySelector("[data-site-nav]");
    var toggle = document.querySelector("[data-nav-toggle]");
    var active = body.dataset.nav;

    if (active) {
        document.querySelectorAll("[data-nav-link]").forEach(function (link) {
            if (link.getAttribute("data-nav-link") === active) {
                link.classList.add("is-active");
                link.setAttribute("aria-current", "page");
            }
        });
    }

    var actions = document.querySelectorAll(".site-actions .site-btn");
    if (nav && actions.length) {
        actions.forEach(function (action) {
            var href = action.getAttribute("href");
            if (!href || nav.querySelector('[data-mobile-action="' + href + '"]')) {
                return;
            }

            var cloned = action.cloneNode(true);
            cloned.classList.add("site-nav__link", "site-nav__link--action");
            cloned.setAttribute("data-mobile-action", href);
            nav.appendChild(cloned);
        });
    }

    function closeMenu() {
        if (!nav || !toggle) {
            return;
        }
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
    }

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            var isOpen = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", String(isOpen));
        });

        document.addEventListener("click", function (event) {
            var target = event.target;
            if (!target.closest(".site-header")) {
                closeMenu();
            }
        });

        window.addEventListener("resize", function () {
            if (window.innerWidth > 900) {
                closeMenu();
            }
        });
    }

    var yearNode = document.querySelector("[data-year]");
    if (yearNode) {
        yearNode.textContent = String(new Date().getFullYear());
    }
})();

const TOTAL_TARGETS = 10;

const playfield = document.getElementById("playfield");
const arena = document.getElementById("arena");
const target = document.getElementById("target");
const progress = document.getElementById("progress");
const timer = document.getElementById("timer");
const misses = document.getElementById("misses");
const remaining = document.getElementById("remaining");
const progressBar = document.getElementById("progressBar");
const finishText = document.getElementById("finishText");
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

    if (!running) {
        playfield.style.setProperty("--scroll-bg-x", "0px");
        playfield.style.setProperty("--scroll-bg-y", "0px");
    }

    if (!isEasy) {
        updateFinishPosition();
        updateGridLines();
    }
}

function updateHardScrollBackground() {
    if (!playfield.classList.contains("hard")) {
        return;
    }

    const x = Math.round(-playfield.scrollLeft * 1.25);
    const y = Math.round(-playfield.scrollTop * 1.1);
    playfield.style.setProperty("--scroll-bg-x", `${x}px`);
    playfield.style.setProperty("--scroll-bg-y", `${y}px`);
}

function updateFinishPosition() {
    if (!playfield.classList.contains("hard")) {
        return;
    }

    const playfieldRect = playfield.getBoundingClientRect();
    const centerX = playfieldRect.left + playfieldRect.width / 2;
    const centerY = playfieldRect.top + playfieldRect.height / 2;

    // 要素の中央がplayfield中央になるよう調整
    finishText.style.left = `${centerX - finishText.offsetWidth / 2}px`;
    finishText.style.top = `${centerY - finishText.offsetHeight / 2}px`;
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
    running = false;
    paused = false;
    cancelAnimationFrame(animationFrameId);

    const clearTime = elapsedBeforePause + (performance.now() - startedAt) / 1000;
    timer.textContent = formatSeconds(clearTime);
    startBtn.textContent = "もう一度";
    pauseBtn.textContent = "一時停止";
    pauseBtn.disabled = true;
    quitBtn.disabled = true;
    target.classList.remove("is-paused");
    target.style.display = "none";
    finishText.classList.add("is-visible");
}

function startGame() {
    hitCount = 0;
    missCount = 0;
    running = true;
    paused = false;
    elapsedBeforePause = 0;
    startedAt = performance.now();

    renderProgress();
    timer.textContent = "0.00s";
    misses.textContent = "0";
    startBtn.textContent = "リスタート";
    pauseBtn.textContent = "一時停止";
    pauseBtn.disabled = false;
    quitBtn.disabled = false;
    finishText.classList.remove("is-visible");

    applyDifficulty();
    playfield.scrollTop = 0;
    playfield.scrollLeft = 0;
    updateHardScrollBackground();
    updateGridLines();

    target.style.display = "block";
    target.classList.remove("is-paused");
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
        pauseBtn.textContent = "再開";
        target.classList.add("is-paused");
        cancelAnimationFrame(animationFrameId);
        return;
    }

    paused = false;
    startedAt = performance.now();
    pauseBtn.textContent = "一時停止";
    target.classList.remove("is-paused");
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
    renderProgress();
    timer.textContent = "0.00s";
    misses.textContent = "0";
    target.classList.remove("is-paused");
    target.style.display = "none";
    finishText.classList.remove("is-visible");

    playfield.scrollTop = 0;
    playfield.scrollLeft = 0;
    updateHardScrollBackground();
    updateGridLines();

    startBtn.textContent = "スタート";
    pauseBtn.textContent = "一時停止";
    pauseBtn.disabled = true;
    quitBtn.disabled = true;
}

difficultyEasy.addEventListener("click", () => {
    currentDifficulty = "easy";
    if (!running) {
        applyDifficulty();
    } else {
        applyDifficulty();
        moveTargetRandomly();
    }
});

difficultyHard.addEventListener("click", () => {
    currentDifficulty = "hard";
    if (!running) {
        applyDifficulty();
        updateHardScrollBackground();
        updateGridLines();
    } else {
        applyDifficulty();
        updateHardScrollBackground();
        updateGridLines();
        moveTargetRandomly();
    }
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
    renderProgress();

    if (hitCount >= TOTAL_TARGETS) {
        finishGame();
        return;
    }

    moveTargetRandomly();
});

playfield.addEventListener("scroll", () => {
    updateHardScrollBackground();
    updateFinishPosition();
    updateGridLines();
});

playfield.addEventListener("click", (event) => {
    if (!running || paused || event.target === target) {
        return;
    }

    missCount += 1;
    misses.textContent = String(missCount);
});

renderProgress();
applyDifficulty();
window.addEventListener("resize", renderProgress);

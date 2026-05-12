(function () {
    var body = document.body;
    if (!body || !body.classList.contains("has-site-layout")) {
        return;
    }

    var nav = document.querySelector("[data-site-nav]");
    var toggle = document.querySelector("[data-nav-toggle]");
    var groups = Array.prototype.slice.call(document.querySelectorAll(".site-nav__group"));
    var active = body.dataset.nav;
    var isMobile = function () {
        return window.innerWidth <= 900;
    };

    function setGroupState(group, open) {
        if (!group) {
            return;
        }
        group.classList.toggle("is-open", open);
        var trigger = group.querySelector("[data-nav-trigger]");
        if (trigger) {
            trigger.setAttribute("aria-expanded", String(open));
        }
    }

    function closeAllGroups() {
        groups.forEach(function (group) {
            setGroupState(group, false);
        });
    }

    if (active) {
        document.querySelectorAll("[data-nav-link]").forEach(function (link) {
            if (link.getAttribute("data-nav-link") === active) {
                link.classList.add("is-active");
                link.setAttribute("aria-current", "page");
                var group = link.closest(".site-nav__group");
                if (group) {
                    group.classList.add("is-active");
                }
            }
        });
    }

    groups.forEach(function (group) {
        var trigger = group.querySelector("[data-nav-trigger]");
        if (!trigger) {
            return;
        }

        trigger.addEventListener("click", function () {
            if (!isMobile()) {
                var opening = !group.classList.contains("is-open");
                closeAllGroups();
                setGroupState(group, opening);
                return;
            }

            var isOpen = group.classList.contains("is-open");
            closeAllGroups();
            setGroupState(group, !isOpen);
        });

        group.addEventListener("mouseenter", function () {
            if (isMobile()) {
                return;
            }
            closeAllGroups();
            setGroupState(group, true);
        });

        group.addEventListener("mouseleave", function () {
            if (isMobile()) {
                return;
            }
            setGroupState(group, false);
        });

        group.addEventListener("focusin", function () {
            if (isMobile()) {
                return;
            }
            closeAllGroups();
            setGroupState(group, true);
        });

        group.addEventListener("focusout", function (event) {
            if (isMobile()) {
                return;
            }
            var nextTarget = event.relatedTarget;
            if (nextTarget && group.contains(nextTarget)) {
                return;
            }
            setGroupState(group, false);
        });
    });

    if (nav) {
        nav.addEventListener("mouseleave", function () {
            if (isMobile()) {
                return;
            }
            closeAllGroups();
        });
    }

    function closeMenu() {
        if (!nav || !toggle) {
            return;
        }
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        closeAllGroups();
    }

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            var isOpen = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", String(isOpen));
            if (!isOpen) {
                closeAllGroups();
            }
        });

        document.addEventListener("click", function (event) {
            var target = event.target;
            if (!target.closest(".site-header")) {
                closeMenu();
            } else if (!target.closest(".site-nav__group")) {
                closeAllGroups();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeMenu();
            }
        });

        window.addEventListener("resize", function () {
            if (window.innerWidth > 900) {
                nav.classList.remove("is-open");
                toggle.setAttribute("aria-expanded", "false");
                closeAllGroups();
            }
        });
    }

    var yearNode = document.querySelector("[data-year]");
    if (yearNode) {
        yearNode.textContent = String(new Date().getFullYear());
    }
})();

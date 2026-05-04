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

/**
 * password-toggle.js
 * Show/hide for every password field: the eye button next to it switches the input
 * between hidden dots (type="password") and readable text (type="text").
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    const ICONS = {
        show: '<i class="bi bi-eye" aria-hidden="true"></i>',
        hide: '<i class="bi bi-eye-slash" aria-hidden="true"></i>'
    };

    document.querySelectorAll(".password-toggle").forEach(function (button) {
        const input = document.querySelector("#" + button.getAttribute("aria-controls"));

        button.addEventListener("click", function () {
            const willShow = input.type === "password";

            input.type = willShow ? "text" : "password";
            button.innerHTML = willShow ? ICONS.hide : ICONS.show;
            button.setAttribute("aria-label", willShow ? "Hide password" : "Show password");
            button.setAttribute("aria-pressed", String(willShow));
        });
    });
})();
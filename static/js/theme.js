/**
 * theme.js
 * Dark mode for every page of CourtList Supply.
 * Loaded in <head>, so the saved theme is applied before the page is drawn
 * (no white flash). The logos and the toggle button are updated once the page has loaded.
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    // localStorage key for the user's theme choice
    const THEME_KEY = "courtlist-theme";

    /**
     * Returns the theme to start with: the saved choice if there is one,
     * otherwise the visitor's operating system setting.
     */
    function getInitialTheme() {
        let saved = null;
        try {
            saved = localStorage.getItem(THEME_KEY);
        } catch (error) {
            // localStorage can be blocked (e.g. some private modes); fall back to the OS setting
        }

        if (saved === "light" || saved === "dark") {
            return saved;
        }
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    /**
     * Applies a theme everywhere: Bootstrap colours (data-bs-theme on <html>),
     * every logo, the toggle button's icon and label, and tells other scripts about it.
     */
    function applyTheme(theme) {
        document.documentElement.setAttribute("data-bs-theme", theme);

        // Each logo carries both image addresses in data attributes, written by Django in base.html
        document.querySelectorAll(".site-logo").forEach(function (logo) {
            logo.src = theme === "dark" ? logo.dataset.logoDark : logo.dataset.logoLight;
        });

        // The button shows what clicking will switch to: a sun in dark mode, a moon in light mode
        const toggle = document.querySelector("#theme-toggle");
        if (toggle) {
            const nextTheme = theme === "dark" ? "light" : "dark";
            toggle.innerHTML =
                theme === "dark"
                    ? '<i class="bi bi-sun" aria-hidden="true"></i>'
                    : '<i class="bi bi-moon-stars" aria-hidden="true"></i>';
            toggle.setAttribute("aria-label", "Switch to " + nextTheme + " mode");
        }

        // Let page scripts (e.g. the analytics charts later) react to the theme change
        document.dispatchEvent(new CustomEvent("courtlist:themechange", { detail: { theme: theme } }));
    }

    let currentTheme = getInitialTheme();

    // Runs straight away, while the page is still loading: Bootstrap's colours are right from the start
    document.documentElement.setAttribute("data-bs-theme", currentTheme);

    // Runs once all the HTML has loaded, when the logos and the toggle button exist
    document.addEventListener("DOMContentLoaded", function () {
        applyTheme(currentTheme);

        document.querySelector("#theme-toggle").addEventListener("click", function () {
            currentTheme = currentTheme === "dark" ? "light" : "dark";
            applyTheme(currentTheme);
            try {
                localStorage.setItem(THEME_KEY, currentTheme);
            } catch (error) {
                // Saving failed (storage blocked); the theme still changes for this page
            }
        });
    });
})();
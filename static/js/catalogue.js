/**
 * catalogue.js
 * Remembers which sidebar panels (Categories, Filters) the user closed, so they
 * stay closed after a search or filter reloads the page.
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    // localStorage key holding the ids of the closed panels, e.g. ["filter-panel"]
    const STORAGE_KEY = "courtlist-closed-panels";

    /** Returns the list of closed panel ids, or an empty list if nothing is saved. */
    function readClosedPanels() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        } catch (error) {
            return []; // storage blocked or data broken: treat every panel as open
        }
    }

    /** Saves the list of closed panel ids. */
    function saveClosedPanels(ids) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
        } catch (error) {
            // Saving failed (storage blocked); the panels still work for this page
        }
    }

    document.querySelectorAll(".sidebar-panel").forEach(function (panel) {
        const toggle = document.querySelector('[data-bs-target="#' + panel.id + '"]');

        // On page load: close the panels the user closed last time
        if (readClosedPanels().includes(panel.id)) {
            panel.classList.remove("show");
            toggle.classList.add("collapsed");
            toggle.setAttribute("aria-expanded", "false");
        }

        // Bootstrap fires these events after a panel finishes closing or opening
        panel.addEventListener("hidden.bs.collapse", function () {
            const closed = readClosedPanels().filter(function (id) {
                return id !== panel.id;
            });
            closed.push(panel.id);
            saveClosedPanels(closed);
        });

        panel.addEventListener("shown.bs.collapse", function () {
            const closed = readClosedPanels().filter(function (id) {
                return id !== panel.id;
            });
            saveClosedPanels(closed);
        });
    });
})();
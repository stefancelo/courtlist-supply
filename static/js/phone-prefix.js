/**
 * phone-prefix.js
 * The country-code dropdown in the phone field shows full names while open
 * ("Greece (+30)") but only the code once chosen ("+30"), so it stays narrow.
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    document.querySelectorAll(".phone-prefix").forEach(function (select) {
        const options = select.querySelectorAll("option");

        // Remember every option's full label before changing anything
        options.forEach(function (option) {
            option.dataset.fullLabel = option.textContent;
        });

        /** Closed: options with a value show only the code, e.g. "+30". */
        function showCodes() {
            options.forEach(function (option) {
                if (option.value) {
                    option.textContent = option.value;
                }
            });
        }

        /** Open: every option shows its full label again. */
        function showFullNames() {
            options.forEach(function (option) {
                option.textContent = option.dataset.fullLabel;
            });
        }

        showCodes();
        select.addEventListener("mousedown", showFullNames); // just before the list opens with a click
        select.addEventListener("focus", showFullNames); // reaching it with the Tab key
        select.addEventListener("change", showCodes); // an option was picked
        select.addEventListener("blur", showCodes); // the user left the dropdown
    });
})();
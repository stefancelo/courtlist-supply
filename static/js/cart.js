/**
 * cart.js
 * Updates the cart instantly: when a quantity changes, it is sent to the server with
 * fetch, and the line total, cart total and navbar count are replaced with the answer.
 * Without JavaScript, the Update buttons still work as normal forms.
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    const totalElement = document.querySelector("#cart-total");
    const countElement = document.querySelector("#cart-count");
    const DELAY = 300; // milliseconds to wait after the last keystroke

    /** Sends one line's new quantity and shows the prices the server calculated. */
    async function updateLine(form) {
        try {
            const response = await fetch(form.action, {
                method: "POST",
                headers: { "X-Requested-With": "fetch" },
                body: new FormData(form)
            });
            if (!response.ok) {
                return;
            }
            const data = await response.json();

            form.querySelector(".quantity-input").value = data.quantity;
            form.closest(".cart-line").querySelector(".line-total").textContent = "€" + data.line_total;
            totalElement.textContent = "€" + data.total;
            if (countElement) {
                countElement.textContent = data.count;
            }
        } catch (error) {
            // Network problem: leave the page as it is; the Update button is a fallback
            form.querySelector("button").hidden = false;
        }
    }

    document.querySelectorAll(".quantity-form").forEach(function (form) {
        const input = form.querySelector(".quantity-input");
        let timer = null;

        // With JavaScript running, the Update button isn't needed
        form.querySelector("button").hidden = true;

        input.addEventListener("input", function () {
            clearTimeout(timer);
            // Wait until the box holds a valid number between min and max
            if (input.value === "" || !input.checkValidity()) {
                return;
            }
            timer = setTimeout(function () {
                updateLine(form);
            }, DELAY);
        });

        // Pressing Enter in the box: update without reloading the page
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            updateLine(form);
        });
    });
})();
/**
 * predictions.js
 * Sends a prediction with fetch when a team button is clicked: the clicked team turns
 * orange and the vote bar is replaced with the one the server sends back.
 * Without JavaScript the buttons still work as a normal form.
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    document.querySelectorAll(".prediction-form").forEach(function (form) {
        const message = form.querySelector(".prediction-message");

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            const clicked = event.submitter;
            const body = new FormData(form);
            body.append("winner", clicked.value);
            message.textContent = "";

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    headers: { "X-Requested-With": "fetch" },
                    body: body
                });
                const data = await response.json();
                if (!data.ok) {
                    message.textContent = data.message;
                    return;
                }

                document.querySelector("#votes-" + form.dataset.fixture).outerHTML = data.bar_html;
                form.querySelectorAll("button").forEach(function (button) {
                    const isPick = button === clicked;
                    button.classList.toggle("btn-orange", isPick);
                    button.classList.toggle("btn-outline-secondary", !isPick);
                    button.setAttribute("aria-pressed", String(isPick));
                });
            } catch (error) {
                message.textContent = "Your prediction couldn't be sent. Please try again.";
            }
        });
    });
})();
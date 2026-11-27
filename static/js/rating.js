/**
 * rating.js
 * Sends the rating form with fetch, so the page doesn't reload: the server saves the
 * rating and answers with JSON, including the refreshed summary and reviews as HTML.
 * Without JavaScript the form still works as a normal POST.
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    const form = document.querySelector("#rating-form");
    if (!form) {
        return;
    }
    const message = document.querySelector("#rating-message");
    const summary = document.querySelector("#rating-summary");
    const reviewList = document.querySelector("#review-list");
    const button = form.querySelector("button[type=submit]");

    /** Shows a green (saved) or red (problem) line under the button. */
    function showMessage(text, isError) {
        message.textContent = text;
        message.classList.toggle("text-danger", isError);
        message.classList.toggle("text-success", !isError);
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        button.disabled = true;

        try {
            const response = await fetch(form.action, {
                method: "POST",
                headers: { "X-Requested-With": "fetch" },
                body: new FormData(form)
            });
            const data = await response.json();

            if (data.ok) {
                summary.innerHTML = data.summary_html;
                reviewList.innerHTML = data.reviews_html;
                button.textContent = "Update your rating";
            }
            showMessage(data.message, !data.ok);
        } catch (error) {
            showMessage("Your rating couldn't be sent. Please try again.", true);
        } finally {
            button.disabled = false;
        }
    });
})();
/**
 * chat.js
 * Makes the Gameweek chat live: messages are sent with fetch (no reload), and every few
 * seconds the page asks the server for messages newer than the last one it has.
 * Before someone's first message, the chat rules must be accepted (remembered in this browser).
 * Enter sends, Shift + Enter adds a new line. Without JavaScript the form posts normally.
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    const list = document.querySelector("#chat-messages");
    if (!list) {
        return;
    }
    const form = document.querySelector("#chat-form");
    const errorBox = document.querySelector("#chat-error");
    const url = list.dataset.url;
    const POLL_EVERY = 5000; // milliseconds
    const RULES_KEY = "courtlist-chat-rules-accepted";
    let rulesAcceptedHere = false; // fallback if localStorage is blocked

    /** The id of the newest message on the page (0 if there are none). */
    function lastId() {
        const messages = list.querySelectorAll(".chat-message");
        return messages.length ? messages[messages.length - 1].dataset.id : 0;
    }

    function scrollToBottom() {
        list.scrollTop = list.scrollHeight;
    }

    /** True if the user is reading the latest messages (not scrolled up through older ones). */
    function isNearBottom() {
        return list.scrollHeight - list.scrollTop - list.clientHeight < 80;
    }

    /** Adds new messages at the bottom, skipping any that are already on the page. */
    function append(messages) {
        if (!messages.length) {
            return;
        }
        const followLatest = isNearBottom();
        const empty = document.querySelector("#chat-empty");
        if (empty) {
            empty.remove();
        }
        messages.forEach(function (message) {
            if (!list.querySelector('[data-id="' + message.id + '"]')) {
                list.insertAdjacentHTML("beforeend", message.html);
            }
        });
        if (followLatest) {
            scrollToBottom();
        }
    }

    /** Asks the server for messages newer than the last one on the page. */
    async function poll() {
        if (document.hidden) {
            return; // the tab isn't visible: don't use the network for nothing
        }
        try {
            const response = await fetch(url + "?after=" + lastId());
            if (response.ok) {
                append((await response.json()).messages);
            }
        } catch (error) {
            // Offline for a moment: the next poll will try again
        }
    }

    /** True if this browser has already accepted the chat rules. */
    function rulesAccepted() {
        try {
            return localStorage.getItem(RULES_KEY) === "yes" || rulesAcceptedHere;
        } catch (error) {
            return rulesAcceptedHere;
        }
    }

    function rememberRulesAccepted() {
        rulesAcceptedHere = true;
        try {
            localStorage.setItem(RULES_KEY, "yes");
        } catch (error) {
            // Storage blocked: the rules are remembered until the page is closed
        }
    }

    if (form) {
        const textBox = form.querySelector("textarea");
        const rulesModal = bootstrap.Modal.getOrCreateInstance(document.querySelector("#chat-rules"));

        /** Sends the message with fetch and shows it (plus anything new) straight away. */
        async function send() {
            errorBox.textContent = "";
            try {
                const response = await fetch(url + "?after=" + lastId(), {
                    method: "POST",
                    headers: { "X-Requested-With": "fetch" },
                    body: new FormData(form)
                });
                const data = await response.json();
                if (!data.ok) {
                    errorBox.textContent = data.message;
                    return;
                }
                append(data.messages);
                scrollToBottom();
                textBox.value = "";
                textBox.focus();
            } catch (error) {
                errorBox.textContent = "Your message couldn't be sent. Please try again.";
            }
        }

        textBox.addEventListener("keydown", function (event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                form.requestSubmit();
            }
        });

        form.addEventListener("submit", function (event) {
            event.preventDefault();
            if (rulesAccepted()) {
                send();
            } else {
                rulesModal.show(); // the message is sent once "I agree" is clicked
            }
        });

        document.querySelector("#chat-rules-accept").addEventListener("click", function () {
            rememberRulesAccepted();
            rulesModal.hide();
            if (textBox.value.trim()) {
                send();
            }
        });
    }

    scrollToBottom();
    setInterval(poll, POLL_EVERY);
})();
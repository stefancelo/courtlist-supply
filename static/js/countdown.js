/**
 * countdown.js
 * Counts down to the next tip-off, updating every second. The tip-off time comes from
 * the page (data-tip-off), written by Django in ISO format.
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    const box = document.querySelector("#countdown");
    if (!box) {
        return;
    }

    const tipOff = new Date(box.dataset.tipOff).getTime();
    const units = {
        days: box.querySelector("[data-unit=days]"),
        hours: box.querySelector("[data-unit=hours]"),
        minutes: box.querySelector("[data-unit=minutes]"),
        seconds: box.querySelector("[data-unit=seconds]")
    };
    let timerId = null;

    /** Two digits, e.g. 7 -> "07". */
    function pad(number) {
        return String(number).padStart(2, "0");
    }

    function update() {
        const secondsLeft = Math.max(0, Math.floor((tipOff - Date.now()) / 1000));

        units.days.textContent = Math.floor(secondsLeft / 86400);
        units.hours.textContent = pad(Math.floor((secondsLeft % 86400) / 3600));
        units.minutes.textContent = pad(Math.floor((secondsLeft % 3600) / 60));
        units.seconds.textContent = pad(secondsLeft % 60);

        if (secondsLeft === 0) {
            clearInterval(timerId);
        }
    }

    update();
    timerId = setInterval(update, 1000);
})();
/**
 * analytics.js
 * Loads the admin statistics from the JSON view with fetch and draws them with Chart.js.
 * Changing a filter reloads only the data, not the page; switching dark mode redraws
 * the charts in the new colours.
 * Wrapped in an IIFE so none of its variables become global.
 */
(function () {
    "use strict";

    const form = document.querySelector("#analytics-filters");
    const errorBox = document.querySelector("#analytics-error");
    const charts = {};
    let latestData = null;

    /** Reads a CSS variable, e.g. Bootstrap's text colour, so the charts match the theme. */
    function cssVar(name) {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    }

    /** Describes a chart's numbers in its aria-label, for screen readers. */
    function describe(id, labels, values) {
        const canvas = document.querySelector("#" + id);
        const parts = labels.map(function (label, index) {
            return label + " " + values[index];
        });
        canvas.setAttribute("aria-label", canvas.dataset.title + ": " + (parts.join(", ") || "no data"));
    }

    /** Draws a chart on its canvas, removing the chart that was there before. */
    function draw(id, config) {
        if (charts[id]) {
            charts[id].destroy();
        }
        charts[id] = new Chart(document.querySelector("#" + id), config);
    }

    /** A simple bar chart in the brand orange. horizontal puts the names on the side. */
    function barChart(id, block, horizontal, max) {
        const valueAxis = horizontal ? "x" : "y";
        const scales = {};
        scales[valueAxis] = { beginAtZero: true, max: max, ticks: { precision: max ? 1 : 0 } };

        draw(id, {
            type: "bar",
            data: {
                labels: block.labels,
                datasets: [{ data: block.values, backgroundColor: cssVar("--cl-orange") }]
            },
            options: {
                indexAxis: horizontal ? "y" : "x",
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: scales
            }
        });
        describe(id, block.labels, block.values);
    }

    /** Fills the totals and draws all five charts from one JSON answer. */
    function render(data) {
        Chart.defaults.color = cssVar("--bs-body-color");
        Chart.defaults.borderColor = cssVar("--bs-border-color");
        Chart.defaults.font.family = cssVar("--bs-body-font-family");

        document.querySelector("#total-orders").textContent = data.totals.orders;
        document.querySelector("#total-revenue").textContent =
            "€" + Number(data.totals.revenue).toLocaleString("en-GB", { minimumFractionDigits: 2 });

        draw("sales-chart", {
            type: "bar",
            data: {
                labels: data.sales.labels,
                datasets: [
                    {
                        type: "bar",
                        label: "Orders",
                        data: data.sales.orders,
                        backgroundColor: cssVar("--bs-secondary-color"),
                        yAxisID: "orders"
                    },
                    {
                        type: "line",
                        label: "Revenue (€)",
                        data: data.sales.revenue,
                        borderColor: cssVar("--cl-orange"),
                        backgroundColor: cssVar("--cl-orange"),
                        cubicInterpolationMode: "monotone",
                        yAxisID: "revenue"
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    orders: { position: "left", beginAtZero: true, ticks: { precision: 0 } },
                    revenue: { position: "right", beginAtZero: true, grid: { drawOnChartArea: false } }
                }
            }
        });
        describe("sales-chart", ["Orders", "Revenue in euros"], [data.totals.orders, data.totals.revenue]);

        barChart("best-sellers-chart", data.best_sellers, true);
        barChart("top-rated-chart", data.top_rated, true, 5);
        barChart("searches-chart", data.searches, false);

        draw("viewed-chart", {
            type: "doughnut",
            data: {
                labels: data.most_viewed.labels,
                datasets: [
                    {
                        data: data.most_viewed.values,
                        backgroundColor: [
                            cssVar("--cl-orange"),
                            cssVar("--bs-primary"),
                            cssVar("--bs-success"),
                            cssVar("--bs-warning"),
                            cssVar("--bs-info")
                        ]
                    }
                ]
            },
            options: { maintainAspectRatio: false }
        });
        describe("viewed-chart", data.most_viewed.labels, data.most_viewed.values);
    }

    /** Asks the JSON view for the statistics matching the filters, then draws them. */
    async function load() {
        const params = new URLSearchParams(new FormData(form));
        errorBox.textContent = "";

        try {
            const response = await fetch(form.dataset.url + "?" + params);
            const data = await response.json();
            if (!response.ok) {
                errorBox.textContent = data.errors.join(" ");
                return;
            }
            latestData = data;
            render(data);
        } catch (error) {
            errorBox.textContent = "The statistics couldn't be loaded. Please try again.";
        }
    }

    form.addEventListener("change", load);
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        load();
    });
    document.addEventListener("courtlist:themechange", function () {
        if (latestData) {
            render(latestData);
        }
    });

    load();
})();
// AI-assisted comment: the lightweight canvas chart was drafted with AI support and reviewed for this CS50x project.
document.addEventListener("DOMContentLoaded", () => {
    const chart = document.querySelector("#statusChart");
    if (!chart) {
        return;
    }

    const labels = JSON.parse(chart.dataset.labels || "[]");
    const values = JSON.parse(chart.dataset.values || "[]");
    const ctx = chart.getContext("2d");
    const width = chart.width = chart.clientWidth;
    const height = chart.height = 190;
    const max = Math.max(...values, 1);
    const barWidth = labels.length ? width / labels.length - 14 : width;

    ctx.clearRect(0, 0, width, height);
    ctx.font = "12px system-ui";
    ctx.fillStyle = "#9aa8ba";

    if (!labels.length) {
        ctx.fillText("No project data yet", 16, 94);
        return;
    }

    labels.forEach((label, index) => {
        const value = values[index];
        const x = index * (barWidth + 14) + 8;
        const barHeight = (value / max) * 115;
        const y = 140 - barHeight;
        const gradient = ctx.createLinearGradient(0, y, 0, 140);
        gradient.addColorStop(0, "#69e2ff");
        gradient.addColorStop(1, "#2f8cff");
        ctx.fillStyle = gradient;
        ctx.roundRect(x, y, barWidth, barHeight, 8);
        ctx.fill();
        ctx.fillStyle = "#f5f7fb";
        ctx.fillText(String(value), x + 4, y - 8);
        ctx.fillStyle = "#9aa8ba";
        ctx.fillText(label.slice(0, 11), x, 168);
    });
});

let currentStation = null;
let historicalChart = null;
let historicalMode = "days";

// lily add: fetch historical data from flask
async function fetchHistoricalData(stationId, mode) {
  const endpoint =
    mode === "hours"
      ? `/availability/${stationId}/hourly`
      : `/availability/${stationId}/daily`;

  const r = await fetch(endpoint);
  if (!r.ok) {
    throw new Error(`Failed to load historical ${mode} data`);
  }

  return await r.json();
}

// lily add: render chart
function renderHistoricalChart(data, mode) {
  const canvas = document.getElementById("historicalCanvas");
  if (!canvas) return;

  const labels = data.series.map(d => formatLabel(d.bucket, mode));
  const bikes = data.series.map(item => Number(item.avg_bikes ?? 0));
  const stands = data.series.map(item => Number(item.avg_stands ?? 0));

  if (historicalChart) {
    historicalChart.destroy();
  }

  historicalChart = new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Available bikes",
          data: bikes,
          backgroundColor: "#4CAF50"
        },
        {
          label: "Free bike stands",
          data: stands,
          backgroundColor: "#FF9800"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

function formatLabel(bucket, mode) {
    if (mode === "days") {
        // bucket 例子: 2026-03-10
        const date = new Date(bucket);
        return date.toLocaleDateString("en-IE", {day: "numeric",
            month: "short" });
        // 输出 Mon / Tue / Wed
    } else {
        // bucket 例子: 2026-03-14 13:00:00
        const date = new Date(bucket.replace(" ", "T"));
        return date.toLocaleTimeString("en-IE", {
            hour: "numeric",
            minute: "2-digit",
            hour12: true
        });
        // 输出 3:00 pm
    }
}

// lily add: load chart
async function loadHistoricalChart(station, mode = "days") {
  if (!station) return;

  try {
    console.log("clicked station:", station);

    const stationId = station.number;
    const data = await fetchHistoricalData(stationId, mode);
    renderHistoricalChart(data, mode);
  } catch (err) {
    console.error("Historical chart load failed:", err);
  }
}

//lily add:init Toggle
function initHistoricalToggle() {
  const buttons = document.querySelectorAll('[data-chart="historical"]');
  const subtitle = document.getElementById("historySubtitle");

  buttons.forEach(btn => {
    btn.addEventListener("click", async () => {
      buttons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      historicalMode = btn.dataset.mode;

      if (subtitle) {
                subtitle.textContent =
                    historicalMode === "hours"
                        ? "Past 8 hours data"
                        : "Past 7 days data";
            }

      if (currentStation) {
        await loadHistoricalChart(currentStation, historicalMode);
      }
    });
  });
}

function setCurrentStation(station) {
  currentStation = station;
}

function getHistoricalMode() {
  return historicalMode;
}

window.initHistoricalToggle = initHistoricalToggle;
window.loadHistoricalChart = loadHistoricalChart;
window.setCurrentStation = setCurrentStation;
window.getHistoricalMode = getHistoricalMode;
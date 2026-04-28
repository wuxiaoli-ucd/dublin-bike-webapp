/*
 * Historical Availability
 *
 * Handles the historical availability chart shown in the station panel.
 * The chart can display either:
 * - past 7 days
 * - past 8 hours
 *
 * Data is fetched from the backend availability endpoints and rendered
 * using Chart.js.
 */

let currentStation = null;
let historicalChart = null;
let historicalMode = "days";


async function fetchHistoricalData(stationId, mode) {
  /*
   * Fetches historical availability for the selected station.
   * The endpoint depends on whether the chart is in Hours or Days mode.
   */
  const endpoint =
  mode === "hours"
    ? `/api/availability/${stationId}/hourly`
    : `/api/availability/${stationId}/daily`;

  const r = await fetch(endpoint);
  if (!r.ok) {
    throw new Error(`Failed to load historical ${mode} data`);
  }

  return await r.json();
}


function renderHistoricalChart(data, mode) {
  /*
   * Renders the historical availability chart.
   * Existing Chart.js instances are destroyed before re-rendering to avoid
   * overlapping charts and memory leaks.
   */
  const canvas = document.getElementById("historicalCanvas");
  if (!canvas) return;

  const labels = data.series.map(d => formatLabel(d.bucket, mode));
  const bikes = data.series.map(item => Math.round(Number(item.avg_bikes ?? 0))); // round to display whole number
  const stands = data.series.map(item => Math.round(Number(item.avg_stands ?? 0)));

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
  /*
   * Formats backend time buckets into readable chart labels.
   * Daily buckets are displayed as dates; hourly buckets are displayed as times.
   */  
  if (mode === "days") {
        const date = new Date(bucket);
        return date.toLocaleDateString("en-IE", {
            weekday: "short",
            day: "numeric",
            month: "short"
        });
    } else {
        const date = new Date(bucket.replace(" ", "T") + "Z");
        return date.toLocaleTimeString("en-IE", {
            hour: "numeric",
            minute: "2-digit",
            hour12: true
        });
    }
}


async function loadHistoricalChart(station, mode = "days") {
  /*
   * Loads and renders the chart for the selected station.
   * Called when a station is opened and when the chart mode changes.
   */
  if (!station) return;

  try {
    const stationId = station.number;
    const data = await fetchHistoricalData(stationId, mode);
    renderHistoricalChart(data, mode);
  } catch (err) {
    console.error("Historical chart load failed:", err);
  }
}


function initHistoricalToggle() {
  /*
   * Sets up the Days / Hours toggle for the historical chart.
   * If a station is already selected, switching mode reloads the chart data.
   */
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
  /*
   * Stores the currently selected station so the chart can refresh
   * when toggling between Days and Hours.
   */
  currentStation = station;
}

function getHistoricalMode() {
  return historicalMode;
}

function getCurrentStation() {
  return currentStation;
}

// Expose functions needed by index.js / station panel logic.
window.getCurrentStation = getCurrentStation;
window.initHistoricalToggle = initHistoricalToggle;
window.loadHistoricalChart = loadHistoricalChart;
window.setCurrentStation = setCurrentStation;
window.getHistoricalMode = getHistoricalMode;
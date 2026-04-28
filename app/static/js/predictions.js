/*
 * Predictions
 *
 * Handles prediction requests and the predicted availability chart.
 *
 * Used for:
 * - Single station prediction requests for a selected Depart At time
 * - Predicted availability chart in the station panel
 * - Depart At day options in the directions form
 */

async function fetchPrediction(stationId, date, time) {
  /*
   * Fetches a single predicted availability result for a station.
   * Used when the user selects a specific Depart At date/time.
   */  
  try {
        const formattedTime = time.length === 5 ? `${time}:00` : time;

        const response = await fetch(
            `/api/predict?date=${date}&time=${formattedTime}&station_id=${stationId}`
        );

        const data = await response.json();

        console.log("Prediction response:", data);

        return data;

    } catch (error) {
        console.error("Prediction error:", error);
        return null;
    }
}

function populateDepartDayOptions() {
  /*
   * Populates the Depart At day dropdown with today + next 3 days.
   * This matches the backend prediction window.
   */
  const departDay = document.getElementById("departDay");
  if (!departDay) return;

  departDay.innerHTML = "";

  const today = new Date();

  for (let i = 0; i <= 3; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() + i);

    const isoValue = d.toISOString().split("T")[0];
    const label = d.toLocaleDateString("en-IE", {
      weekday: "long",
      day: "2-digit",
      month: "2-digit",
      year: "2-digit"
    });

    const option = document.createElement("option");
    option.value = isoValue;   // machine-readable value
    option.textContent = label; // user-friendly label
    departDay.appendChild(option);
  }
}


// for chart
let predictedChart = null;
let predictedMode = "days";

// fetch predicted data from flask
async function fetchPredictedData(stationId, mode) {
  /*
   * Fetches prediction data for the selected station.
   * Days mode and Hours mode use separate backend endpoints.
   */
  const endpoint =
    mode === "hours"
      ? `/api/predictions/${stationId}/hourly`
      : `/api/predictions/${stationId}/daily`;

  const r = await fetch(endpoint);
  if (!r.ok) {
    throw new Error(`Failed to load predicted ${mode} data`);
  }
  
  return await r.json();
}


function renderPredictedChart(data, mode) {
  /*
   * Renders the predicted availability chart.
   * Existing Chart.js instances must be destroyed before rendering again.
   */
  const canvas = document.getElementById("predictedCanvas");
  if (!canvas) return;

  const labels = data.series.map(d => formatPredictedLabel(d.bucket, mode));
  const bikes = data.series.map(item => Number(item.predicted_bikes ?? 0));
  const docks = data.series.map(item => Number(item.predicted_docks ?? 0));

  if (predictedChart) {
    predictedChart.destroy();
  }

  predictedChart = new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Available bikes",
          data: bikes,
          backgroundColor: "#1b27d1"
        },
        {
          label: "Free bike stands",
          data: docks,
          backgroundColor: "#ec0a0a"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

function formatPredictedLabel(bucket, mode) {
  /*
   * Formats prediction buckets for chart labels.
   * Daily predictions show dates; hourly predictions show times.
   */
  const date = new Date(bucket);

  if (mode === "days") {
    return date.toLocaleDateString("en-IE", {
      weekday: "short",
      day: "numeric",
      month: "short"
    });
  } else {
    return date.toLocaleTimeString("en-IE", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true
    });
  }
}


async function loadPredictedChart(station, mode = "days") {
  /*
   * Loads and renders prediction chart data for the selected station.
   * Called when opening a station panel and when switching chart mode.
   */
  if (!station) return;

  try {
    const stationId = station.number;
    const data = await fetchPredictedData(stationId, mode);
    renderPredictedChart(data, mode);
  } catch (err) {
    console.error("Predicted chart load failed:", err);
  }
}


function initPredictedToggle() {
  /*
   * Sets up the Days / Hours toggle for predicted availability.
   * Uses the current station from historical_availability.js shared state.
   */
  const buttons = document.querySelectorAll('[data-chart="predicted"]');
  const subtitle = document.getElementById("predictedSubtitle");

  buttons.forEach(btn => {
    btn.addEventListener("click", async () => {
        buttons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      predictedMode = btn.dataset.mode;

      if (subtitle) {
        subtitle.textContent =
          predictedMode === "hours"
            ? "Next 8 hours forecast"
            : "Next 3 days forecast";
      }

    const station = window.getCurrentStation ? window.getCurrentStation() : null;
    if (station) {
    await loadPredictedChart(station, predictedMode);
    }
    });
  });
}

function getPredictedMode() {
  return predictedMode;
}

// Expose functions used by index.js and the station panel logic.
window.initPredictedToggle = initPredictedToggle;
window.loadPredictedChart = loadPredictedChart;
window.getPredictedMode = getPredictedMode;
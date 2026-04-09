async function fetchPrediction(stationId, date, time) {
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

function setPredictionDateLimits() {
    const dateInput = document.getElementById("depart-date");
    if (!dateInput) return;

    const today = new Date();
    const maxDate = new Date();
    maxDate.setDate(today.getDate() + 3);

    const formatDate = (d) => d.toISOString().split("T")[0];

    dateInput.min = formatDate(today);
    dateInput.max = formatDate(maxDate);
}


// for chart
let predictedChart = null;
let predictedMode = "days";

// fetch predicted data from flask
async function fetchPredictedData(stationId, mode) {
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

// render predicted chart
function renderPredictedChart(data, mode) {
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
  if (!station) return;

  try {
    const stationId = station.number;
    const data = await fetchPredictedData(stationId, mode);
    renderPredictedChart(data, mode);
  } catch (err) {
    console.error("Predicted chart load failed:", err);
  }
}

// init toggle
function initPredictedToggle() {
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

window.initPredictedToggle = initPredictedToggle;
window.loadPredictedChart = loadPredictedChart;
window.getPredictedMode = getPredictedMode;
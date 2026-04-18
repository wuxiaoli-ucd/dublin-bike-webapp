// Keeps track of which forecast view is currently selected
// "hourly" = current / near-term forecast
// "daily"  = today + next 3 days
let weatherMode = "hourly";


function getSelectedDepartTimestamp() {
  const departAtBtn = document.getElementById("departAt");
  const departDaySelect = document.getElementById("departDay");
  const timeInput = document.getElementById("departTime");

  // Only use future-based forecast when Depart At is the active mode
  if (!departAtBtn || !departAtBtn.classList.contains("active")) {
    return null;
  }

  if (!departDaySelect || !timeInput || !departDaySelect.value || !timeInput.value) {
    return null;
  }

  // expects departDay option values to be dates like e.g. "2026-04-18"
  const selected = new Date(`${departDaySelect.value}T${timeInput.value}`);

  if (isNaN(selected.getTime())) {
    return null;
  }

  return Math.floor(selected.getTime() / 1000);
}


/**
 * Updates the current-weather summary in the top bar.
 */
async function updateWeatherStatus() {
  try {
    const response = await fetch("/api/weather/current");
    if (!response.ok) {
      throw new Error(`Weather status request failed: ${response.status}`);
    }

    const data = await response.json();

    const weatherEl = document.getElementById("weatherText");
    const tempEl = document.getElementById("tempText");
    const iconEl = document.getElementById("weatherStatusIcon");

    // Update weather text
    if (weatherEl) {
      const valueEl = weatherEl.querySelector(".value");
      if (valueEl) {
        valueEl.textContent = data.weather;
      } else {
        weatherEl.textContent = `Weather: ${data.weather}`;
      }
    }

    // Update temperature text
    if (tempEl) {
      const valueEl = tempEl.querySelector(".value");
      if (valueEl) {
        valueEl.textContent = `${Math.round(data.temp)}°C`;
      } else {
        tempEl.textContent = `Temp: ${Math.round(data.temp)}°C`;
      }
    }

    // Show small weather icon in header
    if (iconEl && data.icon) {
      iconEl.src = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
      iconEl.alt = data.weather || "weather icon";
      iconEl.style.display = "inline-block";
    }
  } catch (err) {
    console.error("Status Bar Error:", err);

    const weatherEl = document.getElementById("weatherText");
    const tempEl = document.getElementById("tempText");
    const iconEl = document.getElementById("weatherStatusIcon");

    if (weatherEl) weatherEl.textContent = "Weather: unavailable";
    if (tempEl) tempEl.textContent = "Temp: N/A";
    if (iconEl) iconEl.style.display = "none";
  }
}


/**
 * Fetches forecast data from the backend.
 *
 * If Hourly mode is active and Depart At is selected,
 * sends base_time so the backend can return hourly forecast
 * starting from the selected departure time.
 */
async function fetchForecastData() {
  const departTimestamp = getSelectedDepartTimestamp();

  let url = "/api/weather/forecast";

  if (weatherMode === "hourly" && departTimestamp) {
    url += `?base_time=${departTimestamp}`;
  }

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Forecast request failed: ${response.status}`);
  }

  return response.json();
}


/**
 * Renders the hourly forecast grid.
 *
 * If chosenToDepartAt is true, labels show clock times from the
 * selected departure time onward rather than "Now".
 */
function renderHourlyWeather(hourlyData, chosenToDepartAt = false) {
  const container = document.getElementById("weatherForecast");
  const updatedEl = document.getElementById("weatherUpdated");

  if (!container) return;

  container.innerHTML = "";

  if (!hourlyData || hourlyData.length === 0) {
    container.innerHTML =
      `<p style="margin:0; color:#bfdbfe;">Hourly forecast unavailable for selected time.</p>`;

    if (updatedEl) {
      updatedEl.textContent = "";
    }
    return;
  }

  hourlyData.slice(0, 4).forEach((item, i) => {
    const label =
      i === 0 && !chosenToDepartAt
        ? "Now"
        : new Date(item.time * 1000).toLocaleTimeString([], {
            hour: "numeric",
            minute: "2-digit",
            hour12: false
          });

    const iconUrl = `https://openweathermap.org/img/wn/${item.icon}@2x.png`;

    const col = document.createElement("div");
    col.className = "column";

    col.innerHTML = `
      <span class="time-label">${label}</span>
      <img class="weather-icon" src="${iconUrl}" alt="weather">
      <span class="temp">${Math.round(item.temp)}°</span>
      <div class="stat">💧 ${Math.round((item.pop || 0) * 100)}%</div>
    `;

    container.appendChild(col);
  });

  if (updatedEl) {
    updatedEl.textContent = chosenToDepartAt
      ? "Forecast based on selected departure time"
      : `Last updated: ${new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false
        })}`;
  }
}


/**
 * Renders the daily forecast grid.
 * Shows Today + next 3 days.
 */
function renderDailyWeather(dailyData) {
  const container = document.getElementById("weatherForecast");
  const updatedEl = document.getElementById("weatherUpdated");

  if (!container) return;

  container.innerHTML = "";

  if (!dailyData || dailyData.length === 0) {
    container.innerHTML =
      `<p style="margin:0; color:#bfdbfe;">Daily forecast unavailable.</p>`;

    if (updatedEl) {
      updatedEl.textContent = "";
    }
    return;
  }

  dailyData.slice(0, 4).forEach((item, i) => {
    const label =
      i === 0
        ? "Today"
        : new Date(item.time * 1000).toLocaleDateString([], {
            weekday: "short"
          });

    const iconUrl = `https://openweathermap.org/img/wn/${item.icon}@2x.png`;

    const col = document.createElement("div");
    col.className = "column";

    col.innerHTML = `
      <span class="time-label">${label}</span>
      <img class="weather-icon" src="${iconUrl}" alt="weather">
      <span class="temp">${Math.round(item.max_temp)}°</span>
      <div class="stat">💧 ${Math.round((item.pop || 0) * 100)}%</div>
    `;

    container.appendChild(col);
  });

  if (updatedEl) {
    updatedEl.textContent = `Last updated: ${new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false
    })}`;
  }
}


/**
 * Main forecast loader.
 * Decides whether to render hourly or daily view.
 */
async function loadWeather() {
  try {
    const data = await fetchForecastData();
    const departTimestamp = getSelectedDepartTimestamp();

    if (weatherMode === "daily") {
      renderDailyWeather(data.daily || []);
    } else {
      renderHourlyWeather(data.hourly || [], Boolean(departTimestamp));
    }
  } catch (err) {
    console.error("Forecast Widget Error:", err);

    const forecastEl = document.getElementById("weatherForecast");
    const updatedEl = document.getElementById("weatherUpdated");

    if (forecastEl) {
      forecastEl.innerHTML =
        `<p style="margin:0; color:#bfdbfe;">Weather forecast unavailable.</p>`;
    }

    if (updatedEl) {
      updatedEl.textContent = "Could not update weather.";
    }
  }
}


/**
 * Initialises the Hourly / Daily toggle buttons.
 */
function initWeatherToggle() {
  const hourlyBtn = document.getElementById("weatherHourlyBtn");
  const dailyBtn = document.getElementById("weatherDailyBtn");

  if (!hourlyBtn || !dailyBtn) return;

  hourlyBtn.addEventListener("click", () => {
    weatherMode = "hourly";
    hourlyBtn.classList.add("active");
    dailyBtn.classList.remove("active");
    loadWeather();
  });

  dailyBtn.addEventListener("click", () => {
    weatherMode = "daily";
    dailyBtn.classList.add("active");
    hourlyBtn.classList.remove("active");
    loadWeather();
  });
}


/**
 * Refreshes the weather forecast whenever the journey timing controls change.
 *
 * This ensures the hourly forecast follows the selected Depart At time
 * rather than always showing the next few hours from now.
 */
function initDepartWeatherRefresh() {
  const departAtBtn = document.getElementById("departAt");
  const leaveNowBtn = document.getElementById("leaveNow");
  const departDaySelect = document.getElementById("departDay");
  const timeInput = document.getElementById("departTime");

  departAtBtn?.addEventListener("click", () => {
    if (weatherMode === "hourly") loadWeather();
  });

  leaveNowBtn?.addEventListener("click", () => {
    if (weatherMode === "hourly") loadWeather();
  });

  departDaySelect?.addEventListener("change", () => {
    if (weatherMode === "hourly") loadWeather();
  });

  timeInput?.addEventListener("change", () => {
    if (weatherMode === "hourly") loadWeather();
  });
}


/**
 * Initialise weather features once the page is ready.
 */
document.addEventListener("DOMContentLoaded", () => {
  updateWeatherStatus();
  initWeatherToggle();
  initDepartWeatherRefresh();
  loadWeather();

  // Refresh current summary every 10 minutes
  setInterval(updateWeatherStatus, 600000);

  // Refresh forecast every 30 minutes
  setInterval(loadWeather, 1800000);
});
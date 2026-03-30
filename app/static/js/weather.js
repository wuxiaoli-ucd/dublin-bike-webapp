async function updateWeatherStatus() {
  try {
    const response = await fetch("/api/weather/current");
    if (!response.ok) throw new Error(`Weather status request failed: ${response.status}`);

    const data = await response.json();

    const weatherEl = document.getElementById("weatherText");
    const tempEl = document.getElementById("tempText");

    if (weatherEl) {
      weatherEl.querySelector(".value").textContent = data.weather;
    }

    if (tempEl) {
      tempEl.querySelector(".value").textContent = `${Math.round(data.temp)}°C`;
    }
  } catch (err) {
    console.error("Status Bar Error:", err);

    document.getElementById("weatherText").textContent = "Weather: unavailable";
    document.getElementById("tempText").textContent = "Temperature: —";
  }
}

async function loadWeather() {
  try {
    const response = await fetch("/api/weather/forecast");
    if (!response.ok) throw new Error(`Forecast request failed: ${response.status}`);

    const data = await response.json();
    
    const container = document.getElementById("weatherForecast");
    const updatedEl = document.getElementById("weatherUpdated");

    if (!container) return;

    container.innerHTML = "";

    data.forEach((item, i) => {
      const timeLabel =
        i === 0
          ? "Now"
          : new Date(item.time * 1000).toLocaleTimeString([], {
              hour: "numeric",
              minute: "2-digit",
              hour12: true
            });

      const iconUrl = `https://openweathermap.org/img/wn/${item.icon}@2x.png`;

      const col = document.createElement("div");
      col.className = "column";

      col.innerHTML = `
        <span class="time-label">${timeLabel}</span>
        <img class="weather-icon" src="${iconUrl}" alt="weather">
        <span class="temp">${Math.round(item.temp)}°</span>
        <div class="stat">💧 ${Math.round(item.pop * 100)}%</div>
      `;

      container.appendChild(col);
    });

    if (updatedEl) {
      updatedEl.textContent = `Last updated: ${new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
      })}`;
    }
  } catch (err) {
    console.error("Forecast Widget Error:", err);

    document.getElementById("weatherForecast").innerHTML =
      `<p style="margin:0; color:#334155;">Weather forecast unavailable.</p>`;

    document.getElementById("weatherUpdated").textContent =
      "Could not update weather.";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  updateWeatherStatus();
  loadWeather();

  setInterval(updateWeatherStatus, 600000);
  setInterval(loadWeather, 1800000);
});
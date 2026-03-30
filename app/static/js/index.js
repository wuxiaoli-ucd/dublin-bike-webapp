let map;
let startPlace = null;
let destPlace = null;

let routeLines = [];
let routeMarkers = [];

let stationRefreshTimer = null;
const STATION_REFRESH_MS = 60000;

const $ = (id) => document.getElementById(id); // shortcut

// ---------- helpers ----------
function clearRoutes() {
  routeLines.forEach(l => l.setMap(null));
  routeLines = [];
  clearRouteMarkers();
}

function clearRouteMarkers() {
  routeMarkers.forEach(m => m.setMap(null));
  routeMarkers = [];
}

function setError(msg = "") {
  const el = $("error");
  if (el) el.textContent = msg;
}

function durToSec(d) {
  if (!d) return 0;
  const s = String(d).trim();
  if (!s.endsWith("s")) return 0;
  return Math.round(parseFloat(s.slice(0, -1)) || 0);
}

function secToMin(s) {
  return Math.round(s / 60);
}


async function refreshStations() {
  try {
    const stations = await getStations();
    addStations(stations);
  } catch (err) {
    console.error("Station refresh failed:", err);
  }
}

function refreshOpenStationPanel(stations) {
  if (!document.body.classList.contains("station-open")) return;
  if (!currentStation) return;

  const updated = stations.find(s => s.number === currentStation.number);
  if (!updated) return;

  setCurrentStation(updated);

  const nameEl = $("stationName");
  const bikesEl = $("stationBikes");
  const standsEl = $("stationStands");
  const capFill = $("stationCapacityFill");
  const capPct = $("stationCapacityPct");

  if (nameEl) nameEl.textContent = updated.name || "Station";
  if (bikesEl) bikesEl.textContent = updated.available_bikes ?? "—";
  if (standsEl) standsEl.textContent = updated.available_bike_stands ?? "—";

  const bikes = Number(updated.available_bikes ?? 0);
  const total = Number(updated.bike_stands ?? 0);
  const pct = total > 0 ? Math.round((bikes / total) * 100) : 0;

  if (capFill) capFill.style.width = `${pct}%`;
  if (capPct) capPct.textContent = `${pct}%`;
}


// ---------- top right menu button ----------
let totalKmCycled = 0;
const CO2_KG_PER_KM_CAR = 0.14;
let totalCo2Saved = 0;
let totalTrips = 0;

const menuBtn = $("btnMenu");
const dropdown = $("menuDropdown");

menuBtn.addEventListener("click", () => {
  dropdown.hidden = !dropdown.hidden;
});

function updateKmDisplay() {
  const el = $("kmValue");
  if (el) el.textContent = totalKmCycled.toFixed(1);
}

function updateCo2Display() {
  const el = $("co2Value");
  if (el) el.textContent = totalCo2Saved.toFixed(2);
}

function updateTripsDisplay() {
  const el = $("trips");
  if (el) el.textContent = totalTrips;
}


// ---------- left panel (route details) ----------
let showDirections = false;
let showWeather = false;

function updateLeftPanelVisibility() {
  const directionsBlock = $("directionsBlock");
  const weatherBlock = $("weatherBlock");
  const directionsBtn = $("toggleDirections");
  const weatherBtn = $("toggleWeather");

  if (directionsBlock) directionsBlock.hidden = !showDirections;
  if (weatherBlock) weatherBlock.hidden = !showWeather;

  if (directionsBtn) directionsBtn.classList.toggle("active", showDirections);
  if (weatherBtn) weatherBtn.classList.toggle("active", showWeather);

  const nothingSelected = !showDirections && !showWeather;
  document.body.classList.toggle("left-hidden", nothingSelected);
}

function initPanelToggles() {
  const directionsBtn = $("toggleDirections");
  const weatherBtn = $("toggleWeather");

  if (directionsBtn) {
    directionsBtn.addEventListener("click", () => {
      showDirections = !showDirections;

      if (!showDirections) {
        clearRoutes();

      const routeSection = $("routeSection");
      if (routeSection) routeSection.hidden = true;

      setError("");
    }
      updateLeftPanelVisibility();
    });
  }

  if (weatherBtn) {
    weatherBtn.addEventListener("click", () => {
      showWeather = !showWeather;
      updateLeftPanelVisibility();
    });
  }

  updateLeftPanelVisibility();
}

function getStepIcon(title) {
  const t = title.toLowerCase();

  if (t.includes("walk")) return "/static/images/walk.png";
  if (t.includes("cycle")) return "/static/images/red_bike_icon.png";
  if (t.includes("depart station")) return "/static/images/start_station.png";
  if (t.includes("arrival station")) return "/static/images/end_station.png";

  return "/static/images/default_step.png";
}

function showRouteDetails(lines, summaryText) {
  const summary = $("summary");
  const list = $("list");
  const section = $("routeSection"); 

  if (!summary || !list || !section) return;

  summary.textContent = summaryText;
  list.innerHTML = "";

  for (const [title, sub] of lines) {
    const div = document.createElement("div");
    div.className = "item";

    const iconSrc = getStepIcon(title);

    div.innerHTML = `
      <div class="route-row">
        <img class="route-icon" src="${iconSrc}" alt="">
        <div class="route-text">
          <div class="route-title">${title}</div>
          <div class="small">${sub}</div>
        </div>
      </div>
    `;

    list.appendChild(div);
  }

  section.hidden = false;
}

// ---------- right panel (station details) ----------
function openStationPanel(station) {
  //lily add
  setCurrentStation(station);

  const nameEl = $("stationName");
  const bikesEl = $("stationBikes");
  const standsEl = $("stationStands");
  const capFill = $("stationCapacityFill");
  const capPct = $("stationCapacityPct");

  if (nameEl) nameEl.textContent = station.name || "Station";
  if (bikesEl) bikesEl.textContent = station.available_bikes ?? "—";
  if (standsEl) standsEl.textContent = station.available_bike_stands ?? "—";

  const bikes = Number(station.available_bikes ?? 0);
  const total = Number(station.bike_stands ?? 0);
  const pct = total > 0 ? Math.round((bikes / total) * 100) : 0;

  if (capFill) capFill.style.width = `${pct}%`;
  if (capPct) capPct.textContent = `${pct}%`;

  // enable right column + show panel
  document.body.classList.add("station-open");

  loadHistoricalChart(station, getHistoricalMode());
}

function closeStationPanel() {
  // remove right column + hide panel
  document.body.classList.remove("station-open");
  if (window.clearSelectedStation) clearSelectedStation();
}

// ---------- stations ----------
async function getStations() {
  const r = await fetch("/api/stations");
  if (!r.ok) throw new Error("Failed to load stations");
  const data = await r.json();
  return data.stations || [];
}

function addStations(stations) {
  renderStations(map, stations, (station) => {
    openStationPanel(station);
  });
}

// ---------- polyline drawing ----------
function decodePolyline(encoded) {
  let i = 0, lat = 0, lng = 0;
  const path = [];

  while (i < encoded.length) {
    let b, shift = 0, result = 0;
    do { b = encoded.charCodeAt(i++) - 63; result |= (b & 0x1f) << shift; shift += 5; }
    while (b >= 0x20);
    lat += (result & 1) ? ~(result >> 1) : (result >> 1);

    shift = 0; result = 0;
    do { b = encoded.charCodeAt(i++) - 63; result |= (b & 0x1f) << shift; shift += 5; }
    while (b >= 0x20);
    lng += (result & 1) ? ~(result >> 1) : (result >> 1);

    path.push({ lat: lat / 1e5, lng: lng / 1e5 });
  }
  return path;
}

function drawLine(encoded, kind) {
  const path = decodePolyline(encoded);

  let line;

  if (kind === "WALK") {
    line = new google.maps.Polyline({
      map,
      path,
      strokeOpacity: 0,
      icons: [{
        icon: {
          path: "M 0,-1 0,1",
          strokeOpacity: 1,
          strokeColor: "#2563eb",
          scale: 3
        },
        offset: "0",
        repeat: "10px"
      }]
    });
  } else if (kind === "BIKE") {
    line = new google.maps.Polyline({
      map,
      path,
      strokeColor: "#dc2626",
      strokeOpacity: 1,
      strokeWeight: 5
    });
  } else {
    line = new google.maps.Polyline({
      map,
      path,
      strokeOpacity: 1,
      strokeWeight: 5
    });
  }

  routeLines.push(line);
  return path;
}

function addRouteDot(position, kind = "start") {
  const marker = new google.maps.Marker({
    map,
    position,
    zIndex: 1000,
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      fillColor: kind === "start" ? "#2563eb" : "#dc2626",
      fillOpacity: 1,
      strokeColor: "#ffffff",
      strokeWeight: 3,
      scale: 8
    }
  });

  routeMarkers.push(marker);
  return marker;
}

// ---------- routing ----------
async function fetchRoute(start, destination) {
  const r = await fetch("/api/route", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start, destination })
  });

  const data = await r.json().catch(() => null);
  if (!r.ok || !data) throw new Error(data?.error || `Route request failed (${r.status})`);
  return data;
}

async function onGo() {
  setError("");
  clearRoutes();
  closeStationPanel()
  // Hide previous route section if present
  const routeSection = $("routeSection");
  if (routeSection) routeSection.hidden = true;

  if (!startPlace?.geometry || !destPlace?.geometry) {
    setError("Pick start and destination from the dropdown suggestions.");
    return;
  }

  const s = startPlace.geometry.location;
  const d = destPlace.geometry.location;
  const start = { lat: s.lat(), lng: s.lng() };
  const destination = { lat: d.lat(), lng: d.lng() };

  try {
    const data = await fetchRoute(start, destination);

    const bounds = new google.maps.LatLngBounds();

    if (data.mode === "WALK_ONLY") {
      const path = drawLine(data.route.polyline, "WALK");
      path.forEach(p => bounds.extend(p));

      addRouteDot(start, "start");
      addRouteDot(destination, "end");

      const secs = durToSec(data.route.duration);
      showRouteDetails(
        [["Walk to destination", `${secToMin(secs)} min`]],
        `${secToMin(secs)} min`
      );
      
    } else {
      const p1 = drawLine(data.legs.walkToStation.polyline, "WALK");
      const p2 = drawLine(data.legs.cycleBetweenStations.polyline, "BIKE");
      const p3 = drawLine(data.legs.walkToDestination.polyline, "WALK");
      [...p1, ...p2, ...p3].forEach(p => bounds.extend(p));

      addRouteDot(start, "start");
      addRouteDot(destination, "end");

      const s1 = durToSec(data.legs.walkToStation.duration);
      const s2 = durToSec(data.legs.cycleBetweenStations.duration);
      const s3 = durToSec(data.legs.walkToDestination.duration);
      
      
      console.log("route response", data);
      console.log("bike meters", data.legs?.cycleBetweenStations?.distanceMeters);
      
      
      showRouteDetails(
        [
          ["Walk to station", `${secToMin(s1)} min`],
          [`Depart station bikes: ${data.stationA.available_bikes ?? 0}`, data.stationA.name],
          ["Cycle", `${secToMin(s2)} min`],
          [`Arrival station stands: ${data.stationB.available_bike_stands ?? 0}`, data.stationB.name],
          ["Walk to destination", `${secToMin(s3)} min`]
        ],
        `${secToMin(data.totals?.durationSeconds ?? 0)} min`
      );
      
      if (data.mode === "BIKESHARE") {
        const cycleKm = (data.legs.cycleBetweenStations.distanceMeters ?? 0) / 1000;
        totalKmCycled += cycleKm;
        updateKmDisplay();

        totalTrips += 1;
        updateTripsDisplay();

        const totalMeters =
          (data.legs.walkToStation.distanceMeters ?? 0) +
          (data.legs.cycleBetweenStations.distanceMeters ?? 0) +
          (data.legs.walkToDestination.distanceMeters ?? 0);

        const totalKmJourney = totalMeters / 1000;
        totalCo2Saved += totalKmJourney * CO2_KG_PER_KM_CAR;
        updateCo2Display();
      }

    }

    map.fitBounds(bounds);
  } catch (err) {
    setError(err.message || String(err));
  }
}

// ---------- init ----------
function initAutocomplete() {
  const startEl = $("start");
  const destEl = $("dest");
  const goBtn = $("go");

  if (!startEl || !destEl || !goBtn) {
    console.error("Missing required DOM elements (#start, #dest, #go).");
    return;
  }
  
  // only suggest Dublin locations
  const dublinBounds = {
  north: 53.41,
  south: 53.30,
  west: -6.40,
  east: -6.10
  };

  const opts = {
  fields: ["geometry", "name", "formatted_address"],
  componentRestrictions: { country: "ie" },
  bounds: dublinBounds,
  strictBounds: false
  };

  const a = new google.maps.places.Autocomplete(startEl, opts);
  const b = new google.maps.places.Autocomplete(destEl, opts);

  a.addListener("place_changed", () => (startPlace = a.getPlace()));
  b.addListener("place_changed", () => (destPlace = b.getPlace()));

  goBtn.addEventListener("click", onGo);

  document.querySelectorAll(".clearInput").forEach(btn => {
  const targetId = btn.dataset.target;
  const input = document.getElementById(targetId);

  if (!input) return;

  // show/hide X depending on content
  input.addEventListener("input", () => {
    btn.style.display = input.value ? "block" : "none";
  });

  // clear on click
  btn.addEventListener("click", () => {
    input.value = "";
    btn.style.display = "none";

    if (targetId === "start") startPlace = null;
    if (targetId === "dest") destPlace = null;
    });
  });

  // Right panel close button (if present)
  const closeBtn = $("closeStationPanel");
  if (closeBtn) closeBtn.addEventListener("click", closeStationPanel);
}

function initMap() {
  map = new google.maps.Map($("map"), {
    center: { lat: 53.35, lng: -6.266 },
    zoom: 14,

    mapTypeControl: true,
    fullscreenControl: false,
    mapTypeControlOptions: {
    position: google.maps.ControlPosition.BOTTOM_LEFT, 
  }
});

  initAutocomplete();
  initPanelToggles();
  initHistoricalToggle();
  initStationMarkers(map);

  updateLeftPanelVisibility();

  getStations()
    .then(addStations)
    .catch(err => console.error("Stations load failed:", err));

  if (!stationRefreshTimer) {
    stationRefreshTimer = setInterval(refreshStations, STATION_REFRESH_MS);
  }
}

window.initMap = initMap;



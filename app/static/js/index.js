let map;
let startPlace = null;
let destPlace = null;

let stationMarkers = [];
let routeLines = [];

const $ = (id) => document.getElementById(id);

function clearMarkers() {
  stationMarkers.forEach(m => m.setMap(null));
  stationMarkers = [];
}

function clearRoutes() {
  routeLines.forEach(l => l.setMap(null));
  routeLines = [];
}

function setError(msg = "") {
  $("error").textContent = msg;
}

function showDetails(lines, summaryText) {
  $("summary").textContent = summaryText;
  const list = $("list");
  list.innerHTML = "";
  lines.forEach(([title, sub]) => {
    const div = document.createElement("div");
    div.className = "item";
    div.innerHTML = `<div><b>${title}</b></div><div class="small">${sub}</div>`;
    list.appendChild(div);
  });
  $("details").hidden = false;
}

async function getStations() {
  const r = await fetch("/api/stations");
  if (!r.ok) throw new Error("Failed to load stations");
  const data = await r.json();
  return data.stations || [];
}

function addStations(stations) {
  clearMarkers();
  const info = new google.maps.InfoWindow();

  stations.forEach(s => {
    const pos = { lat: s.position.lat, lng: s.position.lng };
    const marker = new google.maps.Marker({ map, position: pos, title: s.name });

    marker.addListener("click", () => {
      info.setContent(
        `<div style="font-family:system-ui">
          <b>${s.name}</b><br>
          Bikes: ${s.available_bikes ?? 0} / ${s.bike_stands ?? 0}<br>
          Stands: ${s.available_bike_stands ?? 0}<br>
          Status: ${s.status ?? "?"}
        </div>`
      );
      info.open({ map, anchor: marker });
    });

    stationMarkers.push(marker);
  });
}

// Google encoded polyline decoder
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

  const line =
    kind === "WALK"
      ? new google.maps.Polyline({
          map,
          path,
          strokeOpacity: 0,
          icons: [{
            icon: { path: "M 0,-1 0,1", strokeOpacity: 1, scale: 3 },
            offset: "0",
            repeat: "12px"
          }]
        })
      : new google.maps.Polyline({
          map,
          path,
          strokeWeight: 5
        });

  routeLines.push(line);
  return path;
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
  $("details").hidden = true;

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

      const secs = durToSec(data.route.duration);
      showDetails(
        [["Walk to destination", `${secToMin(secs)} min`]],
        `${secToMin(secs)} min`
      );
    } else {
      const p1 = drawLine(data.legs.walkToStation.polyline, "WALK");
      const p2 = drawLine(data.legs.cycleBetweenStations.polyline, "BIKE");
      const p3 = drawLine(data.legs.walkToDestination.polyline, "WALK");
      [...p1, ...p2, ...p3].forEach(p => bounds.extend(p));

      const s1 = durToSec(data.legs.walkToStation.duration);
      const s2 = durToSec(data.legs.cycleBetweenStations.duration);
      const s3 = durToSec(data.legs.walkToDestination.duration);

      showDetails(
        [
          ["Walk to station", `${secToMin(s1)} min`],
          [`Depart station bikes: ${data.stationA.available_bikes ?? 0}`, data.stationA.name],
          ["Cycle", `${secToMin(s2)} min`],
          [`Arrival station stands: ${data.stationB.available_bike_stands ?? 0}`, data.stationB.name],
          ["Walk to destination", `${secToMin(s3)} min`]
        ],
        `${secToMin(data.totals?.durationSeconds ?? 0)} min`
      );
    }

    map.fitBounds(bounds);
  } catch (err) {
    setError(err.message || String(err));
  }
}

function initAutocomplete() {
  const opts = { fields: ["geometry", "name", "formatted_address"] };
  const a = new google.maps.places.Autocomplete($("start"), opts);
  const b = new google.maps.places.Autocomplete($("dest"), opts);

  a.addListener("place_changed", () => (startPlace = a.getPlace()));
  b.addListener("place_changed", () => (destPlace = b.getPlace()));

  $("go").addEventListener("click", onGo);
}

function initMap() {
  map = new google.maps.Map($("map"), { center: { lat: 53.35, lng: -6.266 }, zoom: 12 });

  initAutocomplete();

  getStations()
    .then(addStations)
    .catch(err => console.error(err));
}

window.initMap = initMap;
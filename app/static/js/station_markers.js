let markersById = new Map(); // stores key value pairs of current markers by station ID
let tooltipEl = null;
let mapRef = null;
let selectedStationId = null;

function initStationMarkers(mapInstance) {
  /*
   * Stores shared map/tooltip references used by marker functions.
   */
  mapRef = mapInstance;
  tooltipEl = document.getElementById("stationTooltip");
}

// helper functions
function setSelectedStation(stationId) {
  selectedStationId = stationId;
  refreshMarkerStyles();
}

function clearSelectedStation() {
  selectedStationId = null;
  refreshMarkerStyles();
}

function refreshMarkerStyles() {
  for (const [stationId, markerObj] of markersById.entries()) {
    markerObj.marker.setIcon(buildMarkerIcon(markerObj.station, stationId === selectedStationId));
  }
}


// synchronise UI markers with backend
function renderStations(mapInstance, stations, onStationClick) {
  const seen = new Set(); // collection of unique values i.e., which stations are present in most recent api call

  stations.forEach((station) => {
    const stationId = station.number;
    seen.add(stationId);

    // better for performance to update marker rather destroy and create
    if (markersById.has(stationId)) {
      updateMarker(markersById.get(stationId), station);
    } else {
      const markerObj = createMarker(mapInstance, station, onStationClick);
      markersById.set(stationId, markerObj);
    }
  });

  // gets rid of old markers if not currently relevant, basically real time
  for (const [stationId, markerObj] of markersById.entries()) {
    if (!seen.has(stationId)) {
      markerObj.marker.setMap(null);
      markersById.delete(stationId);
    }
  }
}

function createMarker(mapInstance, station, onStationClick) {
  /*
   * Creates a Google Maps marker for a station.
   * The label shows current available bikes.
   */
  const marker = new google.maps.Marker({
    map: mapInstance,
    position: {
      lat: station.position.lat,
      lng: station.position.lng
    },
    title: station.name,
    label: {
      text: String(station.available_bikes ?? 0),
      color: "white",
      fontWeight: "700",
      fontSize: "12px"
    },
    icon: buildMarkerIcon(station)
  });

 marker.addListener("mouseover", (event) => {
  const currentStation = markersById.get(station.number)?.station || station;
  showStationTooltip(currentStation, event);
 });

  marker.addListener("mouseout", () => {
    hideStationTooltip();
  });

  marker.addListener("click", () => {
    const currentStation = markersById.get(station.number)?.station || station;
    hideStationTooltip();
    setSelectedStation(currentStation.number);
    onStationClick(currentStation);
  });

  return { marker, station };
}

function updateMarker(markerObj, station) {
  /*
   * Updates an existing marker with fresh station availability/location data.
   */
  markerObj.station = station;

  markerObj.marker.setPosition({
    lat: station.position.lat,
    lng: station.position.lng
  });

  markerObj.marker.setTitle(station.name);

  markerObj.marker.setLabel({
    text: String(station.available_bikes ?? 0),
    color: "white",
    fontWeight: "700",
    fontSize: "12px"
  });

  markerObj.marker.setIcon(buildMarkerIcon(station, station.number === selectedStationId));
}

function buildMarkerIcon(station, isSelected = false) {
  /*
   * Builds the circular marker icon.
   * Selected markers are larger with a darker border for visibility.
   */
  return {
    path: google.maps.SymbolPath.CIRCLE,
    fillColor: getMarkerColor(station),
    fillOpacity: 1,
    strokeColor: isSelected ? "#111111" : "#ffffff",
    strokeWeight: isSelected ? 4 : 2,
    scale: isSelected ? 20 : 16
  };
}

function getMarkerColor(station) {
  /*
   * Colours markers based on current bike availability.
   * Grey means empty; warmer colours mean low supply; green means healthy supply.
   */
  const bikes = Number(station.available_bikes ?? 0);

  if (bikes === 0) return "#808080";
  if (bikes <= 3) return "#dc2626";
  if (bikes <= 8) return "#f59e0b";
  return "#16a34a";
}

function showStationTooltip(station, event) {
  /*
   * Displays the hover tooltip with station availability information.
   */
  if (!tooltipEl) return;

  tooltipEl.innerHTML = buildTooltipContent(station);
  tooltipEl.hidden = false;

  positionTooltipAbove(event);
}

function hideStationTooltip() {
  if (!tooltipEl) return;
  tooltipEl.hidden = true;
}

function buildTooltipContent(station) {
  /*
   * Builds tooltip HTML. Station names are escaped to avoid injecting
   * untrusted text into the page.
   */
  const bikes = station.available_bikes ?? 0;
  const stands = station.available_bike_stands ?? 0;
  const capacity = station.bike_stands ?? 0;

  return `
    <div class="tooltipTitle">${escapeHtml(station.name || "Station")}</div>
    <div class="tooltipRow">Bikes: ${bikes} / ${capacity}</div>
    <div class="tooltipRow">Stands: ${stands}</div>
  `;
}

// centres tooltip above marker on hover
function positionTooltipAbove(event) {
  if (!tooltipEl || !event || !event.domEvent) return;

  const padding = 12;
  const markerOffsetY = 18;

    // mouse postion on screen
  const mouseX = event.domEvent.clientX; 
  const mouseY = event.domEvent.clientY;

    // measuring tooltip size
  const rect = tooltipEl.getBoundingClientRect();

  let left = mouseX - rect.width / 2;
  let top = mouseY - rect.height - markerOffsetY;

  if (left < padding) {
    left = padding;
  }

  if (left + rect.width > window.innerWidth - padding) {
    left = window.innerWidth - rect.width - padding;
  }

  if (top < padding) {
    top = mouseY + markerOffsetY;
  }

  tooltipEl.style.left = `${left}px`;
  tooltipEl.style.top = `${top}px`;
}

// prevents html injection!
function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function clearAllStationMarkers() {
  for (const { marker } of markersById.values()) {
    marker.setMap(null);
  }
  markersById.clear();
  hideStationTooltip();
}

// global functions
window.initStationMarkers = initStationMarkers;
window.renderStations = renderStations;
window.clearAllStationMarkers = clearAllStationMarkers;
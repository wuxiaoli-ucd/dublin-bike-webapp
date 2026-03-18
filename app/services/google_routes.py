import requests
import os

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
DEFAULT_TIMEOUT_SECONDS = 10


def compute_route(origin: dict, destination: dict, travel_mode: str, *, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> dict | None:
    """
    Calls Google Routes API (Directions v2) to compute a route between two lat/lng points.

    Returns:
      dict: {"distanceMeters": int, "duration": str, "polyline": str}
      None: if Google returns no routes or a network/HTTP error occurs
    """
    api_key = os.getenv("ROUTES_API_KEY")
    if not api_key:
        raise ValueError("ROUTES_API_KEY not set")

    payload = {
        "origin": {"location": {"latLng": {"latitude": origin["lat"], "longitude": origin["lng"]}}},
        "destination": {"location": {"latLng": {"latitude": destination["lat"], "longitude": destination["lng"]}}},
        "travelMode": travel_mode,
        "polylineQuality": "OVERVIEW",
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline" # return only these fields
    }

    try:
        response = requests.post(ROUTES_URL, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        # RequestException covers timeouts, connection errors, non-2xx via raise_for_status, etc.
        # ValueError can occur if resp.json() fails.
        return None

    routes = data.get("routes") or []
    if not routes:
        return None

    route = routes[0]
    polyline = (route.get("polyline") or {}).get("encodedPolyline")

    # guard against incomplete payloads even with field mask
    if polyline is None or "distanceMeters" not in route or "duration" not in route:
        return None

    return {
        "distanceMeters": route["distanceMeters"],
        "duration": route["duration"],
        "polyline": polyline,
    }
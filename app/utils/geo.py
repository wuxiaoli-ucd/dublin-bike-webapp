import math

def _latlng(x: dict):
    """Normalises lat and lng input"""
    if "position" in x:
        return x["position"]["lat"], x["position"]["lng"]
    return x["lat"], x["lng"]

# this avoids multiple api calls i.e., selects nearest station to a point, then we get the route
def haversine(a: dict , b: dict) -> float: 
    """
    Computes distance between two lat/lon points on a sphere
    Take dictionaries as parameters
    Return distance
    """
    R = 6371000 # radius of the Earth
    a_lat, a_lng = _latlng(a)
    b_lat, b_lng = _latlng(b)
    
    lat1, lon1 = math.radians(a_lat), math.radians(a_lng)
    lat2, lon2 = math.radians(b_lat), math.radians(b_lng)
    dlat = lat2 - lat1 # difference in lat
    dlon = lon2 - lon1 # difference in lng

    h = math.sin(dlat/2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2) ** 2 
    
    return 2 * R * math.asin(math.sqrt(h))

def k_nearest_stations(point, stations, k=10):
    """
    Takes a coordinate as input
    Returns k candidate stations
    """
    return sorted(stations, key=lambda s: haversine(point, s))[:k]

import requests

def reverse_geocode(lat, lon):
    """Convert GPS coordinates to a human-readable address"""
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "json",
                "zoom": 18
            },
            headers={
                "User-Agent": "Pixprobe/1.0"
            }
        )

        if response.status_code != 200:
            print(f"[ERROR] Geocoding failed: {response.status_code}")
            return None

        data = response.json()
        address = data.get("display_name", "Unknown location")
        print(f"Address: {address}")
        return address

    except Exception as e:
        print(f"[ERROR] Geocoding failed: {e}")
        return None
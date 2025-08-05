import requests
import os
print("[SCREENSHOT] Screenshot module loaded")

def get_streetview_image(lat, lon, filename="current.png"):
    print(f"[SCREENSHOT] Getting Street View image for ({lat}, {lon})")
    api_key = os.getenv("GOOGLE_MAPS_KEY")
    if not api_key:
        print(f"[SCREENSHOT] ❌ GOOGLE_MAPS_KEY not found in environment")
        raise Exception("GOOGLE_MAPS_KEY not found in environment")
    
    url = f"https://maps.googleapis.com/maps/api/streetview?size=800x600&location={lat},{lon}&key={api_key}"
    print(f"[SCREENSHOT] Request URL: {url[:80]}...")
    
    try:
        print(f"[SCREENSHOT] Making HTTP request...")
        img = requests.get(url, timeout=10)
        img.raise_for_status()
        print(f"[SCREENSHOT] HTTP response: {img.status_code}, content length: {len(img.content)}")
        
        if len(img.content) < 1000:
            print(f"[SCREENSHOT] ❌ Image too small ({len(img.content)} bytes), likely an error")
            raise Exception("Image too small, likely an error response")
            
        print(f"[SCREENSHOT] Writing image to {filename}...")
        with open(filename, 'wb') as f:
            f.write(img.content)
        print(f"[SCREENSHOT] ✅ Image saved successfully ({len(img.content)} bytes)")
            
    except requests.exceptions.RequestException as e:
        print(f"[SCREENSHOT] ❌ Request failed: {e}")
        raise Exception(f"Failed to download street view image: {e}")

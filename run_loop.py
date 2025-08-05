from dotenv import load_dotenv
load_dotenv()
print("[RUN_LOOP] Starting up...")
import time
import queue_manager
from screenshot import get_streetview_image
from gpt_guess import ask_gpt, extract_coords
from scorer import compute_score
from geopy.geocoders import Nominatim
import json
from status_tracker import update_status, update_thinking_status, update_progress_status
print("[RUN_LOOP] All imports loaded successfully")

# Initialize status
update_status("idle", "Claude GeoGuessr Agent initialized - ready for geographic analysis", 0)

def geocode(place):
    print(f"[GEOCODE] Starting geocoding for: {place}")
    try:
        geolocator = Nominatim(user_agent="geo-claude")
        print(f"[GEOCODE] Nominatim client created, making request...")
        loc = geolocator.geocode(place)
        if loc:
            print(f"[GEOCODE] SUCCESS: {place} → ({loc.latitude}, {loc.longitude})")
            return loc.latitude, loc.longitude
        else:
            print(f"[GEOCODE] FAILED: Could not geocode: {place}")
            return None, None
    except Exception as e:
        print(f"[GEOCODE] ERROR geocoding {place}: {e}")
        return None, None

print("[RUN_LOOP] Entering main processing loop...")
while True:
    print("[RUN_LOOP] Checking for new tasks...")
    task = queue_manager.get_next()
    if task:
        print(f"[RUN_LOOP] ✅ FOUND TASK: {task}")
        place = task['place']
        user = task['user']
        
        print(f"[RUN_LOOP] Processing request from {user} for {place}")
        # Reset idle flag since we're now processing
        if hasattr(geocode, 'idle_set'):
            delattr(geocode, 'idle_set')
        update_status("processing", f"Processing location request: {place} (from {user})", 0, {"current_location": place, "user": user})
        update_progress_status(1, 6, f"Geocoding target location: {place}")
        lat, lon = geocode(place)
        if lat is None or lon is None:
            print(f"[RUN_LOOP] ❌ GEOCODING FAILED - Skipping {place}")
            update_status("error", f"Unable to geocode location: {place}", 0)
            queue_manager.complete_task({"user": user, "place": place, "error": "Could not geocode location"})
            continue
            
        update_progress_status(2, 6, "Acquiring Street View imagery")
        print(f"[RUN_LOOP] Getting Street View image for {lat}, {lon}...")
        try:
            get_streetview_image(lat, lon)
            print(f"[RUN_LOOP] ✅ Street View image downloaded successfully")
            update_status("processing", "Street View image successfully acquired", 33, {"showing_image": True})
            time.sleep(1)  # Brief pause to show the image
        except Exception as e:
            print(f"[RUN_LOOP] ❌ ERROR getting street view for {place}: {e}")
            update_status("error", "Failed to acquire Street View imagery", 0)
            queue_manager.complete_task({"user": user, "place": place, "error": "Street view image failed"})
            continue
            
        update_thinking_status("Claude analyzing visual elements and geographic indicators")
        print(f"[RUN_LOOP] Asking GPT to analyze the Street View image...")
        description = ask_gpt("current.png", """You are Claude, an AI playing GeoGuessr. Analyze this Street View image as if you're thinking out loud. Format your response as your internal monologue - natural, conversational thoughts as you examine the image.

Start with: "Looking at this image, I can see..."

Examine these clues systematically but naturally:
- License plates, road markings, driving side
- Street signs, language, text visible
- Architecture, building styles, materials  
- Vegetation, climate indicators
- Infrastructure, utility poles, barriers
- Cultural elements, people, vehicles

Think step by step, noting what catches your attention. Be detailed but conversational, like you're explaining your thought process. Format with clear paragraphs and natural language.

Do NOT state the location name - only describe what you observe.""")
        print(f"[RUN_LOOP] GPT analysis result: {description is not None}")
        if description:
            update_status("processing", "Visual analysis", 50, {"analysis": description, "analysis_type": "first", "showing_image": True})
        
        print(f"[RUN_LOOP] Asking GPT to make final coordinate guess...")
        guess = ask_gpt("current.png", """Continue your GeoGuessr analysis. Now synthesize your observations to make a coordinate prediction. 

Format as your continued thinking:

"Based on what I'm seeing, I need to narrow down the location. [Continue analyzing the strongest clues]

The architecture suggests [region]... The [specific clue] indicates [country/area]... 

Considering all the evidence, my best estimate for coordinates would be:
Latitude: [number]
Longitude: [number]

This appears to be in [general area] based on [key reasoning]."

Be conversational and show your reasoning process naturally. Always provide specific decimal coordinates.""")
        
        if not description or not guess:
            print(f"[RUN_LOOP] ❌ AI analysis failed for {place}")
            queue_manager.complete_task({"user": user, "place": place, "error": "AI analysis failed"})
            continue
        
        # Send the second analysis text for typing out
        update_status("processing", "Coordinate analysis", 75, {"analysis": guess, "analysis_type": "second", "showing_image": True})
        
        # Extract coordinates but don't send them yet - the dashboard will handle this
        print(f"[RUN_LOOP] Extracting coordinates from GPT response...")
        lat_guess, lon_guess = extract_coords(guess)
        if lat_guess is None or lon_guess is None:
            print(f"[RUN_LOOP] ❌ Could not extract coordinates from AI guess for {place}")
            print(f"[RUN_LOOP] GPT guess text was: {guess}")
            update_status("error", "Unable to parse coordinate prediction", 0)
            queue_manager.complete_task({"user": user, "place": place, "error": "Could not parse AI coordinates"})
            continue
        print(f"[RUN_LOOP] ✅ Extracted coordinates: ({lat_guess}, {lon_guess})")
        
        # Get location name for predicted coordinates
        print(f"[RUN_LOOP] Getting location name for predicted coordinates...")
        pred_place = "Unknown Location"
        try:
            geolocator = Nominatim(user_agent="geo-claude")
            location = geolocator.reverse(f"{lat_guess}, {lon_guess}", language='en')
            if location:
                # Extract just city/town/country for cleaner display
                address = location.raw.get('address', {})
                parts = []
                for key in ['city', 'town', 'village', 'municipality', 'county', 'state', 'country']:
                    if key in address and address[key]:
                        parts.append(address[key])
                        if len(parts) >= 2:  # Limit to 2 main parts for clean display
                            break
                pred_place = ", ".join(parts) if parts else location.address.split(',')[0]
                print(f"[RUN_LOOP] Predicted location name: {pred_place}")
        except Exception as e:
            print(f"[RUN_LOOP] Could not get location name for prediction: {e}")
        
        # Store coordinates and result data for later use after typing is complete
        import json
        with open("pending_coordinates.json", "w") as f:
            json.dump({
                "lat": lat_guess, 
                "lng": lon_guess, 
                "ready": False,
                "place": place,
                "pred_place": pred_place,
                "user": user,
                "true_lat": lat,
                "true_lng": lon
            }, f)
            
        update_progress_status(6, 6, "Computing accuracy metrics")
        print(f"[RUN_LOOP] Computing score...")
        dist, score = compute_score((lat, lon), (lat_guess, lon_guess))
        print(f"[RUN_LOOP] Score computed: {score}/5000 ({dist:.1f} km off)")
        
        result = {
            "user": user,
            "place": place,
            "true_coords": [lat, lon],
            "guess_coords": [lat_guess, lon_guess],
            "distance_km": dist,
            "score": score,
            "description": description,
            "guess": guess
        }
        print(f"[RUN_LOOP] Completing task and saving result...")
        queue_manager.complete_task(result)
        print(f"[RUN_LOOP] ✅ Task completed successfully!")
        
        # Update the pending coordinates with final results
        with open("pending_coordinates.json", "w") as f:
            json.dump({
                "lat": lat_guess, 
                "lng": lon_guess, 
                "ready": True,
                "place": place,
                "pred_place": pred_place,
                "user": user,
                "true_lat": lat,
                "true_lng": lon,
                "score": score,
                "distance": dist
            }, f)
        
        update_status("completed", f"Analysis complete: {place} - {score}/5000 points ({dist:.1f}km deviation)", 100, {
            "final_score": score,
            "distance": dist,
            "location": place,
            "user": user
        })
        print(f"[RUN_LOOP] Task completed and marked as done in queue")

        print(f"[RUN_LOOP] Updating results.json...")
        total, best, worst, last = queue_manager.get_stats()
        with open("results.json", "w") as f:
            json.dump({
                "agent_status": "Analysis complete: " + place,
                "current_task": place,
                "total_score": total,
                "best_score": best,
                "worst_score": worst,
                "last_score": last,
                "history": queue_manager.get_results()
            }, f, indent=2)
        print(f"[RUN_LOOP] results.json updated")
    else:
        # Only update status once when becoming idle, not every loop
        if not hasattr(geocode, 'idle_set'):
            print("[RUN_LOOP] No tasks in queue, entering idle state")
            update_status("idle", "Ready for geographic analysis", 0)
            geocode.idle_set = True
    time.sleep(2)

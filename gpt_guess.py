from openai import OpenAI
import base64
import os
import re

api_key = os.getenv("OPENAI_API_KEY")
print(f"[GPT] OpenAI API key exists: {api_key is not None}")
client = OpenAI(api_key=api_key)
print(f"[GPT] OpenAI client initialized")

def ask_gpt(image_path, prompt):
    print(f"[GPT] ask_gpt called with image: {image_path}")
    print(f"[GPT] Prompt: {prompt[:50]}...")
    try:
        print(f"[GPT] Reading image file...")
        with open(image_path, "rb") as f:
            img_data = f.read()
            print(f"[GPT] Image size: {len(img_data)} bytes")
            img_base64 = base64.b64encode(img_data).decode()

        print(f"[GPT] Calling OpenAI API with gpt-4o...")
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user", 
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]
            }],
            max_tokens=1000
        )
        response = res.choices[0].message.content
        print(f"[GPT] ✅ API call successful, response length: {len(response) if response else 0}")
        return response
    except Exception as e:
        print(f"[GPT] ❌ ERROR in ask_gpt: {e}")
        return None

def extract_coords(text):
    print(f"[EXTRACT] Extracting coordinates from text: {text[:200] if text else 'None'}...")
    if not text:
        print(f"[EXTRACT] ❌ No text provided")
        return None, None
    
    # Look for coordinates after "FINAL GUESS:" or just "Latitude:/Longitude:"
    lat_patterns = [
        r'FINAL GUESS:.*?Latitude[:\s]+([\-\d\.]+)',
        r'Latitude[:\s]+([\-\d\.]+)'
    ]
    lon_patterns = [
        r'FINAL GUESS:.*?Longitude[:\s]+([\-\d\.]+)',  
        r'Longitude[:\s]+([\-\d\.]+)'
    ]
    
    lat_match = None
    lon_match = None
    
    for pattern in lat_patterns:
        lat_match = re.search(pattern, text, re.DOTALL)
        if lat_match:
            break
            
    for pattern in lon_patterns:
        lon_match = re.search(pattern, text, re.DOTALL)
        if lon_match:
            break
    
    print(f"[EXTRACT] Latitude match: {lat_match.group(1) if lat_match else 'None'}")
    print(f"[EXTRACT] Longitude match: {lon_match.group(1) if lon_match else 'None'}")
    
    if not lat_match or not lon_match:
        print(f"[EXTRACT] ❌ Could not find latitude/longitude pattern")
        return None, None
    
    try:
        lat_val = float(lat_match.group(1))
        lon_val = float(lon_match.group(1))
        print(f"[EXTRACT] ✅ Extracted: ({lat_val}, {lon_val})")
        return lat_val, lon_val
    except (ValueError, IndexError) as e:
        print(f"[EXTRACT] ❌ Error parsing coordinates: {e}")
        return None, None

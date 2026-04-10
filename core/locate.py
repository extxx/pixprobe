import ollama
import base64
import os

VISION_MODEL = os.getenv("VISION_MODEL", "moondream")
REASONING_MODEL = os.getenv("REASONING_MODEL", "llava:7b")

def detect_landmark(image_path):
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        raise FileNotFoundError("[ERROR] File name is not valid.")

    # pass 1: what do you see
    print(f"Analyzing image with {VISION_MODEL}...")
    pass1 = ollama.chat(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": "List every object, building, sign, text, and landmark visible in this image. Be specific about architectural style, colors, and materials.",
            "images": [image_data]
        }]
    )
    scene = pass1["message"]["content"]

    # pass 2: location clues
    pass2 = ollama.chat(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": "Look at this image as a detective trying to figure out the country and city. What language is on signs? What side do cars drive on? What do the license plates look like? What style is the architecture? What plants or trees are visible? Describe the roads and infrastructure.",
            "images": [image_data]
        }]
    )
    clues = pass2["message"]["content"]

    description = f"SCENE: {scene}\n\nLOCATION CLUES: {clues}"
    print(f"\n{description}\n")

    # reasoning model estimates location
    print(f"Estimating location with {REASONING_MODEL}...")
    reasoning_response = ollama.chat(
        model=REASONING_MODEL,
        messages=[{
            "role": "system",
            "content": """You are a world-class geolocation expert. Given image analysis data, determine where the photo was taken.

Process: narrow from continent → region → country → city using all available clues. Cross-reference clues against each other.

Respond in EXACTLY this format:
Location: [city, country]
Confidence: [0-100]%
Reasoning: [3-4 sentences explaining your deduction]
Clues used: [comma-separated list of decisive clues]
Alternative guesses: [1-2 other locations if confidence is below 80%]"""
        },
        {
            "role": "user",
            "content": f"Where was this photo taken?\n\n{description}"
        }]
    )

    result = reasoning_response["message"]["content"]
    print(result)

    return result

def cross_reference(gps=None, geo_result=None, reverse_data=None, vision_result=None):
    """Take all data sources and make a final location determination"""

    REASONING_MODEL = os.getenv("REASONING_MODEL", "llama3.1:8b")

    # build context from all sources
    context = ""

    if gps:
        context += f"GPS COORDINATES: {gps['lat']}, {gps['lon']}\n"
    if geo_result:
        context += f"REVERSE GEOCODE: {geo_result}\n"
    if reverse_data:
        # extract top results from reverse search
        matches = reverse_data.get("visual_matches", [])[:5]
        if matches:
            titles = [m.get("title", "") for m in matches]
            sources = [m.get("source", "") for m in matches]
            context += f"REVERSE IMAGE SEARCH TOP RESULTS:\n"
            for i, (t, s) in enumerate(zip(titles, sources)):
                context += f"  {i+1}. {t} ({s})\n"
        kg = reverse_data.get("knowledge_graph", [])
        if kg:
            for item in kg:
                context += f"IDENTIFIED AS: {item.get('title', 'Unknown')}\n"
    if vision_result:
        context += f"AI VISION ANALYSIS:\n{vision_result}\n"

    if not context.strip():
        print("No data available for cross-referencing.")
        return None

    response = ollama.chat(
        model=REASONING_MODEL,
        messages=[{
            "role": "system",
            "content": """You are the final judge in a geolocation pipeline. You receive data from multiple sources: GPS coordinates, reverse geocoding, reverse image search results, and AI vision analysis.

Your job is to cross-reference ALL sources and determine the most accurate location. Weight the sources in this order of reliability:
1. GPS coordinates + reverse geocode (most reliable if available)
2. Reverse image search matches (very reliable if results reference specific locations)
3. AI vision analysis (least reliable, use as supporting evidence)

If sources conflict, explain why and go with the more reliable source.

Respond in EXACTLY this format:
FINAL LOCATION: [city, country]
CONFIDENCE: [0-100]%
EVIDENCE SUMMARY: [3-5 sentences combining all available evidence]
DATA SOURCES USED: [list which sources contributed to the conclusion]"""
        },
        {
            "role": "user",
            "content": f"Cross-reference these data sources and determine the final location:\n\n{context}"
        }]
    )

    result = response["message"]["content"]
    print(result)
    return result
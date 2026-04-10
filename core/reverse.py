import requests
import os

SERP_API_KEY = os.environ["SERP_API_KEY"]

def _upload_image(image_path):
    """Litterbox is a temp file host with 1 hour expiry"""
    try:
        with open(image_path, "rb") as f:
            response = requests.post(
                "https://litterbox.catbox.moe/resources/internals/api.php",
                files={"fileToUpload": f},
                data={
                    "reqtype": "fileupload",
                    "time": "1h"
                }
            )
    except FileNotFoundError:
        raise FileNotFoundError("[ERROR] File name is not valid.")

    if response.status_code != 200:
        print(f"[ERROR] Upload failed: {response.status_code}")
        return None

    return response.text.strip()


def reverse_search(image_path):
    if not SERP_API_KEY:
        print("[ERROR] SERP_API_KEY not set. Add it to your .env file.")
        return None

    print("Uploading image...")
    image_url = _upload_image(image_path)
    if not image_url:
        return None

    print("Searching...")
    response = requests.get(
        "https://serpapi.com/search",
        params={
            "engine": "google_lens",
            "url": image_url,
            "api_key": SERP_API_KEY
        }
    )

    if response.status_code != 200:
        print(f"[ERROR] SerpAPI returned status {response.status_code}")
        return None

    data = response.json()

    if "knowledge_graph" in data:
        for item in data["knowledge_graph"]:
            print(f"Identified: {item.get('title', 'Unknown')}")
            if "subtitle" in item:
                print(f"  Info: {item['subtitle']}")
            if "link" in item:
                print(f"  Link: {item['link']}")
            print()

    matches = data.get("visual_matches", [])
    if matches:
        print(f"Found {len(matches)} visual matches:\n")
        for i, match in enumerate(matches[:5]):
            title = match.get("title", "No title")
            source = match.get("source", "Unknown")
            link = match.get("link", "")
            print(f"  {i+1}. {title}")
            print(f"     Source: {source}")
            print(f"     Link: {link}\n")
    else:
        print("No visual matches found.")

    return data
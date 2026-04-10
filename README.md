# Pixprobe

A CLI image forensics and geolocation tool. Extract metadata, reverse image search, and AI-powered location detection from any image.

## Features

- **Metadata Extraction** — Pull EXIF data, GPS coordinates, camera info, and more from images
- **Reverse Image Search** — Find where an image has appeared online using Google Lens via SerpAPI
- **AI Location Detection** — Two-model pipeline using Ollama: a vision model describes the scene, a reasoning model estimates the location like a GeoGuessr pro
- **Reverse Geocoding** — Convert GPS coordinates to human-readable addresses via OpenStreetMap
- **Cross-Referencing** — Combine metadata, reverse search, and AI vision to determine the most accurate location
- **Metadata Stripping** — Remove all EXIF data from images for privacy
- **Image Comparison** — Compare metadata between two images
- **Batch Processing** — Run any command on an entire folder of images

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/extxx/pixprobe.git
cd pixprobe
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Pixprobe uses [Ollama](https://ollama.com) for local AI-powered location detection.

```bash
# macOS
brew install ollama

# or download from https://ollama.com/download
```

Pull the required models:

```bash
ollama pull llava:7b          # vision model (recommended, ~4.7GB)
ollama pull llama3.1:8b       # reasoning model (~4.7GB)
```

Lighter alternatives:
- **Vision:** `moondream` (~2GB) — faster but less accurate
- **Reasoning:** `mistral:7b-instruct` — works great if you already have it

### 5. Get API keys

#### SerpAPI (Reverse Image Search)
1. Sign up at [serpapi.com](https://serpapi.com)
2. Free tier gives you **250 searches/month**
3. Copy your API key from the [API Key Dashboard](https://serpapi.com/manage-api-key)

### 6. Configure environment variables

Create a `.env` file in the project root:

```env
SERP_API_KEY=your_serpapi_key_here
VISION_MODEL=llava:7b
REASONING_MODEL=llama3.1:8b
```

Adjust the model names to match whatever you have installed in Ollama.

## Usage

### `meta` — Extract Metadata

Pull EXIF data from an image including camera model, GPS coordinates, timestamps, and more. If GPS data is found, it automatically resolves the address.

```bash
python app.py meta -i ./samples/photo.jpeg
```

### `reverse` — Reverse Image Search

Upload the image to a temporary host and search Google Lens via SerpAPI to find visual matches online.

```bash
python app.py reverse -i ./samples/photo.jpeg
```

### `locate` — Full Location Analysis

The main command. Runs the full pipeline:

1. **Metadata** — Extracts GPS and resolves address
2. **Reverse Search** — Finds online matches
3. **AI Vision** — Vision model describes the scene, reasoning model estimates location
4. **Cross-Reference** — Final model weighs all evidence and gives a definitive answer

```bash
python app.py locate -i ./samples/photo.jpeg
```

### `geo` — Reverse Geocode

Extract GPS coordinates from an image and convert them to a human-readable address.

```bash
python app.py geo -i ./samples/photo.jpeg
```

### `compare` — Compare Two Images

Compare metadata between two images side by side. Useful for checking if two photos came from the same camera or location.

```bash
python app.py compare -a ./photo1.jpeg -b ./photo2.jpeg
```

### `strip` — Remove Metadata

Strip all EXIF data from an image for privacy. Outputs a clean copy.

```bash
python app.py strip -i ./samples/photo.jpeg
python app.py strip -i ./samples/photo.jpeg -o ./clean_photo.jpeg
```

### `batch` — Batch Process

Run any mode on an entire folder of images.

```bash
python app.py batch -d ./samples -m meta
python app.py batch -d ./samples -m reverse
python app.py batch -d ./samples -m locate
```

## Project Structure

```
pixprobe/
├── app.py                 # CLI entry point
├── core/
│   ├── __init__.py
│   ├── metadata.py        # EXIF extraction, GPS parsing, metadata stripping
│   ├── reverse.py         # Reverse image search via SerpAPI + Google Lens
│   └── locate.py          # AI vision + reasoning location detection
├── utils/
│   ├── __init__.py
│   └── geo.py             # Reverse geocoding via OpenStreetMap Nominatim
├── samples/               
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- SerpAPI free account
__pycache__/
```

## License

MIT

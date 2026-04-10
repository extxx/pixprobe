from PIL import Image, ExifTags
from utils.geo import reverse_geocode

def _dms_to_decimal(dms, ref):
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    if ref in ["S", "W"]:
        decimal = -decimal
    return decimal

def _extract_gps(exif):
    if 34853 not in exif:
        return None

    gps_info = exif.get_ifd(34853)
    if not gps_info or 2 not in gps_info or 4 not in gps_info:
        return None

    lat = _dms_to_decimal(gps_info[2], gps_info[1])
    lon = _dms_to_decimal(gps_info[4], gps_info[3])

    return {"lat": lat, "lon": lon}

def extract_metadata(image_path, gps_only=False):
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        raise FileNotFoundError("[ERROR] File name is not valid.")

    exif = img.getexif()
    if not exif:
        print("no exif detected")
        return None

    gps = _extract_gps(exif)
    if gps_only:
        return gps

    for key, val in exif.items():
        if key == 34853:
            if gps:
                print(f"GPS: {gps['lat']}, {gps['lon']}")
                reverse_geocode(gps["lat"], gps["lon"])
            continue
        if key in ExifTags.TAGS:
            print(f"{ExifTags.TAGS[key]}: {val}")
        else:
            print(f"{key}: {val}")

    return gps

def strip_metadata(image_path, output_path):
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        raise FileNotFoundError("[ERROR] File name is not valid.")

    clean = Image.new(img.mode, img.size)
    clean.putdata(list(img.getdata()))
    clean.save(output_path)
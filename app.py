import argparse
import sys
import os

from dotenv import load_dotenv
load_dotenv()

from core.metadata import extract_metadata
from core.reverse import reverse_search
from core.locate import detect_landmark, cross_reference
from utils.geo import reverse_geocode

def main():
    parser = argparse.ArgumentParser(
        prog="pixprobe",
        description="Pixprobe - Image Forensics Tool"
    )
    subparsers = parser.add_subparsers(dest="command")

    meta_parser = subparsers.add_parser("meta", help="Extract metadata")
    meta_parser.add_argument("-i", "--input", required=True)

    reverse_parser = subparsers.add_parser("reverse", help="Reverse image search")
    reverse_parser.add_argument("-i", "--input", required=True)

    locate_parser = subparsers.add_parser("locate", help="Full location analysis")
    locate_parser.add_argument("-i", "--input", required=True)

    geo_parser = subparsers.add_parser("geo", help="Reverse geocode GPS coords")
    geo_parser.add_argument("-i", "--input", required=True)

    compare_parser = subparsers.add_parser("compare", help="Compare two images")
    compare_parser.add_argument("-a", "--first", required=True)
    compare_parser.add_argument("-b", "--second", required=True)

    strip_parser = subparsers.add_parser("strip", help="Remove metadata")
    strip_parser.add_argument("-i", "--input", required=True)
    strip_parser.add_argument("-o", "--output", help="Output path", default=None)

    batch_parser = subparsers.add_parser("batch", help="Batch process folder")
    batch_parser.add_argument("-d", "--dir", required=True)
    batch_parser.add_argument("-m", "--mode", required=True)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "meta":
        extract_metadata(args.input)

    elif args.command == "reverse":
        reverse_search(args.input)

    elif args.command == "locate":
        print("=== Pixprobe Location Analysis ===\n")

        # step 1: metadata
        print("--- Step 1: Metadata ---")
        gps = extract_metadata(args.input, gps_only=True)
        geo_result = None
        if gps:
            print(f"GPS: {gps['lat']}, {gps['lon']}")
            geo_result = reverse_geocode(gps["lat"], gps["lon"])
        else:
            print("No GPS data found")
        print()

        # step 2: reverse image search
        print("--- Step 2: Reverse Image Search ---")
        reverse_data = reverse_search(args.input)
        print()

        # step 3: AI vision analysis
        print("--- Step 3: AI Vision Analysis ---")
        vision_result = detect_landmark(args.input)
        print()

        # step 4: cross-reference everything
        print("--- Step 4: Final Location Estimate ---")
        cross_reference(
            gps=gps,
            geo_result=geo_result,
            reverse_data=reverse_data,
            vision_result=vision_result
        )

    elif args.command == "geo":
        coords = extract_metadata(args.input, gps_only=True)
        if coords:
            reverse_geocode(coords["lat"], coords["lon"])
        else:
            print("No GPS data found in image")

    elif args.command == "compare":
        extract_metadata(args.first)
        print("\n--- vs ---\n")
        extract_metadata(args.second)

    elif args.command == "strip":
        from core.metadata import strip_metadata
        output = args.output or f"clean_{args.input}"
        strip_metadata(args.input, output)

    elif args.command == "batch":
        folder = args.dir
        for file in os.listdir(folder):
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".tiff")):
                path = os.path.join(folder, file)
                print(f"\n=== {file} ===")
                if args.mode == "meta":
                    extract_metadata(path)
                elif args.mode == "reverse":
                    reverse_search(path)
                elif args.mode == "locate":
                    detect_landmark(path)

if __name__ == "__main__":
    main()
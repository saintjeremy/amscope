#Command-line entry point for Audio Microscope.

import argparse
from pathlib import Path
from library_store import create_item

def main() -> None:
        
    #Read command-line options and hand the import to the library module.
    
    parser = argparse.ArgumentParser(
        description="Import and analyze audio into an ID-based local music library"
    )
    parser.add_argument("input", type=Path, help="Path to an audio file")
    parser.add_argument(
        "--library", type=Path, default=Path("library"), help="Library directory"
    )
    parser.add_argument("--name", help="Editable display name for this item")
    args = parser.parse_args()

    item_dir = create_item(args.input, args.library.expanduser().resolve(), args.name)
    print(f"Saved item: {item_dir}")


if __name__ == "__main__":
    main()
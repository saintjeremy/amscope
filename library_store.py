# Filesystem-backed storage for imported music items. This module owns item IDs, folders, metadata, and the library index. It does not know how audio analysis works; it simply asks ``audio_analysis`` for data and saves the returned result.
 

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from audio_analysis import analyze_audio


# A version number lets future code migrate older metadata when its shape changes.

SCHEMA_VERSION = 1


def utc_now() -> str:
    
    # Return an unambiguous timestamp suitable for saving in JSON behold might iso8601
    
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: Any) -> None:
    
    # Write JSON atomically so an interrupted write cannot corrupt the file. 
    
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    
    # replace() is one filesystem operation, so readers see old or new—not half.
    
    temporary_path.replace(path)


def create_item(input_path: Path, library_dir: Path, name: Optional[str]) -> Path:
    
    # Copy one audio file into the library, analyze it, and return its folder. 
    
    input_path = input_path.expanduser().resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {input_path}")

    # The ID is permanent. Names and paths may change without breaking references.
    item_id = str(uuid.uuid4())
    item_dir = library_dir / "items" / item_id
    source_dir = item_dir / "source"
    analysis_dir = item_dir / "analysis"
    previews_dir = item_dir / "previews"
    for directory in (source_dir, analysis_dir, previews_dir):
        directory.mkdir(parents=True, exist_ok=False)

    created_at = utc_now()
    stored_source = source_dir / input_path.name
    shutil.copy2(input_path, stored_source)

    item = {
        "schemaVersion": SCHEMA_VERSION,
        "id": item_id,
        "kind": "audio",
        "name": name or input_path.stem,
        "status": "analyzing",
        "createdAt": created_at,
        "updatedAt": created_at,
        "source": {
            "type": "file",
            "originalFilename": input_path.name,
            # Store a relative path so the entire library remains portable.
            "storedPath": f"source/{input_path.name}",
        },
    }
    write_json(item_dir / "item.json", item)

    try:
        result = analyze_audio(stored_source, previews_dir)
        write_json(analysis_dir / "summary.json", result["summary"])
        write_json(analysis_dir / "beats.json", result["beats"])

        summary = result["summary"]
        item.update(
            {
                "status": "analyzed",
                "updatedAt": utc_now(),
                "durationSeconds": summary["durationSeconds"],
                "sampleRateHz": summary["sampleRateHz"],
                "tempoBpm": summary["tempoBpm"],
            }
        )
        write_json(item_dir / "item.json", item)
    except Exception as error:

        # Keeping the failed item makes the problem visible and diagnosable.
        
        item.update(
            {"status": "failed", "updatedAt": utc_now(), "error": str(error)}
        )
        write_json(item_dir / "item.json", item)
        rebuild_library_index(library_dir)
        raise

    rebuild_library_index(library_dir)
    return item_dir


def rebuild_library_index(library_dir: Path) -> List[Dict[str, Any]]:
    # Recreate the quick-to-read index from authoritative item.json files.
    items: List[Dict[str, Any]] = []
    items_dir = library_dir / "items"
    if items_dir.exists():
        for metadata_path in sorted(items_dir.glob("*/item.json")):
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                print(f"Skipping unreadable item {metadata_path}: {error}")
                continue

            # The index contains only fields needed to display a library listing.
            items.append(
                {
                    key: metadata[key]
                    for key in (
                        "id",
                        "kind",
                        "name",
                        "status",
                        "createdAt",
                        "updatedAt",
                        "durationSeconds",
                        "tempoBpm",
                    )
                    if key in metadata
                }
            )

    items.sort(key=lambda item: item.get("createdAt", ""), reverse=True)
    write_json(
        library_dir / "library.json",
        {"schemaVersion": SCHEMA_VERSION, "updatedAt": utc_now(), "items": items},
    )
    return items
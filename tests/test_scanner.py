from cleanup.scanner import scan_library, get_library_summary

def test_scan_library():
    photos = scan_library(limit=5)
    assert len(photos) >= 5
    for photo in photos:
        print(f"{photo.filename} — {photo.file_size_bytes} bytes")

def test_library_summary():
    photos = scan_library(limit=20)
    summary = get_library_summary(photos)
    print(summary.model_dump_json(indent=2))
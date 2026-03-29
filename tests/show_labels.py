from cleanup.scanner import scan_library

photos = scan_library(limit=100)
all_labels = set()
for p in photos:
    all_labels.update(p.labels)
for label in sorted(all_labels):
    print(label)
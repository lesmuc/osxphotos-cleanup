from cleanup.scanner import scan_library

photos = scan_library(limit=100)
all_persons = set()
for p in photos:
    all_persons.update(p.metadata.persons)
for person in sorted(all_persons):
    print(person)

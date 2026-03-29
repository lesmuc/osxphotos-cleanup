import photoscript
from cleanup.models import CleanupSuggestion, SuggestedAction

def organize_into_albums(suggestions:list[CleanupSuggestion]) -> None:
    album_names = {
          SuggestedAction.DELETE: "AI: To Delete",
          SuggestedAction.REVIEW: "AI: To Review",
          SuggestedAction.ARCHIVE: "AI: To Archive",        
    }

    photoslib = photoscript.PhotosLibrary()

    for action, album_name in album_names.items():
        photos_for_action = [s for s in suggestions if s.action == action]
        if not photos_for_action:
            continue

        album = photoslib.album(album_name)
        if album is None:
            album = photoslib.create_album(album_name)

        uuids = []      
        for s in photos_for_action:
            uuids.append(s.photo_uuid)  

        photos = []                                                                                 
        for uuid in uuids:                                                                          
            found = list(photoslib.photos(uuid=[uuid]))
            if found:                                                                               
                photos.append(found[0])

        if photos:
            album.add(photos)

        print(f"  {album_name}: {len(photos)} Fotos hinzugefügt")




        

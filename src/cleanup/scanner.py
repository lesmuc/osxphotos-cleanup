from osxphotos import PhotoInfo, PhotosDB
from cleanup.models import PhotoMetadata, LibrarySummary, ScannedPhoto

def _photo_info_to_metadata(photo: PhotoInfo) -> PhotoMetadata:
    return PhotoMetadata(
        uuid=photo.uuid,
        filename=photo.filename,
        original_filename=photo.original_filename,
        path=photo.path,
        date=photo.date,
          file_size_bytes=photo.original_filesize,
          width=photo.width,                                                                                                                                                                                                                                  
          height=photo.height,
          is_screenshot=photo.screenshot,                                                                                                                                                                                                                     
          is_burst=photo.burst,                             
          is_live_photo=photo.live_photo,
          is_portrait=photo.portrait,
          is_selfie=photo.selfie,                                                                                                                                                                                                                             
          is_favorite=photo.favorite,
          is_hidden=photo.hidden,                                                                                                                                                                                                                             
          is_movie=photo.ismovie,                           
          labels=photo.labels,
          keywords=photo.keywords,
          persons=photo.persons,                                                                                                                                                                                                                              
          albums=[a.title for a in photo.album_info],
          has_location=photo.location != (None, None),
    )

def scan_library(limit: int = 0) -> list[ScannedPhoto]:
    photosdb = PhotosDB()                                                                                                                                                                                                                         
    photos = photosdb.photos()
    if limit > 0:                                                                                                                                                                                                                                           
        photos = photos[:limit]    

    result = []
    for p in photos:
        result.append(
            ScannedPhoto(
                metadata=_photo_info_to_metadata(p),
                photo_info=p
            )
        )
    return result
        
def get_library_summary(photos: list[ScannedPhoto]) -> LibrarySummary:
    return LibrarySummary(
          total_photos=sum(1 for p in photos if not p.metadata.is_movie),
          total_videos=sum(1 for p in photos if p.metadata.is_movie),                                                                                                                                                                                                  
          total_size_gb=sum(p.metadata.file_size_bytes for p in photos) / (1024 ** 3),
          screenshots=sum(1 for p in photos if p.metadata.is_screenshot),                                                                                                                                                                                              
          bursts=sum(1 for p in photos if p.metadata.is_burst),
    )
        

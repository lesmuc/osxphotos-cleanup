from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Any

class SuggestedAction(str, Enum):
    KEEP = "keep"
    DELETE = "delete"
    REVIEW = "review"
    ARCHIVE = "archive"

class PhotoMetadata(BaseModel):
    uuid: str
    filename: str
    original_filename: str
    path: str | None
    date: datetime | None
    file_size_bytes: int                                                                                                                                                                                                                                    
    width: int
    height: int                                                                                                                                                                                                                                             
    is_screenshot: bool                                   
    is_burst: bool
    is_live_photo: bool
    is_portrait: bool
    is_selfie: bool
    is_favorite: bool                                                                                                                                                                                                                                       
    is_hidden: bool
    is_movie: bool                                                                                                                                                                                                                                          
    labels: list[str]                                     
    keywords: list[str]
    persons: list[str]
    albums: list[str]
    has_location: bool

class CleanupSuggestion(BaseModel):
    photo_uuid: str
    filename: str
    action: SuggestedAction
    reason: str
    confidence: float
    rule_name: str

class LibrarySummary(BaseModel):
    total_photos: int
    total_videos: int
    total_size_gb: float
    screenshots: int
    bursts: int

class PhotoAnalysis(BaseModel):
    suggestedAction: SuggestedAction
    reason: str

# Container für PhotoMetadata und PhotoInfo aus osxphotos
@dataclass
class ScannedPhoto:
    metadata: PhotoMetadata
    photo_info: Any
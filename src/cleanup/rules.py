from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from cleanup.models import PhotoMetadata, CleanupSuggestion, SuggestedAction, ScannedPhoto

class CleanupRule(ABC):
    name: str

    @abstractmethod
    def evaluate(self, photo: ScannedPhoto, all_photos: list[ScannedPhoto]) -> CleanupSuggestion | None:
        ...

class LargeFileRule(CleanupRule):
    name = "LargeFileRule"

    def evaluate(self, photo: ScannedPhoto, all_photos: list[ScannedPhoto]) -> CleanupSuggestion | None:
        if photo.metadata.is_movie and photo.metadata.file_size_bytes > 500 * 1024 * 1024:
            return CleanupSuggestion(
                photo_uuid=photo.metadata.uuid,
                filename=photo.metadata.filename,
                action=SuggestedAction.REVIEW,
                reason="LargeMovie",
                confidence=0.8,
                rule_name=self.name
            )
        elif not photo.metadata.is_movie and photo.metadata.file_size_bytes > 50 * 1024 * 1024:
            return CleanupSuggestion(
                photo_uuid=photo.metadata.uuid,
                filename=photo.metadata.filename,
                action=SuggestedAction.REVIEW,
                reason="LargePhoto",
                confidence=0.8,
                rule_name=self.name
            )

class BurstCleanupRule(CleanupRule):
    name = "BurstCleanupRule"

    def evaluate(self, photo: ScannedPhoto, all_photos: list[ScannedPhoto]) -> CleanupSuggestion | None:
        if photo.metadata.is_burst and not photo.metadata.is_favorite:
            return CleanupSuggestion(
                photo_uuid=photo.metadata.uuid,
                filename=photo.metadata.filename,
                action=SuggestedAction.DELETE,
                reason="Burst",
                confidence=0.8,
                rule_name=self.name
            )
    
class DrinkRule(CleanupRule):
    name = "DrinkRule"

    def evaluate(self, photo: ScannedPhoto, all_photos: list[ScannedPhoto]) -> CleanupSuggestion | None:
        if photo.metadata.is_favorite:
            return None
                    
        food_labels = {"trinkglas", "flasche"}
        photo_labels = {label.lower() for label in photo.metadata.labels}

        if photo_labels & food_labels:

            # Überspringen, wenn bekannte Personen auf dem Foto sind
            if photo.metadata.persons:
                return None  

            return CleanupSuggestion(
                  photo_uuid=photo.metadata.uuid,
                  filename=photo.metadata.filename,
                  action=SuggestedAction.REVIEW,
                  reason=f"Drink: {photo_labels & food_labels}",
                  confidence=0.6,
                  rule_name=self.name,                
            )
        
class FoodRule(CleanupRule):
    name = "FoodRule"

    def evaluate(self, photo: ScannedPhoto, all_photos: list[ScannedPhoto]) -> CleanupSuggestion | None:
        if photo.metadata.is_favorite:
            return None
        
        food_labels = {"essen"}
        photo_labels = {label.lower() for label in photo.metadata.labels}

        if photo_labels & food_labels:
            # Überspringen, wenn bekannte Personen auf dem Foto sind
            if photo.metadata.persons:
                return None

            return CleanupSuggestion(
                  photo_uuid=photo.metadata.uuid,
                  filename=photo.metadata.filename,
                  action=SuggestedAction.REVIEW,
                  reason=f"Food: {photo_labels & food_labels}",
                  confidence=0.6,
                  rule_name=self.name,                
            )        
        

def run_all_rules(photos: list[ScannedPhoto]) -> list[CleanupSuggestion]:
    rules = [
        LargeFileRule(),
        BurstCleanupRule(),
        DrinkRule(),
        FoodRule()
    ]
    suggestions = []
    for photo in photos:
        for rule in rules:
            result = rule.evaluate(photo, photos)
            if result:
                suggestions.append(result)
                break
    return suggestions

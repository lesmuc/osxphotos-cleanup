from dataclasses import dataclass
from pathlib import Path
from pathlib import Path
import json
from ollama import chat
from pydantic_ai.models.openai import OpenAIModel                                            
from pydantic_ai.providers.openai import OpenAIProvider  
from cleanup.models import PhotoMetadata, PhotoAnalysis, SuggestedAction, ScannedPhoto
from pydantic_ai import Agent, BinaryContent
import tempfile
from PIL import Image
from pillow_heif import register_heif_opener

@dataclass
class AgentDeps:
    photos_by_uuid: dict[str, PhotoMetadata]

model = OpenAIModel(                                                                         
    "llama3.2-vision:11b",
    provider=OpenAIProvider(                                                                 
        base_url="http://localhost:11434/v1",                                                
        api_key="ollama",                                                                    
    ),                                                                                       
)

register_heif_opener()

def analyze_photo(photo: ScannedPhoto, reason: str, on_status=None) -> PhotoAnalysis:

    with tempfile.TemporaryDirectory() as tmpdir:

        filename = "photo.jpeg"
        jpeg_path = f"{tmpdir}/{filename}"

        if photo.metadata.path:
            if on_status:
                on_status("    Konvertiere nach JPEG...")

            # Foto ist lokal
            img = Image.open(photo.metadata.path)
            img.save(jpeg_path, "JPEG")
        else:
            if on_status:
                on_status("    Lade aus iCloud...")

            # Foto nur in der Cloud
            exported = photo.photo_info.export(
                tmpdir,
                filename=filename,
                use_photos_export=True
            )
            img = Image.open(exported[0])
            img.save(jpeg_path, "JPEG")

        if on_status:
            on_status("    Sende an Ollama...")

        response = chat(
            model="gemma3:27b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a photo library cleanup assistant. "
                        "This photo was flagged as a food or drink photo without people. "
                        "Photos showing ONLY food, drinks, bottles, or glasses "
                        "without any people visible should be marked as 'delete'. "
                        "Only suggest 'keep' if the photo clearly shows people, "
                        "a meaningful event, or a recognizable landmark. "
                        "A nice-looking bottle or glass alone is NOT a reason to keep."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"This photo was flagged for cleanup. Reason: {reason}. "
                        f"Should it be kept or deleted? Answer with 'keep' or 'delete' and a short reason."
                    ),
                    "images": [jpeg_path],
                },
            ],
        )

        text = response.message.content.lower()
        if "delete" in text:
            action = SuggestedAction.DELETE
        elif "keep" in text:
            action = SuggestedAction.KEEP
        else:
            action = SuggestedAction.REVIEW

        return PhotoAnalysis(
            suggestedAction=action,
            reason=response.message.content,
        )
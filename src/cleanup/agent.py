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

photo_analyst = Agent(
    model,
    deps_type=AgentDeps,
    result_type=PhotoAnalysis,
    system_prompt=(
        "You are a photo library cleanup assistant. "                                                                                                                      
        "This photo was flagged because it appears to show food or drinks. "                                                                                               
        "Your job is to decide: is this a meaningful memory worth keeping, "                                                                                               
        "or just a casual food/drink snapshot that can be deleted? "                                                                                                       
        "Photos of food or drinks WITHOUT people should usually be deleted. "                                                                                              
        "Only suggest 'keep' if the photo has clear sentimental or artistic value "                                                                                        
        "beyond just showing food or drinks. "                                                                                                                             
        "Respond with valid JSON matching the output schema."
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
            model="llama3.2-vision:11b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a photo library cleanup assistant. "
                        "Analyze the photo and its metadata. "
                        "Determine if it should be kept, deleted, or reviewed. "
                        "Be conservative — when in doubt, suggest 'review'."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"This photo was flagged for cleanup. Reason: {reason}. "                                                                                                          
                        f"Metadata: filename={photo.metadata.filename}, "     
                        f"date={photo.metadata.date}, size={photo.metadata.file_size_bytes} bytes, "                                                                                       
                        f"labels={photo.metadata.labels}, persons={photo.metadata.persons}"
                    ),
                    "images": [jpeg_path],
                },
            ],
            format=PhotoAnalysis.model_json_schema(),
        )

        return PhotoAnalysis.model_validate_json(response.message.content)
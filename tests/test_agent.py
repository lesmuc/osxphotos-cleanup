from cleanup.agent import analyze_photo
from cleanup.models import PhotoMetadata, SuggestedAction
from datetime import datetime, timezone

def test_analyze_single_photo():
    photo = PhotoMetadata(
          uuid="test-1",
          filename="test.jpg",
          original_filename="test.jpg",
          path=None,
          date=datetime(2025, 6, 15, tzinfo=timezone.utc),
          file_size_bytes=2_000_000,
          width=4032,
          height=3024,
          is_screenshot=False,
          is_burst=False,
          is_live_photo=False,
          is_portrait=False,
          is_selfie=False,
          is_favorite=False,
          is_hidden=False,
          is_movie=False,
          labels=["tree", "sky"],
          keywords=[],
          persons=[],
          albums=[],
          has_location=True,
    )

    result = analyze_photo(photo, "/Users/udo/Desktop/B1E37851-98C1-43AC-9F7E-33803523E1FA_1_105_c.jpeg")
    print(f"Description: {result.description}")
    print(f"Quality: {result.cleanup_assessment}")
    print(f"Meaningful: {result.is_meaningful}")
    print(f"Action: {result.suggestedAction}")
    print(f"Reason: {result.reason}")
    print(f"Confidence: {result.confidence}")
    assert result.suggestedAction in list(SuggestedAction)    
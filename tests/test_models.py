from cleanup.models import PhotoMetadata, CleanupSuggestion, LibrarySummary, PhotoAnalysis, SuggestedAction

def test_photo_metadata():
      photo = PhotoMetadata(                                
          uuid="test-123",
          filename="IMG_001.jpg",
          original_filename="IMG_001.jpg",
          path=None,
          date=None,
          file_size_bytes=1024000,
          width=4032,                                                                                                                                                                                                                                         
          height=3024,
          is_screenshot=False,                                                                                                                                                                                                                                
          is_burst=False,                                   
          is_live_photo=False,
          is_portrait=False,
          is_selfie=False,
          is_favorite=True,                                                                                                                                                                                                                                   
          is_hidden=False,
          is_movie=False,                                                                                                                                                                                                                                     
          labels=["tree", "sky"],                           
          keywords=[],
          persons=["Anna"],
          albums=["Urlaub"],
          has_location=True,
      )
      assert photo.uuid == "test-123"
      assert photo.is_favorite is True
      assert photo.path is None
      print(photo.model_dump_json(indent=2))

def test_cleanup_suggestion():
      suggestion = CleanupSuggestion(                       
          photo_uuid="test-123",
          filename="IMG_001.jpg",
          action=SuggestedAction.DELETE,
          reason="Screenshot älter als 6 Monate",                                                                                                                                                                                                             
          confidence=0.9,
          rule_name="ScreenshotRule",                                                                                                                                                                                                                         
      )
      assert suggestion.action == SuggestedAction.DELETE
      print(suggestion.model_dump_json(indent=2))
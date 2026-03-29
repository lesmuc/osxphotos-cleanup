from datetime import datetime, timezone                                                 
from cleanup.models import PhotoMetadata, SuggestedAction                               
from cleanup.rules import (
    ScreenshotRule,                                                                     
    LargeFileRule,
    BurstCleanupRule,
    FoodAndDrinkRule,                                                                   
    run_all_rules,
)                                                                                       

def _make_photo(**overrides) -> PhotoMetadata:
    defaults = {
          "uuid":"test-1",
          "filename":"IMG_001.jpg",
          "original_filename":"IMG_001.jpg",
          "path":None,
          "date":datetime(2025, 1, 1, tzinfo=timezone.utc),
          "file_size_bytes":1_000_000,
          "width":4032,
          "height":3024,
          "is_screenshot":False,
          "is_burst":False,
          "is_live_photo":False,
          "is_portrait":False,
          "is_selfie":False,
          "is_favorite":False,
          "is_hidden":False,
          "is_movie":False,
          "labels":["sky"],
          "keywords":[],
          "persons":[],
          "albums":[],
          "has_location":False,        
    }         
    defaults.update(overrides)
    return PhotoMetadata(**defaults)

# --- ScreenshotRule ---
                                                                                        
def test_screenshot_rule():
    photo = _make_photo(is_screenshot=True)
    result = ScreenshotRule().evaluate(photo, [photo])
    assert result is not None                                                           
    assert result.action == SuggestedAction.DELETE
                                                                                        
                                                                                        
def test_screenshot_rule_skips_normal():
    photo = _make_photo()                                                               
    result = ScreenshotRule().evaluate(photo, [photo])
    assert result is None


# --- LargeFileRule ---

def test_large_photo():                                                                 
    photo = _make_photo(file_size_bytes=60 * 1024 * 1024)
    result = LargeFileRule().evaluate(photo, [photo])                                   
    assert result is not None
    assert result.action == SuggestedAction.REVIEW
    assert result.reason == "LargePhoto"                                                

                                                                                        
def test_large_movie():
    photo = _make_photo(is_movie=True, file_size_bytes=600 * 1024 * 1024)
    result = LargeFileRule().evaluate(photo, [photo])                                   
    assert result is not None
    assert result.reason == "LargeMovie"                                                
                

def test_small_file_ignored():
    photo = _make_photo(file_size_bytes=1_000_000)
    result = LargeFileRule().evaluate(photo, [photo])
    assert result is None                                                               

                                                                                        
# --- BurstCleanupRule ---

def test_burst_not_favorite():
    photo = _make_photo(is_burst=True)
    result = BurstCleanupRule().evaluate(photo, [photo])
    assert result is not None
    assert result.action == SuggestedAction.DELETE

                                                                                        
def test_burst_favorite_stays():
    photo = _make_photo(is_burst=True, is_favorite=True)                                
    result = BurstCleanupRule().evaluate(photo, [photo])
    assert result is None


# --- FoodAndDrinkRule ---

def test_food_detected():
    photo = _make_photo(labels=["Essen", "Teller"])
    result = FoodAndDrinkRule().evaluate(photo, [photo])
    assert result is not None                                                           
    assert result.action == SuggestedAction.REVIEW
                                                                                        
                
def test_food_favorite_stays():
    photo = _make_photo(labels=["Essen"], is_favorite=True)
    result = FoodAndDrinkRule().evaluate(photo, [photo])                                
    assert result is None
                                                                                        
                
def test_no_food_labels():
    photo = _make_photo(labels=["Baum", "Himmel"])
    result = FoodAndDrinkRule().evaluate(photo, [photo])                                
    assert result is None
                                                                                        
                
# --- run_all_rules ---

def test_run_all_rules_first_match_wins():                                              
    photo = _make_photo(is_screenshot=True, file_size_bytes=60 * 1024 * 1024)
    results = run_all_rules([photo])                                                    
    assert len(results) == 1
    assert results[0].rule_name == "ScreenshotRule"                                     
                                                                                        

def test_run_all_rules_no_match():                                                      
    photo = _make_photo()
    results = run_all_rules([photo])
    assert len(results) == 0
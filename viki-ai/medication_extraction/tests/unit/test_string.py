from src.utils.string import remove_prefix, remove_suffix

def test_remove_prefix():
    # Test with existing prefix
    assert remove_prefix("prefix_text", "prefix_") == "text"
    
    # Test with non-existent prefix
    assert remove_prefix("text", "prefix_") == "text"
    
    # Test with empty prefix
    assert remove_prefix("text", "") == "text"
    
    # Test with empty text
    assert remove_prefix("", "prefix_") == ""
    
    # Test when prefix is the entire string
    assert remove_prefix("test", "test") == ""

def test_remove_suffix():
    # Test with existing suffix
    assert remove_suffix("text_suffix", "_suffix") == "text"
    
    # Test with non-existent suffix
    assert remove_suffix("text", "_suffix") == "text"
    
    # Test with empty text
    assert remove_suffix("", "_suffix") == ""
    
    # Test when suffix is the entire string
    assert remove_suffix("test", "test") == ""
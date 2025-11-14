import re

def safe_str(s, noneReplacement=""):
    if s is None:
        return noneReplacement
    return str(s)

def remove_parentheses_substrings(input_string: str) -> str:
    # Use a regular expression to find and remove substrings within parentheses
    result = re.sub(r'\(.*?\)', '', input_string)
    return result

def contains_paranthetical(input_string: str) -> bool:
    # Use a regular expression to check for the pattern (*)
    pattern = r'\(.*?\)'
    match = re.search(pattern, input_string)
    return match is not None

def remove_multiple_spaces(input_string: str) -> str:
    # Use a regular expression to replace multiple spaces with a single space
    result = re.sub(r'\s+', ' ', input_string)
    return result

def to_int(s: str, noneReplacement=0) -> int:
    # Convert a string to an integer
    if s is None:
        return noneReplacement
    return int(s)

def to_float(s: str, noneReplacement=0) -> float:
    # Convert a string to a float
    if s is None:
        return noneReplacement
    return float(s)

def remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def remove_suffix(text: str, suffix: str) -> str:
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text
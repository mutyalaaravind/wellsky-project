

def is_truthy(value: str) -> bool:
    """
    Check if a string is truthy (i.e., not empty and not "false").
    """
    if isinstance(value, bool):
        return value

    if value is None:
        return False
    elif value.lower() in ("true", "1", "yes", "on"):
        return True
    else:
        return False
    


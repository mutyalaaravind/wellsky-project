
def remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def remove_suffix(text: str, suffix: str) -> str:
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text
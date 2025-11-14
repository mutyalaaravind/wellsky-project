

def get_filetype_from_filename(filename: str) -> str:
    return filename.split(".")[-1].lower()
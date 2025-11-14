import uuid


def generate_id():
    """
    Generate a new UUID4 hex string (without hyphens).
    """
    return uuid.uuid4().hex
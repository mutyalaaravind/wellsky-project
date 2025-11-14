"""
User model for authentication.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class User(BaseModel):
    """
    User model representing an authenticated user.

    Attributes:
        sub: Subject identifier from JWT token (unique user ID)
        email: User's email address
        name: User's display name
        claims: All JWT claims from the token
    """
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    claims: Optional[Dict[str, Any]] = None  # Store all JWT claims

    class Config:
        """Pydantic model configuration."""
        # Allow extra fields from JWT claims if needed
        extra = "allow"
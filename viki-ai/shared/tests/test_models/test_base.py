import pytest
from datetime import datetime

from viki_shared.models.base import AggBase


def test_agg_base_creation():
    """Test AggBase model creation with defaults."""
    model = AggBase()
    
    assert model.id is not None
    assert isinstance(model.id, str)
    assert isinstance(model.created_at, datetime)
    assert isinstance(model.modified_at, datetime)
    assert model.created_by is None
    assert model.modified_by is None
    assert model.active is True


def test_agg_base_with_custom_values():
    """Test AggBase model creation with custom values."""
    custom_id = "test-id"
    custom_creator = "test-user"
    
    model = AggBase(
        id=custom_id,
        created_by=custom_creator,
        modified_by=custom_creator,
        active=False
    )
    
    assert model.id == custom_id
    assert model.created_by == custom_creator
    assert model.modified_by == custom_creator
    assert model.active is False
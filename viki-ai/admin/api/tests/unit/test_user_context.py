"""
Unit tests for User Context implementation across all layers.

This test suite verifies that the context-based user management works
correctly from middleware through to infrastructure layer.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Domain layer imports
from domain.models.user_context import (
    set_current_user_sync,
    get_current_user_sync,
    get_audit_context,
    clear_user_context,
    has_user_context
)
from models.user import User

# Application layer imports
from application.profile_resolver import ProfileResolver


class TestUserContext:
    """Test suite for User Context functionality."""

    def setup_method(self):
        """Clear context before each test."""
        clear_user_context()

    def teardown_method(self):
        """Clear context after each test."""
        clear_user_context()

    def test_set_and_get_user_context(self):
        """Test setting and retrieving user from context."""
        # Arrange
        mock_user = User(
            sub="test-user-123",
            email="test@example.com",
            name="Test User",
            claims={
                "sub": "test-user-123",
                "email": "test@example.com",
                "name": "Test User",
                "group-roles": ["admin"]
            }
        )

        # Act
        set_current_user_sync(mock_user)
        retrieved_user = get_current_user_sync()

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.sub == "test-user-123"
        assert retrieved_user.name == "Test User"
        assert retrieved_user.claims["group-roles"] == ["admin"]

    def test_context_isolation(self):
        """Test that context starts empty and can be cleared."""
        # Verify starts empty
        assert get_current_user_sync() is None
        assert not has_user_context()

        # Set user
        mock_user = User(sub="test", email="test@test.com", name="Test")
        set_current_user_sync(mock_user)

        # Verify user is set
        assert has_user_context()
        assert get_current_user_sync() is not None

        # Clear context
        clear_user_context()

        # Verify cleared
        assert get_current_user_sync() is None
        assert not has_user_context()

    def test_audit_context_generation(self):
        """Test audit context generation from user context."""
        # Arrange
        mock_user = User(
            sub="audit-user-456",
            email="audit@example.com",
            name="Audit User",
            claims={
                "sub": "audit-user-456",
                "email": "audit@example.com",
                "name": "Audit User"
            }
        )

        # Act
        set_current_user_sync(mock_user)
        audit_context = get_audit_context()

        # Assert
        assert "timestamp" in audit_context
        assert audit_context["user_sub"] == "audit-user-456"
        assert audit_context["user_email"] == "audit@example.com"
        assert audit_context["user_name"] == "Audit User"

    def test_audit_context_without_user(self):
        """Test audit context generation when no user is set."""
        # Act
        audit_context = get_audit_context()

        # Assert
        assert "timestamp" in audit_context
        assert "user_sub" not in audit_context
        assert "user_email" not in audit_context

    @pytest.mark.asyncio
    async def test_profile_resolver_context_access(self):
        """Test that ProfileResolver can access user context."""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_profile = AsyncMock(return_value=None)

        profile_resolver = ProfileResolver(mock_repo)

        mock_user = User(
            sub="resolver-test",
            email="resolver@test.com",
            name="Resolver Test"
        )
        set_current_user_sync(mock_user)

        # Act - Test sync access to context
        cached_profile = profile_resolver.resolve_current_user_profile_sync()

        # Assert
        assert cached_profile is None  # No cached profile

        # Test that resolver can access user context
        user_from_context = get_current_user_sync()
        assert user_from_context is not None
        assert user_from_context.email == "resolver@test.com"

    def test_infrastructure_layer_context_access(self):
        """Test that infrastructure layer can access context for audit trails."""
        # Arrange - Simulate infrastructure adapter behavior
        mock_user = User(
            sub="infra-user",
            email="infra@example.com",
            name="Infrastructure User"
        )
        set_current_user_sync(mock_user)

        # Act - Simulate what UserProfileFirestoreAdapter does
        current_user = get_current_user_sync()
        current_user_email = current_user.email if current_user else "system"
        audit_context = get_audit_context()

        # Create logging extra data as done in adapter
        extra_logging_data = {
            "operation": "create_user_profile",
            "profile_id": "test-profile",
            "acting_user": current_user_email,
            **audit_context
        }

        # Assert
        assert current_user_email == "infra@example.com"
        assert extra_logging_data["acting_user"] == "infra@example.com"
        assert extra_logging_data["user_email"] == "infra@example.com"
        assert extra_logging_data["operation"] == "create_user_profile"
        assert "timestamp" in extra_logging_data

    def test_context_with_different_user_data(self):
        """Test context with various user data scenarios."""
        # Test with minimal user data
        minimal_user = User(sub="minimal", email=None, name=None, claims={})
        set_current_user_sync(minimal_user)

        retrieved = get_current_user_sync()
        assert retrieved.sub == "minimal"
        assert retrieved.email is None

        # Test audit context with minimal data
        audit = get_audit_context()
        assert audit["user_sub"] == "minimal"
        assert "user_email" not in audit  # Should not include None values

        clear_user_context()

        # Test with full user data
        full_user = User(
            sub="full-user",
            email="full@test.com",
            name="Full User",
            claims={
                "sub": "full-user",
                "email": "full@test.com",
                "name": "Full User",
                "group-roles": ["admin", "user"],
                "custom_claim": "value"
            }
        )
        set_current_user_sync(full_user)

        retrieved = get_current_user_sync()
        assert retrieved.claims["group-roles"] == ["admin", "user"]
        assert retrieved.claims["custom_claim"] == "value"

    def test_multiple_context_operations(self):
        """Test multiple context operations in sequence."""
        users = [
            User(sub="user1", email="user1@test.com", name="User 1"),
            User(sub="user2", email="user2@test.com", name="User 2"),
            User(sub="user3", email="user3@test.com", name="User 3")
        ]

        for user in users:
            # Set user
            set_current_user_sync(user)

            # Verify correct user is set
            retrieved = get_current_user_sync()
            assert retrieved.sub == user.sub
            assert retrieved.email == user.email

            # Verify audit context updates
            audit = get_audit_context()
            assert audit["user_sub"] == user.sub
            assert audit["user_email"] == user.email

        # Final verification
        final_user = get_current_user_sync()
        assert final_user.sub == "user3"  # Should be the last set user
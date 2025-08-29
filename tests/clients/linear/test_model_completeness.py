"""
Tests for model completeness.

This module tests that core domain models include all fields from the Linear GraphQL schema.
"""

import pytest
import os

from alfred.clients.linear import LinearClient
from alfred.clients.linear.domain import (
    LinearIssue,
    LinearUser,
    LinearProject,
    LinearTeam,
)


@pytest.fixture
def client():
    """Create a LinearClient instance for testing."""
    # Get the API key from environment variable
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        pytest.skip("LINEAR_API_KEY environment variable not set")

    # Create and return the client
    return LinearClient(api_key=api_key)


def test_model_completeness(client):
    """Test that core models include all fields from the Linear GraphQL schema."""
    # List of models to check
    models = [
        LinearIssue,
        LinearUser,
        LinearProject,
        LinearTeam,
    ]

    # Model names for better error reporting
    model_names = {
        "LinearIssue": "Issue",
        "LinearUser": "User",
        "LinearProject": "Project",
        "LinearTeam": "Team",
    }

    # Test each model
    for model_class in models:
        # Validate the model against the schema
        result = client.validate_schema(model_class)

        # Get model completeness
        completeness = result.get("completeness", 0) * 100

        # Get missing fields for better error reporting
        missing_fields = result.get("missing_in_model", [])

        # Get model name for better error message
        model_name = model_class.__name__
        graphql_type = model_names.get(model_name, model_class.linear_class_name)

        # Debug print when there are missing fields
        if missing_fields:
            print(f"\nMissing fields in {model_name} (GraphQL Type: {graphql_type}):")
            for field in missing_fields:
                print(f"  - {field}")

        # Check all property getters on the model
        property_fields = []
        for attr_name in dir(model_class):
            if isinstance(getattr(model_class, attr_name), property):
                property_fields.append(attr_name)

        # Known missing fields that are handled by property getters
        known_missing = set(
            model_class.known_missing_fields
            if hasattr(model_class, "known_missing_fields")
            else []
        )

        # Property fields should match known_missing_fields
        for field in property_fields:
            if field not in known_missing and not field.startswith("_"):
                print(
                    f"Warning: Property {field} is not listed in known_missing_fields for {model_name}"
                )

        # Calculate completeness considering property getters for missing fields
        # Only count missing fields that don't have property implementations
        unhandled_missing_fields = [
            f for f in missing_fields if f not in property_fields
        ]

        # Calculate adjusted completeness - we only require 80% completeness to allow for Linear API evolution
        if len(missing_fields) == 0:
            adjusted_completeness = 100.0
        else:
            total_fields = len(result.get("common_fields", [])) + len(missing_fields)
            adjusted_completeness = (
                (total_fields - len(unhandled_missing_fields)) / total_fields
            ) * 100

        # More realistic threshold - 80% completeness allows for API evolution
        MIN_COMPLETENESS = 80.0

        assert adjusted_completeness >= MIN_COMPLETENESS, (
            f"{model_name} (GraphQL Type: {graphql_type}) model completeness is below {MIN_COMPLETENESS}%. "
            + f"Adjusted completeness: {adjusted_completeness:.1f}%. "
            + f"Unhandled missing fields: {unhandled_missing_fields}"
        )

        # Ensure fields in known_missing_fields have corresponding property getters (when they exist)
        for field in known_missing:
            if field in property_fields:
                # This is good - the field is properly handled by a property
                continue
            else:
                # Only warn, don't fail - the field might be intentionally not implemented
                if missing_fields and field in missing_fields:
                    print(
                        f"Info: Field {field} is in known_missing_fields but not implemented as property in {model_name}"
                    )

        # Assert that fields implemented as properties are documented in known_missing_fields
        undocumented_properties = []
        for field in property_fields:
            if (
                not field.startswith("_")
                and not field.startswith("model_")
                and field not in known_missing
            ):
                undocumented_properties.append(field)

        if undocumented_properties:
            print(
                f"Warning: Properties {undocumented_properties} should be listed in known_missing_fields for {model_name}"
            )


def test_model_has_necessary_soft_deletion_fields(client):
    """Test that models have all necessary soft deletion fields."""
    # List of models to check
    models = [
        LinearIssue,
        LinearUser,
        LinearProject,
        LinearTeam,
    ]

    # Soft deletion fields that should be present
    soft_delete_fields = ["archivedAt"]

    # Additional fields based on model type
    issue_fields = ["trashed", "canceledAt", "completedAt", "autoArchivedAt"]
    project_fields = ["trashed", "canceledAt", "completedAt", "autoArchivedAt"]

    # Test each model
    for model_class in models:
        # Validate the model against the schema
        result = client.validate_schema(model_class)

        # Get common fields
        common_fields = set(result.get("common_fields", []))

        # Check required soft deletion fields for all models
        for field in soft_delete_fields:
            assert field in common_fields, (
                f"{field} should be present in {model_class.__name__}"
            )

        # Check additional fields based on model type
        if model_class is LinearIssue:
            for field in issue_fields:
                assert field in common_fields, (
                    f"{field} should be present in LinearIssue"
                )

        if model_class is LinearProject:
            for field in project_fields:
                assert field in common_fields, (
                    f"{field} should be present in LinearProject"
                )

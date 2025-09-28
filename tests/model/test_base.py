# tests/model/test_base.py

import pytest
from Prism.models.base import MetaModel

class TestMetaModel:
    """Tests for the MetaModel class."""

    @pytest.fixture
    def minimal_meta(self) -> MetaModel:
        """A MetaModel instance with only required fields."""
        return MetaModel(id="test-id", name="Test Name")

    @pytest.fixture
    def full_meta(self) -> MetaModel:
        """A MetaModel instance with all fields populated."""
        return MetaModel(
            id="full-id",
            name="Full Name",
            description="A detailed description."
        )

    def test_instantiation_minimal(self, minimal_meta: MetaModel):
        """Test successful instantiation with minimal required data."""
        assert minimal_meta.id == "test-id"
        assert minimal_meta.name == "Test Name"
        assert minimal_meta.description is None

    def test_instantiation_full(self, full_meta: MetaModel):
        """Test successful instantiation with all data."""
        assert full_meta.id == "full-id"
        assert full_meta.name == "Full Name"
        assert full_meta.description == "A detailed description."

    def test_str_representation(self, minimal_meta: MetaModel):
        """Test the __str__ method for a user-friendly representation."""
        assert str(minimal_meta) == "[test-id] Test Name"

    def test_repr_representation_minimal(self, minimal_meta: MetaModel):
        """Test the __repr__ method for a developer-friendly representation (minimal)."""
        expected_repr = str({'id': 'test-id', 'name': 'Test Name'})
        assert repr(minimal_meta) == expected_repr

    def test_repr_representation_full(self, full_meta: MetaModel):
        """Test the __repr__ method includes the description when present."""
        expected_repr = str({
            'id': 'full-id',
            'name': 'Full Name',
            'description': 'A detailed description.'
        })
        assert repr(full_meta) == expected_repr

    def test_equality(self):
        """Test the __eq__ method based on the 'id' field."""
        meta1 = MetaModel(id="same-id", name="Name One")
        meta2 = MetaModel(id="same-id", name="Name Two")
        meta3 = MetaModel(id="different-id", name="Name One")

        assert meta1 == meta2, "Models with the same id should be equal."
        assert meta1 != meta3, "Models with different ids should not be equal."
        assert meta1 != "same-id", "Should not be equal to a non-MetaModel object."
    
    def test_hashability(self):
        """Test that MetaModel instances can be used in sets and as dict keys."""
        meta1 = MetaModel(id="hash-id-1", name="Name 1")
        meta2 = MetaModel(id="hash-id-1", name="Name 2") # Same ID, should hash the same
        meta3 = MetaModel(id="hash-id-3", name="Name 3")

        # Test hashing equality
        assert hash(meta1) == hash(meta2)
        assert hash(meta1) != hash(meta3)

        # Test usage in a set
        meta_set = {meta1, meta2, meta3}
        assert len(meta_set) == 2, "Set should contain two unique models based on id."
        assert meta1 in meta_set
        assert meta3 in meta_set

        # Test usage as a dictionary key
        meta_dict = {meta1: "value1"}
        meta_dict[meta2] = "value2" # Should overwrite the entry for meta1
        assert len(meta_dict) == 1
        assert meta_dict[meta1] == "value2"


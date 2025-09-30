# tests/model/test_block.py

import pytest
from pydantic import ValidationError
from typing import Dict, Any

from Prism.models.block import BlockModel, Variant
from Prism.models.base import MetaModel
from Prism.exceptions import VariantNotFoundError

class TestVariantModel:
    """Tests for the Variant class."""

    def test_instantiation(self, block_persona: Dict[str, Any]):
        """Test that a Variant can be created from valid dictionary data."""
        variant_data = block_persona["variants"][0]
        variant = Variant(**variant_data)

        assert variant.id == "expert_teacher"
        assert variant.template_id == "tpl_persona_expert"
        assert variant.defaults is not None
        assert variant.defaults["language"] == "TypeScript"
        assert variant.contract_id is None

    def test_get_default_method(self):
        """Test the get_default mixin method on the Variant class."""
        variant_with_defaults = Variant(
            id="v1",
            template_id="t1",
            defaults={"key1": "value1", "key2": 100}
        )
        variant_without_defaults = Variant(id="v2", template_id="t2")

        # Case 1: Key exists
        assert variant_with_defaults.get_default("key1") == "value1"
        
        # Case 2: Key does not exist, should return method's default (None)
        assert variant_with_defaults.get_default("non_existent_key") is None
        
        # Case 3: Key does not exist, should return provided default_value
        assert variant_with_defaults.get_default("non_existent_key", "fallback") == "fallback"
        
        # Case 4: `defaults` attribute itself is None
        assert variant_without_defaults.get_default("any_key", "fallback") == "fallback"

class TestBlockModel:
    """Tests for the BlockModel class."""

    @pytest.mark.parametrize(
        "block_fixture_name, expected_id, expected_type, expected_variants",
        [
            ("block_persona", "blk_persona", "Persona", 1),
            ("block_task", "blk_task", "Task", 1),
            ("block_output", "blk_output", "OutputSpecification", 1),
        ]
    )
    def test_instantiation_from_valid_data(
        self, 
        block_fixture_name: str, 
        expected_id: str,
        expected_type: str,
        expected_variants: int,
        request: pytest.FixtureRequest
    ):
        """Test that BlockModel can be successfully instantiated from various valid fixtures."""
        block_data = request.getfixturevalue(block_fixture_name)
        block = BlockModel(**block_data)

        assert isinstance(block, BlockModel)
        assert isinstance(block.meta, MetaModel)
        assert block.meta.id == expected_id
        assert block.id == expected_id  # Test Identifiable property
        assert block.block_type == expected_type
        assert len(block.variants) == expected_variants
        assert all(isinstance(v, Variant) for v in block.variants)

    def test_get_variant_by_id_success(self, block_persona: Dict[str, Any]):
        """Test successfully retrieving an existing variant by its ID."""
        block = BlockModel(**block_persona)
        variant = block.get_variant_by_id("expert_teacher")
        
        assert isinstance(variant, Variant)
        assert variant.id == "expert_teacher"
        assert variant.template_id == "tpl_persona_expert"

    def test_get_variant_by_id_raises_error_for_unknown_id(self, block_persona: Dict[str, Any]):
        """Test that getting a non-existent variant raises a ModelError."""
        block = BlockModel(**block_persona)

        with pytest.raises(VariantNotFoundError) as exc_info:
            block.get_variant_by_id("non_existent_variant")
        
        # Check if the error message is informative
        assert "non_existent_variant" in str(exc_info.value)
        assert "blk_persona" in str(exc_info.value)
        assert "未找到" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_get_default_method_on_block(self, block_persona: Dict[str, Any]):
        """Test the get_default mixin method on the BlockModel class itself."""
        block = BlockModel(**block_persona)

        # Key exists in block-level defaults
        assert block.get_default("language") == "JavaScript"
        
        # Key does not exist, should return provided default
        assert block.get_default("non_existent_key", "fallback") == "fallback"

class TestBlockModelValidation:
    """Tests for Pydantic validation rules on BlockModel."""

    def test_raises_error_on_empty_variants(self, block_persona: Dict[str, Any]):
        """A block must have at least one variant."""
        invalid_data = block_persona.copy()
        invalid_data["variants"] = []
        
        with pytest.raises(ValidationError, match="List should have at least 1 item"):
            BlockModel(**invalid_data)

    def test_raises_error_on_missing_meta(self, block_persona: Dict[str, Any]):
        """A block must have a 'meta' field."""
        invalid_data = block_persona.copy()
        del invalid_data["meta"]
        
        with pytest.raises(ValidationError, match="meta\n  Field required"):
            BlockModel(**invalid_data)

    def test_raises_error_on_invalid_block_type(self, block_persona: Dict[str, Any]):
        """The 'block_type' must be one of the predefined Literal values."""
        invalid_data = block_persona.copy()
        invalid_data["block_type"] = "InvalidType"
        with pytest.raises(ValidationError, match="'Persona', 'Task', 'OutputSpecification'"):
            BlockModel(**invalid_data)

class TestBlockModelValidationWithBadPath:
    """
    Tests Pydantic validation rules on BlockModel using invalid 'badpath' data.
    This approach is data-driven, directly testing against the invalid fixture files.
    """

    @pytest.mark.parametrize(
        "block_id, expected_error_match",
        [
            # --- 原有的结构性错误测试 ---
            ("blk_empty_variants", r"List should have at least 1 item"),
            ("blk_missing_meta", r"meta\n  Field required"),
            ("blk_missing_block_type", r"block_type\n  Field required"),
            ("blk_invalid_block_type", r"Input should be .*'Persona'"), # 使其更通用
            ("blk_variant_missing_template_id", r"variants\.0\.template_id\n  Field required"),

            # --- 新增的类型和深层约束错误测试 ---
            (
                "blk_meta_id_not_string", 
                r"meta\.id\n  Input should be a valid string"
            ),
            (
                "blk_variants_not_array",
                r"variants\n  Input should be a valid list"
            ),
            (
                "blk_variant_id_not_string",
                r"variants\.0\.id\n  Input should be a valid string"
            ),
            (
                "blk_variant_defaults_not_object",
                r"variants\.0\.defaults\n  Input should be a valid dictionary"
            ),
        ]
    )
    def test_instantiation_from_bad_data_raises_validation_error(
        self,
        all_bad_blocks: Dict[str, Dict[str, Any]],
        block_id: str,
        expected_error_match: str
    ):
        """
        Tests that BlockModel raises ValidationError for various invalid data files.

        Note: This tests Pydantic model validation, not schema validation.
              Files testing for extra properties (e.g., 'blk_extra_property' or
              'blk_meta_extra_property') are correctly omitted here, as they should be
              caught by the schema validator. The default Pydantic model behavior
              is to ignore, not forbid, extra fields.
        """
        assert block_id in all_bad_blocks, f"Bad block fixture '{block_id}' not found."
        invalid_data = all_bad_blocks[block_id]
        
        with pytest.raises(ValidationError, match=expected_error_match):
            BlockModel(**invalid_data)
            
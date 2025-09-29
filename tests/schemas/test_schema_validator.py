# tests/schemas/test_schema_validator.py

import pytest
from typing import Dict, Any, Callable
from unittest.mock import patch

from Prism.schemas.schema_validator import (
    validate_block_file,
    validate_dataschema_file,
    validate_recipe_file,
    is_valid_block_file,
    is_valid_dataschema_file,
    is_valid_recipe_file,
)
from Prism.exceptions import DataValidationError, SchemaFileError

class TestSchemaValidators:
    """
    Tests the high-level validation functions using happypath and badpath fixtures.
    """

    # === Happy Path Tests (No changes needed, existing test is good) ===
    @pytest.mark.parametrize("validator, valid_data_fixture", [
        (validate_block_file, "block_persona"),
        (validate_block_file, "block_task"),
        (validate_dataschema_file, "dataschema_code_input"),
        (validate_recipe_file, "recipe_code_explainer"),
    ])
    def test_validate_functions_on_happypath(
        self, validator: Callable[[Dict[str, Any]], None], valid_data_fixture: str, request: pytest.FixtureRequest
    ):
        """Verify that `validate_*` functions pass for valid data."""
        valid_data = request.getfixturevalue(valid_data_fixture)
        try:
            validator(valid_data)
        except DataValidationError as e:
            pytest.fail(f"Validator {validator.__name__} raised unexpected error for {valid_data_fixture}: {e}")

    # === Bad Path Tests (Refactored and Enhanced) ===
    
    # REFACTORED & ENHANCED: This test now uses the new parametrized fixture and checks error details.
    def test_validate_block_file_on_badpath_provides_detailed_errors(self, bad_block_data: Dict[str, Any]):
        """
        Verify that `validate_block_file` raises a DataValidationError with specific,
        non-empty error messages for each invalid block file.
        """
        with pytest.raises(DataValidationError) as exc_info:
            validate_block_file(bad_block_data)
        
        # NEW: Assert that the error object contains meaningful information.
        assert exc_info.value.errors, "The 'errors' list in the exception should not be empty."
        assert isinstance(exc_info.value.errors[0], str), "Error messages should be strings."
        assert len(exc_info.value.errors[0]) > 0, "Error messages should not be empty."

    # REFACTORED & ENHANCED: Similar improvements for dataschemas.
    def test_validate_dataschema_file_on_badpath_provides_detailed_errors(self, bad_dataschema_data: Dict[str, Any]):
        """Verify `validate_dataschema_file` raises a DataValidationError with detailed errors."""
        with pytest.raises(DataValidationError) as exc_info:
            validate_dataschema_file(bad_dataschema_data)
        
        assert exc_info.value.errors, "The 'errors' list should not be empty."
        assert isinstance(exc_info.value.errors[0], str)

    # REFACTORED & ENHANCED: Similar improvements for recipes.
    def test_validate_recipe_file_on_badpath_provides_detailed_errors(self, bad_recipe_data: Dict[str, Any]):
        """Verify `validate_recipe_file` raises a DataValidationError with detailed errors."""
        with pytest.raises(DataValidationError) as exc_info:
            validate_recipe_file(bad_recipe_data)
        
        assert exc_info.value.errors, "The 'errors' list should not be empty."
        assert isinstance(exc_info.value.errors[0], str)

    # NEW: A specific test to ensure the identifier is captured in the error.
    def test_validate_functions_include_identifier_in_error(self, all_bad_blocks: Dict[str, Any]):
        """
        Verify that if an invalid file has a valid `meta.id`, it's included in the exception.
        This tests the `_safe_get_identifier` helper's integration.
        """
        invalid_data = all_bad_blocks.get("blk_empty_variants")
        assert invalid_data is not None, "Fixture 'blk_empty_variants' not found in all_bad_blocks."
        
        with pytest.raises(DataValidationError) as exc_info:
            validate_block_file(invalid_data)
            
        # 验证 identifier 属性被正确设置
        assert exc_info.value.identifier == "blk_empty_variants"
        
        # 【修复】验证 identifier 的值出现在最终的字符串输出中。
        # 这种检查不依赖于具体的格式（如方括号），因此更加健壮。
        error_string = str(exc_info.value)
        assert exc_info.value.identifier in error_string
        
        # 【可选的更严格检查】我们可以检查 pytest 错误输出中看到的 "identifier=..." 模式
        assert f"identifier={exc_info.value.identifier}" in error_string

    # === Tests for `is_valid_*` functions (Refactored and Enhanced) ===

    # REFACTORED: Simplified happy path test.
    @pytest.mark.parametrize("validator, data_fixture", [
        (is_valid_block_file, "block_persona"),
        (is_valid_dataschema_file, "dataschema_code_input"),
        (is_valid_recipe_file, "recipe_code_explainer"),
    ])
    def test_is_valid_functions_on_happypath(
        self, validator: Callable[[Dict[str, Any]], bool], data_fixture: str, request: pytest.FixtureRequest
    ):
        """Test `is_valid_*` functions return True for valid data."""
        data = request.getfixturevalue(data_fixture)
        assert validator(data) is True

    # REFACTORED & ENHANCED: A much cleaner and more comprehensive bad path test.
    def test_is_valid_block_file_on_badpath(self, bad_block_data: Dict[str, Any]):
        """
        Tests that is_valid_block_file returns False for every invalid block file.
        Pytest will run this test once for each file yielded by the bad_block_data fixture.
        """
        assert is_valid_block_file(bad_block_data) is False

    def test_is_valid_dataschema_file_on_badpath(self, bad_dataschema_data: Dict[str, Any]):
        """
        Tests that is_valid_dataschema_file returns False for every invalid dataschema file.
        """
        assert is_valid_dataschema_file(bad_dataschema_data) is False

    def test_is_valid_recipe_file_on_badpath(self, bad_recipe_data: Dict[str, Any]):
        """
        Tests that is_valid_recipe_file returns False for every invalid recipe file.
        """
        assert is_valid_recipe_file(bad_recipe_data) is False

    # === Robustness Tests (Existing test is good, adding one more for schema loading) ===

    # NEW: Test how validators behave when the underlying schema cannot be loaded.
    @pytest.mark.parametrize("validator, schema_loader_method_str", [
        (validate_block_file, "Prism.schemas.schema_loader.SchemaLoader.get_block_schema"),
        (validate_dataschema_file, "Prism.schemas.schema_loader.SchemaLoader.get_dataschema_schema"),
        (validate_recipe_file, "Prism.schemas.schema_loader.SchemaLoader.get_recipe_schema"),
    ])
    def test_validators_propagate_schema_loading_errors(
        self, validator: Callable, schema_loader_method_str: str, block_persona: Dict[str, Any]
    ):
        """
        Verify that if SchemaLoader fails, the validator propagates the SchemaFileError.
        """
        with patch(schema_loader_method_str, side_effect=SchemaFileError("File is corrupted")):
            with pytest.raises(SchemaFileError, match="File is corrupted"):
                validator(block_persona)

    # Existing test is excellent, keeping it as is.
    @pytest.mark.parametrize("is_valid_func, validate_func_str", [
        (is_valid_block_file, "Prism.schemas.schema_validator.validate_block_file"),
        (is_valid_dataschema_file, "Prism.schemas.schema_validator.validate_dataschema_file"),
        (is_valid_recipe_file, "Prism.schemas.schema_validator.validate_recipe_file"),
    ])
    def test_is_valid_reraises_unexpected_errors(self, is_valid_func, validate_func_str, block_persona):
        """
        Verify that `is_valid_*` functions do not suppress non-validation errors.
        """
        with patch(validate_func_str, side_effect=RuntimeError("Unexpected DB error")):
            with pytest.raises(RuntimeError, match="Unexpected DB error"):
                is_valid_func(block_persona)


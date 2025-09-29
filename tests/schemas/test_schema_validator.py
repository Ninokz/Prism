# tests/schemas/test_schema_validator.py

import pytest
from typing import Dict, Any, Callable
from pathlib import Path
import yaml
from unittest.mock import patch

from Prism.schemas.schema_validator import (
    validate_block_file,
    validate_dataschema_file,
    validate_recipe_file,
    is_valid_block_file,
    is_valid_dataschema_file,
    is_valid_recipe_file,
)
from Prism.exceptions import DataValidationError

# Helper function to load all bad path files for parametrization
def load_badpath_files(badpath_dir: Path, subfolder: str) -> list:
    """Loads all YAML files from a specific badpath subfolder."""
    folder = badpath_dir / subfolder
    params = []
    for filepath in folder.glob("*.yaml"):
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            # Mark each test case with the filename for easier debugging
            params.append(pytest.param(data, id=filepath.name))
    return params

class TestSchemaValidators:
    """
    Tests the high-level validation functions using happypath and badpath fixtures.
    """

    # === Happy Path Tests for `validate_*` functions ===
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

    # === Bad Path Tests for `validate_*` functions ===
    @pytest.mark.parametrize("invalid_data", load_badpath_files(Path("tests/fixtures/badpath"), "blocks"))
    def test_validate_block_file_on_badpath(self, invalid_data: Dict[str, Any]):
        """Verify that `validate_block_file` raises DataValidationError for invalid block data."""
        with pytest.raises(DataValidationError):
            validate_block_file(invalid_data)

    @pytest.mark.parametrize("invalid_data", load_badpath_files(Path("tests/fixtures/badpath"), "dataschemas"))
    def test_validate_dataschema_file_on_badpath(self, invalid_data: Dict[str, Any]):
        """Verify that `validate_dataschema_file` raises DataValidationError for invalid dataschema data."""
        with pytest.raises(DataValidationError):
            validate_dataschema_file(invalid_data)

    @pytest.mark.parametrize("invalid_data", load_badpath_files(Path("tests/fixtures/badpath"), "recipes"))
    def test_validate_recipe_file_on_badpath(self, invalid_data: Dict[str, Any]):
        """Verify that `validate_recipe_file` raises DataValidationError for invalid recipe data."""
        with pytest.raises(DataValidationError):
            validate_recipe_file(invalid_data)

    # === Tests for `is_valid_*` functions ===
    @pytest.mark.parametrize("validator, data_fixture, expected_result", [
        # Happy paths
        (is_valid_block_file, "block_persona", True),
        (is_valid_dataschema_file, "dataschema_code_input", True),
        (is_valid_recipe_file, "recipe_code_explainer", True),
        # Bad paths (sampling one from each category)
        (is_valid_block_file, "badpath_block_missing_meta", False),
        (is_valid_dataschema_file, "badpath_ds_missing_data", False),
        (is_valid_recipe_file, "badpath_rec_missing_imports", False),
    ])
    def test_is_valid_functions(
        self, validator: Callable[[Dict[str, Any]], bool], data_fixture: str, expected_result: bool, request: pytest.FixtureRequest
    ):
        """Test `is_valid_*` functions for both valid and invalid data."""
        data = None
        # We need a way to load badpath fixtures by name, let's create them on the fly
        if data_fixture.startswith("badpath_"):
            # --- START: MODIFIED LOGIC ---
            
            # More robust mapping for file naming conventions
            category_info = {
                "block": {"folder": "blocks", "prefix": "blk_", "suffix": ".block.yaml"},
                "ds": {"folder": "dataschemas", "prefix": "ds_", "suffix": ".dataschema.yaml"},
                "rec": {"folder": "recipes", "prefix": "rec_", "suffix": ".recipe.yaml"}
            }

            parts = data_fixture.split("_") # e.g., ['badpath', 'block', 'missing', 'meta']
            category_key = parts[1]         # e.g., 'block'
            
            if category_key in category_info:
                info = category_info[category_key]
                
                # The rest of the parts form the core filename
                core_name_parts = parts[2:] # e.g., ['missing', 'meta']
                core_name = "_".join(core_name_parts) # e.g., 'missing_meta'

                # Construct the full, correct filename
                filename = f"{info['prefix']}{core_name}{info['suffix']}"
                # e.g., "blk_missing_meta.block.yaml"

                filepath = Path("tests/fixtures/badpath") / info['folder'] / filename
                
                if filepath.exists():
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                else:
                    pytest.fail(f"Badpath fixture file not found at calculated path: {filepath}")
            else:
                pytest.fail(f"Unknown category key '{category_key}' in data_fixture string '{data_fixture}'")

            # --- END: MODIFIED LOGIC ---
        else:
            # Happy path logic remains the same
            data = request.getfixturevalue(data_fixture)
        
        assert data is not None, f"Failed to load data for fixture '{data_fixture}'"
        assert validator(data) == expected_result

    @pytest.mark.parametrize("is_valid_func, validate_func_str", [
        (is_valid_block_file, "Prism.schemas.schema_validator.validate_block_file"),
        (is_valid_dataschema_file, "Prism.schemas.schema_validator.validate_dataschema_file"),
        (is_valid_recipe_file, "Prism.schemas.schema_validator.validate_recipe_file"),
    ])
    def test_is_valid_reraises_unexpected_errors(self, is_valid_func, validate_func_str, block_persona):
        """
        Verify that `is_valid_*` functions do not suppress non-validation errors.
        This is a critical test for robustness.
        """
        with patch(validate_func_str, side_effect=RuntimeError("Unexpected DB error")):
            with pytest.raises(RuntimeError, match="Unexpected DB error"):
                is_valid_func(block_persona)


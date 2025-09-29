# tests/model/test_bad_data_instantiation.py

import pytest
from pydantic import ValidationError

from Prism.models.recipe import RecipeModel
from Prism.models.block import BlockModel
from Prism.models.dataschema import DataschemaModel
from Prism.exceptions import ModelError

class TestModelInstantiationWithBadData:

    def test_recipe_model_instantiation_fails_with_bad_data(self, bad_recipe_data):
        """
        验证所有 'badpath/recipes' 下的文件都无法成功实例化为 RecipeModel。
        """
        if "_error" in bad_recipe_data:
            pytest.skip(f"Skipping unparsable fixture: {bad_recipe_data['_error']}")

        with pytest.raises((ValidationError, ModelError)):
            RecipeModel(**bad_recipe_data)

    def test_block_model_instantiation_fails_with_bad_data(self, bad_block_data):
        """
        验证所有 'badpath/blocks' 下的文件都无法成功实例化为 BlockModel。
        """
        if "_error" in bad_block_data:
            pytest.skip(f"Skipping unparsable fixture: {bad_block_data['_error']}")

        with pytest.raises(ValidationError):
            BlockModel(**bad_block_data)

    def test_dataschema_model_instantiation_fails_with_bad_data(self, bad_dataschema_data):
        """
        验证所有 'badpath/dataschemas' 下的文件都无法成功实例化为 DataschemaModel。
        """
        if "_error" in bad_dataschema_data:
            pytest.skip(f"Skipping unparsable fixture: {bad_dataschema_data['_error']}")

        with pytest.raises(ValidationError):
            DataschemaModel(**bad_dataschema_data)

# tests/model/test_recipe.py

import pytest
from pydantic import ValidationError
from typing import Dict, Any

from Prism.models.recipe import (
    ImportRef,
    ImportsModel,
    SequenceItem,
    CompositionModel,
    RecipeModel
)
from Prism.models.base import MetaModel
from Prism.exceptions import ModelError

class TestImportRef:
    """Tests for the ImportRef model."""

    def test_instantiation(self):
        """Test successful instantiation with valid data."""
        data = {"block_id": "blk_task", "variant_id": "explain_code"}
        ref = ImportRef(**data)
        assert ref.block_id == "blk_task"
        assert ref.variant_id == "explain_code"

    @pytest.mark.parametrize("missing_field", ["block_id", "variant_id"])
    def test_missing_required_fields(self, missing_field: str):
        """Test that ValidationError is raised if required fields are missing."""
        data = {"block_id": "blk_task", "variant_id": "explain_code"}
        del data[missing_field]
        with pytest.raises(ValidationError, match=f"{missing_field}\n  Field required"):
            ImportRef(**data)

class TestImportsModel:
    """Tests for the ImportsModel."""

    def test_instantiation_from_full_data(self, recipe_code_explainer: Dict[str, Any]):
        """Test instantiation with a complete set of import data from a fixture."""
        imports_data = recipe_code_explainer["imports"]
        imports = ImportsModel(**imports_data)

        # Test single instance fields
        assert isinstance(imports.persona, ImportRef)
        assert imports.persona.block_id == "blk_persona"
        assert imports.persona.variant_id == "expert_teacher"

        assert isinstance(imports.output_spec, ImportRef)
        assert imports.output_spec.block_id == "blk_output"
        assert imports.output_spec.variant_id == "json_detailed"

        # Test multi-instance fields
        assert isinstance(imports.tasks, list)
        assert len(imports.tasks) == 1
        assert isinstance(imports.tasks[0], ImportRef)
        assert imports.tasks[0].block_id == "blk_task"
        assert imports.tasks[0].variant_id == "explain_code"

        # Test fields that are not present in the data, should default to empty lists
        assert imports.rules == []
        assert imports.examples == []
        assert imports.contexts == []

    def test_instantiation_from_partial_data(self):
        """Test instantiation with only a subset of possible fields."""
        partial_data = {
            "tasks": [{"block_id": "b1", "variant_id": "v1"}],
            "rules": [{"block_id": "b2", "variant_id": "v2"}]
        }
        imports = ImportsModel(**partial_data)  # type: ignore

        assert imports.persona is None
        assert imports.output_spec is None
        assert len(imports.tasks) == 1
        assert len(imports.rules) == 1
        assert imports.examples == []
        assert imports.contexts == []

class TestSequenceItem:
    """Tests for the SequenceItem model, especially its exclusive fields validation."""

    def test_instantiation_with_block_ref(self):
        """Test successful creation with only 'block_ref'."""
        item = SequenceItem(block_ref="persona")
        assert item.block_ref == "persona"
        assert item.literal is None

    def test_instantiation_with_literal(self):
        """Test successful creation with only 'literal'."""
        item = SequenceItem(literal="\n---\n")
        assert item.literal == "\n---\n"
        assert item.block_ref is None

    def test_raises_error_when_both_fields_present(self):
        """Test that ModelError is raised if both 'block_ref' and 'literal' are provided."""
        with pytest.raises(ModelError) as exc_info:
            SequenceItem(block_ref="persona", literal="\n---\n")
        assert "Must provide exactly one of 'block_ref' or 'literal'" in str(exc_info.value)

    def test_raises_error_when_no_fields_present(self):
        """Test that ModelError is raised if neither field is provided."""
        with pytest.raises(ModelError) as exc_info:
            SequenceItem()
        assert "Must provide exactly one of 'block_ref' or 'literal'" in str(exc_info.value)

class TestRecipeModel:
    """Tests for the top-level RecipeModel."""

    def test_instantiation_from_valid_data(self, recipe_code_explainer: Dict[str, Any]):
        """Test successful instantiation of a full RecipeModel from fixture data."""
        recipe = RecipeModel(**recipe_code_explainer)

        # Test Identifiable property
        assert recipe.id == "rec_code_explainer"

        # Test nested model types
        assert isinstance(recipe, RecipeModel)
        assert isinstance(recipe.meta, MetaModel)
        assert isinstance(recipe.imports, ImportsModel)
        assert isinstance(recipe.composition, CompositionModel)

        # Test meta content
        assert recipe.meta.name == "Code Explainer Prompt Recipe"

        # Test composition content
        assert isinstance(recipe.composition.sequence, list)
        assert len(recipe.composition.sequence) == 5

        # Spot-check a few sequence items
        first_item = recipe.composition.sequence[0]
        assert isinstance(first_item, SequenceItem)
        assert first_item.block_ref == "persona"
        assert first_item.literal is None

        second_item = recipe.composition.sequence[1]
        assert isinstance(second_item, SequenceItem)
        assert second_item.literal == "\n\n---\n\n"
        assert second_item.block_ref is None

    def test_composition_sequence_parsing(self, recipe_code_explainer: Dict[str, Any]):
        """Verify all items in the composition sequence are parsed correctly."""
        recipe = RecipeModel(**recipe_code_explainer)
        sequence = recipe.composition.sequence

        expected_sequence = [
            ("block_ref", "persona"),
            ("literal", "\n\n---\n\n"),
            ("block_ref", "tasks[0]"),
            ("literal", "\n\n### REQUIRED OUTPUT FORMAT\n"),
            ("block_ref", "output_spec"),
        ]

        assert len(sequence) == len(expected_sequence)

        for i, (expected_type, expected_value) in enumerate(expected_sequence):
            item = sequence[i]
            if expected_type == "block_ref":
                assert item.block_ref == expected_value
                assert item.literal is None
            else: # literal
                assert item.literal == expected_value
                assert item.block_ref is None

    @pytest.mark.parametrize("missing_field", ["meta", "imports", "composition"])
    def test_missing_top_level_fields(self, recipe_code_explainer: Dict[str, Any], missing_field: str):
        """Test that ValidationError is raised if top-level required fields are missing."""
        invalid_data = recipe_code_explainer.copy()
        del invalid_data[missing_field]
        
        with pytest.raises(ValidationError, match=f"{missing_field}\n  Field required"):
            RecipeModel(**invalid_data)


class TestRecipeModelValidationFromBadFixtures:
    """
    通过尝试解析 'badpath' fixtures 中的文件，
    测试 RecipeModel 拒绝无效数据结构的能力。
    """

    @pytest.mark.parametrize(
        "bad_recipe_id, expected_exception, expected_message_part",
        [
            # --- 原有的测试用例 ---
            (
                "rec_missing_imports", 
                ValidationError, 
                "imports\n  Field required"
            ),
            (
                "rec_import_missing_variant_id", 
                ValidationError, 
                "imports.persona.variant_id\n  Field required"
            ),
            (
                # 测试 SequenceItem 中的自定义验证器，它会引发 ModelError
                "rec_sequence_ambiguous_item", 
                ModelError, 
                "Must provide exactly one of 'block_ref' or 'literal'"
            ),
            (
                # 同样测试自定义验证器
                "rec_sequence_empty_item", 
                ModelError, 
                "Must provide exactly one of 'block_ref' or 'literal'"
            ),
            
            # --- 新增的测试用例 ---
            (
                # 测试 'persona' import 不是一个对象
                "rec_import_persona_not_object",
                ValidationError,
                "imports.persona\n  Input should be a valid dictionary"
            ),
            (
                # 测试 'tasks' import 不是一个数组/列表
                "rec_import_tasks_not_array",
                ValidationError,
                "imports.tasks\n  Input should be a valid list"
            ),
            (
                # 测试 'tasks' 数组中的项不是一个对象
                "rec_import_tasks_item_not_object",
                ValidationError,
                "imports.tasks.0\n  Input should be a valid dictionary"
            ),
            (
                # 测试 'composition.sequence' 不是一个数组/列表
                "rec_sequence_not_array",
                ValidationError,
                "composition.sequence\n  Input should be a valid list"
            ),
            (
                # 测试 sequence 项中的 'block_ref' 值不是字符串
                "rec_sequence_block_ref_not_string",
                ValidationError,
                "composition.sequence.0.block_ref\n  Input should be a valid string"
            ),
            (
                # 测试 sequence 项中的 'literal' 值不是字符串
                "rec_sequence_literal_not_string",
                ValidationError,
                "composition.sequence.0.literal\n  Input should be a valid string"
            ),
        ]
    )
    def test_bad_recipe_data_raises_appropriate_error(
        self,
        bad_recipe_id: str,
        expected_exception: type,
        expected_message_part: str,
        all_bad_recipes: Dict[str, Dict[str, Any]]
    ):
        """
        验证特定的无效 recipe 文件在被 RecipeModel 解析时，
        是否会引发正确的异常并附带信息丰富的错误消息。
        """
        # 获取对应的无效数据
        bad_data = all_bad_recipes[bad_recipe_id]

        # 断言在尝试用无效数据实例化模型时会抛出预期的异常
        with pytest.raises(expected_exception) as exc_info:
            RecipeModel(**bad_data)

        # 断言异常信息中包含我们期望的关键内容，以确保错误是可追溯的
        assert expected_message_part in str(exc_info.value)

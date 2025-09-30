# tests/compiler/test_recipe_compiler.py

import pytest
from typing import Dict, Any
import copy
from Prism.compiler.recipe_compiler import RecipeCompiler
from Prism.models.recipe import RecipeModel
from Prism.models.ir import IRModel, ResolvedBlock, LiteralContent
from Prism.exceptions import ModelError, ModelNotFoundError

# ===================================================================
#
#                       HAPPY PATH TESTS
#
# ===================================================================

class TestRecipeCompilerHappyPath:
    """
    使用 'happypath' 数据进行集成测试，验证编译器的端到端正确性。
    """

    def test_compile_code_explainer_recipe(
        self,
        recipe_compiler: RecipeCompiler,
        recipe_code_explainer: Dict[str, Any]
    ):
        """
        测试编译一个完整的、有效的 recipe ('rec_code_explainer.recipe.yaml')。
        这是最重要的 happy path 测试。
        """
        # --- Arrange ---
        recipe_model = RecipeModel(**recipe_code_explainer)

        # --- Act ---
        ir = recipe_compiler.compile(recipe_model)

        # --- Assert ---
        assert isinstance(ir, IRModel)

        # 1. 验证源元数据
        assert ir.source_recipe_meta.id == "rec_code_explainer"
        assert ir.source_recipe_meta.name == "Code Explainer Prompt Recipe"

        # 2. 验证渲染序列 (Render Sequence)
        assert len(ir.render_sequence) == 5
        
        # Item 0: persona (ResolvedBlock)
        persona_block = ir.render_sequence[0]
        assert isinstance(persona_block, ResolvedBlock)
        assert persona_block.source_ref == "persona"
        assert persona_block.source_block_meta.id == "blk_persona"
        assert persona_block.source_variant_id == "expert_teacher"
        assert "You are an expert" in persona_block.template_content
        assert persona_block.runtime_contract is None  # Persona block has no contract
        # 验证默认值合并：Variant 的 "TypeScript" 覆盖了 Block 的 "JavaScript"
        assert persona_block.merged_defaults["language"] == "TypeScript"
        assert persona_block.merged_defaults["teaching_tone"] == "strict"

        # Item 1: literal (LiteralContent)
        literal1 = ir.render_sequence[1]
        assert isinstance(literal1, LiteralContent)
        assert literal1.content == "\n\n---\n\n"

        # Item 2: tasks[0] (ResolvedBlock)
        task_block = ir.render_sequence[2]
        assert isinstance(task_block, ResolvedBlock)
        assert task_block.source_ref == "tasks[0]"
        assert task_block.source_block_meta.id == "blk_task"
        assert "Your task is to explain" in task_block.template_content
        assert task_block.runtime_contract is not None
        assert task_block.runtime_contract.id == "ds_code_input"
        assert task_block.merged_defaults == {} # Task block has no defaults

        # Item 3: literal (LiteralContent)
        literal2 = ir.render_sequence[3]
        assert isinstance(literal2, LiteralContent)
        assert literal2.content == "\n\n### REQUIRED OUTPUT FORMAT\n"

        # Item 4: output_spec (ResolvedBlock)
        output_block = ir.render_sequence[4]
        assert isinstance(output_block, ResolvedBlock)
        assert output_block.source_ref == "output_spec"
        assert output_block.source_block_meta.id == "blk_output"
        assert "Format your response as a single, valid JSON object" in output_block.template_content
        assert output_block.runtime_contract is None
        assert output_block.merged_defaults["confidence_score_default"] == 0.95

        # 3. 验证聚合的数据契约 (Aggregated Contracts)
        assert len(ir.aggregated_contracts) == 1
        assert "ds_code_input" in ir.aggregated_contracts
        contract = ir.aggregated_contracts["ds_code_input"]
        assert contract.meta.name == "Code Input Schema"
        assert "user_code" in contract.data["required"]

# ===================================================================
#
#                  LOGIC & ERROR HANDLING TESTS
#
# ===================================================================

class TestCompilerLogicAndErrors:
    """
    测试编译器的内部逻辑、边缘情况和错误处理能力。
    """

    def test_expand_block_ref_logic(self, recipe_compiler: RecipeCompiler):
        """
        单元测试 _expand_block_ref 方法的各种情况。
        """
        available_refs = ["persona", "tasks[0]", "tasks[1]", "tasks[10]", "tasks[2]"]
        
        # Case 1: 精确匹配
        assert recipe_compiler._expand_block_ref("persona", available_refs) == ["persona"]
        assert recipe_compiler._expand_block_ref("tasks[1]", available_refs) == ["tasks[1]"]
        
        # Case 2: 展开复数形式，并验证自然排序
        expanded_tasks = recipe_compiler._expand_block_ref("tasks", available_refs)
        assert expanded_tasks == ["tasks[0]", "tasks[1]", "tasks[2]", "tasks[10]"]

        # Case 3: 引用不存在的复数形式
        assert recipe_compiler._expand_block_ref("rules", available_refs) == ["rules"]

    def test_error_on_composition_ref_not_in_imports(
        self,
        recipe_compiler: RecipeCompiler,
        recipe_code_explainer: Dict[str, Any]
    ):
        """
        测试当 composition.sequence 引用一个未在 imports 中定义的 block_ref 时，
        是否会抛出 ModelError。
        """
        # --- Arrange ---
        # 使用 deepcopy 保证数据隔离
        bad_recipe_data = copy.deepcopy(recipe_code_explainer)
        bad_recipe_data["composition"]["sequence"].append({"block_ref": "non_existent_ref"})
        recipe_model = RecipeModel(**bad_recipe_data)

        # --- Act & Assert ---
        with pytest.raises(ModelError) as exc_info:
            recipe_compiler.compile(recipe_model)
        
        assert "non_existent_ref" in str(exc_info.value)
        assert "未在 imports 中定义" in str(exc_info.value) or "not defined in imports" in str(exc_info.value).lower()

    def test_error_on_import_referencing_non_existent_block(
        self,
        recipe_compiler: RecipeCompiler,
        recipe_code_explainer: Dict[str, Any]
    ):
        """
        测试当 imports 引用一个不存在的 block_id 时，是否会抛出异常。
        这个异常应该来自 Resolver。
        """
        # --- Arrange ---
        # 使用 deepcopy 保证数据隔离
        bad_recipe_data = copy.deepcopy(recipe_code_explainer)
        bad_recipe_data["imports"]["persona"]["block_id"] = "non_existent_block"
        recipe_model = RecipeModel(**bad_recipe_data)

        # --- Act & Assert ---
        # Resolver 抛出的是 ModelNotFoundError，消息格式为 "Block with identifier 'xxx' not found."
        with pytest.raises(ModelNotFoundError, match="Block with identifier 'non_existent_block' not found."):
            recipe_compiler.compile(recipe_model)

    def test_error_on_import_referencing_non_existent_variant(
        self,
        recipe_compiler: RecipeCompiler,
        recipe_code_explainer: Dict[str, Any]
    ):
        """
        测试当 imports 引用一个存在的 block 但不存在的 variant_id 时，
        是否会抛出 ModelError。
        """
        # --- Arrange ---
        # 使用 deepcopy 保证数据隔离
        bad_recipe_data = copy.deepcopy(recipe_code_explainer)
        bad_recipe_data["imports"]["persona"]["variant_id"] = "non_existent_variant"
        recipe_model = RecipeModel(**bad_recipe_data)
        
        # --- Act & Assert ---
        with pytest.raises(ModelError) as exc_info:
            recipe_compiler.compile(recipe_model)

        # 现在这个测试应该会按预期工作
        assert "non_existent_variant" in str(exc_info.value)
        assert "blk_persona" in str(exc_info.value)
        assert "未找到" in str(exc_info.value) or "not found" in str(exc_info.value).lower()
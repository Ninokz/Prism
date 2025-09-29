import pytest
import yaml
from pathlib import Path
from typing import Dict, Any


class TestFixturesLoading:
    """测试所有 fixture 的文件加载功能"""
    
    def test_fixtures_dir_exists(self, fixtures_dir: Path):
        """测试 fixtures 目录是否存在"""
        assert fixtures_dir.exists(), f"Fixtures directory does not exist: {fixtures_dir}"
        assert fixtures_dir.is_dir(), f"Fixtures path is not a directory: {fixtures_dir}"
    
    def test_subdirectories_exist(self, templates_dir: Path, blocks_dir: Path, 
                                 dataschemas_dir: Path, recipes_dir: Path):
        """测试所有子目录是否存在"""
        directories = {
            "templates": templates_dir,
            "blocks": blocks_dir,
            "dataschemas": dataschemas_dir,
            "recipes": recipes_dir
        }
        
        for name, dir_path in directories.items():
            assert dir_path.exists(), f"{name} directory does not exist: {dir_path}"
            assert dir_path.is_dir(), f"{name} path is not a directory: {dir_path}"
    
    # ================================
    # Template Loading Tests
    # ================================
    
    def test_template_persona_expert_loading(self, template_persona_expert: str):
        """测试 persona expert 模板加载"""
        assert template_persona_expert is not None
        assert len(template_persona_expert.strip()) > 0
        # 验证模板包含预期的 Jinja2 变量
        assert "{{ language }}" in template_persona_expert
        assert "{{ teaching_tone }}" in template_persona_expert
        assert "expert" in template_persona_expert.lower()
    
    def test_template_task_explain_code_loading(self, template_task_explain_code: str):
        """测试 task explain code 模板加载"""
        assert template_task_explain_code is not None
        assert len(template_task_explain_code.strip()) > 0
        # 验证模板包含预期的 Jinja2 变量
        assert "{{ user_code }}" in template_task_explain_code
        assert "explain" in template_task_explain_code.lower()
    
    def test_template_output_json_loading(self, template_output_json: str):
        """测试 output JSON 模板加载"""
        assert template_output_json is not None
        assert len(template_output_json.strip()) > 0
        # 验证模板包含预期的内容
        assert "{{ confidence_score_default }}" in template_output_json
        assert "JSON" in template_output_json
        assert "explanation" in template_output_json
        assert "language_detected" in template_output_json
        assert "confidence_score" in template_output_json
    
    def test_all_templates_loading(self, all_templates: Dict[str, str]):
        """测试批量模板加载"""
        expected_templates = {
            "tpl_persona_expert",
            "tpl_task_explain_code", 
            "tpl_output_json"
        }
        
        assert set(all_templates.keys()) == expected_templates
        
        # 验证每个模板都有内容
        for template_id, content in all_templates.items():
            assert content is not None, f"Template {template_id} is None"
            assert len(content.strip()) > 0, f"Template {template_id} is empty"
    
    # ================================
    # DataSchema Loading Tests
    # ================================
    
    def test_dataschema_code_input_loading(self, dataschema_code_input: Dict[str, Any]):
        """测试 code input dataschema 加载"""
        assert dataschema_code_input is not None
        assert isinstance(dataschema_code_input, dict)
        
        # 验证结构
        assert "meta" in dataschema_code_input
        assert "data" in dataschema_code_input
        
        # 验证 meta 信息
        meta = dataschema_code_input["meta"]
        assert meta["id"] == "ds_code_input"
        assert meta["name"] == "Code Input Schema"
        
        # 验证 data schema 结构
        data_schema = dataschema_code_input["data"]
        assert data_schema["type"] == "object"
        assert "user_code" in data_schema["required"]
        assert "user_code" in data_schema["properties"]
        assert data_schema["properties"]["user_code"]["type"] == "string"
    
    def test_all_dataschemas_loading(self, all_dataschemas: Dict[str, Dict[str, Any]]):
        """测试批量 dataschema 加载"""
        # 至少应该包含我们知道的数据模式
        assert "ds_code_input" in all_dataschemas
        
        # 验证每个数据模式都有正确的结构
        for schema_id, schema_content in all_dataschemas.items():
            assert isinstance(schema_content, dict), f"Schema {schema_id} is not a dict"
            assert "meta" in schema_content, f"Schema {schema_id} missing 'meta'"
            assert "data" in schema_content, f"Schema {schema_id} missing 'data'"
            
            # 验证 meta 结构
            meta = schema_content["meta"]
            assert "id" in meta, f"Schema {schema_id} meta missing 'id'"
            assert "name" in meta, f"Schema {schema_id} meta missing 'name'"
    
    # ================================
    # Block Loading Tests
    # ================================
    
    def test_block_persona_loading(self, block_persona: Dict[str, Any]):
        """测试 persona block 加载"""
        assert block_persona is not None
        assert isinstance(block_persona, dict)
        
        # 验证基本结构
        assert "meta" in block_persona
        assert "block_type" in block_persona
        assert "variants" in block_persona
        
        # 验证 meta 信息
        meta = block_persona["meta"]
        assert meta["id"] == "blk_persona"
        assert meta["name"] == "AI Persona Definitions"
        
        # 验证 block 类型
        assert block_persona["block_type"] == "Persona"
        
        # 验证 variants 结构
        variants = block_persona["variants"]
        assert len(variants) == 1
        assert variants[0]["id"] == "expert_teacher"
        assert "template_id" in variants[0]
        assert variants[0]["template_id"] == "tpl_persona_expert"
    
    def test_block_task_loading(self, block_task: Dict[str, Any]):
        """测试 task block 加载"""
        assert block_task is not None
        assert isinstance(block_task, dict)
        
        # 验证基本结构
        assert "meta" in block_task
        assert block_task["meta"]["id"] == "blk_task"
        assert block_task["block_type"] == "Task"
        
        # 验证 variants 结构
        variants = block_task["variants"]
        assert len(variants) == 1
        variant = variants[0]
        assert variant["id"] == "explain_code"
        assert variant["template_id"] == "tpl_task_explain_code"
        assert variant["contract_id"] == "ds_code_input"
    
    def test_block_output_loading(self, block_output: Dict[str, Any]):
        """测试 output block 加载"""
        assert block_output is not None
        assert isinstance(block_output, dict)
        
        # 验证基本结构
        assert "meta" in block_output
        assert block_output["meta"]["id"] == "blk_output"
        assert block_output["block_type"] == "OutputSpecification"
        
        # 验证 variants 结构
        variants = block_output["variants"]
        assert len(variants) == 1
        variant = variants[0]
        assert variant["id"] == "json_detailed"
        assert variant["template_id"] == "tpl_output_json"
        assert "defaults" in variant
        assert variant["defaults"]["confidence_score_default"] == 0.95
    
    def test_all_blocks_loading(self, all_blocks: Dict[str, Dict[str, Any]]):
        """测试批量 block 加载"""
        # 定义我们期望必须存在的核心 block 文件
        core_blocks = {"blk_persona", "blk_task", "blk_output"}
        
        # 断言核心 block 集合是实际加载的 block 集合的子集
        # 这意味着只要核心文件都在，即使有更多文件也不会导致测试失败
        assert core_blocks.issubset(set(all_blocks.keys()))
        
        # 验证每个 block 都有正确的结构
        for block_id, block_content in all_blocks.items():
            assert isinstance(block_content, dict), f"Block {block_id} is not a dict"
            assert "meta" in block_content, f"Block {block_id} missing 'meta'"
            assert "block_type" in block_content, f"Block {block_id} missing 'block_type'"
            assert "variants" in block_content, f"Block {block_id} missing 'variants'"
            
            # 验证 meta 结构
            meta = block_content["meta"]
            # 这个断言仍然非常重要，它确保了文件名和文件内容的id是一致的
            assert meta["id"] == block_id, f"Block {block_id} meta.id mismatch"
    
    # ================================
    # Recipe Loading Tests
    # ================================
    
    def test_recipe_code_explainer_loading(self, recipe_code_explainer: Dict[str, Any]):
        """测试 code explainer recipe 加载"""
        assert recipe_code_explainer is not None
        assert isinstance(recipe_code_explainer, dict)
        
        # 验证基本结构
        assert "meta" in recipe_code_explainer
        assert "imports" in recipe_code_explainer
        assert "composition" in recipe_code_explainer
        
        # 验证 meta 信息
        meta = recipe_code_explainer["meta"]
        assert meta["id"] == "rec_code_explainer"
        assert meta["name"] == "Code Explainer Prompt Recipe"
        
        # 验证 imports 结构
        imports = recipe_code_explainer["imports"]
        assert "persona" in imports
        assert "output_spec" in imports
        assert "tasks" in imports
        
        # 验证 composition 结构
        composition = recipe_code_explainer["composition"]
        assert "sequence" in composition
        sequence = composition["sequence"]
        assert len(sequence) == 5  # persona + literal + task + literal + output_spec
    
    def test_all_recipes_loading(self, all_recipes: Dict[str, Dict[str, Any]]):
        """测试批量 recipe 加载"""
        assert "rec_code_explainer" in all_recipes
        
        # 验证每个 recipe 都有正确的结构
        for recipe_id, recipe_content in all_recipes.items():
            assert isinstance(recipe_content, dict), f"Recipe {recipe_id} is not a dict"
            assert "meta" in recipe_content, f"Recipe {recipe_id} missing 'meta'"
            assert "imports" in recipe_content, f"Recipe {recipe_id} missing 'imports'"
            assert "composition" in recipe_content, f"Recipe {recipe_id} missing 'composition'"
            
            # 验证 meta 结构
            meta = recipe_content["meta"]
            assert meta["id"] == recipe_id, f"Recipe {recipe_id} meta.id mismatch"
    
    # ================================
    # Complete Fixture Set Tests
    # ================================
    
    def test_complete_fixture_set(self, complete_fixture_set: Dict[str, Any]):
        """测试完整的 fixture 集合"""
        expected_keys = {"templates", "dataschemas", "blocks", "recipes"}
        assert set(complete_fixture_set.keys()) == expected_keys
        
        # 验证每个部分都不为空
        for key, value in complete_fixture_set.items():
            assert isinstance(value, dict), f"{key} is not a dict"
            assert len(value) > 0, f"{key} is empty"
    
    def test_temp_fixture_files(self, temp_fixture_files: Dict[str, Path]):
        """测试临时文件创建功能"""
        expected_dirs = {"templates", "dataschemas", "blocks", "recipes"}
        assert set(temp_fixture_files.keys()) == expected_dirs
        
        # 验证每个目录都存在且包含文件
        for dir_name, dir_path in temp_fixture_files.items():
            assert dir_path.exists(), f"Temp dir {dir_name} does not exist"
            assert dir_path.is_dir(), f"Temp path {dir_name} is not a directory"
            
            # 检查目录不为空
            files = list(dir_path.iterdir())
            assert len(files) > 0, f"Temp dir {dir_name} is empty"


class TestFixturesContent:
    """测试 fixture 内容的正确性和一致性"""
    
    def test_template_variable_consistency(self, all_templates: Dict[str, str], all_blocks: Dict[str, Dict[str, Any]]):
        """测试模板变量与 block defaults 的一致性"""
        # 检查 persona 模板
        persona_template = all_templates["tpl_persona_expert"]
        persona_block = all_blocks["blk_persona"]
        
        # persona 模板中使用的变量应该在 block defaults 中定义
        expected_vars = {"language", "teaching_tone"}
        for var in expected_vars:
            assert f"{{{{ {var} }}}}" in persona_template, f"Variable {var} not found in persona template"
        
        # 检查 block 的 defaults 或 variant defaults 中是否定义了这些变量
        variant = persona_block["variants"][0]
        if "defaults" in variant:
            defaults = variant["defaults"]
        else:
            defaults = persona_block.get("defaults", {})
        
        # 至少应该有一些默认值定义
        assert len(defaults) > 0, "No defaults found in persona block"
    
    def test_block_template_id_references(self, all_blocks: Dict[str, Dict[str, Any]], all_templates: Dict[str, str]):
        """测试 block 中的 template_id 引用是否存在对应的模板"""
        for block_id, block_content in all_blocks.items():
            for variant in block_content["variants"]:
                template_id = variant["template_id"]
                assert template_id in all_templates, f"Template {template_id} referenced by {block_id} not found"
    
    def test_block_contract_id_references(self, all_blocks: Dict[str, Dict[str, Any]], all_dataschemas: Dict[str, Dict[str, Any]]):
        """测试 block 中的 contract_id 引用是否存在对应的数据模式"""
        for block_id, block_content in all_blocks.items():
            for variant in block_content["variants"]:
                if "contract_id" in variant:
                    contract_id = variant["contract_id"]
                    assert contract_id in all_dataschemas, f"DataSchema {contract_id} referenced by {block_id} not found"
    
    def test_recipe_import_references(self, all_recipes: Dict[str, Dict[str, Any]], all_blocks: Dict[str, Dict[str, Any]]):
        """测试 recipe 中的 import 引用是否存在对应的 block"""
        for recipe_id, recipe_content in all_recipes.items():
            imports = recipe_content["imports"]
            
            # 检查每个 import
            for import_name, import_config in imports.items():
                if isinstance(import_config, dict) and "block_id" in import_config:
                    block_id = import_config["block_id"]
                    assert block_id in all_blocks, f"Block {block_id} imported by {recipe_id} not found"
                    
                    # 如果指定了 variant_id，检查是否存在
                    if "variant_id" in import_config:
                        variant_id = import_config["variant_id"]
                        block = all_blocks[block_id]
                        variant_ids = [v["id"] for v in block["variants"]]
                        assert variant_id in variant_ids, f"Variant {variant_id} of block {block_id} not found"
                elif isinstance(import_config, list):
                    # 处理数组形式的 import
                    for item in import_config:
                        if isinstance(item, dict) and "block_id" in item:
                            block_id = item["block_id"]
                            assert block_id in all_blocks, f"Block {block_id} imported by {recipe_id} not found"

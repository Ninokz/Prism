import pytest
import yaml
from pathlib import Path
from typing import Dict, Any, List
import os


# 获取测试目录的绝对路径
TEST_DIR = Path(__file__).parent
FIXTURES_DIR = TEST_DIR / "fixtures"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """提供 fixtures 目录路径"""
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def templates_dir(fixtures_dir: Path) -> Path:
    """提供模板文件目录路径"""
    return fixtures_dir / "templates"


@pytest.fixture(scope="session")
def blocks_dir(fixtures_dir: Path) -> Path:
    """提供 blocks 文件目录路径"""
    return fixtures_dir / "blocks"


@pytest.fixture(scope="session")
def dataschemas_dir(fixtures_dir: Path) -> Path:
    """提供 dataschemas 文件目录路径"""
    return fixtures_dir / "dataschemas"


@pytest.fixture(scope="session")
def recipes_dir(fixtures_dir: Path) -> Path:
    """提供 recipes 文件目录路径"""
    return fixtures_dir / "recipes"


def _load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """通用的 YAML 文件加载函数"""
    if not file_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _load_text_file(file_path: Path) -> str:
    """通用的文本文件加载函数"""
    if not file_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# ================================
# Template Fixtures
# ================================

@pytest.fixture(scope="session")
def template_persona_expert(templates_dir: Path) -> str:
    """加载 tpl_persona_expert.jinja 模板内容"""
    return _load_text_file(templates_dir / "tpl_persona_expert.jinja")


@pytest.fixture(scope="session")
def template_task_explain_code(templates_dir: Path) -> str:
    """加载 tpl_task_explain_code.jinja 模板内容"""
    return _load_text_file(templates_dir / "tpl_task_explain_code.jinja")


@pytest.fixture(scope="session")
def template_output_json(templates_dir: Path) -> str:
    """加载 tpl_output_json.jinja 模板内容"""
    return _load_text_file(templates_dir / "tpl_output_json.jinja")


@pytest.fixture(scope="session")
def all_templates(templates_dir: Path) -> Dict[str, str]:
    """加载所有模板文件，返回模板ID到内容的映射"""
    templates = {}
    
    template_files = {
        "tpl_persona_expert": "tpl_persona_expert.jinja",
        "tpl_task_explain_code": "tpl_task_explain_code.jinja",
        "tpl_output_json": "tpl_output_json.jinja"
    }
    
    for template_id, filename in template_files.items():
        templates[template_id] = _load_text_file(templates_dir / filename)
    
    return templates


# ================================
# DataSchema Fixtures
# ================================

@pytest.fixture(scope="session")
def dataschema_code_input(dataschemas_dir: Path) -> Dict[str, Any]:
    """加载 ds_code_input.dataschema.yaml"""
    return _load_yaml_file(dataschemas_dir / "ds_code_input.dataschema.yaml")


@pytest.fixture(scope="session")
def all_dataschemas(dataschemas_dir: Path) -> Dict[str, Dict[str, Any]]:
    """加载所有数据模式文件，返回模式ID到内容的映射"""
    dataschemas = {}
    
    # 扫描目录中的所有 .dataschema.yaml 文件
    for file_path in dataschemas_dir.glob("*.dataschema.yaml"):
        # 从文件名提取 ID（去掉 .dataschema.yaml 后缀）
        schema_id = file_path.stem.replace(".dataschema", "")
        dataschemas[schema_id] = _load_yaml_file(file_path)
    
    return dataschemas


# ================================
# Block Fixtures
# ================================

@pytest.fixture(scope="session")
def block_persona(blocks_dir: Path) -> Dict[str, Any]:
    """加载 blk_persona.block.yaml"""
    return _load_yaml_file(blocks_dir / "blk_persona.block.yaml")


@pytest.fixture(scope="session")
def block_task(blocks_dir: Path) -> Dict[str, Any]:
    """加载 blk_task.block.yaml"""
    return _load_yaml_file(blocks_dir / "blk_task.block.yaml")


@pytest.fixture(scope="session")
def block_output(blocks_dir: Path) -> Dict[str, Any]:
    """加载 blk_output.block.yaml"""
    return _load_yaml_file(blocks_dir / "blk_output.block.yaml")


@pytest.fixture(scope="session")
def all_blocks(blocks_dir: Path) -> Dict[str, Dict[str, Any]]:
    """加载所有 Block 文件，返回 Block ID 到内容的映射"""
    blocks = {}
    
    # 扫描目录中的所有 .block.yaml 文件
    for file_path in blocks_dir.glob("*.block.yaml"):
        # 从文件名提取 ID（去掉 .block.yaml 后缀）
        block_id = file_path.stem.replace(".block", "")
        blocks[block_id] = _load_yaml_file(file_path)
    
    return blocks


# ================================
# Recipe Fixtures
# ================================

@pytest.fixture(scope="session")
def recipe_code_explainer(recipes_dir: Path) -> Dict[str, Any]:
    """加载 rec_code_explainer.recipe.yaml"""
    return _load_yaml_file(recipes_dir / "rec_code_explainer.recipe.yaml")


@pytest.fixture(scope="session")
def all_recipes(recipes_dir: Path) -> Dict[str, Dict[str, Any]]:
    """加载所有 Recipe 文件，返回 Recipe ID 到内容的映射"""
    recipes = {}
    
    # 扫描目录中的所有 .recipe.yaml 文件
    for file_path in recipes_dir.glob("*.recipe.yaml"):
        # 从文件名提取 ID（去掉 .recipe.yaml 后缀）
        recipe_id = file_path.stem.replace(".recipe", "")
        recipes[recipe_id] = _load_yaml_file(file_path)
    
    return recipes


# ================================
# 综合 Fixtures (用于集成测试)
# ================================

@pytest.fixture(scope="session")
def complete_fixture_set(all_templates: Dict[str, str], 
                        all_dataschemas: Dict[str, Dict[str, Any]], 
                        all_blocks: Dict[str, Dict[str, Any]], 
                        all_recipes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """返回包含所有测试数据的完整集合"""
    return {
        "templates": all_templates,
        "dataschemas": all_dataschemas,
        "blocks": all_blocks,
        "recipes": all_recipes
    }


# ================================
# 辅助 Fixture（用于文件系统操作测试）
# ================================

@pytest.fixture
def temp_fixture_files(tmp_path: Path, complete_fixture_set: Dict[str, Any]) -> Dict[str, Path]:
    """在临时目录中创建测试文件的副本，用于文件系统操作测试"""
    temp_dirs = {
        "templates": tmp_path / "templates",
        "dataschemas": tmp_path / "dataschemas", 
        "blocks": tmp_path / "blocks",
        "recipes": tmp_path / "recipes"
    }
    
    # 创建目录
    for dir_path in temp_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # 复制模板文件
    for template_id, content in complete_fixture_set["templates"].items():
        file_path = temp_dirs["templates"] / f"{template_id}.jinja"
        file_path.write_text(content, encoding='utf-8')
    
    # 复制 YAML 文件
    for dataschema_id, content in complete_fixture_set["dataschemas"].items():
        file_path = temp_dirs["dataschemas"] / f"{dataschema_id}.dataschema.yaml"
        file_path.write_text(yaml.dump(content, default_flow_style=False), encoding='utf-8')
    
    for block_id, content in complete_fixture_set["blocks"].items():
        file_path = temp_dirs["blocks"] / f"{block_id}.block.yaml"
        file_path.write_text(yaml.dump(content, default_flow_style=False), encoding='utf-8')
    
    for recipe_id, content in complete_fixture_set["recipes"].items():
        file_path = temp_dirs["recipes"] / f"{recipe_id}.recipe.yaml"
        file_path.write_text(yaml.dump(content, default_flow_style=False), encoding='utf-8')
    
    return temp_dirs

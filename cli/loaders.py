# -*- coding: utf-8 -*-
# cli/loaders.py

import yaml
from pathlib import Path
from typing import Dict, Any, Iterator, Tuple, Optional

from Prism.entities import CompilationSources
from Prism.exceptions import PrismError

from config import Config

class LoaderError(PrismError):
    """与文件加载或解析相关的错误。"""
    pass

class ProjectLoader:
    """
    负责从文件系统按需加载项目资产，并将它们打包成 CompilationSources
    对象，以供核心编译器使用。

    该类内部实现了缓存机制，以避免重复读取共享文件（blocks, dataschemas, templates）。
    """
    def __init__(self, config: Config):
        self._config = config
        # 初始化缓存，None 表示尚未加载
        self._templates_cache: Optional[Dict[str, str]] = None
        self._dataschemas_cache: Optional[Dict[str, Dict[str, Any]]] = None
        self._blocks_cache: Optional[Dict[str, Dict[str, Any]]] = None

    def load_for_recipe(self, recipe_name: str) -> CompilationSources:
        """
        为指定的单个 recipe 加载所有必需的编译源。

        Args:
            recipe_name: The name of the recipe to load (e.g., "email-follow-up").

        Returns:
            A CompilationSources object ready for the compiler.

        Raises:
            LoaderError: If the specified recipe file cannot be found or parsed.
        """
        print(f"🚀 Loading assets for recipe: '{recipe_name}'...")
        
        # 1. 使用缓存加载共享资源
        templates = self._get_templates()
        dataschemas = self._get_dataschemas()
        blocks = self._get_blocks()

        # 2. 加载指定的 recipe 文件
        recipe_filename = f"{recipe_name}.recipe.yaml"
        recipe_file_path = self._config.recipes_path / recipe_filename
        
        if not recipe_file_path.is_file():
            raise LoaderError(f"Recipe file not found: {recipe_file_path}")

        try:
            recipe_data = yaml.safe_load(recipe_file_path.read_text(encoding='utf-8'))
            if not isinstance(recipe_data, dict):
                 raise LoaderError(f"Recipe file '{recipe_filename}' is empty or invalid.")
        except Exception as e:
            raise LoaderError(f"Failed to load or parse recipe '{recipe_file_path}': {e}") from e

        print(f"✅ Assets for '{recipe_name}' loaded successfully.")
        
        # 3. 打包并返回
        return CompilationSources(
            templates=templates,
            dataschemas=dataschemas,
            blocks=blocks,
            recipe=recipe_data
        )

    def load_compilation_tasks(self) -> Iterator[Tuple[str, CompilationSources]]:
        """
        [批处理方法] 加载所有共享资产，并为每个找到的 recipe 生成一个编译任务。
        这个方法现在会利用缓存，因此与多次调用 `load_for_recipe` 同样高效。
        """
        print("🚀 Starting batch asset loading process...")
        
        # 1. 预热所有缓存
        templates = self._get_templates()
        dataschemas = self._get_dataschemas()
        blocks = self._get_blocks()
        
        print("\n🔍 Searching for all recipes to compile...")
        recipe_path = self._config.recipes_path
        if not recipe_path.is_dir():
            print(f"⚠️ Recipe directory not found, nothing to compile: {recipe_path}")
            return

        recipe_files = list(recipe_path.glob("*.recipe.y*ml"))
        if not recipe_files:
            print("ℹ️ No recipe files found.")
            return

        for recipe_file in recipe_files:
            recipe_name = recipe_file.name.split('.recipe')[0]
            try:
                recipe_data = yaml.safe_load(recipe_file.read_text(encoding='utf-8'))
                if not recipe_data:
                    print(f"    - Skipping empty recipe file: {recipe_file.name}")
                    continue
                
                sources = CompilationSources(
                    templates=templates,
                    dataschemas=dataschemas,
                    blocks=blocks,
                    recipe=recipe_data
                )
                yield recipe_name, sources
            except Exception as e:
                # 在批处理模式下，可以选择打印警告而不是直接抛出异常
                print(f"⚠️ Failed to load or parse recipe '{recipe_file}', skipping. Error: {e}")
        
        print("\n✅ All compilation tasks prepared.")

    # --- 缓存支持的私有 Getter ---

    def _get_templates(self) -> Dict[str, str]:
        if self._templates_cache is None:
            self._templates_cache = self._load_from_disk(
                self._config.templates_path, "*.jinja", "templates", self._read_text_file
            )
        return self._templates_cache

    def _get_dataschemas(self) -> Dict[str, Dict[str, Any]]:
        if self._dataschemas_cache is None:
            self._dataschemas_cache = self._load_from_disk(
                self._config.dataschemas_path, "*.dataschema.y*ml", "dataschemas", self._read_yaml_file
            )
        return self._dataschemas_cache

    def _get_blocks(self) -> Dict[str, Dict[str, Any]]:
        if self._blocks_cache is None:
            self._blocks_cache = self._load_from_disk(
                self._config.blocks_path, "*.block.y*ml", "blocks", self._read_yaml_file
            )
        return self._blocks_cache

    # --- 底层文件读取辅助方法 ---

    def _load_from_disk(self, dir_path: Path, glob_pattern: str, resource_name: str, reader_func) -> Dict:
        """通用的从磁盘加载资源的函数。"""
        print(f"  - Loading {resource_name} from disk: {dir_path}")
        if not dir_path.is_dir():
            print(f"    - Directory not found, skipping.")
            return {}

        loaded_data = {}
        for file_path in dir_path.glob(glob_pattern):
            resource_id = file_path.name.split('.')[0]
            try:
                content = reader_func(file_path)
                if content:
                    loaded_data[resource_id] = content
            except Exception as e:
                raise LoaderError(f"Failed to process {resource_name} file '{file_path}': {e}") from e
        return loaded_data

    @staticmethod
    def _read_yaml_file(path: Path) -> Optional[Dict[str, Any]]:
        return yaml.safe_load(path.read_text(encoding='utf-8'))

    @staticmethod
    def _read_text_file(path: Path) -> str:
        return path.read_text(encoding='utf-8')


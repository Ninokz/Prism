# -*- coding: utf-8 -*-
# cli/loaders.py

import yaml
from pathlib import Path
from typing import Dict, Any, Iterator, Tuple, Optional

from Prism.entities import CompilationSources
from Prism.exceptions import PrismError

from config import Config

class LoaderError(PrismError):
    pass

class ProjectLoader:
    def __init__(self, config: Config):
        self._config = config
        self._templates_cache: Optional[Dict[str, str]] = None
        self._dataschemas_cache: Optional[Dict[str, Dict[str, Any]]] = None
        self._blocks_cache: Optional[Dict[str, Dict[str, Any]]] = None

    def load_for_recipe(self, recipe_name: str) -> CompilationSources:
        print(f"🚀 Loading assets for recipe: '{recipe_name}'...")
        
        templates = self._get_templates()
        dataschemas = self._get_dataschemas()
        blocks = self._get_blocks()

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
        
        return CompilationSources(
            templates=templates,
            dataschemas=dataschemas,
            blocks=blocks,
            recipe=recipe_data
        )

    def load_compilation_tasks(self) -> Iterator[Tuple[str, CompilationSources]]:
        print("🚀 Starting batch asset loading process...")
        
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
                print(f"⚠️ Failed to load or parse recipe '{recipe_file}', skipping. Error: {e}")
        
        print("\n✅ All compilation tasks prepared.")

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

    def _load_from_disk(self, dir_path: Path, glob_pattern: str, resource_name: str, reader_func) -> Dict:
        print(f"  - Loading {resource_name} from disk: {dir_path}")
        if not dir_path.is_dir():
            print(f"    - Directory '{dir_path}' not found, skipping.")
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


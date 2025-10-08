# -*- coding: utf-8 -*-
# CLI/loaders.py

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Dict
from dataclasses import dataclass

from CLI.exception import LoaderError
from CLI.actions.initializer import ProjectInitializer

from Prism.entities import CompilationSources,CompilationTask

class ProjectLoader:
    def __init__(self, project_path: Path) -> None:
        self.project_path = project_path

        self.blocks_path = self.project_path / 'blocks'
        self.dataschemas_path = self.project_path / 'dataschemas'
        self.recipes_path = self.project_path / 'recipes'
        self.templates_path = self.project_path / 'templates'

        self._templates_cache: Optional[Dict[str, str]] = None
        self._dataschemas_cache: Optional[Dict[str, Dict[str, Any]]] = None
        self._blocks_cache: Optional[Dict[str, Dict[str, Any]]] = None

    def load_compilation_sources(self) -> CompilationSources:
        print("🚀 Loading shared assets for compilation...")
        sources = CompilationSources(
            templates=self._get_templates(),
            dataschemas=self._get_dataschemas(),
            blocks=self._get_blocks()
        )
        print("✅ Shared assets loaded successfully.")
        return sources

    def load_recipe(self, recipe_name: str) -> CompilationTask:
        print(f"🚀 Loading recipe: '{recipe_name}'...")
        recipe_filename = f"{recipe_name}.recipe.yaml"
        recipe_file_path = self.recipes_path / recipe_filename

        if not recipe_file_path.is_file():
            raise LoaderError("recipe", str(recipe_file_path), "File not found")

        try:
            recipe_data = self._read_yaml_file(recipe_file_path)
            if not isinstance(recipe_data, dict):
                raise LoaderError("recipe", str(recipe_file_path), "File is empty or has invalid format")
        except Exception as e:
            raise LoaderError("recipe", str(recipe_file_path), f"Failed to load or parse file: {e}") from e
        
        print(f"✅ Recipe '{recipe_name}' loaded successfully.")
        return CompilationTask(
            recipe_name=recipe_name, 
            sources=recipe_data)

    def _get_templates(self) -> Dict[str, str]:
        if self._templates_cache is None:
            self._templates_cache = self._load_from_disk(
                dir_path=self.templates_path,
                glob_pattern="*.jinja",
                resource_name="templates",
                reader_func=self._read_text_file
            )
        return self._templates_cache

    def _get_dataschemas(self) -> Dict[str, Dict[str, Any]]:
        if self._dataschemas_cache is None:
            self._dataschemas_cache = self._load_from_disk(
                dir_path=self.dataschemas_path,
                glob_pattern="*.dataschema.y*ml", # 支持 .yml 和 .yaml
                resource_name="dataschemas",
                reader_func=self._read_yaml_file
            )
        return self._dataschemas_cache

    def _get_blocks(self) -> Dict[str, Dict[str, Any]]:
        if self._blocks_cache is None:
            self._blocks_cache = self._load_from_disk(
                dir_path=self.blocks_path,
                glob_pattern="*.block.y*ml", # 支持 .yml 和 .yaml
                resource_name="blocks",
                reader_func=self._read_yaml_file
            )
        return self._blocks_cache

    def _load_from_disk(self, dir_path: Path, glob_pattern: str, resource_name: str, reader_func: Callable) -> Dict:
        print(f"  - Loading {resource_name} from: {dir_path}")
        if not dir_path.is_dir():
            print(f"    - Warning: Directory not found, skipping.")
            return {}

        loaded_data = {}
        for file_path in dir_path.glob(glob_pattern):
            # resource_id 通常是文件名去掉第一个点之后的部分
            resource_id = file_path.name.split('.')[0]
            try:
                content = reader_func(file_path)
                if content: # 确保文件不是空的
                    loaded_data[resource_id] = content
            except Exception as e:
                raise LoaderError(resource_name, str(file_path), f"Failed to process file: {e}") from e
        
        print(f"    - Found and loaded {len(loaded_data)} {resource_name}.")
        return loaded_data

    @staticmethod
    def _read_yaml_file(path: Path) -> Optional[Dict[str, Any]]:
        return yaml.safe_load(path.read_text(encoding='utf-8'))

    @staticmethod
    def _read_text_file(path: Path) -> str:
        return path.read_text(encoding='utf-8')

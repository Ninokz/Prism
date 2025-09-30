# -*- coding: utf-8 -*-
# cli/config.py

import json
from pathlib import Path
from typing import Dict

from pydantic import BaseModel, Field, ValidationError

class ConfigError(Exception):
    pass

class Config(BaseModel):
    source_root: Path
    output_root: Path
    source_subdirs: Dict[str, str]
    output_filenames: Dict[str, str]

    @classmethod
    def from_json(cls, path: Path) -> 'Config':
        if not path.is_file():
            raise ConfigError(f"Config file not found: {path}")
        
        config_dir = path.parent

        try:
            with path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'source_root' in data:
                data['source_root'] = config_dir / data['source_root']
            
            if 'output_root' in data:
                data['output_root'] = config_dir / data['output_root']

            instance = cls(**data)
            
            instance.source_root = instance.source_root.resolve()
            instance.output_root = instance.output_root.resolve()
            
            return instance

        except (json.JSONDecodeError, ValidationError) as e:
            raise ConfigError(f"Resolve config file '{path}' failed: {e}") from e
        except KeyError as e:
            raise ConfigError(f"Missing required key in config file '{path}': {e}") from e

    @property
    def blocks_path(self) -> Path:
        return self.source_root / self.source_subdirs['blocks']

    @property
    def dataschemas_path(self) -> Path:
        return self.source_root / self.source_subdirs['dataschemas']

    @property
    def recipes_path(self) -> Path:
        return self.source_root / self.source_subdirs['recipes']

    @property
    def templates_path(self) -> Path:
        return self.source_root / self.source_subdirs['templates']
        
    def get_output_template_path(self, recipe_name: str) -> Path:
        filename = self.output_filenames['template'].format(recipe_name=recipe_name)
        return self.output_root / filename

    def get_output_model_path(self, recipe_name: str) -> Path:
        filename = self.output_filenames['model'].format(recipe_name=recipe_name)
        return self.output_root / filename

# -*- coding: utf-8 -*-
# cli/config.py

import json
from pathlib import Path
from typing import Dict

from pydantic import BaseModel, Field, ValidationError

class ConfigError(Exception):
    pass

class Config(BaseModel):
    source_root: Path = Field(..., description="源文件的根目录")
    output_root: Path = Field(..., description="输出文件的根目录")
    source_subdirs: Dict[str, str] = Field(..., description="源文件子目录映射")
    output_filenames: Dict[str, str] = Field(..., description="输出文件名模板")

    @classmethod
    def from_json(cls, path: Path) -> 'Config':
        if not path.is_file():
            raise ConfigError(f"配置文件不存在: {path}")
        try:
            with path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ConfigError(f"解析配置文件 '{path}' 失败: {e}") from e

    # --- 便捷的路径属性 ---
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
        """获取最终模板文件的输出路径。"""
        filename = self.output_filenames['template'].format(recipe_name=recipe_name)
        return self.output_root / filename

    def get_output_model_path(self, recipe_name: str) -> Path:
        """获取最终模型代码的输出路径。"""
        filename = self.output_filenames['model'].format(recipe_name=recipe_name)
        return self.output_root / filename

# -*- coding: utf-8 -*-
# CLI/scaffolder.py

import jinja2
from pathlib import Path
from typing import Dict, Any, Iterator, Tuple, Optional

from CLI.exception import ScaffoldError
from CLI.actions.initializer import ProjectInitializer

class Scaffolder:
    def __init__(self, project_path: Path) -> None:
        self.project_path = project_path
        self.env = jinja2.Environment(
            loader=jinja2.PackageLoader('CLI', 'templates'),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _create_file_from_template(self, target_path: Path, template_name: str, context: dict):
        if target_path.exists():
            raise ScaffoldError(target_path.suffix.strip('.'), str(target_path), "File already exists")
        try:
            template = self.env.get_template(template_name)
            content = template.render(context)
            target_path.write_text(content, encoding='utf-8')
            print(f"✅ Created new file at: {target_path}")
        except jinja2.TemplateNotFound:
            raise ScaffoldError("scaffolder", template_name, "Internal error: Template not found")
        except Exception as e:
            raise ScaffoldError("scaffolder", str(target_path), f"Failed to write file: {e}")

    def create_block_file(self, block_name: str):
        block_file = self.project_path / 'blocks' / f"{block_name}.block.yaml"
        context = {"block_name": block_name}
        self._create_file_from_template(block_file, 'block.yaml.j2', context)

    def create_recipe_file(self, recipe_name: str):
        recipe_file = self.project_path / 'recipes' / f"{recipe_name}.recipe.yaml"
        context = {"recipe_name": recipe_name}
        self._create_file_from_template(recipe_file, 'recipe.yaml.j2', context)

    def create_dataschema_file(self, dataschema_name: str):
        dataschema_file = self.project_path / 'dataschemas' / f"{dataschema_name}.dataschema.yaml"
        context = {"dataschema_name": dataschema_name}
        self._create_file_from_template(dataschema_file, 'dataschema.yaml.j2', context)
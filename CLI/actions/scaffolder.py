# -*- coding: utf-8 -*-
# CLI/scaffolder.py

from pathlib import Path
import importlib.resources

from ..exception import ScaffoldError

class Scaffolder:
    def __init__(self, project_path:Path) -> None:
        self.project_path = project_path

    def create_block_file(self,block_name:str):
        block_file = self.project_path / 'blocks' / f"{block_name}.py"
        if block_file.exists():
            raise ScaffoldError("block", str(block_file), "File already exists")
        else:
            ...

    def create_recipe_file(self,recipe_name:str):
        recipe_file = self.project_path / 'recipes' / f"{recipe_name}.yaml"
        if recipe_file.exists():
            raise ScaffoldError("recipe", str(recipe_file), "File already exists")
        else:
            ...

    def create_dataschema_file(self,dataschema_name:str):
        dataschema_file = self.project_path / 'dataschemas' / f"{dataschema_name}.py"
        if dataschema_file.exists():
            raise ScaffoldError("dataschema", str(dataschema_file), "File already exists")
        else:
            ...
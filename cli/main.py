import json
from pathlib import Path
from typing import Dict

from config import Config
from loaders import ProjectLoader

from Prism.core import compile_recipe_to_artifacts

config = Config.from_json(Path("config.json"))
loader = ProjectLoader(config)
task = loader.load_for_recipe("email-follow-up")

artifacts = compile_recipe_to_artifacts(task)
print(artifacts.template_content)
import json
from pathlib import Path
from typing import Dict

from config import Config
from loaders import ProjectLoader

from pathlib import Path
from Prism.core import compile_recipe_to_artifacts

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR / "config.json"

config = Config.from_json(CONFIG_PATH)
loader = ProjectLoader(config)

sources = loader.load_for_compilation_source()
task = loader.load_for_recipe("summarize-ticket")

artifacts = compile_recipe_to_artifacts(task, sources)
print(artifacts.template_content)
if artifacts.model_code:
    print(artifacts.model_code)
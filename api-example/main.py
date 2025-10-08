from pathlib import Path
from config import Config
from loaders import ProjectLoader

from Prism.core import compile_recipe_to_artifacts
from Prism.exceptions import PrismError
from Prism.rich_handler import handle_exception

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR / "config.json"

config = Config.from_json(CONFIG_PATH)
loader = ProjectLoader(config)

sources = loader.load_for_compilation_source()
task = loader.load_recipe("summarize-ticket")

try:
    artifacts = compile_recipe_to_artifacts(task, sources)
    print(artifacts.template_content)
    if artifacts.model_code:
        print(artifacts.model_code)
except PrismError as e:
    handle_exception(e)
except Exception as e:
    print(f"Error during compilation: {e}")
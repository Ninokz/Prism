
from pathlib import Path
from CLI.actions.initializer import ProjectInitializer
from CLI.actions.scaffolder import Scaffolder
from CLI.actions.loader import ProjectLoader

from Prism.core import compile_recipe_to_artifacts
from Prism.exceptions import PrismError
from Prism.rich_handler import handle_exception

# "E:\\Project\\prsim-ex"
# pth = Path("E:/Project/prsim-ex")
# ld = ProjectLoader(pth)

# sources = ld.load_compilation_sources()

# print("✨ ----- Task 1 Compilation -----")
# task1 = ld.load_recipe("email-follow-up")
# # 1
# try:
#     artifacts = compile_recipe_to_artifacts(task1, sources)
#     print(artifacts.template_content)
#     if artifacts.model_code:
#         print(artifacts.model_code)
# except PrismError as e:
#     handle_exception(e)
# except Exception as e:
#     print(f"Error during compilation: {e}")

# print("✨ ----- Task 2 Compilation -----")
# # 2
# task2 = ld.load_recipe("summarize-ticket")

# try:
#     artifacts = compile_recipe_to_artifacts(task2, sources)
#     print(artifacts.template_content)
#     if artifacts.model_code:
#         print(artifacts.model_code)
# except PrismError as e:
#     handle_exception(e)
# except Exception as e:
#     print(f"Error during compilation: {e}")


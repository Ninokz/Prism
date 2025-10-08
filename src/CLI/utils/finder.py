# cli/utils/finder.py
from pathlib import Path

class ProjectFinder:
    PROJECT_MARKERS = ['blocks', 'recipes', 'templates']

    @staticmethod
    def find_root(start_path: Path = Path('.')) -> Path:
        current = start_path.resolve()
        while current != current.parent:
            if any((current / marker).exists() for marker in ProjectFinder.PROJECT_MARKERS):
                return current
            current = current.parent
        raise FileNotFoundError("Prism project root not found. Are you inside a project directory?")

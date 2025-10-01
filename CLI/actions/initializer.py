# -*- coding: utf-8 -*-
# CLI/initializer.py

from pathlib import Path

from ..exception import ProjectilitializationError

class ProjectInitializer:
    DIRECTORIES_TO_CREATE = ['blocks', 'dataschemas', 'recipes', 'templates','outputs']

    def __init__(self, project_path:Path) -> None:
        self.project_path = project_path

    def run(self) -> Path:
        project_name = self.project_path.name
        if self.project_path.exists():
            print(f"❌ Error: Directory '{self.project_path}' already exists.")
            raise ProjectilitializationError(str(self.project_path), "Directory already exists")

        print(f"🚀 Initializing new Prism project '{project_name}' at '{self.project_path.parent}'...")
        try:
            self.project_path.mkdir(parents=True, exist_ok=False)
            for subdir in self.DIRECTORIES_TO_CREATE:
                (self.project_path / subdir).mkdir()
        except OSError as e:
            raise ProjectilitializationError(str(self.project_path), str(e)) from e
        # gitignore_content = "outputs/\n.prism_cache/\n"
        # (self.project_path / '.gitignore').write_text(gitignore_content)
        print(f"✅ Project '{project_name}' initialized successfully")
        return self.project_path
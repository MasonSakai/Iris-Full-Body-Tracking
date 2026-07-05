import importlib
import os
import os.path
from pathlib import Path
import traceback
from typing import List

from flask import Flask

from utils.modules.iris_modules import IrisModule


class ModuleManager:

    def __init__(self, app: Flask):
        self.app = app
        self.modules: List[IrisModule] = []

    # ----------------------------
    # Discovery
    # ----------------------------

    def discover(self) -> None:
        self.modules.clear()

        self._discover_from_path(os.path.join(self.app.config["ROOT_PATH"], 'app'), is_core=True)
        self._discover_from_path(self.app.config["MODULE_PATH"], is_core=False)

    def _discover_from_path(self, path: Path | str, is_core: bool):
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            return

        for entry in path.iterdir():
            if not entry.is_dir():
                continue

            if not (entry / "ModInfo.xml").exists():
                continue

            module = self._load_module(entry, is_core)
            if module:
                print(f'Got Module: {module.module_id if module else module}')
                self.modules.append(module)

    def _load_module(self, folder: Path, is_core: bool) -> IrisModule | None:
        module_name = f"{'app' if is_core else 'modules'}.{folder.name}.module"
        try:
            mod = importlib.import_module(module_name)
            module: IrisModule = mod.create_module(self.app)
            module.module_id = folder.name
            return module
        except Exception as e:
            print(f"Failed to load module {folder.name}: {e}")
            #print(traceback.print_exc())
            return None

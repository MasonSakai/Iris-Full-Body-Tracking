from flask import Flask
from utils.modules.module_manager import ModuleManager
from utils.registry import ClearAllThingDatabases
from utils.scribe import Scribe


class AppLifecycle:

    def init_app(self, app: Flask):
        self.app = app
        self.module_manager = ModuleManager(app)

    def initialize(self):
        self.module_manager.discover()

        for module in self.module_manager.modules:
            module.register_databases()

        ClearAllThingDatabases()
        Scribe.loader.BeginLoadSession()
        for module in self.module_manager.modules:
            module.load()
        Scribe.loader.EndLoadSession()

        for module in self.module_manager.modules:
            module.build_runtime()

        for module in self.module_manager.modules:
            module.start_runtime()

    def shutdown(self):
        for module in reversed(self.module_manager.modules):
            module.shutdown_runtime()

        for module in self.module_manager.modules:
            module.save()

import os
import shutil
import tempfile
import unittest

from utils.scribe import Scribe

class test_scribe_base(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        Scribe.ForceStop()

    def tearDown(self):
        Scribe.ForceStop()

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def temp_path(self, filename: str) -> str:
        return os.path.join(self.temp_dir, filename)

    def temp_dummy(self, filename: str) -> str:
        path = self.temp_path("minimal.xml")
        with open(path, "w", encoding="utf-8") as f:
            f.write("<Root />")
        return path
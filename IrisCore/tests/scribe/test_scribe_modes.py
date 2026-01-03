import os
import shutil
import tempfile
import unittest

from utils.Log import LogLevel
from utils.debug import DebugViewSettings
from utils.scribe import LoadSaveMode, Scribe

#DebugViewSettings.logLoadLevel = LogLevel.Error

class test_scribe_modes(unittest.TestCase):

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


    def test_1_force_stop_resets_state(self):
        Scribe.mode = LoadSaveMode.Saving

        Scribe.ForceStop()

        self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)

    def test_2_empty_save_creates_file(self):
        path = self.temp_path("empty_save.xml")

        Scribe.saver.InitSaving("Root")
        Scribe.saver.FinalizeSaving(path)

        self.assertTrue(os.path.exists(path))
        self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)

    def test_3_loading_minimal_file(self):
        path = self.temp_dummy("minimal.xml")

        Scribe.loader.InitLoading(path)
        Scribe.loader.FinalizeLoading()

        self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)

    def test_4_loading_missing_file_force_stops(self):
        path = self.temp_path("does_not_exist.xml")

        with self.assertRaises(Exception):
            Scribe.loader.InitLoading(path)

        # State must be clean afterward
        self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)
        self.assertFalse(os.path.exists(path))

    def test_5_begin_and_finalize_saving(self):
        path = self.temp_path("empty_save.xml")
        self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)

        Scribe.saver.InitSaving("Root")
        self.assertEqual(Scribe.mode, LoadSaveMode.Saving)

        Scribe.saver.FinalizeSaving(path)
        self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)

    def test_6_begin_and_finalize_loading(self):
        path = self.temp_dummy("minimal.xml")
        self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)

        Scribe.loader.InitLoading(path)
        self.assertEqual(Scribe.mode, LoadSaveMode.LoadingVars)

        Scribe.loader.FinalizeLoading()

        # FinalizeLoading should complete the entire cycle
        self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)

    def test_7_loading_exception_does_not_leave_active_mode(self):
        class TestException(Exception):
            pass
        
        path = self.temp_dummy("minimal.xml")
        try:
            Scribe.loader.InitLoading(path)
            self.assertEqual(Scribe.mode, LoadSaveMode.LoadingVars)

            # Simulate failure mid-load
            raise TestException()

        except TestException:
            pass

        finally:
            # What production code should do
            Scribe.loader.FinalizeLoading()

        self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)

    def test_8_force_stop_when_starting_save_while_loading(self):
        path = self.temp_dummy("minimal.xml")
        Scribe.loader.InitLoading(path)
        self.assertNotEqual(Scribe.mode, LoadSaveMode.Inactive)

        # Attempt illegal transition
        Scribe.saver.InitSaving("Root")

        # RimWorld behavior: log + ForceStop + InitSaving
        self.assertEqual(Scribe.mode, LoadSaveMode.Saving)

    def test_9_multiple_sequential_load_save_cycles(self):
        for i in range(5):
            Scribe.saver.InitSaving("Root")
            self.assertEqual(Scribe.mode, LoadSaveMode.Saving)
            path = self.temp_path(f"empty_save_{i}.xml")
            Scribe.saver.FinalizeSaving(path)
            self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)

            Scribe.loader.InitLoading(path)
            self.assertEqual(Scribe.mode, LoadSaveMode.LoadingVars)
            Scribe.loader.FinalizeLoading()
            self.assertEqual(Scribe.mode, LoadSaveMode.Inactive)



if __name__ == '__main__':
    unittest.main()

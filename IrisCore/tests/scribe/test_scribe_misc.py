import unittest
from lxml import etree as ET

from tests.scribe.test_scribe_base import test_scribe_base
from utils.Log import LogLevel
from utils.debug import DebugViewSettings
from utils.scribe import IExposable, ILoadReferenceable, LoadSaveMode, Scribe, Scribe_Deep, Scribe_References, Scribe_Values

#DebugViewSettings.logLoadLevel = LogLevel.Critical

class PostInitTarget(IExposable, ILoadReferenceable):
    def __init__(self, load_id=''):
        self.load_id = load_id

    def GetUniqueLoadID(self):
        return self.load_id

    def ExposeData(self):
        self.load_id = Scribe_Values.Look(self.load_id, 'load_id', str)

class PostInitHolder(IExposable):
    def __init__(self, target=None):
        self.target = target
        self.post_init_called = False
        self.target_seen_in_post = None

    def ExposeData(self):
        self.target = Scribe_References.Look(
            self.target, "target", PostInitTarget
        )

        if Scribe.mode == LoadSaveMode.PostLoadInit:
            self.post_init_called = True
            self.target_seen_in_post = self.target


class test_scribe_misc(test_scribe_base):

    def test_1_postloadinit_called_after_crossrefs(self):
        path = self.temp_path("postloadinit.xml")

        target = PostInitTarget("T1")
        holder = PostInitHolder(target)

        # --- Save ---
        Scribe.saver.InitSaving("root")
        target = Scribe_Deep.Look(target, "target", PostInitTarget)
        holder = Scribe_Deep.Look(holder, "holder", PostInitHolder)
        Scribe.saver.FinalizeSaving(path)

        # --- Load ---
        Scribe.loader.InitLoading(path)
        
        loaded_target = None
        loaded_target = Scribe_Deep.Look(loaded_target, "target", PostInitTarget)

        loaded = None
        loaded = Scribe_Deep.Look(loaded, "holder", PostInitHolder)

        # Still unresolved here
        self.assertIsNone(loaded.target)

        # Finalize triggers PostLoadInit
        Scribe.loader.FinalizeLoading()

        self.assertTrue(loaded.post_init_called)
        self.assertIsNotNone(loaded.target_seen_in_post)
        self.assertEqual(loaded.target_seen_in_post, loaded_target)

    def test_2_postloadinit_called_once(self):
        path = self.temp_path("postloadinit_once.xml")

        holder = PostInitHolder()

        Scribe.saver.InitSaving("root")
        holder = Scribe_Deep.Look(holder, "holder", PostInitHolder)
        Scribe.saver.FinalizeSaving(path)

        Scribe.loader.InitLoading(path)
        loaded = None
        loaded = Scribe_Deep.Look(loaded, "holder", PostInitHolder)

        Scribe.loader.FinalizeLoading()

        self.assertTrue(loaded.post_init_called)


if __name__ == '__main__':
    unittest.main()

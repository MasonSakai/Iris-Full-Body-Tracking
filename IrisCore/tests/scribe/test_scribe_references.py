import unittest
from lxml import etree as ET

from tests.scribe.test_scribe_base import test_scribe_base
from utils.Log import LogLevel, LogSimple
from utils.debug import DebugViewSettings
from utils.scribe import IExposable, ILoadReferenceable, LoadSaveMode, Scribe, Scribe_Deep, Scribe_Values, Scribe_References

#DebugViewSettings.ScribeDebugCrossRefs = True
#DebugViewSettings.logLoadLevel = LogLevel.Critical

class RefObject(ILoadReferenceable, IExposable):
    def __init__(self, load_id=''):
        self.load_id = load_id

    def GetUniqueLoadID(self):
        return self.load_id

    def ExposeData(self):
        self.load_id = Scribe_Values.Look(self.load_id, 'load_id', str)

class RefHolder(IExposable):
    def __init__(self, target=None):
        self.target = target

    def ExposeData(self):
        self.target = Scribe_References.Look(
            self.target, "target", RefObject
        )


class test_scribe_references(test_scribe_base):

    def test_1_reference_saves_id_only(self):
        path = self.temp_path("ref_save.xml")

        obj = RefObject("Ref_1")

        Scribe.saver.InitSaving("root")
        obj = Scribe_References.Look(obj, "ref", RefObject)
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()

        ref_node = root.find("ref")
        self.assertIsNotNone(ref_node)
        self.assertEqual(ref_node.text, "Ref_1")

    def test_2_reference_loadingvars_passthrough(self):
        path = self.temp_path("ref_loadingvars.xml")

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
            <root>
                <ref>Ref_2</ref>
            </root>
            """)

        existing = RefObject("Existing")

        Scribe.loader.InitLoading(path)
        result = Scribe_References.Look(existing, "ref", RefObject)
        Scribe.loader.FinalizeLoading()

        # Must be unchanged during LoadingVars
        self.assertIs(result, existing)

    def test_3_reference_missing_node_passthrough(self):
        path = self.temp_dummy("ref_missing.xml")

        existing = RefObject("Existing")

        Scribe.loader.InitLoading(path)
        result = Scribe_References.Look(existing, "missing", RefObject)
        Scribe.loader.FinalizeLoading()

        self.assertIs(result, existing)

    def test_4_reference_resolves_after_crossrefs(self):
        path = self.temp_path("ref_resolve.xml")

        target = RefObject("Target_1")
        holder = RefHolder(target)

        # --- Save ---
        Scribe.saver.InitSaving("root")
        target = Scribe_Deep.Look(target, "target", RefObject)
        holder = Scribe_Deep.Look(holder, "holder", RefHolder)
        Scribe.saver.FinalizeSaving(path)

        # --- Load ---
        Scribe.loader.InitLoading(path)

        loaded_holder = None
        loaded_holder = Scribe_Deep.Look(
            loaded_holder, "holder", RefHolder
        )

        loaded_target = None
        loaded_target = Scribe_Deep.Look(loaded_target, "target", RefObject)
        
        # Still unresolved after LoadingVars
        self.assertIsNotNone(loaded_target)
        self.assertIsNone(loaded_holder.target)

        # Trigger resolution phase
        Scribe.loader.crossRefs.ResolveAllCrossReferences()
        LogSimple.FlushToStandardLog(LogLevel.Off)

        self.assertIsNotNone(loaded_holder.target)
        self.assertEqual(
            loaded_holder.target.GetUniqueLoadID(),
            "Target_1"
        )

        Scribe.loader.FinalizeLoading()








if __name__ == '__main__':
    unittest.main()

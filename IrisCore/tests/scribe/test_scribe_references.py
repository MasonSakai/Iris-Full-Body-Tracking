import unittest
from lxml import etree as ET

from tests.scribe.test_scribe_base import test_scribe_base
from utils.Log import LogLevel, LogSimple
from utils.debug import DebugViewSettings
from utils.scribe import IExposable, ILoadReferenceable, LoadSaveMode, Scribe, Scribe_Collections, Scribe_Deep, Scribe_Values, Scribe_References

#DebugViewSettings.ScribeDebugCrossRefs = True
#DebugViewSettings.logLoadLevel = LogLevel.Critical

class RefTarget(ILoadReferenceable, IExposable):
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
            self.target, "target", RefTarget
        )

class RefListHolder(IExposable):
    def __init__(self, targets=None):
        self.targets = targets or []

    def ExposeData(self):
        self.targets = Scribe_Collections.LookList(
            self.targets,
            "targets",
            RefTarget,
            Scribe_Collections.LookMode.Reference
        )


class test_scribe_references(test_scribe_base):

    def test_01_reference_saves_id_only(self):
        path = self.temp_path("ref_save.xml")

        obj = RefTarget("Ref_1")

        Scribe.saver.InitSaving("root")
        obj = Scribe_References.Look(obj, "ref", RefTarget)
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()

        ref_node = root.find("ref")
        self.assertIsNotNone(ref_node)
        self.assertEqual(ref_node.text, "Ref_1")

    def test_02_reference_loadingvars_passthrough(self):
        path = self.temp_path("ref_loadingvars.xml")

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
            <root>
                <ref>Ref_2</ref>
            </root>
            """)

        existing = RefTarget("Existing")

        Scribe.loader.InitLoading(path)
        result = Scribe_References.Look(existing, "ref", RefTarget)
        Scribe.loader.FinalizeLoading()

        # Must be unchanged during LoadingVars
        self.assertIs(result, existing)

    def test_03_reference_missing_node_passthrough(self):
        path = self.temp_dummy("ref_missing.xml")

        existing = RefTarget("Existing")

        Scribe.loader.InitLoading(path)
        result = Scribe_References.Look(existing, "missing", RefTarget)
        Scribe.loader.FinalizeLoading()

        self.assertIs(result, existing)

    def test_04_reference_resolves_after_crossrefs(self):
        path = self.temp_path("ref_resolve.xml")

        target = RefTarget("Target_1")
        holder = RefHolder(target)

        # --- Save ---
        Scribe.saver.InitSaving("root")
        target = Scribe_Deep.Look(target, "target", RefTarget)
        holder = Scribe_Deep.Look(holder, "holder", RefHolder)
        Scribe.saver.FinalizeSaving(path)

        # --- Load ---
        Scribe.loader.InitLoading(path)

        loaded_holder = None
        loaded_holder = Scribe_Deep.Look(
            loaded_holder, "holder", RefHolder
        )

        loaded_target = None
        loaded_target = Scribe_Deep.Look(loaded_target, "target", RefTarget)
        
        # Still unresolved after LoadingVars
        self.assertIsNotNone(loaded_target)
        self.assertIsNone(loaded_holder.target)

        # Trigger resolution phase
        Scribe.ExitNode()
        Scribe.loader.crossRefs.ResolveAllCrossReferences()
        LogSimple.FlushToStandardLog(LogLevel.Off)

        self.assertIsNotNone(loaded_holder.target)
        self.assertEqual(
            loaded_holder.target.GetUniqueLoadID(),
            "Target_1"
        )

        Scribe.loader.FinalizeLoading()

    def test_05_reference_list_saves_ids(self):
        path = self.temp_path("ref_list_save.xml")

        a = RefTarget("A")
        b = RefTarget("B")
        holder = RefListHolder([a, b])

        Scribe.saver.InitSaving("root")
        holder = Scribe_Deep.Look(holder, "holder", RefListHolder)
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()

        targets = root.find("holder/targets")
        self.assertIsNotNone(targets)

        lis = targets.findall("li")
        self.assertEqual([li.text for li in lis], ["A", "B"])

    def test_06_reference_list_loadingvars_passthrough(self):
        path = self.temp_path("ref_list_loading.xml")

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
            <root>
                <holder>
                    <targets>
                        <li>A</li>
                        <li>B</li>
                    </targets>
                </holder>
            </root>
            """)

        Scribe.loader.InitLoading(path)

        holder = None
        holder = Scribe_Deep.Look(holder, "holder", RefListHolder)

        # During LoadingVars, list exists but elements are unresolved
        self.assertEqual(holder.targets, [])

        Scribe.loader.FinalizeLoading()

    def test_07_reference_list_resolves_after_crossrefs(self):
        path = self.temp_path("ref_list_resolve.xml")

        a = RefTarget("A")
        b = RefTarget("B")
        holder = RefListHolder([a, b])

        # --- Save ---
        Scribe.saver.InitSaving("root")
        a = Scribe_Deep.Look(a, "A", RefTarget)
        b = Scribe_Deep.Look(b, "B", RefTarget)
        holder = Scribe_Deep.Look(holder, "holder", RefListHolder)
        Scribe.saver.FinalizeSaving(path)

        # --- Load ---
        Scribe.loader.InitLoading(path)
        loaded = None
        loaded = Scribe_Deep.Look(loaded, "holder", RefListHolder)
        
        a_loaded = None
        b_loaded = None
        a_loaded = Scribe_Deep.Look(a_loaded, "A", RefTarget)
        b_loaded = Scribe_Deep.Look(b_loaded, "B", RefTarget)

        # unresolved
        self.assertEqual(loaded.targets, [])
        # resolve
        Scribe.ExitNode()
        Scribe.loader.crossRefs.ResolveAllCrossReferences()
        LogSimple.FlushToStandardLog(LogLevel.Off)

        self.assertEqual(
            [t.GetUniqueLoadID() for t in loaded.targets],
            ["A", "B"]
        )

        Scribe.loader.FinalizeLoading()

    def test_08_reference_missing_target(self):
        path = self.temp_path("ref_missing_target.xml")

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
            <root>
                <holder>
                    <targets>
                        <li>DoesNotExist</li>
                    </targets>
                </holder>
            </root>
            """)

        Scribe.loader.InitLoading(path)

        holder = None
        holder = Scribe_Deep.Look(holder, "holder", RefListHolder)
        
        Scribe.ExitNode()
        Scribe.loader.crossRefs.ResolveAllCrossReferences()
        LogSimple.FlushToStandardLog(LogLevel.Off)

        self.assertEqual(holder.targets, [None])

        Scribe.loader.FinalizeLoading()

    def test_09_reference_empty_entry(self):
        path = self.temp_path("ref_empty.xml")

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
            <root>
                <holder>
                    <targets>
                        <li />
                    </targets>
                </holder>
            </root>
            """)

        Scribe.loader.InitLoading(path)

        holder = None
        holder = Scribe_Deep.Look(holder, "holder", RefListHolder)
        
        Scribe.ExitNode()
        Scribe.loader.crossRefs.ResolveAllCrossReferences()
        LogSimple.FlushToStandardLog(LogLevel.Off)

        self.assertEqual(holder.targets, [None])

        Scribe.loader.FinalizeLoading()

    def test_10_reference_duplicate_ids(self):
        path = self.temp_path("ref_duplicates.xml")

        a = RefTarget("A")
        holder = RefListHolder([a, a])

        # Save
        Scribe.saver.InitSaving("root")
        holder = Scribe_Deep.Look(holder, "holder", RefListHolder)
        Scribe.saver.FinalizeSaving(path)

        # Load
        Scribe.loader.InitLoading(path)
        loaded = None
        loaded = Scribe_Deep.Look(loaded, "holder", RefListHolder)
        
        Scribe.ExitNode()
        Scribe.loader.crossRefs.ResolveAllCrossReferences()
        LogSimple.FlushToStandardLog(LogLevel.Off)

        self.assertIs(loaded.targets[0], loaded.targets[1])

        Scribe.loader.FinalizeLoading()


if __name__ == '__main__':
    unittest.main()

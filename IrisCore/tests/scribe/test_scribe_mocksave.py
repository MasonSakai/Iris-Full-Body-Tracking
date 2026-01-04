from enum import Enum, auto
import unittest
from lxml import etree as ET

from tests.scribe.test_scribe_base import test_scribe_base
from utils.Log import LogLevel
from utils.debug import DebugViewSettings
from utils.scribe import IExposable, ILoadReferenceable, LoadSaveMode, Scribe, Scribe_Deep, Scribe_Values, Scribe_Collections

DebugViewSettings.logLoadLevel = LogLevel.Critical

class TestEnum(Enum):
    A = auto()
    B = auto()

class RefThing(ILoadReferenceable, IExposable):
    def __init__(self, load_id=None, value=0):
        self.load_id = load_id
        self.value = value

    def GetUniqueLoadID(self):
        return self.load_id

    def ExposeData(self):
        self.load_id = Scribe_Values.Look(
            self.load_id, 'load_id', str
        )
        self.value = Scribe_Values.Look(
            self.value, "value", int, defaultValue=0
        )

class NestedData(IExposable):
    def __init__(self):
        self.numbers = []
        self.ref_map = {}
        self.post_loaded = False

    def ExposeData(self):
        self.numbers = Scribe_Collections.LookList(
            self.numbers,
            "numbers",
            int,
            Scribe_Collections.LookMode.Value
        )

        self.ref_map = Scribe_Collections.LookDict(
            self.ref_map,
            "refMap",
            str,
            RefThing,
            Scribe_Collections.LookMode.Value,
            Scribe_Collections.LookMode.Reference
        )

        if Scribe.mode == LoadSaveMode.PostLoadInit:
            # Confirm references exist by now
            self.post_loaded = all(v is not None for v in self.ref_map.values())

class RootSave(IExposable):
    def __init__(self):
        self.name = ""
        self.enum_val = TestEnum.A
        self.nested = None
        self.all_refs = []

    def ExposeData(self):
        self.name = Scribe_Values.Look(
            self.name, "name", str
        )

        self.enum_val = Scribe_Values.Look(
            self.enum_val, "enumVal", TestEnum, defaultValue=TestEnum.A
        )

        self.nested = Scribe_Deep.Look(
            self.nested, "nested", NestedData
        )

        self.all_refs = Scribe_Collections.LookList(
            self.all_refs,
            "allRefs",
            RefThing,
            Scribe_Collections.LookMode.Deep
        )


class test_scribe_mocksave(test_scribe_base):

    def test_1_full_mock_save_load(self):
        path = self.temp_path("full_mock_save.xml")

        # --- Construct object graph ---
        ref1 = RefThing("R1", 10)
        ref2 = RefThing("R2", 20)

        nested = NestedData()
        nested.numbers = [1, 2, 3]
        nested.ref_map = {
            "first": ref1,
            "second": ref2,
        }

        root = RootSave()
        root.name = "Hello\\nWorld"
        root.enum_val = TestEnum.B
        root.nested = nested
        root.all_refs = [ref1, ref2]

        # --- Save ---
        Scribe.saver.InitSaving("root")
        root = Scribe_Deep.Look(root, "root", RootSave)
        Scribe.saver.FinalizeSaving(path)

        # --- Load ---
        Scribe.loader.InitLoading(path)

        loaded = None
        loaded = Scribe_Deep.Look(loaded, "root", RootSave)

        Scribe.loader.FinalizeLoading()

        # --- Assertions ---

        # Values
        self.assertEqual(loaded.name, "Hello\nWorld")
        self.assertEqual(loaded.enum_val, TestEnum.B)

        # Deep object
        self.assertIsNotNone(loaded.nested)
        self.assertEqual(loaded.nested.numbers, [1, 2, 3])

        # References resolved
        self.assertEqual(
            loaded.nested.ref_map["first"].GetUniqueLoadID(), "R1"
        )
        self.assertEqual(
            loaded.nested.ref_map["second"].GetUniqueLoadID(), "R2"
        )

        # Same instances reused
        self.assertIs(
            loaded.nested.ref_map["first"],
            loaded.all_refs[0]
        )

        # PostLoadInit logic ran
        self.assertTrue(loaded.nested.post_loaded)

    def test_2_loadsession_single_file_equivalence(self):
        path = self.temp_path("single_session.xml")

        obj = RootSave()
        obj.name = "Test"

        # Save
        Scribe.saver.InitSaving("root")
        Scribe_Deep.Look(obj, "root", RootSave)
        Scribe.saver.FinalizeSaving(path)

        # Load via LoadSession
        Scribe.loader.BeginLoadSession()
        Scribe.loader.LoadFile(path)

        loaded = None
        loaded = Scribe_Deep.Look(loaded, "root", RootSave)

        Scribe.loader.EndLoadSession()

        self.assertEqual(loaded.name, "Test")

    def test_3_loadsession_cross_file_references(self):
        defs_path = self.temp_path("defs.xml")
        refs_path = self.temp_path("refs.xml")

        # --- File A: definitions ---
        ref1 = RefThing("R1", 100)
        ref2 = RefThing("R2", 200)

        Scribe.saver.InitSaving("defs")
        Scribe_Collections.LookList(
            [ref1, ref2],
            "allRefs",
            RefThing,
            Scribe_Collections.LookMode.Deep
        )
        Scribe.saver.FinalizeSaving(defs_path)

        # --- File B: references ---
        holder = NestedData()
        holder.ref_map = {
            "a": ref1,
            "b": ref2,
        }

        Scribe.saver.InitSaving("refs")
        Scribe_Deep.Look(holder, "holder", NestedData)
        Scribe.saver.FinalizeSaving(refs_path)

        # --- Load both ---
        Scribe.loader.BeginLoadSession()

        Scribe.loader.LoadFile(defs_path)

        loaded_defs = Scribe_Collections.LookList(
            None,
            "allRefs",
            RefThing,
            Scribe_Collections.LookMode.Deep
        )
        
        Scribe.loader.LoadFile(refs_path)

        loaded_holder = None
        loaded_holder = Scribe_Deep.Look(
            loaded_holder, "holder", NestedData
        )

        Scribe.loader.EndLoadSession()

        # --- Assertions ---
        self.assertEqual(
            loaded_holder.ref_map["a"].value, 100
        )
        self.assertEqual(
            loaded_holder.ref_map["b"].value, 200
        )

    def test_4_loadsession_no_early_reference_resolution(self):
        path = self.temp_path("early.xml")

        ref = RefThing("R1", 42)
        holder = NestedData()
        holder.ref_map = {"x": ref}

        # Save
        Scribe.saver.InitSaving("root")
        Scribe_Deep.Look(ref, "ref", RefThing)
        Scribe_Deep.Look(holder, "holder", NestedData)
        Scribe.saver.FinalizeSaving(path)

        # Load
        Scribe.loader.BeginLoadSession()
        Scribe.loader.LoadFile(path)

        loaded_ref = Scribe_Deep.Look(None, "ref", RefThing)

        loaded_holder = None
        loaded_holder = Scribe_Deep.Look(
            loaded_holder, "holder", NestedData
        )

        # Still unresolved
        self.assertIsNone(loaded_holder.ref_map["x"])

        Scribe.loader.EndLoadSession()

        # Now resolved
        self.assertIsNotNone(loaded_holder.ref_map["x"])
        self.assertEqual(loaded_holder.ref_map["x"].value, 42)




if __name__ == '__main__':
    unittest.main()

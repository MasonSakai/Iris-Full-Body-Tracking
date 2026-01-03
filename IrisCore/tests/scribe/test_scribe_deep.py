import unittest
from lxml import etree as ET

from tests.scribe.test_scribe_base import test_scribe_base
from utils.Log import LogLevel
from utils.debug import DebugViewSettings
from utils.scribe import IExposable, Scribe, Scribe_Deep, Scribe_Values

#DebugViewSettings.logLoadLevel = LogLevel.Critical

class SimpleExposable(IExposable):
    def __init__(self, x=0):
        self.x = x

    def ExposeData(self):
        self.x = Scribe_Values.Look(self.x, "x", int, defaultValue=0)

class OuterExposable(IExposable):
    def __init__(self):
        self.inner = SimpleExposable(3)

    def ExposeData(self):
        self.inner = Scribe_Deep.Look(self.inner, "inner", SimpleExposable)

class test_scribe_deep(test_scribe_base):

    def test_1_saving_simple_exposable(self):
        path = self.temp_path("deep_simple.xml")

        obj = SimpleExposable(5)

        Scribe.saver.InitSaving("root")
        obj = Scribe_Deep.Look(obj, "myObj", SimpleExposable)
        Scribe.saver.FinalizeSaving(path)

        # Load raw XML from file (since saver state is gone)
        tree = ET.parse(path)
        root = tree.getroot()

        my_obj_node = root.find("myObj")
        self.assertIsNotNone(my_obj_node)

        x_node = my_obj_node.find("x")
        self.assertIsNotNone(x_node)
        self.assertEqual(x_node.text, "5")

    def test_2_loading_simple_exposable(self):
        path = self.temp_path("deep_load.xml")

        # --- Save ---
        original = SimpleExposable(10)

        Scribe.saver.InitSaving("root")
        original = Scribe_Deep.Look(original, "myObj", SimpleExposable)
        Scribe.saver.FinalizeSaving(path)

        # --- Load ---
        Scribe.loader.InitLoading(path)

        loaded = None
        loaded = Scribe_Deep.Look(loaded, "myObj", SimpleExposable)

        Scribe.loader.FinalizeLoading()

        self.assertIsNotNone(loaded)
        self.assertIsInstance(loaded, SimpleExposable)
        self.assertEqual(loaded.x, 10)

    def test_3_loading_simple_exposable_as_IExposable(self):
        path = self.temp_path("deep_load.xml")

        # --- Save ---
        original = SimpleExposable(10)

        Scribe.saver.InitSaving("root")
        original = Scribe_Deep.Look(original, "myObj", IExposable)
        Scribe.saver.FinalizeSaving(path)
        
        # Load raw XML from file (since saver state is gone)
        tree = ET.parse(path)
        root = tree.getroot()

        my_obj_node = root.find("myObj")
        self.assertIsNotNone(my_obj_node)

        attrib = my_obj_node.get("class")
        self.assertIsNotNone(attrib)
        self.assertEqual(attrib, 'test_scribe_deep:SimpleExposable')


        # --- Load ---
        Scribe.loader.InitLoading(path)

        loaded = None
        loaded = Scribe_Deep.Look(loaded, "myObj", IExposable)

        Scribe.loader.FinalizeLoading()

        self.assertIsNotNone(loaded)
        self.assertIsInstance(loaded, SimpleExposable)
        self.assertEqual(loaded.x, 10)

    def test_4_loading_missing_node_returns_none(self):
        path = self.temp_dummy("deep_missing.xml")

        Scribe.loader.InitLoading(path)

        loaded = SimpleExposable(99)
        loaded = Scribe_Deep.Look(loaded, "missingObj", SimpleExposable)

        Scribe.loader.FinalizeLoading()

        self.assertIsNone(loaded)

    def test_5_nested_deep_exposable(self):
        path = self.temp_path("deep_nested.xml")

        obj = OuterExposable()

        Scribe.saver.InitSaving("root")
        obj = Scribe_Deep.Look(obj, "outer", OuterExposable)
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()

        outer = root.find("outer")
        self.assertIsNotNone(outer)

        inner = outer.find("inner")
        self.assertIsNotNone(inner)

        x = inner.find("x")
        self.assertIsNotNone(x)
        self.assertEqual(x.text, "3")

    def test_6_deep_noop_in_inactive_mode(self):
        obj = SimpleExposable(5)

        # No InitSaving / InitLoading
        result = Scribe_Deep.Look(obj, "myObj", SimpleExposable)

        self.assertIs(result, obj)


if __name__ == '__main__':
    unittest.main()

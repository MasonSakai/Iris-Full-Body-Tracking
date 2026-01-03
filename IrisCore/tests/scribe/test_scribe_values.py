import unittest

import numpy as np

from tests.scribe.test_scribe_base import test_scribe_base
from utils.Log import LogLevel
from utils.debug import DebugViewSettings
from utils.scribe import Scribe, Scribe_Values
from utils.scribe.internal.LoadIDsWantedBank import LoadIDsWantedBank

#DebugViewSettings.logLoadLevel = LogLevel.Critical

class test_scribe_values(test_scribe_base):

    def test_1_saving_and_loading_int(self):
        path = self.temp_path('dummy.xml')

        # --- Saving ---
        Scribe.saver.InitSaving("root")
        value = 42
        value = Scribe_Values.Look(value, "myInt", int, defaultValue=0)

        # Validate XML
        root_elem = Scribe.saver.baseXmlTree
        node = root_elem.find("myInt")
        self.assertIsNotNone(node)
        self.assertEqual(node.text, "42")
        
        Scribe.saver.FinalizeSaving(path)

        # --- Loading ---
        Scribe.loader.InitLoading(path)

        loaded_value = 0
        loaded_value = Scribe_Values.Look(loaded_value, "myInt", int, defaultValue=0)
        Scribe.loader.FinalizeLoading()
        self.assertEqual(loaded_value, 42)

    def test_2_default_value_handling(self):
        path = self.temp_path('dummy.xml')

        # Should not write default unless forceSave=True
        Scribe.saver.InitSaving("root")

        value = 0
        # defaultValue is 0, so this should be omitted
        value = Scribe_Values.Look(value, "myInt", int, defaultValue=0)

        root_elem = Scribe.saver.baseXmlTree
        self.assertIsNone(root_elem.find("myInt"))
        
        Scribe.saver.FinalizeSaving(path)

        # Force save overrides default omission
        Scribe.saver.InitSaving("root")
        value = 0
        value = Scribe_Values.Look(value, "myInt", int, defaultValue=0, forceSave=True)
        root_elem = Scribe.saver.baseXmlTree
        node = root_elem.find("myInt")
        self.assertIsNotNone(node)
        self.assertEqual(node.text, "0")

        Scribe.saver.FinalizeSaving(path)

    def test_3_loading_missing_and_invalid(self):
        # Missing node → returns default
        xml_missing = "<root />"
        Scribe.loader.InitLoadingFromString(xml_missing)
        val = 123
        val = Scribe_Values.Look(val, "missingNode", int, defaultValue=42)
        Scribe.loader.FinalizeLoading()
        self.assertEqual(val, 42)

        # Invalid int → returns default
        xml_invalid = "<root><badInt>not_an_int</badInt></root>"
        Scribe.loader.InitLoadingFromString(xml_invalid)
        val = 0
        val = Scribe_Values.Look(val, "badInt", int, defaultValue=7)
        Scribe.loader.FinalizeLoading()
        self.assertEqual(val, 7)

    def test_4_string_newline_handling(self):
        path = self.temp_path('dummy.xml')

        Scribe.saver.InitSaving("root")
        value = "line1\nline2"
        value = Scribe_Values.Look(value, "myStr", str, defaultValue="")

        # Check XML uses \\n
        root_elem = Scribe.saver.baseXmlTree
        node = root_elem.find("myStr")
        self.assertIsNotNone(node)
        self.assertEqual(node.text, "line1\\nline2")
        
        Scribe.saver.FinalizeSaving(path)

        # Test loading converts back to real newline
        Scribe.loader.InitLoading(path)
        loaded_value = ""
        loaded_value = Scribe_Values.Look(loaded_value, "myStr", str, defaultValue="")
        Scribe.loader.FinalizeLoading()
        self.assertEqual(loaded_value, "line1\nline2")

    def test_5_type_serialization(self):
        path = self.temp_path('dummy.xml')

        Scribe.saver.InitSaving("root")
        value = int  # example type
        value = Scribe_Values.Look(value, "myType", type, defaultValue=None)

        root_elem = Scribe.saver.baseXmlTree.getroot()
        node = root_elem.find("myType")
        self.assertIsNotNone(node)
        # Example: saved as "builtins.int"
        self.assertEqual(node.text, "builtins:int")
        
        Scribe.saver.FinalizeSaving(path)

        # Loading back
        Scribe.loader.InitLoading(path)
        loaded_value = None
        loaded_value = Scribe_Values.Look(loaded_value, "myType", type, defaultValue=None)
        Scribe.loader.FinalizeLoading()
        self.assertIs(loaded_value, int)

    def test_6_type_complex(self):
        path = self.temp_path('dummy.xml')

        Scribe.saver.InitSaving("root")
        value = LoadIDsWantedBank.IdListRecord  # example type
        value = Scribe_Values.Look(value, "myType", type, defaultValue=None)

        root_elem = Scribe.saver.baseXmlTree.getroot()
        node = root_elem.find("myType")
        self.assertIsNotNone(node)
        # Example: saved as "utils.scribe.internal.LoadIDsWantedBank:LoadIDsWantedBank.IdListRecord"
        self.assertEqual(node.text, "utils.scribe.internal.LoadIDsWantedBank:LoadIDsWantedBank.IdListRecord")
        
        Scribe.saver.FinalizeSaving(path)

        # Loading back
        Scribe.loader.InitLoading(path)
        loaded_value = None
        loaded_value = Scribe_Values.Look(loaded_value, "myType", type, defaultValue=None)
        Scribe.loader.FinalizeLoading()
        self.assertIs(loaded_value, LoadIDsWantedBank.IdListRecord)

    def test_7_numpy_array_serialization(self):
        path = self.temp_path('dummy.xml')

        Scribe.saver.InitSaving("root")
        value = np.array([[1, 2], [3, 4]])
        value = Scribe_Values.Look(value, "myArray", np.ndarray, defaultValue=None)

        root_elem = Scribe.saver.baseXmlTree.getroot()
        node = root_elem.find("myArray")
        self.assertIsNotNone(node)
        # Typically saved as CSV string
        self.assertIsNotNone(node.text)
        self.assertEqual(node.get('dtype'), 'numpy.dtypes:Int64DType')
        self.assertEqual(node.get('shape'), '(2, 2)')
        
        Scribe.saver.FinalizeSaving(path)

        # Loading back
        Scribe.loader.InitLoading(path)
        loaded_value = None
        loaded_value = Scribe_Values.Look(loaded_value, "myArray", np.ndarray, defaultValue=None)
        Scribe.loader.FinalizeLoading()
        np.testing.assert_array_equal(loaded_value, np.array([[1, 2], [3, 4]]))

if __name__ == '__main__':
    unittest.main()

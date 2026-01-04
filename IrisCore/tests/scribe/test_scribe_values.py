from enum import Enum
import unittest

from lxml import etree as ET
import numpy as np

from tests.scribe.test_scribe_base import test_scribe_base
from utils.Log import LogLevel
from utils.debug import DebugViewSettings
from utils.scribe import Scribe, Scribe_Values

#DebugViewSettings.logLoadLevel = LogLevel.Critical

class TestEnum(Enum):
    A = 1
    B = 2

class test_scribe_values(test_scribe_base):

    def test_01_saving_and_loading_int(self):
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

    def test_02_default_value_handling(self):
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

    def test_03_loading_missing_and_invalid(self):
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

    def test_04_string_newline_handling(self):
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

    def test_05_type_serialization(self):
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

    class Test6DummyClass:
        pass

    def test_06_type_complex(self):
        path = self.temp_path('dummy.xml')

        Scribe.saver.InitSaving("root")
        value = test_scribe_values.Test6DummyClass  # example type
        value = Scribe_Values.Look(value, "myType", type, defaultValue=None)

        root_elem = Scribe.saver.baseXmlTree.getroot()
        node = root_elem.find("myType")
        self.assertIsNotNone(node)
        # Example: saved as "test_scribe_values:test_scribe_values.Test6DummyClass"
        self.assertEqual(node.text, "test_scribe_values:test_scribe_values.Test6DummyClass")
        
        Scribe.saver.FinalizeSaving(path)

        # Loading back
        Scribe.loader.InitLoading(path)
        loaded_value = None
        loaded_value = Scribe_Values.Look(loaded_value, "myType", type, defaultValue=None)
        Scribe.loader.FinalizeLoading()
        self.assertIs(loaded_value, test_scribe_values.Test6DummyClass)

    def test_07_numpy_array_serialization(self):
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
        self.assertEqual(node.get('shape'), '2, 2')
        
        Scribe.saver.FinalizeSaving(path)

        # Loading back
        Scribe.loader.InitLoading(path)
        loaded_value = None
        loaded_value = Scribe_Values.Look(loaded_value, "myArray", np.ndarray, defaultValue=None)
        Scribe.loader.FinalizeLoading()
        np.testing.assert_array_equal(loaded_value, np.array([[1, 2], [3, 4]]))

    def test_08_enum_saving(self):
        path = self.temp_path("enum_save.xml")

        value = TestEnum.B

        Scribe.saver.InitSaving("root")
        value = Scribe_Values.Look(
            value, "enumVal", TestEnum, defaultValue=TestEnum.A
        )
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()

        node = root.find("enumVal")
        self.assertIsNotNone(node)
        self.assertEqual(node.text, "B")

    def test_09_enum_loading(self):
        path = self.temp_path("enum_load.xml")

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
            <root>
                <enumVal>B</enumVal>
            </root>
            """)

        Scribe.loader.InitLoading(path)

        value = TestEnum.A
        value = Scribe_Values.Look(
            value, "enumVal", TestEnum, defaultValue=TestEnum.A
        )

        Scribe.loader.FinalizeLoading()

        self.assertEqual(value, TestEnum.B)

    def test_10_enum_invalid_returns_default(self):
        path = self.temp_path("enum_invalid.xml")

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
            <root>
                <enumVal>INVALID</enumVal>
            </root>
            """)

        Scribe.loader.InitLoading(path)

        value = TestEnum.B
        value = Scribe_Values.Look(
            value, "enumVal", TestEnum, defaultValue=TestEnum.A
        )

        Scribe.loader.FinalizeLoading()

        self.assertEqual(value, TestEnum.A)



if __name__ == '__main__':
    unittest.main()

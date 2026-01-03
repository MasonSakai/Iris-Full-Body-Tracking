import unittest
from lxml import etree as ET

from tests.scribe.test_scribe_base import test_scribe_base
from utils.Log import LogLevel
from utils.debug import DebugViewSettings
from utils.scribe import IExposable, Scribe, Scribe_Deep, Scribe_Values, Scribe_Collections

#DebugViewSettings.logLoadLevel = LogLevel.Critical

class SimpleExposable(IExposable):
    def __init__(self, x=0):
        self.x = x

    def ExposeData(self):
        self.x = Scribe_Values.Look(self.x, "x", int, defaultValue=0)

class ContainerExposable(IExposable):
    def __init__(self):
        self.items = [SimpleExposable(1)]
        self.after = 99

    def ExposeData(self):
        self.items = Scribe_Collections.LookList(
            self.items, "items", SimpleExposable, Scribe_Collections.LookMode.Deep
        )
        self.after = Scribe_Values.Look(self.after, "after", int)


class test_scribe_collections(test_scribe_base):

    def test_1_looklist_value_saving(self):
        path = self.temp_path("list_values.xml")

        values = [1, 2, 3]

        Scribe.saver.InitSaving("root")
        values = Scribe_Collections.LookList(
            values, "ints", int, Scribe_Collections.LookMode.Value
        )
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()

        ints_node = root.find("ints")
        self.assertIsNotNone(ints_node)

        elems = ints_node.findall("li")
        self.assertEqual(len(elems), 3)
        self.assertEqual([e.text for e in elems], ["1", "2", "3"])

    def test_2_looklist_value_loading(self):
        path = self.temp_path("list_values_load.xml")

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
            <root>
                <ints>
                    <li>4</li>
                    <li>5</li>
                </ints>
            </root>
            """)

        Scribe.loader.InitLoading(path)
        values = None
        values = Scribe_Collections.LookList(
            values, "ints", int, Scribe_Collections.LookMode.Value
        )
        Scribe.loader.FinalizeLoading()

        self.assertEqual(values, [4, 5])

    def test_3_looklist_missing_node(self):
        path = self.temp_dummy("list_missing.xml")

        Scribe.loader.InitLoading(path)
        values = []
        values = Scribe_Collections.LookList(
            values, "missing", int, Scribe_Collections.LookMode.Value
        )
        Scribe.loader.FinalizeLoading()

        self.assertIsNone(values)

    def test_4_looklist_deep_saving(self):
        path = self.temp_path("list_deep.xml")

        values = [SimpleExposable(1), SimpleExposable(2)]

        Scribe.saver.InitSaving("root")
        values = Scribe_Collections.LookList(
            values, "objs", SimpleExposable, Scribe_Collections.LookMode.Deep
        )
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()

        objs = root.find("objs")
        self.assertIsNotNone(objs)

        items = objs.findall("li")
        self.assertEqual(len(items), 2)

        self.assertEqual(items[0].find("x").text, "1")
        self.assertEqual(items[1].find("x").text, "2")

    def test_5_looklist_deep_loading(self):
        path = self.temp_path("list_deep_load.xml")

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
            <root>
                <objs>
                    <li><x>10</x></li>
                    <li><x>20</x></li>
                </objs>
            </root>
            """)

        Scribe.loader.InitLoading(path)
        values = None
        values = Scribe_Collections.LookList(
            values, "objs", SimpleExposable, Scribe_Collections.LookMode.Deep
        )
        Scribe.loader.FinalizeLoading()

        self.assertEqual(len(values), 2)
        self.assertEqual(values[0].x, 10)
        self.assertEqual(values[1].x, 20)

    def test_6_collection_restores_parent(self):
        path = self.temp_path("list_parent.xml")

        obj = ContainerExposable()

        Scribe.saver.InitSaving("root")
        obj = Scribe_Deep.Look(obj, "container", ContainerExposable)
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()
        container = root.find("container")

        # 'after' must NOT be inside the list
        self.assertIsNotNone(container.find("after"))
        self.assertIsNone(container.find("items/after"))

    @unittest.skip("LookDict not implemented yet")
    def test_7_lookdict_value_value(self):
        path = self.temp_path("dict_value_value.xml")

        data = {"a": 1, "b": 2}

        Scribe.saver.InitSaving("root")
        data = Scribe_Collections.LookDict(
            data,
            "dict",
            str,
            int,
            Scribe_Collections.LookMode.Value,
            Scribe_Collections.LookMode.Value,
        )
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()
        node = root.find("dict")

        self.assertIsNotNone(node)
        self.assertEqual(len(node.findall("li")), 2)

    @unittest.skip("LookDict not implemented yet")
    def test_8_lookdict_value_deep(self):
        path = self.temp_path("dict_value_deep.xml")

        data = {"one": SimpleExposable(1)}

        Scribe.saver.InitSaving("root")
        data = Scribe_Collections.LookDict(
            data,
            "dict",
            str,
            SimpleExposable,
            Scribe_Collections.LookMode.Value,
            Scribe_Collections.LookMode.Deep,
        )
        Scribe.saver.FinalizeSaving(path)

        tree = ET.parse(path)
        root = tree.getroot()

        val = root.find("dict/li/value/x")
        self.assertIsNotNone(val)
        self.assertEqual(val.text, "1")

    @unittest.skip("LookDict not implemented yet")
    def test_9_lookdict_missing_node(self):
        path = self.temp_dummy("dict_missing.xml")

        Scribe.loader.InitLoading(path)
        data = {"x": 99}
        data = Scribe_Collections.LookDict(
            data,
            "missing",
            str,
            int,
            Scribe_Collections.LookMode.Value,
            Scribe_Collections.LookMode.Value,
        )
        Scribe.loader.FinalizeLoading()

        self.assertIsNone(data)






if __name__ == '__main__':
    unittest.main()

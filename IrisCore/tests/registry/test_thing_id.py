import unittest

from utils.registry import IThing, ThingIDManager


class test_thing_db(unittest.TestCase):

    def setUp(self):
        ThingIDManager._allocated_ids.clear()
        ThingIDManager._type_names.clear()

    def test_01_class_without_name_is_not_registered(self):
        class TestThing(IThing):
            pass

        self.assertEqual({}, ThingIDManager._type_names)


    def test_02_named_class_is_registered(self):
        class TestThing(IThing, ThingName="TestThing"):
            pass

        self.assertEqual(
            {TestThing: "TestThing"},
            ThingIDManager._type_names
        )
    
    def test_03_child_inherits_parent_name(self):
        class Parent(IThing, ThingName="Thing"):
            pass

        class Child(Parent):
            pass

        self.assertIs(
            ThingIDManager.get_class(Child),
            Parent
        )

    def test_04_child_can_override_name(self):
        class Parent(IThing, ThingName="Thing"):
            pass

        class Child(Parent, ThingName="Child"):
            pass

        self.assertIs(
            ThingIDManager.get_class(Child),
            Child
        )

    def test_05_missing_name_raises(self):
        class Parent(IThing):
            pass

        class Child(Parent):
            pass

        with self.assertRaises(RuntimeError):
            ThingIDManager.get_class(Child)

    def test_06_generated_ids_are_unique(self):
        class TestThing(IThing, ThingName="Thing"):
            pass

        ids = {
            TestThing().ThingID
            for _ in range(1000)
        }

        self.assertEqual(1000, len(ids))

    def test_07_thingid_is_stable(self):
        class TestThing(IThing, ThingName="Thing"):
            pass

        thing = TestThing()

        first = thing.ThingID
        second = thing.ThingID

        self.assertEqual(first, second)

    def test_08_subclasses_share_namespace(self):
        class Base(IThing, ThingName="Thing"):
            pass

        class A(Base):
            pass

        class B(Base):
            pass

        a = A()
        b = B()

        self.assertNotEqual(a.ThingID, b.ThingID)

    def test_09_register_existing_prevents_reuse(self):
        class TestThing(IThing, ThingName="Thing"):
            pass

        thing = TestThing()
        thing._thing_id = "Thing1234"

        ThingIDManager.register(thing)

        self.assertIn(
            "Thing1234",
            ThingIDManager._allocated_ids[TestThing]
        )




if __name__ == '__main__':
    unittest.main()

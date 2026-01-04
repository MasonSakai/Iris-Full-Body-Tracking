import unittest

from utils.registry import CreateThingDatabase, HasThingDatabase, IThing, ThingDatabase

class TestThing(IThing):
    def __init__(self, name: str):
        self._name = name
        self._index = -1
        self.post_set_called = False

    def ThingName(self) -> str:
        return self._name

    def PostSetIndices(self):
        self.post_set_called = True


class test_thing_db(unittest.TestCase):

    def setUp(self):
        if HasThingDatabase(TestThing):
            ThingDatabase(TestThing).Clear()

    def test_01_create_and_get_database(self):
        self.assertFalse(HasThingDatabase(TestThing))

        db = CreateThingDatabase(TestThing)

        self.assertTrue(HasThingDatabase(TestThing))
        self.assertIs(db, ThingDatabase(TestThing))

    def test_02_indices_assigned_on_add(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing("A")
        b = TestThing("B")

        db.Add(a)
        db.Add(b)

        self.assertEqual(a._index, 0)
        self.assertEqual(b._index, 1)

    def test_03_get_named_success(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing("Alpha")
        db.Add(a)

        self.assertIs(db.GetNamed("Alpha"), a)

    def test_04_getnamed_missing(self):
        db = CreateThingDatabase(TestThing)

        self.assertIsNone(
            db.GetNamed("Missing", errorOnFail=False)
        )

    def test_05_duplicate_names_last_wins(self):
        db = CreateThingDatabase(TestThing)

        a1 = TestThing("Dup")
        a2 = TestThing("Dup")

        db.Add(a1)
        db.Add(a2)

        self.assertIs(db.GetNamed("Dup"), a2)
        self.assertIn(a1, db.AllThingsListForReading())

    def test_06_set_indices_assigns_sequential_indices(self):
        db = CreateThingDatabase(TestThing)

        things = [TestThing(f"T{i}") for i in range(5)]
        db.Add(*things)

        for i, t in enumerate(things):
            self.assertEqual(t._index, i)

    def test_07_setindices_is_optional(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing("A")
        b = TestThing("B")

        db.Add(a, b)
        db.Remove(a)

        # stale index is acceptable
        self.assertEqual(b._index, 1)

        db.SetIndices()
        self.assertEqual(b._index, 0)

    def test_08_remove_things(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing("A")
        b = TestThing("B")

        db.Add(a, b)
        db.Remove(a)

        self.assertEqual(db.ThingCount(), 1)
        self.assertNotIn(a, db.AllThings())
        self.assertIn(b, db.AllThings())

    def test_09_remove_does_not_reindex(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing("A")
        b = TestThing("B")
        c = TestThing("C")

        db.Add(a, b, c)
        db.Remove(b)

        self.assertEqual(a._index, 0)
        self.assertEqual(c._index, 2)  # stale but expected

    def test_10_mutable_add_remove_visibility(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing("A")
        db.Add(a)

        self.assertIn(a, db.AllThings())

        db.Remove(a)
        self.assertNotIn(a, db.AllThings())

    def test_11_setindices_reassigns_and_calls_post(self):
        db = CreateThingDatabase(TestThing)

        things = [TestThing(str(i)) for i in range(3)]
        db.Add(*things)

        # corrupt indices intentionally
        things[0]._index = 10

        db.SetIndices()

        for i, t in enumerate(things):
            self.assertEqual(t._index, i)
            self.assertTrue(t.post_set_called)

    def test_12_clear_resets_database(self):
        db = CreateThingDatabase(TestThing)

        db.Add(TestThing("A"), TestThing("B"))
        db.Clear()

        self.assertEqual(db.ThingCount(), 0)
        self.assertEqual(list(db.AllThings()), [])

    def test_13_get_random(self):
        db = CreateThingDatabase(TestThing)

        things = [TestThing(str(i)) for i in range(10)]
        db.Add(*things)

        rand = db.GetRandom()
        self.assertIn(rand, things)

    def test_14_allthingslistforreading_is_live(self):
        db = CreateThingDatabase(TestThing)

        lst = db.AllThingsListForReading()
        self.assertIs(lst, db.AllThingsListForReading())

        t = TestThing("X")
        db.Add(t)

        self.assertIn(t, lst)



if __name__ == '__main__':
    unittest.main()

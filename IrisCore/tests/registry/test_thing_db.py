import unittest

from utils.registry import CreateThingDatabase, HasThingDatabase, IThing, ThingDatabase

class TestThing(IThing):
    def __init__(self, name: str):
        self._name = name
        self.post_set_called = False

    def ThingID(self) -> str:
        return self._name


class test_thing_db(unittest.TestCase):

    def setUp(self):
        if HasThingDatabase(TestThing):
            ThingDatabase(TestThing).Clear()

    def test_01_create_and_get_database(self):
        self.assertFalse(HasThingDatabase(TestThing))

        db = CreateThingDatabase(TestThing)

        self.assertTrue(HasThingDatabase(TestThing))
        self.assertIs(db, ThingDatabase(TestThing))

    def test_02_get_named_success(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing("Alpha")
        db.Add(a)

        self.assertIs(db.Get("Alpha"), a)

    def test_03_getnamed_missing(self):
        db = CreateThingDatabase(TestThing)

        self.assertIsNone(
            db.Get("Missing", errorOnFail=False)
        )

    def test_04_duplicate_names_last_wins(self):
        db = CreateThingDatabase(TestThing)

        a1 = TestThing("Dup")
        a2 = TestThing("Dup")

        db.Add(a1)
        db.Add(a2)

        self.assertIs(db.Get("Dup"), a2)
        self.assertIn(a1, db.AllThingsListForReading())

    def test_05_remove_things(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing("A")
        b = TestThing("B")

        db.Add(a, b)
        db.Remove(a)

        self.assertEqual(db.ThingCount(), 1)
        self.assertNotIn(a, db.AllThings())
        self.assertIn(b, db.AllThings())

    def test_06_mutable_add_remove_visibility(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing("A")
        db.Add(a)

        self.assertIn(a, db.AllThings())

        db.Remove(a)
        self.assertNotIn(a, db.AllThings())

    def test_07_clear_resets_database(self):
        db = CreateThingDatabase(TestThing)

        db.Add(TestThing("A"), TestThing("B"))
        db.Clear()

        self.assertEqual(db.ThingCount(), 0)
        self.assertEqual(list(db.AllThings()), [])

    def test_08_get_random(self):
        db = CreateThingDatabase(TestThing)

        things = [TestThing(str(i)) for i in range(10)]
        db.Add(*things)

        rand = db.GetRandom()
        self.assertIn(rand, things)

    def test_09_allthingslistforreading_is_live(self):
        db = CreateThingDatabase(TestThing)

        lst = db.AllThingsListForReading()
        self.assertIs(lst, db.AllThingsListForReading())

        t = TestThing("X")
        db.Add(t)

        self.assertIn(t, lst)



if __name__ == '__main__':
    unittest.main()

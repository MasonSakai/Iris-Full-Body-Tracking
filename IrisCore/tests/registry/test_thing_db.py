import unittest

from utils.registry import CreateThingDatabase, HasThingDatabase, IThing, ThingDatabase

class TestThing(IThing, ThingName='TestThing'):
    pass


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

        a = TestThing()
        db.Add(a)

        self.assertIs(db.Get(a.ThingID), a)

    def test_03_getnamed_missing(self):
        db = CreateThingDatabase(TestThing)

        self.assertIsNone(
            db.Get("Missing", errorOnFail=False)
        )


    def test_05_remove_things(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing()
        b = TestThing()

        db.Add(a, b)
        db.Remove(a)

        self.assertEqual(db.ThingCount(), 1)
        self.assertNotIn(a, db.AllThings())
        self.assertIn(b, db.AllThings())

    def test_06_mutable_add_remove_visibility(self):
        db = CreateThingDatabase(TestThing)

        a = TestThing()
        db.Add(a)

        self.assertIn(a, db.AllThings())

        db.Remove(a)
        self.assertNotIn(a, db.AllThings())

    def test_07_clear_resets_database(self):
        db = CreateThingDatabase(TestThing)

        db.Add(TestThing(), TestThing())
        db.Clear()

        self.assertEqual(db.ThingCount(), 0)
        self.assertEqual(list(db.AllThings()), [])

    def test_08_get_random(self):
        db = CreateThingDatabase(TestThing)

        things = [TestThing() for i in range(10)]
        db.Add(*things)

        rand = db.GetRandom()
        self.assertIn(rand, things)

    def test_09_allthingslistforreading_is_live(self):
        db = CreateThingDatabase(TestThing)

        lst = db.AllThingsListForReading()
        self.assertIs(lst, db.AllThingsListForReading())

        t = TestThing()
        db.Add(t)

        self.assertIn(t, lst)



if __name__ == '__main__':
    unittest.main()

'''
    In order to run the tester:
    1.  Make sure your AVLTree.py file and this file
        are both in the same directory.
    2.  Run: python3 student_tester.py
    3.  Your grade will be printed at the end.
        Only failed tests will be printed.
'''

import unittest
from AVLTree import AVLTree

GRADE = 0
MAX_GRADE = 10
TEST_COUNT = 9
POINTS_PER_TEST = MAX_GRADE / TEST_COUNT


class BasicStudentTester(unittest.TestCase):

    def setUp(self):
        self.T = AVLTree(True)

    def add_points(self):
        global GRADE
        GRADE += POINTS_PER_TEST

    def test_insert_small(self):
        self.T.insert(10, "10")
        self.T.insert(5, "5")
        self.T.insert(15, "15")

        self.assertEqual(self.T.size(), 3)
        self.assertIsNotNone(self.T.search(10)[0])
        self.assertIsNotNone(self.T.search(5)[0])
        self.assertIsNotNone(self.T.search(15)[0])

        self.add_points()

    def test_delete_small(self):
        for i in range(5):
            self.T.insert(i, str(i))

        self.assertEqual(self.T.size(), 5)

        self.T.delete(self.T.search(0)[0])
        self.T.delete(self.T.search(3)[0])

        self.assertEqual(self.T.size(), 3)

        self.add_points()

    def test_insert_delete_mix(self):
        nums = [7, 3, 9, 1, 5]
        for x in nums:
            self.T.insert(x, str(x))

        self.assertEqual(self.T.size(), 5)

        self.T.delete(self.T.search(5)[0])
        self.assertEqual(self.T.size(), 4)

        self.T.insert(20, "20")
        self.assertEqual(self.T.size(), 5)

        self.add_points()

    def test_search_time_root_found(self):
        self.T.insert(46, "46")

        node, search_time = self.T.search(46)

        self.assertIsNotNone(node)
        self.assertEqual(node.key, 46)
        self.assertEqual(search_time, 1)

        self.add_points()

    def test_search_time_root_missing_left(self):
        self.T.insert(46, "46")

        node, search_time = self.T.search(17)

        self.assertIsNone(node)
        self.assertEqual(search_time, 2)

        self.add_points()

    def test_search_time_left_child_found(self):
        self.T.insert(46, "46")
        self.T.insert(17, "17")

        node, search_time = self.T.search(17)

        self.assertIsNotNone(node)
        self.assertEqual(node.key, 17)
        self.assertEqual(search_time, 2)

        self.add_points()

    def test_search_time_right_of_left_missing(self):
        self.T.insert(46, "46")
        self.T.insert(17, "17")

        node, search_time = self.T.search(18)

        self.assertIsNone(node)
        self.assertEqual(search_time, 3)

        self.add_points()

    def test_insert_metrics_double_rotation_example(self):
        self.T.insert(3, "3")
        self.T.insert(1, "1")
        node, search_time, rotations, height_changes = self.T.insert(2, "2")

        self.assertIsNotNone(node)
        self.assertEqual(node.key, 2)
        self.assertEqual(search_time, 3)
        self.assertEqual(rotations, 2)
        self.assertEqual(height_changes, 1)

        self.add_points()

    def test_insert_metrics_single_rotation_example(self):
        self.T.insert(3, "3")
        self.T.insert(4, "4")
        node, search_time, rotations, height_changes = self.T.insert(5, "5")

        self.assertIsNotNone(node)
        self.assertEqual(node.key, 5)
        self.assertEqual(search_time, 3)
        self.assertEqual(rotations, 1)
        self.assertEqual(height_changes, 1)

        self.add_points()


if __name__ == "__main__":
    print("Running Student Tester...\n")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BasicStudentTester)
    result = unittest.TextTestRunner(verbosity=0).run(suite)

    print("\n==============================")
    print("       TESTER SUMMARY")
    print("==============================")

    if result.failures or result.errors:
        print("\nFailed Tests:")
        for test, err in result.failures + result.errors:
            test_name = test.id().split(".")[-1]
            print(f"  - {test_name}")
            print(f"    {err.splitlines()[-1]}")
    else:
        print("\nAll tests passed!")

    print(f"\nGrade: {GRADE:.1f} / {MAX_GRADE}")
    print("==============================")

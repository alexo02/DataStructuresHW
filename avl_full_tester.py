"""
Full tester for the Data Structures AVL/BST project.

How to run:
1. Put this file in the same folder as your AVLTree.py.
2. Run:
       python avl_full_tester.py
3. For heavier randomized tests, run:
       python avl_full_tester.py --stress

The tester assumes the public API from the assignment:
AVLTree(is_avl), search, insert, delete, avl_to_list, size, get_root, get_height.
"""

import math
import random
import sys
import unittest

STRESS = "--stress" in sys.argv
if STRESS:
    sys.argv.remove("--stress")

sys.setrecursionlimit(100000)

try:
    from AVLTree import AVLTree, AVLNode
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "Could not import AVLTree.py. Put avl_full_tester.py in the same folder as AVLTree.py."
    ) from exc


def is_real(node):
    if node is None:
        return False
    if not hasattr(node, "is_real_node"):
        raise AssertionError(f"Node {node!r} has no is_real_node() method")
    try:
        return bool(node.is_real_node())
    except Exception as ex:
        raise AssertionError(f"is_real_node() raised an exception for node {node!r}: {ex}") from ex


def node_key(node):
    return getattr(node, "key", "<missing key>")


def expected_search_from_current_tree(tree, key):
    """Return (expected_node_or_None, expected_search_time) from the current shape of the tree."""
    root = tree.get_root()
    if root is None:
        return None, 1

    if not is_real(root):
        raise AssertionError("get_root() returned a virtual node instead of None or a real root")

    current = root
    visited_real_nodes = 0
    seen = set()

    while current is not None and is_real(current):
        if id(current) in seen:
            raise AssertionError("Cycle detected while calculating expected search_time")
        seen.add(id(current))

        visited_real_nodes += 1
        if key == current.key:
            return current, visited_real_nodes
        if key < current.key:
            current = current.left
        else:
            current = current.right

    return None, visited_real_nodes + 1


def assert_search_exact(testcase, tree, key):
    expected_node, expected_time = expected_search_from_current_tree(tree, key)
    actual_node, actual_time = tree.search(key)

    testcase.assertEqual(
        actual_time,
        expected_time,
        f"Wrong search_time for search({key}). Expected {expected_time}, got {actual_time}.",
    )

    if expected_node is None:
        testcase.assertIsNone(actual_node, f"search({key}) should return None for missing key")
    else:
        testcase.assertIs(
            actual_node,
            expected_node,
            f"search({key}) should return the exact node object stored in the tree",
        )


def validate_tree(testcase, tree, expected_items, is_avl, *, require_shared_virtual=True):
    """
    Validate all structural invariants against expected_items, a dict key -> value.
    This function is intentionally strict.
    """
    expected_pairs = sorted(expected_items.items())

    testcase.assertEqual(tree.size(), len(expected_items), "size() returned a wrong value")
    testcase.assertEqual(
        tree.avl_to_list(),
        expected_pairs,
        "avl_to_list() must return sorted (key, value) tuples",
    )

    root = tree.get_root()
    if len(expected_items) == 0:
        testcase.assertIsNone(root, "get_root() must return None for an empty tree")
        testcase.assertEqual(tree.get_height(), -1, "get_height() must return -1 for an empty tree")
        return

    testcase.assertIsNotNone(root, "get_root() returned None for a non-empty tree")
    testcase.assertTrue(is_real(root), "get_root() must return a real node")
    testcase.assertIsNone(root.parent, "The root parent must be None")

    seen_real_ids = set()
    virtual_ids = set()

    def walk(node, lo, hi):
        testcase.assertIsNotNone(node, "Real nodes must use virtual children, not None")

        if not is_real(node):
            virtual_ids.add(id(node))
            testcase.assertEqual(
                getattr(node, "height", None),
                -1,
                "A virtual node must have height -1",
            )
            return -1, 0, []

        testcase.assertNotIn(id(node), seen_real_ids, "Cycle or duplicate real node reference detected")
        seen_real_ids.add(id(node))

        testcase.assertIn(node.key, expected_items, f"Unexpected key found in tree: {node.key}")
        testcase.assertEqual(
            node.value,
            expected_items[node.key],
            f"Wrong value stored for key {node.key}",
        )

        if lo is not None:
            testcase.assertGreater(node.key, lo, f"BST violation: key {node.key} is not greater than {lo}")
        if hi is not None:
            testcase.assertLess(node.key, hi, f"BST violation: key {node.key} is not smaller than {hi}")

        testcase.assertIsNotNone(node.left, f"Node {node.key} has left=None. Use a virtual node.")
        testcase.assertIsNotNone(node.right, f"Node {node.key} has right=None. Use a virtual node.")

        left_height, left_count, left_keys = walk(node.left, lo, node.key)
        if is_real(node.left):
            testcase.assertIs(
                node.left.parent,
                node,
                f"Wrong parent pointer for left child of key {node.key}",
            )

        right_height, right_count, right_keys = walk(node.right, node.key, hi)
        if is_real(node.right):
            testcase.assertIs(
                node.right.parent,
                node,
                f"Wrong parent pointer for right child of key {node.key}",
            )

        real_height = max(left_height, right_height) + 1

        if is_avl:
            testcase.assertEqual(
                node.height,
                real_height,
                f"Wrong height field at key {node.key}. Expected {real_height}, got {node.height}",
            )
            testcase.assertLessEqual(
                abs(left_height - right_height),
                1,
                f"AVL violation at key {node.key}: left height {left_height}, right height {right_height}",
            )

        return real_height, left_count + right_count + 1, left_keys + [node.key] + right_keys

    height, count, inorder_keys = walk(root, None, None)

    testcase.assertEqual(count, len(expected_items), "Tree contains the wrong number of real nodes")
    testcase.assertEqual(inorder_keys, sorted(expected_items), "In-order traversal is not sorted as expected")
    testcase.assertEqual(tree.get_height(), height, "get_height() returned the wrong tree height")

    if is_avl:
        testcase.assertEqual(root.height, height, "In AVL mode, root.height must match get_height()")
        # Safe AVL height upper bound. This is looser than the exact AVL bound.
        upper = math.ceil(2 * math.log2(len(expected_items) + 2)) + 2
        testcase.assertLessEqual(
            height,
            upper,
            f"AVL tree is too tall: height {height}, size {len(expected_items)}",
        )

    if require_shared_virtual:
        testcase.assertEqual(
            len(virtual_ids),
            1,
            "All missing children must point to one shared virtual node for the whole tree",
        )


def insert_and_check(testcase, tree, expected_items, key, value, is_avl, *, exact_rotations=None, exact_height_changes=None):
    _, expected_time = expected_search_from_current_tree(tree, key)
    result = tree.insert(key, value)

    testcase.assertIsInstance(result, tuple, "insert() must return a tuple")
    testcase.assertEqual(len(result), 4, "insert() must return (x, search_time, rotations, height_changes)")

    node, search_time, rotations, height_changes = result

    testcase.assertTrue(is_real(node), "insert() must return the inserted real node")
    testcase.assertEqual(node.key, key, "insert() returned a node with the wrong key")
    testcase.assertEqual(node.value, value, "insert() returned a node with the wrong value")
    testcase.assertEqual(search_time, expected_time, f"Wrong insert search_time for key {key}")

    if is_avl:
        testcase.assertIsInstance(rotations, int, "rotations must be an int")
        testcase.assertIsInstance(height_changes, int, "height_changes must be an int")
        testcase.assertGreaterEqual(rotations, 0, "rotations cannot be negative")
        testcase.assertLessEqual(rotations, 2, "AVL insertion can use at most 2 rotations")
        testcase.assertGreaterEqual(height_changes, 0, "height_changes cannot be negative")
        if exact_rotations is not None:
            testcase.assertEqual(
                rotations,
                exact_rotations,
                f"Wrong rotations count for insert({key})",
            )
        if exact_height_changes is not None:
            testcase.assertEqual(
                height_changes,
                exact_height_changes,
                f"Wrong height_changes count for insert({key})",
            )
    else:
        testcase.assertEqual(rotations, 0, "BST mode must return rotations=0")
        testcase.assertEqual(height_changes, 0, "BST mode must return height_changes=0")

    expected_items[key] = value
    validate_tree(testcase, tree, expected_items, is_avl)
    assert_search_exact(testcase, tree, key)
    return node


def delete_key_and_check(testcase, tree, expected_items, key, is_avl):
    node, search_time = tree.search(key)
    testcase.assertIsNotNone(node, f"Test bug: key {key} should exist before delete")
    testcase.assertTrue(is_real(node), f"search({key}) returned a non-real node before delete")
    before_size = len(expected_items)

    result = tree.delete(node)
    testcase.assertIsNone(result, "delete() should not return a value")

    expected_items.pop(key)
    validate_tree(testcase, tree, expected_items, is_avl)
    testcase.assertEqual(tree.size(), before_size - 1, "size() did not decrease after delete()")
    missing_node, _ = tree.search(key)
    testcase.assertIsNone(missing_node, f"Deleted key {key} is still searchable")


class TestEmptyAndBasicAPI(unittest.TestCase):
    def test_empty_tree_contract(self):
        for is_avl in (False, True):
            with self.subTest(is_avl=is_avl):
                tree = AVLTree(is_avl)
                validate_tree(self, tree, {}, is_avl)
                for key in [0, -1, 999999999]:
                    assert_search_exact(self, tree, key)

    def test_direct_real_node_contract(self):
        node = AVLNode(123, "abc")
        self.assertTrue(node.is_real_node(), "AVLNode created with an int key should be real")
        self.assertEqual(node.key, 123)
        self.assertEqual(node.value, "abc")


class TestKnownAVLInsertCounts(unittest.TestCase):
    def assert_sequence(self, keys, expected_stats, expected_root_key):
        tree = AVLTree(True)
        expected = {}
        for key, (search_time, rotations, height_changes) in zip(keys, expected_stats):
            _, expected_time_from_shape = expected_search_from_current_tree(tree, key)
            self.assertEqual(
                expected_time_from_shape,
                search_time,
                f"Test expectation mismatch before inserting {key}",
            )
            insert_and_check(
                self,
                tree,
                expected,
                key,
                f"v{key}",
                True,
                exact_rotations=rotations,
                exact_height_changes=height_changes,
            )
        self.assertEqual(tree.get_root().key, expected_root_key)

    def test_ll_rotation(self):
        self.assert_sequence(
            [30, 20, 10],
            [(1, 0, 0), (2, 0, 1), (3, 1, 1)],
            20,
        )

    def test_rr_rotation(self):
        self.assert_sequence(
            [10, 20, 30],
            [(1, 0, 0), (2, 0, 1), (3, 1, 1)],
            20,
        )

    def test_lr_double_rotation(self):
        self.assert_sequence(
            [30, 10, 20],
            [(1, 0, 0), (2, 0, 1), (3, 2, 1)],
            20,
        )

    def test_rl_double_rotation(self):
        self.assert_sequence(
            [10, 30, 20],
            [(1, 0, 0), (2, 0, 1), (3, 2, 1)],
            20,
        )

    def test_height_does_not_always_change(self):
        self.assert_sequence(
            [20, 10, 30],
            [(1, 0, 0), (2, 0, 1), (2, 0, 0)],
            20,
        )

    def test_assignment_page_4_style_case(self):
        tree = AVLTree(True)
        expected = {}
        for key in [2, 1, 3, 4]:
            insert_and_check(self, tree, expected, key, f"v{key}", True)
        self.assertEqual(tree.get_root().key, 2)
        self.assertEqual(tree.get_height(), 2)

        # This mirrors the small example in the assignment: inserting 5 causes one height change and one rotation.
        insert_and_check(
            self,
            tree,
            expected,
            5,
            "v5",
            True,
            exact_rotations=1,
            exact_height_changes=1,
        )
        self.assertEqual(tree.get_root().key, 2)


class TestBSTMode(unittest.TestCase):
    def test_sorted_insert_creates_chain_in_bst_mode(self):
        tree = AVLTree(False)
        expected = {}
        n = 60
        for key in range(1, n + 1):
            insert_and_check(self, tree, expected, key, str(key), False)
            self.assertEqual(tree.get_height(), key - 1, "Sorted BST insertion should create a chain")
            self.assertEqual(tree.get_root().key, 1, "BST mode must not rotate")

        for key in [1, 2, 30, 60, 61, 0]:
            assert_search_exact(self, tree, key)

    def test_bst_deletion_shapes(self):
        tree = AVLTree(False)
        expected = {}
        keys = [50, 30, 70, 20, 40, 60, 80, 35, 45, 65, -10, 0, 999999]
        for key in keys:
            insert_and_check(self, tree, expected, key, f"value:{key}", False)

        # leaf, one-child cases, two-child cases, root deletion, negative and large keys.
        for key in [20, 60, 40, 70, 50, -10, 999999, 0, 30, 35, 45, 65, 80]:
            delete_key_and_check(self, tree, expected, key, False)

        validate_tree(self, tree, {}, False)

    def test_weird_values_and_keys(self):
        tree = AVLTree(False)
        expected = {}
        cases = [
            (0, ""),
            (-5, "שלום"),
            (5, "emoji 🙂"),
            (-10**9, "min-ish"),
            (10**9, "max-ish"),
            (42, "line1\\nline2"),
        ]
        for key, value in cases:
            insert_and_check(self, tree, expected, key, value, False)
        for key, _ in cases:
            assert_search_exact(self, tree, key)
        for key, _ in reversed(cases):
            delete_key_and_check(self, tree, expected, key, False)


class TestAVLModeGeneral(unittest.TestCase):
    def test_sorted_insert_stays_balanced(self):
        tree = AVLTree(True)
        expected = {}
        n = 200 if not STRESS else 800
        total_rotations = 0
        total_height_changes = 0

        for key in range(1, n + 1):
            _, st, rotations, height_changes = tree.insert(key, str(key))
            expected[key] = str(key)
            total_rotations += rotations
            total_height_changes += height_changes
            self.assertLessEqual(rotations, 2, "Each AVL insert should have at most 2 rotations")
            if key <= 100 or key % 50 == 0 or key == n:
                validate_tree(self, tree, expected, True)

        validate_tree(self, tree, expected, True)
        self.assertGreater(total_rotations, 0, "Sorted AVL insertion should require rotations")
        self.assertGreater(total_height_changes, 0, "Sorted AVL insertion should require height changes")

    def test_random_insert_delete_avl(self):
        n = 120 if not STRESS else 300
        for seed in range(5 if not STRESS else 8):
            with self.subTest(seed=seed):
                rng = random.Random(seed)
                keys = rng.sample(range(-10 * n, 10 * n), n)
                tree = AVLTree(True)
                expected = {}

                for i, key in enumerate(keys):
                    insert_and_check(self, tree, expected, key, f"v:{key}", True)
                    if i % 17 == 0:
                        for probe in rng.sample(keys[: i + 1], min(i + 1, 5)):
                            assert_search_exact(self, tree, probe)
                        for missing in [10 * n + seed, -10 * n - seed, key + 1]:
                            if missing not in expected:
                                assert_search_exact(self, tree, missing)

                delete_order = keys[:]
                rng.shuffle(delete_order)
                for i, key in enumerate(delete_order):
                    delete_key_and_check(self, tree, expected, key, True)
                    if expected and i % 19 == 0:
                        for probe in rng.sample(list(expected.keys()), min(len(expected), 5)):
                            assert_search_exact(self, tree, probe)

                validate_tree(self, tree, {}, True)

    def test_delete_root_repeatedly(self):
        for is_avl in (False, True):
            with self.subTest(is_avl=is_avl):
                tree = AVLTree(is_avl)
                expected = {}
                keys = [8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15]
                for key in keys:
                    insert_and_check(self, tree, expected, key, str(key), is_avl)

                while expected:
                    root = tree.get_root()
                    self.assertIsNotNone(root)
                    delete_key_and_check(self, tree, expected, root.key, is_avl)

    def test_delete_many_after_perfectish_avl(self):
        tree = AVLTree(True)
        expected = {}
        keys = list(range(1, 64))
        for key in keys:
            insert_and_check(self, tree, expected, key, str(key), True)

        # This order tends to expose bugs in rebalance-after-delete and root replacement.
        delete_order = [
            1, 2, 3, 4, 5, 6, 7, 8,
            63, 62, 61, 60, 59, 58, 57, 56,
            32, 16, 48, 24, 40, 12, 28, 36, 52,
            9, 10, 11, 13, 14, 15, 17, 18, 19, 20,
            21, 22, 23, 25, 26, 27, 29, 30, 31,
            33, 34, 35, 37, 38, 39, 41, 42, 43, 44,
            45, 46, 47, 49, 50, 51, 53, 54, 55,
        ]
        self.assertEqual(sorted(delete_order), keys)
        for key in delete_order:
            delete_key_and_check(self, tree, expected, key, True)


class TestSearchTimesAcrossMutations(unittest.TestCase):
    def test_search_times_after_rotations_and_deletions(self):
        tree = AVLTree(True)
        expected = {}
        keys = [50, 20, 70, 10, 30, 60, 80, 25, 35, 65, 75, 5, 15, 27, 33]
        for key in keys:
            insert_and_check(self, tree, expected, key, str(key), True)

        for key in [-100, 5, 15, 27, 33, 50, 81, 1000]:
            assert_search_exact(self, tree, key)

        for key in [20, 70, 50, 10, 80]:
            delete_key_and_check(self, tree, expected, key, True)
            for probe in [-100, 5, 15, 27, 33, 50, 81, 1000]:
                assert_search_exact(self, tree, probe)


if __name__ == "__main__":
    unittest.main(verbosity=2)

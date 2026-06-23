# id1:
# name1:
# username1:
# id2:
# name2:
# username2:


"""A class representing a node in an AVL tree"""


class AVLNode(object):
    """Constructor, you are allowed to add more fields.

    @type key: int
    @param key: key of your node
    @type value: string
    @param value: data of your node
    """

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.height = -1

    """returns whether self is not a virtual node 

    @rtype: bool
    @returns: False if self is a virtual node, True otherwise.
    """

    def is_real_node(self):
        return self.key is not None


"""
A class implementing an AVL tree.
"""


class AVLTree(object):
    """
    Constructor, you are allowed to add more fields.

    @type is_avl: boolean
    @param is_avl: If True then tree is AVL, otherwise it is just a "regular" binary search tree, without rotations.
    """

    def __init__(self, is_avl):
        self.is_avl = is_avl
        self.root = None
        self._size = 0
        self.virtual = AVLNode(None, None)

    def _new_node(self, key, val):
        node = AVLNode(key, val)
        node.left = self.virtual
        node.right = self.virtual
        node.height = 0
        return node

    def _height(self, node):
        if node is None or not node.is_real_node():
            return -1
        return node.height

    def _update_height(self, node):
        if node is not None and node.is_real_node():
            node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right)

    def _replace_parent_child(self, old_node, new_node):
        parent = old_node.parent
        if parent is None:
            self.root = new_node if new_node.is_real_node() else None
            if self.root is not None:
                self.root.parent = None
            return

        if parent.left is old_node:
            parent.left = new_node
        else:
            parent.right = new_node

        if new_node.is_real_node():
            new_node.parent = parent

    def _rotate_left(self, x):
        y = x.right
        beta = y.left
        parent = x.parent

        y.parent = parent
        if parent is None:
            self.root = y
        elif parent.left is x:
            parent.left = y
        else:
            parent.right = y

        y.left = x
        x.parent = y

        x.right = beta
        if beta.is_real_node():
            beta.parent = x

        self._update_height(x)
        self._update_height(y)
        return y

    def _rotate_right(self, x):
        y = x.left
        beta = y.right
        parent = x.parent

        y.parent = parent
        if parent is None:
            self.root = y
        elif parent.left is x:
            parent.left = y
        else:
            parent.right = y

        y.right = x
        x.parent = y

        x.left = beta
        if beta.is_real_node():
            beta.parent = x

        self._update_height(x)
        self._update_height(y)
        return y

    def _rebalance_after_insert(self, node):
        rotations = 0
        height_changes = 0
        y = node.parent

        while y is not None:
            bf = self._balance_factor(y)

            if abs(bf) < 2:
                old_height = y.height
                new_height = 1 + max(self._height(y.left), self._height(y.right))

                if new_height == old_height:
                    break

                y.height = new_height
                height_changes += 1
                y = y.parent
                continue

            if bf == 2:
                if self._balance_factor(y.left) < 0:
                    self._rotate_left(y.left)
                    rotations += 1
                self._rotate_right(y)
                rotations += 1
            else:
                if self._balance_factor(y.right) > 0:
                    self._rotate_right(y.right)
                    rotations += 1
                self._rotate_left(y)
                rotations += 1

            break

        return rotations, height_changes

    def _rebalance_after_delete(self, node):
        y = node

        while y is not None:
            old_height = y.height
            bf = self._balance_factor(y)

            if abs(bf) < 2:
                self._update_height(y)
                if y.height == old_height:
                    break
                y = y.parent
                continue

            if bf == 2:
                if self._balance_factor(y.left) < 0:
                    self._rotate_left(y.left)
                new_root = self._rotate_right(y)
            else:
                if self._balance_factor(y.right) > 0:
                    self._rotate_right(y.right)
                new_root = self._rotate_left(y)

            y = new_root.parent

    def _subtree_min(self, node):
        current = node
        while current.left.is_real_node():
            current = current.left
        return current

    """searches for a node in the dictionary corresponding to the key (starting at the root)

    @type key: int
    @param key: a key to be searched
    @rtype: (AVLNode,int)
    @returns: a tuple (x, search_time) where x is the node corresponding to key (or None if not found)
    and search_time is the search time, as defined and explained in the assignment.
    """

    def search(self, key):
        if self.root is None:
            return None, 1

        current = self.root
        search_time = 0

        while current.is_real_node():
            search_time += 1

            if key == current.key:
                return current, search_time

            if key < current.key:
                current = current.left
            else:
                current = current.right

        return None, search_time + 1

    """inserts a new node into the dictionary with corresponding key and value (starting at the root)

    @type key: int
    @pre: key currently does not appear in the dictionary
    @param key: key of item that is to be inserted to self
    @type val: string
    @param val: the value of the item
    @rtype: (AVLNode,int,int,int)
    @returns: a 4-tuple (x, search_time, rotations, height_changes), where x is the new node
    and the other 3 return values are as defined and explained in the assignment.
    """

    def insert(self, key, val):
        new_node = self._new_node(key, val)

        if self.root is None:
            self.root = new_node
            self._size = 1
            return new_node, 1, 0, 0

        current = self.root
        parent = None
        search_time = 0

        while current.is_real_node():
            parent = current
            search_time += 1

            if key < current.key:
                current = current.left
            else:
                current = current.right

        new_node.parent = parent
        if key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1
        search_time += 1

        rotations = 0
        height_changes = 0
        if self.is_avl:
            rotations, height_changes = self._rebalance_after_insert(new_node)

        return new_node, search_time, rotations, height_changes

    """deletes node from the dictionary

    @type node: AVLNode
    @pre: node is a real pointer to a node in self
    """

    def delete(self, node):
        if node is None or not node.is_real_node():
            return

        rebalance_start = node.parent

        if not node.left.is_real_node():
            child = node.right
            self._replace_parent_child(node, child)

        elif not node.right.is_real_node():
            child = node.left
            self._replace_parent_child(node, child)

        else:
            successor = self._subtree_min(node.right)

            if successor.parent is node:
                rebalance_start = successor
            else:
                rebalance_start = successor.parent

                successor_child = successor.right

                if successor.parent.left is successor:
                    successor.parent.left = successor_child
                else:
                    successor.parent.right = successor_child

                if successor_child.is_real_node():
                    successor_child.parent = successor.parent

                successor.right = node.right
                successor.right.parent = successor

            self._replace_parent_child(node, successor)
            successor.left = node.left
            successor.left.parent = successor
            successor.height = node.height

        self._size -= 1

        node.left = None
        node.right = None
        node.parent = None

        if self.is_avl:
            self._rebalance_after_delete(rebalance_start)

    """returns a list representing dictionary 

    @rtype: list
    @returns: a list of (key, value) tuples sorted by key, representing the data structure
    """

    def avl_to_list(self):
        result = []
        stack = []
        current = self.root

        while stack or (current is not None and current.is_real_node()):
            while current is not None and current.is_real_node():
                stack.append(current)
                current = current.left

            current = stack.pop()
            result.append((current.key, current.value))
            current = current.right

        return result

    """returns the number of items in dictionary 

    @rtype: int
    @returns: the number of items in dictionary 
    """

    def size(self):
        return self._size

    """returns the root of the tree representing the dictionary

    @rtype: AVLNode
    @returns: the root, None if the dictionary is empty
    """

    def get_root(self):
        return self.root

    """returns the height of the tree

        @rtype: int
        @returns: the height of the tree 
        """

    def get_height(self):
        if self.root is None:
            return -1

        if self.is_avl:
            return self.root.height

        max_height = -1
        stack = [(self.root, 0)]

        while stack:
            node, height = stack.pop()

            if node is None or not node.is_real_node():
                continue

            if height > max_height:
                max_height = height

            stack.append((node.left, height + 1))
            stack.append((node.right, height + 1))

        return max_height

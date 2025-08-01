class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1 # Initial height is 1 for a new node

    def to_dict(self):
        """
        Serializes the node and its children into a dictionary format suitable for JSON.
        """
        return {
            "value": self.value,
            "height": self.height,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

class AVLTree:
    def __init__(self):
        self.root = None

    def get_height(self, node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def rotate_right(self, y):
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x

    def rotate_left(self, x):
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def insert(self, node, value):
        # Standard BST insertion
        if not node:
            return Node(value)

        if value < node.value:
            node.left = self.insert(node.left, value)
        elif value > node.value:
            node.right = self.insert(node.right, value)
        else:
            return node # Duplicate values are not allowed in this implementation

        # Update height of the current node
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

        # Get the balance factor
        balance = self.get_balance(node)

        # Perform rotations if needed to balance the tree
        # Left Left Case
        if balance > 1 and value < node.left.value:
            return self.rotate_right(node)

        # Right Right Case
        if balance < -1 and value > node.right.value:
            return self.rotate_left(node)

        # Left Right Case
        if balance > 1 and value > node.left.value:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)

        # Right Left Case
        if balance < -1 and value < node.right.value:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def build_from_list(self, numbers):
        """
        Builds an AVL tree from a list of numbers.
        """
        self.root = None # Reset root for new tree construction
        for num in numbers:
            self.root = self.insert(self.root, num)
        return self.root

    def to_dict(self):
        """
        Serializes the entire AVL tree into a dictionary format suitable for JSON.
        """
        return self.root.to_dict() if self.root else None

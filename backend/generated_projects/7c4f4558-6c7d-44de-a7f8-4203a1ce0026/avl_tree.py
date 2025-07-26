# AVL Tree Implementation

class Node:
    """Represents a node in the AVL tree."""
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.height = 1  # Height of the node; initially 1


class AVLTree:
    """Implements the AVL tree data structure."""

    def __init__(self):
        self.root = None

    def insert(self, data):
        """Inserts a new node into the AVL tree."""
        self.root = self._insert(self.root, data)

    def _insert(self, node, data):
        """Recursive helper function for insertion."""
        if not node:
            return Node(data)
        elif data < node.data:
            node.left = self._insert(node.left, data)
        else:
            node.right = self._insert(node.right, data)

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)

        # Left Heavy
        if balance > 1:
            if data < node.left.data:
                return self.right_rotate(node)
            else:
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)

        # Right Heavy
        if balance < -1:
            if data > node.right.data:
                return self.left_rotate(node)
            else:
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)

        return node

    def delete(self, data):
        """Deletes a node from the AVL tree."""
        self.root = self._delete(self.root, data)

    def _delete(self, node, data):
        """Recursive helper function for deletion."""
        if not node:
            return node

        if data < node.data:
            node.left = self._delete(node.left, data)
        elif data > node.data:
            node.right = self._delete(node.right, data)
        else:
            if not node.left:
                temp = node.right
                # node = None  # No need to set node to None; it's going out of scope anyway.
                return temp
            elif not node.right:
                temp = node.left
                # node = None
                return temp

            temp = self._min_value_node(node.right)
            node.data = temp.data
            node.right = self._delete(node.right, temp.data)

        # If the tree had only one node then return
        if node is None:
            return node

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)

        # Left Heavy
        if balance > 1:
            if self.get_balance(node.left) >= 0:
                return self.right_rotate(node)
            else:
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)

        # Right Heavy
        if balance < -1:
            if self.get_balance(node.right) <= 0:
                return self.left_rotate(node)
            else:
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)

        return node

    def _min_value_node(self, node):
        """Helper function to find the node with the minimum value in a subtree."""
        current = node
        while current.left:
            current = current.left
        return current

    def find(self, data):
        """Searches AVL tree for the Node with value 'data'."""
        return self._find(self.root, data)

    def _find(self, node, data):
        """Recursive helper for find."""
        if not node:
            return None
        if data == node.data:
            return node
        elif data < node.data:
            return self._find(node.left, data)
        else:
            return self._find(node.right, data)

    def get_height(self, node):
        """Returns height of Node."""
        if not node:
            return 0
        return node.height

    def update_height(self, node):
        """Updates the height after insertion or deletion."""
        if not node:
            return 0
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

    def get_balance(self, node):
        """Returns the balance factor of a node."""
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def left_rotate(self, node):
        """Performs a left rotation on a node."""
        y = node.right
        T2 = y.left

        y.left = node
        node.right = T2

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    def right_rotate(self, node):
        """Performs a right rotation on a node."""
        x = node.left
        T2 = x.right

        x.right = node
        node.left = T2

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))

        return x

    def inorder_traversal(self, node):
        """Performs an inorder traversal of the tree and returns data in a list."""
        result = []
        if node:
            result.extend(self.inorder_traversal(node.left))
            result.append(node.data)
            result.extend(self.inorder_traversal(node.right))
        return result


if __name__ == '__main__':
    # Example usage (can be removed when integrated with Streamlit)
    tree = AVLTree()
    tree.insert(10)
    tree.insert(20)
    tree.insert(30)
    tree.insert(40)
    tree.insert(50)
    tree.insert(25)

    print("Inorder traversal:", tree.inorder_traversal(tree.root))

    tree.delete(30)

    print("Inorder traversal after deleting 30:", tree.inorder_traversal(tree.root))

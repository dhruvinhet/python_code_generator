from typing import Optional


class AVLNode:
    """
    Represents a node in the AVL Tree.
    Each node stores a key, references to left and right children, and its height.
    """
    def __init__(self, key: int):
        self.key = key
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height: int = 1  # New nodes are initially at height 1


class AVLTree:
    """
    Implements the AVL (Adelson-Velsky and Landis) self-balancing binary search tree.
    Ensures that for any node, the heights of its left and right subtrees differ by at most 1.
    """
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def _get_height(self, node: Optional[AVLNode]) -> int:
        """
        Helper method to get the height of a node.
        Returns 0 if the node is None, otherwise returns the node's height.
        """
        if not node:
            return 0
        return node.height

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        """
        Helper method to get the balance factor of a node.
        Balance factor = height(left_subtree) - height(right_subtree).
        """
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """
        Performs a right rotation around node y.
        Used to balance the tree when the left subtree is too heavy.
        
              y                            x
             / \                          /  \
            x   T3  (rotate right)       T1   y
           / \      ------------>            / \
          T1  T2                            T2  T3
        """
        x: AVLNode = y.left
        T2: Optional[AVLNode] = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights after rotation
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))

        # Return new root of the subtree
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """
        Performs a left rotation around node x.
        Used to balance the tree when the right subtree is too heavy.

            x                              y
           / \                            / \
          T1  y   (rotate left)          x   T3
             / \  ------------>         / \
            T2  T3                     T1  T2
        """
        y: AVLNode = x.right
        T2: Optional[AVLNode] = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights after rotation
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        # Return new root of the subtree
        return y

    def insert(self, node: Optional[AVLNode], key: int) -> AVLNode:
        """
        Inserts a new key into the AVL tree, starting from the given node.
        This is a recursive function that returns the (potentially new) root of the subtree.
        It also handles balancing the tree after insertion.
        """
        # 1. Perform standard BST insertion
        if not node:
            return AVLNode(key)

        if key < node.key:
            node.left = self.insert(node.left, key)
        elif key > node.key:
            node.right = self.insert(node.right, key)
        else:
            # Key already exists. For AVL, typically we don't insert duplicates.
            # Or handle based on specific requirements (e.g., count frequency, update value).
            # Here, we'll simply return the existing node, effectively ignoring duplicates.
            return node

        # 2. Update height of the current node
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # 3. Get the balance factor of this node to check if it became unbalanced
        balance = self._get_balance(node)

        # 4. Perform rotations if the node is unbalanced

        # Left Left Case (Node is left-heavy and new key is in the left-left subtree)
        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)

        # Right Right Case (Node is right-heavy and new key is in the right-right subtree)
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)

        # Left Right Case (Node is left-heavy and new key is in the left-right subtree)
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left) # Perform left rotation on left child
            return self._rotate_right(node)          # Then right rotation on current node

        # Right Left Case (Node is right-heavy and new key is in the right-left subtree)
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right) # Perform right rotation on right child
            return self._rotate_left(node)           # Then left rotation on current node

        # If the node is balanced, return it unchanged
        return node

    def get_tree_structure(self, node: Optional[AVLNode], level: int = 0, prefix: str = "Root: ") -> str:
        """
        Generates a multi-line string representation of the AVL tree structure for visualization.
        Displays nodes with their key, height, and balance factor using indentation.
        The output is oriented to show the right subtree above the current node
        and the left subtree below, with increasing indentation for deeper levels.
        
        Args:
            node (AVLNode): The current node to start rendering from (typically the tree's root).
            level (int): The current indentation level for recursive calls.

            prefix (str): A prefix to add to the root node (e.g., "Root: " ).
                          This is only applied at level 0.

        Returns:
            str: A string representing the tree structure.
        """
        if node is None:
            # Return "" if it's a recursive call on an empty subtree, otherwise "Tree is empty."
            return "" if level > 0 else "Tree is empty."

        lines = []
        indent_str = "    " * level

        # Recursively get the structure for the right child (appears above current node)
        if node.right:
            # For subtrees, no "Root: " prefix is needed, so pass an empty string
            lines.append(self.get_tree_structure(node.right, level + 1, ""))

        # Add the current node's information
        balance = self._get_balance(node)
        node_info = f"{node.key} (h:{node.height}, b:{balance})"
        
        # Apply prefix only to the root node (level 0)
        current_node_line = f"{indent_str}{prefix}{node_info}" if level == 0 else f"{indent_str}{node_info}"
        lines.append(current_node_line)

        # Recursively get the structure for the left child (appears below current node)
        if node.left:
            # For subtrees, no "Root: " prefix is needed
            lines.append(self.get_tree_structure(node.left, level + 1, ""))
        
        # Join all collected lines to form the final string representation
        return "\n".join(lines)

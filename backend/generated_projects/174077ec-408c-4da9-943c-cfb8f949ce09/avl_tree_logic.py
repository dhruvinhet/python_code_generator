# avl_tree_logic.py
# Contains the core AVL tree data structure and all necessary logic
# for insertion, height calculation, balance factor calculation, and rotations.

class AVLTreeNode:
    """
    Represents a node in the AVL tree.
    Attributes:
        key (int): The value stored in the node.
        left (AVLTreeNode): Reference to the left child node.
        right (AVLTreeNode): Reference to the right child node.
        height (int): The height of the node in the tree.
    """
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1 # New node is initially at height 1

def get_height(node):
    """
    Returns the height of the given node.
    Returns 0 if the node is None.
    """
    if not node:
        return 0
    return node.height

def get_balance(node):
    """
    Calculates the balance factor of the given node.
    Balance factor = height(left_subtree) - height(right_subtree).
    Returns 0 if the node is None.
    """
    if not node:
        return 0
    return get_height(node.left) - get_height(node.right)

def right_rotate(y):
    """
    Performs a right rotation around node y.
    y -> root of the subtree being rotated
    x -> left child of y
    T2 -> right child of x
    """
    x = y.left
    T2 = x.right

    # Perform rotation
    x.right = y
    y.left = T2

    # Update heights
    y.height = 1 + max(get_height(y.left), get_height(y.right))
    x.height = 1 + max(get_height(x.left), get_height(x.right))

    # Return new root
    return x

def left_rotate(x):
    """
    Performs a left rotation around node x.
    x -> root of the subtree being rotated
    y -> right child of x
    T2 -> left child of y
    """
    y = x.right
    T2 = y.left

    # Perform rotation
    y.left = x
    x.right = T2

    # Update heights
    x.height = 1 + max(get_height(x.left), get_height(x.right))
    y.height = 1 + max(get_height(y.left), get_height(y.right))

    # Return new root
    return y

def insert_avl_node(root, key):
    """
    Inserts a new key into the AVL tree and performs rotations if necessary
    to maintain balance.
    Returns the new root of the (sub)tree after insertion.
    """
    # 1. Perform standard BST insertion
    if not root:
        return AVLTreeNode(key)
    elif key < root.key:
        root.left = insert_avl_node(root.left, key)
    elif key > root.key:
        root.right = insert_avl_node(root.right, key)
    else: # Duplicate keys are not allowed in this implementation, return existing node
        return root

    # 2. Update height of the current node
    root.height = 1 + max(get_height(root.left), get_height(root.right))

    # 3. Get the balance factor
    balance = get_balance(root)

    # 4. If the node is unbalanced, then try out the 4 cases

    # Left Left Case
    if balance > 1 and key < root.left.key:
        return right_rotate(root)

    # Right Right Case
    if balance < -1 and key > root.right.key:
        return left_rotate(root)

    # Left Right Case
    if balance > 1 and key > root.left.key:
        root.left = left_rotate(root.left)
        return right_rotate(root)

    # Right Left Case
    if balance < -1 and key < root.right.key:
        root.right = right_rotate(root.right)
        return left_rotate(root)

    return root

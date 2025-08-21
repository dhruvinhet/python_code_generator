# Streamlit AVL Tree Visualizer Documentation

## 1. Project Overview and Purpose

The **Streamlit AVL Tree Visualizer** is an interactive web application designed to demonstrate the fascinating self-balancing properties of an **AVL (Adelson-Velsky and Landis) Tree**. AVL trees are a type of self-balancing binary search tree, where the difference between heights of left and right subtrees (the "balance factor") for any node is at most one. This property ensures that the tree remains relatively balanced, leading to efficient search, insertion, and deletion operations with a time complexity of O(log n).

This application allows users to:
*   Input numerical values.
*   Observe how these values are inserted into the AVL tree.
*   Visualize the tree's structure as it grows.
*   Witness real-time rotations (single and double) as the tree automatically rebalances itself to maintain the AVL property.

The primary purpose of this project is educational, providing a clear and dynamic visual aid for understanding complex data structures and algorithms, particularly useful for students, educators, and anyone interested in the inner workings of self-balancing trees.

## 2. Features and Functionality

*   **Interactive Input:** Easily add new integer nodes to the AVL tree via a simple input field.
*   **Real-time Visualization:** The tree structure is updated and displayed immediately after each insertion, showing node values, heights, and balance factors.
*   **Self-Balancing Demonstration:** Witness the AVL tree perform rotations (Left Rotation, Right Rotation, Left-Right Rotation, Right-Left Rotation) to correct imbalances automatically.
*   **Clear Tree State:** A "Reset Tree" button allows users to clear the current tree and start fresh.
*   **User-Friendly Interface:** Built with Streamlit for a clean and intuitive web-based experience.

## 3. Installation Requirements

To run this application, you need Python installed on your system, along with the `streamlit` library.

1.  **Python:** Ensure you have Python 3.7 or newer installed. You can download it from [python.org](https://www.python.org/downloads/).
2.  **Streamlit:** Install Streamlit using pip, Python's package installer.

    ```bash
    pip install streamlit
    ```

## 4. How to Run the Application

This application is a Streamlit web application. Follow these steps to get it up and running:

1.  **Save the Project Files:** Ensure both `main.py` and `avl_tree_logic.py` are saved in the same directory on your computer.

2.  **Open Terminal/Command Prompt:** Navigate to the directory where you saved the files using your terminal or command prompt.

    ```bash
    cd path/to/your/project/directory
    ```

3.  **Run the Streamlit Application:**
    The **recommended and correct** way to run a Streamlit application is using the `streamlit run` command:

    ```bash
    streamlit run main.py
    ```

    Upon executing this command, your default web browser will automatically open and display the Streamlit AVL Tree Visualizer application. If it doesn't open automatically, a local URL (e.g., `http://localhost:8501`) will be provided in the terminal, which you can copy and paste into your browser.

    > **Note on `python main.py`:** While the `main.py` file is structured with an `if __name__ == "__main__": main()` block, running `python main.py` directly will execute the script but will *not* launch the Streamlit server or display the interactive GUI in your web browser. Streamlit applications require the `streamlit run` command to be properly served as a web application.

## 5. Usage Instructions

Once the application is running in your web browser:

1.  **Insert New Node:**
    *   Locate the "Insert New Node" section.
    *   In the text box labeled "Enter an integer to insert:", type any integer (e.g., `50`, `25`, `75`).
    *   Click the "Insert Node" button.
    *   The application will display a success message and update the "Current AVL Tree Structure" section.

2.  **Observe Tree Changes:**
    *   After each insertion, carefully observe the textual representation of the tree.
    *   Notice how nodes are added and how the `H:` (Height) and `B:` (Balance Factor) values change for various nodes.
    *   When an imbalance occurs (balance factor > 1 or < -1), the tree will perform rotations to rebalance itself. You'll see the tree structure rearrange to maintain balance.

3.  **Reset Tree:**
    *   To clear all nodes from the tree and start a new visualization, click the "Reset Tree" button under the "Tree Actions" section. A success message will confirm the reset, and the tree visualization will indicate it's empty.

## 6. Project Structure Explanation

The project is designed with a modular approach, separating the core AVL tree logic from the user interface.

```
streamlit_avl_tree_visualizer/
├── main.py
└── avl_tree_logic.py
```

*   **`main.py`**: This is the entry point for the Streamlit GUI. It handles all user interactions, input processing, and the rendering of the AVL tree visualization. It acts as the orchestrator, importing and utilizing the AVL tree data structure and algorithms from `avl_tree_logic.py`.
*   **`avl_tree_logic.py`**: This file is purely responsible for the core AVL tree data structure and its associated algorithms. It defines the `AVLTreeNode` class and functions for insertion, height calculation, balance factor calculation, and the crucial rotation operations (left and right rotations). This separation ensures that the AVL tree logic can be reused independently of the Streamlit interface if needed.

This architecture promotes separation of concerns, making the codebase easier to understand, maintain, and extend.

## 7. File Descriptions

### `main.py`

This file sets up the Streamlit application and manages the user interface.

*   **Imports:** `streamlit as st` for the GUI, and `avl_tree_logic` to access the AVL tree implementation.
*   **`_build_tree_string(node, indent, last, result_list)`**: A private helper function used internally by `visualize_tree`. It recursively traverses the tree and constructs a formatted string representation (using Unicode characters for branches) suitable for display, including node key, height, and balance factor.
*   **`visualize_tree(root)`**: Takes the root of the AVL tree as input and displays its textual representation in the Streamlit interface using `st.code`. It provides a message if the tree is empty.
*   **`main()`**: The main function of the Streamlit application.
    *   Configures the Streamlit page layout.
    *   Sets the application title and a brief description.
    *   Initializes `st.session_state.avl_root` to `None` if the tree is empty, and `st.session_state.insert_value_str` for input management, ensuring the tree state persists across Streamlit reruns.
    *   Handles user input for inserting new nodes:
        *   Uses `st.text_input` for numerical input.
        *   Validates input to ensure it's an integer.
        *   Calls `avl_tree_logic.insert_avl_node` to add the new value to the tree.
        *   Provides success/error messages.
        *   Clears the input field after successful insertion.
    *   Calls `visualize_tree` to render the current state of the AVL tree.
    *   Provides a "Reset Tree" button to clear the tree state, resetting `st.session_state.avl_root` to `None`.
*   **`if __name__ == "__main__": main()`**: The standard Python entry point. When `streamlit run main.py` is executed, Streamlit imports and runs this script, calling the `main()` function to build and manage the web application.

### `avl_tree_logic.py`

This file encapsulates the fundamental data structure and algorithms for an AVL tree.

*   **`class AVLTreeNode`**:
    *   Represents a single node in the AVL tree.
    *   **`key` (int):** The integer value stored in the node.
    *   **`left` (AVLTreeNode):** Reference to the left child node.
    *   **`right` (AVLTreeNode):** Reference to the right child node.
    *   **`height` (int):** The height of the node in its subtree (initialized to 1 for a new node).
*   **`get_height(node)`**:
    *   Calculates and returns the height of a given node. Returns `0` if the node is `None`.
*   **`get_balance(node)`**:
    *   Calculates the balance factor of a given node: `height(left_subtree) - height(right_subtree)`. Returns `0` if the node is `None`.
*   **`right_rotate(y)`**:
    *   Performs a right rotation operation around node `y`. This is used to balance a left-heavy subtree. It returns the new root of the rotated subtree.
*   **`left_rotate(x)`**:
    *   Performs a left rotation operation around node `x`. This is used to balance a right-heavy subtree. It returns the new root of the rotated subtree.
*   **`insert_avl_node(root, key)`**:
    *   This is the core insertion function for the AVL tree.
    *   **Step 1: Standard BST Insertion:** Recursively inserts the `key` into the tree as if it were a standard Binary Search Tree. Handles base cases (empty tree) and duplicate keys (returns existing node).
    *   **Step 2: Update Height:** After insertion, updates the height of the current `root` based on its children's heights.
    *   **Step 3: Get Balance Factor:** Calculates the balance factor of the current `root`.
    *   **Step 4: Perform Rotations (if unbalanced):** Checks the balance factor. If it's greater than 1 or less than -1, it means the node is unbalanced. It then applies the appropriate rotation(s) based on the four AVL cases (Left-Left, Right-Right, Left-Right, Right-Left) to restore balance.
    *   Returns the (potentially new) root of the subtree after insertion and balancing.

## 8. Configuration Options

This application currently has no explicit user-configurable options beyond its interactive inputs. All parameters are hardcoded within the `main.py` and `avl_tree_logic.py` files.

## 9. Troubleshooting Tips

*   **"ModuleNotFoundError: No module named 'streamlit'" or "'avl_tree_logic'"**:
    *   **Cause:** The required libraries are not installed, or the files are not in the correct location.
    *   **Solution:** Ensure you have run `pip install streamlit`. Also, make sure `main.py` and `avl_tree_logic.py` are in the same directory.
*   **Application doesn't open in browser:**
    *   **Cause:** Streamlit server might not have started correctly, or a firewall is blocking the port.
    *   **Solution:** Check your terminal for any error messages. Manually open your web browser and navigate to the URL provided in the terminal (usually `http://localhost:8501`). Ensure no other applications are using port 8501.
*   **"Invalid input. Please enter an integer." error:**
    *   **Cause:** You entered non-numeric characters, a decimal number, or left the input field blank when trying to insert.
    *   **Solution:** Only enter whole numbers (integers) in the input field.
*   **Tree visualization looks cluttered or strange:**
    *   **Cause:** This might be due to a very large number of nodes, or terminal font issues.
    *   **Solution:** The current visualization is text-based. For very large trees, it might become less readable. Try resetting the tree and inserting fewer nodes. Ensure your browser's font settings are standard.

## 10. Technical Details for Developers

### AVL Tree Algorithm Insights

The `avl_tree_logic.py` file implements the standard AVL tree insertion algorithm:

1.  **Recursive Insertion (BST-like):** The `insert_avl_node` function first performs a typical binary search tree insertion. It recursively traverses down the tree until it finds the correct position for the new node.
2.  **Height Update:** As the recursion unwinds (i.e., returns from recursive calls), the height of each visited node is updated based on the heights of its children. This is crucial for calculating balance factors.
3.  **Balance Factor Check:** For each node on the path from the inserted node up to the root, its balance factor (`height(left) - height(right)`) is calculated.
4.  **Rotation Logic:** If the absolute balance factor exceeds 1, an imbalance is detected. The code then determines which of the four cases applies and performs the necessary single or double rotation(s):
    *   **Left-Left (LL) Case:** `balance > 1` and `key < root.left.key` -> Perform `right_rotate(root)`.
    *   **Right-Right (RR) Case:** `balance < -1` and `key > root.right.key` -> Perform `left_rotate(root)`.
    *   **Left-Right (LR) Case:** `balance > 1` and `key > root.left.key` -> First `root.left = left_rotate(root.left)`, then `right_rotate(root)`.
    *   **Right-Left (RL) Case:** `balance < -1` and `key < root.right.key` -> First `root.right = right_rotate(root.right)`, then `left_rotate(root)`.

The rotation functions (`left_rotate` and `right_rotate`) correctly re-parent nodes and update heights after the rotation, ensuring the new subtree root maintains correct height information.

### Streamlit Session State

The application utilizes Streamlit's `st.session_state` to maintain the state of the AVL tree (`st.session_state.avl_root`) across reruns. Streamlit applications re-execute from top to bottom every time a widget is interacted with. Without `session_state`, the `avl_root` would reset to `None` on every interaction, making the application non-functional for maintaining a persistent tree.
`st.session_state.insert_value_str` is used to bind the text input field, allowing the application to programmatically clear the input after a successful insertion.

### Tree Visualization (`_build_tree_string`)

The `_build_tree_string` function provides a console-style visualization of the tree. It uses Unicode characters (like `─`, `├`, `└`, `│`) to draw branches, similar to the `tree` command in Linux. It traverses the right child first to make the tree appear more naturally "rooted" from the top in a text display. It also annotates each node with its key, height, and balance factor, which are crucial for understanding the AVL properties.

## 11. Future Enhancement Possibilities

*   **Deletion Functionality:** Implement the deletion of nodes from the AVL tree, which also requires rebalancing.
*   **Search Functionality:** Add a feature to search for a specific key in the tree and highlight its path.
*   **Graphical Visualization:** Instead of a text-based representation, use a library like `Graphviz` or `Plotly` to render a more dynamic and visually appealing graphical tree, possibly showing rotations with animations.
*   **Step-by-Step Mode:** Allow users to step through the insertion process, pausing at each critical step (e.g., node insertion, height update, balance check, rotation) to better understand the algorithm.
*   **Multiple Input Modes:** Allow users to input multiple numbers at once (e.g., comma-separated list) or load from a file.
*   **Performance Metrics:** Display statistics like the number of nodes, height of the tree, or number of rotations performed during insertions.
*   **Export/Import Tree:** Option to save the current tree structure to a file and load a tree from a file.
*   **Error Handling Improvements:** More robust input validation and user feedback.
*   **Interactive Controls for Rotations:** While AVL trees self-balance, an advanced feature could allow users to manually trigger a rotation on a specific node to see its effect, for educational purposes.
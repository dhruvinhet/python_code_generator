# main.py
import streamlit as st
import avl_tree_logic

def _build_tree_string(node, indent="", last=True, result_list=None):
    """
    Recursively builds a string representation of the tree structure.
    Used internally by visualize_tree.
    """
    if result_list is None:
        result_list = []

    if node is not None:
        s = indent
        if last:
            s += "└── "
            new_indent = indent + "    "
        else:
            s += "├── "
            new_indent = indent + "│   "

        balance = avl_tree_logic.get_balance(node)
        s += f"Node: {node.key} (H:{node.height}, B:{balance})\n"
        result_list.append(s)

        # Traverse right child first to display it "above" the left child
        _build_tree_string(node.right, new_indent, False, result_list)
        _build_tree_string(node.left, new_indent, True, result_list)
    return "".join(result_list)


def visualize_tree(root):
    """
    Displays a textual representation of the AVL tree in Streamlit.
    """
    if root is None:
        st.info("The AVL tree is currently empty. Insert some numbers!")
    else:
        st.subheader("Current AVL Tree Structure:")
        tree_string = _build_tree_string(root)
        st.code(tree_string, language="text")

def main():
    st.set_page_config(layout="centered")
    st.title("🌳 Streamlit AVL Tree Visualizer")
    st.markdown(
        """
        This application demonstrates the self-balancing properties of an AVL tree.
        Enter numbers to insert them into the tree, and observe how the tree
        adjusts its structure through rotations to maintain balance.
        """
    )

    # Initialize session state for the AVL tree root if not already present
    if 'avl_root' not in st.session_state:
        st.session_state.avl_root = None
    if 'insert_value_str' not in st.session_state: # Use a string for input field value
        st.session_state.insert_value_str = ""

    # --- User Input Section ---
    st.subheader("Insert New Node")
    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        key_to_insert = st.text_input(
            "Enter an integer to insert:",
            value=st.session_state.insert_value_str, # Bind to session state for clearing
            key="input_key_raw"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True) # Add some vertical space
        if st.button("Insert Node", use_container_width=True):
            if key_to_insert:
                try:
                    node_value = int(key_to_insert)
                    st.session_state.avl_root = avl_tree_logic.insert_avl_node(st.session_state.avl_root, node_value)
                    st.success(f"Successfully inserted {node_value}.")
                    st.session_state.insert_value_str = "" # Clear input field after successful insertion
                except ValueError:
                    st.error("Invalid input. Please enter an integer.")
            else:
                st.warning("Please enter a number to insert.")
    
    # --- Tree Visualization Section ---
    st.markdown("---")
    visualize_tree(st.session_state.avl_root)

    # --- Actions Section ---
    st.markdown("---")
    st.subheader("Tree Actions")
    if st.button("Reset Tree", help="Clear all nodes from the tree"):
        st.session_state.avl_root = None
        st.success("AVL Tree has been reset.")
        st.session_state.insert_value_str = "" # Clear input


if __name__ == "__main__":
    main()

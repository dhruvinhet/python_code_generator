import streamlit as st
import avl_tree

# --- Streamlit Application --- 

def insert_number_callback():
    """
    Callback function for the 'Insert Number' button.
    Retrieves the number from input, validates it, inserts into the AVL tree,
    and updates the tree structure display in session state.
    """
    # Get the number from the session state text input. .strip() to remove whitespace.
    input_value: str = st.session_state.get("num_input", "").strip()
    
    if not input_value:
        st.warning("Please enter a number.")
        return

    try:
        number_to_insert: int = int(input_value)
        
        # Access the AVL tree instance from session state
        avl_tree_instance: avl_tree.AVLTree = st.session_state.avl_tree
        
        # Insert the number. The insert method returns the new root of the subtree.
        # We update the tree's root with the result of the insertion.
        # This handles the case where the root itself changes due to rotations.
        avl_tree_instance.root = avl_tree_instance.insert(avl_tree_instance.root, number_to_insert)
        
        # Update the displayed tree structure string in session state
        st.session_state.tree_structure = avl_tree_instance.get_tree_structure(avl_tree_instance.root)
        
        # Clear the input field after successful insertion for better UX
        st.session_state.num_input = ""
        
        st.success(f"Successfully inserted {number_to_insert} into the AVL tree.")

    except ValueError:
        st.error("Invalid input. Please enter an integer number.")
    except Exception as e:
        # Catch any other unexpected errors during tree operations
        st.error(f"An unexpected error occurred: {e}")


def run_streamlit_app():
    """
    Main function to run the Streamlit AVL Tree Builder application.
    Initializes session state variables for the AVL tree and its display,
    sets up the user interface for input, and displays the tree structure.
    """
    # Set basic Streamlit page configuration
    st.set_page_config(page_title="Streamlit AVL Tree Builder", layout="centered")
    st.title("AVL Tree Visualization")
    st.write("Enter numbers to build and visualize an AVL Tree. Duplicates are ignored.")

    # Initialize AVL Tree and its string representation in Streamlit's session state.
    # Session state ensures that objects and their states persist across Streamlit reruns,
    # which happens on user interaction or code changes.
    if "avl_tree" not in st.session_state:
        st.session_state.avl_tree = avl_tree.AVLTree()
        # Initialize tree structure message
        st.session_state.tree_structure = st.session_state.avl_tree.get_tree_structure(st.session_state.avl_tree.root)

    # --- User Input Section ---
    # Using columns for better layout of input and button
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        # text_input with a key to allow programmatic clearing and access via session_state
        st.text_input("Enter a number to insert:", key="num_input", 
                      value=st.session_state.get("num_input", ""),
                      placeholder="e.g., 50")
    with col2:
        st.write("") # Add a small empty space for vertical alignment with the input field
        st.button("Insert Number", on_click=insert_number_callback, use_container_width=True)

    st.markdown("--- ") # Separator for visual clarity

    # --- Tree Visualization Section ---
    st.subheader("Current AVL Tree Structure:")
    
    # Display the tree structure. st.code is used for preformatted text, preserving newlines and spaces.
    # The tree_structure string is updated by the insert_number_callback.
    st.code(st.session_state.tree_structure, language="python")

    st.markdown("__Note:__ (h:height, b:balance factor)")


if __name__ == "__main__":
    # This block ensures that the Streamlit application is run correctly.
    # When invoked via `streamlit run main.py`, Streamlit executes this file,
    # and the call to `run_streamlit_app()` starts the UI loop.
    run_streamlit_app()

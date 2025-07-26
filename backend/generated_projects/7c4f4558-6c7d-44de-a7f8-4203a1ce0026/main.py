# main.py
import streamlit as st
from avl_tree import AVLTree


def visualize_tree(tree):
    """Visualizes the AVL tree using Streamlit's graphviz."""
    if not tree.root:
        st.write("Tree is empty.")
        return

    dot = "digraph AVLTree {\n"

    def add_nodes_edges(node):
        nonlocal dot
        if node:
            dot += f'  {node.data} [label="{node.data}\nHeight: {node.height}\nBalance: {tree.get_balance(node)}"];\n'
            if node.left:
                dot += f'  {node.data} -> {node.left.data};\n'
                add_nodes_edges(node.left)
            if node.right:
                dot += f'  {node.data} -> {node.right.data};\n'
                add_nodes_edges(node.right)

    add_nodes_edges(tree.root)
    dot += "}\n"

    st.graphviz_chart(dot)


def main():
    """Entry point for the Streamlit application."""
    st.title("AVL Tree Visualization")

    input_data = st.text_input("Enter numbers separated by commas:", "")

    if input_data:
        try:
            numbers = [int(x.strip()) for x in input_data.split(",") if x.strip()]
            tree = AVLTree()
            for num in numbers:
                tree.insert(num)

            st.subheader("AVL Tree")
            visualize_tree(tree)

            # Display inorder traversal
            inorder_list = tree.inorder_traversal(tree.root)
            st.write(f"Inorder Traversal: {inorder_list}")

        except ValueError:
            st.error("Invalid input. Please enter numbers separated by commas.")

        # Delete functionality
        delete_data = st.text_input("Enter number to delete:", "")
        if delete_data:
            try:
                del_num = int(delete_data.strip())
                tree.delete(del_num)

                st.subheader("AVL Tree after Deletion")
                visualize_tree(tree)

                inorder_list = tree.inorder_traversal(tree.root)
                st.write(f"Inorder Traversal after Deletion: {inorder_list}")

            except ValueError:
                st.error("Invalid input for deletion. Please enter a number.")
            except Exception as e:
                st.error(f"Deletion failed. Element may not exist. Error: {e}")


if __name__ == "__main__":
    main()

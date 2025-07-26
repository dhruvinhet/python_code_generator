# main.py
import streamlit as st
import nfa_to_dfa_converter
import dfa_visualization


def main():
    """Entry point for the application. Handles user interface, input parsing, and calls the conversion and visualization functions."""
    st.title("NFA to DFA Converter")
    st.write("Enter the NFA description in English:")

    nfa_description = st.text_area("NFA Description", "Example: States are q0, q1. Alphabet is a, b. Start state is q0. Accepting states are q1. Transitions: q0 on a goes to q0 and q1, q0 on b goes to q0, q1 on a goes to q1, q1 on b goes to q1.")

    if st.button("Convert to DFA"):  # Button to trigger the conversion
        if nfa_description:
            try:
                dfa = nfa_to_dfa_converter.convert_nfa_to_dfa(nfa_description)

                # Display the DFA visualization
                if dfa:
                    graph = dfa_visualization.visualize_dfa(dfa)
                    if graph:
                        st.graphviz_chart(graph)
                    else:
                        st.error("Failed to generate DFA visualization.")
                else:
                    st.error("Failed to convert NFA to DFA. Check the NFA description.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter an NFA description.")


if __name__ == "__main__":
    main()
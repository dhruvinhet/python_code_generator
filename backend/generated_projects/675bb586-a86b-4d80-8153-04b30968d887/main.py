# main.py
import streamlit as st
import nltk
import graphviz
import pydotplus
from nlp_processing import parse_input_text, extract_actions_and_conditions, create_flowchart_data
from flowchart_generator import create_graph, add_nodes, add_edges, render_graph


def main():
    """Main entry point for the Streamlit application."""
    st.title("NLP Flowchart Generator")

    user_input = st.text_area("Enter your natural language description:", "")

    if st.button("Generate Flowchart"):
        if user_input:
            try:
                # Process the NLP input
                sentences = parse_input_text(user_input)
                actions, conditions = extract_actions_and_conditions(sentences)
                flowchart_data = create_flowchart_data(actions, conditions)

                # Generate the flowchart
                graph = create_graph()
                add_nodes(graph, flowchart_data)
                add_edges(graph, flowchart_data)
                dot_graph = render_graph(graph)

                # Display the flowchart
                if dot_graph:
                    st.graphviz_chart(dot_graph)
                else:
                    st.error("Failed to render flowchart.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a description before generating the flowchart.")



# Detect and run with 'streamlit run'
if __name__ == "__main__":
    try:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
    except Exception as e:
        print(f"Error downloading nltk data: {e}")
    main()
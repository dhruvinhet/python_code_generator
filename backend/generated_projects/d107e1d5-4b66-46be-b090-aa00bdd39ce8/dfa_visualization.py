# dfa_visualization.py
import graphviz


def visualize_dfa(dfa):
    """Handles the visual representation of the DFA using Graphviz."""
    dot = graphviz.Digraph(comment='DFA')

    # Add states
    for state in dfa['states']:
        if state in dfa['accepting_states']:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state)

    # Add transitions
    for (from_state, symbol), to_state in dfa['transitions'].items():
        dot.edge(from_state, to_state, label=symbol)

    dot.attr('node', shape='circle')

    try:
        return dot
    except graphviz.backend.ExecutableNotFound as e:
        print(f"Error: Graphviz executable not found: {e}")
        return None
    except Exception as e:
        print(f"Error generating graph: {e}")
        return None
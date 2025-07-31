# flowchart_generator.py
import graphviz
import pydotplus


def create_graph():
    """Creates a directed graph object.

    Returns:
        graphviz.Digraph: The created graph object.
    """
    try:
        graph = graphviz.Digraph(comment='Flowchart')
        return graph
    except Exception as e:
        print(f"Error creating graph: {e}")
        return None


def add_nodes(graph, flowchart_data):
    """Adds nodes to the graph based on the flowchart data.

    Args:
        graph (graphviz.Digraph): The graph object.
        flowchart_data (dict): The flowchart data.
    """
    try:
        graph.node(flowchart_data['start']['label'], label=flowchart_data['start']['label'], shape='circle')
        graph.node(flowchart_data['end']['label'], label=flowchart_data['end']['label'], shape='doublecircle')

        for action in flowchart_data['actions']:
            graph.node(action['label'], label=action['label'], shape='box')

        for condition in flowchart_data['conditions']:
            graph.node(condition['label'], label=condition['label'], shape='diamond')
    except Exception as e:
        print(f"Error adding nodes: {e}")


def add_edges(graph, flowchart_data):
    """Adds edges to the graph based on the flowchart data.

    Args:
        graph (graphviz.Digraph): The graph object.
        flowchart_data (dict): The flowchart data.
    """
    try:
        # Example: Connect Start -> First Action -> First Condition -> End
        #  Improve this logic to create more complex and meaningful connections
        if flowchart_data['actions']:
            graph.edge(flowchart_data['start']['label'], flowchart_data['actions'][0]['label'])
            if flowchart_data['conditions']:
                graph.edge(flowchart_data['actions'][0]['label'], flowchart_data['conditions'][0]['label'])
                graph.edge(flowchart_data['conditions'][0]['label'], flowchart_data['end']['label'])
            else:
                graph.edge(flowchart_data['actions'][0]['label'], flowchart_data['end']['label'])
        else:
            graph.edge(flowchart_data['start']['label'], flowchart_data['end']['label'])
    except Exception as e:
        print(f"Error adding edges: {e}")


def render_graph(graph):
    """Renders the graph to a DOT format.

    Args:
        graph (graphviz.Digraph): The graph object.

    Returns:
        str: The DOT representation of the graph.
    """
    try:
        return graph.pipe(format='dot').decode('utf-8')
    except Exception as e:
        print(f"Error rendering graph: {e}")
        return None
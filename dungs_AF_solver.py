import io
import networkx as nx
import subprocess
import matplotlib.pyplot as plt

def run_mu_toksia(reasoning, semantics, filename, file_format, mu_toksia_path, query=None):
    command = [mu_toksia_path, "./build/release/bin/mu-toksia", "-p", f'{reasoning}-{semantics}', "-f", filename, "-fo", file_format]
    if query is not None:
        command += ["-a", query]
    try:
        output = subprocess.check_output(command, shell=True)
        return output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        error_msg = f"Command '{e.cmd}' returned non-zero exit status {e.returncode}\n"
        error_msg += f"Output: {e.output.decode('utf-8')}"
        raise RuntimeError(error_msg)

def read_tgf_file(uploaded_file):
    # create an empty directed graph
    G = nx.DiGraph()

    # create an in-memory file object from the uploaded file data
    file_content = uploaded_file.getvalue().decode('utf-8')
    file_object = io.StringIO(file_content)

    # read the graph from the file object using the nx.parse_tgf function
    for line in file_object:
        line = line.strip()
        if line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 1:
            G.add_node(parts[0])
        elif len(parts) == 2:
            G.add_edge(parts[0], parts[1])

    return G

def highlight_nodes(graph, nodes, node_color="r"):
    pos = nx.spring_layout(graph)
    node_labels = nx.get_node_attributes(graph, "label")
    nx.draw_networkx_nodes(graph, pos, nodelist=nodes, node_color=node_color)
    nx.draw_networkx_labels(graph, pos, labels=node_labels)
    nx.draw_networkx_edges(graph, pos)
    plt.show()


def parse_tgf_file(file):
    graph = nx.DiGraph()
    nodes = {}
    for line in file:
        line = line.strip()
        if not line:
            continue
        if line == '#':
            break
        node_id, node_label = line.split(' ', 1)
        nodes[node_id] = {'label': node_label}
        graph.add_node(node_id)
    for line in file:
        line = line.strip()
        if not line:
            continue
        from_node_id, to_node_id = line.split(' ')
        graph.add_edge(from_node_id, to_node_id)
    return graph

def get_extensions(graph):
    """
    Compute the complete, stable, preferred, and grounded extensions of the given graph.

    Parameters:
    -----------
    graph : nx.DiGraph
        A directed graph representing an argumentation framework.

    Returns:
    --------
    complete : bool
        True if the graph is complete, False otherwise.
    stable : dict
        A dictionary where the keys are the nodes in the graph and the values are the labeling values
        for the stable extension of the graph.
    preferred : dict
        A dictionary where the keys are the nodes in the graph and the values are the labeling values
        for the preferred extension of the graph.
    grounded : dict
        A dictionary where the keys are the nodes in the graph and the values are the labeling values
        for the grounded extension of the graph.
    """
    if not graph:
        # If graph is empty, return False for all extensions
        return False, {}, {}, {}

    complete = nx.algorithms.is_directed_acyclic_graph(graph)
    if complete:
        stable = _stable_semantic_path(graph)
        preferred = _preferred_semantic_path(graph)
        grounded = _grounded_semantic_path(graph)
    else:
        stable = _stable_semantic_path(graph)
        preferred = _preferred_semantic_path(graph)
        grounded = _grounded_semantic_path(graph)

    return complete, stable, preferred, grounded

def _stable_semantic_path(graph):
    """
    Compute the stable extension of an argumentation framework using the
    stable semantic path algorithm.
    """
    
    labeling = {}
    for node in graph:
        labeling[node] = 0
    for i in range(1, len(graph)):
        for node in graph:
            if labeling[node] == i - 1:
                attacked = [n for n in graph.successors(node) if labeling[n] < i]
                if all([labeling[n] == i - 1 for n in attacked]):
                    labeling[node] = i
    return labeling

def _preferred_semantic_path(graph):
    """
    Compute the preferred extension of an argumentation framework using the
    preferred semantic path algorithm.
    Parameters:
    -----------
    graph : nx.DiGraph
    A directed graph representing an argumentation framework.

    Returns:
    --------
    labeling : dict
       A dictionary where the keys are the nodes in the graph and the values are the labeling values
       for the preferred extension of the graph.
    """
    labeling = {}
    for node in graph:
        labeling[node] = 0
    for i in range(1, len(graph)):
        for node in graph:
            if labeling[node] == i - 1:
                attacked = [n for n in graph.successors(node) if labeling[n] < i]
                if any([labeling[n] == i-1 for n in attacked]):
                    labeling[node] = i
    return labeling

def _grounded_semantic_path(graph):
    """
    Compute the grounded extension of an argumentation framework using the
    grounded semantic path algorithm.
    Parameters:
    -----------
    graph : nx.DiGraph
        A directed graph representing an argumentation framework.

    Returns:
    --------
    labeling : dict
        A dictionary where the keys are the nodes in the graph and the values are the labeling values
        for the grounded extension of the graph.
    """
    labeling = {}
    for node in graph:
        labeling[node] = 0
    changed = True
    while changed:
        changed = False
        for node in graph:
            if labeling[node] == 0:
                attacked = [n for n in graph.successors(node) if labeling[n] == 0]
                if not attacked:
                    labeling[node] = 1
                    changed = True
    return labeling

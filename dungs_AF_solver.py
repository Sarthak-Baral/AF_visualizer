import io
import random
import networkx as nx
import subprocess
import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1
from pyvis.network import Network


def run_solver(reasoning, semantics, filename, file_format, filepath, query=None):
    command = f"sudo docker run --rm -v {filepath}:/data odinaldo/eqargsolver ./eqargsolver-2.87 -p {reasoning}-{semantics} -f /data/{filename} -fo {file_format}"
    if query is not None:
        command += f" -a {query}"

    try:
        output = subprocess.run(command, capture_output=True, text=True, check=True, shell=True).stdout
        return output
    except subprocess.CalledProcessError as e:
        error_msg = f"Command '{e.cmd}' returned non-zero exit status {e.returncode}\n"
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

# If the output is a list of nodes
def parse_nodes(node_str):
    node_list = node_str.strip()[1:-1].split(',')
    return [node.strip() for node in node_list]

# If the output is a list of list of nodes
def parse_sublists(sublists_str):
    sublists_list = sublists_str.strip()[2:-2].split('], [')
    sublists = []
    for sublist_str in sublists_list:
        sublist = parse_nodes(sublist_str)
        sublists.append(sublist)
    return sublists


def get_random_color():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())

def highlight_nodes(graph, output, problem):

    # Check if output is empty
    if not output:
        st.warning("Output is empty")
        return

    # Parse the output if it's a string
    if isinstance(output, str):
        if problem == "SE":
            nodes = parse_nodes(output)
        elif problem == "EE":
            sublists = parse_sublists(output)
    else:
        nodes = output if problem == "SE" else None
        sublists = output if problem == "EE" else None

    # If nodes are present, highlight nodes in the original graph
    if nodes:
        color = get_random_color()
        for node in nodes:
            graph.nodes[node]['color'] = color

    # If sublists are present, create the network graph and allow filtering of sublists
    elif sublists:
        num_sublists = len(sublists)
        if num_sublists > 0 and problem == 'EE':
            # Create a filter button for each sublist
            for i in range(num_sublists):
                st.button(f'Sublist {i+1}')
            # Highlight the nodes in the original graph
            for sublist in sublists:
                color = get_random_color()
                for node in sublist:
                    graph.nodes[node]['color'] = color

    return graph

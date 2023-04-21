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
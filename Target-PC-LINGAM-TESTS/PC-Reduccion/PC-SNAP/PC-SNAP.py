import os
import numpy as np
import networkx as nx
import pydot
import subprocess
from collections import defaultdict
from difflib import SequenceMatcher


# CONFIGURACIÓN
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOT_FILE = os.path.join(BASE_DIR, "PC_output_graph.dot")

TARGET = "SCORE_NEM"

OUTPUT_NAME = "snap_result"


# CLEAN
def clean(x):
    if x is None:
        return ""
    return str(x).replace('"', '').replace("\\n", " ").strip()



# CARGAR DOT
def load_dot_graph(dot_file):

    graphs = pydot.graph_from_dot_file(dot_file)
    graph = graphs[0]

    G = nx.DiGraph()
    id_to_label = {}

    for n in graph.get_nodes():

        node_id = clean(n.get_name())

        if node_id in ["node", "graph", "edge", ""]:
            continue

        label = clean(n.get_label())
        if label == "":
            label = node_id

        id_to_label[node_id] = label
        G.add_node(label)

    for e in graph.get_edges():

        u = clean(e.get_source())
        v = clean(e.get_destination())

        u = id_to_label.get(u, u)
        v = id_to_label.get(v, v)

        if u and v:
            G.add_edge(u, v)

    return G


# TARGET RESOLUTION
def resolve_target(G, target):

    tnorm = target.lower().replace(" ", "")

    best, best_score = None, 0

    for n in G.nodes():
        nn = n.lower().replace(" ", "")

        if nn == tnorm:
            return n

        score = SequenceMatcher(None, nn, tnorm).ratio()
        if score > best_score:
            best_score = score
            best = n

    if best_score >= 0.6:
        return best

    raise ValueError("TARGET NO ENCONTRADO")


# SNAP CORE (basado en paper)
def get_poss_anc(G, targets):

    nodes = list(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)}

    n = len(nodes)
    A = np.zeros((n, n), dtype=int)

    for u, v in G.edges():
        A[idx[u], idx[v]] = 1

    # transitive closure (reachability)
    reach = np.linalg.matrix_power((A + np.eye(n)).astype(bool), n)

    target_idx = [idx[t] for t in targets if t in idx]

    mask = np.any(reach[:, target_idx], axis=1)

    return np.where(mask)[0], nodes


# SNAP WRAPPER
def snap_from_dot(G, target):

    target = resolve_target(G, target)

    poss_idx, nodes = get_poss_anc(G, [target])

    poss_nodes = [nodes[i] for i in poss_idx]

    return G.subgraph(poss_nodes).copy()



# EXPORT 
def export_graph(G, name):

    dot_path = os.path.join(BASE_DIR, f"{name}.dot")

    P = nx.nx_pydot.to_pydot(G)

    P.set_rankdir("LR")
    P.set_splines("true")
    P.set_overlap("false")

    
    # NODOS SIN COLOR
    
    for node in P.get_nodes():

        node_name = clean(node.get_name())

        if node_name in ["", "node", "graph", "edge"]:
            continue

        node.set_shape("ellipse")
        node.set_style("solid")
        node.set_fontsize("18")

        # eliminar cualquier color si existe
        if hasattr(node, "obj_dict"):
            attrs = node.obj_dict.get("attributes", {})
            attrs.pop("fillcolor", None)
            attrs.pop("color", None)

    
    # EDGES
    
    for edge in P.get_edges():
        edge.set_penwidth("1.2")

    # SAVE DOT
    P.write_raw(dot_path)

    png_path = os.path.join(BASE_DIR, f"{name}_hd.png")
    pdf_path = os.path.join(BASE_DIR, f"{name}_hd.pdf")

    subprocess.run([
        "dot", "-Tpng",
        "-Gdpi=600",
        "-Nfontsize=20",
        "-Efontsize=16",
        dot_path,
        "-o",
        png_path
    ], check=True)

    subprocess.run([
        "dot", "-Tpdf",
        "-Gdpi=600",
        "-Nfontsize=20",
        "-Efontsize=16",
        dot_path,
        "-o",
        pdf_path
    ], check=True)

    print("\n✔ DOT:", dot_path)
    print("✔ PNG:", png_path)
    print("✔ PDF:", pdf_path)


# MAIN
if __name__ == "__main__":

    print("\n=================================================")
    print(" SNAP PAPER VERSION (DOT INPUT)")
    print("=================================================")

    print("\nCargando DOT...")
    G = load_dot_graph(DOT_FILE)

    print("Nodos:", G.number_of_nodes())
    print("Aristas:", G.number_of_edges())

    print("\nEjecutando SNAP...")

    G_snap = snap_from_dot(G, TARGET)

    print("SNAP nodos:", G_snap.number_of_nodes())
    print("SNAP aristas:", G_snap.number_of_edges())

    export_graph(G_snap, OUTPUT_NAME)

    print("\nCOMPLETADO---")

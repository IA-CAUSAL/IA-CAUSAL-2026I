import networkx as nx
import pydot
import subprocess
from networkx.drawing.nx_pydot import write_dot

DOT_FILE = "PC_output_graph.dot"
TARGET = "SCORE_NEM"

# CARGAR DOT
graphs = pydot.graph_from_dot_file(DOT_FILE)
pydot_graph = graphs[0]

G = nx.DiGraph()
node_map = {}

# NODOS
for node in pydot_graph.get_nodes():
    name = node.get_name().strip('"').strip()
    label = node.get_label()

    if name in ("node", "graph", "edge", ""):
        continue

    real_name = label.strip('"').strip() if label else name

    G.add_node(real_name)
    node_map[name] = real_name

# ARISTAS
for edge in pydot_graph.get_edges():
    u = edge.get_source().strip('"').strip()
    v = edge.get_destination().strip('"').strip()

    u = node_map.get(u, u)
    v = node_map.get(v, v)

    G.add_edge(u, v)

print("Nodos:", G.number_of_nodes())
print("Aristas:", G.number_of_edges())

# HACER DAG (Tener cuidado aqui PASO CLAVE)
G_dag = G.copy()

while not nx.is_directed_acyclic_graph(G_dag):
    cycle = list(nx.simple_cycles(G_dag))[0]
    u, v = cycle[-1], cycle[0]

    print(f"Eliminando ciclo: {u} -> {v}")
    G_dag.remove_edge(u, v)

print("DAG válido obtenido")

# TARGET
target_node = None

if TARGET in G_dag.nodes():
    target_node = TARGET
else:
    for n in G_dag.nodes():
        if TARGET.lower() in str(n).lower():
            target_node = n
            break

print("Target:", target_node)

# PEARL: ANCESTROS
anc = nx.ancestors(G_dag, target_node)
subG = G_dag.subgraph(anc.union({target_node})).copy()

# PEARL REDUCTION (CORRECTA)
subG_red = nx.transitive_reduction(subG)
print("Subgrafo nodos:", subG.number_of_nodes())
print("Aristas reducidas:", subG_red.number_of_edges())

# EXPORT
write_dot(subG, "PC_pearl_subgrafo.dot")
write_dot(subG_red, "PC_pearl_reducido.dot")

# PNG
subprocess.run([
    "dot",
    "-Tpng",
    "-Gdpi=600",
    "-Grankdir=LR",
    "PC_pearl_reducido.dot",
    "-o",
    "PC_pearl_reducido.png"
])

# PDF
subprocess.run([
    "dot",
    "-Tpdf",
    "-Gdpi=600",
    "-Grankdir=LR",
    "PC_pearl_reducido.dot",
    "-o",
    "PC_pearl_reducido.pdf"
])

print("\n EJECUCIÓN PEARL COMPLETADO CORRECTAMENTE")

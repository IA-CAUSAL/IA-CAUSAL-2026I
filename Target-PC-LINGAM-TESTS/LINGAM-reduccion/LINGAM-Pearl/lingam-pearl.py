import networkx as nx
import pandas as pd
import pydot
import subprocess
from networkx.drawing.nx_pydot import write_dot


# 1. Cargar archivo DOT original
archivo_dot = "lingam.dot"
graphs = pydot.graph_from_dot_file(archivo_dot)
pydot_graph = graphs[0]
G = nx.DiGraph()

# Nodos
for node in pydot_graph.get_nodes():
    nombre = node.get_name().strip('"').strip()
    if nombre not in ("node", "graph", "edge"):
        G.add_node(nombre)

# Aristas
for edge in pydot_graph.get_edges():
    origen = edge.get_source().strip('"').strip()
    destino = edge.get_destination().strip('"').strip()
    G.add_edge(origen, destino)

print("Nodos:", G.number_of_nodes())
print("Aristas:", G.number_of_edges())


# 2. Buscar nodo objetivo
nodo_objetivo = None

for n in G.nodes():
    if "score_nem" in n.lower():
        nodo_objetivo = n
        break

if nodo_objetivo is None:
    print("\nNo se encontró score_nem. Lista de nodos:\n")
    for n in G.nodes():
        print(n)
    raise ValueError("Revisar nombre del nodo")

print("Nodo objetivo:", nodo_objetivo)


# 3. Subgrafo de ANCESTROS
ancestros = nx.ancestors(G, nodo_objetivo)
nodos_subgrafo = ancestros.union({nodo_objetivo})
subG = G.subgraph(nodos_subgrafo).copy()
print("Nodos en subgrafo (ancestros):", subG.number_of_nodes())
write_dot(subG, "ancestros_score_nem.dot")
subprocess.run([
    "dot", "-Tpng", "-Gdpi=600", "-Grankdir=LR",
    "ancestros_score_nem.dot",
    "-o", "ancestros_score_nem.png"
])


# 4. Reducción transitiva
if nx.is_directed_acyclic_graph(subG):
    subG_red = nx.transitive_reduction(subG)
    print("Aplicando reducción transitiva...")
else:
    subG_red = subG.copy()
    print("El grafo no es DAG, no se aplica reducción")

print("Aristas después de reducción:", subG_red.number_of_edges())
write_dot(subG_red, "ancestros_score_nem_reducido.dot")
subprocess.run([
    "dot", "-Tpng", "-Gdpi=600", "-Grankdir=LR",
    "ancestros_score_nem_reducido.dot",
    "-o", "ancestros_score_nem_reducido.png"
])

# 5. Matriz de adyacencia
matriz = nx.to_pandas_adjacency(subG_red)
matriz.to_csv("score_nem_matriz.csv", sep=";")
print("Archivo OK")

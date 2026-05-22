import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from causallearn.search.FCMBased import lingam
from causallearn.search.FCMBased.lingam.utils import make_dot

from graphviz import Digraph

TARGET = "SCORE_NEM"
print("Cargando dataset")
data = pd.read_csv('dataset_270411_final_ingles.csv', sep=';')
data.columns = data.columns.str.strip().str.replace('"', '', regex=False)
if TARGET not in data.columns:
    raise Exception(f"TARGET '{TARGET}' no existe")
print("Procesando...")

data = data.apply(pd.to_numeric, errors='coerce')
data = data.dropna()

labels = list(data.columns)
data_array = data.to_numpy(dtype=np.float32)

# Configurar LINGAM
print("Ejecutando DirectLiNGAM...")
model = lingam.DirectLiNGAM()
model.fit(data_array)
print("LiNGAM finalizado.")
# Aqui se genera el grafo
dot = make_dot(model.adjacency_matrix_, labels=labels)

# IMPORTANTE
# FORZAR TARGET COMO NODO FINAL
# Graphviz: rank sink = abajo del todo

dot.attr(rankdir="TB")
dot.attr(splines="true")
dot.attr(overlap="false")

# crear subgraph para forzar orden
dot.body.append('{ rank = sink; "' + TARGET + '"; }')

# DOT
dot.attr(dpi="600")   # alta resolución real

# EXPORTAR ARCHIVOS dot, png y pdf
dot_file = "lingam.dot"
png_file = "lingam.png"
pdf_file = "lingam.pdf"

dot.save(dot_file)

# PNG
dot.format = "png"
dot.render("lingam", cleanup=False)

# PDF ALTA RESOLUCIÓN
dot.format = "pdf"
dot.render("lingam", cleanup=False)

# Mostrar foto
img = plt.imread(png_file)
plt.figure(figsize=(12, 12))
plt.imshow(img)
plt.axis("off")
plt.tight_layout()
plt.show()

print("\nArchivos generados:")
print("DOT:", dot_file)
print("PNG:", png_file)
print("PDF:", pdf_file)

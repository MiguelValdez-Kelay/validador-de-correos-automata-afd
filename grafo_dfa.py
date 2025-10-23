# grafo_dfa.py
from graphviz import Digraph
import os
from shutil import copyfile

def generar_animacion(path, carpeta="animacion_dfa"):
    """
    Genera una imagen por paso en 'carpeta' resaltando el estado actual.
    Copia el último paso como 'grafo_dfa.png' para mostrar en la interfaz.
    """
    os.makedirs(carpeta, exist_ok=True)
    archivos = []

    accept = "q34"
    error  = "qError"

    # Conjunto de estados que aparecerán (solo los del recorrido para que sea legible)
    estados_unicos = list(dict.fromkeys(path))

    for paso, estado_actual in enumerate(path, start=1):
        dot = Digraph(comment=f"Paso {paso}", format="png")
        dot.attr(rankdir='LR')

        # Nodos
        for st in estados_unicos:
            if st == error:
                dot.node(st, st, shape="circle", color="red", style="filled", fillcolor="#f8d7da")
            elif st == accept:
                dot.node(st, st, shape="doublecircle", color="green", style="filled", fillcolor="#d4edda")
            elif st == estado_actual:
                dot.node(st, st, shape="circle", color="blue", style="filled", fillcolor="#cfe2ff")
            else:
                dot.node(st, st, shape="circle")

        # Aristas del recorrido
        for i in range(len(path) - 1):
            a, b = path[i], path[i+1]
            dot.edge(a, b)

        fname = os.path.join(carpeta, f"paso_{paso}")
        dot.render(fname, cleanup=True)
        archivos.append(fname + ".png")

    # Imagen final para la interfaz
    if archivos:
        copyfile(archivos[-1], "grafo_dfa.png")

    return archivos

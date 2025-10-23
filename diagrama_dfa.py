from graphviz import Digraph

dot = Digraph('DFA_Correo', filename='dfa_correo.gv', format='png')
dot.attr(rankdir='LR')  # izquierda a derecha

# ---------------------
# Crear estados (38 en total)
# ---------------------
# q0 a q37
for i in range(38):
    if 2 <= i <= 24:  # los estados qT_2 a qT_24 son de aceptación
        dot.node(f"qT_{i}", f"qT_{i}", shape="doublecircle", color="green")
    else:
        dot.node(f"q{i}", f"q{i}", shape="circle")

# Estado de error (pozo)
dot.node("qERROR", "qERROR", shape="circle", color="red")

# ---------------------
# Transiciones principales (simplificadas)
# ---------------------
dot.edge("q0", "q1", label="letra/dígito")
dot.edge("q1", "q1", label="letra/dígito")
dot.edge("q1", "q2", label=".")
dot.edge("q1", "q3", label="_ / + / -")
dot.edge("q1", "q4", label="@")
dot.edge("q2", "q1", label="letra/dígito")
dot.edge("q3", "q1", label="letra/dígito / .")
dot.edge("q4", "q5", label="letra/dígito (inicio dominio)")
dot.edge("q5", "q5", label="letra/dígito")
dot.edge("q5", "q6", label="-")
dot.edge("q5", "q7", label=".")
dot.edge("q6", "q5", label="letra/dígito")
dot.edge("q7", "q5", label="letra/dígito (nueva etiqueta)")

# Bloque TLD (qT_1 ... qT_24)
for i in range(1, 24):
    src = f"qT_{i}" if i > 1 else "q7"
    dst = f"qT_{i+1}"
    dot.edge(src, dst, label="letra")
# Transición a estado de error si TLD inválido
dot.edge("q7", "qERROR", label="no letra")
dot.edge("qERROR", "qERROR", label="cualquier otro")

# ---------------------
# Estado inicial
# ---------------------
dot.attr('node', shape='plaintext')
dot.node('inicio', 'Inicio')
dot.edge('inicio', 'q0')

# ---------------------
# Exportar imagen
# ---------------------
dot.render('DFA_correo', format='png', cleanup=True)
print(" Diagrama generado: DFA_correo.png")

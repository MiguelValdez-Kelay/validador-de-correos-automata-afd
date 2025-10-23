# interfaz_dfa.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # si no lo tienes: pip install pillow
from validador_dfa import simulate
from grafo_dfa import generar_animacion
import time
import os

VENT_W, VENT_H = 760, 580
IMG_W, IMG_H = 700, 360

def validar():
    correo = entry.get().strip()
    if not correo:
        messagebox.showwarning("Atención", "Ingresa un correo primero.")
        return

    path, accepted = simulate(correo)

    # Limpiar frame
    for w in frame_img.winfo_children():
        w.destroy()

    # Generar animación por pasos (archivos PNG)
    archivos = generar_animacion(path)

    # Mostrar último estado directamente
    if os.path.exists("grafo_dfa.png"):
        mostrar_imagen("grafo_dfa.png")

    lbl_result.config(
        text="✅ Correo válido" if accepted else "❌ Correo inválido",
        fg="green" if accepted else "red"
    )

def mostrar_imagen(ruta):
    img = Image.open(ruta).resize((IMG_W, IMG_H))
    tk_img = ImageTk.PhotoImage(img)
    lbl = tk.Label(frame_img, image=tk_img, bg="#f7f7f7")
    lbl.image = tk_img
    lbl.pack()

# UI
root = tk.Tk()
root.title("Simulador DFA (35 estados) — Validador de Correos")
root.geometry(f"{VENT_W}x{VENT_H}")
root.configure(bg="#f7f7f7")

tk.Label(root, text="Ingrese un correo electrónico:", font=("Arial", 12), bg="#f7f7f7").pack(pady=(15,5))
entry = tk.Entry(root, width=60, font=("Arial", 12))
entry.pack()

btn = tk.Button(root, text="Validar", font=("Arial", 12, "bold"), command=validar)
btn.pack(pady=10)

lbl_result = tk.Label(root, text="", font=("Arial", 14, "bold"), bg="#f7f7f7")
lbl_result.pack(pady=5)

frame_img = tk.Frame(root, bg="#f7f7f7")
frame_img.pack(pady=10)

# Sugerencia visual inicial
tk.Label(root, text="Estados: q0..q34 (35 en total). Aceptación en q34. Error en qError.",
         font=("Arial", 10), bg="#f7f7f7", fg="#555").pack(pady=(0,10))

root.mainloop()

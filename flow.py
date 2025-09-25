import streamlit as st
import numpy as np
import time
import random
from itertools import cycle

st.set_page_config(page_title="Magia para Nahomy 💖", page_icon="💖", layout="wide")

# --- CONFIGURACIÓN ---
nombre = "Nahomy"
palabras = ["Increíble", "Valiente", "Amable", "Inspiradora", "Única", "Radiante", "Especial", "Brillante"]

canvas_width = 800
canvas_height = 600

# Ciclo de colores para el corazón
colores = cycle(["#ff4d6d", "#ff66a3", "#ff99c8", "#ff4d6d"])

# Inicializar posiciones de estrellas y flores
num_estrellas = 50
num_flores = 30
estrellas = np.column_stack((np.random.randint(0, canvas_width, num_estrellas),
                             np.random.randint(0, canvas_height, num_estrellas)))
flores = np.column_stack((np.random.randint(0, canvas_width, num_flores),
                          np.random.randint(0, canvas_height, num_flores)))

# Velocidad de caída
vel_estrellas = np.random.randint(2, 6, num_estrellas)
vel_flores = np.random.randint(1, 4, num_flores)

# Placeholder para animación
placeholder = st.empty()

# --- FUNCIONES ---
def draw_heart(scale=1.0):
    """Devuelve lista de puntos del corazón escalado y centrado"""
    x_center = canvas_width // 2
    y_center = canvas_height // 2
    t = np.linspace(0, 2*np.pi, 200)
    x = 16 * np.sin(t)**3
    y = 13*np.cos(t) - 5*np.cos(2*t) - 2*np.cos(3*t) - np.cos(4*t)
    x = x * 15 * scale + x_center
    y = -y * 15 * scale + y_center
    return list(zip(x, y))

def update_positions():
    """Actualiza posiciones de estrellas y flores"""
    global estrellas, flores
    estrellas[:,1] += vel_estrellas
    flores[:,1] += vel_flores
    estrellas[:,1] %= canvas_height
    flores[:,1] %= canvas_height

def render_frame(scale):
    """Devuelve puntos del corazón y posiciones actuales de estrellas y flores"""
    heart_points = draw_heart(scale)
    return heart_points

# --- ANIMACIÓN ---
scale = 1.0
creciendo = True

# Bucle de animación controlado con placeholder
while True:
    # Latido del corazón
    if creciendo:
        scale += 0.02
        if scale >= 1.2:
            creciendo = False
    else:
        scale -= 0.02
        if scale <= 1.0:
            creciendo = True

    # Actualizar posiciones de estrellas y flores
    update_positions()
    heart_points = render_frame(scale)
    color_actual = next(colores)

    # Construir canvas con HTML/CSS
    html_canvas = f"<div style='position:relative; width:{canvas_width}px; height:{canvas_height}px; background-color:#0a0a0a; overflow:hidden;'>"

    # Dibujar estrellas y flores
    for x, y in estrellas:
        html_canvas += f"<div style='position:absolute; left:{x}px; top:{y}px; color:white; font-size:18px;'>⭐</div>"
    for x, y in flores:
        html_canvas += f"<div style='position:absolute; left:{x}px; top:{y}px; color:#ff69b4; font-size:20px;'>🌸</div>"

    # Dibujar corazón con nombre
    for x, y in heart_points[::5]:  # cada 5 puntos para eficiencia
        html_canvas += f"<div style='position:absolute; left:{x}px; top:{y}px; color:{color_actual}; font-size:24px; font-weight:bold;'>{nombre}</div>"

    # Dibujar palabras flotantes
    for _ in range(8):
        px = np.random.randint(canvas_width//4, 3*canvas_width//4)
        py = np.random.randint(canvas_height//4, 3*canvas_height//4)
        word = random.choice(palabras)
        html_canvas += f"<div style='position:absolute; left:{px}px; top:{py}px; color:#ffcc00; font-size:18px; font-weight:bold;'>{word}</div>"

    html_canvas += "</div>"

    # Mostrar en Streamlit
    placeholder.markdown(html_canvas, unsafe_allow_html=True)

    # Esperar un poco para animación fluida
    time.sleep(0.1)







import streamlit as st
import numpy as np
import time
from streamlit_drawable_canvas import st_canvas
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

# Placeholder para canvas
placeholder = st.empty()

# Función para dibujar corazón
def draw_heart(scale=1.0):
    x_center = canvas_width // 2
    y_center = canvas_height // 2
    heart_points = []
    t = np.linspace(0, 2*np.pi, 200)
    x = 16 * np.sin(t)**3
    y = 13*np.cos(t) - 5*np.cos(2*t) - 2*np.cos(3*t) - np.cos(4*t)
    x = x * 15 * scale + x_center
    y = -y * 15 * scale + y_center
    heart_points = list(zip(x, y))
    return heart_points

# Función para actualizar posiciones de estrellas y flores
def update_positions():
    global estrellas, flores
    estrellas[:,1] += vel_estrellas
    flores[:,1] += vel_flores
    estrellas[:,1] %= canvas_height
    flores[:,1] %= canvas_height

# Función para dibujar todo en el canvas
def render_frame():
    heart_points = draw_heart(scale=scale)
    canvas_data = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8) + 10  # Fondo oscuro
    
    # Dibujar estrellas
    for x, y in estrellas:
        x_int = int(x)
        y_int = int(y)
        if 0 <= x_int < canvas_width and 0 <= y_int < canvas_height:
            canvas_data[y_int-1:y_int+1, x_int-1:x_int+1] = [255, 255, 255]  # Blanco
    
    # Dibujar flores
    for x, y in flores:
        x_int = int(x)
        y_int = int(y)
        if 0 <= x_int < canvas_width and 0 <= y_int < canvas_height:
            canvas_data[y_int-2:y_int+2, x_int-2:x_int+2] = [255, 105, 180]  # Rosado
    
    return canvas_data, heart_points

# Variables de animación
scale = 1.0
creciendo = True

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

    # Actualizar posiciones
    update_positions()

    # Renderizar frame
    canvas_data, heart_points = render_frame()

    # Dibujar en Streamlit Canvas
    canvas_result = st_canvas(
        fill_color="rgba(0,0,0,0)",  # transparente
        stroke_width=2,
        background_color="#0a0a0a",
        height=canvas_height,
        width=canvas_width,
        drawing_mode="freedraw",
        key="canvas",
        display_toolbar=False
    )

    # Dibujar corazón y palabras
    for x, y in heart_points[::5]:  # cada 5 puntos para eficiencia
        st.markdown(
            f"<div style='position:absolute; left:{x}px; top:{y}px; color:{next(colores)}; font-size:24px; font-weight:bold;'>{nombre}</div>",
            unsafe_allow_html=True
        )

    for _ in range(5):  # palabras flotando aleatorias
        px = np.random.randint(canvas_width//4, 3*canvas_width//4)
        py = np.random.randint(canvas_height//4, 3*canvas_height//4)
        word = random.choice(palabras)
        st.markdown(
            f"<div style='position:absolute; left:{px}px; top:{py}px; color:#ffcc00; font-size:18px;'>{word}</div>",
            unsafe_allow_html=True
        )

    time.sleep(0.1)






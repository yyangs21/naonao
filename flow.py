import streamlit as st
import time
import random
from itertools import cycle

st.set_page_config(page_title="Corazón para Nahomy", page_icon="💖", layout="wide")

# Nombre y palabras bonitas
nombre = "Nahomy"
palabras = ["Increíble", "Valiente", "Amable", "Inspiradora", "Única", "Radiante", "Brillante", "Especial"]

# Patrón base del corazón
heart_pattern = [
    "  NNN   NNN  ",
    " NNNNN NNNNN ",
    "NNNNNNNNNNNNN",
    " NNNNNNNNNNN ",
    "  NNNNNNNNN  ",
    "   NNNNNNN   ",
    "    NNNNN    ",
    "     NNN     ",
    "      N      "
]

# Función para formar el corazón con el nombre
def formar_corazon(nombre, escala=1.0):
    lines = []
    for line in heart_pattern:
        idx = 0
        new_line = ""
        for char in line:
            if char == "N":
                new_line += nombre[idx % len(nombre)]
                idx += 1
            else:
                new_line += " "
        lines.append(new_line)
    if escala != 1.0:
        new_lines = []
        for line in lines:
            scaled_line = ""
            for c in line:
                scaled_line += c * int(escala)
            new_lines.extend([scaled_line]*int(escala))
        return new_lines
    return lines

# Ciclo de colores para el corazón
colores = cycle(["#ff4d6d", "#ff66a3", "#ff99c8", "#ff4d6d"])

# Placeholder para animación
placeholder = st.empty()

try:
    escala = 1.0
    creciendo = True
    while True:
        canvas = []
        # Latido del corazón
        if creciendo:
            escala += 0.05
            if escala >= 1.3:
                creciendo = False
        else:
            escala -= 0.05
            if escala <= 1.0:
                creciendo = True

        corazon = formar_corazon(nombre, escala)
        color_actual = next(colores)

        for row in corazon:
            new_row = ""
            for char in row:
                if char == " ":
                    # Espacios pueden ser estrellas o flores aleatorias
                    new_row += random.choice([" ", "⭐", "🌸", " "])
                else:
                    # Letras del nombre
                    new_row += char
            canvas.append(new_row)

        # Palabras flotando dentro del corazón
        palabras_line = "   ".join(random.sample(palabras, k=len(palabras)))

        # Mostrar en Streamlit
        placeholder.markdown(
            f"<pre style='font-size:20px; line-height:1.1; text-align:center; color:{color_actual}'>{'\n'.join(canvas)}</pre>\n"
            f"<h3 style='text-align:center; color:#ffcc00'>{palabras_line}</h3>",
            unsafe_allow_html=True
        )

        time.sleep(0.3)

except KeyboardInterrupt:
    placeholder.markdown("<h2 style='text-align:center; color:#ff4d6d;'>💖 Animación terminada 💖</h2>", unsafe_allow_html=True)



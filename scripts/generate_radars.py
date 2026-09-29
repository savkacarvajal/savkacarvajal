#!/usr/bin/env python3
"""
Genera los radares SVG de assets/radar-security.svg y assets/radar-languages.svg
usando la paleta negro/blanco/rojo (easykid) del perfil.

Edita los diccionarios SECURITY_SKILLS y LANGUAGE_SKILLS de abajo (valores 0-100,
son autoevaluación subjetiva, no vienen de ninguna fuente externa) y corre:

    python scripts/generate_radars.py
"""
import math
import os

# TODO(savka): estos valores son un punto de partida, ajústalos a tu criterio real.
SECURITY_SKILLS = {
    "Pentesting": 55,
    "Redes": 75,
    "Hardening": 65,
    "GRC": 60,
    "Cloud": 55,
    "Forense": 40,
}

# TODO(savka): idem, ajusta según tu nivel real en cada lenguaje.
LANGUAGE_SKILLS = {
    "Python": 70,
    "Bash": 55,
    "JavaScript": 60,
    "C++": 35,
    "SQL": 50,
}

BG = "#0d0d0d"
GRID = "#3a1216"
GRID_STRONG = "#5c1a20"
LINE = "#c1121f"
FILL = "#ff2a36"
DOT = "#f2f2f2"
LABEL = "#e6e6e6"
TITLE = "#f2f2f2"

SIZE = 500
CENTER = SIZE / 2
RADIUS = 125
RINGS = 4
FONT = "Consolas, 'Courier New', monospace"

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")


CENTER_Y = CENTER + 24


def point(angle_deg, r):
    angle = math.radians(angle_deg - 90)
    return CENTER + r * math.cos(angle), CENTER_Y + r * math.sin(angle)


def render_radar(title, skills):
    labels = list(skills.keys())
    values = list(skills.values())
    n = len(labels)
    step = 360 / n
    rot = step / 2

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" '
        f'width="{SIZE}" height="{SIZE}" role="img" aria-label="{title}">'
    )
    svg.append(f'<rect width="{SIZE}" height="{SIZE}" rx="16" fill="{BG}"/>')

    # anillos de la grilla
    for ring in range(1, RINGS + 1):
        r = RADIUS * ring / RINGS
        pts = [point(i * step + rot, r) for i in range(n)]
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        stroke = GRID_STRONG if ring == RINGS else GRID
        svg.append(f'<polygon points="{pts_str}" fill="none" stroke="{stroke}" stroke-width="1"/>')

    # ejes
    for i in range(n):
        x, y = point(i * step + rot, RADIUS)
        svg.append(f'<line x1="{CENTER}" y1="{CENTER_Y}" x2="{x:.1f}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')

    # polígono de datos
    data_pts = [point(i * step + rot, RADIUS * (values[i] / 100)) for i in range(n)]
    data_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in data_pts)
    svg.append(f'<polygon points="{data_str}" fill="{FILL}" fill-opacity="0.22" stroke="{LINE}" stroke-width="2.5"/>')

    for x, y in data_pts:
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{DOT}" stroke="{LINE}" stroke-width="1.5"/>')

    # etiquetas
    for i, label in enumerate(labels):
        lx, ly = point(i * step + rot, RADIUS + 38)
        anchor = "middle"
        if lx < CENTER - 10:
            anchor = "end"
        elif lx > CENTER + 10:
            anchor = "start"
        svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" font-family="{FONT}" font-size="13" '
            f'fill="{LABEL}" text-anchor="{anchor}">{label}</text>'
        )

    svg.append(
        f'<text x="{CENTER}" y="28" font-family="{FONT}" font-size="15" font-weight="700" '
        f'fill="{TITLE}" text-anchor="middle">{title}</text>'
    )

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    security_svg = render_radar("Security Skill Radar", SECURITY_SKILLS)
    with open(os.path.join(ASSETS_DIR, "radar-security.svg"), "w", encoding="utf-8") as f:
        f.write(security_svg)

    language_svg = render_radar("Language Radar", LANGUAGE_SKILLS)
    with open(os.path.join(ASSETS_DIR, "radar-languages.svg"), "w", encoding="utf-8") as f:
        f.write(language_svg)

    print("Generados: assets/radar-security.svg, assets/radar-languages.svg")


if __name__ == "__main__":
    main()

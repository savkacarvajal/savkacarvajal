#!/usr/bin/env python3
"""
Genera los radares SVG de assets/radar-security.svg y assets/radar-languages.svg
usando la paleta negro/blanco/rojo (easykid) del perfil.

Edita los diccionarios SECURITY_SKILLS y LANGUAGE_SKILLS de abajo (valores 0-100)
y corre:

    python scripts/generate_radars.py

Los valores de partida NO son inventados al azar: están acotados por la evidencia
real en tus repos públicos (gh api repos/.../languages y el contenido de cada
proyecto). Siguen siendo una estimación, no una medición exacta — ajústalos si no
reflejan tu nivel real.
"""
import math
import os

# Basado en la profundidad de evidencia real por repo, no en autoevaluación libre:
# - Redes (60): labs de Cisco Packet Tracer + GNS3 con OSPF/VLAN/DHCP y defensa oral.
# - GRC (55): sgsi-novaretail, un SGSI completo basado en ISO/IEC 27001:2022.
# - Cloud (45): AWS Gallery (despliegue + informe de arquitectura) y Firebase en
#   varios proyectos (shark2026, riego-iot-nodemcu, HomePass).
# - Hardening (35): lo mencionás como foco ACTUAL/en curso, no como algo ya asentado.
# - Pentesting (25): solo el badge de Kali Linux y la ingeniería inversa de BLE
#   (uLamp/Ambilight) — no hay un proyecto de pentesting formal en los repos.
# - Forense (10): sin evidencia en ningún repo.
# TODO(savka): siguen siendo una estimación — ajusta si no te representan.
SECURITY_SKILLS = {
    "Pentesting": 25,
    "Redes": 60,
    "Hardening": 35,
    "GRC": 55,
    "Cloud": 45,
    "Forense": 10,
}

# Basado en bytes de código por lenguaje (gh api repos/.../languages) sumados en
# todos tus repos públicos, con dos ajustes manuales:
# - Python: Gmexpress-Backend reporta ~15MB de Python, pero ese repo tiene una
#   carpeta venv/ commiteada (entorno virtual, no código tuyo) — descontado.
#   El resto es real: manage.py, apps de Django, scripts de utilidades, más el
#   Python de miksapropiedades.
# - SQL: no hay archivos .sql trackeados por GitHub, pero sí trabajo real con
#   bases de datos (MySQL en HomePass y Gmexpress-Backend) — se refleja bajo
#   pero no en cero.
# - Bash: la mayoría de tus "Shell" son scripts puntuales de despliegue, no
#   desarrollo central.
# TODO(savka): siguen siendo una estimación — ajusta si no te representan.
LANGUAGE_SKILLS = {
    "Python": 55,
    "Bash": 25,
    "JavaScript": 45,
    "C++": 30,
    "SQL": 30,
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

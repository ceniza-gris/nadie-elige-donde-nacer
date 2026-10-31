"""
Nadie elige dónde nacer
Un recorrido por la vida en Argentina con datos abiertos (EPH, Censo 2022, DEIS, BCRA, INDEC).

Para correrlo:  streamlit run app.py
Necesita, en la carpeta datos/: datos_juego.json y provincias.geojson
"""
import json
import math
import os
import random
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Nadie elige dónde nacer", page_icon="🎲", layout="wide")


# Si falta el archivo de colores (.streamlit/config.toml), lo crea. Se aplica al reiniciar Streamlit.
_TEMA = """[theme]
primaryColor = "#F2B705"
backgroundColor = "#EAF3F1"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1D2A3A"
font = "sans serif"
"""
if not os.path.exists(os.path.join(".streamlit", "config.toml")):
    try:
        os.makedirs(".streamlit", exist_ok=True)
        with open(os.path.join(".streamlit", "config.toml"), "w", encoding="utf-8") as _f:
            _f.write(_TEMA)
        st.toast("Se creó el archivo de colores. Reiniciá Streamlit (Ctrl + C y streamlit run app.py) para verlo.")
    except OSError:
        pass

st.markdown("""
<style>
/* menos espacio arriba: cubre los nombres que usan distintas versiones de Streamlit */
.block-container, [data-testid="stMainBlockContainer"], [data-testid="stAppViewBlockContainer"] {
  padding-top: 1.2rem !important; padding-bottom: 1.5rem !important; max-width: 1360px;}
header, .stAppHeader, [data-testid="stHeader"] {background: transparent !important; height: 2.6rem !important;
  min-height: 0 !important; box-shadow: none !important; border: none !important;}
.stAppDeployButton, [data-testid="stAppDeployButton"], [data-testid="stDecoration"] {display: none !important;}
[data-testid="stSidebarHeader"] {padding-bottom: 0 !important; height: 2.6rem !important;}
[data-testid="stSidebarUserContent"] {padding-top: 0 !important;}
h1 {padding-top: 0 !important; margin: 0 0 .2rem 0 !important; font-size: 2.1rem !important; letter-spacing: -0.02em;
  line-height: 1.15 !important;}
h2 {letter-spacing: -0.01em;}
[data-testid="stMetricValue"] {font-size: 1.9rem !important;}
/* botones principales con el color de acento aunque falte el tema */
button[kind="primary"] {background: #E3A008 !important; border-color: #E3A008 !important; color: #16253A !important; font-weight: 600;}
button[kind="primary"]:hover {background: #C98C05 !important; border-color: #C98C05 !important;}
/* dados */
.dados {display: flex; gap: 34px; justify-content: center; padding: 26px 0 30px; perspective: 700px;}
.dado-wrap {position: relative;}
.dado-wrap::after {content: ""; position: absolute; left: 6px; right: 6px; bottom: -16px; height: 8px;
  border-radius: 50%; background: rgba(22,37,58,.18); animation: sombra 1.3s ease-out forwards;}
.dado {width: 58px; height: 58px; position: relative; transform-style: preserve-3d;
  animation: rodar 1.3s cubic-bezier(.15,.65,.25,1) forwards;}
.cara {position: absolute; inset: 0; background: #FFFDF6; border: 2px solid #16253A; border-radius: 11px;
  display: grid; grid-template-columns: repeat(3,1fr); grid-template-rows: repeat(3,1fr); padding: 7px; box-sizing: border-box;}
.cara i {width: 10px; height: 10px; border-radius: 50%; background: #16253A; margin: auto;}
.c1 {transform: translateZ(29px);} .c2 {transform: rotateY(90deg) translateZ(29px);}
.c3 {transform: rotateY(180deg) translateZ(29px);} .c4 {transform: rotateY(-90deg) translateZ(29px);}
.c5 {transform: rotateX(90deg) translateZ(29px);} .c6 {transform: rotateX(-90deg) translateZ(29px);}
@keyframes rodar {
  0%   {transform: translateY(-70px) rotateX(0deg) rotateY(0deg);}
  55%  {transform: translateY(6px) rotateX(calc(var(--rx) * .85)) rotateY(calc(var(--ry) * .85));}
  72%  {transform: translateY(-14px) rotateX(calc(var(--rx) * .95)) rotateY(calc(var(--ry) * .95));}
  86%  {transform: translateY(0) rotateX(var(--rx)) rotateY(var(--ry));}
  93%  {transform: translateY(-4px) rotateX(var(--rx)) rotateY(var(--ry));}
  100% {transform: translateY(0) rotateX(var(--rx)) rotateY(var(--ry));}
}
@keyframes sombra {0% {transform: scale(.4); opacity: .2;} 55% {transform: scale(1); opacity: 1;}
  72% {transform: scale(.8);} 100% {transform: scale(1); opacity: 1;}}

/* ===== estilo juego de mesa ===== */
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@400;600;700;800&display=swap');
.stApp {background: #EAF3F1 radial-gradient(#d7e7e3 1.2px, transparent 1.2px) 0 0 / 22px 22px;}
.stApp p, .stApp li, .stApp label, .stApp button p {font-family: 'Nunito', 'Segoe UI', sans-serif;}
h1, h2, h3, h4, .carta-res, .tablero b {font-family: 'Baloo 2', 'Nunito', sans-serif !important;}
h1 {color: #1D2A3A;}
h4 {font-size: 1.25rem !important; margin-top: .6rem !important;}
button[kind="primary"], button[kind="secondary"] {border: 3px solid #1D2A3A !important; border-radius: 14px !important;
  box-shadow: 4px 4px 0 #1D2A3A !important; transition: transform .08s, box-shadow .08s; font-weight: 800 !important;}
button[kind="primary"]:active, button[kind="secondary"]:active {transform: translate(3px,3px); box-shadow: 1px 1px 0 #1D2A3A !important;}
[data-testid="stSidebar"] {background: #FFF8E6 !important; border-right: 3px solid #1D2A3A;}
/* tablero de etapas */
.tablero {display: flex; gap: 8px; margin: .3rem 0 1rem; flex-wrap: wrap;}
.casilla-e {flex: 1 1 120px; min-width: 112px; background: #fff; border: 3px solid #1D2A3A; border-radius: 14px;
  padding: 6px 8px; display: flex; align-items: center; gap: 8px; box-shadow: 3px 3px 0 #1D2A3A; opacity: .55;}
.casilla-e .ic {font-size: 1.3rem;}
.casilla-e b {font-size: 1rem; color: #1D2A3A; white-space: nowrap;}
.casilla-e .ok {display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%;
  background: #2A9D8F; color: #fff; font-size: .75rem; font-weight: 800; flex: none;}
.casilla-e.hecha {opacity: 1; background: #E7F6EF;}
.casilla-e.actual {opacity: 1; background: #F2B705; transform: translateY(-3px); box-shadow: 4px 6px 0 #1D2A3A;}
/* fichas de decisiones tomadas */
.ficha {display: flex; align-items: center; gap: 10px; background: #fff; border: 2.5px solid #1D2A3A; border-radius: 999px;
  padding: 5px 14px 5px 5px; margin: 2px 0 6px; box-shadow: 3px 3px 0 #1D2A3A; width: fit-content; max-width: 100%;}
.ficha .pct {background: #1D2A3A; color: #fff; border-radius: 999px; padding: 2px 10px; font-weight: 800; font-size: .9rem;
  font-family: 'Nunito', sans-serif; white-space: nowrap;}
.ficha .txt {font-weight: 700; color: #1D2A3A; font-family: 'Nunito', sans-serif;}
.ficha .sub {color: #5a6676; font-size: .82rem; font-family: 'Nunito', sans-serif;}
/* cartas de resultado */
.carta-res {position: relative; background: #fff; border: 3px solid #1D2A3A; border-radius: 18px; box-shadow: 6px 6px 0 #1D2A3A;
  margin: 1rem 0 1.1rem; overflow: hidden; animation: aparecer .45s cubic-bezier(.2,.9,.3,1.3) both;}
.carta-res .franja {padding: 8px 16px; display: flex; align-items: center; gap: 10px; border-bottom: 3px solid #1D2A3A;
  font-weight: 800; letter-spacing: .04em; text-transform: uppercase; font-size: .85rem; color: #1D2A3A;}
.carta-res .franja .ic {font-size: 1.4rem;}
.carta-res .cuerpo {padding: 12px 18px 16px;}
.carta-res .titulo {font-size: 2rem; font-weight: 800; line-height: 1.1; color: #1D2A3A; margin-bottom: 8px;}
.carta-res .linea {font-family: 'Nunito', sans-serif; color: #33414f; font-size: .98rem; margin: 6px 0 0; line-height: 1.45;}
.carta-res .chips {display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;}
.carta-res .chip {font-family: 'Nunito', sans-serif; font-weight: 800; font-size: .88rem; border: 2px solid #1D2A3A;
  border-radius: 999px; padding: 3px 12px; background: #F4F7F9; color: #1D2A3A;}
.carta-res .chip.fuerte {background: #1D2A3A; color: #fff;}
.carta-res .sello {position: absolute; right: 14px; top: 46px; width: 74px; height: 74px; border-radius: 50%;
  border: 3px dashed #1D2A3A; display: flex; flex-direction: column; align-items: center; justify-content: center;
  transform: rotate(-10deg); background: #FFF8E6; font-family: 'Baloo 2', sans-serif; color: #1D2A3A; line-height: 1;}
.carta-res .sello b {font-size: 1.5rem;} .carta-res .sello small {font-size: .62rem; text-align: center; font-weight: 700;}
.carta-res.con-sello .titulo, .carta-res.con-sello .chips, .carta-res.con-sello .linea:first-of-type {padding-right: 84px;}
.vida-grid {display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; margin-top: 10px;}
.vida-grid div {border: 2.5px solid #1D2A3A; border-radius: 12px; padding: 8px 10px; background: #F4F7F9; font-family: 'Nunito', sans-serif;}
.vida-grid small {display: block; font-weight: 800; color: #5a6676; text-transform: uppercase; font-size: .7rem; letter-spacing: .05em;}
.vida-grid span {font-weight: 700; color: #1D2A3A;}
@keyframes aparecer {from {opacity: 0; transform: translateY(14px) rotate(-1.5deg) scale(.96);} to {opacity: 1; transform: none;}}
@media (prefers-reduced-motion: reduce) {.dado, .dado-wrap::after, .carta-res {animation-duration: .01s;}}
</style>
""", unsafe_allow_html=True)

PIPS = {1: [5], 2: [1, 9], 3: [1, 5, 9], 4: [1, 3, 7, 9], 5: [1, 3, 5, 7, 9], 6: [1, 3, 4, 6, 7, 9]}


def dados_html(n=2):
    """Dos dados en 3D que caen, rebotan y giran hasta quedar quietos."""
    def cara(k):
        pips = "".join(f'<i style="grid-row:{(p - 1) // 3 + 1};grid-column:{(p - 1) % 3 + 1}"></i>' for p in PIPS[k])
        return f'<div class="cara c{k}">{pips}</div>'
    dados = ""
    for _ in range(n):
        rx = 360 * random.choice([2, 3]) + 90 * random.randint(0, 3)
        ry = 360 * random.choice([2, 3]) + 90 * random.randint(0, 3)
        dados += (f'<div class="dado-wrap"><div class="dado" style="--rx:{rx}deg;--ry:{ry}deg">'
                  + "".join(cara(k) for k in range(1, 7)) + "</div></div>")
    return f'<div class="dados">{dados}</div>'


def tirar_dados(segundos=1.4):
    """Muestra la animación de los dados mientras se espera el resultado."""
    lugar = st.empty()
    lugar.markdown(dados_html(), unsafe_allow_html=True)
    time.sleep(segundos)

SOL = "#E3A008"
TINTA = "#16253A"
GRIS = "#C9D3DC"
AZUL = "#3E6E96"

ETAPAS = ["Nacer", "Estudiar", "Trabajar", "Hijos", "Deudas", "Vejez"]
NIVELES = {
    "sec_i": "Secundario incompleto", "sec_c": "Secundario completo",
    "ter_i": "Terciario incompleto", "ter_c": "Terciario completo",
    "uni_i": "Universitario incompleto", "uni_c": "Universitario completo",
    "posg": "Posgrado",
}
REGIONES = {"CABA": "la Ciudad de Buenos Aires", "BA": "la provincia de Buenos Aires",
            "PAM": "la región Pampeana", "CUY": "Cuyo", "NOA": "el Noroeste",
            "NEA": "el Noreste", "PAT": "la Patagonia"}


# ---------------------------------------------------------------- datos
@st.cache_data
def cargar(version):
    """_version = fecha de modificación de los archivos: si cambian, se vuelven a leer."""
    with open("datos/datos_juego.json", encoding="utf-8") as f:
        datos = json.load(f)
    with open("datos/provincias.geojson", encoding="utf-8") as f:
        geo = json.load(f)
    return datos, geo


D, GEO = cargar(os.path.getmtime("datos/datos_juego.json") + os.path.getmtime("datos/provincias.geojson"))
_FALTAN = [k for k in ("deuda_provincias", "jubilacion") if k not in D]
if _FALTAN:
    st.error("Tu archivo datos/datos_juego.json es de una versión anterior (le falta: " + ", ".join(_FALTAN) +
             "). Reemplazalo por el que viene en el zip más nuevo.")
    st.stop()
PROV = D["provincias"]


# ---------------------------------------------------------------- utilidades
def pct(x):
    """Porcentaje en formato argentino: 37% o 4,2%."""
    return f"{round(x * 100)}%" if x >= 0.1 else f"{x * 100:.1f}%".replace(".", ",")


def num(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


def de_region(z):
    return ("de " + REGIONES[z]).replace("de el ", "del ")


def sexo_txt(s, mayus=False):
    t = "varón" if s == "varon" else "mujer"
    return t.capitalize() if mayus else t


def nuevo_juego():
    st.session_state.etapa = 1
    st.session_state.jugador = {}
    st.session_state.res = {}


if "etapa" not in st.session_state:
    nuevo_juego()

J = st.session_state.jugador
RES = st.session_state.res


def borrar_etapa(n):
    """Borra las decisiones de la etapa n y de todas las siguientes."""
    for k in [k for k in RES if int(k.split("_")[0]) >= n]:
        del RES[k]
    for campo, desde in [("edu", 2), ("trabajo", 3), ("hijos", 4), ("deuda", 5), ("edad_muerte", 6), ("jubilacion", 6)]:
        if desde >= n:
            J.pop(campo, None)


def cum_etapa(n):
    """Probabilidad acumulada del camino recorrido en la etapa n."""
    p = 1.0
    for k, v in RES.items():
        if k.startswith(f"{n}_"):
            p *= v[2]
    return p


ICONOS = {1: "👶", 2: "🎓", 3: "💼", 4: "👨‍👩‍👧", 5: "💳", 6: "👵"}
COLORES = {1: "#F2B705", 2: "#7FC8A9", 3: "#8EC5FC", 4: "#F7A8B8", 5: "#F4A261", 6: "#C3B1E1"}


def tablero_html(etapa_actual):
    """Las seis etapas como casillas de un tablero."""
    cas = []
    for i, nombre in enumerate(ETAPAS, start=1):
        clase = "actual" if i == etapa_actual else "hecha" if i < etapa_actual else ""
        marca = '<span class="ok">✓</span>' if i < etapa_actual else ""
        cas.append(f'<div class="casilla-e {clase}"><span class="ic">{ICONOS[i]}</span><b>{nombre}</b>{marca}</div>')
    return '<div class="tablero">' + "".join(cas) + "</div>"


def ficha_html(texto, p):
    return (f'<div class="ficha"><span class="pct">{pct(p)}</span><span class="txt">{texto}</span>'
            f'<span class="sub">de las personas como vos</span></div>')


def carta(n, rotulo, titulo, lineas=(), chips=(), sello=None):
    """Carta de resultado al estilo de un juego de mesa. sello = (número grande, texto chico) o None."""
    chips_html = "".join(f'<span class="chip{" fuerte" if i == 0 else ""}">{c}</span>' for i, c in enumerate(chips))
    lin = "".join(f'<p class="linea">{l}</p>' for l in lineas)
    sel = f'<div class="sello"><b>{sello[0]}</b><small>{sello[1]}</small></div>' if sello else ""
    html = (f'<div class="carta-res{" con-sello" if sello else ""}">'
            f'<div class="franja" style="background:{COLORES[n]}"><span class="ic">{ICONOS[n]}</span>{rotulo}</div>'
            f'{sel}<div class="cuerpo"><div class="titulo">{titulo}</div>'
            f'{"<div class=chips>" + chips_html + "</div>" if chips else ""}{lin}</div></div>')
    st.markdown(html, unsafe_allow_html=True)


def sello_camino(n):
    v = cum_etapa(n) * 100
    return ("<1" if v < 1 else str(round(v)), "de cada 100<br>llegan acá")


def md(t):
    """Negritas de markdown a HTML para usar dentro de las cartas."""
    import re as _re
    return _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def decision(sid, pregunta, opciones, nota=None):
    """
    Muestra una decisión con sus probabilidades.
    opciones: lista de (clave, texto, probabilidad, descripción opcional).
    Devuelve la clave elegida, o None si el jugador todavía no decidió.
    """
    st.markdown(f"#### {pregunta}")
    total = sum(o[2] for o in opciones)
    opciones = [(o[0], o[1], o[2] / total, o[3] if len(o) > 3 else "") for o in opciones]
    if sid in RES:
        clave, texto, p = RES[sid]
        st.markdown(ficha_html(texto, p), unsafe_allow_html=True)
        return clave
    for _, texto, p, desc in opciones:
        st.progress(min(max(p, 0.0), 1.0), text=f"{texto}: {pct(p)}" + (f" — {desc}" if desc else ""))
    if nota:
        st.caption(nota)
    if st.session_state.get("modo", "azar") == "azar":
        if st.button("🎲 Tirar los dados", key=f"btn_{sid}", type="primary"):
            tirar_dados()
            elegida = random.choices(opciones, weights=[o[2] for o in opciones])[0]
            RES[sid] = (elegida[0], elegida[1], elegida[2])
            st.rerun()
    else:
        cols = st.columns(min(len(opciones), 2))
        for i, (clave, texto, p, _) in enumerate(opciones):
            if cols[i % len(cols)].button(texto, key=f"btn_{sid}_{clave}", width="stretch"):
                RES[sid] = (clave, texto, p)
                st.rerun()
    return None


def grilla_100(cum, subtitulo):
    """Grilla de 100 puntos: cuántas personas como vos llegan hasta acá."""
    n = round(cum * 100)
    xs = [i % 10 for i in range(100)]
    ys = [9 - i // 10 for i in range(100)]
    colores = [SOL if i < n else GRIS for i in range(100)]
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="markers", hoverinfo="skip",
                               marker=dict(size=22, color=colores)))
    fig.update_layout(height=330, margin=dict(l=0, r=0, t=0, b=0),
                      xaxis=dict(visible=False, range=[-0.7, 9.7]),
                      yaxis=dict(visible=False, range=[-0.7, 9.7], scaleanchor="x"),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.markdown(f"### {'Menos de 1' if n < 1 and cum > 0 else n} de 100")
    st.caption(subtitulo)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def barras(filas, resaltar=None, formato=pct, alto=None):
    """Barras horizontales simples; resalta una fila con el color de acento."""
    df = pd.DataFrame(filas, columns=["etiqueta", "valor"])
    marcar = resaltar if isinstance(resaltar, (list, tuple, set)) else [resaltar]
    df["color"] = [SOL if e in marcar else AZUL for e in df.etiqueta]
    fig = go.Figure(go.Bar(x=df.valor, y=df.etiqueta, orientation="h", marker_color=df.color,
                           text=[formato(v) for v in df.valor], textposition="outside",
                           hoverinfo="skip"))
    fig.update_layout(height=alto or 40 * len(filas) + 30, margin=dict(l=0, r=40, t=5, b=5),
                      xaxis=dict(visible=False, range=[0, df.valor.max() * 1.2]),
                      yaxis=dict(autorange="reversed"), plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ---------------------------------------------------------------- mapa
K_LAT = math.cos(math.radians(38))  # corrige la deformación este-oeste a la latitud media del país
CABA_XY = (-58.45 * K_LAT, -34.61)


def _anillos(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        ring = poly[0]
        yield [x * K_LAT for x, _ in ring], [y for _, y in ring]


FORMAS = {f["properties"]["provincia"]: list(_anillos(f["geometry"])) for f in GEO["features"]}
ESCALA = "Blues"


def mapa(valores, titulo, fmt=lambda v: num(v), resaltar=None, alto=560, escala=None):
    """Mapa de provincias dibujado como polígonos: no depende de servicios externos y llena todo el espacio."""
    from plotly.colors import sample_colorscale
    escala = escala or ESCALA
    validos = [v for v in valores.values() if v is not None]
    vmin, vmax = min(validos), max(validos)
    txt = lambda v: "sin dato" if v is None else fmt(v)

    def color(v):
        if v is None:
            return "#D5DBE1"
        t = (v - vmin) / (vmax - vmin) if vmax > vmin else 0.5
        return sample_colorscale(escala, [0.1 + 0.9 * t])[0]

    fig = go.Figure()
    for prov, partes in FORMAS.items():
        elegida = prov == resaltar
        for xs, ys in partes:
            fig.add_trace(go.Scatter(
                x=xs, y=ys, fill="toself", mode="lines", hoveron="fills", showlegend=False,
                fillcolor=SOL if elegida else color(valores[prov]),
                line=dict(color=TINTA if elegida else "white", width=2 if elegida else 0.7),
                text=f"<b>{prov}</b><br>{titulo}: {txt(valores[prov])}", hoverinfo="text"))
    # CABA es demasiado chica para verse: se marca con un círculo al este de su ubicación real
    cx, cy = CABA_XY
    caba = "Ciudad de Buenos Aires"
    fig.add_trace(go.Scatter(x=[cx, cx + 1.6], y=[cy, cy + 0.5], mode="lines", hoverinfo="skip",
                             line=dict(color=TINTA, width=0.8), showlegend=False))
    fig.add_trace(go.Scatter(
        x=[cx + 1.6], y=[cy + 0.5], mode="markers+text", text=["CABA"], textposition="middle right",
        textfont=dict(size=11, color=TINTA), showlegend=False, hoverinfo="text",
        hovertext=f"<b>{caba}</b><br>{titulo}: {txt(valores[caba])}",
        marker=dict(size=13, color=SOL if resaltar == caba else color(valores[caba]),
                    line=dict(color=TINTA, width=1.2))))
    # barra de colores horizontal debajo del mapa
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers", hoverinfo="skip", showlegend=False,
        marker=dict(colorscale=[[i / 10, sample_colorscale(escala, [0.1 + 0.09 * i])[0]] for i in range(11)],
                    cmin=vmin, cmax=vmax, color=[vmin],
                    colorbar=dict(title=dict(text=titulo, side="top"), orientation="h", x=0.5, y=0,
                                  xanchor="center", yanchor="top", len=0.7, thickness=8, outlinewidth=0,
                                  title_font=dict(size=12), tickfont=dict(size=11)))))
    fig.update_layout(height=alto, margin=dict(l=0, r=0, t=0, b=48), dragmode=False,
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      xaxis=dict(visible=False, fixedrange=True),
                      yaxis=dict(visible=False, scaleanchor="x", fixedrange=True),
                      hoverlabel=dict(bgcolor=TINTA, font_color="white"))
    return fig


def boton_seguir(siguiente, texto):
    if st.button(texto, type="primary", key=f"seguir_{siguiente}"):
        st.session_state.etapa = siguiente
        st.rerun()


def boton_reintentar(n):
    if st.button("Volver a intentar esta etapa", key=f"reintentar_{n}"):
        borrar_etapa(n)
        st.rerun()


# ---------------------------------------------------------------- avatar
PIELES = ["#F1C9A5", "#D9A27C", "#B07A55", "#7A5139"]


def avatar_svg(j, etapa):
    """Dibuja una persona simple que cambia con el sexo, la edad y lo que pasó en la vida."""
    mujer = j["sexo"] == "mujer"
    piel = PIELES[j.get("piel", 0)]
    if etapa == 1:
        edad = "bebe"
    elif etapa == 2:
        edad = "joven"
    elif etapa == 6:
        edad = "mayor"
    else:
        edad = "adulto"
    pelo = "#B9BEC4" if edad == "mayor" else "#3B2A20"
    ropa = "#3E6E96" if mujer else "#2F5D50"
    p = []
    if edad == "bebe":
        # bebé envuelto en una manta
        p.append('<ellipse cx="80" cy="150" rx="42" ry="34" fill="#F6E7B8" stroke="#E3A008" stroke-width="2"/>')
        p.append(f'<circle cx="80" cy="105" r="28" fill="{piel}"/>')
        p.append(f'<path d="M58 96 Q80 70 102 96 Q92 86 80 88 Q68 86 58 96Z" fill="{pelo}"/>')
        if mujer:
            p.append('<circle cx="100" cy="86" r="5" fill="#E3A008"/>')  # moñito
        p.append('<circle cx="71" cy="106" r="2.6" fill="#16253A"/><circle cx="89" cy="106" r="2.6" fill="#16253A"/>')
        p.append('<path d="M73 116 Q80 121 87 116" stroke="#16253A" stroke-width="2" fill="none" stroke-linecap="round"/>')
    else:
        alto = 0.88 if edad == "joven" else 1.0
        p.append(f'<g transform="translate(80 200) scale({alto}) translate(-80 -200)">')
        if mujer:  # pelo largo detrás de la cabeza
            p.append(f'<path d="M50 72 Q48 120 58 128 L102 128 Q112 120 110 72 Q80 40 50 72Z" fill="{pelo}"/>')
        # piernas y cuerpo
        p.append('<rect x="64" y="150" width="13" height="44" rx="5" fill="#16253A"/>')
        p.append('<rect x="83" y="150" width="13" height="44" rx="5" fill="#16253A"/>')
        if mujer:
            p.append(f'<path d="M58 100 L102 100 L110 162 L50 162Z" fill="{ropa}"/>')
        else:
            p.append(f'<rect x="56" y="100" width="48" height="58" rx="12" fill="{ropa}"/>')
        p.append(f'<rect x="46" y="104" width="11" height="44" rx="5" fill="{piel}"/>')
        p.append(f'<rect x="103" y="104" width="11" height="44" rx="5" fill="{piel}"/>')
        trab = j.get("trabajo", {}).get("tipo") if etapa >= 3 else None
        if trab == "formal":  # corbata o pañuelo
            p.append('<path d="M80 102 L74 110 L80 136 L86 110Z" fill="#E3A008"/>')
        if edad == "joven":  # mochila
            p.append('<path d="M60 102 L66 150" stroke="#E3A008" stroke-width="4"/><path d="M100 102 L94 150" stroke="#E3A008" stroke-width="4"/>')
        # cabeza
        p.append(f'<rect x="74" y="88" width="12" height="14" fill="{piel}"/>')
        p.append(f'<circle cx="80" cy="72" r="24" fill="{piel}"/>')
        if mujer:
            p.append(f'<path d="M56 72 Q58 44 80 46 Q102 44 104 72 Q96 56 80 58 Q66 58 56 72Z" fill="{pelo}"/>')
        else:
            p.append(f'<path d="M56 70 Q56 44 80 46 Q104 44 104 70 Q100 58 80 58 Q60 58 56 70Z" fill="{pelo}"/>')
        p.append('<circle cx="72" cy="74" r="2.6" fill="#16253A"/><circle cx="88" cy="74" r="2.6" fill="#16253A"/>')
        p.append('<path d="M73 84 Q80 89 87 84" stroke="#16253A" stroke-width="2" fill="none" stroke-linecap="round"/>')
        if edad == "mayor":  # anteojos y bastón
            p.append('<circle cx="72" cy="74" r="6" fill="none" stroke="#16253A" stroke-width="1.6"/>'
                     '<circle cx="88" cy="74" r="6" fill="none" stroke="#16253A" stroke-width="1.6"/>'
                     '<path d="M78 74 L82 74" stroke="#16253A" stroke-width="1.6"/>')
            p.append('<path d="M114 146 L118 196 M114 146 Q112 138 104 140" stroke="#7A5139" stroke-width="4" fill="none" stroke-linecap="round"/>')
        if j.get("edu") in ("ter_c", "uni_c", "posg") and etapa >= 2:  # birrete
            p.append('<path d="M52 50 L80 38 L108 50 L80 62Z" fill="#16253A"/>')
            p.append('<rect x="66" y="52" width="28" height="8" fill="#16253A"/>')
            p.append('<path d="M106 50 L108 66" stroke="#E3A008" stroke-width="2"/><circle cx="108" cy="67" r="3" fill="#E3A008"/>')
        p.append('</g>')
    # hijos: figuras chicas a la izquierda (a la derecha va el bastón)
    n = min(4, j.get("hijos", {}).get("n", 0)) if etapa >= 4 else 0
    for k in range(n):
        x, y = 14 + (k % 2) * 20, 146 + (k // 2) * 33
        p.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{piel}"/>'
                 f'<rect x="{x - 7}" y="{y + 8}" width="14" height="16" rx="5" fill="#E3A008"/>')
    return ('<svg viewBox="0 0 180 205" width="100%" style="max-width:190px;display:block;margin:4px auto 0" '
            'role="img" aria-label="Tu avatar" xmlns="http://www.w3.org/2000/svg">' + "".join(p) + "</svg>")


# ---------------------------------------------------------------- barra lateral
with st.sidebar:
    st.markdown("## 🎲 Nadie elige dónde nacer")
    st.radio("Modo de juego", ["azar", "elegir"], key="modo", horizontal=True,
             format_func=lambda m: "Que decida el azar" if m == "azar" else "Elegir yo")
    st.divider()
    if J:
        st.markdown("**Tu vida hasta ahora**")
        edades = {1: "Recién nacido" if J["sexo"] == "varon" else "Recién nacida", 2: "18 años", 3: "30 años",
                  4: "33 años", 5: "35 años",
                  6: f"{J['edad_muerte']} años" if "edad_muerte" in J else "65 años"}
        st.markdown(avatar_svg(J, st.session_state.etapa), unsafe_allow_html=True)
        st.caption(edades[st.session_state.etapa])
        st.markdown(f"- {sexo_txt(J['sexo'], True)} en {J['provincia']}, clase {J['clase']}")
        if "edu" in J:
            st.markdown(f"- {NIVELES[J['edu']]}")
        if "trabajo" in J:
            st.markdown(f"- {J['trabajo']['texto']}")
        if "hijos" in J:
            st.markdown(f"- {J['hijos']['texto']}")
        if "deuda" in J:
            st.markdown(f"- {J['deuda']['texto']}")
    st.divider()
    if st.button("Volver a nacer"):
        nuevo_juego()
        st.rerun()

st.title("Nadie elige dónde nacer")
etapa = st.session_state.etapa
st.markdown(tablero_html(etapa), unsafe_allow_html=True)


# ---------------------------------------------------------------- etapa 1: nacer
def etapa_nacer():
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        capas = {
            "Nacimientos": ("% de los nacimientos del país", lambda p, i: i["pct_nacimientos"]),
            "Esperanza de vida": ("Esperanza de vida al nacer (años)",
                                  lambda p, i: (i["esperanza_vida_varones"] + i["esperanza_vida_mujeres"]) / 2),
            "Hogares de ingreso bajo": ("% de chicos en los dos quintiles más pobres",
                                        lambda p, i: D["quint"][p][0] + D["quint"][p][1]),
            "Madres adolescentes": ("% de bebés de madres menores de 20 años",
                                    lambda p, i: i["pct_madres_menores_20"]),
        }
        capa = st.segmented_control("Colorear el mapa por", list(capas), default="Nacimientos",
                                    label_visibility="collapsed") or "Nacimientos"
        titulo, f = capas[capa]
        valores = {p: f(p, i) for p, i in PROV.items()}
        fig = mapa(valores, titulo, resaltar=J.get("provincia"))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption("Las Islas Malvinas se muestran como parte de Tierra del Fuego, Antártida e Islas del Atlántico Sur.")

    with der:
        provincias = list(PROV)
        pesos = [PROV[p]["pct_nacimientos"] for p in provincias]
        pv = D["prob_varon_al_nacer"]
        if st.session_state.modo == "azar":
            if st.button("🎲 Nacer", type="primary", width="stretch"):
                tirar_dados()
                prov = random.choices(provincias, weights=pesos)[0]
                sexo = "varon" if random.random() < pv else "mujer"
                q = random.choices([1, 2, 3, 4, 5], weights=D["quint"][prov])[0]
                borrar_etapa(2)
                J.update(provincia=prov, sexo=sexo, clase="baja" if q <= 2 else "media" if q <= 4 else "alta",
                         piel=random.randrange(len(PIELES)))
                st.rerun()
        else:
            prov = st.selectbox("¿Dónde nacés?", provincias,
                                index=provincias.index(J["provincia"]) if J else 0)
            sexo = st.radio("¿Varón o mujer?", ["mujer", "varon"], horizontal=True, format_func=sexo_txt)
            clase = st.radio("¿En qué hogar?", ["baja", "media", "alta"], horizontal=True,
                             format_func=lambda c: f"Clase {c}")
            if st.button("Nacer así", type="primary", width="stretch"):
                borrar_etapa(2)
                J.update(provincia=prov, sexo=sexo, clase=clase, piel=random.randrange(len(PIELES)))
                st.rerun()

        if not J:
            st.info("Todavía no naciste. Tocá **Nacer** para empezar.")
            return
        prov, info = J["provincia"], PROV[J["provincia"]]
        q = D["quint"][prov]
        qs = {"baja": [0, 1], "media": [2, 3], "alta": [4]}[J["clase"]]
        p_clase = sum(q[i] for i in qs) / 100
        p_sexo = pv if J["sexo"] == "varon" else 1 - pv
        p_prov = info["pct_nacimientos"] / 100
        e0 = info["esperanza_vida_varones"] if J["sexo"] == "varon" else info["esperanza_vida_mujeres"]
        uno_en = max(1, round(1 / (p_prov * p_sexo * p_clase)))
        carta(1, "Tu punto de partida", f"{sexo_txt(J['sexo'], True)} en {prov}",
              chips=[f"Clase {J['clase']}", f"Esperanza de vida: {num(e0)} años"],
              lineas=[f"<b>{pct(p_prov)}</b> de los bebés del país nacen en {prov}.",
                      f"<b>{pct(p_sexo)}</b> de probabilidad de nacer {sexo_txt(J['sexo'])}.",
                      f"<b>{pct(p_clase)}</b> de los chicos de {prov} crecen en un hogar de clase {J['clase']}."],
              sello=("1/" + f"{uno_en:,}".replace(",", "."), "bebés nace<br>como vos"))
        st.caption("Cómo se reparten los chicos de tu provincia según el ingreso del hogar:")
        barras([("20% más pobre", q[0] / 100), ("Quintil 2", q[1] / 100), ("Quintil 3", q[2] / 100),
                ("Quintil 4", q[3] / 100), ("20% más rico", q[4] / 100)],
               resaltar={"baja": ["20% más pobre", "Quintil 2"], "media": ["Quintil 3", "Quintil 4"],
                         "alta": ["20% más rico"]}[J["clase"]])
        boton_seguir(2, "Seguir: estudiar →")


# ---------------------------------------------------------------- etapa 2: estudiar
def prob_nivel(nivel, zona, clase, sexo):
    p = D["edu"][f"{zona}|{clase}|{sexo}"]
    q = D["edu2"][f"{zona}|{sexo}"]
    s = p["sec"] * p["sup"]
    u, t = s * p["uni"], s * (1 - p["uni"])
    return {"sec_i": 1 - p["sec"], "sec_c": p["sec"] * (1 - p["sup"]),
            "ter_i": t * (1 - q["egr_ter"]), "ter_c": t * q["egr_ter"],
            "uni_i": u * (1 - q["egr_uni"]), "uni_c": u * q["egr_uni"] * (1 - q["posg"]),
            "posg": u * q["egr_uni"] * q["posg"]}[nivel]


def etapa_estudiar():
    zona = PROV[J["provincia"]]["region"]
    p = D["edu"][f"{zona}|{J['clase']}|{J['sexo']}"]
    q = D["edu2"][f"{zona}|{J['sexo']}"]
    izq, der = st.columns([2, 3], gap="large")
    with der:
        st.caption(f"{sexo_txt(J['sexo'], True)} de {J['provincia']}, clase {J['clase']}. "
                   f"Se usan los datos {de_region(zona)}.")
        nivel = None
        r = decision("2_sec", "¿Terminás la secundaria?",
                     [("si", "La termino", p["sec"]), ("no", "La dejo", 1 - p["sec"])])
        if r == "no":
            nivel = "sec_i"
        elif r == "si":
            r = decision("2_sup", "¿Seguís estudiando después?",
                         [("si", "Sigo estudiando", p["sup"]), ("no", "Salgo a trabajar", 1 - p["sup"])])
            if r == "no":
                nivel = "sec_c"
            elif r == "si":
                tipo = decision("2_tipo", "¿Universidad o terciario?",
                                [("uni", "Universidad", p["uni"]), ("ter", "Terciario", 1 - p["uni"])])
                if tipo:
                    priv = p["priv_" + tipo]
                    g = decision("2_gest", "¿Pública o privada?",
                                 [("pub", "Pública", 1 - priv), ("priv", "Privada", priv)])
                    if g:
                        egr = q["egr_" + tipo]
                        r = decision("2_egr", "¿Te recibís?",
                                     [("si", "Me recibo", egr), ("no", "Lo dejo", 1 - egr)])
                        if r == "no":
                            nivel = tipo + "_i"
                        elif r == "si" and tipo == "ter":
                            nivel = "ter_c"
                        elif r == "si":
                            r = decision("2_posg", "¿Hacés un posgrado?",
                                         [("si", "Hago un posgrado", q["posg"]),
                                          ("no", "Hasta acá llego", 1 - q["posg"])],
                                         nota="La EPH no distingue entre maestría y doctorado.")
                            if r:
                                nivel = "posg" if r == "si" else "uni_c"
        if nivel:
            J["edu"] = nivel
            st.divider()
            carta(2, "Tu educación", NIVELES[nivel], sello=sello_camino(2))
            st.markdown(f"De cada 100 {'chicos' if J['sexo'] == 'varon' else 'chicas'} {de_region(zona)}, "
                        "cuántos llegan a tu mismo nivel educativo según la clase del hogar en el que nacen:")
            barras([(f"Clase {c}", prob_nivel(nivel, zona, c, J["sexo"])) for c in ["baja", "media", "alta"]],
                   resaltar=f"Clase {J['clase']}")
            boton_seguir(3, "Seguir: trabajar →")
            boton_reintentar(2)
    with izq:
        grilla_100(cum_etapa(2), "chicos que nacen como vos llegan hasta este punto de tu camino")


# ---------------------------------------------------------------- etapa 3: trabajar
CALIF = [("1", "Profesional", "requiere título universitario"),
         ("2", "Técnico", "conocimientos específicos, como enfermería o programación"),
         ("3", "Operativo", "habilidades prácticas, como ventas u oficios"),
         ("4", "No calificado", "tareas sin formación específica, como limpieza o carga")]


def ingreso(zona, nivel, sexo, calif, tipo):
    """Ingreso relativo al mediano nacional, según el modelo log-lineal estimado con la EPH."""
    c = D["coef"]

    def g(var, v):
        return c.get(f"C({var})[T.{v}]", 0)

    return math.exp(c["Intercept"] + g("zona", zona) + g("niv", nivel) + g("sexo", sexo)
                    + g("calif", calif) + g("tipo", tipo)) * D["smear"]


def etapa_trabajar():
    zona, nivel = PROV[J["provincia"]]["region"], J["edu"]
    T = D["tr"][f"{zona}|{nivel}|{J['sexo']}"]
    izq, der = st.columns([2, 3], gap="large")
    with der:
        st.caption(f"{sexo_txt(J['sexo'], True)} con {NIVELES[nivel].lower()}. "
                   f"Datos de personas de 25 a 44 años {de_region(zona)}.")
        r = decision("3_ocup", "¿Conseguís trabajo?",
                     [("si", "Consigo trabajo", T["ocup"]), ("no", "Sigo buscando", 1 - T["ocup"])])
        if r == "no":
            J["trabajo"] = {"tipo": "desoc", "texto": "Desocupado" if J["sexo"] == "varon" else "Desocupada"}
            st.divider()
            carta(3, "Tu trabajo", J["trabajo"]["texto"], sello=sello_camino(3),
                  lineas=[f"Le pasa a <b>{pct(1 - T['ocup'])}</b> de las personas con tu perfil que buscan trabajo."])
        elif r == "si":
            cal = decision("3_calif", "¿Qué tipo de trabajo hacés?",
                           [(k, txt, T[f"cal{k}"], desc) for k, txt, desc in CALIF])
            if cal:
                a = T[f"asal{cal}"]
                cat = decision("3_cat", "¿Con un empleador o por tu cuenta?",
                               [("asal", "Con un empleador", a), ("cp", "Por mi cuenta", 1 - a)])
                tipo = None
                if cat == "cp":
                    tipo = "cp"
                elif cat == "asal":
                    pub = T[f"pub{cal}"]
                    sec = decision("3_sector", "¿En el Estado o en el sector privado?",
                                   [("pub", "En el Estado", pub), ("priv", "En el sector privado", 1 - pub)])
                    if sec == "pub":
                        tipo = "pub"
                    elif sec == "priv":
                        fo = T[f"form{cal}"]
                        f = decision("3_form", "¿En blanco o en negro?",
                                     [("f", "En blanco", fo), ("i", "En negro", 1 - fo)])
                        if f:
                            tipo = "priv_f" if f == "f" else "priv_i"
                if tipo:
                    textos = {"cp": "por tu cuenta", "pub": "en el Estado",
                              "priv_f": "en blanco", "priv_i": "en negro"}
                    trab = "informal" if tipo in ("cp", "priv_i") else "formal"
                    nombre = dict((k, t) for k, t, _ in CALIF)[cal]
                    J["trabajo"] = {"tipo": trab, "texto": f"Trabajo {nombre.lower()}, {textos[tipo]}"}
                    r_yo = ingreso(zona, nivel, J["sexo"], cal, tipo)
                    otro = "mujer" if J["sexo"] == "varon" else "varon"
                    r_otro = ingreso(zona, nivel, otro, cal, tipo)
                    debajo = sum(1 for x in D["pcts"] if x < r_yo)
                    st.divider()
                    carta(3, "Tu trabajo", J["trabajo"]["texto"], sello=sello_camino(3),
                          chips=[f"Ganás {num(r_yo)} veces el ingreso mediano",
                                 f"Más que {max(1, debajo)} de cada 100 personas ocupadas"])
                    h = D["hrs"]
                    h_yo, h_otro = h[f"{J['sexo']}|{nivel}"], h[f"{otro}|{nivel}"]
                    if J["sexo"] == "mujer":
                        st.markdown(f"Un varón con tu mismo perfil y trabajo ganaría **{round((r_otro / r_yo - 1) * 100)}% "
                                    f"más** por mes. Parte de la diferencia se explica porque los varones trabajan más horas "
                                    f"pagas ({num(h_otro)} contra {num(h_yo)} por semana), pero aun por hora la brecha "
                                    "ronda el 28%.")
                    else:
                        st.markdown(f"Una mujer con tu mismo perfil y trabajo ganaría **{round((1 - r_otro / r_yo) * 100)}% "
                                    f"menos** por mes. Parte de la diferencia se explica porque las mujeres trabajan menos "
                                    f"horas pagas ({num(h_otro)} contra {num(h_yo)} por semana), pero aun por hora la brecha "
                                    "ronda el 28%.")
        if "trabajo" in J:
            boton_seguir(4, "Seguir: hijos →")
            boton_reintentar(3)
    with izq:
        grilla_100(cum_etapa(3), "personas con tu origen y tu educación llegan hasta este punto")


# ---------------------------------------------------------------- etapa 4: hijos
EDAD1 = ["Antes de los 20", "Entre los 20 y los 24", "Entre los 25 y los 29", "Entre los 30 y los 34", "A los 35 o más"]


def etapa_hijos():
    H = D["hij"]
    pp = H["pp"][f"{J['provincia']}|{J['edu']}"]
    first = H["first"][J["edu"]]
    izq, der = st.columns([2, 3], gap="large")
    with der:
        nota = (" El Censo pregunta por hijos solo a las mujeres, así que acá se usan los datos de mujeres "
                "de tu provincia con tu misma educación.") if J["sexo"] == "varon" else ""
        st.caption(f"{sexo_txt(J['sexo'], True)} de {J['provincia']} con {NIVELES[J['edu']].lower()}.{nota}")
        n = None
        r = decision("4_tiene", "¿Tenés hijos?", [("si", "Tengo hijos", 1 - pp[0]), ("no", "No tengo hijos", pp[0])])
        if r == "no":
            n = 0
        elif r == "si":
            e = decision("4_edad", "¿A qué edad tenés el primero?",
                         [(str(k), t, first[k]) for k, t in enumerate(EDAD1)])
            if e:
                m = pp[1:]
                c = decision("4_cuantos", "¿Cuántos hijos tenés en total?",
                             [("1", "Uno", m[0]), ("2", "Dos", m[1]), ("3", "Tres", m[2]),
                              ("4", "Cuatro o más", m[3] + m[4])])
                if c:
                    n = int(c)
        if n is not None:
            textos = ["Sin hijos", "Un hijo", "Dos hijos", "Tres hijos", "Cuatro hijos o más"]
            J["hijos"] = {"n": n, "texto": textos[n]}
            st.divider()
            carta(4, "Tu familia", textos[n], sello=sello_camino(4),
                  chips=[f"El primero, {EDAD1[int(RES['4_edad'][0])].lower()}"] if n > 0 else [])
            o, k = H["ocu"], min(n, 3)
            if n == 0:
                st.markdown(f"Entre las mujeres de 25 a 44 años sin hijos menores en el hogar trabaja el "
                            f"{pct(o['mujer|0'])}; con tres hijos o más, el {pct(o['mujer|3'])}. En los varones casi "
                            f"no cambia: {pct(o['varon|0'])} y {pct(o['varon|3'])}.")
            else:
                st.markdown("Quiénes trabajan entre las personas de 25 a 44 años con la misma cantidad de hijos "
                            "menores en el hogar:")
                barras([("Madres", o[f"mujer|{k}"]), ("Padres", o[f"varon|{k}"]),
                        ("Mujeres sin hijos", o["mujer|0"])],
                       resaltar="Madres" if J["sexo"] == "mujer" else "Padres")
            st.markdown("Promedio de hijos de las mujeres de 45 a 49 años, según nivel educativo:")
            barras([(NIVELES[k], H["mean"][k]) for k in NIVELES], resaltar=NIVELES[J["edu"]],
                   formato=lambda v: num(v))
            boton_seguir(5, "Seguir: deudas →")
            boton_reintentar(4)
    with izq:
        grilla_100(cum_etapa(4), "personas con tu origen y tu educación llegan hasta este punto")


# ---------------------------------------------------------------- etapa 5: deudas
EDAD_DEUDA = "26-35"


def etapa_deudas():
    zona = PROV[J["provincia"]]["region"]
    trab = J["trabajo"]["tipo"]
    nk = min(3, J["hijos"]["n"])
    dd = D["deu"]

    def eph(t):
        return dd["eph"][f"{zona}|{J['edu']}|{t}|{nk}"]

    e = eph(trab)
    izq, der = st.columns([2, 3], gap="large")
    with der:
        st.caption("En esta etapa tenés entre 26 y 35 años.")
        r = decision("5_pide", "Este año la plata no alcanza. ¿Pedís prestado?",
                     [("banco", "Pido un préstamo a un banco o financiera", e[0]),
                      ("familia", "Le pido a familiares o amigos", e[1]),
                      ("nada", "No pido prestado", e[2])])
        if r in ("familia", "nada"):
            J["deuda"] = {"texto": "Te prestó tu familia" if r == "familia" else "No pediste prestado"}
            st.divider()
            carta(5, "Tus deudas", J["deuda"]["texto"], sello=sello_camino(5))
            st.markdown("Personas con tu educación, región e hijos que le piden plata a familiares o amigos, "
                        "según su trabajo:")
            nombres = {"formal": "Trabajo en blanco", "informal": "En negro o por su cuenta", "desoc": "Sin trabajo"}
            barras([(nombres[t], eph(t)[1]) for t in ["formal", "informal", "desoc"]], resaltar=nombres[trab])
        elif r == "banco":
            c = dd["comp_prov"].get(f"{J['provincia']}|{J['sexo']}", dd["comp"][f"{J['sexo']}|{EDAD_DEUDA}"])
            a = decision("5_acr", "¿A quién terminás debiéndole?",
                         [("banco", "Solo a bancos", c[0]), ("ambos", "A bancos y también fuera de ellos", c[1]),
                          ("otro", "Solo fuera de los bancos", c[2], "tarjetas no bancarias, fintech, financieras")])
            if a:
                m = dd["mora_prov"].get(f"{J['provincia']}|{J['sexo']}|{a}", dd["mora"][f"{J['sexo']}|{EDAD_DEUDA}|{a}"])
                mo = decision("5_mora", "¿Pagás a tiempo?", [("dia", "Pago al día", 1 - m), ("mora", "Caigo en mora", m)],
                              nota=f"Mora: al menos una deuda con más de 90 días de atraso. Personas de 26 a 35 años de "
                                   f"{J['provincia']} (Central de Deudores del BCRA, {dd['fecha']}).")
                if mo:
                    J["deuda"] = {"texto": "Caíste en mora" if mo == "mora" else "Pagaste tus deudas al día"}
                    st.divider()
                    carta(5, "Tus deudas", J["deuda"]["texto"], sello=sello_camino(5),
                          lineas=[f"En todo el país, el <b>{pct(dd['total'])}</b> de las personas con deudas está en mora."])
                    st.markdown("Personas en mora según a quién le deben:")
                    nom = {"banco": "Solo a bancos", "ambos": "Bancos y otros", "otro": "Fuera de los bancos"}
                    barras([(nom[k], dd["acr"][k]) for k in nom], resaltar=nom[a])
                    st.markdown("Personas en mora según la edad:")
                    barras([(e_, v) for e_, v in dd["edad"]], resaltar="26 a 35")
        if "deuda" in J:
            boton_seguir(6, "Seguir: vejez →")
            boton_reintentar(5)
    with izq:
        mapa_deudas()


def mapa_deudas():
    """Mapa de la deuda por provincia, con varias capas para comparar."""
    dp = D["deuda_provincias"]
    fuente_bcra = ("Fuente: Central de Deudores del BCRA (agosto de 2026) cruzada con el padrón de ARCA para "
                   "obtener la provincia de cada persona.")
    capas = {
        "Mora": (dp["mora"], "Deudores en mora (%)", "Reds",
                 "Personas con al menos una deuda con más de 90 días de atraso, sobre el total de personas con "
                 "deudas de cada provincia. " + fuente_bcra),
        "Adultos con deudas": (dp["pct_adultos_endeudados"], "Adultos con deudas (%)", "Blues",
                               "Personas de 18 años o más con al menos una deuda, sobre la población adulta "
                               "proyectada por el INDEC para 2026. " + fuente_bcra +
                               " La provincia es la del domicilio fiscal, que puede no coincidir con donde vive la persona."),
        "Deuda promedio": (dp["deuda_media_millones"], "Deuda promedio por deudor (millones de $)", "Purples",
                           "Suma de las deudas de cada persona en el sistema, en pesos de agosto de 2026. " + fuente_bcra),
        "Préstamos de bancos": (dp["eph_banco"], "Hogares con préstamo de banco o financiera (%)",
                                "Blues", "En los últimos tres meses. Fuente: EPH, INDEC (2025 y 1.er trimestre de 2026)."),
        "Préstamos de familiares": (dp["eph_familia"], "Hogares que pidieron a familiares o amigos (%)",
                                    "Purples", "En los últimos tres meses. Fuente: EPH, INDEC (2025 y 1.er trimestre de 2026)."),
        "Compras en cuotas": (dp["eph_cuotas"], "Hogares que compraron en cuotas o al fiado (%)", "Oranges",
                              "Con tarjeta de crédito o libreta, en los últimos tres meses. Fuente: EPH, INDEC."),
        "Créditos hipotecarios": (dp["hipotecarios_10k"], "Hipotecarios nuevos cada 10.000 adultos",
                                  "Greens", "Otorgados en 2025. Fuente: BCRA, Informe de Inclusión Financiera (abril de 2026)."),
    }
    capa = st.segmented_control("Ver en el mapa", list(capas), default="Mora", key="capa_deuda") or "Mora"
    valores, titulo, escala, fuente = capas[capa]
    valores = {p: valores.get(p) for p in PROV}
    prov = J["provincia"]
    st.plotly_chart(mapa(valores, titulo, resaltar=prov, escala=escala, alto=540),
                    width="stretch", config={"displayModeBar": False})
    v = valores[prov]
    if v is None:
        st.markdown(f"**{prov}:** sin dato en esta fuente.")
    else:
        orden = sorted([x for x in valores.values() if x is not None], reverse=True)
        st.markdown(f"**{prov}: {num(v)}** · puesto {orden.index(v) + 1} de {len(orden)} "
                    "(1 = el valor más alto del país)")
    st.caption(fuente)


# ---------------------------------------------------------------- etapa 6: vejez
def etapa_vejez():
    lx = D["vida"]["lx"][f"{J['provincia']}|{J['sexo']}"]

    def l_at(edad):
        k = min(21, int(edad // 5))
        if k >= 21:
            return 0.0
        fr = (edad - 5 * k) / 5
        return lx[k] + (lx[min(21, k + 1)] - lx[k]) * fr

    def sortear_edad(a0, a1):
        u = random.random() * (l_at(a0) - l_at(a1))
        for a in range(a0, a1):
            d = l_at(a) - l_at(a + 1)
            if u <= d:
                return a
            u -= d
        return a1 - 1

    ret = 65 if J["sexo"] == "varon" else 60
    info = PROV[J["provincia"]]
    e0 = info["esperanza_vida_varones"] if J["sexo"] == "varon" else info["esperanza_vida_mujeres"]
    tramos = [(ret, 75), (75, 85), (85, 95), (95, 105)]
    izq, der = st.columns([2, 3], gap="large")
    with der:
        st.caption(f"Llegaste a los 35. En {J['provincia']}, la esperanza de vida al nacer de "
                   f"{'los varones' if J['sexo'] == 'varon' else 'las mujeres'} es de {num(e0)} años.")
        p_jub = l_at(ret) / l_at(35)
        r = decision("6_jub", f"¿Llegás a jubilarte a los {ret}?",
                     [("si", "Llego a jubilarme", p_jub), ("no", "Muero antes", 1 - p_jub)],
                     nota=f"Probabilidad de llegar con vida a los {ret} para {'un varón' if J['sexo'] == 'varon' else 'una mujer'} "
                          f"de {J['provincia']} que ya cumplió 35, según la tabla de vida de su provincia.")
        if r == "no" and "edad_muerte" not in J:
            J["edad_muerte"] = sortear_edad(35, ret)
        elif r == "si":
            jb = D["jubilacion"]["dist"][f"{J['sexo']}|{J['edu']}"]
            minima = f"${D['jubilacion']['minima_con_bono_2026T1']:,}".replace(",", ".")
            monto = decision("6_monto", "¿Con cuánto te jubilás?",
                             [("no", "No cobro jubilación ni pensión", jb[0]),
                              ("min", "Con la mínima", jb[1], f"unos {minima} por mes con el bono, a comienzos de 2026"),
                              ("1a2", "Entre 1 y 2 mínimas", jb[2]),
                              ("mas2", "Más de 2 mínimas", jb[3])],
                             nota=f"Personas de 65 años o más con {NIVELES[J['edu']].lower()}, según la suma de jubilaciones "
                                  "y pensiones que declaran en la EPH.")
            if monto:
                J["jubilacion"] = {"no": "Sin jubilación ni pensión", "min": "Jubilación mínima",
                                   "1a2": "Entre 1 y 2 mínimas", "mas2": "Más de 2 mínimas"}[monto]
                opts = [(str(i), f"Entre los {a} y los {b - 1}" if b < 105 else "95 años o más",
                         (l_at(a) - l_at(b)) / l_at(ret)) for i, (a, b) in enumerate(tramos)]
                t = decision("6_edad", "¿Hasta qué edad vivís?", opts)
                if t and "edad_muerte" not in J:
                    a, b = tramos[int(t)]
                    J["edad_muerte"] = sortear_edad(a, b)
        if "edad_muerte" in J:
            st.divider()
            if RES.get("6_jub", ("",))[0] == "no":
                linea = (f"Te tocó estar en el <b>{pct(1 - p_jub)}</b> que muere antes de jubilarse: de cada 100 personas "
                         f"como vos que llegan a los 35, {round((1 - p_jub) * 100)} no llegan a los {ret}.")
            else:
                linea = f"Llegaste a jubilarte, como el <b>{pct(p_jub)}</b> de las personas como vos."
            items = [("Naciste", f"{sexo_txt(J['sexo'], True)} en {J['provincia']}, clase {J['clase']}"),
                     ("Estudiaste", NIVELES[J["edu"]]), ("Trabajaste", J["trabajo"]["texto"]),
                     ("Familia", J["hijos"]["texto"]), ("Deudas", J["deuda"]["texto"]),
                     ("Vejez", J.get("jubilacion", "No llegaste a jubilarte"))]
            grid = '<div class="vida-grid">' + "".join(f"<div><small>{a}</small><span>{b}</span></div>" for a, b in items) + "</div>"
            carta(6, "Fin del juego · Tu vida en Argentina", f"Viviste {J['edad_muerte']} años",
                  lineas=[linea + f" La edad exacta sale de la tabla de vida de {J['provincia']}.", grid])
            campo = "esperanza_vida_varones" if J["sexo"] == "varon" else "esperanza_vida_mujeres"
            orden = sorted(PROV.items(), key=lambda x: -x[1][campo])
            filas = [(orden[0][0], orden[0][1][campo])]
            if J["provincia"] not in (orden[0][0], orden[-1][0]):
                filas.append((J["provincia"], e0))
            filas.append((orden[-1][0], orden[-1][1][campo]))
            st.markdown(f"Esperanza de vida al nacer de {'los varones' if J['sexo'] == 'varon' else 'las mujeres'}: "
                        "la provincia más alta, la tuya y la más baja.")
            barras(filas, resaltar=J["provincia"], formato=lambda v: num(v))
            otro = info["esperanza_vida_mujeres"] if J["sexo"] == "varon" else info["esperanza_vida_varones"]
            st.markdown(f"Si hubieras nacido {'mujer' if J['sexo'] == 'varon' else 'varón'} en {J['provincia']}, "
                        f"tu esperanza de vida sería de {num(otro)} años: {num(abs(otro - e0))} años "
                        f"{'más' if otro > e0 else 'menos'}.")
            if st.button("🎲 Volver a nacer", type="primary"):
                nuevo_juego()
                st.rerun()
            boton_reintentar(6)
    with izq:
        grilla_100(cum_etapa(6), "personas de tu provincia y tu sexo que llegan a los 35 llegan hasta acá")


# ---------------------------------------------------------------- navegación
[etapa_nacer, etapa_estudiar, etapa_trabajar, etapa_hijos, etapa_deudas, etapa_vejez][etapa - 1]()

with st.expander("Fuentes y metodología"):
    st.markdown("""
- **Nacimientos y madres adolescentes:** DEIS, estadísticas vitales 2024.
- **Clase del hogar, educación, trabajo, préstamos:** INDEC, Encuesta Permanente de Hogares (2025 y 1.er trimestre de 2026).
  Probabilidades estimadas con modelos logísticos por región, clase, nivel educativo y sexo.
- **Hijos:** INDEC, Censo 2022 (fecundidad, cuadros 1, 2, 6 y 18), con ajuste proporcional iterativo.
- **Deudas y mora:** BCRA, Central de Deudores de agosto de 2026, cruzada con el padrón de ARCA para obtener provincia, sexo y edad (procesada de forma anónima en una computadora local; solo se usaron totales agregados).
- **Jubilaciones:** EPH, personas de 65 años o más; suma de jubilaciones y pensiones comparada con la mínima más el bono de cada trimestre (ANSES).
- **Esperanza de vida y tablas de vida:** INDEC, proyecciones de población 2022-2040 (modelo logito de Brass).
- **Mapa:** Natural Earth.
""")

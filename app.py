import streamlit as st
import streamlit.components.v1 as components
import datetime
import base64
import os

import pandas as pd
import numpy as np
import math
import matplotlib

matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.lines as mlines
from matplotlib.ticker import FuncFormatter, MultipleLocator

import almanaque
import calculos
import graficas
import memoria

st.set_page_config(page_title="Navegación Astronómica", page_icon="escudo.png", layout="wide")
st.markdown("""
    <style>
    @media print {
        /* 1. Ocultar interfaz de la web */
        [data-testid="stSidebar"], header, button, .stToolbar { display: none !important; }
        
        /* 2. FORZAR QUE NUNCA SE CORTE EL TEXTO (Anti-Guillotina) */
        .stApp, .main, div, [data-testid="column"], [data-testid="stVerticalBlock"] { 
            background: white !important; 
            color: black !important; 
            overflow: visible !important; 
            height: auto !important; 
            min-height: 0 !important;
        }
        
        /* Aprovechar el folio A4 al máximo subiendo el contenido */
        .stApp { margin-top: -80px !important; }
        .block-container { padding: 0rem 1rem !important; }
        
        /* 3. Textos tamaño libro (10pt) */
        p, li, span { 
            font-size: 10pt !important; 
            line-height: 1.2 !important; 
            margin-bottom: 2px !important; 
        }
        
        /* 4. Títulos súper compactos */
        h1, h2, h3, h4 { font-family: "Georgia", "Times New Roman", serif !important; page-break-after: avoid !important; }
        h1 { font-size: 12pt !important; margin: 2px 0 !important; }
        h2 { font-size: 11pt !important; margin: 2px 0 !important; }
        h3 { font-size: 10.5pt !important; margin: 4px 0 2px 0 !important; text-decoration: underline; }
        h4 { font-size: 10pt !important; margin: 2px 0 0 0 !important; font-weight: bold; }
        
        /* 5. Matemáticas LaTeX Súper Apretadas */
        .katex { font-size: 9.5pt !important; }
        .katex-display { margin: 1px 0 !important; padding: 0 !important; }
        
        /* 6. Líneas separadoras más finas */
        hr { margin: 4px 0 !important; border-bottom: 1px solid #ddd !important; }
        
        /* 7. Ajuste fino de las columnas */
        [data-testid="column"] { padding: 0 10px !important; }
    }
    </style>
""", unsafe_allow_html=True)

if "modo_navegacion" not in st.session_state:
    st.session_state["modo_navegacion"] = None

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
img_file = 'sol.webp'
base64_img = ""
if os.path.exists(img_file):
    base64_img = get_base64_of_bin_file(img_file)

st.markdown(f"""
<style>
    /* 1. REDUCIR ANCHO DE LA BARRA LATERAL */
    [data-testid="stSidebar"] {{
        min-width: 200px !important;
        max-width: 250px !important;
    }}

    /* BANNER TIPO HERO */
    .hero-container {{
        position: relative;
        width: 100%;
        height: 220px;
        background-image: url("data:image/webp;base64,{base64_img}");
        background-size: cover;
        background-position: center;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    .hero-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.5)); 
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}

    .hero-title {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        margin: 0;
        text-align: center;
    }}
    
    .hero-subtitle {{
        font-family: 'Georgia', serif; 
        color: #f0f0f0;
        font-size: 1.4rem;
        font-weight: 300;
        margin-top: 10px;
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.9);
        text-align: center;
        border-top: 1px solid rgba(255,255,255,0.5);
        padding-top: 10px;
        width: 60%;
    }}

    /* Estilos generales */
    .stNumberInput input {{ text-align: center; font-size: 0.9em; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.1rem; }}
    .unit-header {{ font-size: 0.8em; color: #555; text-align: center; font-weight: bold; margin-bottom: 5px; }}
    
    /* CAJA IMPORTANTE (VERDE) */
    .info-card-green {{
        background-color: #d1e7dd;
        border: 1px solid #badbcc;
        color: #0f5132;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-family: sans-serif;
        margin-bottom: 15px;
    }}
    
    /* CAJA SECUNDARIA (GRIS FORMAL) */
    .info-card-secondary {{
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        color: #495057;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-family: sans-serif;
        margin-bottom: 15px;
        font-size: 0.95rem; 
    }}

    .card-label {{ font-size: 0.9rem; font-weight: bold; display: block; margin-bottom: 4px; opacity: 0.8; }}
    .card-value {{ font-size: 1.2rem; font-weight: bold; }}
    .card-value-small {{ font-size: 1.1rem; font-weight: bold; }} 
    
    /* Estilo para las imágenes del menú lateral */
    .menu-img {{
        width: 100%;
        border-radius: 8px 8px 0 0;
        margin-bottom: -5px; /* Pegado al botón */
        border: 1px solid #ccc;
    }}
    .menu-img-estrellas {{
        filter: hue-rotate(220deg) brightness(0.8);
    }}
</style>
""", unsafe_allow_html=True)

def dms_a_decimal(grados, minutos, segundos, cardinal):
    """Convierte Grados, Minutos, Segundos y Letra a formato decimal para el PDF."""
    decimal = float(grados) + (float(minutos) / 60.0) + (float(segundos) / 3600.0)
    if cardinal in ['S', 'W']:
        decimal = -decimal
    return decimal

def decimal_a_dms_cardinal(valor, es_latitud=True):
    signo = 1 if valor >= 0 else -1
    valor_abs = abs(valor)
    g = int(valor_abs)
    rest_m = (valor_abs - g) * 60
    m = int(rest_m)
    s = (rest_m - m) * 60
    if es_latitud: cardinal = "N" if signo > 0 else "S"
    else: cardinal = "E" if signo > 0 else "W"
    return f"{g}º {m}' {s:.1f}'' {cardinal}"

def decimal_a_dms_simple(valor):
    valor_abs = abs(valor)
    g = int(valor_abs)
    rest_m = (valor_abs - g) * 60
    m = int(rest_m)
    s = (rest_m - m) * 60
    return f"{g}º {m}' {s:.1f}''"

def fmt_gms(valor_decimal):
    g = int(valor_decimal)
    m = abs((valor_decimal - g) * 60)
    return f"{g}^{{\\circ}} {m:.1f}'"

def fmt_gm(val):
    """Formato Grados y Minutos para LaTeX (usado en Meridiana)."""
    d = int(val)
    m = (val - d) * 60.0
    return f"{d}^{{\\circ}} {abs(m):.1f}'"

def format_seconds_to_hhmm(x, pos):
    h = int(x // 3600)
    m = int((x % 3600) // 60)
    return f"{h:02}:{m:02}"
def resetear_ejercicio():
    """Borra todas las claves de ejercicio del session_state"""
    claves_a_mantener = {
        "modo_navegacion", 
        "tipo_calculo_sol", 
        "herramienta_estrellas",
        "menu_abierto", 
        "mensaje_flash"
    }
    for k in list(st.session_state.keys()):
        if k not in claves_a_mantener:
            del st.session_state[k]

def dibujar_mono_astros(estrellas_visibles, modo_etiqueta="Nombres"):
    import matplotlib.pyplot as plt
    import numpy as np
    import math
    
    fig, ax = plt.subplots(figsize=(7.5, 7.5), subplot_kw={'projection': 'polar'})

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_xticks(np.radians([0, 45, 90, 135, 180, 225, 270, 315]))
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], fontweight='bold', color='#333333')

    ax.set_ylim(0, 90)
    ax.set_yticks([0, 30, 60, 90])
    ax.set_yticklabels(['90º', '60º', '30º', '0º'], color='grey', fontsize=8)

    planetas_nombres = ['Venus', 'Marte', 'Jupiter', 'Saturno']
    cajas_ocupadas = []

    if estrellas_visibles:
        for astro in estrellas_visibles:
            az_rad = np.radians(astro['azimut'])
            r = 90 - astro['altura']
            x = r * math.sin(az_rad)
            y = r * math.cos(az_rad)
            cajas_ocupadas.append((x - 2.5, x + 2.5, y - 2.5, y + 2.5))

        def ruta_libre(x_ast, y_ast, x_txt, y_txt, w_t, h_t):
            n_xmin, n_xmax = x_txt - w_t/2, x_txt + w_t/2
            n_ymin, n_ymax = y_txt - h_t/2, y_txt + h_t/2

            for (xmin, xmax, ymin, ymax) in cajas_ocupadas:
                if not (n_xmax <= xmin or n_xmin >= xmax or n_ymax <= ymin or n_ymin >= ymax):
                    return False
                    
            dist = math.sqrt((x_txt - x_ast)**2 + (y_txt - y_ast)**2)
            pasos = max(2, int(dist / 1.0))
            
            for i in range(1, pasos):
                px = x_ast + (x_txt - x_ast) * (i / pasos)
                py = y_ast + (y_txt - y_ast) * (i / pasos)
                
                if math.sqrt((px - x_ast)**2 + (py - y_ast)**2) < 3.0:
                    continue
                    
                for (xmin, xmax, ymin, ymax) in cajas_ocupadas:
                    if xmin < px < xmax and ymin < py < ymax:
                        return False
            return True

        for astro in estrellas_visibles:
            az_rad = np.radians(astro['azimut'])
            r = 90 - astro['altura']
            nombre_real = astro['nombre']
            es_planeta = nombre_real in planetas_nombres
            
            if modo_etiqueta == "Números":
                texto_mostrar = str(astro.get('numero', ''))
                peso_fuente = 'bold'
            else:
                texto_mostrar = nombre_real
                peso_fuente = 'normal'

            if es_planeta:
                ax.plot(az_rad, r, marker='o', markersize=7, color='#E67E22', markeredgecolor='#A04000', zorder=4)
            else:
                ax.plot(az_rad, r, marker='*', markersize=9, color='#FFC300', markeredgecolor='#D35400', zorder=3)

            x_astro = r * math.sin(az_rad)
            y_astro = r * math.cos(az_rad)

            w_txt = max(3.5, len(texto_mostrar) * 1.6)
            h_txt = 3.5

            hueco_encontrado = False
            x_txt_final, y_txt_final = x_astro, y_astro
            
            angulos_deg = np.arange(0, 360, 15) 
            
            for radio_offset in np.arange(3.5, 40.0, 1.5):
                for ang_deg in angulos_deg:
                    ang_rad = math.radians(ang_deg)
                    x_cand = x_astro + radio_offset * math.cos(ang_rad)
                    y_cand = y_astro + radio_offset * math.sin(ang_rad)
                    
                    if ruta_libre(x_astro, y_astro, x_cand, y_cand, w_txt, h_txt):
                        hueco_encontrado = True
                        x_txt_final = x_cand
                        y_txt_final = y_cand
                        break
                if hueco_encontrado:
                    break

            if not hueco_encontrado:
                x_txt_final, y_txt_final = x_astro + 20, y_astro

            cajas_ocupadas.append((x_txt_final - w_txt/2, x_txt_final + w_txt/2, 
                                   y_txt_final - h_txt/2, y_txt_final + h_txt/2))
                                   
            dist = math.sqrt((x_txt_final - x_astro)**2 + (y_txt_final - y_astro)**2)
            pasos = max(2, int(dist / 1.5))
            for i in range(1, pasos):
                px = x_astro + (x_txt_final - x_astro) * (i / pasos)
                py = y_astro + (y_txt_final - y_astro) * (i / pasos)
                cajas_ocupadas.append((px - 0.5, px + 0.5, py - 0.5, py + 0.5))

            r_txt = math.sqrt(x_txt_final**2 + y_txt_final**2)
            az_rad_txt = math.atan2(x_txt_final, y_txt_final)
            if az_rad_txt < 0:
                az_rad_txt += 2 * math.pi

            ax.annotate(texto_mostrar,
                        xy=(az_rad, r),
                        xytext=(az_rad_txt, r_txt),
                        xycoords='data', textcoords='data',
                        color='#1B4F72', ha='center', va='center',
                        fontsize=8, fontweight=peso_fuente, alpha=1.0, zorder=5,
                        arrowprops=dict(
                            arrowstyle="-|>", color='#2C3E50', lw=1.0, alpha=0.9,
                            shrinkA=3.0, shrinkB=3.5, mutation_scale=10,
                            connectionstyle="arc3,rad=0.0" 
                        ))

    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_facecolor('#EBF5FB')
    fig.patch.set_alpha(0.0) 

    return fig

def calcular_astros_visibles(fecha, hora, lat_decimal, lon_decimal):
    import math
    import almanaque
    
    astros_visibles = []
    hora_decimal = hora.hour + (hora.minute / 60.0) + (hora.second / 3600.0)
    
    estrellas = almanaque.obtener_lista_estrellas()
    if not estrellas or estrellas[0].startswith("⚠️"):
        estrellas = [] 
        
    planetas = ['Venus', 'Marte', 'Jupiter', 'Saturno']
    estrellas_limpias = [e for e in estrellas if e not in planetas]
    
    nombres_astros = estrellas_limpias + planetas
    
    for nombre in nombres_astros:
        if nombre in ['Venus', 'Marte', 'Jupiter', 'Saturno']:
            gha, dec = almanaque.get_datos_planeta(nombre, fecha.day, fecha.month, fecha.year, hora_decimal)
        else:
            gha, dec, _ = almanaque.get_datos_estrella_aries(nombre, fecha.day, fecha.month, fecha.year, hora_decimal)
            
        if gha is None or dec is None:
            continue
            
        lha = (gha + lon_decimal) % 360.0
        
        lat_rad = math.radians(lat_decimal)
        dec_rad = math.radians(dec)
        lha_rad = math.radians(lha)
        
        sin_hc = math.sin(lat_rad) * math.sin(dec_rad) + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(lha_rad)
        hc_rad = math.asin(sin_hc)
        hc_deg = math.degrees(hc_rad)
        
        if hc_deg > 0:
            cos_z = (math.sin(dec_rad) - math.sin(lat_rad) * math.sin(hc_rad)) / (math.cos(lat_rad) * math.cos(hc_rad))
            cos_z = max(-1.0, min(1.0, cos_z)) 
            z_rad = math.acos(cos_z)
            z_deg = math.degrees(z_rad)
            
            if 0 < lha < 180:
                zv = 360.0 - z_deg 
            else:
                zv = z_deg         
                
            astros_visibles.append({
                'nombre': nombre,
                'azimut': zv,
                'altura': hc_deg
            })
            
    astros_visibles.sort(key=lambda x: x['azimut'])
    return astros_visibles

def input_coord_dms(label, key_suffix, tipo="lat", def_g=0, def_m=0, def_s=0.0, def_card="N"):
    st.write(f"**{label}**")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.8])
    
    k_g = f"{key_suffix}_g"
    k_m = f"{key_suffix}_m"
    k_s = f"{key_suffix}_s"
    k_c = f"{key_suffix}_card"

    with c1:
        st.caption("Grados (º)")
        kwargs_g = {"key": k_g, "label_visibility": "collapsed"}
        if k_g not in st.session_state:
            kwargs_g["value"] = int(def_g)
        g = st.number_input("G", 0, 180 if tipo=="lon" else 90, **kwargs_g)

    with c2:
        st.caption("Minutos (')")
        kwargs_m = {"key": k_m, "label_visibility": "collapsed"}
        if k_m not in st.session_state:
            kwargs_m["value"] = int(def_m)
        m = st.number_input("M", 0, 59, **kwargs_m)

    with c3:
        st.caption("Segundos ('')")
        kwargs_s = {"key": k_s, "label_visibility": "collapsed"}
        if k_s not in st.session_state:
            kwargs_s["value"] = int(def_s)
        s = st.number_input("S", 0, 59, **kwargs_s)

    with c4:
        st.caption("Card")
        opciones = ["N", "S"] if tipo == "lat" else ["E", "W"]
        if k_c not in st.session_state:
            st.session_state[k_c] = def_card if def_card in opciones else opciones[0]
        card = st.selectbox("Dir", opciones, key=k_c, label_visibility="collapsed")
    
    decimal = float(g) + (float(m)/60.0) + (float(s)/3600.0)
    if card in ["S", "W"]: decimal = -decimal
    return decimal

def procesar_input_estrella(columna, id_obs, lat_est_global, lon_est_global):
    es_pdf = st.session_state.get("orden_imprimir_pdf", False)
    
    if id_obs == 1:
        sugerencia = ""
        h_def = (0, 0, 0.0); a_def = (0, 0, 0.0)
    elif id_obs == 2:
        sugerencia = ""
        h_def = (0, 0, 0.0); a_def = (0, 0, 0.0)
    else:
        sugerencia = ""
        h_def = (0, 0, 0.0); a_def = (0, 0, 0.0)

    if not es_pdf:
        with columna:
            st.subheader(f"Astro {id_obs}")
            lista = almanaque.obtener_lista_estrellas()
            nombre = st.selectbox("Astro", lista, index=0, key=f"est_n_{id_obs}")
            
            st.markdown("---")
            st.write("**Mediciones**")
            if f"est_nm_{id_obs}" not in st.session_state:
                st.session_state[f"est_nm_{id_obs}"] = 1
            n_med = st.number_input("Nº Mediciones", 1, 10, key=f"est_nm_{id_obs}")
            
            c_titulos = st.columns([1, 1])
            c_titulos[0].caption("**HORA UTC (H : M : S)**")
            c_titulos[1].caption("**ALTURA (º  '  '')**")
    else:
        nombre = st.session_state.get(f"est_n_{id_obs}", sugerencia)
        n_med = st.session_state.get(f"est_nm_{id_obs}", 3)

    raw = []
    
    for i in range(n_med):
        if not es_pdf:
            with columna:
                cols = st.columns([1, 1, 1.2, 0.2, 1, 1, 1.2])
                for key, val in [(f"eh_{id_obs}_{i}", int(h_def[0])), 
                 (f"em_{id_obs}_{i}", int(h_def[1])),
                 (f"es_{id_obs}_{i}", int(h_def[2])),
                 (f"eg_{id_obs}_{i}", int(a_def[0])),
                 (f"emi_{id_obs}_{i}", int(a_def[1])),
                 (f"esi_{id_obs}_{i}", int(a_def[2]))]:
                    if key not in st.session_state:
                        st.session_state[key] = val

                hh = cols[0].number_input(f"h{i}", 0, 23, key=f"eh_{id_obs}_{i}", label_visibility="collapsed")
                mm = cols[1].number_input(f"m{i}", 0, 59, key=f"em_{id_obs}_{i}", label_visibility="collapsed")
                ss = cols[2].number_input(f"s{i}", 0, 59, key=f"es_{id_obs}_{i}", label_visibility="collapsed")

                gg = cols[4].number_input(f"g{i}", 0, 90, key=f"eg_{id_obs}_{i}", label_visibility="collapsed")
                mmi = cols[5].number_input(f"mi{i}", 0, 59, key=f"emi_{id_obs}_{i}", label_visibility="collapsed")
                sse = cols[6].number_input(f"si{i}", 0, 59, key=f"esi_{id_obs}_{i}", label_visibility="collapsed")
        else:   
            hh = st.session_state.get(f"eh_{id_obs}_{i}", h_def[0])
            mm = st.session_state.get(f"em_{id_obs}_{i}", h_def[1])
            ss = st.session_state.get(f"es_{id_obs}_{i}", h_def[2])
            gg = st.session_state.get(f"eg_{id_obs}_{i}", a_def[0])
            mmi = st.session_state.get(f"emi_{id_obs}_{i}", a_def[1])
            sse = st.session_state.get(f"esi_{id_obs}_{i}", a_def[2])
        
        h_dec = float(hh) + float(mm)/60.0 + float(ss)/3600.0
        ai_dec = float(gg) + float(mmi)/60.0 + float(sse)/3600.0
        
        raw.append({
            'id': i, 'x': hh*3600+mm*60+ss, 'y': ai_dec, 'h_dec': h_dec,
            'hh': int(hh), 'mm': int(mm), 'ss': float(ss),
            'gg': int(gg), 'mmi': int(mmi), 'sse': float(sse)
        })
        
    df = pd.DataFrame(raw)
    
    if not df.empty:
        if not es_pdf:
            with columna:
                st.markdown("#### Depuración")
                borrar = st.multiselect("Selecciona mediciones erróneas (X):", options=df['id'], format_func=lambda x: f"Med #{x+1}", key=f"del_est_{id_obs}")
        else:
            borrar = st.session_state.get(f"del_est_{id_obs}", [])

        df_clean = df[~df['id'].isin(borrar)]
        df_borradas = df[df['id'].isin(borrar)]
        
        if df_clean.empty:
            if not es_pdf:
                with columna:
                    st.error("⚠️ Deja al menos una medición.")
            return None
        
        media_ai = df_clean['y'].mean()
        media_h = df_clean['h_dec'].mean()
        media_x_seg = df_clean['x'].mean()

        h_m = int(media_h); rest_m = (media_h - h_m) * 60
        m_m = int(rest_m); s_m = int((rest_m - m_m) * 60)
        
        try:
            media_ai_str = decimal_a_dms_simple(media_ai)
        except:
            media_ai_str = f"{media_ai:.4f}º"
        
        fig, ax = plt.subplots(figsize=(5, 2.5) if not es_pdf else (4.5, 2.2))

        def formato_grados_minutos(val, pos):
            d = int(val)
            m = int(round((abs(val) - abs(d)) * 60))
            if m == 60: 
                d += 1 if val >= 0 else -1
                m = 0
            return f"{d}º {m:02d}'"
            
        ax.yaxis.set_major_formatter(FuncFormatter(formato_grados_minutos))
        ax.scatter(df_clean['x'], df_clean['y'], c='blue', s=30, label='Válidas')
        if not df_borradas.empty:
            ax.scatter(df_borradas['x'], df_borradas['y'], c='gray', marker='x', s=30, label='Descartadas')
        
        if len(df_clean) > 1 and df_clean['x'].nunique() > 1:
            z = np.polyfit(df_clean['x'], df_clean['y'], 1)
            p = np.poly1d(z)
            ax.plot(df_clean['x'], p(df_clean['x']), "b--", alpha=0.4, label='Tendencia')
            
        if df_clean['x'].nunique() <= 1:
            ax.set_xlim(media_x_seg - 60, media_x_seg + 60)
        if df_clean['y'].nunique() <= 1:
            ax.set_ylim(media_ai - 0.2, media_ai + 0.2)
        
        ax.scatter(media_x_seg, media_ai, c='gold', edgecolors='red', s=80, zorder=10, label='Media')
        
        try:
            ax.xaxis.set_major_formatter(FuncFormatter(format_seconds_to_hhmm))
        except:
            pass
            
        ax.tick_params(axis='both', labelsize=7)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize='x-small', loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)

        if es_pdf:
            textos_observaciones = []
            for item in raw:
                estado = "Descartada" if item['id'] in borrar else "Válida"
                txt_hora = f"{item['hh']:02d}:{item['mm']:02d}:{int(item['ss']):02d}"
                txt_alt = f"{item['gg']}º {item['mmi']:02d}' {item['sse']:04.1f}''"
                textos_observaciones.append(f"- **Obs #{item['id']+1}:** {txt_hora} &nbsp;|&nbsp; {txt_alt} ({estado})")
            
            return {
                "Nombre": nombre, "LatEst": lat_est_global, "LonEst": lon_est_global, 
                "Hora": media_h, "Ai": media_ai,
                "textos_obs": textos_observaciones,
                "texto_hora_media": f"{h_m:02d}:{m_m:02d}:{s_m:02d}",
                "texto_altura_media": media_ai_str,
                "Figura": fig  
            }
        
        else:
            with columna:
                st.pyplot(fig)
                st.markdown(f"""
                <div class="info-card-green">
                    <span class="card-label">MEDIAS CALCULADAS (UTC | ALTURA)</span>
                    <span class="card-value">{h_m:02}:{m_m:02}:{s_m:02} &nbsp;&nbsp;|&nbsp;&nbsp; {media_ai_str}</span>
                </div>
                """, unsafe_allow_html=True)
                
            return {"Nombre": nombre, "LatEst": lat_est_global, "LonEst": lon_est_global, "Hora": media_h, "Ai": media_ai}
    
    return None

def procesar_observacion(columna, num_obs_id, nombre_obs):
    es_pdf = st.session_state.get("orden_imprimir_pdf", False)
    with columna:
        st.header(f"{nombre_obs}")
        st.markdown("---")

        st.subheader("1. Situación de Estima")
        if es_pdf:
            lat_est = st.session_state.get(f"pdf_lat_{num_obs_id}", 40.0)
            lon_est = st.session_state.get(f"pdf_lon_{num_obs_id}", 0.0)
            
            def dec_to_dms(val, es_lat):
                letra = "N" if es_lat and val >= 0 else "S" if es_lat else "E" if val >= 0 else "W"
                v = abs(val)
                g = int(v)
                m = int((v - g) * 60)
                s = int(round((v - g - m/60.0) * 3600))
                return f"{g}º {m}' {s:02d}'' {letra}"

            st.write(f"- **Latitud Estimada:** {dec_to_dms(lat_est, True)}")
            st.write(f"- **Longitud Estimada:** {dec_to_dms(lon_est, False)}")
        else:
            lat_est = input_coord_dms("Latitud Estimada", f"lat_{num_obs_id}", "lat")
            st.write("") 
            lon_est = input_coord_dms("Longitud Estimada", f"lon_{num_obs_id}", "lon")

            st.session_state[f"pdf_lat_{num_obs_id}"] = lat_est
            st.session_state[f"pdf_lon_{num_obs_id}"] = lon_est
        st.divider()

        st.subheader("2. Condiciones de Observación")
        if es_pdf:
            f_obs = st.session_state.get(f"f_{num_obs_id}", datetime.date.today())
            eo = st.session_state.get(f"eo_{num_obs_id}", 0.0)
            ei = st.session_state.get(f"ei_{num_obs_id}", 0.0)
            st.write(f"**Fecha:** {f_obs.strftime('%d/%m/%Y')}")
            st.write(f"**Elevación Observador:** {eo} m &nbsp;&nbsp;|&nbsp;&nbsp; **Error Índice:** {ei}'")
            fecha_obs = f_obs
        else:
            key_fecha = f"f_{num_obs_id}"
            if key_fecha not in st.session_state:
                st.session_state[key_fecha] = datetime.date.today()

            fecha_obs = st.date_input("**Fecha de Observación**", format="DD/MM/YYYY", key=key_fecha)
            c_eo, c_ei = st.columns(2)
            with c_eo:
                st.write("**Elevación del Observador (m)**")
                key_eo = f"eo_{num_obs_id}"
                if key_eo not in st.session_state:
                    st.session_state[key_eo] = 0.0
                eo = st.number_input("Elev", step=0.1, key=key_eo, label_visibility="collapsed")
            with c_ei:
                st.write("**Error Índice (')**")
                key_ei = f"ei_{num_obs_id}"
                if key_ei not in st.session_state:
                    st.session_state[key_ei] = 0.0
                ei = st.number_input("Err", step=0.1, key=key_ei, label_visibility="collapsed")

        st.divider()

        st.subheader("3. Registro de Alturas")
        raw_data = []
        if es_pdf:
            n_med = st.session_state.get(f"n_{num_obs_id}", 3)
            borradas = st.session_state.get(f"del_{num_obs_id}", [])
        else:
            key_n = f"n_{num_obs_id}"
            if key_n not in st.session_state:
                st.session_state[key_n] = 3
            n_med = st.number_input(f"Nº Mediciones", 1, 5, key=key_n)
        if not es_pdf:
            c_h_head, c_a_head = st.columns([1, 1], gap="medium")
            c_h_head.markdown("<div class='unit-header'>Hora UTC<br>( h ) : ( m ) : ( s )</div>", unsafe_allow_html=True)
            c_a_head.markdown("<div class='unit-header'>Altura Instrumental<br>( º ) : ( ' ) : ( '' )</div>", unsafe_allow_html=True)

        textos_obs_pdf = []
        for i in range(n_med):
            if es_pdf:
                    hh = st.session_state.get(f"h_{num_obs_id}_{i}", 10)
                    mm = st.session_state.get(f"m_{num_obs_id}_{i}", 0)
                    ss = st.session_state.get(f"s_{num_obs_id}_{i}", 0.0)
                    gg = st.session_state.get(f"g_{num_obs_id}_{i}", 25)
                    mmi = st.session_state.get(f"mi_{num_obs_id}_{i}", 0)
                    sse = st.session_state.get(f"si_{num_obs_id}_{i}", 0.0)
                    
                    estado = "(Descartada)" if i in borradas else "(Válida)"
                    textos_obs_pdf.append(f"- **Obs #{i+1}:** {int(hh):02d}:{int(mm):02d}:{int(ss):02d} &nbsp;|&nbsp; {int(gg)}º {int(mmi):02d}' {int(sse):02d}'' {estado}")
            else:
                with st.container():
                    c_hora, c_alt = st.columns([1, 1], gap="medium")
                    
                    with c_hora:
                        ch, cm, cs = st.columns(3)
                        hh = ch.number_input("H", 0, 23, 0, key=f"h_{num_obs_id}_{i}", label_visibility="collapsed")
                        mm = cm.number_input("M", 0, 59, 0, key=f"m_{num_obs_id}_{i}", label_visibility="collapsed")
                        ss = cs.number_input("S", 0, 59, 0, key=f"s_{num_obs_id}_{i}", label_visibility="collapsed")

                    with c_alt:
                        cg, cmi, cse = st.columns(3)
                        gg = cg.number_input("G", 0, 90, 0, key=f"g_{num_obs_id}_{i}", label_visibility="collapsed")
                        mmi = cmi.number_input("M", 0, 59, 0, key=f"mi_{num_obs_id}_{i}", label_visibility="collapsed")
                        sse = cse.number_input("S", 0, 59, 0, key=f"si_{num_obs_id}_{i}", label_visibility="collapsed")
                
            h_dec = float(hh) + float(mm)/60.0 + float(ss)/3600.0
            ai_dec = float(gg) + float(mmi)/60.0 + float(sse)/3600.0
            raw_data.append({"id": i, "x": hh*3600+mm*60+ss, "y": ai_dec, "h_dec": h_dec})
        
        if es_pdf:
            st.markdown("\n".join(textos_obs_pdf))

        df = pd.DataFrame(raw_data)

        if not es_pdf:
            st.markdown("#### Depuración")
            borrar = st.multiselect("Selecciona mediciones erróneas (X):", options=df['id'], format_func=lambda x: f"Obs #{x+1}", key=f"del_{num_obs_id}")
        else:
            borrar = borradas

        df_clean = df[~df['id'].isin(borrar)]
        df_borradas = df[df['id'].isin(borrar)]
        
        if df_clean.empty: st.error("⚠️ Debes dejar al menos una medición válida."); return None

        media_ai = df_clean['y'].mean()
        media_h_dec = df_clean['h_dec'].mean()
        media_x_segundos = df_clean['x'].mean()

        if not es_pdf:
            fig, ax = plt.subplots(figsize=(5, 3))
            def formato_grados_minutos(val, pos):
                d = int(val)
                m = int(round((abs(val) - abs(d)) * 60))
                if m == 60: 
                    d += 1 if val >= 0 else -1
                    m = 0
                return f"{d}º {m:02d}'"
            ax.yaxis.set_major_formatter(FuncFormatter(formato_grados_minutos))
            ax.scatter(df_clean['x'], df_clean['y'], c='blue', s=30, zorder=5)
            for idx, row in df_clean.iterrows():
                ax.text(row['x'], row['y'], f"{int(row['id'])+1}", fontsize=8, ha='center', va='bottom', color='black', fontweight='bold')
            if not df_borradas.empty: ax.scatter(df_borradas['x'], df_borradas['y'], c='gray', marker='x', s=30, zorder=5)
            if len(df_clean) > 1 and df_clean['x'].nunique() > 1:
                try:
                    z = np.polyfit(df_clean['x'], df_clean['y'], 1)
                    p = np.poly1d(z)
                    ax.plot(df_clean['x'], p(df_clean['x']), "b--", alpha=0.4)
                except np.linalg.LinAlgError:
                    pass
                
            ax.scatter(media_x_segundos, media_ai, c='gold', edgecolors='orangered', linewidth=2, marker='o', s=100, zorder=10)
            ax.set_ylabel("Altura (º)", fontsize=8)
            ax.set_xlabel("Hora UTC", fontsize=8)
            ax.xaxis.set_major_formatter(FuncFormatter(format_seconds_to_hhmm))
            ax.tick_params(axis='both', which='major', labelsize=7)
            ax.grid(True, alpha=0.2, linestyle='--')
            
            legend_elements = [
                mlines.Line2D([], [], color='blue', marker='o', linestyle='None', markersize=6, label='Válidas'),
                mlines.Line2D([], [], color='gray', marker='x', linestyle='None', markersize=6, label='Descartadas'),
                mlines.Line2D([], [], color='blue', linestyle='--', linewidth=1, label='Tendencia'),
                mlines.Line2D([], [], color='gold', marker='o', linestyle='None', markeredgecolor='orangered', markersize=8, label='Media')
            ]
            ax.legend(handles=legend_elements, fontsize='x-small', loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=4, frameon=False)
            st.pyplot(fig)
            
        h_m = int(media_h_dec); rest_m = (media_h_dec - h_m) * 60
        m_m = int(rest_m); s_m = int((rest_m - m_m) * 60)
        media_ai_str = decimal_a_dms_simple(media_ai)
        
        if es_pdf:
            st.markdown(f"**MEDIAS CALCULADAS:** {h_m:02}:{m_m:02}:{s_m:02} &nbsp;&nbsp;|&nbsp;&nbsp; {media_ai_str}")
        else:
            st.markdown(f"""
            <div class="info-card-green">
                <span class="card-label">MEDIAS CALCULADAS (UTC | ALTURA)</span>
                <span class="card-value">{h_m:02}:{m_m:02}:{s_m:02} &nbsp;&nbsp;|&nbsp;&nbsp; {media_ai_str}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("4. Desarrollo de Cálculos")
        gha, dec = almanaque.get_datos_sol(fecha_obs.day, fecha_obs.month, fecha_obs.year, media_h_dec)
        correcciones = calculos.calcular_altura_verdadera(media_ai, eo, ei, fecha_obs.month, fecha_obs.day, fecha_obs.year)

        st.markdown("**A) Datos del Almanaque**")
        txt_gha = fmt_gms(gha)
        txt_dec = fmt_gms(dec)
        st.latex(rf'\mathbf{{hG_{{Sol}}}} = {txt_gha} \quad | \quad \boldsymbol{{\delta}} = {txt_dec}')

        doy = fecha_obs.timetuple().tm_yday
        num_pag = doy + 9

        if not es_pdf:
            with st.expander("Definiciones y fuentes"):
                st.markdown(f"""
            * **$hG_{{Sol}}$(Ángulo Horario del Sol)**: Longitud entre el Meridiano de Greenwich y el meridiano del Sol.
                * **$\\delta$ (Declinación):** Ángulo desde el ecuador hasta la proyección del Sol en la Tierra (Latitud del Sol).
                    * *Fuente:* Páginas Diarias (Pág. {num_pag} Almanaque Náutico)
                """)
            
        st.markdown("<br>**B) Correcciones de Altura**", unsafe_allow_html=True)
        txt_ai = fmt_gms(media_ai); txt_ao = fmt_gms(correcciones['AltObservada'])
        txt_ha = fmt_gms(correcciones['AltAparente']); txt_hv = fmt_gms(correcciones['AltVerdadera'])
        txt_ei = f"{ei:+.1f}'"; txt_dep = f"{correcciones['CorrSolA_min']:+.1f}'"
        txt_b1 = f"{correcciones['CorrSolB1_min']:+.1f}'"; txt_b2 = f"{correcciones['CorrSolB2_min']:+.1f}'"

        st.latex(rf'''\mathbf{{h_i}} = \mathbf{{{txt_ai}}}''')
        st.latex(rf'''\mathbf{{h_o}} = h_i + e_i = {txt_ai} + ({txt_ei}) = \mathbf{{{txt_ao}}}''')
        st.latex(rf'''\mathbf{{h_a}} = h_o + d = {txt_ao} + ({txt_dep}) = \mathbf{{{txt_ha}}}''')
        if es_pdf:
            st.latex(rf'''\mathbf{{h_v}} = h_a + b_1 + b_2 = {txt_ha} + ({txt_b1}) + ({txt_b2})''')
            st.latex(rf'''\mathbf{{h_v = {txt_hv}}}''')
        else:
            st.latex(rf'''\mathbf{{h_v}} = h_a + b_1 + b_2 = {txt_ha} + ({txt_b1}) + ({txt_b2}) = \mathbf{{{txt_hv}}}''')

        if not es_pdf:
            with st.expander("Definiciones y fuentes"):
                st.markdown(r"""
                * **$h_i$ (Altura Instrumental):** Lectura directa del sextante.
                * **$h_o$ (Altura Observada):** Corregida por error instrumental ($h_i + e_i$).
                * **$h_a$ (Altura Aparente):** Corregida por la altura del ojo ($h_o + d$).
                * **$h_v$ (Altura Verdadera):** Altura final corregida.
                * **$e_i$ (Error de Índice):** Error propio del sextante.
                * **$d$ (Depresión del Horizonte):** Corrección por elevación del observador.
                    * *Fuente:* Tabla A (Pág. 387 Almanaque Náutico).
                    * *Fórmula:* $d = -1.7757 \cdot \sqrt{\text{Elevación}}$
                * **$b_1$ (Corrección principal Sol):** Corrige los efectos de semidiámetro, refracción y paralaje.
                    * *Fuente:* Tabla B (Pág. 387 Almanaque Náutico).
                * **$b_2$ (Corrección Adicional Sol):** Ajuste fino según la fecha.
                    * *Fuente:* Tabla B (Pág. 387 Almanaque Náutico).
                """)

        
        
        st.markdown("<br>**C) Resolución Triángulo Posición**", unsafe_allow_html=True)
        tri = calculos.resolver_triangulo_posicion(lat_est, lon_est, gha, dec)
        hc = tri['AltSolEst']; z = tri['Azimut']
        det = (correcciones['AltVerdadera'] - hc) * 60.0
        val_lat = f"{lat_est:.2f}"; val_dec = f"{dec:.2f}"
        val_P   = f"{tri['AngPol']:.2f}"; val_hc  = f"{hc:.2f}"
        val_lon = f"{lon_est:.2f}"; val_gha = f"{gha:.2f}"
        if es_pdf:
            st.write("")
        st.caption("Cálculo del Ángulo en el Polo:")
        lha_calc = (gha + lon_est) % 360.0
        st.latex(rf"hG_{{Sol}} = {val_gha}^\circ")
        st.latex(r"hL = (hG_{{Sol}} + \lambda)")
        st.latex(rf"\mathbf{{hL}} = ({val_gha}^\circ + ({val_lon}^\circ)) = {lha_calc:.2f}^\circ")
        if lha_calc > 180:
            st.markdown("El Sol está al **ESTE** del observador:")
            st.latex(r"P = hL - 360^\circ")
            st.latex(rf"\mathbf{{P}} = {lha_calc:.2f}^\circ - 360^\circ = \mathbf{{{tri['AngPol']:.2f}^\circ}}")
        else:
            st.markdown("El Sol está al **OESTE** del observador:")
            st.latex(r"P = hL")
            st.latex(rf"\mathbf{{P = {lha_calc:.2f}^\circ}}")

        st.markdown("---")
        st.caption("Cálculo de Altura Calculada:")
        st.latex(r"\sin(h_c) = \sin(\varphi)\sin(\delta) + \cos(\varphi)\cos(\delta)\cos(P)")
        st.latex(rf"\sin(h_c) = \sin({val_lat}^\circ)\sin({val_dec}^\circ) + \cos({val_lat}^\circ)\cos({val_dec}^\circ)\cos({val_P}^\circ)")
        txt_hc_gms = fmt_gms(hc)
        st.latex(rf"\mathbf{{h_c = {txt_hc_gms}}} \quad ({val_hc}^\circ)")

        st.markdown("---")
        st.caption("Cálculo de Azimut:")
        z_intermedio = tri.get('AziAst_Base', tri['Azimut'])
        z_final = tri['Azimut']
        st.latex(r"\cos(Z) = \frac{\sin(\delta) - \sin(\varphi)\sin(h_c)}{\cos(\varphi)\cos(h_c)}")
        st.latex(rf"\cos(Z) = \frac{{\sin({val_dec}^\circ) - \sin({val_lat}^\circ)\sin({val_hc}^\circ)}}{{\cos({val_lat}^\circ)\cos({val_hc}^\circ)}}")
        st.latex(rf"Z = {z_intermedio:.1f}^\circ")
        
        if abs(z_final - z_intermedio) < 0.1:
            st.latex(r"\text{Sol al Este del observador}")
            st.latex(rf"\mathbf{{Z_v = {z_final:.1f}^\circ}}")
        else:
            st.latex(r"\text{Sol al Oeste del observador}")
            st.latex(rf"\mathbf{{Z_v = 360^\circ - {z_intermedio:.1f}^\circ = {z_final:.1f}^\circ}}")

        if not es_pdf:
            with st.expander("Definiciones y fuentes"):
                st.markdown(f"""
                * **$\\varphi$ (Latitud Estimada):** Coordenada vertical de nuestra posición supuesta.
                * **$\\lambda$ (Longitud Estimada):** Coordenada horizontal de nuestra posición supuesta.
                * **$\\delta$ (Declinación):** Ángulo desde el ecuador hasta la proyección del Sol en la Tierra (Latitud del Sol).
                    * *Fuente:* Páginas Diarias (Pág. {num_pag} Almanaque Náutico).
                * **$hL$ (Ángulo Horario Local):** Ángulo medido hacia el Oeste desde nuestro meridiano hasta el meridiano del Sol ($hG + \lambda$).
                * **$P$ (Ángulo en el Polo):** Ángulo menor de 180º formado en el Polo entre tu meridiano y el meridiano del Sol (derivado de $hL$).
                * **$h_c$ (Altura Calculada):** La altura teórica exacta que tendría el Sol si estuviéramos en la situación de estima.
                * **$Z$ (Azimut):** La demora a la que se encuentra el Sol desde nuestra posición.
                """)
        
        st.markdown("<br>**D) Resultados Finales**", unsafe_allow_html=True)
        txt_res = f"{det:+.2f}'"
        txt_hv = fmt_gms(correcciones['AltVerdadera'])
        st.latex(rf"\Delta h = h_v - h_c = {txt_hv} - {txt_hc_gms} = \mathbf{{{txt_res}}}")
        if es_pdf:
            st.markdown(f"<div style='padding-bottom: 15px;'</strong> &nbsp;&nbsp; Determinante: <strong>{det:+.2f}'</strong> &nbsp;&nbsp;|&nbsp;&nbsp; Azimut: <strong>{tri['Azimut']:.1f}º</strong></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="info-card-green">
                <span class="card-label">RESULTADOS (Determinante | Azimut)</span>
                <span class="card-value">{det:+.2f}' &nbsp;&nbsp;|&nbsp;&nbsp; {tri['Azimut']:.1f}º</span>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Ver Triángulo de Posición 3D (Esfera)", expanded=False):
                try:
                    fig_tri = graficas.dibujar_triangulo_posicion_3d(
                        lat_est, lon_est, dec, gha, "Sol", None, None
                    )
                    st.plotly_chart(fig_tri, use_container_width=True, key=f"tri_3d_sol_{num_obs_id}")
                except Exception as e:
                    st.error(f"No se pudo generar el gráfico 3D: {e}")

        return {"LatEst": lat_est, "LonEst": lon_est, "Azimut": tri['Azimut'], "Determinante": det}

with st.sidebar:
    st.markdown("## MENÚ PRINCIPAL")
    
    st.markdown(f'<img src="data:image/webp;base64,{base64_img}" class="menu-img"/>', unsafe_allow_html=True)

    if st.button("**SOL**", use_container_width=True):
        if st.session_state.get("menu_abierto") == "sol":
            st.session_state["menu_abierto"] = "ninguno" 
        else:
            st.session_state["menu_abierto"] = "sol"    
        st.rerun() 

    if st.session_state.get("menu_abierto") == "sol":
        col_botones, col_margen = st.columns([0.9, 0.1])
        
        with col_botones:
            if st.button("Rectas de Altura", key="btn_sol_recta", use_container_width=True):
                resetear_ejercicio()
                st.session_state["modo_navegacion"] = "sol"
                st.session_state["tipo_calculo_sol"] = "recta"
                st.rerun()

            if st.button("Meridiana", key="btn_sol_meridiana", use_container_width=True):
                resetear_ejercicio()
                st.session_state["modo_navegacion"] = "sol"
                st.session_state["tipo_calculo_sol"] = "meridiana"
                st.rerun()
        
    st.write("") 

    st.markdown(f'<img src="data:image/webp;base64,{base64_img}" class="menu-img menu-img-estrellas"/>', unsafe_allow_html=True)
    
    if st.button("**ESTRELLAS Y PLANETAS**", use_container_width=True):
        if st.session_state.get("menu_abierto") == "estrellas":
            st.session_state["menu_abierto"] = "ninguno"
        else:
            st.session_state["menu_abierto"] = "estrellas"
        st.rerun()

    if st.session_state.get("menu_abierto") == "estrellas":
        col_botones_est, col_margen_est = st.columns([0.9, 0.1])
        
        with col_botones_est:
            if st.button("Rectas de Altura", key="btn_est_recta", use_container_width=True):
                resetear_ejercicio()
                st.session_state["modo_navegacion"] = "estrellas"
                st.session_state["herramienta_estrellas"] = "rectas"
                st.rerun()

            if st.button("Mono de Astros", key="btn_est_mono", use_container_width=True):
                resetear_ejercicio()
                st.session_state["modo_navegacion"] = "estrellas"
                st.session_state["herramienta_estrellas"] = "mono"
                st.rerun()
                    
                st.write("") 
    
    try:
        with open("memoria.png", "rb") as image_file:
            base64_img_memoria = base64.b64encode(image_file.read()).decode()
            
        st.markdown(f'<img src="data:image/png;base64,{base64_img_memoria}" class="menu-img"/>', unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.caption("⚠️ No se encuentra el archivo 'memoria.png' en la carpeta.")

    if st.button("**MEMORIA**", use_container_width=True):
        if st.session_state.get("menu_abierto") == "memoria":
            st.session_state["menu_abierto"] = "ninguno"
        else:
            st.session_state["menu_abierto"] = "memoria"
        st.rerun()

    if st.session_state.get("menu_abierto") == "memoria":
        
        st.markdown("### Archivos Guardados")
        
        if "mensaje_flash" in st.session_state:
            st.success(st.session_state["mensaje_flash"])
            del st.session_state["mensaje_flash"] 
        
        lista_archivos = memoria.listar_ejercicios()
        
        if not lista_archivos:
            st.info("Aún no hay ejercicios guardados.")
        else:
            st.caption("1. Tipo de archivo:")
            filtro_tipo = st.selectbox(
                "Categoría:",
                [
                    "☀️ Rectas de Altura", 
                    "☀️ Meridiana", 
                    "✨ Rectas de Altura", 
                    "🔭 Mono de Astros"
                ],
                label_visibility="collapsed" 
            )
            
            archivos_filtrados = []
            for e in lista_archivos:
                t = str(e.get('tipo', '')).lower()
                
                if filtro_tipo == "☀️ Rectas de Altura" and "sol" in t and "recta" in t:
                    archivos_filtrados.append(e)
                elif filtro_tipo == "☀️ Meridiana" and "sol" in t and "meridiana" in t:
                    archivos_filtrados.append(e)
                elif filtro_tipo == "✨ Rectas de Altura" and "estrella" in t and "mono" not in t:
                    archivos_filtrados.append(e)
                elif filtro_tipo == "🔭 Mono de Astros" and "mono" in t:
                    archivos_filtrados.append(e)

            st.markdown("<br>", unsafe_allow_html=True) 
            
            if not archivos_filtrados:
                st.info("No hay ejercicios guardados en esta categoría.")
            else:
                st.caption("2. Selecciona el archivo:")
                
                archivos_filtrados = sorted(archivos_filtrados, key=lambda x: x.get('fecha', ''), reverse=True)
                opciones = {e['nombre']: e for e in archivos_filtrados}  
                seleccion = st.selectbox("Ejercicios", options=list(opciones.keys()), label_visibility="collapsed")
                archivo_elegido = opciones[seleccion]
                
                c_load, c_pdf, c_del = st.columns([2, 2, 1])

                if c_load.button("📂 Abrir", use_container_width=True):
                    datos_cargados, tipo_cargado = memoria.cargar_ejercicio(archivo_elegido['ruta_completa'])

                    if datos_cargados:
                        st.session_state.clear() 

                        for k, v in datos_cargados.items():
                            if isinstance(v, str) and len(v) == 10 and v.count('-') == 2:
                                try:
                                    fecha_obj = datetime.datetime.strptime(v, "%Y-%m-%d").date()
                                    st.session_state[k] = fecha_obj
                                except ValueError:
                                    st.session_state[k] = v
                            else:
                                st.session_state[k] = v

                        if "sol" in tipo_cargado:
                            st.session_state["modo_navegacion"] = "sol"
                            st.session_state["tipo_calculo_sol"] = "meridiana" if "meridiana" in tipo_cargado else "recta"
                        elif "estrellas" in tipo_cargado:
                            st.session_state["modo_navegacion"] = "estrellas"
                            st.session_state["herramienta_estrellas"] = "mono" if "mono" in tipo_cargado else "rectas"
                            
                        st.session_state["mensaje_flash"] = "¡Ejercicio cargado!"
                        st.rerun() 

                if c_pdf.button("🖨️ PDF", help="Generar documento PDF", use_container_width=True):
                    datos_cargados, tipo_cargado = memoria.cargar_ejercicio(archivo_elegido['ruta_completa'])
                    
                    if datos_cargados:
                        st.session_state.clear()
                        
                        for k, v in datos_cargados.items():
                            if k == "orden_imprimir_pdf":
                                    continue
                            if isinstance(v, str) and len(v) == 10 and v.count('-') == 2:
                                try: st.session_state[k] = datetime.datetime.strptime(v, "%Y-%m-%d").date()
                                except: st.session_state[k] = v
                            else: st.session_state[k] = v

                        st.session_state["orden_imprimir_pdf"] = True

                        if "sol" in tipo_cargado:
                            st.session_state["modo_navegacion"] = "sol"
                            st.session_state["tipo_calculo_sol"] = "meridiana" if "meridiana" in tipo_cargado else "recta"
                        elif "estrellas" in tipo_cargado:
                            st.session_state["modo_navegacion"] = "estrellas"
                            st.session_state["herramienta_estrellas"] = "mono" if "mono" in tipo_cargado else "rectas"
                            
                        st.rerun()

                if c_del.button("🗑️", help="Borrar ejercicio"):
                    memoria.eliminar_ejercicio(archivo_elegido['ruta_completa'])
                    st.session_state["mensaje_flash"] = "Ejercicio borrado."
                    st.rerun()
                
    st.markdown("---") 

if st.session_state["modo_navegacion"] == "sol":

        if "tipo_calculo_sol" not in st.session_state:
            st.session_state["tipo_calculo_sol"] = "recta"

        if st.session_state["tipo_calculo_sol"] == "recta": 
        
            es_pdf = st.session_state.get("orden_imprimir_pdf", False)

            if es_pdf:
                st.markdown("""
                <div style='text-align: center; margin-bottom: 15px;'>
                    <h2 style='text-decoration: underline; margin-bottom: 5px;'>CÁLCULO DE LA POSICIÓN MEDIANTE RECTAS DE ALTURA</h2>
                    <h3 style='margin-top: 0;'>OBSERVACIÓN DEL SOL</h3>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="hero-container">
                    <div class="hero-overlay">
                        <div class="hero-title">CÁLCULO DE LA POSICIÓN MEDIANTE RECTAS DE ALTURA</div>
                        <div class="hero-subtitle">OBSERVACIÓN DEL SOL</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            col_izq, col_der = st.columns(2, gap="medium")
            res_obs1 = procesar_observacion(col_izq, 1, "1ª Observación")
            res_obs2 = procesar_observacion(col_der, 2, "2ª Observación")

            st.markdown("---")
            with st.container():
                if not es_pdf:
                    st.header("Solución gráfica")

                if res_obs1 and res_obs2:
                    calcular = es_pdf or st.button("CALCULAR POSICIÓN FINAL", type="primary", use_container_width=True, key="btn_calc_situacion")
                    if calcular:
                        col_res_datos, col_res_mapa = st.columns([1, 2])
                        
                        with col_res_mapa:
                            try:
                                lat_fix, lon_fix = graficas.dibujar_situacion(res_obs1, res_obs2)
                                st.pyplot(plt.gcf())
                            except Exception as e:
                                st.error(f"Error en gráfico: {e}")
                                lat_fix = None; lon_fix = None
                        
                        with col_res_datos:
                            if lat_fix:
                                try:
                                    lat_str = decimal_a_dms_cardinal(lat_fix, es_latitud=True)
                                    lon_str = decimal_a_dms_cardinal(lon_fix, es_latitud=False)
                                except:
                                    lat_str = f"{lat_fix:.4f}°"
                                    lon_str = f"{lon_fix:.4f}°"

                                st.markdown("### Situación Corregida ")

                                if es_pdf:
                                    st.write(f"- **Latitud Verdadera:** {lat_str}")
                                    st.write(f"- **Longitud Verdadera:** {lon_str}")
                                else:
                                    st.markdown(f"""
                                    <div class='info-card-green'>
                                        <span class='card-label'>LATITUD VERDADERA</span>
                                        <span class='card-value'>{lat_str}</span>
                                    </div>
                                    <div class='info-card-green'>
                                        <span class='card-label'>LONGITUD VERDADERA</span>
                                        <span class='card-value'>{lon_str}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                lat_ref = res_obs2.get('LatEst', 0); lon_ref = res_obs2.get('LonEst', 0)
                                dLat = (lat_fix - lat_ref); dLon = (lon_fix - lon_ref)
                                
                                try:
                                    dLat_str = decimal_a_dms_cardinal(dLat, es_latitud=True)
                                    dLon_str = decimal_a_dms_cardinal(dLon, es_latitud=False)
                                except:
                                    dLat_str = f"{dLat:.2f}'"; dLon_str = f"{dLon:.2f}'"

                                st.markdown("### Corrección a la Estima")

                                if es_pdf:
                                    st.write(f"- **Diferencia Latitud:** {dLat_str}")
                                    st.write(f"- **Diferencia Longitud:** {dLon_str}")
                                else:
                                    st.markdown(f"""
                                    <div class='info-card-secondary'>
                                        <span class='card-label'>DIFERENCIA LATITUD</span>
                                        <span class='card-value card-value-small'>{dLat_str}</span>
                                    </div>
                                    <div class='info-card-secondary'>
                                        <span class='card-label'>DIFERENCIA LONGITUD</span>
                                        <span class='card-value card-value-small'>{dLon_str}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
            
            if not es_pdf:
                st.markdown("---")
                st.subheader("📂 Guardar Observación del Sol")
                c_name, c_btn = st.columns([3, 1])
                nombre_real = c_name.text_input("Nombre del ejercicio", placeholder="Ej: Situación Mañana", key="save_recta_input")
                
                c_btn.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if c_btn.button("Guardar", key="btn_save_sol_recta"):

                    n1 = st.session_state.get("n_1", 1); n2 = st.session_state.get("n_2", 1)
                    datos_a_guardar = {}
                    for k, v in st.session_state.items():
                        if "btn_" in k or "tri_3d" in k or k == "mensaje_flash" or k == "orden_imprimir_pdf": continue
                        parts = k.split('_')
                        if len(parts) >= 3 and parts[-1].isdigit():
                            idx = int(parts[-1]); id_obs = parts[-2]
                            if id_obs == '1' and idx >= n1: continue
                            if id_obs == '2' and idx >= n2: continue
                        datos_a_guardar[k] = v
                    
                    ok, msg = memoria.guardar_ejercicio(nombre_real, datos_a_guardar, "sol_recta")
                    
                    if ok:
                        st.session_state["mensaje_flash"] = msg 
                        st.rerun()
                    else:
                        st.error(msg)
            
        elif st.session_state["tipo_calculo_sol"] == "meridiana":
            es_pdf = st.session_state.get("orden_imprimir_pdf", False)

            if es_pdf:
                st.markdown("""
                <div style='text-align: center; margin-bottom: 0px;'>
                    <h2 style='text-decoration: underline; margin-bottom: 2px;'>CÁLCULO DE LA LATITUD MEDIANTE LA MERIDIANA</h2>
                    <h3 style='margin-top: 0; margin-bottom: 5px;'>OBSERVACIÓN DEL SOL</h3>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="hero-container">
                    <div class="hero-overlay">
                        <div class="hero-title">CÁLCULO DE LA LATITUD MEDIANTE LA MERIDIANA</div>
                        <div class="hero-subtitle">OBSERVACIÓN DEL SOL</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            col_izq_datos, col_der_datos = st.columns(2, gap="large")
            
            with col_izq_datos:
                st.markdown("### 1. Situación de Estima")
                if es_pdf:
                    l_g = st.session_state.get("meri_lat_g", 40)
                    l_m = st.session_state.get("meri_lat_m", 0)
                    l_s = st.session_state.get("meri_lat_s", 0.0)
                    l_card = st.session_state.get("meri_lat_c", "N")
                    L_g = st.session_state.get("meri_lon_g", 0)
                    L_m = st.session_state.get("meri_lon_m", 0)
                    L_s = st.session_state.get("meri_lon_s", 0.0)
                    L_card = st.session_state.get("meri_lon_c", "W")
                    st.write(f"- **Latitud Estimada:** {l_g}º {l_m}' {l_s}'' {l_card}")
                    st.write(f"- **Longitud Estimada:** {L_g}º {L_m}' {L_s}'' {L_card}")
                else:
                    st.caption("**Latitud estimada**")
                    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.8])
                    with c1: l_g = st.number_input("Grados", 0, 90, 0, key="meri_lat_g", label_visibility="collapsed")
                    with c2: l_m = st.number_input("Min", 0, 59, 0, key="meri_lat_m", label_visibility="collapsed")
                    with c3: l_s = st.number_input("Seg", 0.0, 59.9, 0.0, step=0.1, key="meri_lat_s", label_visibility="collapsed")
                    with c4: l_card = st.selectbox("N/S", ["N", "S"], key="meri_lat_c", label_visibility="collapsed")

                    st.caption("**Longitud estimada**")
                    c5, c6, c7, c8 = st.columns([1, 1, 1, 0.8])
                    with c5: L_g = st.number_input("Grados", 0, 180, 0, key="meri_lon_g", label_visibility="collapsed")
                    with c6: L_m = st.number_input("Min", 0, 59, 0, key="meri_lon_m", label_visibility="collapsed")
                    with c7: L_s = st.number_input("Seg", 0.0, 59.9, 0.0, step=0.1, key="meri_lon_s", label_visibility="collapsed")
                    with c8: L_card = st.selectbox("E/W", ["W", "E"], key="meri_lon_c", label_visibility="collapsed")

                le_decimal = l_g + (l_m / 60) + (l_s / 3600)
                if l_card == "S":
                    le_decimal = -le_decimal

            with col_der_datos:
                st.markdown("### 2. Condiciones de Observación")
                if es_pdf:
                    fecha_meridiana = st.session_state.get("meri_fecha", datetime.date.today())
                    ei = st.session_state.get("meri_ei", 0.0)
                    ao = st.session_state.get("meri_ao", 2.0)
                    st.write(f"- **Fecha:** {fecha_meridiana.strftime('%d/%m/%Y')}")
                    st.write(f"- **Elevación Observador:** {ao} m &nbsp;&nbsp;|&nbsp;&nbsp; **Error Índice:** {ei}'")
                else:
                    if "meri_fecha" not in st.session_state:
                        st.session_state["meri_fecha"] = datetime.date.today()
                    fecha_meridiana = st.date_input("**Fecha de Observación**", format="DD/MM/YYYY", key="meri_fecha")
                    c_cond1, c_cond2 = st.columns(2)
                    if "meri_ei" not in st.session_state:
                        st.session_state["meri_ei"] = 0.0
                    ei = c_cond1.number_input("**Error Índice (')**", step=0.1, 
                                            format="%.1f", key="meri_ei")
                    if "meri_ao" not in st.session_state:
                        st.session_state["meri_ao"] = 0.0
                    ao = c_cond2.number_input("**Elevación del observador (m)**", step=0.5, 
                                            format="%.1f", key="meri_ao")

            st.markdown("---")

            st.markdown("### 3. Registro de Alturas")
            
            if es_pdf:
                n_med = st.session_state.get("n_meri_input", 5)
                borradas = st.session_state.get("del_meri_final_smart", [])
            else:
                n_med = st.number_input(f"Nº Mediciones", 1, 20, 5, key="n_meri_input") 
            
            raw_data = []
            textos_observaciones_pdf = []
            
            if not es_pdf:
                c_h_head, c_a_head = st.columns([1, 1], gap="medium")
                c_h_head.markdown("<div class='unit-header'>Hora UTC<br>( h ) : ( m ) : ( s )</div>", unsafe_allow_html=True)
                c_a_head.markdown("<div class='unit-header'>Altura Instrumental<br>( º ) : ( ' ) : ( '' )</div>", unsafe_allow_html=True)

            for i in range(n_med):
                if es_pdf:
                    hh = st.session_state.get(f"h_meri_{i}", 12)
                    mm = st.session_state.get(f"m_meri_{i}", 0)
                    ss = st.session_state.get(f"s_meri_{i}", 0.0)
                    gg = st.session_state.get(f"g_meri_{i}", 45)
                    mmi = st.session_state.get(f"mi_meri_{i}", 0)
                    sse = st.session_state.get(f"si_meri_{i}", 0.0)
                    estado = "(Descartada)" if i in borradas else "(Válida)"
                    textos_observaciones_pdf.append(f"- **Obs #{i+1}:** {int(hh):02d}:{int(mm):02d}:{int(ss):02d} &nbsp;|&nbsp; {int(gg)}º {int(mmi):02d}' {int(sse):02d}'' {estado}")
                else:
                    with st.container():
                        c_hora, c_alt = st.columns([1, 1], gap="medium")
                        with c_hora:
                            ch, cm, cs = st.columns(3)
                            hh = ch.number_input("H", 0, 23, 0, key=f"h_meri_{i}", label_visibility="collapsed")
                            mm = cm.number_input("M", 0, 59, 0, key=f"m_meri_{i}", label_visibility="collapsed")
                            ss = cs.number_input("S", 0, 59, 0, key=f"s_meri_{i}", label_visibility="collapsed")
                        with c_alt:
                            cg, cmi, cse = st.columns(3)
                            gg = cg.number_input("G", 0, 90, 0, key=f"g_meri_{i}", label_visibility="collapsed")
                            mmi = cmi.number_input("M", 0, 59, 0, key=f"mi_meri_{i}", label_visibility="collapsed")
                            sse = cse.number_input("S", 0, 59, 0, key=f"si_meri_{i}", label_visibility="collapsed")
                
                h_dec = float(hh) + float(mm)/60.0 + float(ss)/3600.0
                ai_dec = float(gg) + float(mmi)/60.0 + float(sse)/3600.0
                time_seconds = hh*3600 + mm*60 + ss
                
                if time_seconds > 0 or ai_dec > 0:
                    raw_data.append({"id": i, "x": time_seconds, "y": ai_dec, "h_dec": h_dec})

            df = pd.DataFrame(raw_data)
            
            if df.empty:
                st.info("Introduce datos para ver la gráfica.")
                st.stop()

            if es_pdf:
                borrar = borradas
            else:
                st.markdown("#### Depuración")
                borrar = st.multiselect("Selecciona mediciones erróneas (X):", options=df['id'], format_func=lambda x: f"Obs #{x+1}", key="del_meri_final_smart")
            
            df_clean = df[~df['id'].isin(borrar)]
            df_borradas = df[df['id'].isin(borrar)]
            
            if df_clean.empty:
                st.error("⚠️ No hay mediciones válidas.")
                st.stop()

            ai_max_final = None 
            time_max_final = None 
            mostrar_curva = False
            mostrar_recta = False
            p_recta = None
            
            row_max_obs = df_clean.loc[df_clean['y'].idxmax()]
            ai_max_obs = row_max_obs['y']
            time_max_obs = row_max_obs['x']

            if len(df_clean) < 3:
                if len(df_clean) == 2:
                    try:
                        z_lin = np.polyfit(df_clean['x'], df_clean['y'], 1)
                        p_recta = np.poly1d(z_lin)
                        mostrar_recta = True
                    except:
                        pass
                
                if len(df_clean) == 2 and abs(df_clean.iloc[0]['y'] - df_clean.iloc[1]['y']) < 0.001:
                    ai_max_final = df_clean.iloc[0]['y']
                    time_max_final = (df_clean.iloc[0]['x'] + df_clean.iloc[1]['x']) / 2.0
                else:
                    ai_max_final = ai_max_obs
                    time_max_final = time_max_obs
            else:
                z = np.polyfit(df_clean['x'], df_clean['y'], 2)
                p = np.poly1d(z)
                a_poly = z[0]
                b_poly = z[1]
                
                if a_poly != 0:
                    time_vertex = -b_poly / (2 * a_poly)
                    ai_vertex = p(time_vertex)
                    mostrar_curva = True
                    if ai_max_obs > ai_vertex:
                        ai_max_final = ai_max_obs
                        time_max_final = time_max_obs
                    else:
                        ai_max_final = ai_vertex
                        time_max_final = time_vertex
                else:
                    ai_max_final = ai_max_obs
                    time_max_final = time_max_obs

            if es_pdf:
                fig, ax = plt.subplots(figsize=(3.5, 2.5)) 
            else:
                fig, ax = plt.subplots(figsize=(7, 4)) 

            def formato_grados_minutos(val, pos):
                d = int(val)
                m = int(round((abs(val) - abs(d)) * 60))
                if m == 60: 
                    d += 1 if val >= 0 else -1
                    m = 0
                return f"{d}º {m:02d}'"
            ax.yaxis.set_major_formatter(FuncFormatter(formato_grados_minutos))
            
            c_puntos = 'blue'      
            c_linea = 'b--'        
            c_max = 'gold'         
            e_max = 'orangered'

            ax.scatter(df_clean['x'], df_clean['y'], c=c_puntos, s=30 if es_pdf else 40, alpha=0.7, zorder=5, label='Válidas')
            if not df_borradas.empty: 
                ax.scatter(df_borradas['x'], df_borradas['y'], c='gray', marker='x', s=30 if es_pdf else 40, alpha=0.5, zorder=5)
            
            if mostrar_curva:
                x_span_total = df_clean['x'].max() - df_clean['x'].min()
                if x_span_total == 0: x_span_total = 60
                xp = np.linspace(df_clean['x'].min() - x_span_total*0.2, df_clean['x'].max() + x_span_total*0.2, 100)
                ax.plot(xp, p(xp), c_linea, linewidth=1, alpha=0.5, label='Parábola')

            if mostrar_recta and p_recta is not None:
                x_vals = df_clean['x']
                margin = (x_vals.max() - x_vals.min()) * 0.1 if (x_vals.max() - x_vals.min()) > 0 else 60
                xp = np.linspace(x_vals.min() - margin, x_vals.max() + margin, 10)
                ax.plot(xp, p_recta(xp), c_linea, linewidth=1, alpha=0.6, label='Tendencia')
            
            ax.scatter(time_max_final, ai_max_final, c=c_max, edgecolors=e_max, linewidth=1, marker='^', s=80 if es_pdf else 100, zorder=10, label='Máximo')
            
            y_vals = df_clean['y'].values
            if mostrar_curva: y_vals = np.append(y_vals, ai_max_final)
            y_min, y_max = np.min(y_vals), np.max(y_vals)
            margin_y = (y_max - y_min) * 0.2 if y_max != y_min else 0.1
            
            x_vals = df_clean['x'].values
            if mostrar_curva: x_vals = np.append(x_vals, time_max_final)
            x_min, x_max = np.min(x_vals), np.max(x_vals)
            
            span_x = x_max - x_min
            margin_x = span_x * 0.15 if span_x > 0 else 60
            x_lim_min = x_min - margin_x
            x_lim_max = x_max + margin_x
            
            ax.set_ylim(y_min - margin_y, y_max + margin_y)
            ax.set_xlim(x_lim_min, x_lim_max)

            total_seconds_visible = x_lim_max - x_lim_min
            possible_steps = [60, 120, 180, 300, 600, 900, 1200, 1800, 3600]
            raw_step = total_seconds_visible / 6
            chosen_step = 60 
            for step in possible_steps:
                if step >= raw_step:
                    chosen_step = step
                    break
            
            if total_seconds_visible < 3600 * 5:
                ax.xaxis.set_major_locator(MultipleLocator(chosen_step))

            ax.xaxis.set_major_formatter(FuncFormatter(format_seconds_to_hhmm))
            
            ax.set_ylabel("Altura (º)", fontsize=8 if es_pdf else 9)
            ax.set_xlabel("Hora UTC", fontsize=8 if es_pdf else 9)
            ax.tick_params(axis='both', which='major', labelsize=7 if es_pdf else 8)
            plt.xticks(rotation=0)
            ax.grid(True, alpha=0.3, linestyle='--', which='both')
            ax.legend(fontsize=7 if es_pdf else 8, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
            
            plt.tight_layout() 
            
            deg_int = int(ai_max_final)
            min_int = int((ai_max_final - deg_int)*60)
            sec_dec = (ai_max_final - deg_int - min_int/60)*3600
            ai_str = f"{deg_int}° {min_int}' {sec_dec:.1f}''"
            
            h_v = int(time_max_final // 3600)
            m_v = int((time_max_final % 3600) // 60)
            s_v = int(time_max_final % 60)

            if es_pdf:
                col_lista, col_grafica = st.columns([1, 1], gap="medium")
                
                with col_lista:
                    for linea in textos_observaciones_pdf:
                        st.write(linea)
                    st.markdown(f"<br>**PUNTO MÁXIMO CALCULADO (UTC | ALTURA):**<br>{h_v:02}:{m_v:02}:{s_v:02} &nbsp;&nbsp;|&nbsp;&nbsp; {ai_str}", unsafe_allow_html=True)
                
                with col_grafica:
                    st.pyplot(fig, use_container_width=True)
            else:
                st.pyplot(fig, use_container_width=False)
                st.markdown(f"""
                <div class="info-card-green" style="padding: 10px; margin-top: 5px;">
                    <div style="display:flex; justify-content:space-between;">
                        <div style="text-align:center; width:48%;">
                            <span class="card-label" style="font-size: 1rem;">HORA UTC</span><br>
                            <span class="card-value" style="font-size: 1.2rem;">{h_v:02}:{m_v:02}:{s_v:02}</span>
                        </div>
                        <div style="border-left:1px solid #ddd;"></div>
                        <div style="text-align:center; width:48%;">
                            <span class="card-label" style="font-size: 1rem;">ALTURA MÁXIMA</span><br>
                            <span class="card-value" style="font-size: 1.2rem;">{ai_str}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if ai_max_final is not None and time_max_final is not None:
                st.markdown("---")
                st.markdown("### 4. Desarrollo de Cálculos")
                
                try:
                    h_paso = int(time_max_final // 3600)
                    m_paso = int((time_max_final % 3600) // 60)
                    s_paso = int(time_max_final % 60)
                    time_paso = datetime.time(h_paso, m_paso, s_paso)

                    anio = fecha_meridiana.year
                    dia_anho = fecha_meridiana.timetuple().tm_yday
                    nombre_archivo = f"AN{anio}{dia_anho + 9}.dat"
                    ruta_archivo = os.path.join("almanaque", nombre_archivo)
                    
                    dec = 0.0 
                    
                    if not os.path.exists(ruta_archivo):
                        st.error(f"❌ No encuentro el archivo: {ruta_archivo}")
                        st.stop()
                    else:
                        datos_dia = almanaque.leer_datos_dat_completo(ruta_archivo)
                        dato_hora_actual = datos_dia.get(h_paso)
                        dato_hora_siguiente = datos_dia.get(h_paso + 1)
                        
                        if dato_hora_actual:
                            dec1 = dato_hora_actual['dec_sol']
                            if dato_hora_siguiente:
                                dec2 = dato_hora_siguiente['dec_sol']
                                factor = (m_paso / 60.0) + (s_paso / 3600.0)
                                dec = dec1 + (dec2 - dec1) * factor
                            else:
                                dec = dec1
                        else:
                            st.error(f"Sin datos para la hora {h_paso}.")
                            st.stop()

                    st.markdown("#### A) Datos del Almanaque")
                    d_dec = int(dec)
                    m_dec = (dec - d_dec) * 60
                    txt_dec = f"{d_dec}^\circ {abs(m_dec):.1f}'"

                    st.latex(rf"\text{{Declinación }}(\delta) = \mathbf{{{txt_dec}}}")

                    if not es_pdf:
                        doy = fecha_meridiana.timetuple().tm_yday
                        num_pag = doy + 9
                        with st.expander("Definiciones y fuentes"):
                            st.markdown(f"""
                                * **$\\delta$ (Declinación):** Ángulo desde el ecuador hasta la proyección del Sol en la Tierra (Latitud del Sol).
                                    * *Fuente:* Páginas Diarias (Pág. {num_pag} Almanaque Náutico)
                                """)

                    st.markdown("#### B) Correcciones de Altura")
                    
                    hi = ai_max_final
                    
                    ho = hi + (ei / 60.0)
                    
                    corr_dep_min = -1.7757 * math.sqrt(ao) 
                    ha = ho + (corr_dep_min / 60.0)
                    
                    b1_min = almanaque.obtener_correccion_b1(ha)
                    
                    b2_min = almanaque.obtener_correccion_b2(fecha_meridiana.month, fecha_meridiana.day, fecha_meridiana.year)
                    
                    hv = ha + (b1_min / 60.0) + (b2_min / 60.0)

                    txt_ai = fmt_gm(hi)
                    txt_ao = fmt_gm(ho)
                    txt_ha = fmt_gm(ha)
                    txt_hv = fmt_gm(hv)
                    
                    txt_ei_str = f"{ei:+.1f}'"
                    txt_dep_str = f"{corr_dep_min:+.1f}'"
                    txt_b1_str = f"{b1_min:+.1f}'"
                    txt_b2_str = f"{b2_min:+.1f}'"

                    st.latex(rf'''\mathbf{{h_i}} = \mathbf{{{txt_ai}}}''')
                    st.latex(rf'''\mathbf{{h_o}} = h_i + e_i = {txt_ai} + ({txt_ei_str}) = \mathbf{{{txt_ao}}}''')
                    st.latex(rf'''\mathbf{{h_a}} = h_o + d = {txt_ao} + ({txt_dep_str}) = \mathbf{{{txt_ha}}}''')
                    st.latex(rf'''\mathbf{{h_v}} = h_a + b_1 + b_2 = {txt_ha} + ({txt_b1_str}) + ({txt_b2_str}) = \mathbf{{{txt_hv}}}''')

                    if not es_pdf:
                        with st.expander("Definiciones y fuentes"):
                            st.markdown(r"""
                            * **$h_i$ (Altura Instrumental):** Lectura máxima obtenida.
                            * **$h_o$ (Altura Observada):** Corregida por error instrumental ($h_i + e_i$).
                            * **$h_a$ (Altura Aparente):** Corregida por la altura del ojo ($h_o + d$).
                            * **$h_v$ (Altura Verdadera):** Altura final corregida.
                            * **$e_i$ (Error de Índice):** Error propio del sextante.
                            * **$d$ (Depresión del Horizonte):** Corrección por elevación del observador.
                                * *Fuente:* Tabla A (Pág. 387 Almanaque Náutico).
                                * *Fórmula:* $d = -1.7757 \cdot \sqrt{\text{Elevación}}$
                            * **$b_1$ (Corrección principal Sol):** Corrige los efectos de semidiámetro, refracción y paralaje.
                                * *Fuente:* Tabla B (Pág. 387 Almanaque Náutico).
                            * **$b_2$ (Corrección Adicional Sol):** Ajuste fino según la fecha (Semidiámetro real).
                                * *Fuente:* Tabla B (Pág. 387 Almanaque Náutico).
                            """)

                    st.markdown("#### C) Resolución Latitud")

                    def fmt_dms(val):
                        d = int(val)
                        m_float = abs((val - d) * 60.0)
                        m = int(m_float)
                        s = (m_float - m) * 60.0
                        return f"{d}^\circ {m}' {s:.1f}''" 
                    
                    def fmt_dms_txt(val):
                        d = int(val)
                        m_float = abs((val - d) * 60.0)
                        m = int(m_float)
                        s = (m_float - m) * 60.0
                        return f"{d}° {m}' {s:.1f}''"

                    z = 90.0 - hv
                    if dec > le_decimal:
                        lat_calc = dec - z
                    else:
                        lat_calc = z + dec   
                    
                    txt_hv = fmt_gm(hv)    
                    txt_z  = fmt_gm(z)     
                    txt_dec = fmt_gm(dec)  
                    
                    txt_lat_latex = fmt_dms(lat_calc) 
                    txt_lat_final = fmt_dms_txt(lat_calc) 

                    st.latex(rf"\mathbf{{z}} = 90^\circ - h_v = 90^\circ - {txt_hv} = {txt_z}")
                    if "-" in str(txt_dec):
                        dec_formatted = f"({txt_dec})"
                    else:
                        dec_formatted = txt_dec
                    st.latex(rf"\boldsymbol{{\varphi}} = z + \delta = {txt_z} + {dec_formatted} = \mathbf{{{txt_lat_latex}}}")
                    
                    if not es_pdf:
                        with st.expander("Definiciones y fuentes"):
                            st.markdown(r"""
                            * **$z$ (Distancia Cenital):** Es la distancia angular desde el cenit (nuestra vertical) hasta el astro.
                            * **$\varphi$ (Latitud):**  Coordenada vertical de nuestra posición supuesta.
                            """)
                        with st.expander("Ver diagrama geométrico de la Meridiana", expanded=False):
                            try:
                                fig_meri = graficas.dibujar_diagrama_meridiana(
                                    hv, dec, lat_calc
                                )
                                st.pyplot(fig_meri, use_container_width=True)
                                plt.close(fig_meri)
                            except Exception as e:
                                st.warning(f"No se pudo generar el diagrama: {e}")

                    lat_decimal = lat_calc

                    diferencia = lat_decimal - le_decimal

                    def formato_dms(valor_decimal):
                        val_abs = abs(valor_decimal)
                        grados = int(val_abs)
                        resto_minutos = (val_abs - grados) * 60
                        minutos = int(resto_minutos)
                        segundos = (resto_minutos - minutos) * 60
                        return grados, minutos, segundos

                    g_lat, m_lat, s_lat = formato_dms(lat_decimal)
                    letra_lat = "N" if lat_decimal >= 0 else "S"
                    lat_str_final = f"{g_lat}° {m_lat}' {s_lat:.1f}'' {letra_lat}"

                    g_dif, m_dif, s_dif = formato_dms(diferencia)
                    letra_dif = "N" if diferencia >= 0 else "S"
                    dLat_str = f"{g_dif}° {m_dif}' {s_dif:.1f}'' {letra_dif}"

                    st.markdown("### Resultado Final")

                    if es_pdf:
                        st.markdown(f"**RESULTADO FINAL:** &nbsp;&nbsp; Latitud Corregida: **{lat_str_final}** &nbsp;&nbsp;|&nbsp;&nbsp; Corrección: **{dLat_str}**")

                    else:
                        st.markdown("""
                        <style>
                        .info-card-green {
                            background-color: #d4edda;
                            border-left: 5px solid #28a745;
                            padding: 15px;
                            border-radius: 5px;
                            margin-bottom: 10px;
                            color: #155724;
                        }
                        .info-card-secondary {
                            background-color: #e2e3e5;
                            border-left: 5px solid #6c757d;
                            padding: 15px;
                            border-radius: 5px;
                            margin-bottom: 10px;
                            color: #383d41;
                        }
                        .card-label {
                            display: block; font-size: 0.8em; font-weight: bold; text-transform: uppercase;
                        }
                        .card-value {
                            display: block; font-size: 1.5em; font-weight: bold;
                        }
                        .card-value-small {
                            font-size: 1.2em; 
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                            <div class='info-card-green'>
                                <span class='card-label'>LATITUD CORREGIDA</span>
                                <span class='card-value'>{lat_str_final}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                        st.markdown(f"""
                            <div class='info-card-secondary'>
                                <span class='card-label'>DIFERENCIA DE LATITUD</span>
                                <span class='card-value card-value-small'>{dLat_str}</span>
                            </div>
                        """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error en el cálculo: {e}")
            
            if not es_pdf:
                st.markdown("---")
                st.subheader("📂 Guardar Meridiana")
                c_name_m, c_btn_m = st.columns([3, 1])
                nombre_real = c_name_m.text_input("Nombre", placeholder="Ej: Meridiana Mediodía", key="save_meri_input")
                
                c_btn_m.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if c_btn_m.button("Guardar", key="btn_save_meri"):
                    
                    n_actual = st.session_state.get("n_meri_input", 1)
                    datos_a_guardar = {}
                    for k, v in st.session_state.items():
                        if "btn_" in k or "tri_3d" in k or k == "mensaje_flash" or k == "orden_imprimir_pdf": continue
                        parts = k.split('_')
                        if len(parts) > 1 and parts[-1].isdigit() and "meri" in k:
                            if int(parts[-1]) >= n_actual: continue
                        datos_a_guardar[k] = v
                    
                    ok, msg = memoria.guardar_ejercicio(nombre_real, datos_a_guardar, "sol_meridiana")
                    
                    if ok:
                        st.session_state["mensaje_flash"] = msg 
                        st.rerun()
                    else:
                        st.error(msg)

if st.session_state["modo_navegacion"] == "estrellas":
    
    herramienta_estrellas = st.session_state.get("herramienta_estrellas", "rectas")
    es_pdf = st.session_state.get("orden_imprimir_pdf", False)

    if st.session_state.get("orden_imprimir_pdf", False) and st.session_state.get("herramienta_estrellas") == "mono":
        herramienta_estrellas = "mono"
    if herramienta_estrellas == "rectas":
        if es_pdf:
            st.markdown("""
            <div style='text-align: center;'>
                <h2><u>CÁLCULO DE LA POSICIÓN MEDIANTE RECTAS DE ALTURA</u></h2>
                <h3><u>OBSERVACIÓN DE ESTRELLAS Y PLANETAS</u></h3>
            </div>
            <br>
            """, unsafe_allow_html=True)
            st.markdown("---")
        else:
            st.markdown("""
            <div class="hero-container" style="filter: hue-rotate(220deg) brightness(0.8);">
                <div class="hero-overlay">
                    <div class="hero-title">CÁLCULO DE LA POSICIÓN MEDIANTE RECTAS DE ALTURA</div>
                    <div class="hero-subtitle">OBSERVACIÓN DE ESTRELLAS Y PLANETAS</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


        if not es_pdf:
            st.markdown("### 1. Situación de Estima")
            col_lat_gen, col_lon_gen = st.columns(2)
            with col_lat_gen:
                lat_general = input_coord_dms("Latitud Estimada", "est_global_lat", "lat", 0, 0, 0.0, "N")
            with col_lon_gen:
                lon_general = input_coord_dms("Longitud Estimada", "est_global_lon", "lon", 0, 0, 0.0, "W")
            st.markdown("---")
            st.subheader("2. Condiciones de Observación")
        
            st.markdown("""
                <style>
                div[data-testid="stDateInput"] input {
                    text-align: center;
                }
                </style>
                """, unsafe_allow_html=True)

            col_izq, col_centro, col_der = st.columns([1, 1, 1])
            
            with col_centro:
                if "fecha_estrellas" not in st.session_state:
                    st.session_state["fecha_estrellas"] = datetime.date.today()
                fecha = st.date_input("Fecha de la Observación", format="DD/MM/YYYY", key="fecha_estrellas")

            st.write("") 

            c_cond_1, c_cond_2 = st.columns(2, gap="medium")

            with c_cond_1:
                if "eo_estrellas" not in st.session_state:
                    st.session_state["eo_estrellas"] = 0.0
                eo = st.number_input("Elevación del Observador (metros)", step=0.1, format="%.1f", key="eo_estrellas")

            with c_cond_2:
                if "ei_estrellas" not in st.session_state:
                    st.session_state["ei_estrellas"] = 0.0
                ei = st.number_input("Error de Índice (minutos)", step=0.1, format="%.1f", key="ei_estrellas")

            st.markdown("---")
            st.markdown("### 3. Observaciones")

            c1, c2, c3 = st.columns(3, gap="small")
            columnas = [c1, c2, c3]

        else:
            g_lat = st.session_state.get("est_global_lat_g", 0)
            m_lat = st.session_state.get("est_global_lat_m", 0)
            s_lat = st.session_state.get("est_global_lat_s", 0.0)
            c_lat = st.session_state.get("est_global_lat_c", "N")
            
            g_lon = st.session_state.get("est_global_lon_g", 0)
            m_lon = st.session_state.get("est_global_lon_m", 0)
            s_lon = st.session_state.get("est_global_lon_s", 0.0)
            c_lon = st.session_state.get("est_global_lon_c", "W")
            
            lat_general = dms_a_decimal(g_lat, m_lat, s_lat, c_lat)
            lon_general = dms_a_decimal(g_lon, m_lon, s_lon, c_lon)
            
            fecha = st.session_state.get("fecha_estrellas", datetime.date.today())
            eo = st.session_state.get("eo_estrellas", 0.0)
            ei = st.session_state.get("ei_estrellas", 0.0)

            col_pdf_est, col_pdf_cond = st.columns(2)

            with col_pdf_est:
                st.markdown("#### <u>1. Situación de Estima</u>", unsafe_allow_html=True)
                st.write(f"- **Latitud:** {g_lat}º {m_lat}' {s_lat}'' {c_lat}")
                st.write(f"- **Longitud:** {g_lon}º {m_lon}' {s_lon}'' {c_lon}")
                
            with col_pdf_cond:
                st.markdown("#### <u>2. Condiciones de Observación</u>", unsafe_allow_html=True)
                st.write(f"- **Fecha:** {fecha.strftime('%d/%m/%Y')}")
                st.write(f"- **Elevación Ojo:** {eo} m")
                st.write(f"- **Error Índice:** {ei}'")
            
            columnas = [st.container(), st.container(), st.container()]

        resultados = []

        for i in range(3):
            obs = procesar_input_estrella(columnas[i], i+1, lat_general, lon_general)
            
            if obs is not None:
                with columnas[i]:
                    if es_pdf:
                        st.markdown("---")
                        st.markdown(f"<h3 style='text-align: center;'>3.{i+1} Observación {obs['Nombre']}</h3>", unsafe_allow_html=True)
                        c_txt, c_fig = st.columns([1, 1.2])
                        
                        with c_txt:
                            st.markdown("**Registro de Alturas**")
                            for txt in obs['textos_obs']:
                                st.write(txt)
                                
                            st.write("")
                            st.markdown(f"**MEDIAS CALCULADAS:**<br>{obs['texto_hora_media']} &nbsp;|&nbsp; {obs['texto_altura_media']}", unsafe_allow_html=True)
                        
                        with c_fig:
                            if "Figura" in obs and obs["Figura"]:
                                st.pyplot(obs["Figura"])
                                               
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        st.markdown(f"#### <u>4.{i+1} Desarrollo de Cálculos</u>", unsafe_allow_html=True)
                    
                    else:
                        st.markdown(f"#### 4.{i+1} Desarrollo de Cálculos")
                    
                    planetas = ["Venus", "Marte", "Jupiter", "Saturno"]
                    es_planeta = obs['Nombre'] in planetas
                    
                    gha_est = None
                    dec = None
                    
                    if es_planeta:
                        gha_pla, dec_pla = almanaque.get_datos_planeta(obs['Nombre'], fecha.day, fecha.month, fecha.year, obs['Hora'])
                        
                        if gha_pla is None:
                            if not es_pdf: st.error("❌ Datos no encontrados en el archivo DAT.")
                        else:
                            st.markdown("**A) Datos del Almanaque**")
                            txt_gha = fmt_gms(gha_pla)
                            txt_dec = fmt_gms(dec_pla)
                            
                            st.latex(rf"\mathbf{{hG_{{{obs['Nombre']}}}}} = {txt_gha}")
                            st.latex(rf"\boldsymbol{{\delta}} = {txt_dec}")
                            
                            gha_est = gha_pla
                            dec = dec_pla
                            gha_aries = 0.0   
                            sha_aprox = 0.0   
                            doy = fecha.timetuple().tm_yday
                            num_pag = doy + 9

                            if not es_pdf:
                                with st.expander("Definiciones y fuentes"):
                                    st.markdown(f"""
                                    * **$hG_{{{obs['Nombre']}}}$ (Ángulo Horario del astro ):** Longitud entre el Meridiano de Greenwich y el meridiano del astro. 
                                    * **$\\delta$ (Declinación):** Es el ángulo desde el ecuador hasta la proyección del astro en la Tierra (Latitud del astro).
                                        * *Fuente:* Páginas Diarias (Pág. {num_pag} Almanaque Náutico).
                                    """)

                    else:
                        gha_calc, dec_calc, gha_aries = almanaque.get_datos_estrella_aries(obs['Nombre'], fecha.day, fecha.month, fecha.year, obs['Hora'])
                        
                        if gha_calc is None:
                            if not es_pdf: st.error(f"{gha_aries}") 
                        else:
                            sha_aprox = (gha_calc - gha_aries) % 360.0
                            st.markdown("**A) Datos del Almanaque**")
                            
                            txt_gha_aries = fmt_gms(gha_aries)
                            txt_sha = fmt_gms(sha_aprox)
                            txt_dec = fmt_gms(dec_calc)
                            txt_gha_est = fmt_gms(gha_calc)
                            
                            st.latex(rf"\mathbf{{hG_\Upsilon}} = {txt_gha_aries}")
                            st.latex(rf"\mathbf{{A.S_*}} = {txt_sha} \quad | \quad \boldsymbol{{\delta}} = {txt_dec}")
                            st.latex(rf"\mathbf{{hG_*}} = hG_\Upsilon + A.S_* = \mathbf{{{txt_gha_est}}}")
                            
                            gha_est = gha_calc
                            dec = dec_calc
                            
                            doy = fecha.timetuple().tm_yday
                            num_pag = doy + 9

                            if not es_pdf:
                                with st.expander("Definiciones y fuentes"):
                                    st.markdown(f"""
                                    * **$hG_\\Upsilon$ (Ángulo Horario de Aries):** Longitud entre el Meridiano de Greenwich y el meridiano de Aries.
                                    * **$A.S_*$ (Ángulo Sidéreo):** Longitud entre el meridiano de Aries y el meridiano del astro.
                                    * **$hG_*$ (Ángulo Horario de la Estrella):** Longitud entre el Meridiano de Greenwich y el meridiano del astro. 
                                    * **$\\delta$ (Declinación):** Es el ángulo desde el ecuador hasta la proyección del astro en la Tierra (Latitud del astro).
                                        * *Fuente:* Páginas Diarias (Pág. {num_pag} Almanaque Náutico).
                                    """)

                    if gha_est is not None and dec is not None:
                        
                        st.markdown("**B) Correcciones de Altura**")
                        
                        corr = calculos.calcular_correccion_estrellas(obs['Ai'], eo, ei, obs['Nombre'], fecha)
                        hv = corr['AltVerdadera']
                        
                        txt_ai = fmt_gms(obs['Ai']); txt_ho = fmt_gms(corr['AltObservada'])
                        txt_ha = fmt_gms(corr['AltAparente']); txt_hv = fmt_gms(hv)
                        txt_ei = f"{ei:+.1f}'"; txt_dep = f"{corr['Depresion_min']:+.1f}'"
                        ref_valor = corr['Refraccion_min'] 
                        txt_ref = f"{ref_valor:.1f}'"

                        st.latex(rf"\mathbf{{h_i}} = \mathbf{{{txt_ai}}}")
                        st.latex(rf"\mathbf{{h_o}} = h_i + e_i = {txt_ai} + ({txt_ei}) = \mathbf{{{txt_ho}}}")
                        st.latex(rf"\mathbf{{h_a}} = h_o + d = {txt_ho} + ({txt_dep}) = \mathbf{{{txt_ha}}}")
                        
                        paralaje = corr.get('CorrParalaje_min', 0.0)
                        
                        if obs['Nombre'] in ['Venus', 'Marte']:
                            txt_par = f"{paralaje:+.1f}'"
                            st.latex(rf"\mathbf{{h_v}} = h_a - c_1 + c_2 = {txt_ha} - {txt_ref} + ({txt_par}) = \mathbf{{{txt_hv}}}")
                            
                            texto_adicional = r"""
                            * **$c_1$ (Refracción):** Tabla C (Pág. 387).
                            * **$c_2$ (Paralaje):** Corrección adicional por cercanía (Venus/Marte).
                            """
                        else:
                            st.latex(rf"\mathbf{{h_v}} = h_a - c_1 = {txt_ha} - {txt_ref} = \mathbf{{{txt_hv}}}")
                            texto_adicional = r"* **$c_1$ (Refracción):** Tabla C (Pág. 387 Almanaque)."

                        if not es_pdf:
                            with st.expander("Definiciones y Fuentes"):
                                
                                if obs['Nombre'] in ['Venus', 'Marte']:
                                    st.markdown(r"""
                                    * **$h_i$ (Altura Instrumental):** Lectura directa del sextante.
                                    * **$h_o$ (Altura Observada):** Corregida por error instrumental ($h_i + e_i$).
                                    * **$h_a$ (Altura Aparente):** Corregida por la altura del ojo ($h_o + d$).
                                    * **$h_v$ (Altura Verdadera):** Altura final ($h_a - c_1 + c_2$).
                                    * **$e_i$ (Error de Índice):** Error propio del sextante.
                                    * **$d$ (Depresión del Horizonte):** Corrección por elevación del ojo.
                                    * **$c_1$ (Refracción):** Corrección negativa por atmósfera.
                                    * *Fuente:* Tabla C (Pág. 387 Almanaque Náutico).
                                    * **$c_2$ (Paralaje):** Corrección positiva por cercanía (Solo Venus/Marte).
                                    * *Fuente:* Tabla C (Pág. 387 Almanaque Náutico).
                                    """)
                                
                                else:
                                    st.markdown(r"""
                                    * **$h_i$ (Altura Instrumental):** Lectura directa del sextante.
                                    * **$h_o$ (Altura Observada):** Corregida por error instrumental ($h_i + e_i$).
                                    * **$h_a$ (Altura Aparente):** Corregida por la altura del ojo ($h_o + d$).
                                    * **$h_v$ (Altura Verdadera):** Altura final ($h_a - c_1$).
                                    * **$e_i$ (Error de Índice):** Error propio del sextante.
                                    * **$d$ (Depresión del Horizonte):** Corrección por elevación del ojo.
                                    * **$c_1$ (Refracción):** Corrección negativa por atmósfera.
                                    * *Fuente:* Tabla C (Pág. 387 Almanaque Náutico).
                                    """)

                        st.markdown("**C) Resolución Triángulo Posición**")
                        
                        tri = calculos.resolver_triangulo_posicion(obs['LatEst'], obs['LonEst'], gha_est, dec)
                        hc = tri['AltSolEst']
                        det = (hv - hc) * 60.0
                        obs.update({'Azimut': tri['Azimut'], 'Determinante': det})
                        resultados.append(obs)

                        val_lat  = f"{obs['LatEst']:.2f}"
                        val_dec  = f"{dec:.2f}"
                        val_P    = f"{tri['AngPol']:.2f}"
                        val_hc   = f"{hc:.2f}"
                        val_ghaA = f"{gha_aries:.2f}"
                        val_sha  = f"{sha_aprox:.2f}"
                        val_lon  = f"{obs['LonEst']:.2f}"

                        gha_star_total = (gha_aries + sha_aprox) % 360.0
                        lha_calc = (gha_star_total + obs['LonEst']) % 360.0
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.caption("Cálculo del Ángulo en el Polo:")
                        
                        if es_planeta:
                            label_gha = f"hG_{{{obs['Nombre']}}}" 
                        else:
                            label_gha = "hG_*"
                        
                        st.latex(rf"{label_gha} = {gha_est:.2f}^\circ")
                        
                        st.latex(rf"hL = ({label_gha} + \lambda)")
                        
                        lha_calc = (gha_est + obs['LonEst']) % 360.0
                        st.latex(rf"\mathbf{{hL}} = ({gha_est:.2f}^\circ + ({val_lon}^\circ)) = {lha_calc:.2f}^\circ")
                        
                        if lha_calc > 180:
                            if es_pdf:
                                st.latex(r"\text{Astro al \textbf{ESTE} del observador:}")
                            else:
                                st.markdown("Astro al **ESTE** del observador:")
                            st.latex(r"P = hL - 360^\circ")
                            st.latex(rf"\mathbf{{P}} = {lha_calc:.2f}^\circ - 360^\circ = \mathbf{{{tri['AngPol']:.2f}^\circ}}")
                        else:
                            if es_pdf:
                                st.latex(r"\text{Astro al \textbf{OESTE} del observador:}")
                            else:
                                st.markdown("Astro al **OESTE** del observador:")
                            st.latex(r"P = hL")
                            st.latex(rf"\mathbf{{P = {lha_calc:.2f}^\circ}}")
                        if not es_pdf:
                            st.markdown("---")

                        st.caption("Cálculo de Altura Calculada:")
                        st.latex(r"\sin(h_c) = \sin(\varphi)\sin(\delta) + \cos(\varphi)\cos(\delta)\cos(P)")
                        st.latex(rf"\sin(h_c) = \sin({val_lat}^\circ)\sin({val_dec}^\circ) + \cos({val_lat}^\circ)\cos({val_dec}^\circ)\cos({val_P}^\circ)")
                        txt_hc = fmt_gms(hc)
                        st.latex(rf"\mathbf{{h_c = {txt_hc}}} \quad ({val_hc}^\circ)")

                        if not es_pdf:
                            st.markdown("---")
                        
                        st.caption("Cálculo de Azimut:")
                        z_intermedio = tri.get('AziAst_Base', tri['Azimut'])
                        z_final = tri['Azimut']
                        st.latex(r"\cos(Z) = \frac{\sin(\delta) - \sin(\varphi)\sin(h_c)}{\cos(\varphi)\cos(h_c)}")
                        st.latex(rf"\cos(Z) = \frac{{\sin({val_dec}^\circ) - \sin({val_lat}^\circ)\sin({val_hc}^\circ)}}{{\cos({val_lat}^\circ)\cos({val_hc}^\circ)}}")
                        st.latex(rf"Z = {z_intermedio:.1f}^\circ")
                        
                        if abs(z_final - z_intermedio) < 0.1:
                            st.latex(r"\text{Astro al Este del observador}")
                            st.latex(rf"\mathbf{{Z_v = {z_final:.1f}^\circ}}")
                        else:
                            st.latex(r"\text{Astro al Oeste del observador}")
                            st.latex(rf"\mathbf{{Z_v = 360^\circ - {z_intermedio:.1f}^\circ = {z_final:.1f}^\circ}}")

                        if not es_pdf:
                            with st.expander("Definiciones y fuentes"):
                                st.markdown(f"""
                                * **$\\varphi$ (Latitud Estimada):** Coordenada vertical de nuestra posición supuesta.
                                * **$\\lambda$ (Longitud Estimada):** Coordenada horizontal de nuestra posición supuesta.
                                * **$\\delta$ (Declinación):** Es el ángulo desde el ecuador hasta la proyección del astro en la Tierra. Equivale a una Latitud.
                                    * *Fuente:* Páginas Diarias (Pág. {num_pag} Almanaque Náutico).
                                * **$hL$ (Ángulo Horario Local):** Ángulo medido hacia el Oeste desde nuestro meridiano hasta el meridiano del astro ($hG + \lambda$).
                                * **$P$ (Ángulo en el Polo):** Ángulo formado en el Polo entre tu meridiano y el meridiano del astro.
                                * **$h_c$ (Altura Calculada):** La altura teórica exacta que tendría el astro si estuviéramos en la situación de estima.
                                * **$Z$ (Azimut):** La demora a la que se encuentra el astro desde nuestra posición.
                                """)

                        st.markdown("**D) Resultados Finales**")
                        txt_res = f"{det:+.2f}'"
                        st.latex(rf"\Delta h = h_v - h_c = {txt_hv} - {txt_hc} = \mathbf{{{txt_res}}}")

                        if es_pdf:
                            st.write(f"- **Determinante:** {det:+.2f}'")
                            st.write(f"- **Azimut:** {tri['Azimut']:.1f}º")
                        else:
                            st.markdown(f"""
                            <div class="info-card-green">
                            <span class="card-label">RESULTADOS (Determinante | Azimut)</span>
                            <span class="card-value">{det:+.2f}' &nbsp;&nbsp;|&nbsp;&nbsp; {tri['Azimut']:.1f}º</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if not es_pdf:
                            with st.expander("Ver Triángulo de Posición 3D (Esfera)", expanded=False):
                                try:
                                    loc = locals()
                                    
                                    sha_val = loc.get('sha_est', loc.get('sha_aprox', None))
                                    
                                    gha_aries_val = loc.get('gha_aries', None)
                                    
                                    fig_tri = graficas.dibujar_triangulo_posicion_3d(
                                        obs['LatEst'], obs['LonEst'], dec, gha_est, obs['Nombre'], 
                                        gha_aries=gha_aries_val, sha_astro=sha_val
                                    )
                                    st.plotly_chart(fig_tri, use_container_width=True, key=f"tri_3d_{obs.get('id', i)}")
                                except Exception as e:
                                    st.error(f"Error gráfico 3D: {e}")


        st.markdown("---")
        if not es_pdf:
            st.header("Solución gráfica")

        if len(resultados) >= 2:
            calcular_final = es_pdf or st.button("CALCULAR POSICIÓN FINAL", type="primary", use_container_width=True)
            if calcular_final:
                df_res = pd.DataFrame(resultados)
                if not df_res.empty:
                    df_res = df_res.drop_duplicates(subset=['Nombre'], keep='last')
                    resultados_limpios = df_res.to_dict('records')
                else:
                    resultados_limpios = []

                c_g, c_d = st.columns([2, 1])
                
                with c_g:
                    try:
                        lat, lon = graficas.dibujar_situacion_estrellas(resultados_limpios)
                        st.pyplot(plt.gcf())
                    except Exception as e:
                        st.error(f"Error Gráfico: {e}")
                        lat = None

                with c_d:
                    if lat:
                        st.markdown("### Situación Corregida")
                        l = decimal_a_dms_cardinal(lat, True)
                        L = decimal_a_dms_cardinal(lon, False)

                        if es_pdf:
                            st.write(f"- **Latitud Verdadera:** {l}")
                            st.write(f"- **Longitud Verdadera:** {L}")
                        
                        else:
                        
                            st.markdown(f"""
                            <div class='info-card-green'>
                                <span class='card-label'>LATITUD</span>
                                <span class='card-value'>{l}</span>
                            </div>
                            <div class='info-card-green'>
                                <span class='card-label'>LONGITUD</span>
                                <span class='card-value'>{L}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        dLat = (lat - lat_general) 
                        dLon = (lon - lon_general) 
                        
                        dLat_str = decimal_a_dms_cardinal(dLat, True)
                        dLon_str = decimal_a_dms_cardinal(dLon, False)

                        st.markdown("### Corrección a la Estima")
                        if es_pdf:
                            st.write(f"- **Diferencia Latitud:** {dLat_str}")
                            st.write(f"- **Diferencia Longitud:** {dLon_str}")
                        else:
                            st.markdown(f"""
                            <div class='info-card-secondary'>
                                <span class='card-label'>DIFERENCIA LATITUD</span>
                                <span class='card-value card-value-small'>{dLat_str}</span>
                            </div>
                            <div class='info-card-secondary'>
                                <span class='card-label'>DIFERENCIA LONGITUD</span>
                                <span class='card-value card-value-small'>{dLon_str}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("### Tabla Resumen")
                        if es_pdf:
                            tabla_md = "| Nombre | Azimut | Determinante |\n|---|---|---|\n"
                            for _, row in df_res.iterrows():
                                tabla_md += f"| {row['Nombre']} | {row['Azimut']:.1f}º | {row['Determinante']:+.2f}' |\n"
                            st.markdown(tabla_md)
                        else:
                            st.table(df_res[['Nombre', 'Azimut', 'Determinante']].style.format({
                                'Azimut': '{:.1f}º',
                                'Determinante': '{:+.2f}'
                            }))

        if len(resultados) > 0 and not es_pdf:
            st.markdown("---")
            st.subheader("📂 Guardar Observación de Astros")
            c_name_e, c_btn_e = st.columns([3, 1])
            nombre_real = c_name_e.text_input("Nombre", placeholder="Ej: Crepúsculo Vespertino", key="save_est_input")
            
            c_btn_e.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if c_btn_e.button("Guardar", key="btn_save_est"):

                nm_1 = st.session_state.get("est_nm_1", 1); nm_2 = st.session_state.get("est_nm_2", 1); nm_3 = st.session_state.get("est_nm_3", 1)
                datos_a_guardar = {}
                for k, v in st.session_state.items():
                    if "btn_" in k or "tri_3d" in k or k == "mensaje_flash": continue
                    parts = k.split('_')
                    if len(parts) >= 3 and parts[-1].isdigit():
                        idx = int(parts[-1]); id_astro = parts[-2]
                        if id_astro == '1' and idx >= nm_1: continue
                        if id_astro == '2' and idx >= nm_2: continue
                        if id_astro == '3' and idx >= nm_3: continue
                    datos_a_guardar[k] = v
                
                ok, msg = memoria.guardar_ejercicio(nombre_real, datos_a_guardar, "estrellas")
                
                if ok:
                    st.session_state["mensaje_flash"] = msg
                    st.rerun()
                else:
                    st.error(msg)              
        else:
            if not es_pdf:
                st.info("Rellena y depura al menos 2 estrellas para ver la solución gráfica.")
     
    elif herramienta_estrellas == "mono":
        es_pdf = st.session_state.get("orden_imprimir_pdf", False)
        if es_pdf:
            st.markdown("""
            <div style='text-align: center;'>
                <h2><u>MONO DE ASTROS</u></h2>
                <h3><u>OBSERVACIÓN DE ESTRELLAS Y PLANETAS</u></h3>
            </div>
            <br>
            """, unsafe_allow_html=True)
            st.markdown("#### <u>1. Datos de Observación</u>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="hero-container" style="filter: hue-rotate(220deg) brightness(0.8);">
                <div class="hero-overlay">
                    <div class="hero-title">MONO DE ASTROS</div>
                    <div class="hero-subtitle">OBSERVACIÓN DE ESTRELLAS Y PLANETAS</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
            st.markdown("""
                    <style>
                    div[data-testid="stDateInput"] input { text-align: center; }
                    </style>
                """, unsafe_allow_html=True)
            
            st.markdown("### 1. Datos de Observación")
        
        if not es_pdf:
            c_f, c_h = st.columns(2)
            with c_f:
                st.markdown("**Fecha de la Observación**")
                fecha_mono = st.date_input("Fecha", key="mono_fecha", label_visibility="collapsed")
            with c_h:
                st.markdown("**Hora UTC (H : M : S)**")
                ch1, ch2, ch3 = st.columns(3)
                if "mo_h_h" not in st.session_state: st.session_state["mo_h_h"] = 0
                if "mo_h_m" not in st.session_state: st.session_state["mo_h_m"] = 0
                if "mo_h_s" not in st.session_state: st.session_state["mo_h_s"] = 0
                
                with ch1: h_h = st.number_input("Hora", 0, 23, key="mo_h_h", label_visibility="collapsed")
                with ch2: h_m = st.number_input("Min", 0, 59, key="mo_h_m", label_visibility="collapsed")
                with ch3: h_s = st.number_input("Seg", 0, 59, key="mo_h_s", label_visibility="collapsed")
            
            st.markdown("---")
            
            c_lat, c_lon = st.columns(2)
            with c_lat:
                lat_decimal = input_coord_dms("Latitud Estimada", "mono_lat", tipo="lat", def_g=0, def_card="N")
                
            with c_lon:
                lon_decimal = input_coord_dms("Longitud Estimada", "mono_lon", tipo="lon", def_g=0, def_card="W")

            st.markdown("<br>", unsafe_allow_html=True)
            btn_calcular_mono = st.button("🔭 Generar Mapa Celeste", type="primary", use_container_width=True)
        
        else:
            btn_calcular_mono = False
            fecha_mono = st.session_state.get("mono_fecha", datetime.date.today())
            h_h = st.session_state.get("mo_h_h", 12)
            h_m = st.session_state.get("mo_h_m", 0)
            h_s = st.session_state.get("mo_h_s", 0)
            
            g_lat = st.session_state.get("mono_lat_g", 35)
            m_lat = st.session_state.get("mono_lat_m", 0)
            s_lat = st.session_state.get("mono_lat_s", 0.0)
            c_lat = st.session_state.get("mono_lat_c", "N")
            
            g_lon = st.session_state.get("mono_lon_g", 40)
            m_lon = st.session_state.get("mono_lon_m", 0)
            s_lon = st.session_state.get("mono_lon_s", 0.0)
            c_lon = st.session_state.get("mono_lon_c", "W")
            
            lat_decimal = dms_a_decimal(g_lat, m_lat, s_lat, c_lat)
            lon_decimal = dms_a_decimal(g_lon, m_lon, s_lon, c_lon)
            
            col_pdf_datos, col_pdf_coord = st.columns(2)
            with col_pdf_datos:
                st.write(f"- **Fecha:** {fecha_mono.strftime('%d/%m/%Y')}")
                st.write(f"- **Hora UTC:** {h_h:02d}:{h_m:02d}:{h_s:02d}")
            with col_pdf_coord:
                st.write(f"- **Latitud:** {g_lat}º {m_lat}' {s_lat}'' {c_lat}")
                st.write(f"- **Longitud:** {g_lon}º {m_lon}' {s_lon}'' {c_lon}")
            
            st.markdown("---")
    
        if es_pdf or btn_calcular_mono:

            hora_mono = datetime.time(h_h, h_m, h_s)
            
            with st.spinner("Resolviendo triángulos de posición..."):
                mis_astros = calcular_astros_visibles(fecha_mono, hora_mono, lat_decimal, lon_decimal)
            
            if mis_astros:
                mis_astros = sorted(mis_astros, key=lambda x: x['nombre'])
                
                for i, astro in enumerate(mis_astros, start=1):
                    astro['numero'] = i
                    
                st.session_state["mono_resultados"] = mis_astros
            else:
                st.session_state["mono_resultados"] = []

        if "mono_resultados" in st.session_state and st.session_state["mono_resultados"]:
            mis_astros = st.session_state["mono_resultados"]
            
            if not es_pdf:
                st.success(f"Se han identificado {len(mis_astros)} astros sobre el horizonte.")
                
                col_mapa, col_tabla = st.columns([1.3, 1], gap="medium")
                
                with col_mapa:
                    modo_etiq = st.radio("Mostrar etiquetas como:", ["Nombres", "Números"], horizontal=True)
                    fig_mapa = dibujar_mono_astros(mis_astros, modo_etiq)
                    st.pyplot(fig_mapa)
                    
                with col_tabla:
                    st.markdown("#### Catálogo de Visibilidad")
                    df_astros = pd.DataFrame(mis_astros)
                    df_astros = df_astros[["numero", "nombre", "azimut", "altura"]]
                    df_astros.columns = ["Nº", "Astro", "Azimut (Zv)", "Altura (Hc)"]
                    
                    def formato_grados_minutos(decimal_deg):
                        try:
                            val = float(decimal_deg)
                            g = int(val)
                            m = (val - g) * 60
                            return f"{g}º {m:04.1f}'"
                        except:
                            return f"{decimal_deg}º"
                    
                    df_astros["Altura (Hc)"] = df_astros["Altura (Hc)"].apply(formato_grados_minutos)
                    df_astros["Azimut (Zv)"] = df_astros["Azimut (Zv)"].apply(lambda x: f"{float(x):.1f}º" if pd.notnull(x) else "")
                    
                    st.dataframe(df_astros, use_container_width=True, hide_index=True, height=500)
            
            else:
                st.markdown("#### <u>2. Catálogo de Visibilidad</u>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                
                def formato_grados_minutos_pdf(decimal_deg):
                    try:
                        val = float(decimal_deg)
                        g = int(val)
                        m = (val - g) * 60
                        return f"{g}º {m:04.1f}'"
                    except:
                        return f"{decimal_deg}º"
                
                html_c1 = "<table style='width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.7em;'>"
                html_c2 = "<table style='width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.7em;'>"
                
                mitad = (len(mis_astros) + 1) // 2
                
                for i, astro in enumerate(mis_astros):
                    hc_str = formato_grados_minutos_pdf(astro['altura'])
                    zv_str = f"{float(astro['azimut']):.1f}º" if pd.notnull(astro['azimut']) else ""
                    
                    fila_html = f"<tr><td style='width: 38%; padding: 2px 0px; border: none; white-space: nowrap;'><b>{astro['numero']}. {astro['nombre']}</b></td><td style='width: 32%; padding: 2px 4px; border: none; white-space: nowrap; color: #333;'> Zv: {zv_str}</td><td style='width: 30%; padding: 2px 0px; border: none; white-space: nowrap; color: #333;'> Hc: {hc_str}</td></tr>"
                    
                    if i < mitad:
                        html_c1 += fila_html
                    else:
                        html_c2 += fila_html
                        
                html_c1 += "</table>"
                html_c2 += "</table>"
                
                with c1:
                    st.markdown(html_c1, unsafe_allow_html=True)
                with c2:
                    st.markdown(html_c2, unsafe_allow_html=True)

                st.markdown("<div style='page-break-before: always;'></div>", unsafe_allow_html=True)
                
                st.markdown("#### <u>3. Mapas Celestes</u>", unsafe_allow_html=True)
                
                fig_mapa_num = dibujar_mono_astros(mis_astros, "Números")
                st.pyplot(fig_mapa_num)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                fig_mapa_nom = dibujar_mono_astros(mis_astros, "Nombres")
                st.pyplot(fig_mapa_nom)

        elif btn_calcular_mono:
            st.warning("⚠️ No se han encontrado astros visibles o faltan datos en el Almanaque para esa fecha.")
        
        if not es_pdf:
            st.markdown("---")
            st.subheader("📂 Guardar Mono de Astros")
            
            c_name_m, c_btn_m = st.columns([3, 1])
            nombre_real = c_name_m.text_input("Nombre", placeholder="Ej: Cielo del Estrecho", key="save_mono_input")
            c_btn_m.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            
            if c_btn_m.button("Guardar", key="btn_save_mono"):
                datos_a_guardar = {}
                for k, v in st.session_state.items():
                    if "btn_" in k or "tri_3d" in k or k == "mensaje_flash" or k == "mono_resultados": 
                        continue
                    
                    datos_a_guardar[k] = v
                
                ok, msg = memoria.guardar_ejercicio(nombre_real, datos_a_guardar, "mono")
                
                if ok:
                    st.session_state["mensaje_flash"] = msg
                    st.rerun()
                else:
                    st.error(msg)

if st.session_state.get("orden_imprimir_pdf", False):
    import streamlit.components.v1 as components
    components.html("""
        <script>
            setTimeout(function() {
                window.parent.print();
            }, 1000); 
        </script>
    """, height=0, width=0)
    
    st.session_state["orden_imprimir_pdf"] = False
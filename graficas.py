import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.ticker as ticker
import math
import numpy as np
from itertools import combinations
import plotly.graph_objects as go

def calcular_punto_determinante(lat_est, lon_est, azimut, determinante):
    rad_az = math.radians(azimut)
    dx = determinante * math.sin(rad_az)
    dy = determinante * math.cos(rad_az)
    return dx, dy

def resolver_cruce_rectas(p1, z1, p2, z2):
    try:
        rad_z1 = math.radians(z1); rad_z2 = math.radians(z2)
        A1 = math.sin(rad_z1); B1 = math.cos(rad_z1); C1 = A1 * p1[0] + B1 * p1[1]
        A2 = math.sin(rad_z2); B2 = math.cos(rad_z2); C2 = A2 * p2[0] + B2 * p2[1]
        
        det = A1*B2 - A2*B1
        if abs(det) < 1e-9: return None
        
        return (C1*B2 - C2*B1)/det, (A1*C2 - A2*C1)/det
    except:
        return None

def ajustar_zoom_dinamico(ax, x_vals, y_vals, margen_pct=0.15):
    if not x_vals or not y_vals: return
    min_x, max_x = min(x_vals), max(x_vals)
    min_y, max_y = min(y_vals), max(y_vals)
    rango_x = max_x - min_x
    rango_y = max_y - min_y
    centro_x = (max_x + min_x) / 2.0
    centro_y = (max_y + min_y) / 2.0
    max_span = max(rango_x, rango_y, 5.0)
    radio_vista = (max_span / 2.0) * (1 + margen_pct)
    ax.set_xlim(centro_x - radio_vista, centro_x + radio_vista)
    ax.set_ylim(centro_y - radio_vista, centro_y + radio_vista)

def pintar_recta(ax, p_det, azimut, color, estilo, label, longitud=30, grosor=1.0):
    rad_z = math.radians(azimut)
    vx = math.cos(rad_z); vy = -math.sin(rad_z)
    x1 = p_det[0] - vx * longitud; y1 = p_det[1] - vy * longitud
    x2 = p_det[0] + vx * longitud; y2 = p_det[1] + vy * longitud
    ax.plot([x1, x2], [y1, y2], color=color, linestyle=estilo, linewidth=grosor, label='_nolegend_')
    return [x1, x2], [y1, y2]

def formato_coord(valor, es_lat):
    signo = 1
    if valor < 0:
        signo = -1
        valor = abs(valor)
    grad = int(valor)
    minutos = (valor - grad) * 60.0
    card = ""
    if es_lat: card = "N" if signo > 0 else "S"
    else: card = "E" if signo > 0 else "W"
    return f"{grad}º {minutos:.1f}' {card}"

def anadir_marca_paralela(ax, x, y, azimut, color):
    """
    Dibuja '//' en las coordenadas (x,y) rotado según la recta.
    """
    rotacion = (90 - azimut)
    
    ax.text(x, y, '//', ha='center', va='center', rotation=rotacion,
            color=color, fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0', fc='white', ec='none', alpha=0.7),
            zorder=20)

def calcular_posicion_marca_optima(center, fix, azimut, longitud):
    """
    Calcula una posición para la marca que esté en el lado CONTRARIO al Fix.
    """
    cx, cy = center
    rad_z = math.radians(azimut)
    
    vx_lop = math.cos(rad_z)
    vy_lop = -math.sin(rad_z)
    
    if not fix:
        return cx + vx_lop * (longitud * 0.5), cy + vy_lop * (longitud * 0.5)
    
    fx, fy = fix
    
    vec_to_fix_x = fx - cx
    vec_to_fix_y = fy - cy
    
    dot_product = (vx_lop * vec_to_fix_x) + (vy_lop * vec_to_fix_y)
    
    distancia_marca = longitud * 0.6
    
    if dot_product >= 0:
        mx = cx - vx_lop * distancia_marca
        my = cy - vy_lop * distancia_marca
    else:
        mx = cx + vx_lop * distancia_marca
        my = cy + vy_lop * distancia_marca
        
    return mx, my

def dibujar_situacion(obs1, obs2):
    fig, ax = plt.subplots(figsize=(10, 10)) 
    font_titulo = {'family': 'serif', 'color': '#333333', 'weight': 'bold', 'size': 14}
    ax.set_title("Situación Corregida", fontdict=font_titulo, pad=15)
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.set_aspect('equal')
    ax.set_xlabel("Longitud", fontsize=9); ax.set_ylabel("Latitud", fontsize=9)
    ax.tick_params(axis='x', rotation=45, labelsize=8); ax.tick_params(axis='y', labelsize=8)

    center_lat = obs2['LatEst']
    center_lon = obs2['LonEst']
    cos_lat = math.cos(math.radians(center_lat))

    def format_y(x, pos): return formato_coord(center_lat + (x / 60.0), True)
    def format_x(x, pos): return formato_coord(center_lon + (x / (60.0 * cos_lat)), False)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_y))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_x))

    todos_x = []; todos_y = []
    
    pos_est2 = (0, 0) 
    dLat_millas = (obs1['LatEst'] - center_lat) * 60.0
    dLon_millas = (obs1['LonEst'] - center_lon) * 60.0 * cos_lat
    pos_est1 = (dLon_millas, dLat_millas)

    dx1, dy1 = calcular_punto_determinante(0, 0, obs1['Azimut'], obs1['Determinante'])
    p_det1_orig = (pos_est1[0] + dx1, pos_est1[1] + dy1) 
    p_det1_trans = (dx1, dy1)                            
    
    dx2, dy2 = calcular_punto_determinante(0, 0, obs2['Azimut'], obs2['Determinante'])
    p_det2 = (dx2, dy2)

    cruce = resolver_cruce_rectas(p_det1_trans, obs1['Azimut'], p_det2, obs2['Azimut'])
    
    len_r1 = 40; len_r2 = 40
    punto_lat = None; punto_lon = None

    if cruce:
        cx, cy = cruce
        dist_1 = math.sqrt((cx - p_det1_trans[0])**2 + (cy - p_det1_trans[1])**2)
        dist_2 = math.sqrt((cx - p_det2[0])**2 + (cy - p_det2[1])**2)
        len_r1 = max(40, dist_1 * 1.3)
        len_r2 = max(40, dist_2 * 1.3)
        punto_lat = center_lat + (cy / 60.0)
        punto_lon = center_lon + (cx / (60.0 * cos_lat))
        todos_x.append(cx); todos_y.append(cy)

    ax.plot(pos_est1[0], pos_est1[1], marker='+', color='gray', markersize=12, markeredgewidth=1.5, zorder=5)
    ax.plot(pos_est2[0], pos_est2[1], marker='+', color='black', markersize=14, markeredgewidth=2, zorder=5)
    ax.annotate("", xy=pos_est2, xytext=pos_est1, arrowprops=dict(arrowstyle="->", linestyle="--", color="gray", alpha=0.5))
    todos_x.extend([pos_est1[0], pos_est2[0]]); todos_y.extend([pos_est1[1], pos_est2[1]])

    ax.arrow(pos_est1[0], pos_est1[1], dx1, dy1, head_width=0.3, color='gray', length_includes_head=True, alpha=0.4)
    lx, ly = pintar_recta(ax, p_det1_orig, obs1['Azimut'], 'gray', ':', None, len_r1, grosor=1.0)
    todos_x.extend(lx); todos_y.extend(ly)
    
    mx1_orig, my1_orig = calcular_posicion_marca_optima(p_det1_orig, 
                                                        (p_det1_orig[0] + (cruce[0]-p_det1_trans[0]), p_det1_orig[1] + (cruce[1]-p_det1_trans[1])) if cruce else None, 
                                                        obs1['Azimut'], len_r1)
    anadir_marca_paralela(ax, mx1_orig, my1_orig, obs1['Azimut'], 'gray')

    ax.annotate("", xy=p_det1_trans, xytext=p_det1_orig, arrowprops=dict(arrowstyle="->", linestyle="--", color="gray", alpha=0.5))

    ax.arrow(0, 0, dx1, dy1, head_width=0.3, color='blue', length_includes_head=True)
    lx, ly = pintar_recta(ax, p_det1_trans, obs1['Azimut'], 'blue', '--', None, len_r1, grosor=1.0)
    todos_x.extend(lx); todos_y.extend(ly)
    
    mx1_trans, my1_trans = calcular_posicion_marca_optima(p_det1_trans, cruce, obs1['Azimut'], len_r1)
    anadir_marca_paralela(ax, mx1_trans, my1_trans, obs1['Azimut'], 'blue')

    ax.arrow(0, 0, dx2, dy2, head_width=0.3, color='green', length_includes_head=True)
    lx, ly = pintar_recta(ax, p_det2, obs2['Azimut'], 'green', '--', None, len_r2, grosor=1.0)
    todos_x.extend(lx); todos_y.extend(ly)

    if cruce:
        ax.plot(cruce[0], cruce[1], marker='o', color='red', markersize=8, markeredgecolor='black', zorder=10)

    def format_coord_local(val, is_lat):
        v = abs(val)
        g = int(v)
        m = int((v - g) * 60)
        s = (v - g - m/60.0) * 3600
        letra = "N" if is_lat and val >= 0 else "S" if is_lat else "E" if val >= 0 else "W"
        return f"{g}º {m:02d}' {s:04.1f}'' {letra}"

    estilo_caja = dict(boxstyle="round,pad=0.4", facecolor='white', alpha=0.9, edgecolor='#cccccc')
    
    estilo_flecha = dict(arrowstyle="->", connectionstyle="arc3,rad=0.1", color="#666666", alpha=0.5, lw=0.5)

    box_min_x = min(todos_x); box_max_x = max(todos_x)
    box_min_y = min(todos_y); box_max_y = max(todos_y)
    ancho_caja = box_max_x - box_min_x
    alto_caja = box_max_y - box_min_y

    texto_e1 = f"Estima 1:\n{format_coord_local(obs1['LatEst'], True)}\n{format_coord_local(obs1['LonEst'], False)}"
    texto_e2 = f"Estima 2:\n{format_coord_local(obs2['LatEst'], True)}\n{format_coord_local(obs2['LonEst'], False)}"
    texto_r1 = f"Recta 1:\nZ = {obs1['Azimut']:.1f}º\nDet = {obs1['Determinante']:+.1f}'"
    texto_r2 = f"Recta 2:\nZ = {obs2['Azimut']:.1f}º\nDet = {obs2['Determinante']:+.1f}'"

    if cruce:
        texto_verdadera = f"Situación Verdadera:\n{format_coord_local(punto_lat, True)}\n{format_coord_local(punto_lon, False)}"
        ax.annotate(texto_verdadera, xy=(cx, cy), xytext=(cx, box_max_y), 
                    color='red', fontsize=8, ha='center', va='bottom', fontweight='bold', 
                    bbox=estilo_caja, arrowprops=estilo_flecha, zorder=30)

    ax.annotate(texto_r1, xy=(dx1/2.0, dy1/2.0), xytext=(box_min_x, dy1/2.0), 
                color='blue', fontsize=8, ha='right', va='center', fontweight='bold', 
                bbox=estilo_caja, arrowprops=estilo_flecha, zorder=30)

    ax.annotate(texto_r2, xy=(dx2/2.0, dy2/2.0), xytext=(box_max_x, dy2/2.0), 
                color='green', fontsize=8, ha='left', va='center', fontweight='bold', 
                bbox=estilo_caja, arrowprops=estilo_flecha, zorder=30)

    x_e2 = box_min_x + (ancho_caja * 0.25)
    ax.annotate(texto_e2, xy=(0, 0), xytext=(x_e2, box_min_y), 
                color='black', fontsize=8, ha='center', va='top', fontweight='bold', 
                bbox=estilo_caja, arrowprops=estilo_flecha, zorder=30)

    x_e1 = box_max_x - (ancho_caja * 0.25)
    ax.annotate(texto_e1, xy=pos_est1, xytext=(x_e1, box_min_y), 
                color='#555555', fontsize=8, ha='center', va='top', fontweight='bold', 
                bbox=estilo_caja, arrowprops=estilo_flecha, zorder=30)

    pad_x = ancho_caja * 0.25
    pad_y = alto_caja * 0.15
    todos_x.extend([box_min_x - pad_x, box_max_x + pad_x])
    todos_y.extend([box_min_y - pad_y, box_max_y + pad_y])
    h_est1 = mlines.Line2D([], [], color='gray', marker='+', linestyle='None', markersize=8, markeredgewidth=1.5, label='Estima 1ª Obs')
    h_est2 = mlines.Line2D([], [], color='black', marker='+', linestyle='None', markersize=10, markeredgewidth=2, label='Estima 2ª Obs')
    h_az1 = mlines.Line2D([], [], color='blue', linestyle='-', linewidth=1.5, label='Azimut 1ª Obs')
    h_az2 = mlines.Line2D([], [], color='green', linestyle='-', linewidth=1.5, label='Azimut 2ª Obs')
    h_ra1_orig = mlines.Line2D([], [], color='gray', linestyle=':', linewidth=1.0, label='R.A. 1ª Obs')
    h_ra1 = mlines.Line2D([], [], color='blue', linestyle='--', linewidth=1.0, label='R.A. 1ª Obs Trasladada')
    h_ra2 = mlines.Line2D([], [], color='green', linestyle='--', linewidth=1.0, label='R.A. 2ª Obs')
    h_sit = mlines.Line2D([], [], color='red', marker='o', linestyle='None', markeredgecolor='black', markersize=8, label='Situación Verdadera')

    handles = [h_est1, h_est2, h_az1, h_az2, h_ra1_orig, h_ra1, h_ra2, h_sit]
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize='small', frameon=True)

    ajustar_zoom_dinamico(ax, todos_x, todos_y)
    plt.tight_layout()
    
    return punto_lat, punto_lon

def dibujar_situacion_estrellas(lista_resultados):
    if len(lista_resultados) < 2: return None, None

    datos_unicos = {obs['Nombre']: obs for obs in lista_resultados}.values()
    lista_limpia = list(datos_unicos)

    latitudes_estima = [obs['LatEst'] for obs in lista_limpia]
    longitudes_estima = [obs['LonEst'] for obs in lista_limpia]
    
    lat_estima_media = sum(latitudes_estima) / len(latitudes_estima)
    lon_estima_media = sum(longitudes_estima) / len(longitudes_estima)
    
    cos_lat_estima = math.cos(math.radians(lat_estima_media))
    if abs(cos_lat_estima) < 1e-6: cos_lat_estima = 1e-6

    fig, ax = plt.subplots(figsize=(10, 10))
    font_titulo = {'family': 'serif', 'color':  '#2c3e50', 'weight': 'bold', 'size': 14}
    ax.set_title(f"Situación Corregida", fontdict=font_titulo, pad=15)
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.set_aspect('equal')
    
    ax.set_xlabel("Longitud", fontsize=9); ax.set_ylabel("Latitud", fontsize=9)
    ax.tick_params(axis='x', rotation=45, labelsize=8); ax.tick_params(axis='y', labelsize=8)

    def format_y(y_millas, pos): 
        return formato_coord(lat_estima_media + (y_millas/60.0), True)
    
    def format_x(x_millas_dep, pos): 
        return formato_coord(lon_estima_media + (x_millas_dep/(60.0*cos_lat_estima)), False)
        
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_y))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_x))

    todos_x = []; todos_y = []
    colores = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta']
    datos_rectas = []
    
    for i, obs in enumerate(lista_limpia):
        color = colores[i % len(colores)]
        
        dLat_millas = (obs['LatEst'] - lat_estima_media) * 60.0
        diff_lon = obs['LonEst'] - lon_estima_media
        if diff_lon > 180: diff_lon -= 360
        if diff_lon < -180: diff_lon += 360
        dLon_millas_dep = diff_lon * 60.0 * cos_lat_estima
        
        origen = (dLon_millas_dep, dLat_millas)
        dx, dy = calcular_punto_determinante(0, 0, obs['Azimut'], obs['Determinante'])
        p_det = (origen[0] + dx, origen[1] + dy)
        
        datos_rectas.append({
            'nombre': obs['Nombre'], 
            'color': color, 
            'origen': origen, 
            'p_det': p_det, 
            'azimut': obs['Azimut'],
            'det': obs['Determinante']
        })
        todos_x.extend([origen[0], p_det[0]]); todos_y.extend([origen[1], p_det[1]])

    cruces = []
    for i1, i2 in combinations(range(len(datos_rectas)), 2):
        r1 = datos_rectas[i1]; r2 = datos_rectas[i2]
        cruce = resolver_cruce_rectas(r1['p_det'], r1['azimut'], r2['p_det'], r2['azimut'])
        if cruce:
            cruces.append(cruce); todos_x.append(cruce[0]); todos_y.append(cruce[1])
            ax.plot(cruce[0], cruce[1], marker='+', color='gray', markersize=6, alpha=0.3)

    radio_accion = 10.0
    if todos_x: radio_accion = max(max(todos_x)-min(todos_x), max(todos_y)-min(todos_y), 5.0)
    
    for r in datos_rectas:
        ax.plot(r['origen'][0], r['origen'][1], marker='o', color=r['color'], markersize=4, alpha=0.6)
        ax.arrow(r['origen'][0], r['origen'][1], r['p_det'][0]-r['origen'][0], r['p_det'][1]-r['origen'][1], 
                 head_width=radio_accion*0.03, color=r['color'], length_includes_head=True, alpha=0.5)
        lx, ly = pintar_recta(ax, r['p_det'], r['azimut'], r['color'], '--', None, radio_accion*1.2, grosor=1.0)
        todos_x.extend(lx); todos_y.extend(ly)

    lat_final = None; lon_final = None
    
    if cruces:
        A_ls = np.array([
            [math.sin(math.radians(r['azimut'])), math.cos(math.radians(r['azimut']))]
            for r in datos_rectas
        ])
        b_ls = np.array([
            math.sin(math.radians(r['azimut'])) * r['p_det'][0] +
            math.cos(math.radians(r['azimut'])) * r['p_det'][1]
            for r in datos_rectas
        ])
        sol_ls, _, _, _ = np.linalg.lstsq(A_ls, b_ls, rcond=None)
        avg_x_dep, avg_y_millas = sol_ls[0], sol_ls[1]

        if len(cruces) >= 3: ax.add_patch(plt.Polygon(cruces, color='gold', alpha=0.2))
        ax.plot(avg_x_dep, avg_y_millas, marker='o', color='gold', markeredgecolor='black', markersize=10, zorder=15)

        lat_aprox = lat_estima_media + (avg_y_millas / 60.0)
        cos_lat_iter = math.cos(math.radians((lat_estima_media + lat_aprox) / 2.0))
        if abs(cos_lat_iter) < 1e-6: cos_lat_iter = 1e-6

        lat_final = lat_aprox
        lon_final = lon_estima_media + (avg_x_dep / (60.0 * cos_lat_iter))

        def format_coord_local(val, is_lat):
            v = abs(val)
            g = int(v)
            m = int((v - g) * 60)
            s = (v - g - m/60.0) * 3600
            letra = "N" if is_lat and val >= 0 else "S" if is_lat else "E" if val >= 0 else "W"
            return f"{g}º {m:02d}' {s:04.1f}'' {letra}"

        estilo_caja = dict(boxstyle="round,pad=0.4", facecolor='white', alpha=0.9, edgecolor='#cccccc')
        estilo_flecha = dict(arrowstyle="->", connectionstyle="arc3,rad=0.1", color="#666666", alpha=0.5, lw=0.5)

        box_min_x = min(todos_x); box_max_x = max(todos_x)
        box_min_y = min(todos_y); box_max_y = max(todos_y)
        ancho_caja = box_max_x - box_min_x
        alto_caja = box_max_y - box_min_y

        texto_verdadera = f"Situación Verdadera:\n{format_coord_local(lat_final, True)}\n{format_coord_local(lon_final, False)}"
        ax.annotate(texto_verdadera, xy=(avg_x_dep, avg_y_millas), xytext=(avg_x_dep, box_max_y), 
                    color='goldenrod', fontsize=8, ha='center', va='bottom', fontweight='bold', 
                    bbox=estilo_caja, arrowprops=estilo_flecha, zorder=30)

        texto_e = f"Situación Estimada:\n{format_coord_local(lat_estima_media, True)}\n{format_coord_local(lon_estima_media, False)}"
        ax.annotate(texto_e, xy=(0, 0), xytext=(0, box_min_y), 
                    color='black', fontsize=8, ha='center', va='top', fontweight='bold', 
                    bbox=estilo_caja, arrowprops=estilo_flecha, zorder=30)

        for r in datos_rectas:
            texto_r = f"{r['nombre']} :\nZ = {r['azimut']:.1f}º\nDet = {r['det']:+.1f}'"
            
            if r['p_det'][0] <= (box_min_x + box_max_x) / 2.0:
                x_pos = box_min_x
                ha_align = 'right'
            else:
                x_pos = box_max_x
                ha_align = 'left'

            ax.annotate(texto_r, xy=(r['p_det'][0], r['p_det'][1]), xytext=(x_pos, r['p_det'][1]), 
                        color=r['color'], fontsize=8, ha=ha_align, va='center', fontweight='bold', 
                        bbox=estilo_caja, arrowprops=estilo_flecha, zorder=30)

        pad_x = ancho_caja * 0.16 
        pad_y = alto_caja * 0.08
        todos_x.extend([box_min_x - pad_x, box_max_x + pad_x])
        todos_y.extend([box_min_y - pad_y, box_max_y + pad_y])

    ajustar_zoom_dinamico(ax, todos_x, todos_y)
    plt.tight_layout()
    
    return lat_final, lon_final

def dibujar_triangulo_posicion_3d(lat, lon, dec, gha_astro, nombre_astro, gha_aries=None, sha_astro=None):
    """
    Dibuja la esfera celeste con:
    - Ecuador/Greenwich: Rojo Oscuro Discontinuo.
    - Co-Latitud/Meridiano Local: Azul Marino SÓLIDO.
    - Co-Declinación/Meridiano Astro: Verde Oscuro SÓLIDO.
    - Leyenda: Situada abajo horizontalmente para no tapar.
    - Emoji estrella: Normal (⭐️).
    """
    
    phi = np.radians(lat)
    delta = np.radians(dec)
    rad_lon = np.radians(lon) 
    rad_gha = np.radians(-gha_astro)
    
    P_vec = np.array([0, 0, 1]) # Polo Norte
    
    Z_vec = np.array([
        np.cos(phi) * np.cos(rad_lon),
        np.cos(phi) * np.sin(rad_lon),
        np.sin(phi)
    ])
    
    A_vec = np.array([
        np.cos(delta) * np.cos(rad_gha),
        np.cos(delta) * np.sin(rad_gha),
        np.sin(delta)
    ])
    
    def get_arc(p1, p2, n=50):
        t = np.linspace(0, 1, n)
        pts = []
        for x in t:
            p = (1-x)*p1 + x*p2
            norm = np.linalg.norm(p)
            if norm > 0: p = p / norm
            pts.append(p)
        return np.array(pts).T

    def get_meridian(angle_rad, color, width=2, dash='solid', name="Meridiano"):
        theta = np.linspace(-np.pi/2, np.pi/2, 60)
        x = np.cos(theta) * np.cos(angle_rad)
        y = np.cos(theta) * np.sin(angle_rad)
        z = np.sin(theta)
        return go.Scatter3d(
            x=x, y=y, z=z, 
            mode='lines', 
            line=dict(color=color, width=width, dash=dash), 
            name=name, hoverinfo='skip'
        )

    fig = go.Figure()

    u, v = np.mgrid[0:2*np.pi:60j, 0:np.pi:30j]
    x_s = np.cos(u)*np.sin(v); y_s = np.sin(u)*np.sin(v); z_s = np.cos(v)
    
    fig.add_trace(go.Surface(
        x=x_s, y=y_s, z=z_s, 
        opacity=0.05, showscale=False, colorscale='Blues', 
        hoverinfo='skip'
    ))

    t_eq = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter3d(
        x=np.cos(t_eq), y=np.sin(t_eq), z=np.zeros_like(t_eq), 
        mode='lines', line=dict(color='darkred', width=2, dash='dash'), 
        name='Ecuador', hoverinfo='skip'
    ))
    
    fig.add_trace(get_meridian(0, 'darkred', width=2, dash='dash', name='Meridiano Greenwich'))
    
    fig.add_trace(get_meridian(rad_lon, 'navy', width=3, dash='solid', name='Tu Meridiano'))

    fig.add_trace(get_meridian(rad_gha, 'darkgreen', width=3, dash='solid', name=f'Meridiano {nombre_astro}'))

    arc_pz = get_arc(P_vec, Z_vec)
    arc_pa = get_arc(P_vec, A_vec)
    arc_za = get_arc(Z_vec, A_vec)

    fig.add_trace(go.Scatter3d(
        x=arc_pz[0], y=arc_pz[1], z=arc_pz[2], 
        mode='lines', line=dict(color='navy', width=8), 
        name='Co-Latitud', hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter3d(
        x=arc_pa[0], y=arc_pa[1], z=arc_pa[2], 
        mode='lines', line=dict(color='darkgreen', width=8), 
        name='Co-Declinación', hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter3d(
        x=arc_za[0], y=arc_za[1], z=arc_za[2], 
        mode='lines', line=dict(color='darkred', width=6), 
        name='Dist. Cenital', hoverinfo='skip'
    ))

    start_vec = Z_vec * 0.15 + P_vec * 0.85
    end_vec   = A_vec * 0.15 + P_vec * 0.85
    arc_angle = get_arc(start_vec, end_vec, n=15)
    
    pts_fill_x = [0] + list(arc_angle[0]) + [0]
    pts_fill_y = [0] + list(arc_angle[1]) + [0]
    pts_fill_z = [1] + list(arc_angle[2]) + [1]

    fig.add_trace(go.Mesh3d(
        x=pts_fill_x, y=pts_fill_y, z=pts_fill_z,
        color='gold', opacity=0.6, name='Ángulo P', hoverinfo='skip'
    ))

    nombre_limpio = nombre_astro.lower().strip()
    
    emoji_astro = "⭐️" 
    if "sol" in nombre_limpio: emoji_astro = "☀️"
    elif "venus" in nombre_limpio: emoji_astro = "🪐"
    elif "marte" in nombre_limpio: emoji_astro = "🪐"
    elif "jupiter" in nombre_limpio: emoji_astro = "🪐"
    elif "saturno" in nombre_limpio: emoji_astro = "🪐"
    elif "luna" in nombre_limpio: emoji_astro = "🌙"

    fig.add_trace(go.Scatter3d(
        x=[P_vec[0], Z_vec[0], A_vec[0]],
        y=[P_vec[1], Z_vec[1], A_vec[1]],
        z=[P_vec[2], Z_vec[2], A_vec[2]],
        mode='text+markers',
        marker=dict(size=4, color=['black', 'navy', 'darkgreen']),
        text=["<b>PN</b>", "🧍", emoji_astro],
        textfont=dict(size=[14, 24, 24], color="black"),
        textposition="top center",
        hoverinfo='skip',
        name='Puntos Clave'
    ))

    fig.update_layout(
        title=dict(text=f"Triángulo de Posición: {nombre_astro}", font=dict(size=14)),
        hovermode=False, 
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            aspectmode='data',
            camera=dict(eye=dict(x=1.3, y=1.3, z=1.3))
        ),
        margin=dict(l=0, r=0, b=50, t=30), 
        legend=dict(
            orientation="h",   
            yanchor="top",
            y=-0.05,          
            xanchor="center",
            x=0.5,           
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="Black",
            borderwidth=1,
            font=dict(size=10)
        )
    )
    
    return fig

def dibujar_diagrama_meridiana(hv_deg, dec_deg, lat_deg):
    """
    Diagrama 2D del plano meridiano para visualizar la Meridiana del Sol.
    Muestra gráficamente la relación φ = z + δ sobre la sección del meridiano.

    Parámetros:
    - hv_deg  : Altura Verdadera del Sol (grados)
    - dec_deg : Declinación del Sol (grados, positiva Norte)
    - lat_deg : Latitud calculada del observador (grados)
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    hv_deg  = float(hv_deg)
    dec_deg = float(dec_deg)
    lat_deg = float(lat_deg)
    z_deg   = 90.0 - hv_deg

    sun_north = dec_deg > lat_deg

    th_pn  =  90.0              
    th_ps  = -90.0              
    th_z   = lat_deg               
    th_sun = dec_deg               
    th_hs  = lat_deg - 90.0        
    th_hn  = lat_deg + 90.0        
    th_eq  =  0.0                  
    R      = 1.0

    def pt(theta, r=R):
        """Devuelve coordenadas (x, y) para un ángulo y radio dados."""
        t = np.radians(theta)
        return np.array([r * np.cos(t), r * np.sin(t)])

    def draw_arc(ax, t1, t2, r, color, lw=5, zorder=3, alpha=1.0):
        """Dibuja un arco de circunferencia entre dos ángulos (grados) al radio r."""
        if abs(t2 - t1) < 0.1:
            return
        t1s, t2s = sorted([t1, t2])
        thetas = np.linspace(np.radians(t1s), np.radians(t2s), 400)
        ax.plot(r * np.cos(thetas), r * np.sin(thetas),
                color=color, lw=lw, alpha=alpha,
                solid_capstyle='round', zorder=zorder)

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_alpha(0.0)

    ax.add_patch(plt.Circle((0, 0), R, color='#f0f4f8', alpha=0.55, zorder=0))
    ax.add_patch(plt.Circle((0, 0), R, fill=False,
                             color='#2c3e50', lw=2.2, zorder=4))

    ax.plot([0, 0], [-1.22, 1.22],
            color='#aaa', lw=0.9, ls='--', alpha=0.65, zorder=1)

    hn_ext = pt(th_hn, 1.12)
    hs_ext = pt(th_hs, 1.12)
    ax.plot([hn_ext[0], hs_ext[0]], [hn_ext[1], hs_ext[1]],
            color='#444', lw=1.4, alpha=0.75, zorder=1)

    zp_ext  = pt(th_z,       1.12)
    nad_ext = pt(th_z + 180, 1.08)
    ax.plot([nad_ext[0], zp_ext[0]], [nad_ext[1], zp_ext[1]],
            color='navy', lw=0.9, ls=':', alpha=0.45, zorder=1)

    ax.plot([-R * 0.97, R * 0.97], [0, 0],
            color='#aaa', lw=0.9, ls='-.', alpha=0.5, zorder=1)

    C_LAT = '#e67e22'   
    C_HV  = '#27ae60'   
    C_Z   = '#2980b9'  
    C_DEC = '#c0392b'  

    R_HV  = 1.07
    R_Z   = 1.17
    R_DEC = 1.27
    R_LAT = 1.37

    if sun_north:
        draw_arc(ax, th_sun, th_hn, R_HV, C_HV)   
    else:
        draw_arc(ax, th_hs, th_sun, R_HV, C_HV)  

    draw_arc(ax, th_sun, th_z, R_Z, C_Z)

    if abs(dec_deg) > 0.3:
        draw_arc(ax, th_eq, th_sun, R_DEC, C_DEC)

    draw_arc(ax, th_eq, th_z, R_LAT, C_LAT)

    caps_config = []
    if sun_north:
        caps_config += [(th_sun, R_HV, C_HV), (th_hn, R_HV, C_HV)]
    else:
        caps_config += [(th_hs, R_HV, C_HV), (th_sun, R_HV, C_HV)]
    caps_config += [(th_sun, R_Z, C_Z), (th_z, R_Z, C_Z)]
    if abs(dec_deg) > 0.3:
        caps_config += [(th_eq, R_DEC, C_DEC), (th_sun, R_DEC, C_DEC)]
    caps_config += [(th_eq, R_LAT, C_LAT), (th_z, R_LAT, C_LAT)]

    for (th, r, c) in caps_config:
        ax.plot(*pt(th, r), 'o', color=c, ms=4.5, zorder=6)

    ax.plot(*pt(th_pn), 'o', color='#2c3e50', ms=9,  zorder=7)
    ax.plot(*pt(th_ps), 'o', color='#2c3e50', ms=9,  zorder=7)
    ax.plot(*pt(th_z),  'o', color='navy',    ms=10, zorder=7)
    ax.plot(*pt(th_hs), 'o', color='#555',    ms=6,  zorder=7)
    ax.plot(*pt(th_hn), 'o', color='#555',    ms=6,  zorder=7)
    ax.plot(*pt(th_eq), 'o', color='#aaa',    ms=5,  zorder=7)
    sun_x, sun_y = pt(th_sun)
    ax.plot(sun_x, sun_y, 'o', color='#f1c40f',
            ms=16, markeredgecolor='#e67e22', markeredgewidth=1.2, zorder=7)
    for ang_ray in np.arange(0, 360, 45):
        rx = np.cos(np.radians(ang_ray))
        ry = np.sin(np.radians(ang_ray))
        ax.plot([sun_x + rx * 0.075, sun_x + rx * 0.115],
                [sun_y + ry * 0.075, sun_y + ry * 0.115],
                color='#e67e22', lw=1.5, zorder=7, solid_capstyle='round')

    def lbl(x, y, text, color='#2c3e50', fs=10, bold=False,
            ha='center', va='center'):
        ax.text(x, y, text, color=color, fontsize=fs, zorder=10,
                fontweight='bold' if bold else 'normal', ha=ha, va=va)

    pn_pos = pt(th_pn)
    ps_pos = pt(th_ps)
    lbl(pn_pos[0] - 0.07, pn_pos[1] + 0.11, 'PN', bold=True, fs=12)
    lbl(ps_pos[0] - 0.07, ps_pos[1] - 0.11, 'Ps', bold=True, fs=12)

    zdir = pt(th_z) / R
    zp   = pt(th_z) + zdir * 0.14
    lbl(*zp, 'Cénit (Z)', color='navy', bold=True, fs=10,
        ha='left' if zdir[0] > 0 else 'right')

    sdir = pt(th_sun) / R
    sp   = pt(th_sun) + sdir * 0.17
    lbl(*sp, '☀  Sol', color='#e67e22', bold=True, fs=10,
        ha='left' if sdir[0] > 0 else 'right')

    hn_d = pt(th_hn) / R
    hs_d = pt(th_hs) / R
    lbl(*(pt(th_hn) + hn_d * 0.13), 'N', color='#333', bold=True, fs=11)
    lbl(*(pt(th_hs) + hs_d * 0.13), 'S', color='#333', bold=True, fs=11)

    rot_horiz = th_hs % 180
    if rot_horiz > 90:
        rot_horiz -= 180
    nadir_dir = np.array([np.cos(np.radians(th_z + 180)),
                          np.sin(np.radians(th_z + 180))])
    p_along_hn = np.array([np.cos(np.radians(th_hn)),
                           np.sin(np.radians(th_hn))]) * 0.38
    p_horiz_lbl = p_along_hn + nadir_dir * 0.09
    ax.text(p_horiz_lbl[0], p_horiz_lbl[1], 'Horizonte astr.',
            color='#555', fontsize=8, ha='center', va='center',
            rotation=rot_horiz, rotation_mode='anchor', zorder=10)

    ax.text(-0.28, -0.11, 'Ecuador Celeste',
            color='#777', fontsize=8, ha='center', va='top',
            rotation=0, zorder=10)

    def fmt_gm(val):
        neg = val < 0
        v   = abs(val)
        g   = int(v)
        m   = (v - g) * 60.0
        return f"{'-' if neg else ''}{g}°{m:.1f}'"

    def lbl_col(t_mid, r_arc, texto, color):
        """Dibuja etiqueta en columna derecha fija con línea guía al arco."""
        t   = np.radians(t_mid)
        ax_pt = np.array([r_arc * np.cos(t), r_arc * np.sin(t)])
        col_x = 1.62
        col_y = ax_pt[1]
        ax.plot([ax_pt[0], col_x - 0.01], [ax_pt[1], col_y],
                color=color, lw=0.7, ls='--', alpha=0.55, zorder=8)
        ax.text(col_x, col_y, texto, color=color, fontsize=8,
                fontweight='bold', ha='left', va='center', zorder=10,
                bbox=dict(boxstyle='round,pad=0.22', facecolor='white',
                         edgecolor=color, alpha=0.95, lw=1.3))

    t_mid_hv  = (th_sun + th_hn) / 2 if sun_north else (th_hs + th_sun) / 2
    t_mid_z   = (th_sun + th_z)   / 2
    t_mid_dec = (th_eq  + th_sun) / 2
    t_mid_lat = (th_eq  + th_z)   / 2

    etiquetas = [
        (t_mid_hv,  R_HV,  f'hv = {fmt_gm(hv_deg)}',  C_HV),
        (t_mid_z,   R_Z,   f'z = {fmt_gm(z_deg)}',     C_Z),
        (t_mid_lat, R_LAT, f'φ = {fmt_gm(lat_deg)}',   C_LAT),
    ]
    if abs(dec_deg) > 0.3:
        etiquetas.append((t_mid_dec, R_DEC, f'δ = {fmt_gm(dec_deg)}', C_DEC))
    else:
        lbl(0.0, 0.09, "δ = 0°0.0'", color=C_DEC, fs=8, ha='center')

    etiquetas.sort(key=lambda e: np.sin(np.radians(e[0])), reverse=True)

    MIN_SEP = 0.18
    ys_asignados = []

    for (t_mid, r_arc, texto, color) in etiquetas:
        t     = np.radians(t_mid)
        y_nat = r_arc * np.sin(t)   

        y_final = y_nat
        for y_prev in ys_asignados:
            if abs(y_final - y_prev) < MIN_SEP:
                y_final = y_prev - MIN_SEP

        ys_asignados.append(y_final)

        ax_pt_x = r_arc * np.cos(t)
        ax_pt_y = r_arc * np.sin(t)
        col_x   = 1.62

        ax.plot([ax_pt_x, col_x - 0.01], [ax_pt_y, y_final],
                color=color, lw=0.7, ls='--', alpha=0.55, zorder=8)
        ax.text(col_x, y_final, texto, color=color, fontsize=8,
                fontweight='bold', ha='left', va='center', zorder=10,
                bbox=dict(boxstyle='round,pad=0.22', facecolor='white',
                         edgecolor=color, alpha=0.95, lw=1.3))

    legend_items = [
        mpatches.Patch(color=C_LAT, label=f'Latitud φ'),
        mpatches.Patch(color=C_HV,  label=f'Altura hv'),
        mpatches.Patch(color=C_Z,   label=f'Dist. Cenital z'),
        mpatches.Patch(color=C_DEC, label=f'Declinación δ'),
    ]
    ax.legend(handles=legend_items, loc='upper left',
              bbox_to_anchor=(-0.02, 1.02), fontsize=8,
              framealpha=0.92, edgecolor='#ccc', ncol=2)

    ax.set_xlim(-1.80, 2.35)
    ax.set_ylim(-1.60, 1.60)
    plt.tight_layout()
    return fig
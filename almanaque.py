import os
import datetime
from datetime import date, timedelta
import pandas as pd
import numpy as np
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_min = os.path.join(BASE_DIR, 'almanaque')
ruta_may = os.path.join(BASE_DIR, 'ALMANAQUE')

if os.path.exists(ruta_may): DATA_DIR = ruta_may
elif os.path.exists(ruta_min): DATA_DIR = ruta_min
else: DATA_DIR = ruta_may

FILE_ESTRELLAS = os.path.join(DATA_DIR, 'estrellas.csv')
FILE_B1 = os.path.join(DATA_DIR, 'tabla_b1_altura.csv')
FILE_B2 = os.path.join(DATA_DIR, 'tabla_b2_fecha.csv') 
FILE_C = os.path.join(DATA_DIR, 'tabla_c_refraccion.csv')
FILE_C_PARALAJE = os.path.join(DATA_DIR, 'tabla_c_paralaje.csv')

def cargar_csv(ruta):
    if not os.path.exists(ruta): return None
    try: return pd.read_csv(ruta)
    except: return None

def interpolar_lineal_simple(x_target, x1, y1, x2, y2):
    if abs(x2 - x1) < 1e-9: return y1 
    return y1 + (x_target - x1) * (y2 - y1) / (x2 - x1)

def interpolar_dataframe(df, col_x, col_y, valor_x):
    if df.empty: return 0.0
    if valor_x <= df[col_x].iloc[0]: return float(df[col_y].iloc[0])
    if valor_x >= df[col_x].iloc[-1]: return float(df[col_y].iloc[-1])
    try:
        idx_sup = df[df[col_x] >= valor_x].index[0]
        idx_inf = idx_sup - 1
        x1 = float(df[col_x].iloc[idx_inf]); y1 = float(df[col_y].iloc[idx_inf])
        x2 = float(df[col_x].iloc[idx_sup]); y2 = float(df[col_y].iloc[idx_sup])
        return interpolar_lineal_simple(valor_x, x1, y1, x2, y2)
    except: return 0.0

def obtener_lista_estrellas():
    df = cargar_csv(FILE_ESTRELLAS)
    if df is None or df.empty: return ["⚠️ Error: Falta estrellas.csv"]
    if 'nombre' in df.columns:
        return sorted(df['nombre'].astype(str).str.strip().unique().tolist())
    return ["⚠️ Error: Columna 'nombre' no encontrada"]

def obtener_sha_dec_estrella(nombre, dia, mes, anio, hora_decimal=0):
    df = cargar_csv(FILE_ESTRELLAS)
    if df is None or df.empty: return None, None

    fila = df[df['nombre'].astype(str).str.strip() == nombre]
    if fila.empty: return None, None
    datos = fila.iloc[0]

    fecha_obs = date(anio, mes, dia)
    
    fecha_pivote_actual = date(anio, mes, 15)

    if fecha_obs < fecha_pivote_actual:
        
        f2 = fecha_pivote_actual
        m2 = mes

        f1 = f2.replace(day=1) - timedelta(days=1) 
        f1 = f1.replace(day=15) 
        m1 = f1.month
        
    else:
        
        f1 = fecha_pivote_actual
        m1 = mes
        
        if mes == 12:
            f2 = date(anio + 1, 1, 15)
            m2 = 1
        else:
            f2 = date(anio, mes + 1, 15)
            m2 = mes + 1

    try:
        sha_start = float(datos[f'sha_{m1}']); dec_start = float(datos[f'dec_{m1}'])
        sha_end   = float(datos[f'sha_{m2}']); dec_end   = float(datos[f'dec_{m2}'])
    except KeyError:
        return float(datos.get('sha_1', 0)), float(datos.get('dec_1', 0))

    total_dias = (f2 - f1).days
    
    dias_pasados = (fecha_obs - f1).days + (hora_decimal / 24.0)
    
    fraccion = dias_pasados / total_dias if total_dias > 0 else 0

    diff_sha = sha_end - sha_start
    
    if diff_sha > 180: diff_sha -= 360 
    if diff_sha < -180: diff_sha += 360
    
    sha_final = (sha_start + diff_sha * fraccion) % 360.0
    dec_final = dec_start + (dec_end - dec_start) * fraccion

    return sha_final, dec_final

def limpiar_dato(texto):
    if not isinstance(texto, str): return str(texto)
    texto = texto.replace('{', '').replace('}', '').replace('\\', '').replace('$', '')
    return texto.strip()

def obtener_ruta_archivo_dat(dia, mes, anio):
    try:
        doy = date(anio, mes, dia).timetuple().tm_yday
        num_pag = doy + 9
        nombre = f"AN{anio}{num_pag}.DAT"
        posibles = [nombre, nombre.lower(), nombre.upper()]
        for n in posibles:
            ruta = os.path.join(DATA_DIR, n)
            if os.path.exists(ruta): return ruta
        return None
    except: return None

def leer_datos_dat_completo(ruta_archivo):
    datos = {}
    if not ruta_archivo or not os.path.exists(ruta_archivo): return datos
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
            contenido = f.readlines()
            
        modo_aries = False
        
        last_dec_deg_sol = 0.0
        last_signo_sol = 1  
        
        memoria_planetas = [
            {'deg': 0.0, 'signo': 1}, 
            {'deg': 0.0, 'signo': 1}, 
            {'deg': 0.0, 'signo': 1}, 
            {'deg': 0.0, 'signo': 1} 
        ]
        
        for linea in contenido:
            if r'\def\abajo{' in linea or 'Aries' in linea:
                modo_aries = True
                continue
            
            l = linea.strip()
            if not l: continue 
            l = l.replace(r'\bf', '').replace(r'\scriptsize', '').replace(r'\tt', '')
            partes = l.split('&')
            
            if len(partes) < 3: continue
            
            try:
                txt_hora = limpiar_dato(partes[0])
                txt_hora_limpia = ''.join(filter(str.isdigit, txt_hora))
                if not txt_hora_limpia: continue
                hora = int(txt_hora_limpia)
                
                if hora not in datos: datos[hora] = {}

                if not modo_aries:
                    hg_deg = float(limpiar_dato(partes[1]))
                    hg_min = float(limpiar_dato(partes[2]))
                    
                    txt_signo = limpiar_dato(partes[3]).upper()
                    
                    if '-' in txt_signo or 'S' in txt_signo:
                        last_signo_sol = -1
                    elif '+' in txt_signo or 'N' in txt_signo:
                        last_signo_sol = 1
                    
                    signo = last_signo_sol
                    
                    txt_dec_deg = limpiar_dato(partes[4])
                    if not txt_dec_deg:
                        dec_deg = last_dec_deg_sol
                    else:
                        dec_deg = float(txt_dec_deg)
                        last_dec_deg_sol = dec_deg
                    
                    dec_min = float(limpiar_dato(partes[5]))
                    
                    datos[hora]['hg_sol'] = hg_deg + (hg_min / 60.0)
                    datos[hora]['dec_sol'] = (dec_deg + (dec_min / 60.0)) * signo
                    
                else:
                    val_deg = limpiar_dato(partes[1])
                    val_min = limpiar_dato(partes[2])
                    if val_deg and val_min:
                        datos[hora]['hg_aries'] = float(val_deg) + (float(val_min) / 60.0)

                    mapa_planetas = {
                        'Venus':   {'col_gha': 3,  'col_dec': 5,  'idx': 0},
                        'Marte':   {'col_gha': 8,  'col_dec': 10, 'idx': 1},
                        'Jupiter': {'col_gha': 13, 'col_dec': 15, 'idx': 2},
                        'Saturno': {'col_gha': 18, 'col_dec': 20, 'idx': 3}
                    }

                    for nombre_p, conf in mapa_planetas.items():
                        base_g = conf['col_gha']
                        base_d = conf['col_dec']
                        idx = conf['idx']
                        
                        if len(partes) <= base_d + 2: continue

                        p_gha_deg = float(limpiar_dato(partes[base_g]))
                        p_gha_min = float(limpiar_dato(partes[base_g + 1]))
                        gha_decimal = p_gha_deg + (p_gha_min / 60.0)

                        txt_signo = limpiar_dato(partes[base_d])
                        if '-' in txt_signo or 'S' in txt_signo:
                            memoria_planetas[idx]['signo'] = -1
                        elif '+' in txt_signo or 'N' in txt_signo:
                            memoria_planetas[idx]['signo'] = 1
                        
                        signo_actual = memoria_planetas[idx]['signo']

                        txt_deg = limpiar_dato(partes[base_d + 1])
                        if txt_deg:
                            memoria_planetas[idx]['deg'] = float(txt_deg)
                        
                        deg_actual = memoria_planetas[idx]['deg']
                        txt_min = limpiar_dato(partes[base_d + 2])
                        min_actual = float(txt_min) if txt_min else 0.0

                        dec_decimal = (deg_actual + (min_actual / 60.0)) * signo_actual

                        datos[hora][f'gha_{nombre_p}'] = gha_decimal
                        datos[hora][f'dec_{nombre_p}'] = dec_decimal

            except Exception as e:
                continue
    except: return {}
    return datos


def get_datos_sol(dia, mes, anio, hora_decimal):
    ruta = obtener_ruta_archivo_dat(dia, mes, anio)
    if not ruta: return None, None
    datos = leer_datos_dat_completo(ruta)
    
    h_int = int(hora_decimal)
    fraccion = hora_decimal - h_int
    
    if h_int not in datos: return None, None
    hg1 = datos[h_int].get('hg_sol')
    dec1 = datos[h_int].get('dec_sol')
    
    if hg1 is None or dec1 is None: return None, None
    
    hg2 = None; dec2 = None
    if (h_int + 1) in datos:
        hg2 = datos[h_int+1].get('hg_sol')
        dec2 = datos[h_int+1].get('dec_sol')
        
    if hg2 is None:
        hg2 = (hg1 + 15.04107) % 360.0 
        dec2 = dec1 
        
    diff_hg = hg2 - hg1
    if diff_hg < -300: diff_hg += 360 
    
    hg_final = (hg1 + diff_hg * fraccion) % 360.0
    dec_final = dec1 + (dec2 - dec1) * fraccion
    
    return hg_final, dec_final

def get_datos_estrella_aries(nombre, dia, mes, anio, hora_decimal):
    ruta = obtener_ruta_archivo_dat(dia, mes, anio)
    if not ruta: return None, None, "Falta DAT"
    datos_dat = leer_datos_dat_completo(ruta)
    
    h_int = int(hora_decimal)
    fraccion = hora_decimal - h_int
    
    if h_int not in datos_dat: return None, None, "Hora no en DAT"
    
    gha_aries_1 = datos_dat[h_int].get('hg_aries')
    if gha_aries_1 is None: return None, None, "Falta GHA Aries"
    
    gha_aries_2 = None
    if (h_int + 1) in datos_dat:
        gha_aries_2 = datos_dat[h_int+1].get('hg_aries')
        
    if gha_aries_2 is None:
        gha_aries_2 = (gha_aries_1 + 15.04107) % 360.0
        
    diff_aries = gha_aries_2 - gha_aries_1
    if diff_aries < -300: diff_aries += 360
    
    gha_aries_final = (gha_aries_1 + diff_aries * fraccion) % 360.0
    
    sha_star, dec_star = obtener_sha_dec_estrella(nombre, dia, mes, anio, hora_decimal)
    if sha_star is None: return None, None, "Estrella no encontrada"
    
    gha_star_final = (gha_aries_final + sha_star) % 360.0
    return gha_star_final, dec_star, gha_aries_final

def get_datos_planeta(nombre_planeta, dia, mes, anio, hora_decimal):
    """
    Obtiene GHA y Dec interpolados para Venus, Marte, Jupiter o Saturno.
    Lectura directa del .DAT (similar al Sol).
    """
    ruta = obtener_ruta_archivo_dat(dia, mes, anio)
    if not ruta: return None, None
    datos = leer_datos_dat_completo(ruta)
    
    h_int = int(hora_decimal)
    fraccion = hora_decimal - h_int
    
    key_gha = f'gha_{nombre_planeta}'
    key_dec = f'dec_{nombre_planeta}'

    if h_int not in datos: return None, None
    if key_gha not in datos[h_int]: return None, None

    gha1 = datos[h_int].get(key_gha)
    dec1 = datos[h_int].get(key_dec)
    
    gha2 = None; dec2 = None
    if (h_int + 1) in datos:
        gha2 = datos[h_int+1].get(key_gha)
        dec2 = datos[h_int+1].get(key_dec)
        
    if gha2 is None:
        gha2 = (gha1 + 15.0) % 360.0 
        dec2 = dec1 
        
    diff_gha = gha2 - gha1
    if diff_gha < -300: diff_gha += 360 
    
    gha_final = (gha1 + diff_gha * fraccion) % 360.0
    
    dec_final = dec1 + (dec2 - dec1) * fraccion
    
    return gha_final, dec_final

def obtener_correccion_b1(altura_aparente_grad):
    df = cargar_csv(FILE_B1)
    if df is None: return 0.0
    
    if 'Alt_Min' in df.columns and 'Alt_Max' in df.columns and 'Corr' in df.columns:
        df = df.sort_values('Alt_Min').reset_index(drop=True)
        df['Alt_Max'] = df['Alt_Max'].astype(float)
        df['Corr'] = df['Corr'].astype(float)
        
        filas_validas = df[df['Alt_Max'] >= altura_aparente_grad]
        
        if not filas_validas.empty:
            return filas_validas.iloc[0]['Corr']
            
        return df['Corr'].iloc[-1]

    return 0.0

def obtener_refraccion_tabla_c(altura_aparente_decimal):
    df = cargar_csv(FILE_C)
    if df is None: return 0.0
    if 'Alt_Dec' not in df.columns: df['Alt_Dec'] = df['Alt_G'] + (df['Alt_M'] / 60.0)
    df = df.sort_values('Alt_Dec').reset_index(drop=True)
    return interpolar_dataframe(df, 'Alt_Dec', 'Corr', altura_aparente_decimal)

def obtener_correccion_b2(mes_obs, dia_obs, anio_obs):
    df = cargar_csv(FILE_B2)
    if df is None: return 0.0
    try:
        doy_obs = date(anio_obs, mes_obs, dia_obs).timetuple().tm_yday
        puntos = []
        for _, row in df.iterrows():
            doy_row = date(anio_obs, int(row['M_Min']), int(row['D_Min'])).timetuple().tm_yday
            puntos.append({'doy': doy_row, 'corr': float(row['Corr'])})
        df_interp = pd.DataFrame(puntos).sort_values('doy').reset_index(drop=True)
        return interpolar_dataframe(df_interp, 'doy', 'corr', doy_obs)
    except: return 0.0

def obtener_correccion_paralaje(nombre_astro, fecha_obs, altura_aparente):
    """
    Calcula la corrección por paralaje (c2) para Venus y Marte.
    Regla General: Si fecha_obs > fecha_tabla -> Se aplica el valor nuevo.
                   Si fecha_obs <= fecha_tabla -> Se mantiene el valor anterior.
    Excepción: El 1 de Enero (doy=1) coge su propio valor porque no hay anterior.
    """
    nombre = nombre_astro.strip().lower()
    if nombre not in ['venus', 'marte']:
        return 0.0

    df = cargar_csv(FILE_C_PARALAJE)
    if df is None or df.empty:
        return 0.0

    mapa_meses = {
        'Ene.': 1, 'Feb.': 2, 'Mar.': 3, 'Abr.': 4, 'May.': 5, 'Jun.': 6,
        'Jul.': 7, 'Ago.': 8, 'Sep.': 9, 'Oct.': 10, 'Nov.': 11, 'Dic.': 12
    }

    columna_valor = ""
    if nombre == 'venus':
        columna_valor = 'Venus'
    elif nombre == 'marte':
        if altura_aparente < 30:
            columna_valor = 'Marte_low'
        elif 30 <= altura_aparente <= 60:
            columna_valor = 'Marte_mid'
        else:
            columna_valor = 'Marte_high'
    
    if columna_valor not in df.columns: return 0.0

    correccion_final = 0.0
    doy_obs = fecha_obs.timetuple().tm_yday
    
    for _, row in df.iterrows():
        partes = row['Fecha'].split()
        if len(partes) < 2: continue
        
        mes_txt = partes[0]
        dia_num = int(partes[1])
        mes_num = mapa_meses.get(mes_txt, 1)
        
        doy_tabla = date(fecha_obs.year, mes_num, dia_num).timetuple().tm_yday
        
        if (doy_obs > doy_tabla) or (doy_obs == 1 and doy_tabla == 1):
            correccion_final = float(row[columna_valor])
        else:
            break
            
    return correccion_final
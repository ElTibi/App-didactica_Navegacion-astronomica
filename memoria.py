import os
import json
import datetime

CARPETA_GUARDADOS = "guardados"

if not os.path.exists(CARPETA_GUARDADOS):
    os.makedirs(CARPETA_GUARDADOS)

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

def guardar_ejercicio(nombre_usuario, datos_session, tipo_ejercicio):
    """
    Guarda o Sobrescribe el ejercicio.
    """
    if not nombre_usuario or nombre_usuario.strip() == "":
        nombre_usuario = f"Ejercicio_{datetime.datetime.now().strftime('%H%M')}"
    
    nombre_seguro = "".join([c for c in nombre_usuario if c.isalnum() or c in (' ', '-', '_')]).strip()
    
    filename = f"{tipo_ejercicio}_{nombre_seguro}.json"
    ruta_completa = os.path.join(CARPETA_GUARDADOS, filename)
    
    contenido = {
        "meta": {
            "nombre_visible": nombre_usuario, 
            "nombre": nombre_usuario,         
            "tipo": tipo_ejercicio,
            "fecha_guardado": datetime.datetime.now().isoformat()
        },
        "datos": datos_session 
    }
    
    try:
        with open(ruta_completa, 'w', encoding='utf-8') as f:
            json.dump(contenido, f, cls=DateEncoder, indent=4, ensure_ascii=False)
        return True, f"✅ Ejercicio '{nombre_usuario}' guardado correctamente."
    except Exception as e:
        return False, f"❌ Error al guardar: {e}"

def listar_ejercicios():
    lista = []
    if not os.path.exists(CARPETA_GUARDADOS):
        return lista
        
    for f in os.listdir(CARPETA_GUARDADOS):
        if f.endswith(".json"):
            ruta = os.path.join(CARPETA_GUARDADOS, f)
            try:
                with open(ruta, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    meta = data.get('meta', {})
                    
                    nombre_mostrar = meta.get('nombre_visible', meta.get('nombre', 'Sin Nombre'))
                    
                    lista.append({
                        'archivo': f,
                        'ruta_completa': ruta, 
                        'nombre': nombre_mostrar,
                        'tipo': meta.get('tipo', 'Desconocido'),
                        'fecha': meta.get('fecha_guardado', '')
                    })
            except:
                continue
    
    lista.sort(key=lambda x: x['fecha'], reverse=True)
    return lista

def cargar_ejercicio(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['datos'], data['meta']['tipo']
    except Exception as e:
        return None, None

def eliminar_ejercicio(ruta_archivo):
    try:
        os.remove(ruta_archivo)
        return True
    except:
        return False
import math
import numpy as np
import almanaque

def acotar_valor(valor):
    if valor > 1.0: return 1.0
    if valor < -1.0: return -1.0
    return valor

def calcular_depresion(elevacion_ojo):
    """Calcula la depresión del horizonte en minutos."""
    if elevacion_ojo > 0:
        return 1.7757 * math.sqrt(elevacion_ojo)
    return 0.0

def calcular_refraccion_estandar(altura_aparente_grados):
    return almanaque.obtener_refraccion_tabla_c(altura_aparente_grados)

def calcular_altura_verdadera(ai_media, ele_obs, corr_ind, mes_obs, dia_obs, anio_obs):
    alt_sol_obs = ai_media + (corr_ind / 60.0)
    corr_sol_a_minutos = -calcular_depresion(ele_obs)
    alt_sol_apa = alt_sol_obs + (corr_sol_a_minutos / 60.0)
    b1_minutos = almanaque.obtener_correccion_b1(alt_sol_apa)
    b2_minutos = almanaque.obtener_correccion_b2(mes_obs, dia_obs, anio_obs)
    alt_sol_ver = alt_sol_apa + (b1_minutos / 60.0) + (b2_minutos / 60.0)
    return {
        "AltInstrumental": ai_media,
        "AltObservada": alt_sol_obs,
        "AltAparente": alt_sol_apa,
        "AltVerdadera": alt_sol_ver,
        "CorrIndice_min": corr_ind,
        "CorrSolA_min": corr_sol_a_minutos,
        "CorrSolB1_min": b1_minutos,
        "CorrSolB2_min": b2_minutos
    }

def calcular_correccion_estrellas(ai, ele_obs, corr_ind, nombre_astro, fecha_obs):
    """
    Calcula la altura verdadera para estrellas y planetas.
    Hv = Ha - Refraccion + Paralaje (Solo Venus/Marte)
    """
    ho = ai + (corr_ind / 60.0)
    
    depresion_min = calcular_depresion(ele_obs)
    ha = ho - (depresion_min / 60.0)
    
    raw_ref = calcular_refraccion_estandar(ha)
    refraccion_min = abs(raw_ref)
    
    paralaje_min = almanaque.obtener_correccion_paralaje(nombre_astro, fecha_obs, ha)
    
    hv = ha - (refraccion_min / 60.0) + (paralaje_min / 60.0)
    
    return {
        "AltInstrumental": ai,
        "AltObservada": ho,
        "AltAparente": ha,
        "AltVerdadera": hv,
        "Depresion_min": -depresion_min,
        "Refraccion_min": refraccion_min,
        "CorrParalaje_min": paralaje_min  
    }

def resolver_triangulo_posicion(lat_est, lon_est, gha, dec):
    LadLat = 90.0 - lat_est
    LadDec = 90.0 - dec
    AngPol = (gha + lon_est) % 360.0
    if AngPol > 180: AngPol -= 360 
    
    rad_LadLat = math.radians(LadLat)
    rad_LadDec = math.radians(LadDec)
    rad_AngPol = math.radians(AngPol)
    
    cos_LadAlt = (math.cos(rad_LadLat) * math.cos(rad_LadDec)) + \
                 (math.sin(rad_LadLat) * math.sin(rad_LadDec) * math.cos(rad_AngPol))
    cos_LadAlt = acotar_valor(cos_LadAlt)
    rad_LadAlt = math.acos(cos_LadAlt)
    LadAlt = math.degrees(rad_LadAlt)
    AltSolEst = 90.0 - LadAlt

    numerador = math.cos(rad_LadDec) - (math.cos(rad_LadLat) * math.cos(rad_LadAlt))
    denominador = math.sin(rad_LadLat) * math.sin(rad_LadAlt)
    
    if abs(denominador) < 1e-9:
        AziAst = 0.0
        AziAst_Calc = 0.0
    else:
        cos_AziAst = numerador / denominador
        cos_AziAst = acotar_valor(cos_AziAst)
        rad_AziAst = math.acos(cos_AziAst)
        AziAst_Calc = math.degrees(rad_AziAst)
        
        if 0.0 <= AngPol < 180.0:
            AziAst = 360.0 - AziAst_Calc
        else:
            AziAst = AziAst_Calc
    
    p_check = (gha + lon_est) % 360.0
    if p_check >= 0 and p_check <= 180:
        AziAst = 360.0 - AziAst if AziAst < 180 else AziAst 
        
    return {
        "LadLat": LadLat, "LadDec": LadDec, "AngPol": AngPol, "LadAlt": LadAlt,       
        "AltSolEst": AltSolEst, "AziAst_Base": AziAst_Calc, "Azimut": AziAst       
    }
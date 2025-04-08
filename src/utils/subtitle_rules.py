# utils/subtitle_rules.py

import math

# Preferred punctuation characters for breaking (using Unicode ellipsis '…')
PREFERRED_PUNCTUATION = '.,!?;:…'

def format_dialog_simple_split(text, max_chars=37):
    """
    Formatea el texto en una o dos líneas.
    - Si cabe en una línea (<= max_chars), devuelve una línea.
    - Si no, busca el último espacio antes o en max_chars para crear la primera línea.
      El resto del texto va a la segunda línea, sin importar su longitud.
    - Si no hay espacios en la primera parte, fuerza el corte en max_chars.

    Args:
        text (str): El texto completo a formatear (ya preprocesado, sin \n internos).
        max_chars (int): Máximo de caracteres para la PRIMERA línea.

    Returns:
        str: Texto formateado en una o dos líneas separadas por '\n'.
    """
    text = text.strip() # Asegurarse de que no hay espacios extra al inicio/final
    if not text:
        return ""
    if len(text) <= max_chars:
        return text # Cabe en una línea

    # Buscar el último espacio ANTES o EN la posición max_chars
    break_point = -1
    # Consideramos romper justo DESPUÉS del espacio, así que buscamos <= max_chars
    # Ajuste: buscar hasta max_chars inclusive
    search_limit = min(max_chars, len(text) - 1)
    for i in range(search_limit, 0, -1):
        if text[i] == ' ':
            # Verificamos que el carácter anterior no sea también un espacio
            # y que no estemos al principio absoluto del texto si i=0
            if i > 0 and text[i-1] != ' ':
                 break_point = i
                 break
        # Considerar si el carácter EN max_chars es espacio (no necesario con el min anterior)

    if break_point != -1:
        # Romper en el espacio encontrado
        line1 = text[:break_point].strip()
        line2 = text[break_point+1:].strip()
        # Asegurarse de que ninguna línea quede vacía si había espacios extra
        if not line1: return line2 # Si la primera parte era solo espacio
        if not line2: return line1 # Si la segunda parte era solo espacio
        return f"{line1}\n{line2}"
    else:
        # No se encontró espacio adecuado antes de max_chars, forzar corte en max_chars
        # Asegurarse de que max_chars no exceda la longitud del texto
        split_point = min(max_chars, len(text))
        line1 = text[:split_point].strip()
        line2 = text[split_point:].strip()
        if not line1: return line2
        if not line2: return line1
        # Evitar añadir línea vacía si no hay segunda parte
        return f"{line1}\n{line2}" if line2 else line1


# --- srt_time_to_ms, ms_to_srt_time (SIN CAMBIOS) ---
def srt_time_to_ms(srt_time):
    h, m, s_ms = srt_time.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)

def ms_to_srt_time(ms):
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    milli = ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"

def merge_subtitles(subtitles,
                    max_gap=3000,      # Gap máx. entre subtítulos para fusionar
                    max_chars=37,      # Máx. 37 caracteres en la primera línea
                    max_sub_dur=8000   # Máx. 8 segundos (8000 ms) por subtítulo
                   ):
    """
    Fusiona subtítulos consecutivos si:
      - Son del mismo personaje,
      - El gap entre ellos es <= max_gap,
      - Al combinar ambos no superan 8s totales,
      - Y no se excede el límite de 2 líneas de 37 caracteres (74)
        cuando ambas intervenciones, por separado, cumplen ese límite.

    Si una intervención individual ya supera 74 caracteres, se omite la norma
    para esa intervención (no podemos partirla), pero no se sigue concatenando
    con otras que sí cumplen la norma, para no generar un subtítulo aún mayor.
    """
    if not subtitles:
        return []

    merged = []
    if not subtitles:
        return []

    # Copia profunda para evitar modificar la lista original indirectamente
    import copy
    buffer_sub = copy.deepcopy(subtitles[0])

    # Función auxiliar para saber si un texto cabe en 2 líneas de 37
    def fits_in_two_lines(text, max_chars=37):
        formatted = format_dialog_simple_split(text.strip(), max_chars)
        # Verifica si hay más de un salto de línea (más de 2 líneas)
        # O si alguna línea excede max_chars (aunque format_dialog debería prevenirlo)
        lines = formatted.split('\n')
        if len(lines) > 2:
            return False
        # La primera línea ya está limitada por format_dialog_simple_split
        # La segunda línea puede ser más larga, así que verificamos la longitud total como proxy.
        # Una comprobación más robusta verificaría cada línea individualmente si format_dialog cambiara.
        return len(text.strip()) <= (2 * max_chars) # Aproximación simple usada antes
        # Alternativa más precisa si format_dialog pudiera fallar:
        # return all(len(line) <= max_chars for line in lines)

    for i in range(1, len(subtitles)):
        current = subtitles[i]
        same_speaker = (current["character"] == buffer_sub["character"])
        gap = current["start_ms"] - buffer_sub["end_ms"]

        # Asegurarse de que los tiempos son coherentes (start <= end)
        if buffer_sub["end_ms"] < buffer_sub["start_ms"]: buffer_sub["end_ms"] = buffer_sub["start_ms"]
        if current["end_ms"] < current["start_ms"]: current["end_ms"] = current["start_ms"]
        gap = current["start_ms"] - buffer_sub["end_ms"] # Recalcular por si acaso

        if same_speaker and 0 <= gap <= max_gap:
            # Duración si unimos buffer_sub + current
            combined_duration = current["end_ms"] - buffer_sub["start_ms"]

            if combined_duration <= max_sub_dur:
                # Verificar longitudes individuales y combinadas
                buffer_text = buffer_sub["dialog"].strip()
                current_text = current["dialog"].strip()
                # Usar '...' para indicar continuación natural si no hay puntuación fuerte
                joiner = " "
                if buffer_text and not buffer_text.endswith(tuple(PREFERRED_PUNCTUATION + " '\"")):
                   if current_text and not current_text.startswith(tuple(PREFERRED_PUNCTUATION + " '\"")):
                       joiner = "... " # O simplemente " " si prefieres no añadir puntos

                combined_text = buffer_text + joiner + current_text

                # Usar la función format_dialog para una mejor estimación del ajuste
                buffer_fits = fits_in_two_lines(buffer_text, max_chars)
                current_fits = fits_in_two_lines(current_text, max_chars)
                combined_fits = fits_in_two_lines(combined_text, max_chars)


                # Permitir fusión si el combinado cabe, independientemente de si los originales cabían.
                # La lógica anterior era demasiado restrictiva.
                if combined_fits:
                    # Se pueden fusionar
                    buffer_sub["dialog"] = combined_text
                    buffer_sub["end_ms"] = current["end_ms"]
                    # Si la duración combinada se ha vuelto negativa o cero (error en datos), forzar duración mínima
                    if buffer_sub["end_ms"] <= buffer_sub["start_ms"]:
                        buffer_sub["end_ms"] = buffer_sub["start_ms"] + 100 # Ajustar a un valor mínimo razonable
                else:
                    # No se fusionan porque el resultado excede las 2 líneas / 74 chars
                    merged.append(buffer_sub)
                    buffer_sub = copy.deepcopy(current)

            else:
                # Se excede la duración de 8s => no fusionar
                merged.append(buffer_sub)
                buffer_sub = copy.deepcopy(current)
        else:
            # Distinto personaje o gap inválido => no fusionar
            merged.append(buffer_sub)
            buffer_sub = copy.deepcopy(current)

    # Agregar el último buffer_sub
    merged.append(buffer_sub)
    return merged


# --- postprocess_subtitles: MODIFICADO ---
def postprocess_subtitles(subtitles, min_gap=24, min_dur=1000, max_dur=8000, max_chars=37, cps=15):
    """
    Ajusta tiempos (gap, duración) y formatea el diálogo.
    Aplica regla CPS para extender duración, pero NO si eso retrasa
    el inicio original del siguiente subtítulo (respetando min_gap).
    """
    if not subtitles:
        return []

    processed_subs = []
    last_end_ms = -min_gap  # Para permitir que el primer subtítulo empiece en 0

    num_subs = len(subtitles)
    for i, sub_data in enumerate(subtitles):
        text_to_format = sub_data["dialog"]
        original_start_ms = sub_data["start_ms"]
        original_end_ms = sub_data["end_ms"]
        character = sub_data["character"]

        formatted_lines = format_dialog_simple_split(text_to_format, max_chars)
        if not formatted_lines:
            continue

        # --- Ajuste de Tiempos ---
        # 1. Ajustar inicio para cumplir min_gap con el subtítulo ANTERIOR PROCESADO
        current_start_ms = max(original_start_ms, last_end_ms + min_gap)

        # --- Calcular fin basado en reglas, pero con LÍMITE SUPERIOR ---

        # 2. Calcular duración estimada por CPS
        visual_text = formatted_lines.replace('\n', '')
        num_lines = formatted_lines.count('\n') + 1
        chars_per_second = cps
        line_penalty = 1.1 if num_lines == 2 else 1.0 # Pequeña penalización por 2 líneas

        # Evitar división por cero si CPS es 0
        estimated_duration_ms_cps = 0
        if chars_per_second > 0:
             estimated_duration_ms_cps = (len(visual_text) / chars_per_second) * 1000 * line_penalty
        
        # Duración mínima requerida
        required_duration_ms = max(min_dur, estimated_duration_ms_cps)

        # 3. Calcular el fin MÍNIMO basado en inicio ajustado y duración mínima REQUERIDA
        min_required_end_ms = current_start_ms + required_duration_ms

        # 4. Determinar el LÍMITE SUPERIOR para el fin del subtítulo actual.
        #    Este límite viene dado por el inicio original del SIGUIENTE subtítulo.
        max_allowed_end_ms = current_start_ms + max_dur # Límite por max_dur
        
        # Si NO es el último subtítulo, considerar el inicio del siguiente
        if i + 1 < num_subs:
            next_original_start_ms = subtitles[i+1]["start_ms"]
            # El final de este sub no puede pasar de (inicio_original_siguiente - min_gap)
            limit_by_next = next_original_start_ms - min_gap
            # Tomamos el MÍNIMO entre el límite de max_dur y el límite impuesto por el siguiente sub
            max_allowed_end_ms = min(max_allowed_end_ms, limit_by_next)


        # 5. Calcular el fin final:
        #    - Debe ser al menos el fin mínimo requerido (min_required_end_ms)
        #    - No debe exceder el límite superior calculado (max_allowed_end_ms)
        #    - También debería respetar el fin original si es posterior al mínimo requerido,
        #      pero sin pasarse del límite superior.
        current_end_ms = max(min_required_end_ms, original_end_ms)
        current_end_ms = min(current_end_ms, max_allowed_end_ms)

        # 6. Asegurarse de que el fin no sea anterior al inicio + min_dur (última garantía)
        #    Esto puede pasar si max_allowed_end_ms es muy restrictivo.
        current_end_ms = max(current_end_ms, current_start_ms + min_dur)
        
        # 7. Asegurarse de que el fin no sea anterior al inicio (puede ocurrir con gaps negativos o datos raros)
        if current_end_ms < current_start_ms:
            current_end_ms = current_start_ms + min_dur # Forzar duración mínima

        processed_subs.append({
            "start_ms": int(round(current_start_ms)),
            "end_ms": int(round(current_end_ms)),
            "dialog": formatted_lines,
            "character": character,
            # Podrías añadir el CPS real para depuración si quieres:
            # "cps_real": len(visual_text) / ((current_end_ms - current_start_ms) / 1000) if (current_end_ms - current_start_ms) > 0 else 0
        })

        # Actualizar fin para el cálculo del gap del SIGUIENTE subtítulo
        last_end_ms = current_end_ms

    return processed_subs

# --- Ejemplo de uso (necesitarías datos reales) ---
# dummy_subtitles = [
#     {"start_ms": 1000, "end_ms": 3000, "dialog": "Esta es la primera línea.", "character": "A"},
#     {"start_ms": 3500, "end_ms": 6000, "dialog": "Y esta es la segunda, que podría extenderse.", "character": "A"},
#     {"start_ms": 6100, "end_ms": 8000, "dialog": "Tercera línea que no debe moverse.", "character": "B"},
#     {"start_ms": 9000, "end_ms": 12000, "dialog": "Una línea muy muy muy muy muy muy muy larga que definitivamente necesita más tiempo según CPS.", "character": "C"},
#     {"start_ms": 12050, "end_ms": 14000, "dialog": "Última línea.", "character": "C"},
# ]
# 
# # Primero fusionar si es necesario
# merged = merge_subtitles(dummy_subtitles)
# # Luego postprocesar tiempos y formato
# final_subs = postprocess_subtitles(merged, min_gap=50, min_dur=1000, max_dur=8000, max_chars=37, cps=15)
# 
# for i, sub in enumerate(final_subs):
#     start_time = ms_to_srt_time(sub['start_ms'])
#     end_time = ms_to_srt_time(sub['end_ms'])
#     print(f"{i+1}")
#     print(f"{start_time} --> {end_time}")
#     print(f"{sub['dialog']}")
#     # print(f"(CPS: {sub.get('cps_real', 0):.2f})") # Descomentar para ver CPS real
#     print()
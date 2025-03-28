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
    for i in range(max_chars, 0, -1):
        if text[i] == ' ':
            # Verificamos que el carácter anterior no sea también un espacio
            # para evitar dobles espacios al unir o romper.
            if i > 0 and text[i-1] != ' ':
                 break_point = i
                 break
        # Si el carácter EN max_chars es espacio, también es válido
        if i == max_chars and text[i] == ' ':
             if i > 0 and text[i-1] != ' ':
                 break_point = i
                 break


    if break_point != -1:
        # Romper en el espacio encontrado
        line1 = text[:break_point].strip()
        line2 = text[break_point+1:].strip()
        # Asegurarse de que ninguna línea quede vacía si había espacios extra
        if not line1: return line2 # Si la primera parte era solo espacio
        if not line2: return line1 # Si la segunda parte era solo espacio
        return f"{line1}\n{line2}"
    else:
        # No se encontró espacio adecuado, forzar corte en max_chars
        # (esto es raro si el texto viene de JSON con espacios)
        line1 = text[:max_chars].strip()
        line2 = text[max_chars:].strip()
        if not line1: return line2
        if not line2: return line1
        return f"{line1}\n{line2}"

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
    buffer_sub = subtitles[0].copy()

    # Función auxiliar para saber si un texto cabe en 2 líneas de 37
    def fits_in_two_lines(text, max_chars=37):
        # Muy simple: si no supera 74 caracteres en total, podremos partirlo
        # en una primera línea de hasta 37 y el resto en la segunda.
        return len(text.strip()) <= (2 * max_chars)

    for current in subtitles[1:]:
        same_speaker = (current["character"] == buffer_sub["character"])
        gap = current["start_ms"] - buffer_sub["end_ms"]

        if same_speaker and 0 <= gap <= max_gap:
            # Duración si unimos buffer_sub + current
            combined_duration = current["end_ms"] - buffer_sub["start_ms"]

            if combined_duration <= max_sub_dur:
                # Verificar longitudes individuales y combinadas
                buffer_text = buffer_sub["dialog"].strip()
                current_text = current["dialog"].strip()
                combined_text = buffer_text + " " + current_text

                buffer_fits = fits_in_two_lines(buffer_text, max_chars)
                current_fits = fits_in_two_lines(current_text, max_chars)
                combined_fits = fits_in_two_lines(combined_text, max_chars)

                # Caso 1: Ambas intervenciones caben por separado en 2 líneas (<=74)
                if buffer_fits and current_fits:
                    # Solo fusionar si el resultado también cabe en <=74
                    if combined_fits:
                        # Se pueden fusionar sin romper la norma
                        buffer_sub["dialog"] = combined_text
                        buffer_sub["end_ms"] = current["end_ms"]
                    else:
                        # No se fusionan para no romper la norma
                        merged.append(buffer_sub)
                        buffer_sub = current.copy()
                else:
                    # Caso 2: Al menos una de las dos ya excede 74.
                    # "No queda otra" que ignorar la norma para esa intervención
                    # PERO lo recomendable es no concatenar más si una ya incumple,
                    # para no agravar la longitud. Por tanto, tampoco fusionamos.
                    merged.append(buffer_sub)
                    buffer_sub = current.copy()
            else:
                # Se excede la duración de 8s => no fusionar
                merged.append(buffer_sub)
                buffer_sub = current.copy()
        else:
            # Distinto personaje o gap > max_gap => no fusionar
            merged.append(buffer_sub)
            buffer_sub = current.copy()

    # Agregar el último buffer_sub
    merged.append(buffer_sub)
    return merged


# --- postprocess_subtitles: Refactored to handle overflow ---
def postprocess_subtitles(subtitles, min_gap=24, min_dur=1000, max_dur=8000, max_chars=37):
    """
    Ajusta tiempos (gap, duración) y formatea el diálogo usando simple split.
    Ya NO maneja overflow creando nuevos subtítulos.
    """
    if not subtitles:
        return []

    processed_subs = []
    last_end_ms = -min_gap # Para permitir que el primer subtítulo empiece en 0

    for sub_data in subtitles:
        text_to_format = sub_data["dialog"] # Ya viene preprocesado (sin \n, sin paréntesis)
        original_start_ms = sub_data["start_ms"]
        original_end_ms = sub_data["end_ms"]
        character = sub_data["character"]

        # CAMBIO: Usar la nueva función de formato simple
        # Esta función devuelve todo el texto formateado, no hay 'remaining_text'
        formatted_lines = format_dialog_simple_split(text_to_format, max_chars)

        if not formatted_lines:
             continue # Ignorar subtítulos vacíos

        # --- Ajuste de Tiempos ---
        # 1. Ajustar inicio para cumplir min_gap con el subtítulo anterior
        current_start_ms = max(original_start_ms, last_end_ms + min_gap)

        # 2. Calcular duración estimada basada en caracteres (opcional, puede ayudar a guiar)
        #    Podemos usar una heurística simple o basarnos en el número de líneas
        num_lines = formatted_lines.count('\n') + 1
        chars_per_second = 15 # Ajusta según necesidad
        # Usamos len(text_to_format) porque formatted_lines incluye el \n
        estimated_duration_ms = max(min_dur, (len(text_to_format) / chars_per_second) * 1000)

        # 3. Calcular el fin MÍNIMO basado en el inicio ajustado y la duración mínima
        min_end_ms = current_start_ms + min_dur

        # 4. Calcular el fin basado en la duración estimada
        estimated_end_ms = current_start_ms + estimated_duration_ms

        # 5. Determinar el fin final, respetando la duración mínima, máxima y el OUT original
        current_end_ms = min_end_ms # Empezar con el mínimo requerido
        current_end_ms = max(current_end_ms, estimated_end_ms) # Intentar alcanzar la duración estimada
        current_end_ms = min(current_end_ms, current_start_ms + max_dur) # No exceder la duración máxima
        # Ya NO necesitamos la lógica compleja de max_allowed_end_ms porque no hay overflow
        current_end_ms = max(current_end_ms, original_end_ms) # Intentar respetar el OUT original si es más tardío


        # Asegurarse de que el fin no sea anterior al inicio (puede pasar con ajustes agresivos)
        if current_end_ms <= current_start_ms:
            current_end_ms = current_start_ms + min_dur # Forzar duración mínima si hay conflicto

        processed_subs.append({
            "start_ms": int(current_start_ms),
            "end_ms": int(current_end_ms),
            "dialog": formatted_lines, # El texto ya formateado en 1 o 2 líneas
            "character": character
        })

        # Actualizar el tiempo de fin para el cálculo del gap del siguiente subtítulo
        last_end_ms = current_end_ms

    # CAMBIO: Eliminada la sección de añadir puntos suspensivos de continuidad.
    # CAMBIO: Eliminada la validación final de >2 líneas (no debería ocurrir).

    return processed_subs
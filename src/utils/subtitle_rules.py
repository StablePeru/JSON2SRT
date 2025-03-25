# utils/subtitle_rules.py

def srt_time_to_ms(srt_time):
    """
    Convierte un tiempo en formato SRT ("hh:mm:ss,mmm") a milisegundos.
    """
    h, m, s_ms = srt_time.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)

def ms_to_srt_time(ms):
    """
    Convierte milisegundos a un tiempo en formato SRT ("hh:mm:ss,mmm").
    """
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    milli = ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"

def merge_subtitles(subtitles, max_gap=500, max_length=80):
    """
    Fusiona subtítulos consecutivos del mismo personaje si se cumplen criterios:
      - Se fusionan si la diferencia (current["start_ms"] - buffer["end_ms"]) es menor o igual a max_gap
        (esto incluye solapamientos con gap negativo).
      - Se fusionan si la longitud combinada del diálogo es menor que max_length.
      
    Cada subtítulo es un dict:
      {
        "start_ms": int,   # tiempo de inicio en ms
        "end_ms":   int,     # tiempo de fin en ms
        "dialog":   str,     # texto del subtítulo
        "character": str     # nombre del personaje
      }
    
    En la fusión se toma el IN más pequeño y el OUT más alto.
    Se procesan los subtítulos en el orden en que aparecen en la lista (orden original del JSON).
    """
    if not subtitles:
        return []
    
    merged = []
    buffer_sub = subtitles[0]
    
    for current in subtitles[1:]:
        same_speaker = (current["character"] == buffer_sub["character"])
        gap = current["start_ms"] - buffer_sub["end_ms"]
        # Se fusionan si el mismo personaje y si el gap es menor o igual a max_gap (incluye solapamiento)
        temp_merged_text = buffer_sub["dialog"] + " " + current["dialog"]
        if same_speaker and gap <= max_gap and len(temp_merged_text) < max_length:
            # Fusionar: conservar el IN menor y el OUT mayor
            buffer_sub["dialog"] = temp_merged_text.strip()
            buffer_sub["start_ms"] = min(buffer_sub["start_ms"], current["start_ms"])
            buffer_sub["end_ms"] = max(buffer_sub["end_ms"], current["end_ms"])
        else:
            merged.append(buffer_sub)
            buffer_sub = current
    
    merged.append(buffer_sub)
    return merged

def postprocess_subtitles(subtitles, min_gap=24, min_dur=1000, max_dur=8000, max_chars=37):
    """
    Ajusta los tiempos para:
      - Garantizar un espacio mínimo de 'min_gap' ms entre subtítulos.
      - Forzar duraciones entre 'min_dur' y 'max_dur' ms.
    Además, divide el diálogo en hasta 2 líneas de 'max_chars' caracteres cada una.
    
    Devuelve la lista final de subtítulos.
    """
    # Se procesan en el orden original
    for i in range(len(subtitles)):
        if i > 0:
            prev_end = subtitles[i-1]["end_ms"]
            if subtitles[i]["start_ms"] < prev_end + min_gap:
                subtitles[i]["start_ms"] = prev_end + min_gap
        
        duration = subtitles[i]["end_ms"] - subtitles[i]["start_ms"]
        if duration < min_dur:
            subtitles[i]["end_ms"] = subtitles[i]["start_ms"] + min_dur
        elif duration > max_dur:
            subtitles[i]["end_ms"] = subtitles[i]["start_ms"] + max_dur
        
        subtitles[i]["dialog"] = format_dialog(subtitles[i]["dialog"], max_chars)
    
    return subtitles

def format_dialog(text, max_chars=37):
    """
    Divide el texto en hasta 2 líneas de 'max_chars' caracteres,
    respetando el orden de las palabras.
    """
    words = text.split()
    if len(text) < 33 or not words:
        return text
    
    line1, line2 = "", ""
    for w in words:
        if not line1:
            if len(w) <= max_chars:
                line1 = w
            else:
                return w  # palabra demasiado larga, se devuelve tal cual
        else:
            if len(line1) + len(w) + 1 <= max_chars:
                line1 += " " + w
            else:
                if not line2:
                    line2 = w
                else:
                    if len(line2) + len(w) + 1 <= max_chars:
                        line2 += " " + w
                    else:
                        line2 += " " + w
                        
    return line1 + "\n" + line2 if line2 else line1

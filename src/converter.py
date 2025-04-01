# converter.py

import json
import os
import logging

from utils.character_utils import count_character_appearances, get_top_characters, assign_color_code
from utils.time_utils import convert_time  # Convierte "hh:mm:ss:ff" a "hh:mm:ss,mmm"

# Importar las funciones de subtitle_rules
from utils.subtitle_rules import (
    srt_time_to_ms,
    ms_to_srt_time,
    merge_subtitles,
    postprocess_subtitles # Asegúrate de que este importa la versión MODIFICADA
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_json_file(json_path):
    """
    Carga y parsea un archivo JSON.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error reading file {json_path}: {e}")

def extract_data_from_json(json_content):
    """
    Extrae la lista de subtítulos del contenido JSON.
    """
    if isinstance(json_content, list):
        data = json_content
    elif isinstance(json_content, dict) and 'data' in json_content:
        data = json_content['data']
    else:
        data = []

    if not data:
        raise ValueError("No valid data found in JSON content")

    return data

def create_srt_entry(index, start_time, end_time, color_code, dialog):
    """
    Crea la entrada SRT (texto) para un subtítulo.
    """
    # Asegurarse de que el diálogo no tenga espacios extra al inicio/final de las líneas
    cleaned_dialog = "\n".join(line.strip() for line in dialog.strip().split('\n'))
    return f"{index}\n{start_time} --> {end_time}\n{color_code}{cleaned_dialog}\n"

# --- FUNCIÓN MODIFICADA ---
def process_json_to_srt(json_file, output_file, fps=25, callback=None):
    """
    Procesa un archivo JSON a SRT, aplicando fusión de subtítulos consecutivos,
    ajuste de tiempos y formateo de texto según las nuevas reglas.
    """
    try:
        logger.info(f"Processing {json_file} to {output_file}")

        # 1) Cargar y extraer datos del JSON
        json_content = load_json_file(json_file)
        data = extract_data_from_json(json_content)

        # 2) Contar personajes y obtener top_characters (para color codes)
        character_counter = count_character_appearances(json_content)
        top_characters = get_top_characters(character_counter)

        logger.info("Top 4 characters with most lines:")
        for i, character in enumerate(top_characters):
            logger.info(f"{i+1}. {character}: {character_counter[character]} lines")

        # 3) Convertir cada elemento en una estructura con tiempos en ms y PREPROCESAR DIÁLOGO
        subtitles = []
        for item in data:
            if "IN" in item and "OUT" in item and "DIÁLOGO" in item:
                # Convertir "hh:mm:ss:ff" a "hh:mm:ss,mmm" (formato SRT)
                start_srt = convert_time(item["IN"], fps)
                end_srt = convert_time(item["OUT"], fps)

                # Convertir a milisegundos
                start_ms = srt_time_to_ms(start_srt)
                end_ms = srt_time_to_ms(end_srt)

                # CAMBIO: Preprocesar diálogo: reemplazar \n por espacio y quitar espacios extra
                dialog = item["DIÁLOGO"].replace('\n', ' ').strip()
                # CAMBIO: Ya NO se llama a remove_parentheses_content

                character = item.get("PERSONAJE", "")

                subtitles.append({
                    "start_ms": start_ms,
                    "end_ms": end_ms,
                    "dialog": dialog, # Dialogo preprocesado
                    "character": character,
                    # Guardar partes originales por si se necesita en la fusión (opcional pero puede ser útil)
                    "original_dialog": item["DIÁLOGO"].strip()
                })

        # 4) Fusionar subtítulos consecutivos del mismo personaje (NUEVA REGLA DE GAP)
        #    Pasamos el nuevo max_gap=3000 y quitamos max_length de aquí
        merged_subs = merge_subtitles(subtitles, max_gap=3000) # max_length ya no se pasa aquí

        # 5) Postprocesar: ajustar espacios mínimos, duraciones y formatear el texto (NUEVA LÓGICA)
        final_subs = postprocess_subtitles(
            merged_subs,
            min_gap=24,
            min_dur=1000,
            max_dur=8000,
            max_chars=37 # Este sigue siendo el límite para la PRIMERA línea
        )

        # 6) Generar el contenido SRT final
        srt_content = []
        total_items = len(final_subs)

        for i, sub in enumerate(final_subs, start=1):
            new_start = ms_to_srt_time(sub["start_ms"])
            new_end = ms_to_srt_time(sub["end_ms"])

            # Asignar color code según el personaje
            color_code = assign_color_code(sub["character"], top_characters)

            # Crear la entrada SRT
            # La función create_srt_entry se asegura de limpiar espacios finales
            srt_entry = create_srt_entry(i, new_start, new_end, color_code, sub["dialog"])
            srt_content.append(srt_entry)

            if callback and i % 5 == 0:
                callback(i / total_items * 100)

        if not srt_content:
            raise ValueError("Could not generate SRT content from data")

        # 7) Guardar el archivo SRT
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(srt_content))

        if callback:
            callback(100)

        logger.info(f"SRT file created: {output_file}")
        return True

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise

# --- FIN FUNCIÓN MODIFICADA ---
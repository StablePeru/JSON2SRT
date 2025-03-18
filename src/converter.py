"""
Main module for converting JSON subtitle files to SRT format.
"""
import json
import os
import logging
from utils.character_utils import count_character_appearances, get_top_characters, assign_color_code
from utils.time_utils import convert_time
from utils.text_utils import remove_parentheses_content

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_json_file(json_path):
    """
    Loads and parses a JSON file.
    
    Args:
        json_path (str): Path to the JSON file
        
    Returns:
        dict: Parsed JSON content
        
    Raises:
        Exception: If file cannot be read or parsed
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error reading file {json_path}: {e}")

def extract_data_from_json(json_content):
    """
    Extracts data from JSON content.
    
    Args:
        json_content (dict or list): Parsed JSON content
        
    Returns:
        list: List of data items
        
    Raises:
        ValueError: If no valid data is found
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
    Creates a single SRT entry.
    
    Args:
        index (int): Subtitle index
        start_time (str): Start time in SRT format
        end_time (str): End time in SRT format
        color_code (str): Color code for the character
        dialog (str): Dialog text
        
    Returns:
        str: Formatted SRT entry
    """
    return f"{index}\n{start_time} --> {end_time}\n{color_code}{dialog}\n"

def process_json_to_srt(json_file, output_file, fps=25, callback=None):
    """
    Processes a JSON file to SRT format with color codes.
    
    Args:
        json_file (str): Path to the JSON file
        output_file (str): Path to the output SRT file
        fps (int): Frames per second for time conversion
        callback (function): Optional callback for progress reporting
        
    Returns:
        bool: True if conversion was successful
        
    Raises:
        Exception: If conversion fails
    """
    try:
        logger.info(f"Processing {json_file} to {output_file}")
        
        # Load and parse JSON
        json_content = load_json_file(json_file)
        data = extract_data_from_json(json_content)
        
        # Count character appearances and get top characters
        character_counter = count_character_appearances(json_content)
        top_characters = get_top_characters(character_counter)
        
        # Log top characters
        logger.info("Top 4 characters with most lines:")
        for i, character in enumerate(top_characters):
            logger.info(f"{i+1}. {character}: {character_counter[character]} lines")
        
        # Create SRT content
        srt_content = []
        total_items = len(data)
        
        for i, item in enumerate(data, 1):
            if "IN" in item and "OUT" in item and "DIÁLOGO" in item:
                # Convert time format
                start_time = convert_time(item["IN"], fps)
                end_time = convert_time(item["OUT"], fps)
                
                # Assign color code
                character = item.get("PERSONAJE", "")
                color_code = assign_color_code(character, top_characters)
                
                # Process dialog text
                dialog = remove_parentheses_content(item["DIÁLOGO"])
                
                # Create SRT entry
                srt_entry = create_srt_entry(i, start_time, end_time, color_code, dialog)
                srt_content.append(srt_entry)
                
                # Report progress if callback is provided
                if callback and i % 5 == 0:
                    callback(i / total_items * 100)
        
        # Verify content
        if not srt_content:
            raise ValueError("Could not generate SRT content from data")
        
        # Write SRT file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(srt_content))
        
        # Report 100% progress
        if callback:
            callback(100)
        
        logger.info(f"SRT file created: {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise
"""
Utilities for handling character-related operations in subtitle files.
"""
from collections import Counter

def count_character_appearances(data):
    """
    Counts the appearances of each character in the data.
    
    Args:
        data (list or dict): JSON data containing character information
        
    Returns:
        Counter: Counter object with character counts
    """
    character_counter = Counter()
    
    # Check if data is in list format or inside a 'data' key
    if isinstance(data, list):
        data_list = data
    elif isinstance(data, dict) and 'data' in data:
        data_list = data['data']
    else:
        data_list = []
    
    for item in data_list:
        if "PERSONAJE" in item and item["PERSONAJE"]:
            character_counter[item["PERSONAJE"]] += 1
    
    return character_counter

def get_top_characters(character_counter, top_n=4):
    """
    Gets the top N characters that speak the most.
    
    Args:
        character_counter (Counter): Counter object with character counts
        top_n (int): Number of top characters to return
        
    Returns:
        list: List of top character names
    """
    return [char for char, _ in character_counter.most_common(top_n)]

def assign_color_code(character, top_characters):
    """
    Assigns a color code based on the character's position in the top list.
    
    Args:
        character (str): Character name
        top_characters (list): List of top character names
        
    Returns:
        str: Color code for the character
    """
    if character not in top_characters:
        return "<BN1>"  # White - Not main character
    
    position = top_characters.index(character)
    if position == 0:
        return "<AN1>"  # Yellow - Main character 1
    elif position == 1:
        return "<CN1>"  # Light blue - Main character 2
    elif position == 2:
        return "<MN1>"  # Magenta - Main character 3
    elif position == 3:
        return "<VN1>"  # Green - Main character 4
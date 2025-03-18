"""
Utilities for handling time format conversions in subtitle files.
"""

def convert_time(time_str, fps=25):
    """
    Converts a time string with format "hh:mm:ss:ff" to "hh:mm:ss,mmm"
    where frames are converted to milliseconds using fps.
    
    Args:
        time_str (str): Time string in format "hh:mm:ss:ff"
        fps (int): Frames per second, defaults to 25
        
    Returns:
        str: Time string in format "hh:mm:ss,mmm"
        
    Raises:
        ValueError: If time string format is incorrect
    """
    try:
        parts = time_str.split(":")
        if len(parts) != 4:
            raise ValueError(f"Incorrect time format: {time_str}")
        h, m, s, f = parts
        h, m, s, f = int(h), int(m), int(s), int(f)
        ms = round(f * (1000 / fps))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    except Exception as e:
        raise ValueError(f"Error converting time '{time_str}': {e}")
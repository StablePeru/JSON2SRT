"""
Utilities for handling time format conversions in subtitle files.
"""

def convert_time(time_str, fps=25):
    """
    Converts a time string with format "hh:mm:ss:ff" to "hh:mm:ss,mmm"
    where frames are converted to milliseconds using fps.
    """
    try:
        parts = time_str.split(":")
        if len(parts) != 4:
            raise ValueError(f"Incorrect time format: {time_str}")
        h, m, s, f = map(int, parts)
        total_ms = ((h * 3600 + m * 60 + s) * 1000) + round((f * 1000) / fps)
        hh = total_ms // 3600000
        total_ms %= 3600000
        mm = total_ms // 60000
        total_ms %= 60000
        ss = total_ms // 1000
        ms = total_ms % 1000
        return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"
    except Exception as e:
        raise ValueError(f"Error converting time '{time_str}': {e}")

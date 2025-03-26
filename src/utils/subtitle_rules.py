# utils/subtitle_rules.py

import math

# Preferred punctuation characters for breaking (using Unicode ellipsis '…')
PREFERRED_PUNCTUATION = '.,!?;:…'

def format_dialog_balanced(text, max_chars=37):
    """
    Formats text into one or two lines (max_chars per line).
    Aims for balanced lines and prefers breaking after punctuation.
    If text exceeds two lines, returns the formatted first 1 or 2 lines
    and the remaining text separately.

    Returns:
        tuple: (formatted_lines: str, remaining_text: str or None)
               formatted_lines: Text for the current subtitle (1 or 2 lines).
               remaining_text: Overflow text for the next subtitle, or None.
    """
    text = text.strip()
    if not text:
        return ("", None)

    # --- Case 1: Fits in a single line ---
    if len(text) <= max_chars:
        return (text, None)

    # --- Case 2: Potentially fits in two lines (or needs splitting) ---
    
    best_2line_break = {'index': -1, 'imbalance': float('inf'), 'type': None} # type: 'punct' or 'space'

    potential_break_indices = [i for i, char in enumerate(text) if char == ' ']

    # Try to find the best balanced 2-line split
    for i in potential_break_indices:
        line1_len = i
        char_before_space = text[i - 1] if i > 0 else ''
        line2_len = len(text) - line1_len - 1

        # Check validity for a potential *two-line* subtitle block
        if line1_len > 0 and line1_len <= max_chars and line2_len > 0 and line2_len <= max_chars:
            imbalance = abs(line1_len - line2_len)
            is_punctuation = char_before_space in PREFERRED_PUNCTUATION

            current_type = 'punct' if is_punctuation else 'space'
            
            # Prioritize punctuation breaks, then lower imbalance
            prefer_current = False
            if best_2line_break['index'] == -1:
                prefer_current = True
            elif current_type == 'punct' and best_2line_break['type'] == 'space':
                 prefer_current = True
            elif current_type == best_2line_break['type'] and imbalance < best_2line_break['imbalance']:
                 prefer_current = True
            elif current_type == 'space' and best_2line_break['type'] == 'punct' and imbalance < best_2line_break['imbalance'] - 10: # Allow slightly more imbalance for punctuation
                 # Optional: Allow non-punct break if significantly more balanced
                 pass # Currently sticking to punctuation preference

            if prefer_current:
                best_2line_break['imbalance'] = imbalance
                best_2line_break['index'] = i
                best_2line_break['type'] = current_type

    # --- Decision based on findings ---

    # If a valid 2-line split was found:
    if best_2line_break['index'] != -1:
        split_i = best_2line_break['index']
        line1 = text[:split_i]
        line2 = text[split_i + 1:]
        return (f"{line1}\n{line2}", None) # All text fits in 2 lines

    # If NO valid 2-line split exists (text might be > 2*max_chars or have long words):
    # We MUST split. Find the best place to break off the *first line*.
    best_1line_break = {'index': -1, 'distance_from_max': float('inf'), 'type': None}

    for i in potential_break_indices:
        line1_len = i
        char_before_space = text[i - 1] if i > 0 else ''

        # Check validity for only the *first line*
        if line1_len > 0 and line1_len <= max_chars:
            distance = max_chars - line1_len # How close to max_chars without exceeding
            is_punctuation = char_before_space in PREFERRED_PUNCTUATION
            current_type = 'punct' if is_punctuation else 'space'

            prefer_current = False
            if best_1line_break['index'] == -1:
                 prefer_current = True
            # Prefer breaks closer to max_chars for the first line when overflowing
            elif distance < best_1line_break['distance_from_max']:
                 prefer_current = True
            elif distance == best_1line_break['distance_from_max'] and current_type == 'punct' and best_1line_break['type'] == 'space':
                 prefer_current = True # Prefer punctuation if distance is equal

            if prefer_current:
                 best_1line_break['distance_from_max'] = distance
                 best_1line_break['index'] = i
                 best_1line_break['type'] = current_type

    # If a valid break for the first line was found:
    if best_1line_break['index'] != -1:
        split_i = best_1line_break['index']
        line1 = text[:split_i]
        remaining_text = text[split_i + 1:]
        # Now, try to format the *remaining_text* into the second line if possible
        if len(remaining_text) <= max_chars:
             return (f"{line1}\n{remaining_text}", None) # Fits after forced first line break
        else:
            # Remaining text is still too long for line 2. Find best break for line 2.
            best_line2_break = {'index': -1, 'distance_from_max': float('inf'), 'type': None}
            potential_break_indices_rem = [i for i, char in enumerate(remaining_text) if char == ' ']
            
            for i in potential_break_indices_rem:
                 line2_len = i
                 char_before_space = remaining_text[i-1] if i > 0 else ''
                 if line2_len > 0 and line2_len <= max_chars:
                      distance = max_chars - line2_len
                      is_punctuation = char_before_space in PREFERRED_PUNCTUATION
                      current_type = 'punct' if is_punctuation else 'space'
                      
                      prefer_current = False
                      if best_line2_break['index'] == -1: prefer_current = True
                      elif distance < best_line2_break['distance_from_max']: prefer_current = True
                      elif distance == best_line2_break['distance_from_max'] and current_type == 'punct' and best_line2_break['type'] == 'space': prefer_current = True
                      
                      if prefer_current:
                           best_line2_break['distance_from_max'] = distance
                           best_line2_break['index'] = i
                           best_line2_break['type'] = current_type

            if best_line2_break['index'] != -1:
                 split_i2 = best_line2_break['index']
                 line2 = remaining_text[:split_i2]
                 final_remaining = remaining_text[split_i2 + 1:]
                 return (f"{line1}\n{line2}", final_remaining)
            else:
                 # Cannot even break remaining text for line 2 (e.g., long word)
                 # Put only line1 in this sub, return all remaining_text
                 return (line1, remaining_text)
                 
    else:
        # Cannot even find a break for the first line (e.g., single word > max_chars)
        # Return the word itself and signal no remainder (it won't fit anyway)
        # Or maybe split arbitrarily? For now, return as is.
        first_word = text.split(' ', 1)[0]
        if len(first_word) > max_chars:
             # If even the first word is too long, return it and the rest
             remaining = text[len(first_word):].lstrip()
             return (first_word, remaining if remaining else None)
        else: # Should have been caught by single line case or 1-line break, but safety.
             return (text, None)


# --- srt_time_to_ms, ms_to_srt_time, merge_subtitles remain the same ---
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

def merge_subtitles(subtitles, max_gap=500, max_length=80):
    # ... (implementation remains the same as previous version) ...
    if not subtitles: return []
    merged = []
    if not subtitles: return []
    buffer_sub = subtitles[0].copy() 
    for current in subtitles[1:]:
        same_speaker = (current["character"] == buffer_sub["character"])
        gap = current["start_ms"] - buffer_sub["end_ms"]
        potential_dialog = buffer_sub["dialog"].strip() + " " + current["dialog"].strip()
        if same_speaker and gap <= max_gap and len(potential_dialog) <= max_length:
            buffer_sub["dialog"] = potential_dialog 
            buffer_sub["start_ms"] = min(buffer_sub["start_ms"], current["start_ms"])
            buffer_sub["end_ms"] = max(buffer_sub["end_ms"], current["end_ms"])
        else:
            merged.append(buffer_sub)
            buffer_sub = current.copy() 
    merged.append(buffer_sub)
    return merged

# --- postprocess_subtitles: Refactored to handle overflow ---
def postprocess_subtitles(subtitles, min_gap=24, min_dur=1000, max_dur=8000, max_chars=37):
    """
    Adjusts timings, formats dialog using balanced line breaking (max 2 lines),
    handles text overflow by creating new subtitle blocks, and adds continuity ellipsis.
    """
    if not subtitles:
        return []

    processed_subs = []
    # Use an index to iterate through the original list, as we might add new entries implicitly
    
    temp_subs_to_process = subtitles[:] # Start with a copy of the original list

    i = 0
    while i < len(temp_subs_to_process):
        sub_data = temp_subs_to_process[i]
        
        # --- Process current text chunk ---
        text_to_format = sub_data["dialog"]
        original_start_ms = sub_data["start_ms"]
        original_end_ms = sub_data["end_ms"]
        character = sub_data["character"]

        # Format the text, potentially getting remaining overflow
        formatted_lines, remaining_text = format_dialog_balanced(text_to_format, max_chars)

        if not formatted_lines: # Skip if formatting returned nothing (e.g., empty input)
             i += 1
             continue

        # --- Timing for the current formatted block ---
        current_start_ms = original_start_ms
        
        # Adjust start based on *last added* subtitle in processed_subs
        if processed_subs:
            prev_end = processed_subs[-1]["end_ms"]
            if current_start_ms < prev_end + min_gap:
                current_start_ms = prev_end + min_gap

        # Estimate duration based on text length (e.g., Reading Speed Chars/Sec)
        # A simple approach: 15 chars/sec approx. Adjust as needed.
        chars_per_second = 15
        estimated_duration_ms = max(min_dur, (len(formatted_lines) / chars_per_second) * 1000)
        
        # Apply min/max duration rules, constrained by original end time if no overflow
        calculated_end_ms = current_start_ms + estimated_duration_ms
        
        # If there's remaining text, the current block cannot extend past the original end time.
        # If there's NO remaining text, it can extend based on rules, but capped reasonably.
        max_allowed_end_ms = original_end_ms if remaining_text else (current_start_ms + max_dur)

        current_end_ms = current_start_ms + min_dur # Ensure min duration first
        current_end_ms = max(current_end_ms, calculated_end_ms) # Apply calculated duration if longer
        current_end_ms = min(current_end_ms, current_start_ms + max_dur) # Cap at max duration
        current_end_ms = min(current_end_ms, max_allowed_end_ms) # Don't exceed original end if splitting
        
        # Final safety check: ensure end >= start
        current_end_ms = max(current_end_ms, current_start_ms + 50) # Ensure at least tiny duration

        # Add the processed subtitle block
        processed_subs.append({
            "start_ms": int(current_start_ms),
            "end_ms": int(current_end_ms),
            "dialog": formatted_lines,
            "character": character
        })

        # --- Handle Overflow ---
        if remaining_text:
            # Prepare the remaining text as a new temporary subtitle entry
            # It will be processed in the next iteration (or inserted).
            # Start time for the overflow block is right after the current one ends (+ min_gap)
            overflow_start_ms = current_end_ms + min_gap
             # Ensure overflow starts no later than the original end time
            overflow_start_ms = min(overflow_start_ms, original_end_ms) 
            
            # The overflow block inherits the *original* end time boundary.
            overflow_end_ms = original_end_ms
            
            # Ensure overflow end is actually after its start
            overflow_end_ms = max(overflow_end_ms, overflow_start_ms + min_dur)

            new_sub_data = {
                "start_ms": overflow_start_ms,
                "end_ms": overflow_end_ms,
                "dialog": remaining_text,
                "character": character
            }
            # Insert this new data right after the current index 'i'
            # so it gets processed in the next loop iteration.
            temp_subs_to_process.insert(i + 1, new_sub_data)

        # Move to the next item in the (potentially expanded) list
        i += 1
        
    # --- Final Pass: Add continuity markers (...) ---
    # (This logic remains the same as the previous version, operating on processed_subs)
    if len(processed_subs) > 1:
        for i in range(1, len(processed_subs)):
            prev_sub = processed_subs[i-1]
            current_sub = processed_subs[i]
            is_same_speaker = (prev_sub["character"] == current_sub["character"]) and prev_sub["character"]
            time_gap_ms = current_sub["start_ms"] - prev_sub["end_ms"]
            needs_continuity_marker = is_same_speaker and (0 <= time_gap_ms <= 5000)

            if needs_continuity_marker:
                # Add ellipsis to end of prev_sub if space allows
                prev_lines = prev_sub["dialog"].split('\n')
                last_line_prev = prev_lines[-1]
                trailing_punctuation = '.,!?;:… '
                cleaned_last_line = last_line_prev.rstrip(trailing_punctuation)
                ellipsis_marker = "…"
                new_last_line = cleaned_last_line + ellipsis_marker
                if len(new_last_line) <= max_chars:
                    prev_lines[-1] = new_last_line
                    prev_sub["dialog"] = "\n".join(prev_lines)

                # Add ellipsis to start of current_sub if space allows
                current_lines = current_sub["dialog"].split('\n')
                first_line_current = current_lines[0]
                ellipsis_prefix = "…"
                new_first_line = ellipsis_prefix + first_line_current
                if len(new_first_line) <= max_chars:
                     current_lines[0] = new_first_line
                     current_sub["dialog"] = "\n".join(current_lines)

    # --- Final Validation (Optional but Recommended) ---
    for sub in processed_subs:
         if sub["dialog"].count('\n') >= 2:
              # This should not happen with the new logic, but log if it does.
              print(f"WARNING: Subtitle still found with >2 lines after processing: Start={ms_to_srt_time(sub['start_ms'])} Text='{sub['dialog'][:50]}...'")
              # Optionally, truncate aggressively here if needed, though it indicates a logic flaw earlier.
              lines = sub["dialog"].split('\n')
              sub["dialog"] = "\n".join(lines[:2])


    return processed_subs
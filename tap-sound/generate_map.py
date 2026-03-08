#!/usr/bin/env python3
"""
Generate frequency_map.json
Edit the frequency variables below
"""
import random
import json
import os
import sys

# ============================================
# FREQUENCY CONFIGURATION - EDIT THESE
# ============================================
FREQUENCY_MIN = 100         # Minimum frequency (Hz)
FREQUENCY_MAX = 20000       # Maximum frequency (Hz)
FREQUENCY_INCREMENT = 1   # Hz step between available frequencies

CHARACTERS = '123456789'  # All digits for tap code (1-5 for chars, 6-9 for space)
NUM_CHARACTERS = len(CHARACTERS)
FREQUENCY_MAP_FILE = 'key.json'

def create_frequency_map():
    """
    Create frequency map by randomly shuffling character assignments across all frequencies.
    
    Example with 3 chars (A,B,C) and 12 frequencies:
    1. Create all 12 frequencies: [10000, 10001, 10002, ...]
    2. Create character list with each appearing 4 times: [A, B, C, C, B, C, A, A, B, B, C, A]
    3. SHUFFLE randomly: [A, B, C, C, B, C, A, A, B, B, C, A] → [C, A, B, A, C, B, C, A, B, C, A, B]
    4. Assign: A gets frequencies at positions where A appears, etc.
    
    Result: NO OVERLAP, completely random distribution!
    """
    freq_range = FREQUENCY_MAX - FREQUENCY_MIN
    num_frequencies = int(freq_range / FREQUENCY_INCREMENT)
    freq_per_char = num_frequencies // NUM_CHARACTERS
    
    # Generate all frequencies
    all_frequencies = [FREQUENCY_MIN + (i * FREQUENCY_INCREMENT) for i in range(num_frequencies)]
    
    # Create character list: A appears freq_per_char times, B appears freq_per_char times, etc.
    character_list = []
    for char in CHARACTERS:
        character_list.extend([char] * freq_per_char)
    
    # SHUFFLE the character list completely randomly
    random.shuffle(character_list)
    
    # Assign frequencies to characters based on shuffled positions
    freq_map = {char: [] for char in CHARACTERS}
    for i, char in enumerate(character_list):
        freq_map[char].append(all_frequencies[i])
    
    return freq_map

def save_frequency_map(freq_map, filepath='frequency_map.json'):
    """Save frequency map to JSON in compact format (one key per line, frequencies compacted on one line)."""
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    
    # Create compact JSON output manually
    with open(filepath, 'w') as f:
        f.write('{\n')
        chars = list(freq_map.keys())
        for i, char in enumerate(chars):
            freq_pool = freq_map[char]
            # All frequencies on one line, no spaces
            freq_str = ','.join(str(f) for f in freq_pool)
            f.write(f'  "{char}":[{freq_str}]')
            if i < len(chars) - 1:
                f.write(',')
            f.write('\n')
        f.write('}\n')
    print(f"✓ Frequency map saved to {filepath}")

# Create and save (saves to current directory)
if __name__ == "__main__":
    freq_map = create_frequency_map()
    save_frequency_map(freq_map, FREQUENCY_MAP_FILE)

    # Show summary
    print(f"\n{'='*60}")
    print(f"FREQUENCY MAP CREATED")
    print(f"{'='*60}")
    print(f"Total characters: {NUM_CHARACTERS}")
    print(f"Frequencies per character: ~{len(freq_map[CHARACTERS[0]])}")
    print(f"Frequency range: {FREQUENCY_MIN}-{FREQUENCY_MAX} Hz")
    print(f"\nSample:")
    for i, char in enumerate(CHARACTERS[:5]):
        pool = freq_map[char]
        print(f"  {char}: {len(pool)} frequencies - {min(pool)}-{max(pool)} Hz")
        print(f"       Samples: {pool[:3]}...")
    print(f"{'='*60}\n")

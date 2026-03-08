#!/usr/bin/env python3
"""
Generate key.json for binary sound encryption
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
FREQUENCY_INCREMENT = 1     # Hz step between available frequencies

CHARACTERS = '01'  # Binary: 0 and 1
NUM_CHARACTERS = len(CHARACTERS)
FREQUENCY_MAP_FILE = 'key.json'

def create_frequency_map():
    """
    Create frequency map by randomly shuffling character assignments across all frequencies.
    
    Process:
    1. Create all available frequencies in range
    2. Create character list with 0 and 1 each appearing equally
    3. SHUFFLE randomly so 0 and 1 have completely random, non-overlapping frequency pools
    4. Assign frequencies based on shuffled positions
    
    Result: 0 gets ~10,000 random frequencies, 1 gets ~10,000 different random frequencies
    """
    freq_range = FREQUENCY_MAX - FREQUENCY_MIN
    num_frequencies = int(freq_range / FREQUENCY_INCREMENT)
    freq_per_char = num_frequencies // NUM_CHARACTERS
    
    # Generate all frequencies
    all_frequencies = [FREQUENCY_MIN + (i * FREQUENCY_INCREMENT) for i in range(num_frequencies)]
    
    # Create character list: 0 appears freq_per_char times, 1 appears freq_per_char times
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

def save_frequency_map(freq_map, filepath='key.json'):
    """Save frequency map to JSON file."""
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write('{\n')
        chars = list(freq_map.keys())
        for i, char in enumerate(chars):
            freq_str = ','.join(str(freq) for freq in freq_map[char])
            f.write(f'  "{char}":[{freq_str}]')
            if i < len(chars) - 1:
                f.write(',')
            f.write('\n')
        f.write('}\n')
    print(f"✓ Frequency map saved to {filepath}")

if __name__ == '__main__':
    print(f"Generating frequency map for binary (0-1) with {FREQUENCY_MAX - FREQUENCY_MIN} Hz range...")
    freq_map = create_frequency_map()
    
    print(f"✓ '0' has {len(freq_map['0'])} random frequencies")
    print(f"✓ '1' has {len(freq_map['1'])} random frequencies")
    
    save_frequency_map(freq_map, FREQUENCY_MAP_FILE)
    print("✓ Done! Your key.json is ready. Keep it secret!")

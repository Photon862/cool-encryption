"""
CORE ENCRYPTION/DECRYPTION LOGIC
All the complex math and signal processing happens here.
Tap code system: Each character converts to 2 digits (row, column)
"""

import numpy as np
from scipy.fft import fft
from .config import (
    SAMPLE_RATE, TONE_DURATION, AMPLITUDE, FREQUENCY_MIN, FREQUENCY_MAX,
    FREQUENCY_INCREMENT, CHARACTERS, NUM_CHARACTERS, FREQUENCY_TOLERANCE, FFT_WINDOW
)
import random
import json
import os


# Tap code mapping (C/K and I/J merged)
TAP_CODE = {
    'A': (1, 1), 'B': (1, 2), 'C': (1, 3), 'K': (1, 3), 'D': (1, 4), 'E': (1, 5),
    'F': (2, 1), 'G': (2, 2), 'H': (2, 3), 'I': (2, 4), 'J': (2, 4), 'L': (3, 1),
    'M': (3, 2), 'N': (3, 3), 'O': (3, 4), 'P': (3, 5),
    'Q': (4, 1), 'R': (4, 2), 'S': (4, 3), 'T': (4, 4), 'U': (4, 5),
    'V': (5, 1), 'W': (5, 2), 'X': (5, 3), 'Y': (5, 4), 'Z': (5, 5),
}

# Reverse mapping: (row, col) -> character
REVERSE_TAP_CODE = {v: k for k, v in TAP_CODE.items()}

# Space code: Any combination with 6-9 (uses digits outside 1-5)
SPACE_CODE = (6, 2)  # Space is encoded as 62


def character_to_tap_code(char):
    """Convert a character to tap code (row, col) tuple."""
    char = char.upper()
    if char not in TAP_CODE:
        raise ValueError(f"Character '{char}' not in tap code mapping")
    return TAP_CODE[char]


def tap_code_to_character(row, col):
    """Convert tap code (row, col) back to character."""
    if (row, col) not in REVERSE_TAP_CODE:
        return '?'
    return REVERSE_TAP_CODE[(row, col)]


def is_space_code(row, col):
    """Check if a digit pair represents a space (contains 6-9)."""
    return row >= 6 or col >= 6


def create_frequency_map():
    """
    Create a COMPLETELY RANDOM frequency map with ZERO pattern.
    
    Process:
    1. For EACH character independently
    2. Generate N completely random frequencies (not sequential)
    3. Each frequency is picked randomly from the range (WHOLE NUMBERS)
    4. All characters get the SAME amount of random frequencies
    5. Result: A gets [10847, 13421, 10234, 14998, ...], B gets [11203, 10089, 14567, ...] etc
    
    Returns:
        dict: {character: [completely random frequencies], ...}
    """
    freq_range = FREQUENCY_MAX - FREQUENCY_MIN
    num_frequencies = int(freq_range / FREQUENCY_INCREMENT)
    
    # Calculate how many frequencies each character gets
    freq_per_char = num_frequencies // NUM_CHARACTERS
    
    freq_map = {}
    for char in CHARACTERS:
        # For THIS character, generate completely random frequencies
        # NO pattern, NO sequence, just pure randomness (WHOLE NUMBERS)
        char_frequencies = []
        for _ in range(freq_per_char):
            # Pick a completely random frequency in the range (as integer)
            random_freq = random.randint(FREQUENCY_MIN, FREQUENCY_MAX)
            char_frequencies.append(random_freq)
        
        freq_map[char] = char_frequencies
    
    return freq_map


def save_frequency_map(freq_map, filepath='frequency_map.json'):
    """Save the frequency map to JSON in compact format (one key per line, frequencies compacted on one line)."""
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    
    # Create compact JSON output manually
    with open(filepath, 'w') as f:
        f.write('{\n')
        chars = list(freq_map.keys())
        for i, char in enumerate(chars):
            freq_pool = freq_map[char]
            # All frequencies on one line, no spaces
            freq_str = ','.join(str(freq) for freq in freq_pool)
            f.write(f'  "{char}":[{freq_str}]')
            if i < len(chars) - 1:
                f.write(',')
            f.write('\n')
        f.write('}\n')
    print(f"Frequency map saved to {filepath}")


def load_frequency_map(filepath='frequency_map.json'):
    """Load frequency map from JSON."""
    with open(filepath, 'r') as f:
        json_map = json.load(f)
    
    # Convert lists back to lists (already lists from JSON)
    freq_map = {char: freq_pool for char, freq_pool in json_map.items()}
    return freq_map


def pick_random_frequency(char, freq_map):
    """
    Pick a RANDOM frequency from the character's available pool.
    
    Each character has a pool of ~139 randomly distributed frequencies.
    Each encoding picks a DIFFERENT random one from the pool.
    
    Args:
        char: Character (A-Z, 0-9)
        freq_map: Frequency mapping {char: [freqs...], ...}
    
    Returns:
        float: Random frequency in Hz from the character's pool
    """
    if char not in freq_map:
        raise ValueError(f"Character '{char}' not in frequency map")
    
    freq_pool = freq_map[char]
    random_freq = random.choice(freq_pool)
    return random_freq


def generate_tone(frequency, duration=TONE_DURATION, sample_rate=SAMPLE_RATE, amplitude=AMPLITUDE):
    """
    Generate a sine wave tone at specified frequency.
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        amplitude: Amplitude (0.0 to 1.0)
    
    Returns:
        numpy array: Audio samples (float32)
    """
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave.astype(np.float32)


def stack_tones(frequencies, duration=TONE_DURATION):
    """
    Stack multiple frequencies together (mix them).
    Each frequency is played simultaneously.
    
    Args:
        frequencies: List of frequencies in Hz
        duration: Duration in seconds
    
    Returns:
        numpy array: Mixed audio samples (float32)
    """
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, endpoint=False)
    
    # Sum all sine waves
    stacked_audio = np.zeros(samples, dtype=np.float32)
    for freq in frequencies:
        tone = AMPLITUDE * np.sin(2 * np.pi * freq * t)
        stacked_audio += tone
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(stacked_audio))
    if max_val > 0:
        stacked_audio = stacked_audio / max_val * 0.9
    
    return stacked_audio.astype(np.float32)


def encode_message(message, freq_map):
    """
    Encode a message into audio chunks using tap code.
    
    Each character converts to tap code (row, col) - 2 digits.
    Each digit gets its own individual sound file.
    Spaces are encoded as digit pairs with 6-9 (e.g., 62).
    
    Args:
        message: String like "HELLO WORLD"
        freq_map: Frequency mapping for digits 1-5 (and 6-9 for space)
    
    Returns:
        list: Audio chunks (each is a numpy array for one digit)
    """
    message = message.upper()
    
    # Convert message to tap code digits
    tap_code_digits = []
    for char in message:
        if char == ' ':
            # Insert space code (any digit pair with 6-9)
            tap_code_digits.append('6')
            tap_code_digits.append('2')
            continue
        if char not in TAP_CODE:
            print(f"Warning: Character '{char}' not in tap code map, skipping")
            continue
        
        row, col = character_to_tap_code(char)
        tap_code_digits.append(str(row))
        tap_code_digits.append(str(col))
    
    # Generate individual sounds for each digit
    audio_chunks = []
    for digit in tap_code_digits:
        # All digits (1-9) use the frequency map
        if digit in freq_map:
            # Pick a random frequency from this digit's pool
            freq = pick_random_frequency(digit, freq_map)
            # Generate single tone (no stacking)
            tone = generate_tone(freq)
            audio_chunks.append(tone)
        else:
            print(f"Warning: Digit '{digit}' not in frequency map")
    
    return audio_chunks
    
    return audio_chunks


def detect_frequencies_in_chunk(audio_chunk, tolerance=FREQUENCY_TOLERANCE):
    """
    Detect all dominant frequencies in an audio chunk using FFT with zero-padding.
    Improved for short tones (< 0.13s).
    
    Args:
        audio_chunk: Audio samples (numpy array)
        tolerance: Frequency tolerance in Hz
    
    Returns:
        list: Detected frequencies in Hz
    """
    # Zero-pad for better frequency resolution (4x padding for short tones)
    padded_chunk = np.pad(audio_chunk, (0, len(audio_chunk) * 3), mode='constant')
    
    # Apply window function
    windowed = padded_chunk * np.hanning(len(padded_chunk))
    
    # FFT
    fft_result = np.abs(fft(windowed))
    freqs = np.fft.fftfreq(len(windowed), 1/SAMPLE_RATE)
    
    # Work with positive frequencies only
    positive_freqs = freqs[:len(freqs)//2]
    positive_fft = fft_result[:len(fft_result)//2]
    
    # Find peaks (dominant frequencies) using local maxima
    detected = []
    threshold = np.max(positive_fft) * 0.05  # Lowered threshold for short tones
    
    # Find local maxima instead of just threshold crossings
    for i in range(1, len(positive_freqs) - 1):
        if (positive_fft[i] > threshold and 
            positive_fft[i] > positive_fft[i-1] and 
            positive_fft[i] > positive_fft[i+1]):
            # Use parabolic interpolation for better frequency estimate
            if positive_fft[i-1] > 0 and positive_fft[i+1] > 0:
                # Refine frequency estimate
                a = positive_fft[i-1]
                b = positive_fft[i]
                c = positive_fft[i+1]
                offset = 0.5 * (a - c) / (a - 2*b + c)
                refined_freq = positive_freqs[i] + offset * (positive_freqs[1] - positive_freqs[0])
                detected.append(refined_freq)
            else:
                detected.append(positive_freqs[i])
    
    # Cluster frequencies that are too close together
    if detected:
        detected = cluster_frequencies(detected, tolerance)
    
    return detected


def cluster_frequencies(frequencies, tolerance):
    """
    Merge frequencies that are within tolerance of each other.
    """
    if not frequencies:
        return []
    
    frequencies = sorted(frequencies)
    clusters = []
    current_cluster = [frequencies[0]]
    
    for freq in frequencies[1:]:
        if freq - current_cluster[-1] <= tolerance:
            current_cluster.append(freq)
        else:
            # Average the cluster
            clusters.append(np.mean(current_cluster))
            current_cluster = [freq]
    
    clusters.append(np.mean(current_cluster))
    return clusters


def map_frequency_to_character(frequency, freq_map, tolerance=FREQUENCY_TOLERANCE):
    """
    Map a detected frequency back to its character.
    Find the CLOSEST matching frequency in the entire map.
    
    Args:
        frequency: Detected frequency in Hz
        freq_map: Frequency mapping {char: [freqs...], ...}
        tolerance: Allowed tolerance in Hz
    
    Returns:
        str: Character with closest matching frequency, or '?' if not found
    """
    closest_char = None
    closest_distance = float('inf')
    
    # Find the closest frequency across ALL characters
    for char, freq_pool in freq_map.items():
        for pool_freq in freq_pool:
            distance = abs(frequency - pool_freq)
            if distance < closest_distance:
                closest_distance = distance
                closest_char = char
    
    # Only return if within tolerance
    if closest_distance <= tolerance:
        return closest_char
    
    return '?'


def map_frequency_to_digit(frequency, freq_map, tolerance=FREQUENCY_TOLERANCE):
    """
    Map a detected frequency back to its digit (1-5).
    Find the CLOSEST matching frequency in the entire map.
    
    Args:
        frequency: Detected frequency in Hz
        freq_map: Frequency mapping {digit: [freqs...], ...}
        tolerance: Allowed tolerance in Hz
    
    Returns:
        str: Digit (1-5) with closest matching frequency, or '?' if not found
    """
    closest_digit = None
    closest_distance = float('inf')
    
    # Find the closest frequency across ALL digits
    for digit, freq_pool in freq_map.items():
        for pool_freq in freq_pool:
            distance = abs(frequency - pool_freq)
            if distance < closest_distance:
                closest_distance = distance
                closest_digit = digit
    
    # Only return if within tolerance
    if closest_distance <= tolerance:
        return str(closest_digit)
    
    return '?'


def decode_audio_chunks(audio_chunks, freq_map):
    """
    Decode audio chunks back to text using tap code.
    
    Each chunk is a single digit (1-5, or 6-9 for space).
    Pairs them up: (row, col) -> character
    Space codes: Any pair with 6-9 in either position
    
    Args:
        audio_chunks: List of audio arrays (one per digit)
        freq_map: Frequency mapping for digits 1-5
    
    Returns:
        str: Decoded message
    """
    decoded_digits = []
    
    for chunk in audio_chunks:
        # Detect frequency in this chunk
        detected_freqs = detect_frequencies_in_chunk(chunk)
        
        if detected_freqs:
            # Take the first/strongest frequency
            freq = detected_freqs[0]
            # Map to digit using frequency map (works for all 1-9)
            digit = map_frequency_to_digit(freq, freq_map)
            if digit != '?':
                decoded_digits.append(digit)
    
    # Pair up digits and convert to characters
    decoded_message = []
    for i in range(0, len(decoded_digits), 2):
        if i + 1 < len(decoded_digits):
            row = int(decoded_digits[i])
            col = int(decoded_digits[i + 1])
            # Check if this is a space code (contains 6-9)
            if is_space_code(row, col):
                decoded_message.append(' ')
            else:
                char = tap_code_to_character(row, col)
                decoded_message.append(char)
    
    return ''.join(decoded_message)


def show_frequency_map(freq_map):
    """Display the frequency mapping in a readable format."""
    print("\n" + "="*70)
    print("FREQUENCY MAP - Randomized Pools for Each Tap Code Digit (1-5)")
    print("="*70)
    print(f"Total frequencies per digit: ~{len(freq_map[CHARACTERS[0]])}")
    print(f"Total range: {FREQUENCY_MIN}-{FREQUENCY_MAX} Hz")
    print(f"Distribution: COMPLETELY RANDOMIZED (no pattern, whole numbers)")
    print("-"*70)
    
    for digit in CHARACTERS:
        freq_pool = freq_map[digit]
        freq_min = min(freq_pool)
        freq_max = max(freq_pool)
        print(f"  {digit:3s}: {len(freq_pool):3d} frequencies (range: {freq_min:8d}-{freq_max:8d} Hz)")
    
    print("="*70)
    print("Note: Each digit's pool is COMPLETELY RANDOM.")
    print("When encoding, a random frequency from the pool is selected.")
    print("Same digit picks DIFFERENT frequency each time!")
    print("\nTap Code System:")
    print("  Rows 1-5 (5 columns each) = 25 letters")
    print("  Each character -> 2 digits (row, col)")
    print("  Example: H = 23 (row 2, col 3)\n")
    print("="*70 + "\n")

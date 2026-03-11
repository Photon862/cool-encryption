"""
CORE ENCRYPTION/DECRYPTION LOGIC FOR BASE64-SOUND
All the complex math and signal processing happens here.
Each character maps to ONE frequency (no stacking).
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


def create_frequency_map():
    """
    Create a COMPLETELY RANDOM frequency map for base64 characters.
    
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


def save_frequency_map(freq_map, filepath='key.json'):
    """Save the frequency map to JSON."""
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    
    # Convert lists to JSON-serializable format
    json_map = {char: freq_pool for char, freq_pool in freq_map.items()}
    
    with open(filepath, 'w') as f:
        json.dump(json_map, f, indent=2)
    print(f"Frequency map saved to {filepath}")


def load_frequency_map(filepath='key.json'):
    """Load frequency map from JSON."""
    with open(filepath, 'r') as f:
        json_map = json.load(f)
    
    # Convert lists back to lists (already lists from JSON)
    freq_map = {char: freq_pool for char, freq_pool in json_map.items()}
    return freq_map


def pick_random_frequency(char, freq_map):
    """
    Pick a RANDOM frequency from the character's available pool.
    
    Each character has a pool of randomly distributed frequencies.
    Each encoding picks a DIFFERENT random one from the pool.
    
    Args:
        char: Character in base64 set
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


def encode_message(message, freq_map):
    """
    Encode a message into audio chunks - ONE CHARACTER = ONE SOUND.
    
    Each character gets its own separate sound chunk.
    NO STACKING - each character plays independently.
    
    Args:
        message: String to encode
        freq_map: Frequency map {char: [freqs...], ...}
    
    Returns:
        list: Audio chunks (one per character)
    """
    audio_chunks = []
    
    for char in message:
        if char not in freq_map:
            print(f"Warning: Character '{char}' not in frequency map, skipping")
            continue
        
        # Pick a random frequency for this character
        freq = pick_random_frequency(char, freq_map)
        
        # Generate tone for this character
        tone = generate_tone(freq)
        audio_chunks.append(tone)
    
    return audio_chunks


def detect_frequencies_in_chunk(chunk):
    """
    Detect frequencies in a single audio chunk using FFT.
    Improved for short tones with better frequency resolution.
    
    Args:
        chunk: Audio samples (numpy array)
    
    Returns:
        list: Detected frequencies (strongest first)
    """
    if len(chunk) < 100:
        return []
    
    # Apply window to reduce spectral leakage
    windowed = chunk * np.hanning(len(chunk))
    
    # Zero-pad to improve frequency resolution for short tones
    padded_length = int(SAMPLE_RATE * 0.5)  # Pad to 0.5 second for better resolution
    if len(windowed) < padded_length:
        windowed = np.pad(windowed, (0, padded_length - len(windowed)), mode='constant')
    
    # FFT
    spectrum = fft(windowed)
    magnitude = np.abs(spectrum[:len(spectrum)//2])
    freqs = np.fft.fftfreq(len(windowed), 1/SAMPLE_RATE)[:len(spectrum)//2]
    
    # Find the single strongest frequency (expected for single character)
    peak_idx = np.argmax(magnitude)
    peak_freq = freqs[peak_idx]
    
    # Only return if there's a clear peak
    peak_magnitude = magnitude[peak_idx]
    if peak_magnitude > np.median(magnitude) * 2:  # Peak must be at least 2x median
        return [peak_freq]
    else:
        return []


def map_frequency_to_character(freq, freq_map):
    """
    Map a detected frequency to the closest character.
    Always returns the CLOSEST match (most reliable approach).
    
    Args:
        freq: Detected frequency in Hz
        freq_map: Frequency map {char: [freqs...], ...}
    
    Returns:
        str: Most likely character (closest frequency match)
    """
    best_char = None
    best_distance = float('inf')
    
    for char, freq_pool in freq_map.items():
        # Find closest frequency in this character's pool
        min_distance = min(abs(freq - f) for f in freq_pool)
        
        if min_distance < best_distance:
            best_distance = min_distance
            best_char = char
    
    # Always return the best match (closest frequency)
    # Even if outside tolerance, better to have a guess than '?'
    return best_char if best_char else '?'


def decode_audio_chunks(chunks, freq_map):
    """
    Decode audio chunks back to characters - ONE CHUNK = ONE CHARACTER.
    
    Args:
        chunks: List of audio chunks (one per character)
        freq_map: Frequency map {char: [freqs...], ...}
    
    Returns:
        list: Decoded characters
    """
    decoded_chars = []
    
    for chunk in chunks:
        # Detect frequency in this chunk
        detected_freqs = detect_frequencies_in_chunk(chunk)
        
        if detected_freqs:
            freq = detected_freqs[0]
            char = map_frequency_to_character(freq, freq_map)
            decoded_chars.append(char)
    
    return decoded_chars


def show_frequency_map(freq_map):
    """Display frequency map summary."""
    print(f"\n{'='*60}")
    print(f"FREQUENCY MAP")
    print(f"{'='*60}")
    print(f"Total characters: {len(freq_map)}")
    
    sample_size = min(5, len(freq_map))
    print(f"\nSample (first {sample_size} characters):")
    
    chars = list(freq_map.keys())[:sample_size]
    for char in chars:
        pool = freq_map[char]
        print(f"  '{char}': {len(pool)} frequencies - {min(pool)}-{max(pool)} Hz")
        if pool:
            print(f"         Samples: {pool[:3]}...")
    
    print(f"{'='*60}\n")

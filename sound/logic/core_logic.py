"""
CORE ENCRYPTION/DECRYPTION LOGIC
All the complex math and signal processing happens here.
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
    """Save the frequency map to JSON."""
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    
    # Convert lists to JSON-serializable format
    json_map = {char: freq_pool for char, freq_pool in freq_map.items()}
    
    with open(filepath, 'w') as f:
        json.dump(json_map, f, indent=2)
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
    Encode a message into audio chunks.
    
    Words (separated by spaces) are encoded as single sounds.
    Each letter in the word picks a random frequency from its range.
    All letters in a word play simultaneously.
    
    Args:
        message: String like "HELLO THERE"
        freq_map: Frequency mapping
    
    Returns:
        list: Audio chunks (each is a numpy array for one word)
    """
    message = message.upper()
    words = message.split(' ')
    
    audio_chunks = []
    
    for word in words:
        if not word:  # Skip empty words
            continue
        
        # Pick random frequency for each letter
        frequencies = []
        for char in word:
            if char in freq_map:
                freq = pick_random_frequency(char, freq_map)
                frequencies.append(freq)
            else:
                print(f"Warning: Character '{char}' not in map, skipping")
        
        if frequencies:
            # Stack all frequencies for this word
            stacked = stack_tones(frequencies)
            audio_chunks.append(stacked)
    
    return audio_chunks


def detect_frequencies_in_chunk(audio_chunk, tolerance=FREQUENCY_TOLERANCE):
    """
    Detect all dominant frequencies in an audio chunk using FFT.
    
    Args:
        audio_chunk: Audio samples (numpy array)
        tolerance: Frequency tolerance in Hz
    
    Returns:
        list: Detected frequencies in Hz
    """
    # Apply window function
    windowed = audio_chunk * np.hanning(len(audio_chunk))
    
    # FFT
    fft_result = np.abs(fft(windowed))
    freqs = np.fft.fftfreq(len(windowed), 1/SAMPLE_RATE)
    
    # Work with positive frequencies only
    positive_freqs = freqs[:len(freqs)//2]
    positive_fft = fft_result[:len(fft_result)//2]
    
    # Find peaks (dominant frequencies)
    detected = []
    threshold = np.max(positive_fft) * 0.1  # 10% of max amplitude
    
    for i in range(len(positive_freqs)):
        if positive_fft[i] > threshold:
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


def decode_audio_chunks(audio_chunks, freq_map):
    """
    Decode audio chunks back to text.
    
    Each chunk contains multiple stacked frequencies.
    Detects all frequencies and maps them to characters.
    
    Args:
        audio_chunks: List of audio arrays (one per word)
        freq_map: Frequency mapping
    
    Returns:
        list: Decoded words (may be scrambled)
    """
    decoded_words = []
    
    for chunk in audio_chunks:
        # Detect frequencies in this chunk
        detected_freqs = detect_frequencies_in_chunk(chunk)
        
        # Map each frequency to a character
        characters = []
        for freq in detected_freqs:
            char = map_frequency_to_character(freq, freq_map)
            if char != '?':
                characters.append(char)
        
        # Join characters (order may be scrambled)
        word = ''.join(characters)
        decoded_words.append(word)
    
    return decoded_words


def show_frequency_map(freq_map):
    """Display the frequency mapping in a readable format."""
    print("\n" + "="*70)
    print("FREQUENCY MAP - Randomized Pools for Each Character")
    print("="*70)
    print(f"Total frequencies per character: ~{len(freq_map[CHARACTERS[0]])}")
    print(f"Total range: {FREQUENCY_MIN}-{FREQUENCY_MAX} Hz")
    print(f"Distribution: COMPLETELY RANDOMIZED (no pattern, whole numbers)")
    print("-"*70)
    
    for char in CHARACTERS:
        freq_pool = freq_map[char]
        freq_min = min(freq_pool)
        freq_max = max(freq_pool)
        print(f"  {char:3s}: {len(freq_pool):3d} frequencies (range: {freq_min:8d}-{freq_max:8d} Hz)")
    
    print("="*70)
    print("Note: Each character's pool is COMPLETELY RANDOM.")
    print("When encoding, a random frequency from the pool is selected.")
    print("Same character picks DIFFERENT frequency each time!\n")
    print("="*70 + "\n")

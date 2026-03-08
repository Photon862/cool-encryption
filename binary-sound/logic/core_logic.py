"""
CORE ENCRYPTION/DECRYPTION LOGIC - Binary Sound
All the complex math and signal processing happens here.
Binary system: Each character converts to 8 bits (UTF-8)
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


def string_to_binary(text):
    """
    Convert string to binary using UTF-8 encoding.
    Each character = 8 bits.
    
    Example: "A" = 01000001 (8 bits)
    """
    binary_string = ''
    for char in text:
        # Get UTF-8 encoded byte(s)
        utf8_bytes = char.encode('utf-8')
        for byte in utf8_bytes:
            binary_string += format(byte, '08b')
    return binary_string


def binary_to_string(binary):
    """
    Convert binary string back to UTF-8 text.
    Groups binary into 8-bit chunks and decodes.
    """
    # Pad binary to multiple of 8
    while len(binary) % 8 != 0:
        binary += '0'
    
    # Split into 8-bit chunks
    bytes_list = []
    for i in range(0, len(binary), 8):
        byte_str = binary[i:i+8]
        bytes_list.append(int(byte_str, 2))
    
    # Decode UTF-8
    try:
        text = bytes(bytes_list).decode('utf-8', errors='replace')
        return text
    except:
        return "ERROR: Could not decode binary"


def create_frequency_map():
    """
    Create a completely random frequency map for 0 and 1.
    Each digit gets a pool of random frequencies (no overlap).
    """
    freq_range = FREQUENCY_MAX - FREQUENCY_MIN
    num_frequencies = int(freq_range / FREQUENCY_INCREMENT)
    freq_per_char = num_frequencies // NUM_CHARACTERS
    
    freq_map = {}
    for char in CHARACTERS:
        char_frequencies = []
        for _ in range(freq_per_char):
            random_freq = random.randint(FREQUENCY_MIN, FREQUENCY_MAX)
            char_frequencies.append(random_freq)
        freq_map[char] = sorted(set(char_frequencies))  # Remove duplicates
    
    return freq_map


def save_frequency_map(freq_map, filepath='key.json'):
    """Save frequency map to JSON."""
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


def load_frequency_map(filepath='key.json'):
    """Load frequency map from JSON."""
    with open(filepath, 'r') as f:
        json_map = json.load(f)
    freq_map = {char: freq_pool for char, freq_pool in json_map.items()}
    return freq_map


def pick_random_frequency(char, freq_map):
    """
    Pick a RANDOM frequency from the character's available pool.
    Each encoding picks a DIFFERENT random one from the pool.
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
        np.array: Audio samples
    """
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave.astype(np.float32)


def encode_message(message, freq_map):
    """
    Encode message to audio chunks using binary encoding.
    
    Process:
    1. Convert message to UTF-8 binary
    2. For each bit (0 or 1), pick random frequency from pool
    3. Generate tone for that frequency
    4. Return list of audio chunks
    """
    binary_string = string_to_binary(message)
    
    audio_chunks = []
    for bit in binary_string:
        frequency = pick_random_frequency(bit, freq_map)
        tone = generate_tone(frequency)
        audio_chunks.append(tone)
    
    return audio_chunks


def detect_frequency(audio_chunk, sample_rate=SAMPLE_RATE):
    """
    Detect the dominant frequency in an audio chunk using FFT.
    Uses zero-padding and parabolic interpolation for accuracy.
    """
    # Zero-pad for better frequency resolution
    padded_length = 2 ** int(np.ceil(np.log2(len(audio_chunk) * 4)))
    audio_padded = np.pad(audio_chunk, (0, padded_length - len(audio_chunk)), mode='constant')
    
    # FFT
    fft_result = fft(audio_padded)
    magnitude = np.abs(fft_result[:padded_length // 2])
    
    # Find peak
    peak_idx = np.argmax(magnitude)
    if peak_idx == 0:
        return None
    
    # Parabolic interpolation for sub-bin accuracy
    if peak_idx > 0 and peak_idx < len(magnitude) - 1:
        y1, y2, y3 = magnitude[peak_idx - 1], magnitude[peak_idx], magnitude[peak_idx + 1]
        a = (y3 - 2 * y2 + y1) / 2
        b = (y3 - y1) / 2
        if a != 0:
            delta = -b / (2 * a)
            peak_idx = peak_idx + delta
    
    # Convert bin to frequency
    freq_resolution = sample_rate / padded_length
    detected_freq = peak_idx * freq_resolution
    
    return detected_freq


def decode_message(audio_chunks, freq_map, sample_rate=SAMPLE_RATE):
    """
    Decode audio chunks back to original message.
    
    Process:
    1. For each chunk, detect frequency
    2. Match frequency to 0 or 1 in frequency map
    3. Build binary string
    4. Convert binary back to UTF-8 text
    """
    binary_string = ''
    
    for chunk in audio_chunks:
        detected_freq = detect_frequency(chunk, sample_rate)
        
        if detected_freq is None:
            binary_string += '?'
            continue
        
        # Match detected frequency to 0 or 1
        best_bit = None
        best_distance = float('inf')
        
        for bit in ['0', '1']:
            freq_pool = freq_map[bit]
            for freq in freq_pool:
                distance = abs(detected_freq - freq)
                if distance < best_distance:
                    best_distance = distance
                    best_bit = bit
        
        if best_distance <= FREQUENCY_TOLERANCE:
            binary_string += best_bit
        else:
            binary_string += '?'
    
    # Convert binary to text
    message = binary_to_string(binary_string)
    return message


def show_frequency_map(freq_map):
    """Display the frequency map."""
    for char in sorted(freq_map.keys()):
        freqs = freq_map[char]
        print(f"Bit '{char}': {len(freqs)} frequencies")
        print(f"  Range: {min(freqs)} - {max(freqs)} Hz")
        print(f"  Sample: {freqs[:5]}")

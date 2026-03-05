"""
Configuration for encoder and decoder logic.
These are used internally by the encoder/decoder classes.
"""

# Audio settings
SAMPLE_RATE = 44100  # Hz (44.1 kHz = CD quality)
TONE_DURATION = 0.1  # seconds per sound/word - optimized
AMPLITUDE = 0.3      # Volume (0.0 to 1.0)

# Frequency mapping settings
FREQUENCY_MIN = 100         # Very low Hz (avoids rumble)
FREQUENCY_MAX = 20000       # Near max audible frequency
FREQUENCY_INCREMENT = 10    # Optimal: 10 Hz steps for reliability

CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
NUM_CHARACTERS = len(CHARACTERS)

# Decoding settings
FREQUENCY_TOLERANCE = 8  # Hz tolerance for matching (increased for short tones)
FFT_WINDOW = 'hann'      # Window type for FFT (hann, hamming, blackman)

# File settings
FREQUENCY_MAP_FILE = 'frequency_map.json'
OUTPUT_DIR = 'output'

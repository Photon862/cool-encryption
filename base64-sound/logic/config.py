"""
Configuration for encoder and decoder logic.
These are used internally by the encoder/decoder classes.
"""

# Audio settings
SAMPLE_RATE = 44100  # Hz (44.1 kHz = CD quality)
TONE_DURATION = 0.22  # seconds per sound/character - optimized for speed
AMPLITUDE = 0.3      # Volume (0.0 to 1.0)

# Frequency mapping settings
FREQUENCY_MIN = 100         # Very low Hz (avoids rumble)
FREQUENCY_MAX = 20000       # Near max audible frequency
FREQUENCY_INCREMENT = 5     # Hz steps for reliability

CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/-'
NUM_CHARACTERS = len(CHARACTERS)

# Decoding settings
FREQUENCY_TOLERANCE = 8  # Hz tolerance for matching
FFT_WINDOW = 'hann'      # Window type for FFT (hann, hamming, blackman)

# File settings
FREQUENCY_MAP_FILE = 'key.json'
OUTPUT_DIR = 'output'

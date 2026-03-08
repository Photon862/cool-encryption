"""
CONFIGURATION - Binary Sound Encryption
Customize these values for your binary sound system
"""

SAMPLE_RATE = 44100  # Hz (44.1 kHz = CD quality)
TONE_DURATION = 0.03  # seconds per bit sound
AMPLITUDE = 0.3      # Volume (0.0 to 1.0)

FREQUENCY_MIN = 100         # Minimum frequency (Hz)
FREQUENCY_MAX = 20000       # Maximum frequency (Hz)
FREQUENCY_INCREMENT = 1     # Hz step between available frequencies

FREQUENCY_TOLERANCE = 100   # Hz tolerance for frequency detection
FFT_WINDOW = 4096           # FFT window size for analysis

CHARACTERS = '01'  # Only binary: 0 and 1
NUM_CHARACTERS = len(CHARACTERS)

FREQUENCY_MAP_FILE = 'key.json'
OUTPUT_DIR = 'output'

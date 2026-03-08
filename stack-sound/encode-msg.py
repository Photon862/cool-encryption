"""
ENCODE MESSAGE - Run this to encode your message
"""

from datetime import datetime
import csv
import os
import sys
import importlib.util

# Load frequency variables from generate_map.py
spec = importlib.util.spec_from_file_location("generate_map_module", "generate_map.py")
generate_map_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_map_module)

FREQUENCY_MIN = generate_map_module.FREQUENCY_MIN
FREQUENCY_MAX = generate_map_module.FREQUENCY_MAX
FREQUENCY_INCREMENT = generate_map_module.FREQUENCY_INCREMENT

# ============================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================
TEST_MESSAGE = "lets see if this works again"  # EDIT THIS MESSAGE TO ENCODE

SAMPLE_RATE = 44100  # Hz (44.1 kHz = CD quality)
TONE_DURATION = 0.22  # seconds per sound/word - optimized for speed
AMPLITUDE = 0.3      # Volume (0.0 to 1.0)

CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

FREQUENCY_MAP_FILE = 'frequency_map.json'
OUTPUT_DIR = 'output'

# Update logic config with these values BEFORE importing Encoder
import logic.config as config
config.SAMPLE_RATE = SAMPLE_RATE
config.TONE_DURATION = TONE_DURATION
config.AMPLITUDE = AMPLITUDE
config.FREQUENCY_MIN = FREQUENCY_MIN
config.FREQUENCY_MAX = FREQUENCY_MAX
config.FREQUENCY_INCREMENT = FREQUENCY_INCREMENT
config.CHARACTERS = CHARACTERS
config.NUM_CHARACTERS = len(CHARACTERS)
config.FREQUENCY_MAP_FILE = FREQUENCY_MAP_FILE

# ============================================
# ENCODING
# ============================================

from logic.encoder import Encoder

def log_action(action_type, message, tone_duration=None, freq_min=None, freq_max=None, freq_increment=None):
    """Log action to log.csv with timestamp, tone duration, and frequency settings."""
    log_file = f'{OUTPUT_DIR}/log.csv'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Create file with header if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Log'])
    # Format log entry as requested
    log_entry = f'ENCODED, {message}, ToneDuration={tone_duration}, {freq_min}-{freq_max}HZ, Increment={freq_increment}'
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, log_entry])

if __name__ == "__main__":
    encoder = Encoder()
    encoder.encode(TEST_MESSAGE, f'{OUTPUT_DIR}/test.wav')
    print(f"✓ Encoded: {TEST_MESSAGE}")
    log_action('ENCODED', TEST_MESSAGE, TONE_DURATION, FREQUENCY_MIN, FREQUENCY_MAX, FREQUENCY_INCREMENT)

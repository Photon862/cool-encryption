"""
ENCODE MESSAGE - Run this to encode your message
Converts text to base64, then encodes base64 string to audio
"""

from datetime import datetime
import csv
import os
import sys
import base64
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
TEST_MESSAGE = "this is testing with a tone duration of 0.01 seconds hopefully it works"  # EDIT THIS MESSAGE TO ENCODE

SAMPLE_RATE = 44100  # Hz (44.1 kHz = CD quality)
TONE_DURATION = 0.01  # seconds per sound/character - optimized for speed
AMPLITUDE = 0.3      # Volume (0.0 to 1.0)

CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/-'

FREQUENCY_MAP_FILE = 'key.json'
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
    # Format log entry
    log_entry = f'ENCODED, {message}, ToneDuration={tone_duration}, {freq_min}-{freq_max}HZ, Increment={freq_increment}'
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, log_entry])

if __name__ == "__main__":
    # Convert message to base64
    original_message = TEST_MESSAGE
    base64_bytes = base64.b64encode(original_message.encode('utf-8'))
    base64_string = base64_bytes.decode('utf-8')
    
    # Remove '=' padding characters
    base64_string_no_padding = base64_string.replace('=', '')
    
    print(f"Original message: {original_message}")
    print(f"Base64 string:    {base64_string}")
    print(f"Base64 (no =):    {base64_string_no_padding}")
    print(f"Characters to encode: {len(base64_string_no_padding)}")
    print()
    
    # Encode to audio
    encoder = Encoder()
    encoder.encode(base64_string_no_padding, f'{OUTPUT_DIR}/test.wav')
    
    print(f"✓ Encoded: {original_message}")
    log_action('ENCODED', original_message, TONE_DURATION, FREQUENCY_MIN, FREQUENCY_MAX, FREQUENCY_INCREMENT)

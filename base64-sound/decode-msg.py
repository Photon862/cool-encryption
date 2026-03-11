"""
DECODE MESSAGE - Run this to decode the encoded message
Decodes audio to base64 string, then converts base64 to original text
"""

from datetime import datetime
import csv
import os
import base64
import importlib.util

# Load variables from encode-msg.py
spec = importlib.util.spec_from_file_location("encode_msg", "encode-msg.py")
encode_msg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(encode_msg)

OUTPUT_DIR = encode_msg.OUTPUT_DIR

# Update logic config with these values BEFORE importing Decoder
import logic.config as config
config.TONE_DURATION = encode_msg.TONE_DURATION
config.SAMPLE_RATE = encode_msg.SAMPLE_RATE
config.FREQUENCY_MIN = encode_msg.FREQUENCY_MIN
config.FREQUENCY_MAX = encode_msg.FREQUENCY_MAX
config.FREQUENCY_INCREMENT = encode_msg.FREQUENCY_INCREMENT

from logic.decoder import Decoder

def add_base64_padding(base64_string):
    """
    Add '=' padding back to base64 string to make it valid.
    Base64 strings should have length divisible by 4.
    """
    remainder = len(base64_string) % 4
    if remainder != 0:
        base64_string += '=' * (4 - remainder)
    return base64_string

def decode_base64_message(base64_string):
    """
    Decode base64 string back to original message.
    
    Args:
        base64_string: Base64 encoded string (with or without padding)
    
    Returns:
        str: Decoded original message
    """
    # Add padding if needed
    padded = add_base64_padding(base64_string)
    
    try:
        decoded_bytes = base64.b64decode(padded)
        original_message = decoded_bytes.decode('utf-8')
        return original_message
    except Exception as e:
        return f"[ERROR: Could not decode base64: {e}]"

if __name__ == "__main__":
    decoder = Decoder()
    
    # Decode audio to characters
    decoded_chars = decoder.decode(f'{OUTPUT_DIR}/test.wav')
    decoded_base64 = ''.join(decoded_chars)
    
    print(f"Decoded base64 string (no padding): {decoded_base64}")
    
    # Convert base64 back to original message
    original_message = decode_base64_message(decoded_base64)
    print(f"Decoded original message: {original_message}")
    print()
    
    # Log in 1 line
    csv.writer(open(f'{OUTPUT_DIR}/log.csv', 'a', newline='')).writerow([
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        f"DECODED, {original_message}"
    ])

"""
DECODE MESSAGE - Run this to decode the encoded message
"""

from datetime import datetime
import csv
import os
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

decoder = Decoder()
decoded = decoder.decode(f'{OUTPUT_DIR}/test.wav')
decoded_msg = ' '.join(decoded)
print(f"✓ Decoded: {decoded_msg}")

# Log in 1 line
csv.writer(open(f'{OUTPUT_DIR}/log.csv', 'a', newline='')).writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "DECODED", decoded_msg])

"""
DECODER - Simple interface to decode audio files back to messages.
Uses core_logic for the heavy lifting.
"""

import wave
import numpy as np
import os
from .config import SAMPLE_RATE, TONE_DURATION, FREQUENCY_MAP_FILE
from .core_logic import (
    load_frequency_map, decode_message, show_frequency_map
)


class Decoder:
    """Decode WAV files back to text messages using binary decoding."""
    
    def __init__(self):
        """Initialize decoder with frequency map."""
        if not os.path.exists(FREQUENCY_MAP_FILE):
            raise FileNotFoundError(
                f"ERROR: Required frequency map file '{FREQUENCY_MAP_FILE}' not found. "
                f"Cannot decode without the key."
            )
        self.freq_map = load_frequency_map(FREQUENCY_MAP_FILE)
        print(f"✓ Loaded frequency map from {FREQUENCY_MAP_FILE}")
    
    def decode(self, audio_file):
        """
        Decode a WAV file back to original message.
        
        Args:
            audio_file: Path to WAV file
        
        Returns:
            str: Decoded message
        """
        if not os.path.exists(audio_file):
            print(f"Error: File '{audio_file}' not found")
            return None
        
        # Load audio
        print(f"Loading: {audio_file}")
        audio_data = self._load_wav(audio_file)
        
        if audio_data is None:
            return None
        
        # Split audio into chunks (one per bit) using actual TONE_DURATION
        samples_per_bit = int(SAMPLE_RATE * TONE_DURATION)
        audio_chunks = []
        
        for i in range(0, len(audio_data), samples_per_bit):
            chunk = audio_data[i:i+samples_per_bit]
            if len(chunk) > 0:
                audio_chunks.append(chunk)
        
        print(f"✓ Detected {len(audio_chunks)} bits")
        
        # Decode message
        message = decode_message(audio_chunks, self.freq_map, SAMPLE_RATE)
        print(f"Decoded message: {message}")
        
        return message
    
    def _load_wav(self, filepath):
        """Load audio data from WAV file."""
        try:
            with wave.open(filepath, 'r') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0
                return audio_data
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def show_map(self):
        """Show the frequency map."""
        show_frequency_map(self.freq_map)


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python decode-msg.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    decoder = Decoder()
    decoder.decode(audio_file)


if __name__ == '__main__':
    main()

"""
ENCODER - Simple interface to encode messages to audio files using tap code.
Uses core_logic for the heavy lifting.
"""

import wave
import numpy as np
import os
from .config import SAMPLE_RATE, OUTPUT_DIR, FREQUENCY_MAP_FILE
from .core_logic import (
    create_frequency_map, save_frequency_map, load_frequency_map,
    encode_message, show_frequency_map, character_to_tap_code
)


class Encoder:
    """Encode text messages into WAV files using tap code."""
    
    def __init__(self):
        """Initialize encoder with frequency map."""
        if not os.path.exists(FREQUENCY_MAP_FILE):
            raise FileNotFoundError(
                f"ERROR: Required frequency map file '{FREQUENCY_MAP_FILE}' not found. "
                f"Please generate it using generate_map.py first."
            )
        self.freq_map = load_frequency_map(FREQUENCY_MAP_FILE)
        print(f"✓ Loaded frequency map from {FREQUENCY_MAP_FILE}")
    
    def encode(self, message, output_file=None):
        """
        Encode a message to WAV file using tap code.
        
        Each character is converted to tap code (2 digits).
        Each digit gets its own individual sound.
        
        Example:
            encoder = Encoder()
            encoder.encode("HELLO", "output/message.wav")
            # H=32, E=51, L=13, L=13, O=43
            # Output: 6 individual tones for [3,2,5,1,1,3,1,3,4,3]
        
        Args:
            message: String to encode (e.g., "HELLO")
            output_file: Output WAV file path (optional)
        
        Returns:
            str: Path to output WAV file
        """
        if not output_file:
            output_file = os.path.join(OUTPUT_DIR, "encoded.wav")
        
        # Show tap code conversion
        print(f"Message: {message}")
        converted = ""
        for char in message.upper():
            if char == ' ':
                continue
            try:
                row, col = character_to_tap_code(char)
                converted += f"{row}{col} "
            except ValueError:
                pass
        print(f"Tap code: {converted}")
        
        # Encode message
        audio_chunks = encode_message(message, self.freq_map)
        
        if not audio_chunks:
            print("Error: No valid characters to encode")
            return None
        
        # Concatenate all chunks (each chunk is one digit's sound)
        full_audio = np.concatenate(audio_chunks)
        
        # Save as WAV
        self._save_wav(full_audio, output_file)
        return output_file
    
    def _save_wav(self, audio_data, filepath):
        """Save audio data to WAV file."""
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        # Convert float32 to int16
        audio_int16 = np.int16(audio_data * 32767)
        
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio_int16.tobytes())
        
        duration = len(audio_data) / SAMPLE_RATE
        print(f"✓ Saved to '{filepath}' ({duration:.2f}s)")
    
    def show_map(self):
        """Show the frequency map."""
        show_frequency_map(self.freq_map)


def main():
    """Example usage."""
    encoder = Encoder()
    encoder.show_map()
    encoder.encode("HELLO WORLD", "output/hello_world.wav")


if __name__ == "__main__":
    main()

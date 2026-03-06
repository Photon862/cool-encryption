"""
DECODER - Simple interface to decode WAV files back to text using tap code.
Uses core_logic for the heavy lifting.
"""

import wave
import numpy as np
import os
from .config import SAMPLE_RATE, FREQUENCY_MAP_FILE, TONE_DURATION
from .core_logic import (
    load_frequency_map, detect_frequencies_in_chunk,
    map_frequency_to_digit, decode_audio_chunks, tap_code_to_character
)


class Decoder:
    """Decode WAV files back into text messages using tap code."""
    
    def __init__(self):
        """Initialize decoder with frequency map."""
        if os.path.exists(FREQUENCY_MAP_FILE):
            self.freq_map = load_frequency_map(FREQUENCY_MAP_FILE)
            print(f"✓ Loaded frequency map from {FREQUENCY_MAP_FILE}")
        else:
            raise FileNotFoundError(f"Frequency map not found: {FREQUENCY_MAP_FILE}")
    
    def decode(self, wav_file):
        """
        Decode a WAV file back to text using tap code.
        
        Example:
            decoder = Decoder()
            text = decoder.decode("output/message.wav")
            print(text)  # e.g., "HELLO"
        
        Args:
            wav_file: Path to WAV file
        
        Returns:
            str: Decoded message
        """
        # Load WAV file
        audio_chunks = self._load_wav(wav_file)
        
        if not audio_chunks:
            print("Error: No audio data found")
            return ""
        
        # Decode chunks using tap code logic
        message = decode_audio_chunks(audio_chunks, self.freq_map)
        return message
    
    def _load_wav(self, filepath):
        """
        Load WAV file and split into chunks (one per digit/tone).
        """
        with wave.open(filepath, 'rb') as wav:
            n_channels = wav.getnchannels()
            n_frames = wav.getnframes()
            audio_bytes = wav.readframes(n_frames)
            
            # Convert to mono
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
            if n_channels == 2:
                audio_data = audio_data.reshape(-1, 2).mean(axis=1)
            
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # Split into chunks (one per tone/digit)
        chunk_size = int(SAMPLE_RATE * TONE_DURATION)
        chunks = []
        
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i+chunk_size]
            if len(chunk) > 0:
                chunks.append(chunk)
        
        return chunks
    
    def show_details(self, wav_file):
        """Show detailed frequency detection for a WAV file."""
        chunks = self._load_wav(wav_file)
        decoded_text = self.decode(wav_file)
        
        print(f"\n{'='*60}")
        print(f"DETAILED ANALYSIS: {wav_file}")
        print(f"{'='*60}")
        
        decoded_digits = []
        for digit_idx, chunk in enumerate(chunks, 1):
            detected_freqs = detect_frequencies_in_chunk(chunk)
            
            if detected_freqs:
                freq = detected_freqs[0]
                digit = map_frequency_to_digit(freq, self.freq_map)
                decoded_digits.append(digit)
                print(f"Tone {digit_idx}: {freq:8.1f} Hz -> Digit '{digit}'")
            else:
                print(f"Tone {digit_idx}: No frequency detected")
        
        # Show tap code pairs
        print(f"\n{'='*60}")
        print("TAP CODE DECODING:")
        print("-"*60)
        for i in range(0, len(decoded_digits), 2):
            if i + 1 < len(decoded_digits):
                row = decoded_digits[i]
                col = decoded_digits[i + 1]
                char = tap_code_to_character(int(row), int(col))
                print(f"  ({row},{col}) -> '{char}'")
            elif i < len(decoded_digits):
                print(f"  ({decoded_digits[i]},?) -> Incomplete pair")
        
        print(f"\n{'='*60}")
        print(f"DECODED MESSAGE: {decoded_text}")
        print(f"{'='*60}\n")


def main():
    """Example usage."""
    decoder = Decoder()
    
    # Decode a message
    text = decoder.decode("output/test.wav")
    print(f"✓ Decoded: {text}")
    
    # Show details
    decoder.show_details("output/test.wav")


if __name__ == "__main__":
    main()


def main():
    """Example usage."""
    decoder = Decoder()
    
    # Decode a message
    words = decoder.decode("output/hello_world.wav")
    print(f"Decoded: {' '.join(words)}")
    
    # Show details
    decoder.show_details("output/hello_world.wav")


if __name__ == "__main__":
    main()

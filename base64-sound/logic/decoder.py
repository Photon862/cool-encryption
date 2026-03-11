"""
DECODER - Simple interface to decode WAV files back to text.
Uses core_logic for the heavy lifting.
Decodes character-by-character from base64 audio.
"""

import wave
import numpy as np
import os
from .config import SAMPLE_RATE, FREQUENCY_MAP_FILE, TONE_DURATION
from .core_logic import (
    load_frequency_map, detect_frequencies_in_chunk,
    map_frequency_to_character, decode_audio_chunks
)


class Decoder:
    """Decode WAV files back into text messages."""
    
    def __init__(self):
        """Initialize decoder with frequency map."""
        if os.path.exists(FREQUENCY_MAP_FILE):
            self.freq_map = load_frequency_map(FREQUENCY_MAP_FILE)
            print(f"✓ Loaded frequency map from {FREQUENCY_MAP_FILE}")
        else:
            raise FileNotFoundError(f"Frequency map not found: {FREQUENCY_MAP_FILE}")
    
    def decode(self, wav_file):
        """
        Decode a WAV file back to characters.
        
        Example:
            decoder = Decoder()
            text = decoder.decode("output/message.wav")
            print(text)
        
        Args:
            wav_file: Path to WAV file
        
        Returns:
            list: Decoded characters
        """
        # Load WAV file
        audio_chunks = self._load_wav(wav_file)
        
        if not audio_chunks:
            print("Error: No audio data found")
            return []
        
        # Decode chunks (one chunk = one character)
        chars = decode_audio_chunks(audio_chunks, self.freq_map)
        return chars
    
    def _load_wav(self, filepath):
        """
        Load WAV file and split into chunks (one per character).
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
        
        # Split into chunks (one per character)
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
        chars = self.decode(wav_file)
        
        print(f"\n{'='*60}")
        print(f"DETAILED ANALYSIS: {wav_file}")
        print(f"{'='*60}")
        print(f"Total characters decoded: {len(chars)}")
        print(f"Characters: {''.join(chars)}\n")
        
        for char_idx, chunk in enumerate(chunks, 1):
            print(f"Character {char_idx}: '{chars[char_idx-1] if char_idx <= len(chars) else '?'}'")
            print("-" * 40)
            
            detected_freqs = detect_frequencies_in_chunk(chunk)
            print(f"  Detected {len(detected_freqs)} frequencies:")
            
            for freq_idx, freq in enumerate(detected_freqs, 1):
                char = map_frequency_to_character(freq, self.freq_map)
                print(f"    {freq_idx}. {freq:8.1f} Hz -> '{char}'")
        
        print(f"\n{'='*60}\n")


def main():
    """Example usage."""
    decoder = Decoder()
    decoded = decoder.decode('output/test.wav')
    print(f"✓ Decoded: {''.join(decoded)}")


if __name__ == "__main__":
    main()

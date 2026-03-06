# Cool Encryption - Sound-Based Message Encoder

**What is this?**

This project lets you encode messages into sound. Two different encryption systems are available:
- **sound1**: Original character-based system (A-Z, 0-9)
- **sound2**: Tap code system with individual digit sounds (more efficient)

As far as I know, it's nearly impossible to decode without the json file key.

---

## Two Systems

### Sound1 - Character-Based System

The original system that encodes characters directly.

**How it works:**

1. Generates a random frequency map for each character (A-Z, 0-9) with a given range and increment (e.g., 100-20,000 Hz with 10 Hz steps)

```json
{
  "A": [110, 180, 140, ...],
  "B": [120, 290, 200, ...],
  ...
}
```

2. Converts the message into sound (each character has multiple frequency options to pick from)

3. Combines all frequencies for each word into one stacked sound - so "HELLO" creates a single sound containing H, E, L, L, O frequencies all at once

4. Longer tone duration required for reliable detection (typically 0.13s or higher)

**Features:**
- Each character picks a random frequency from its pool on every encode
- Character "E" repeated multiple times won't sound identical (adds randomness)
- Better for preserving word structure in original format

**Limitations:**
- Longer audio files (each word = one chunk)
- Needs longer tone durations for accuracy
- Message decoding may mix up character order within words (order preserved between words)

---

### Sound2 - Tap Code System

A more efficient system using tap code (like prison communication) with individual digit sounds and space support.

**How it works:**

1. Converts each character to tap code (2 digits where row=1-5, column=1-5):
   - A = (1,1), B = (1,2), H = (2,3), I = (2,4), J = (2,5), Z = (5,5)
   - C and K both = (1,3) [only C/K are merged]
   - I and J are completely separate codes!

2. Generates frequency map for digits 1-9 (1-5 for characters, 6-9 for space markers):

```json
{
  "1": [freq1, freq2, ...],
  "2": [freq1, freq2, ...],
  ...
  "6": [freq1, freq2, ...],  // Used in space codes
  "7": [freq1, freq2, ...],  // Used in space codes
  "8": [freq1, freq2, ...],  // Used in space codes
  "9": [freq1, freq2, ...]   // Used in space codes
}
```

3. Encodes each digit as an individual sound (NOT stacked):
   - "HELLO" → [2,3,1,5,3,1,3,1,3,4] → 10 separate tones
   - "HELLO WORLD" → includes space code (any pair with 6-9) → multiple tones

4. Space handling: Any digit pair where at least one digit is 6-9 is decoded as a space
   - Examples: (6,2), (3,7), (9,1), (8,8) all = space
   - Encoding randomly picks from valid space pairs for randomness

5. Short tone durations work fine (0.03s-0.08s, optimized detection with FFT zero-padding and local maxima finding)

**Features:**
- Spaces are preserved in messages
- Much shorter audio files (individual digit sounds)
- Works with very short tone durations
- Improved frequency detection using zero-padding and parabolic interpolation
- More efficient encoding/decoding

**Limitations:**
- C/K and I/J are merged (same tap code)
- Individual digits detected separately (no word grouping)

---

## Usage Instructions for both sound1 and sound2

```bash
cd sound1

# 1. Generate a new frequency map
python generate_map.py

# 2. Edit TEST_MESSAGE in encode-msg.py

# 3. Encode the message
python encode-msg.py

# 4. Decode the message
python decode-msg.py
```

---

## Frequency Map Security

The `frequency_map.json` file is your encryption key. Without it, the audio file is just noise.

**Tips:**
- Keep your frequency map file secret
- Use different maps for different messages
- Maps are stored in JSON - each digit/character maps to a pool of frequencies
- Example: digit "1" might have 2,211 random frequencies spread across 100-20,000 Hz

---

## Technical Details

### Sound1 - Encoding Process
1. Message "HELLO" → split into words → ["HELLO"]
2. Each character picks random frequency from its pool
3. All frequencies for "HELLO" stacked together (mixed)
4. Output: 1 audio chunk (one sound file for the whole word)

### Sound2 - Encoding Process
1. Message "HELLO WORLD" → "HELLO WORLD"
2. Convert to tap code (with spaces):
   - H=(2,3), E=(1,5), L=(3,1), L=(3,1), O=(3,4)
   - Space = random pair with 6-9 (e.g., (6,8) or (4,7) or (9,9))
   - W=(5,2), O=(3,4), R=(4,2), L=(3,1), D=(1,4)
3. Flatten to digits: [2,3,1,5,3,1,3,1,3,4, X,Y, 5,2,3,4,4,2,3,1,1,4] where X,Y is space pair with at least one 6-9
4. Each digit picks random frequency from digit's pool
5. Output: Individual audio chunks (one tone per digit)

---

## Notes

**General Limitations:**
- Audio quality matters (compression or noise affects decoding)
- Frequency increment affects accuracy (smaller = more frequencies, better randomness but more data)
- Tone duration trade-off: shorter = faster but harder to detect; longer = slower but more reliable

**Future Improvements:**
- Password-based key generation instead of random maps
- Error correction codes for noisy channels
- Variable tone durations for adaptive encoding
- Support for more characters through extended tap code

---

## Comparison Table

| Feature | Sound1 | Sound2 |
|---------|--------|--------|
| Encoding | Character-based | Tap code + digits |
| Message Format | Words grouped | Individual digits |
| Spaces | No | Yes |
| Minimum Tone Duration | 0.13s+ | 0.03-0.08s |
| Audio Size | Smaller | Slightly larger (per char) |
| Speed | Slower | Faster |
| Efficiency | Good | Better |
| C/K Merging | No | Yes (only C/K) |
| I/J Merging | No | No (I and J are separate) |
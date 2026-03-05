# Cool Encryption - Sound-Based Message Encoder

**What is this?**

This project lets you encode any text message as a WAV audio file using random sound frequencies, and decode it back to text—if you have the secret frequency map. It's not traditional cryptography, but a fun, privacy-focused way to hide messages in sound. Lose the map, lose the message!

---

## The Core Idea

At its heart, this system is about **randomness and sound frequencies**. Here's the deal:

1. You generate a `frequency_map.json` file that assigns random frequencies to each letter
2. You use that file to encode messages into sound
3. You use that same file to decode messages from sound
4. **Without that file, the message is basically gone forever**

The frequency map is your key. Lose it, and even if you have the audio file, you can't decode it.

---

## Step 1: Generating the Frequency Map (`generate_map.py`)

### How It Works

When you run `generate_map.py`, here's what happens:

1. **Define your range**: Pick your frequency limits (default: 100 Hz - 20,000 Hz) and increment (default: 10 Hz)
   - 100 Hz: Safe minimum that even low-end computers can handle
   - 20,000 Hz: Upper limit for consumer audio hardware
   - Increment: Spacing between available frequencies (10 Hz means 100, 110, 120, 130, etc.)

2. **Calculate available frequencies**:
   - With 100-20,000 Hz and 10 Hz increments → ~1,990 possible frequencies
   - You have 36 characters (A-Z + 0-9)
   - Each character gets roughly 55 randomly selected frequencies from that pool

3. **Assign randomness**:
   - For character "A": Randomly pick 55 frequencies from the 1,990 available
   - For character "B": Randomly pick 55 different frequencies from the remaining pool
   - For character "H": Randomly pick 55 different frequencies
   - **No two characters share the same frequency**

4. **Save to JSON**:
   ```json
   {
     "A": [1024, 5431, 8732, 2109, ...],
     "B": [3421, 7654, 1032, 9876, ...],
     "H": [4892, 6123, 9876, 1200, ...]
   }
   ```

### The Critical Point

This JSON file is **your encryption key**. Share it with the person you want to communicate with. Delete it, and you've deleted the ability to decode all messages encoded with it.

---

## Step 2: Encoding Messages (`encode-msg.py`)

### The Process

#### Word Split
Your message gets broken into words:
- Input: `"HELLO WORLD"`
- Split: `["HELLO", "WORLD"]`

#### Letter-by-Letter Frequency Selection
For each word, you look at each letter:
- Find the letter "H" in your frequency map → You have 55 random options
- **Pick one randomly** → Maybe 4,892 Hz (different next time!)
- Find the letter "E" in your frequency map → You have 55 random options
- **Pick one randomly** → Maybe 7,634 Hz (could be different next time!)
- Continue for each letter

So if you encode "HELLO WORLD" three times:
- First time: H=4892, E=7634, L=3421, L=2109, O=9876...
- Second time: H=6123, E=5431, L=8732, L=1024, O=2891... (all different!)
- Third time: H=1200, E=9876, L=5634, L=4123, O=3421... (all different again!)

#### Word Stacking (Playing Multiple Frequencies Together)
All letters in **one word** are played **at the same time**:
- Word "HI": 
  - H's frequency (4,892 Hz) + I's frequency (8,732 Hz) play simultaneously
  - Result: One complex sound with both frequencies mixed in

### Why Stack Words?
**Convenience**: It's faster to play 3 words as 3 sounds instead of 9-15 individual letter sounds.

### The Problem with Stacking
Here's the weakness: **If someone hears your encoded audio, they know:**
- How many words are in your message (count the gaps/chunks)
- How many letters are in each word (count the frequencies in each chunk)

Example:
- Audio chunk 1: 5 frequencies → 5-letter word
- Audio chunk 2: 5 frequencies → 5-letter word
- Audio chunk 3: 5 frequencies → 5-letter word
- **An attacker now knows it's 3 five-letter words** → "HELLO WORLD THERE"? 

### Alternative: Tone Each Letter Separately
Instead of stacking words, you could tone each letter individually:
- No word gaps
- No way to tell where words end/begin
- Harder for attackers to recognize patterns
- Currently not implemented, but easier than it sounds

---

## Step 3: Audio Generation and Playback

### How Sound is Created
Each frequency is a **sine wave**. When you stack multiple frequencies, they overlap:

```
H frequency (4892 Hz): ~~~~/~~~~\~~~
I frequency (8732 Hz): ~~~~~~/~~~~~\~~~~~~  
Mixed result:          Combined overlapping waves
```

### Tone Duration Parameter
This controls **how long each word plays**:
- `TONE_DURATION = 0.1` → Fast, might miss some frequencies (less accurate)
- `TONE_DURATION = 0.2` → Balanced, good accuracy
- `TONE_DURATION = 0.5` → Slow, very accurate but takes longer

The longer the tone, the more time the machine has to "hear" and detect all the frequencies.

### Testing and Tuning
The system has limits. Play around with:
- **Increment size**: 10 Hz, 20 Hz, 50 Hz (larger increments = fewer frequency choices per character)
- **Tone duration**: 0.1s, 0.15s, 0.2s, 0.25s
- **Frequency range**: Stick with 100 Hz minimum, max can be 16,000-20,000 depending on hardware

**You'll find that:**
- Too-small increments + too-fast speed = decoding breaks (machine can't distinguish)
- Too-large increments + too-slow speed = wastes time unnecessarily
- There's a sweet spot - experiment to find it for your hardware

---

## Step 4: Decoding Messages (`decode-msg.py`)

### The Reverse Process

1. **Load audio file**: Read `output/test.wav`
2. **Split into chunks**: Find where words start and stop
3. **Analyze each chunk**:
   - Use FFT (Fast Fourier Transform) to break down the mixed frequencies
   - Identify which frequencies are present in the sound
   - Example: Detected [4892 Hz, 8732 Hz]

4. **Map frequencies back to letters**:
   - 4892 Hz → Search frequency map → Found in character "H"
   - 8732 Hz → Search frequency map → Found in character "I"
   - Result: "HI"

5. **Reconstruct message**:
   - Word 1: "HELLO"
   - Word 2: "WORLD"
   - Final: "HELLO WORLD"

### Why Exact Frequency Matching Matters
Because frequencies are generated with slight variations (rounding, hardware differences, audio compression), the decoder looks for the **closest match** within a tolerance range (usually 5-10 Hz):
- Decoded: 4890 Hz → Close to 4892 Hz in map → Matches "H" ✓
- Decoded: 8735 Hz → Close to 8732 Hz in map → Matches "I" ✓

---

## Configuration: What You Can Adjust

### In `encode-msg.py` or `generate_map.py`:

| Parameter | Default | What It Does |
|-----------|---------|--------------|
| `FREQUENCY_MIN` | 100 Hz | Lowest tone frequency (safe for all hardware) |
| `FREQUENCY_MAX` | 20,000 Hz | Highest tone frequency (adjust for low-end hardware) |
| `FREQUENCY_INCREMENT` | 10 Hz | Gap between available frequencies (smaller = more options, harder to decode) |
| `TONE_DURATION` | 0.2s | How long each word's sound plays (longer = more accurate) |
| `SAMPLE_RATE` | 44,100 Hz | Audio quality in samples per second |
| `AMPLITUDE` | 0.3 | Volume (0.0 = silent, 1.0 = maximum) |

### Tips for Experiments:
- **For speed**: Reduce `TONE_DURATION` to 0.15s and increase `FREQUENCY_INCREMENT` to 20Hz
- **For accuracy**: Keep `TONE_DURATION` at 0.2s and `FREQUENCY_INCREMENT` at 10Hz
- **For low-end computers**: Lower `FREQUENCY_MAX` to 16,000 Hz
- **For better security**: Increase frequency range and reduce increment (more unique freq per char)

---

## Security: What's Strong, What's Weak

### Strong Points:
1. **Randomness**: Same message encodes differently each time (can't pattern-match)
2. **Key-based**: Without `frequency_map.json`, audio is useless
3. **Unusual format**: Audio files don't look like encrypted data
4. **Per-character entropy**: Each letter has 50+ random options

### Weak Points:
1. **Word structure leaks**: Stacking words reveals message length and word lengths
2. **Key distribution**: How do you safely share the frequency map?
3. **Frequency analysis**: If someone has many encoded messages, they might reverse-engineer the map
4. **Hardware artifacts**: Audio quality issues can cause decoding failures
5. **Not cryptographically designed**: This is privacy-focused, not military-grade

---

## When to Use This:

✓ **Good for:**
- Fun, casual encrypted messages between friends
- Hiding messages in plain sight (sounds like random noise/music)
- Learning how encryption and signal processing work
- Privacy-focused communication (not high-security)

✗ **Not good for:**
- Protecting against sophisticated attackers
- Bank accounts, passwords, classified info
- Long-term storage (frequency map could be lost)
- Situations where word/letter structure reveals meaning

---

## Quick Start

### 1. Generate Frequency Map (First Time Only)
```bash
python generate_map.py
```
This creates `frequency_map.json` - **KEEP THIS FILE SAFE**

### 2. Encode a Message
```bash
# Edit encode-msg.py - change TEST_MESSAGE to your text
python encode-msg.py
# Output: output/test.wav (your encrypted audio)
```

### 3. Decode the Message
```bash
python decode-msg.py
# Output: Prints decoded message to console
```

### 4. Share Safely
- Share `output/test.wav` however you want (no security risk)
- Share `frequency_map.json` **securely** with the person who needs to decode (this is your key)

---

## Troubleshooting

### Can't Decode? Gibberish Output?
- Make sure you have the **exact same** `frequency_map.json` used for encoding
- Even tiny differences break decoding

### Audio Breaks or Missing Frequencies?
- Increase `TONE_DURATION` to 0.22-0.25s
- Decrease `FREQUENCY_INCREMENT` to 5Hz (more unique frequencies per letter)
- Lower `FREQUENCY_MAX` if on low-end hardware

### Encoding/Decoding Too Slow?
- Decrease `TONE_DURATION` to 0.15s (tradeoff: slightly less accurate)
- Increase `FREQUENCY_INCREMENT` to 20Hz (fewer options per letter, less secure)
- Reduce `SAMPLE_RATE` to 22,050 Hz (lower quality but faster)

### Too Much Distortion in Audio?
- Lower `AMPLITUDE` to 0.2 or even 0.1
- Shorter `TONE_DURATION` (less chance of clipping)

---

## The Bottom Line

This system proves **encryption doesn't have to be mathematical**. It's based on:
- **Physics**: Sound waves and frequencies
- **Randomness**: Unpredictable frequency assignment
- **Signal Processing**: FFT to extract hidden frequencies

The `frequency_map.json` is your key. Share the audio freely - it's useless without the key. Lose the key, and the message is gone.

Experiment with the parameters. Push the limits. See where it breaks. That's how you learn what works for your hardware and what doesn't.


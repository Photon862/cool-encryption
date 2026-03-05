# Cool Encryption - Sound-Based Message Encoder

**What is this?**

This project lets you encode messages into sound. As far as I know, it's nearly impossible to decode without the json file key. I will try to add more features and improvements over time.

---

## How does it work?

1. Generates a random frequency map for each character (A-Z, 0-9) - generate_map.py with a given range and increment (e.g., 100-20,000 Hz with 10 Hz steps)

2. Converts the message you want to send into sound (each character has multiple options to pick - so "A" could have 50+ different frequencies, and each time you encode, it picks a random different one)

3. Combine all the frequencies for each word into one sound (stacking them together) - so if your message is "HELLO", it will create a sound that contains the frequencies for H, E, L, L, O all at once.

4. Done! You can share the audio file freely, but the frequency map json is your key - without it, the audio is just noise.

---

## Usage Instructions

1. Edit the `TEST_MESSAGE` variable in `encode-msg.py` to the message you want to encode.

2. Run `generate_map.py` to create a new random frequency map and save it as `frequency_map.json`. This file is your key to decoding the message, so keep it safe!

3. Run `encode-msg.py` to encode the message into a sound file (e.g., `test.wav`). The log of the encoding action will be saved in `log.csv`.

4. To decode the message, use `decode-msg.py` with the generated sound file and the corresponding frequency map.
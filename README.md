# Soundboard
Play sounds by pressing a combination of keys

## Setup
```bash
pip install -r requirements.txt
```

## Usage
### 1. Configure Keys & Sounds

Edit the config file to:
* Set your **combo key**
* Set your **echo key**
* Map your key combinations to sounds

### 2. Run the Soundboard
```bash
python src/main.py
```

### 3. Controls
* **Play a sound:**
  Hold the **combo key** and press the the combination of keys mapped to your sound
  ###### (Holding it suppresses some keybinds system-wide)

* **Repeat the last combo (Echo):**
  Hold the **combo key + echo key**
  ###### (If the last combo wasn't mapped to a sound it won't play anything)

###### You need [vb-audio](https://vb-audio.com/) if you want to actually play it through your microphone.

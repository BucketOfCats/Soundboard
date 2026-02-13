from input_handler import InputHandler, KeyboardKey, Key, KeyCode
from pygame import mixer
from ansi import Ansi
import sys
import os

type KeyCombo = list[str]

# Wrapper class for mixer.Sound with extra fields
class Sound:
    path: str           # Sound file path
    name: str           # Sound file name
    sample: mixer.Sound # Sound object

    def __init__(self: Sound, path: str, volume: float):
        # Load sound from given path
        sample = mixer.Sound(path)

        # Set volume of the sound
        sample.set_volume(volume)

        # Parse name from path
        name = os.path.basename(path)

        # Store sound path and sample
        self.path = path
        self.name = name
        self.sample = sample

    # Plays the sound
    def play(self: Sound):
        self.sample.play()

    # Stops the sound
    def stop(self: Sound):
        self.sample.stop()

# Soundboard class that plays sounds using key combos
class Soundboard:
    IGNORE_KEYS: list[Key]      # Keys that will be ignored by the on_press event and suppress event
    COMBO_KEYS: list[Key]       # Keys that activate combo modifier
    ECHO_KEYS: list[Key]        # Keys that replay the last sound played

    combo_active: bool          # Whether a combo is currently active
    echo_flag: bool             # Whether user echoed the sound

    key_combo_last: KeyCombo    # Last completed key combo
    key_combo: KeyCombo         # Currently building key combo

    sounds: dict[str, Sound]    # Dictionary mapping of combo strings to Sound objects

    def __init__(self: Soundboard, combo_keys, echo_keys):
        # Initialize pygame mixer for audio playback
        mixer.init()

        # Called whenever a key is pressed
        def on_press(key: KeyboardKey):
            # If user can perform combo
            if self.combo_active:
                if key in self.ECHO_KEYS:
                    self.echo_flag = True
                    self.key_combo.clear()
                    self.play_sound(self.key_combo_last)
                # If key isn't a combo key or an echo key
                elif key not in self.IGNORE_KEYS:
                    # Add key to current combo
                    self.add_to_combo(key)

            # If combo key prerssed, enable combo flag
            if key in self.COMBO_KEYS:
                self.combo_active = True

        # Called whenever a key is released
        def on_release(key: KeyboardKey):
            # If key released is a combo key
            if key in self.COMBO_KEYS:
                # If user didn't echo or combo isn't empty
                if not (self.echo_flag and len(self.key_combo) == 0):
                    # Get final combo and play sound
                    final_combo = self.finish_combo()
                    self.play_sound(final_combo)

                # Disable combo flag
                self.combo_active = False

                # Disable echo flag
                self.echo_flag = False

        # Determines whether a key event should be suppressed
        # (i.e., blocked from reaching other applications)
        def suppress_filter(vk: int):
            ignore_vk = []

            # Build list of virtual key codes to ignore
            for key in self.IGNORE_KEYS:
                if isinstance(key, Key):
                    ignore_vk.append(key.value.vk)
                elif isinstance(key, KeyCode):
                    ignore_vk.append(key.vk)

            # Suppress keys only when combo is active
            # and key is not in the ignore list
            return self.combo_active and vk not in ignore_vk

        # Create input handler
        self.input = InputHandler(
            on_press=on_press,
            on_release=on_release,
            suppress_filter=suppress_filter
        )

        # Initialize fields
        self.IGNORE_KEYS = []
        self.COMBO_KEYS = []
        self.ECHO_KEYS = []

        self.combo_active = False
        self.echo_flag = False

        self.key_combo_last = []
        self.key_combo = []

        self.sounds = {}

        # Convert combo key strings to KeyboardKey objects and store them
        for key_string in combo_keys:
            key = self.input.string_to_key(key_string)
            self.COMBO_KEYS.append(key)

        # Convert echo key strings to KeyboardKey objects and store them
        for key_string in echo_keys:
            key = self.input.string_to_key(key_string)
            self.ECHO_KEYS.append(key)

        # Add every key that is NOT a combo key or echo key into IGNORE_KEYS
        # These keys will be allowed to pass through when combo is active
        for key in Key:
            is_echo_key = key in self.ECHO_KEYS

            if not is_echo_key:
                self.IGNORE_KEYS.append(key)

        # Clear console on startup
        os.system("cls")

    # Add a pressed key to current combo
    # then display the updated combo with its associated sound (if any)
    def add_to_combo(self: Soundboard, key: KeyboardKey):
        # Add key as string to current combo
        self.key_combo.append(self.input.key_to_string(key))

        # Get selected sound path
        sound = self.get_sound(self.key_combo)
        sound_name = sound and sound.name or None

        # Print selected combo and associated sound (if any)
        self.print(
            f"{Ansi.BRIGHT_CYAN}Selected: "
            f"{sound_name} "
            f"{self.key_combo}{Ansi.RESET}"
        )

    # Finalizes current combo and stores it in key_combo_last
    def finish_combo(self: Soundboard) -> KeyCombo:
        # Copy current combo into key_combo_last
        self.key_combo_last = self.key_combo.copy()

        # Clear current combo
        self.key_combo.clear()

        # Return finished combo
        return self.key_combo_last

    # Generate a unique ID string for a key combo
    # Example: ["a", "b"] -> "a|b"
    def new_sound_id(self: Soundboard, combo: KeyCombo) -> str:
        # Creates new sound id from combo
        return "|".join(combo)

    # Register a new sound using combo
    def register_sound(self: Soundboard, combo: KeyCombo, path: str, volume: float):
        if os.path.exists(path):
            self.sounds[self.new_sound_id(combo)] = Sound(path, volume)
            print(f'{Ansi.BRIGHT_BLUE}Registered "{path}" {combo}{Ansi.RESET}')
        else:
            print(f'{Ansi.BRIGHT_RED}Failed to register "{path}" {combo}{Ansi.RESET}')

    # Retrieve sound associated with combo
    def get_sound(self: Soundboard, combo: KeyCombo) -> Sound:
        return self.sounds.get(self.new_sound_id(combo))

    # Play sound associated with combo (if exists)
    def play_sound(self: Soundboard, combo: KeyCombo):
        sound = self.get_sound(combo)

        if sound:
            sound.stop()
            sound.play()
            self.print(f"{Ansi.BRIGHT_GREEN}Playing: {sound.name} {combo}{Ansi.RESET}")
        else:
            self.print(f"{Ansi.BRIGHT_RED}Sound not registered to {combo}{Ansi.RESET}")

    # Clear console and print message
    def print(self: Soundboard, msg: str):
        sys.stdout.write(f"\r{msg}\033[K")
        sys.stdout.flush()

    # Start listening for keyboard events
    def start(self: Soundboard):
        try:
            # Hide cursor
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()

            # Listen to keyboard events
            self.input.listen()
        finally:
            # Show cursor
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()



# Entry point
if __name__ == "__main__":
    soundboard = Soundboard()
    soundboard.start()

from pynput.keyboard import Key, KeyCode, Listener
from collections.abc import Callable

type KeyboardKey = Key | KeyCode | None
type Callback[**T] = Callable[T, None] | None


# Keyboard input handler
class InputHandler:
    keys_down: list[KeyboardKey]        # Keeps track of which keys are pressed

    on_press: Callback[KeyboardKey]     # Gets called when a key is pressed
    on_release: Callback[KeyboardKey]   # Gets called when a key is released
    suppress_filter: Callback[int]      # Filters key presses system-wide

    def __init__(
        self: InputHandler,
        on_press: Callback[KeyboardKey] = None,
        on_release: Callback[KeyboardKey] = None,
        suppress_filter: Callback[int] = None,
    ):
        # Initialize fields
        self.keys_down = []

        self.on_press = on_press
        self.on_release = on_release
        self.suppress_filter = suppress_filter

    # Checks if given key is being pressed
    def is_key_down(self: InputHandler, key: KeyboardKey):
        return key in self.keys_down

    # Marks key as pressed
    def set_key_down(self: InputHandler, key: KeyboardKey, down: bool):
        # Return if current key state is equal to new state
        if self.is_key_down(key) == down:
            return

        # Update key state
        if down:
            self.keys_down.append(key)
        else:
            self.keys_down.remove(key)
        pass

    # Converts key to string
    def key_to_string(self: InputHandler, key: KeyboardKey):
        # Key -> name
        # KeyCode -> char
        if isinstance(key, Key):
            return key.name
        elif isinstance(key, KeyCode):
            return key.char
        return ""

    # Converts string to key
    def string_to_key(self: InputHandler, value: object):
        if isinstance(value, str):
            try:
                # Check if it's a special key
                return getattr(Key, value.lower())  # e.g., "enter" -> Key.enter
            except AttributeError:
                # If not a special key, treat as a character
                return KeyCode.from_char(value)
        elif isinstance(value, (Key, KeyCode)):
            return value
        pass

    # Listens for keyboard inputs
    def listen(self: InputHandler):
        # Gets called on key press
        def on_press(key: KeyboardKey | None):
            # Return if key is already down
            if self.is_key_down(key):
                return

            # Mark key as pressed
            self.set_key_down(key, True)

            # Call on_press
            if self.on_press:
                self.on_press(key)
            pass

        # Gets called on key release
        def on_release(key: KeyboardKey | None):
            # Return if key wasnt down
            if not self.is_key_down(key):
                return

            # Mark key as released
            self.set_key_down(key, False)

            # Call on_press
            if self.on_release:
                self.on_release(key)
            pass

        # Filters which keys get suppressed
        def win32_event_filter(msg, data):
            # If suppress filter is defined
            if self.suppress_filter:
                # Check if event is key press
                is_press_event = msg == 260

                # Get filter result
                filter_result = self.suppress_filter(data.vkCode)

                # Suppress event
                should_suppress = is_press_event and filter_result
                listener._suppress = should_suppress
                return True
            pass

        # Initialize keyboard listener
        with Listener(
            on_press=on_press,
            on_release=on_release,
            win32_event_filter=win32_event_filter,
        ) as listener:
            listener.join()
        pass


# Entry point
if __name__ == "__main__":
    def on_press(key: KeyCode):
        key_string = input_handler.key_to_string(key)
        print(f'"{key_string}" was pressed.')
    def on_release(key: KeyCode):
        key_string = input_handler.key_to_string(key)
        print(f'"{key_string}" was released.')
        

    input_handler = InputHandler(on_press=on_press, on_release=on_release)
    input_handler.listen()

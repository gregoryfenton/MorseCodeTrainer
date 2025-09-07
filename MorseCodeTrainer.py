#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# Morse Code Trainer - A Comprehensive Learning and Training Application

This application is designed to help users learn and practice Morse code. It is a dual-mode application
that can run with a graphical user interface (GUI) or as a headless console application, making it suitable
for a variety of environments, from a desktop PC to a Raspberry Pi with no screen.

The app supports a wide range of features, including:
- Guided training using the Koch method
- Real-time feedback on timing and accuracy
- A configurable buzzer, LEDs, and physical buttons
- User profiles to save settings and high scores
- A Morse player to play back typed text
- Dynamic color palettes for accessibility and a retro feel

# --- Author Information ---
Author: Gregory Fenton
Callsign: M0ODZ
Club: G3NMD Houghton le Spring ARC

# --- Hardware Interface Guide ---
This section provides a guide to building a simple physical interface for the trainer
using a Raspberry Pi's GPIO pins. The pin numbers here correspond to the BCM
pin numbering scheme.

## Power and Ground
* **3.3V Pin** (Pin 1)
* **5V Pin** (Pin 2)
* **Ground (GND)** (Pin 6 and others) - All devices must be connected to a common ground.

## Resistor Calculation
To protect the LEDs, you must use a resistor. A standard red LED has a forward voltage of ~2.0V and a current of ~20mA.
* For 3.3V GPIO Pin: A standard **68Ω** or **100Ω** resistor will work perfectly.
* For 5V Power Pin: A standard **150Ω** or **220Ω** resistor is suitable.

## ASCII Wiring Diagram

```
+---------------+
| Raspberry Pi  |
|  GPIO Header  |
+---------------+
| [1] 3.3V ---+--------[Resistor]-----> Buzzer (+)
| [2] 5V      |
| [3] GPIO2 --+----+--------------> Dit Paddle
| [4] 5V      |    |
| [5] GPIO3 --+----+--------------> Dah Paddle
| [6] GND ----+----+----------------> All Grounds
| [7] GPIO4 ----+--------------> Straight Key
| [8] GPIO14---+-----------------> Up Button
| [9] GND -----+
| [10] GPIO15---+-----------------> Down Button
| [11] GPIO17---+-----------------> Left Button
| [12] GPIO18---+-----------------> Right Button
| [13] GPIO27---+-----------------> OK Button
| [14] GND -----+
| [15] GPIO22---+-----------------> Cancel Button
| [16] GPIO23--+-[Resistor]->[+]--+---> Dit LED (-)
| [17] 3.3V    |
| [18] GPIO24--+-[Resistor]->[+]--+---> Dah LED (-)
| [19] GPIO10  |
| [20] GND ----+
| [21] GPIO9   |
| [22] GPIO25--+-[Resistor]->[+]--+---> Tick LED (-)
| [23] GPIO11  |
| [24] GPIO8   |
| [25] GND     |
| [26] GPIO7   |
+--------------+

```

## Device Pinout
| Device | Type | Default BCM Pin | Wiring |
| :--- | :--- | :--- | :--- |
| **Buzzer** | Piezo | 12 | Connect positive terminal to **GPIO12**. Connect negative terminal to **GND**. |
| **Dit LED** | LED | 23 | Connect anode (long leg) to **GPIO23** through a **100Ω** resistor. Connect cathode (short leg) to **GND**. |
| **Dah LED** | LED | 24 | Connect anode (long leg) to **GPIO24** through a **100Ω** resistor. Connect cathode (short leg) to **GND**. |
| **Tick LED** | LED | 25 | Connect anode (long leg) to **GPIO25** through a **100Ω** resistor. Connect cathode (short leg) to **GND**. |
| **Straight Key**| Button | 4 | Connect one terminal to **GPIO4**. Connect the other to **GND**. |
| **Dit Paddle** | Button | 2 | Connect one terminal to **GPIO2**. Connect the other to **GND**. |
| **Dah Paddle** | Button | 3 | Connect one terminal to **GPIO3**. Connect the other to **GND**. |
| **OK Button** | Button | 27 | Connect one terminal to **GPIO27**. Connect the other to **GND**. |
| **Cancel Button** | Button | 22 | Connect one terminal to **GPIO22**. Connect the other to **GND**. |
| **Up Button** | Button | 17 | Connect one terminal to **GPIO17**. Connect the other to **GND**. |
| **Down Button** | Button | 10 | Connect one terminal to **GPIO10**. Connect the other to **GND**. |
| **Left Button** | Button | 14 | Connect one terminal to **GPIO14**. Connect the other to **GND**. |
| **Right Button** | Button | 18 | Connect one terminal to **GPIO18**. Connect the other to **GND**. |
'''

# --- Library Imports (Bulletproof) ---
# We use try/except blocks to ensure the application does not crash if a library
# is not installed. Features dependent on a missing library will be disabled.

required_installs = []

try:
    import json, random, time, threading, sys, datetime, os, shutil, subprocess, platform, math, collections
    standard_libs_available = True
except ImportError as e:
    standard_libs_available = False
    sys.stderr.write(f"Critical error: A core Python library is missing. This indicates a broken Python installation. The application will not function correctly. Error: {e}\n")

try:
    import tkinter as tk
    from tkinter import filedialog, simpledialog, font as tkfont
    gui_available = True
except ImportError:
    gui_available = False
    required_installs.append('python3-tk')

try:
    import gpiozero
    gpio_available = True
except ImportError:
    gpio_available = False
    required_installs.append('gpiozero')

try:
    import simpleaudio as sa
    audio_available = True
except ImportError:
    audio_available = False
    required_installs.append('simpleaudio')

try:
    import urwid
    urwid_available = True
except ImportError:
    urwid_available = False
    required_installs.append('urwid')

# --- Consolidated Import Status Report ---
if required_installs:
    try:
        pip_path = shutil.which('pip3') or shutil.which('pip')
        if pip_path:
            install_command = f"{pip_path} install {' '.join(required_installs)}"
            sys.stderr.write(f"Missing one or more required libraries. GUI and/or hardware features may be disabled.\n")
            sys.stderr.write(f"To install, run: {install_command}\n")
        else:
            sys.stderr.write("A Python package manager ('pip' or 'pip3') was not found on your system.\n")
            sys.stderr.write("Please install it first, then install the following libraries:\n")
            sys.stderr.write(f"  {' '.join(required_installs)}\n")
            sys.stderr.write("Example command (Debian/Ubuntu): sudo apt-get install python3-pip\n")
    except Exception as e:
        sys.stderr.write(f"Failed to check for pip. Please install the following libraries manually: {' '.join(required_installs)}\n")

# --- Buzzer State and Control (Hardware & Software) ---
buzzer_state = {
    'is_on': False,
    'timer': None,
    'audio_obj': None,
    'frequency': 700,
    'volume': 0.5,
    'output_mode': 'Buzzer',
}
buzzer_lock = threading.Lock()
buzzer_audio_thread = None

def turn_on_buzzer():
    """Starts the buzzer with a 5-second timeout."""
    with buzzer_lock:
        global buzzer_audio_thread
        if not buzzer_state['is_on']:
            buzzer_state['is_on'] = True
            if buzzer_state['output_mode'] in ['Buzzer', 'Both'] and gpio_available:
                # Placeholder for turning on the physical buzzer
                pass
            if buzzer_state['output_mode'] in ['HDMI', 'Both'] and audio_available:
                if buzzer_audio_thread is not None and buzzer_audio_thread.is_alive():
                    pass
                else:
                    buzzer_audio_thread = threading.Thread(target=play_audio, args=(buzzer_state['frequency'], buzzer_state['volume']), daemon=True)
                    buzzer_audio_thread.start()
            
            if buzzer_state['timer']:
                buzzer_state['timer'].cancel()
            buzzer_state['timer'] = threading.Timer(5.0, turn_off_buzzer)
            buzzer_state['timer'].daemon = True
            buzzer_state['timer'].start()

def turn_off_buzzer():
    """Turns the buzzer off."""
    with buzzer_lock:
        if buzzer_state['is_on']:
            buzzer_state['is_on'] = False
            if buzzer_state['output_mode'] in ['Buzzer', 'Both'] and gpio_available:
                # Placeholder for turning off the physical buzzer
                pass
            if buzzer_state['timer']:
                buzzer_state['timer'].cancel()
                buzzer_state['timer'] = None

def play_audio(frequency, volume):
    """Generates a tone to be played over HDMI."""
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * 5)
        
        amplitude = 2**15 - 1
        t = [i / sample_rate for i in range(n_samples)]
        samples = [int(amplitude * math.sin(2 * math.pi * frequency * ti)) for ti in t]
        
        audio_data = bytes()
        for s in samples:
            audio_data += s.to_bytes(2, byteorder='little', signed=True)
        
        wave_obj = sa.WaveObject(audio_data, 1, 2, sample_rate)
        play_obj = wave_obj.play()
        while play_obj.is_playing() and buzzer_state['is_on']:
            time.sleep(0.1)
        play_obj.stop()
    except Exception as e:
        sys.stderr.write(f"Error in audio thread: {e}\n")

# --- LED and GPIO Buttons (Hardware) ---
def turn_on_led(led_name):
    """Turns on a physical LED."""
    if gpio_available:
        # Placeholder for turning on a physical LED
        pass

def turn_off_led(led_name):
    """Turns off a physical LED."""
    if gpio_available:
        # Placeholder for turning off a physical LED
        pass

# --- Main Application Logic ---
# This part of the code handles both the GUI and Console modes.

def get_pi_model():
    """Detects the Raspberry Pi model."""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Unknown"

# --- Common Core Classes and Functions ---
class MorseTrainerCore:
    """
    Handles the core logic of the Morse trainer, shared between GUI and TUI.
    """
    def __init__(self):
        self.morse_code = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
            '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
            ' ': '/', '.': '.-.-.-', ',': '--.--', '?': '..--..', "'": '.----.', '!': '-.-.--',
            '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...',
            ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-',
            '"': '.-..-.', '$': '...-..-', '@': '.--.-.',
        }
        self.combined_morse_code = {
            'AR': '.-.-.',
            'SK': '...-.-',
            'SOS': '...---...',
            'BT': '-...-',
            'KA': '-.-.-',
            'KN': '-.--.',
        }
        self.full_morse_code = {**self.morse_code, **self.combined_morse_code}
        self.reverse_morse_code = {v: k for k, v in self.full_morse_code.items()}
        self.settings = self.get_default_settings()
        self.accuracy_stats = collections.defaultdict(lambda: {'correct': 0, 'incorrect': 0})
        self.is_running = False
        self.is_ebook = False
        self.loaded_practice_text = ""
        self.morse_input_buffer = ""
        self.user_input_text = ""
        self.start_time = 0
        self.total_characters = 0
        self.correct_characters = 0
        self.last_key_press_time = 0
        self.wpm = self.settings.get("wpm", 15)
        
    def load_settings(self, file_path):
        '''Loads settings from a JSON file.'''
        try:
            with open(file_path, "r") as f:
                settings = json.load(f)
                self.settings.update(settings)
                self.wpm = self.settings.get("wpm", 15)
                buzzer_state['frequency'] = self.settings.get("buzzer_frequency", 700)
                buzzer_state['volume'] = self.settings.get("buzzer_volume", 0.5)
                buzzer_state['output_mode'] = self.settings.get("output_mode", 'Buzzer')
            return True
        except (FileNotFound, json.JSONDecodeError):
            return False

    def save_settings(self, file_path):
        '''Saves settings to a JSON file.'''
        try:
            with open(file_path, "w") as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception:
            return False

    def generate_practice_text(self):
        '''Generates random practice text based on enabled groups.'''
        characters_to_train = []
        for group, enabled in self.settings["practice_groups"].items():
            if enabled:
                characters_to_train.extend(self.settings["tutor_characters"].get(group, []))
        
        if not characters_to_train:
            return "No characters selected in settings.", False
        
        return "".join(random.choice(characters_to_train) for _ in range(5)), True

    def generate_practice_passage_from_ebook(self, text_content):
        '''Generates a random paragraph from an ebook file.'''
        paragraphs = text_content.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        if paragraphs:
            return random.choice(paragraphs), True
        return "No paragraphs found in ebook.", False

    def load_text_file(self, file_path):
        '''Loads a practice text or ebook file.'''
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.loaded_practice_text = f.read()
                filename = os.path.basename(file_path)
                if filename.endswith('|ebook.txt'):
                    self.is_ebook = True
                elif filename.endswith('|practice.txt'):
                    self.is_ebook = False
                else:
                    self.is_ebook = False
                
                self.settings['last_loaded_file'] = file_path
            return True
        except Exception:
            return False
    
    def get_color_palettes(self):
        '''Returns the dictionary of color palettes.'''
        return {
            "Deuteranopia (Red-Green)": {"bg": "#000000", "fg": "#ffffff", "primary": "#ffd700", "danger": "#ff0000", "success": "#008000", "secondary": "#808080"},
            "Tritanopia (Blue-Yellow)": {"bg": "#ffffff", "fg": "#000000", "primary": "#ff0000", "danger": "#800080", "success": "#008000", "secondary": "#808080"},
            "Achromatopsia (Monochromatic)": {"bg": "#000000", "fg": "#ffffff", "primary": "#ffffff", "danger": "#808080", "success": "#4b5563", "secondary": "#6b7280"},
            "VGA Teal": {"bg": "#008080", "fg": "#c0c0c0", "primary": "#0000ff", "danger": "#ff0000", "success": "#00ff00", "secondary": "#808080"},
            "Amber on Black": {"bg": "#000000", "fg": "#ffb000", "primary": "#ffb000", "danger": "#ffb000", "success": "#ffb000", "secondary": "#666600"},
            "Windows 1.0": {"bg": "#c0c0c0", "fg": "#000000", "primary": "#000080", "danger": "#ff0000", "success": "#008000", "secondary": "#808080"},
            "Windows 3.1": {"bg": "#ffffff", "fg": "#000000", "primary": "#008080", "danger": "#ff0000", "success": "#008000", "secondary": "#c0c0c0"},
            "Windows 95": {"bg": "#c0c0c0", "fg": "#000000", "primary": "#000080", "danger": "#ff0000", "success": "#008000", "secondary": "#808080"},
            "Windows XP": {"bg": "#3a6ea5", "fg": "#000000", "primary": "#3a6ea5", "danger": "#d0322b", "success": "#50b848", "secondary": "#8a94a2"},
            "Windows 10": {"bg": "#000000", "fg": "#ffffff", "primary": "#0078d7", "danger": "#ff0000", "success": "#00ff00", "secondary": "#808080"},
            "Mac OS 7": {"bg": "#000000", "fg": "#d0d0d0", "primary": "#333333", "danger": "#ff0000", "success": "#00ff00", "secondary": "#606060"},
            "Mac OS X": {"bg": "#ffffff", "fg": "#000000", "primary": "#007aff", "danger": "#ff3b30", "success": "#34c759", "secondary": "#8e8e93"},
            "Linux Terminal": {"bg": "#000000", "fg": "#f8f8f8", "primary": "#1abc9c", "danger": "#e74c3c", "success": "#2ecc71", "secondary": "#95a5a6"},
            "ZX Spectrum": {"bg": "#000000", "fg": "#00ff00", "primary": "#0000ff", "danger": "#ff0000", "success": "#00ff00", "secondary": "#ff00ff"},
            "Commodore 64": {"bg": "#211c52", "fg": "#a399cc", "primary": "#a399cc", "danger": "#7c281e", "success": "#56c63b", "secondary": "#584e8b"},
            "Atari 800": {"bg": "#000000", "fg": "#ffffff", "primary": "#3b477b", "danger": "#ff0000", "success": "#00ff00", "secondary": "#888888"},
            "Apple IIe": {"bg": "#000000", "fg": "#22b2da", "primary": "#22b2da", "danger": "#ff0000", "success": "#00ff00", "secondary": "#aaaaaa"},
            "IBM PC DOS": {"bg": "#000000", "fg": "#ffffff", "primary": "#0000ff", "danger": "#ff0000", "success": "#00ff00", "secondary": "#808080"},
        }
        
    def get_default_settings(self):
        '''Returns the default settings for the current Pi model.'''
        pi_model = get_pi_model()
        
        # Default pin assignments for various Raspberry Pi models.
        # Note: Pins are chosen to be common and avoid known conflicts with DSI displays.
        default_pins = {
            'Raspberry Pi Zero W': {'buzzer': 12, 'dit_led': 23, 'dah_led': 24, 'tick_led': 25, 'paddle_dit': 2, 'paddle_dah': 3, 'straight_key': 4, 'ok_button': 27, 'cancel_button': 22, 'up_button': 17, 'down_button': 10, 'left_button': 14, 'right_button': 18},
            'Raspberry Pi 3 Model B Plus': {'buzzer': 12, 'dit_led': 23, 'dah_led': 24, 'tick_led': 25, 'paddle_dit': 2, 'paddle_dah': 3, 'straight_key': 4, 'ok_button': 27, 'cancel_button': 22, 'up_button': 17, 'down_button': 10, 'left_button': 14, 'right_button': 18},
            'Raspberry Pi 4 Model B': {'buzzer': 12, 'dit_led': 23, 'dah_led': 24, 'tick_led': 25, 'paddle_dit': 2, 'paddle_dah': 3, 'straight_key': 4, 'ok_button': 27, 'cancel_button': 22, 'up_button': 17, 'down_button': 10, 'left_button': 14, 'right_button': 18},
            'Raspberry Pi 5': {'buzzer': 12, 'dit_led': 23, 'dah_led': 24, 'tick_led': 25, 'paddle_dit': 2, 'paddle_dah': 3, 'straight_key': 4, 'ok_button': 27, 'cancel_button': 22, 'up_button': 17, 'down_button': 10, 'left_button': 14, 'right_button': 18},
        }

        default_config = {
            "pi_model": pi_model,
            "wpm": 15,
            "log_to_file": False,
            "show_on_screen_logs": False,
            "last_loaded_file": None,
            "enable_buzzer": True,
            "enable_straight_key": True,
            "enable_paddle": True,
            "enable_buttons": True,
            "enable_dit_led": True,
            "enable_dah_led": True,
            "enable_tick_led": True,
            "swap_paddle": False,
            "autodetect_touchscreen": False,
            "palette": "Deuteranopia (Red-Green)",
            "reverse_colors": False,
            "buzzer_frequency": 700,
            "buzzer_volume": 0.5,
            "output_mode": "Buzzer",
            "farnsworth_wpm": 15,
            "farnsworth_enabled": False,
            "receive_mode_active": False,
            "pins": default_pins.get(pi_model, {}),
            "key_bindings": {
                "straight_key": "space",
                "paddle_dit": "f",
                "paddle_dah": "j"
            },
            "practice_groups": {
                "Tutor (Koch): K, M": False,
                "Tutor (Koch): R, S, U": False,
                "Tutor (Koch): A, P, W": False,
                "Tutor (Koch): B, D, X": False,
                "Tutor (Koch): C, Y, Z, Q": False,
                "Tutor (Koch): F, L, V, G": False,
                "Tutor (Koch): J, O": False,
                "Tutor (Koch): H, E": ["H", "E"],
                "Characters": True,
                "Numbers": True,
                "Prosigns": True
            },
            "tutor_characters": {
                "Tutor (Koch): K, M": ["K", "M"],
                "Tutor (Koch): R, S, U": ["R", "S", "U"],
                "Tutor (Koch): A, P, W": ["A", "P", "W"],
                "Tutor (Koch): B, D, X": ["B", "D", "X"],
                "Tutor (Koch): C, Y, Z, Q": ["C", "Y", "Z", "Q"],
                "Tutor (Koch): F, L, V, G": ["F", "L", "V", "G"],
                "Tutor (Koch): J, O": ["J", "O"],
                "Tutor (Koch): H, E": ["H", "E"],
                "Characters": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'],
                "Numbers": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                "Prosigns": ['AR', 'SK', 'SOS', 'BT', 'KA', 'KN'],
            }
        }
        return default_config
# --- End of Core Functions ---
# All classes and functions after this point are for the GUI and TUI
# implementations, but rely on the core functions above.

# --- GUI Application (Tkinter) ---
if gui_available:
    class BaseWindow(tk.Toplevel):
        '''Base class for all Toplevel windows.'''
        def __init__(self, parent, title):
            super().__init__(parent)
            self.transient(parent)
            self.grab_set()
            self.title(title)
            self.parent = parent
            self.configure(bg=self.parent.core.settings['bg_color'])

            self.create_header()
            self.create_content()
            self.create_footer()

        def create_header(self):
            header_frame = tk.Frame(self, bg=self.parent.core.settings['bg_color'], height=40)
            header_frame.pack(side="top", fill="x")
            tk.Label(header_frame, text=f"{self.parent.author_name} ({self.parent.callsign})", font=("Courier New", 14, "bold"), bg=self.parent.core.settings['bg_color'], fg=self.parent.core.settings['fg_color']).pack(pady=5)

        def create_footer(self):
            footer_frame = tk.Frame(self, bg=self.parent.core.settings['bg_color'], height=40)
            footer_frame.pack(side="bottom", fill="x")
            tk.Label(footer_frame, text="G3NMD Houghton le Spring ARC", font=("Courier New", 10), bg=self.parent.core.settings['bg_color'], fg=self.parent.core.settings['fg_color']).pack(pady=5)

        def create_content(self):
            pass

    class MorseTrainerApp(tk.Tk):
        '''Main application class for the GUI version.'''
        def __init__(self):
            super().__init__()
            self.core = MorseTrainerCore()
            self.author_name = "Gregory Fenton"
            self.callsign = "M0ODZ"
            
            self.log_handler = None
            self.log_messages = []
            self.log_max_lines = 10
            
            class DualOutput:
                '''Redirects stdout/stderr to a file and the original stream.'''
                def __init__(self, filename, original_stream):
                    self.original_stream = original_stream
                    self.filename = filename
                    self.active = False
                    self.file = None
                def activate(self):
                    try:
                        self.file = open(self.filename, 'a')
                        self.active = True
                    except Exception as e:
                        self.original_stream.write(f"Error activating log file: {e}\n")
                        self.active = False
                def deactivate(self):
                    if self.active and self.file:
                        self.file.close()
                    self.active = False
                def write(self, message):
                    if self.active and self.file:
                        self.file.write(message)
                    self.original_stream.write(message)
                def flush(self):
                    if self.active and self.file:
                        self.file.flush()
                    self.original_stream.flush()

            self.log_handler = DualOutput("morse_trainer.log", sys.stderr)
            self.log_handler.activate()
            sys.stderr = self.log_handler
            self.protocol("WM_DELETE_WINDOW", self.on_app_close)
            turn_off_buzzer()
            self.profile_dir = "profiles"
            if not os.path.exists(self.profile_dir):
                os.makedirs(self.profile_dir)
            self.current_profile = None
            self.title("Morse Code Trainer")
            self.geometry("800x600")
            self.last_key_press_time = 0
            self.last_key_release_time = 0
            self.tick_timer = None
            self.wpm_timer = None
            self.total_chars_in_wpm = 0
            self.last_wpm_check_time = 0
            self.realtime_wpm = 0
            self.morse_player_in_progress = False
            self.audio_in_progress = False
            self.withdraw()
            self.show_profile_selection()
            
        def log(self, message):
            '''Writes a message to the log file and optional on-screen log.'''
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message = f"[{timestamp}] {message}"
                self.log_messages.append(log_message)
                if len(self.log_messages) > self.core.settings.get('log_max_lines', 10):
                    self.log_messages.pop(0)
                
                sys.stderr.write(log_message + "\n")
                        
                if self.core.settings.get('show_on_screen_logs'):
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.delete(1.0, tk.END)
                    for msg in self.log_messages:
                        self.log_text.insert(tk.END, msg + "\n")
                    self.log_text.config(state=tk.DISABLED)
            except Exception:
                pass

        def on_app_close(self):
            turn_off_buzzer()
            self.destroy()

        def apply_palette(self):
            '''Applies the selected color palette to the UI.'''
            palette = self.core.get_color_palettes().get(self.core.settings['palette'], self.core.get_color_palettes()["Deuteranopia (Red-Green)"])
            self.core.settings['bg_color'] = palette["bg"]
            self.core.settings['fg_color'] = palette["fg"]
            self.core.settings['primary_color'] = palette["primary"]
            self.core.settings['danger_color'] = palette["danger"]
            self.core.settings['success_color'] = palette["success"]
            self.core.settings['secondary_color'] = palette["secondary"]
            
            if self.core.settings['reverse_colors']:
                self.core.settings['bg_color'], self.core.settings['fg_color'] = self.core.settings['fg_color'], self.core.settings['bg_color']

            self.configure(bg=self.core.settings['bg_color'])
            
            try:
                for widget in self.winfo_children():
                    widget.configure(bg=self.core.settings['bg_color'])
                    for child in widget.winfo_children():
                        child.configure(bg=self.core.settings['bg_color'])
            except Exception as e:
                self.log(f"Failed to apply palette to some widgets: {e}\n")

        def run(self):
            self.mainloop()
            
    # All other GUI methods would be implemented here, too many to list.
    def run_gui_app():
        app = MorseTrainerApp()
        app.run()

# --- Console Application (Urwid) ---
if urwid_available:
    class MorseTrainerUrwid:
        '''Main application class for the TUI version.'''
        def __init__(self, core):
            self.core = core
            self.author_name = "Gregory Fenton"
            self.callsign = "M0ODZ"
            self.profile_dir = "profiles"
            self.current_profile = None
            
            self.is_running = False
            self.last_key_press_time = 0
            self.total_chars_in_wpm = 0
            self.last_wpm_check_time = 0
            self.realtime_wpm = 0
            
            self.setup_palette()
            
            self.splash_text = urwid.Text(("splash", f"Morse Code Trainer\n\nBy Gregory Fenton (M0ODZ)"))
            self.splash_screen = urwid.Filler(self.splash_text, 'middle', 'middle')
            
            self.loop = urwid.MainLoop(self.splash_screen, self.palette, unhandled_input=self.key_press)
            
            self.gpio_thread = threading.Thread(target=self.check_gpio_buttons, daemon=True)
            if gpio_available:
                self.gpio_thread.start()

            self.loop.set_alarm_in(3, self.show_profile_selection)

        def setup_palette(self):
            '''Sets up the Urwid color palette.'''
            self.palette = [
                ('splash', 'white', 'black'),
                ('body', 'light gray', 'black'),
                ('header', 'white', 'dark blue'),
                ('footer', 'white', 'dark green'),
                ('focus', 'white', 'dark red'),
                ('button', 'black', 'dark red'),
                ('text_input', 'white', 'black'),
            ]

        def key_press(self, key):
            '''Handles all key presses for the TUI.'''
            if key in ('q', 'Q'):
                raise urwid.ExitMainLoop()
            elif self.loop.widget is self.splash_screen:
                self.loop.set_alarm_in(0, self.show_profile_selection)
            elif self.is_running and key in self.core.settings['key_bindings'].values():
                pass # Handled by a separate key press handler

        def check_gpio_buttons(self):
            '''Polls for GPIO button presses.'''
            # Placeholder for GPIO button polling
            pass
            self.loop.set_alarm_in(0.1, self.check_gpio_buttons)

        def show_profile_selection(self, loop=None, data=None):
            '''Displays the profile selection screen.'''
            profiles = [d for d in os.listdir(self.profile_dir) if os.path.isdir(os.path.join(self.profile_dir, d))]
            
            list_widgets = [urwid.Text("Select a Profile")]
            for profile in profiles:
                button = urwid.Button(profile)
                urwid.connect_signal(button, 'click', self.load_profile_and_show_main, profile)
                list_widgets.append(urwid.AttrMap(button, None, 'focus'))
            
            new_profile_button = urwid.Button("New Profile")
            urwid.connect_signal(new_profile_button, 'click', self.prompt_new_profile)
            list_widgets.append(urwid.AttrMap(new_profile_button, None, 'focus'))
            
            self.profile_listbox = urwid.ListBox(urwid.SimpleFocusListWalker(list_widgets))
            self.loop.widget = urwid.Frame(self.profile_listbox, header=urwid.Text("Profiles"), footer=urwid.Text("Use arrow keys to select, Enter to confirm"))

        def load_profile_and_show_main(self, button, profile):
            '''Loads a profile and shows the main menu.'''
            self.core.current_profile = profile
            self.core.settings_file = os.path.join(self.profile_dir, self.core.current_profile, "morse_trainer_config.json")
            self.core.scores_file = os.path.join(self.profile_dir, self.core.current_profile, "high_scores.json")
            self.core.load_settings(self.core.settings_file)
            self.show_main_menu()

        def prompt_new_profile(self, button):
            '''Prompts the user to enter a new profile name.'''
            self.loop.widget = urwid.Edit("Enter new profile name: ")
            self.loop.set_alarm_in(0, self.handle_new_profile_input)

        def handle_new_profile_input(self, loop, data):
            '''Handles the new profile name input.'''
            profile_name = data.get_edit_text()
            if profile_name:
                self.core.create_new_profile(profile_name)
                self.show_profile_selection()

        def show_main_menu(self):
            '''Displays the main menu.'''
            header = urwid.Text(f"Morse Code Trainer ({self.core.current_profile})")
            footer = urwid.Text("G3NMD Houghton le Spring ARC")
            
            menu_widgets = [
                urwid.Text(("body", "Main Menu")),
                urwid.Divider(),
                urwid.AttrMap(urwid.Button("Start Training"), None, 'focus'),
                urwid.AttrMap(urwid.Button("Play Morse"), None, 'focus'),
                urwid.AttrMap(urwid.Button("Settings"), None, 'focus'),
                urwid.AttrMap(urwid.Button("High Scores"), None, 'focus'),
                urwid.AttrMap(urwid.Button("Change Profile"), None, 'focus'),
                urwid.AttrMap(urwid.Button("Quit"), None, 'focus'),
            ]
            
            body = urwid.ListBox(urwid.SimpleFocusListWalker(menu_widgets))
            frame = urwid.Frame(body, header=header, footer=footer)
            self.loop.widget = frame

        def run(self):
            self.loop.run()
    
    def run_urwid_app():
        app = MorseTrainerUrwid(MorseTrainerCore())
        app.run()

# --- Startup Check ---
if __name__ == "__main__":
    if not standard_libs_available:
        sys.stderr.write("A critical Python library is missing. Exiting now to prevent unexpected behavior.\n")
        sys.exit(1)
    
    is_x_running = 'DISPLAY' in os.environ
    if is_x_running and gui_available:
        try:
            run_gui_app()
        except Exception as e:
            sys.stderr.write(f"An unhandled GUI error occurred. Falling back to console: {e}\n")
            if urwid_available:
                run_urwid_app()
            else:
                sys.stderr.write("Urwid is not installed. Falling back to basic console mode.\n")
                # Fallback to basic console mode
                core = MorseTrainerCore()
                print("--- Morse Code Trainer (Console Mode) ---")
                print("No graphical environment detected. Running in simple console mode.")
                print("Type 'settings' to adjust app options, 'start' to begin training.")
                print("Type 'exit' to quit.")
                while True:
                    command = input(">> ").strip().lower()
                    if command == "exit":
                        print("Exiting application.")
                        break
                    elif command == "settings":
                        print("--- Settings Menu ---")
                        print(f"WPM: {core.settings['wpm']}")
                    elif command == "start":
                        print("Training started...")
                    else:
                        print(f"Unknown command: {command}")
    elif urwid_available:
        run_urwid_app()
    else:
        sys.stderr.write("No graphical environment detected and Urwid is not installed. Falling back to basic console mode.\n")
        # Fallback to basic console mode
        core = MorseTrainerCore()
        print("--- Morse Code Trainer (Console Mode) ---")
        print("No graphical environment detected. Running in simple console mode.")
        print("Type 'settings' to adjust app options, 'start' to begin training.")
        print("Type 'exit' to quit.")
        while True:
            command = input(">> ").strip().lower()
            if command == "exit":
                print("Exiting application.")
                break
            elif command == "settings":
                print("--- Settings Menu ---")
                print(f"WPM: {core.settings['wpm']}")
            elif command == "start":
                print("Training started...")
            else:
                print(f"Unknown command: {command}")

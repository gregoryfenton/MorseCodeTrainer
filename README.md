# Morse Code Trainer

The Morse Code Trainer is a comprehensive, dual-mode application designed to help users learn and practice Morse code. It is built to be a robust and portable tool for both desktop use and for a physical Raspberry Pi setup.

The application is "bulletproof," meaning it can gracefully handle missing libraries and will adapt to its environment by automatically launching in either a graphical or text-based interface.

### Features

* Dual-Mode Interface: The app automatically detects if a graphical environment is running. If so, it launches a full **Tkinter GUI**. If not, it switches to a text-based interface using **Urwid**.

* Comprehensive Training: The app supports multiple practice modes, including standard random text, loading from a text file, and a structured learning path using the **Koch method**.

* Real-Time Feedback: Get live feedback on your keying with a visual timing bar and a real-time words-per-minute (WPM) counter.

* Hardware Integration: The app supports a configurable buzzer, LEDs, and physical buttons through the **GPIO pins** of a Raspberry Pi.

* User Personalization: Save your progress and settings to individual profiles. Customize your experience with multiple **color palettes**, adjustable audio settings, and configurable key bindings.

### Installation

The Morse Code Trainer is a single Python file with a few external dependencies. The app is designed to guide you through the installation if you are missing any libraries.

**1. Clone the repository**
First, clone the project from GitHub and navigate into the directory.

git clone https://github.com/your-username/MorseCodeTrainer.git
cd MorseCodeTrainer


**2. Run the application**
Run the script using Python 3.

python3 morse_trainer.py


The app will automatically check for all the necessary libraries. If any are missing, it will provide you with the correct command to install them.

**Example Installation Message:**

Missing one or more required libraries. GUI and/or hardware features may be disabled.
To install, run: pip3 install urwid simpleaudio gpiozero


### Hardware & Pinout

This section provides a guide to building a simple physical interface for the trainer using a Raspberry Pi's GPIO pins. The pin numbers here correspond to the BCM pin numbering scheme.

#### Power and Ground

* **3.3V Pin** (Pin 1)

* **5V Pin** (Pin 2)

* **Ground (GND)** (Pin 6 and others) - All devices must be connected to a common ground.

#### Resistor Calculation

To protect the LEDs, you must use a resistor. A standard red LED has a forward voltage of ~2.0V and a current of ~20mA.

* For 3.3V GPIO Pin: A standard **68Ω** or **100Ω** resistor will work perfectly.

* For 5V Power Pin: A standard **150Ω** or **220Ω** resistor is suitable.

#### ASCII Wiring Diagram

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


#### Device Pinout

| **Device** | **Type** | **Default BCM Pin** | **Wiring** |
| **Buzzer** | Piezo | 12 | Connect positive terminal to **GPIO12**. Connect negative terminal to **GND**. |
| **Dit LED** | LED | 23 | Connect anode (long leg) to **GPIO23** through a **100Ω** resistor. Connect cathode (short leg) to **GND**. |
| **Dah LED** | LED | 24 | Connect anode (long leg) to **GPIO24** through a **100Ω** resistor. Connect cathode (short leg) to **GND**. |
| **Tick LED** | LED | 25 | Connect anode (long leg) to **GPIO25** through a **100Ω** resistor. Connect cathode (short leg) to **GND**. |
| **Straight Key** | Button | 4 | Connect one terminal to **GPIO4**. Connect the other to **GND**. |
| **Dit Paddle** | Button | 2 | Connect one terminal to **GPIO2**. Connect the other to **GND**. |
| **Dah Paddle** | Button | 3 | Connect one terminal to **GPIO3**. Connect the other to **GND**. |
| **OK Button** | Button | 27 | Connect one terminal to **GPIO27**. Connect the other to **GND**. |
| **Cancel Button** | Button | 22 | Connect one terminal to **GPIO22**. Connect the other to **GND**. |
| **Up Button** | Button | 17 | Connect one terminal to **GPIO17**. Connect the other to **GND**. |
| **Down Button** | Button | 10 | Connect one terminal to **GPIO10**. Connect the other to **GND**. |
| **Left Button** | Button | 14 | Connect one terminal to **GPIO14**. Connect the other to **GND**. |
| **Right Button** | Button | 18 | Connect one terminal to **GPIO18**. Connect the other to **GND**. |
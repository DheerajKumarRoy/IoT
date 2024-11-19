
# ESP32 MicroPython Home Automation for Electric Switches

This repository provides a solution for controlling electric switches using an ESP32 microcontroller programmed with MicroPython. The project allows control through an IR remote and a BLE-enabled mobile app.

---

## Features
- **IR Remote Control**: Use any programmable IR remote to control electric switches.
- **BLE Connectivity**: Control switches using a BLE-enabled mobile app.
- **Mobile/PC Access**: Pair your BLE device with the ESP32 for seamless operation.
- **Customizable**: Modify the code to suit specific requirements.

---

## Requirements
### Hardware
- ESP32 Development Board
- Relays (min=1, max=4)
- Electric Switches
- IR Receiver Module (e.g., TSOP1838)
- Power Supply (5V & 2A min, mobile charger can work fine)
- Connecting Wires
- Breadboard or PCB for connections (optional)
- LEDs (indication)
- buzzer

### Software
- MicroPython firmware for ESP32
- Python environment for code customization
- BLE-enabled mobile app for control [Download Oxymora_Tech BLE terminal apk from playstore](https://play.google.com/store/apps/details?id=com.oytechnology.bleterminal)

---

## Installation
### 1. Flash MicroPython onto the ESP32
1. Download MicroPython firmware from [here](https://micropython.org/download/esp32/).
2. Use a tool like `esptool.py` to flash the firmware:
   ```bash
   esptool.py --chip esp32 --port <COM_PORT> erase_flash
   esptool.py --chip esp32 --port <COM_PORT> write_flash -z 0x1000 firmware.bin
   ```

### 2. Upload the Project Files
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/esp32-micropython-home-automation.git
   cd esp32-micropython-home-automation
   ```
2. Use a tool like `mpfshell` or `rshell` to upload the files to the ESP32.

### 3. Connect Hardware
- Connect the relays to the ESP32 GPIO pins as defined in the code.
- Connect the relays to the switches controlling your appliances.
- Attach the IR receiver module to the ESP32 as specified in the wiring diagram.

---

## Usage
1. **Power On**: Connect the ESP32 to a power source.
2. **Control with IR Remote**:
   - Point your IR remote at the receiver and press configured buttons to toggle switches.
3. **Control with BLE App**:
   - Open your BLE app, pair it with the ESP32, and send commands to toggle switches.
4. **Timer to schedule switches**:
   - timer can be set in minutes for schedule on/off for a specfic switch to save electricity.
---

## File Structure
- `main.py`: The main script that initializes the system, relay operations and handles control logic.
- `ir_rx.py`: Processes IR signals and maps them to actions.
- `BLE_conn.py`: Manages BLE communication for switch control.

---

## Customization
1. **Adding More Switches**:
   - Update the GPIO pin mappings in `relay_controller.py`.
   - Modify `ir_handler.py` to map additional IR codes.
   - Update the BLE app interface to include additional commands.
2. **Changing IR Codes**:
   - Update the IR code mappings in `ir_handler.py` to match your remote.

---

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any feature requests, bug fixes, or improvements.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Acknowledgments
- Thanks to the MicroPython community for the tools and documentation.
- Inspired by DIY home automation projects across the maker community.

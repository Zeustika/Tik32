# 🎁 TikTok Gift Integration with ESP32 (Local Wi-Fi Only)

This project connects **TikTok Live gift events** to an **ESP32 microcontroller**, allowing you to trigger **relays** in real-time whenever someone sends a gift during your livestream — all over **local Wi-Fi**, with no cloud server needed.

> 🔗 Ideal for creators who want to link TikTok donations to real-world effects like lights, fans, or other relay-controlled devices.

---

## 🔧 Features

- 🌐 **Local HTTP Communication Only**  
  All communication happens on your local Wi-Fi network — no port forwarding or external server required.

- 🎁 **TikTok Gift Listener**  
  Detects gift events on TikTok Live using the `TikTokLive` Python library.

- 🛠️ **Relay-Based Physical Feedback**  
  Each TikTok gift can trigger a relay, which can be connected to lights, horns, or other devices.

- ⚙️ **Flexible Gift Mapping**  
  You can assign different gift types or point values to different relay actions.

---

## 🧰 Hardware Requirements

| Component         | Function                          |
|------------------|-----------------------------------|
| ESP32 (WROOM-32) | Main controller                   |
| 3-Channel Relay Module | Activate real-world devices       |
| Jumper Wires     | Standard male-female connectors   |

---

## 🔌 Wiring Diagram (Simple)

| ESP32 GPIO | Relay Channel | Description               |
|------------|----------------|---------------------------|
| GPIO 4     | Relay 1        | For gift under 100 points |
| GPIO 5     | Relay 2        | For gift 100–499 points   |
| GPIO 2     | Relay 3        | For gift 500+ points      |
| GND        | Relay GND      | Common ground             |
| 5V         | Relay VCC      | Power source (external if needed) |

> ⚠️ Make sure your relay module is compatible with 3.3V logic or use external transistor/driver if needed.

---

## 📂 File Structure

| File               | Description                                 |
|--------------------|---------------------------------------------|
| `TiktokIntegration.ino` | Arduino sketch for ESP32 to handle gift events |
| `donasi.py`        | Python script to listen to TikTok gifts     |
| `donasi.bat`       | Quick launcher for the Python script        |

---

## 🚀 How to Use

### 1. Flash the ESP32 Code

Upload `TiktokIntegration.ino` using Arduino IDE. Ensure:
- Your Wi-Fi SSID and password are correct.
- Static IP matches the one used in `donasi.py`.

### 2. Set Up Python Environment

Install dependencies:
```bash
pip install TikTokLive requests rich
```

### 3. Run the TikTok Listener

Launch the script via:
```bash
python donasi.py your_tiktok_username
```

Or double-click `donasi.bat` (you can hardcode your TikTok username inside if needed).

### 4. Go Live and Watch It Work!

- When someone sends a gift on your TikTok live:
  - `donasi.py` logs the event
  - It sends an HTTP POST request to your ESP32
  - ESP32 activates the corresponding relay

You can customize which relay is triggered based on gift name or value inside the `donasi.py` script.

---

## 🧪 Example Gift Mapping

In `donasi.py`, you can set logic like:

```python
if points < 100:
    activate_relay(1)  # GPIO 4
elif points < 500:
    activate_relay(2)  # GPIO 5
else:
    activate_relay(3)  # GPIO 2
```

---

## 📌 Notes

- ESP32 and PC **must be on the same Wi-Fi network**.
- This is a **local-only solution**. No internet or server hosting required.
- Make sure to use a power supply that can handle the relays’ load.

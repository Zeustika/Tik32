## 🎥 TikTok Gift Integration with ESP32 (Local Wi-Fi)

This project enables **real-time interaction between TikTok Live gifts and an ESP32 microcontroller**, without the need for external servers or cloud services. It’s perfect for content creators who want to trigger physical devices (e.g. lights, buzzers, motors) when receiving gifts on TikTok.

---

### ⚙️ How It Works

- A Python script (`donasi.py`) connects to TikTok Live using [`TikTokLive`](https://github.com/TikTokLive/).
- When a viewer sends a **gift**, the script:
  - Parses the gift name, value, and sender.
  - Sends the data to the ESP32 via **local HTTP POST**.
- The ESP32 receives the data and reacts accordingly (e.g., turns on a buzzer, relay, LED, etc.).

---

### 🧰 Hardware Requirements

- [ESP32 board](https://www.espressif.com/en/products/socs/esp32)
- 3 channel Relay
- Local Wi-Fi (ESP32 and PC must be on the same network)
- Optional output devices: relay, buzzer, LED, etc.

---

### 📂 Project Files

- `donasi.py` – Python script for reading TikTok Live gifts and sending data to ESP32.
- `donasi.bat` – Windows batch file to launch the script quickly.
- `TiktokIntegration.ino` – Arduino code for ESP32 that listens for `/gift` POST requests and responds to gift data.

---

### 🚀 How to Use

#### 1. Flash ESP32

Upload the `TiktokIntegration.ino` sketch to your ESP32 using the Arduino IDE. Ensure the Wi-Fi credentials and static IP match the Python script.

#### 2. Set Up Python Environment

Install dependencies:

```bash
pip install TikTokLive rich requests
```

#### 3. Run the Script

You can run the script directly:

```bash
python donasi.py your_tiktok_username
```

Or double-click `donasi.bat` (after editing it to include your TikTok username).

#### 4. Go Live on TikTok

Once you start your live session, the script will connect and monitor gift events in real time. When a gift is received, the ESP32 will react based on your code logic.

---

### 🧪 Example Use Case

> A fan sends you a “Galaxy” gift on TikTok Live → your buzzer rings + LED flashes on your ESP32 desk setup.

---

### 📌 Notes

- Ensure your PC and ESP32 are on the **same local network**.
- This integration is **local-only**; it does not expose anything to the internet.
- You can expand this to support follower events, likes, etc., by modifying the script.

---

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// Web server object
WebServer server(80);

// Relay pins
int relay_pin_1 = 4;
int relay_pin_2 = 5;
int relay_pin_3 = 2;

// Wi-Fi configuration
String wifi_ssid = "";
String wifi_password = "";

// Mode AP credentials
const char* ap_ssid = "ESP32-pakan"; // Nama Wi-Fi yang dipancarkan ESP32
const char* ap_password = "12345678"; // Password Wi-Fi ESP32

unsigned long relayStartTime = 0;
int relayDuration = 0; // Duration for relay activation (in seconds)
bool isRelayActive = false;

// Function prototypes
void handleRoot();
void handleScanWiFi();
void handleSaveWiFi();
void handleGift();
void activateRelay(int relayPin);
void deactivateRelay(int relayPin);
void connectToWiFi();

void setup() {
    Serial.begin(115200);

    // Initialize relay pins
    pinMode(relay_pin_1, OUTPUT);
    pinMode(relay_pin_2, OUTPUT);
    pinMode(relay_pin_3, OUTPUT);
    digitalWrite(relay_pin_1, HIGH); // Ensure relays are off initially
    digitalWrite(relay_pin_2, HIGH);
    digitalWrite(relay_pin_3, HIGH);

    // Start in AP mode
    WiFi.softAP(ap_ssid, ap_password);
    Serial.println("Access Point started");
    Serial.print("AP SSID: ");
    Serial.println(ap_ssid);
    Serial.print("AP IP Address: ");
    Serial.println(WiFi.softAPIP());

    // Set up the server routes
    server.on("/", handleRoot);               // Root page for Wi-Fi configuration
    server.on("/scan", handleScanWiFi);       // Endpoint to scan available Wi-Fi networks
    server.on("/savewifi", handleSaveWiFi);   // Endpoint to save Wi-Fi credentials
    server.on("/gift", HTTP_POST, handleGift); // Endpoint for gift handling

    // Start the server
    server.begin();
    Serial.println("Server started");
}

void loop() {
    server.handleClient();

    // Non-blocking relay control
    if (isRelayActive && (millis() - relayStartTime >= relayDuration * 1000)) {
        deactivateRelay(relay_pin_1);
        deactivateRelay(relay_pin_2);
        deactivateRelay(relay_pin_3);
        isRelayActive = false;
    }
}

// Handle root page (Wi-Fi configuration)
void handleRoot() {
    String html = R"(
        <html>
            <body>
                <h1>Wi-Fi Configuration</h1>
                <p>Scan available Wi-Fi networks:</p>
                <button onclick="window.location.href='/scan'">Scan Wi-Fi</button>
            </body>
        </html>
    )";
    server.send(200, "text/html", html);
}

// Handle scanning available Wi-Fi networks
void handleScanWiFi() {
    String html = R"(
        <html>
            <body>
                <h1>Available Wi-Fi Networks</h1>
                <form action="/savewifi" method="POST">
                    <label for="ssid">Select SSID:</label><br>
                    <select name="ssid" id="ssid">
    )";

    // Scan for available networks
    int numNetworks = WiFi.scanNetworks();
    for (int i = 0; i < numNetworks; i++) {
        html += "<option value=\"" + WiFi.SSID(i) + "\">" + WiFi.SSID(i) + "</option>";
    }

    html += R"(
                    </select><br>
                    <label for="password">Password:</label><br>
                    <input type="password" name="password" id="password"><br>
                    <input type="submit" value="Connect">
                </form>
            </body>
        </html>
    )";
    server.send(200, "text/html", html);
}

// Handle saving Wi-Fi credentials
void handleSaveWiFi() {
    if (server.method() == HTTP_POST) {
        wifi_ssid = server.arg("ssid");
        wifi_password = server.arg("password");

        // Send response
        server.send(200, "text/plain", "Connecting to Wi-Fi...");

        // Connect to the selected Wi-Fi
        connectToWiFi();
    } else {
        server.send(405, "text/plain", "Method Not Allowed");
    }
}

// Handle gift endpoint
void handleGift() {
    if (server.method() == HTTP_POST) {
        // Parse JSON from the request body
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, server.arg("plain"));

        if (error) {
            server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"Invalid JSON\"}");
            return;
        }

        const char* gift = doc["gift"];
        int points = doc["points"];
        const char* user = doc["user"];

        // Log to serial monitor
        Serial.printf("Received gift: %s\n", gift);
        Serial.printf("Points: %d\n", points);
        Serial.printf("From user: %s\n", user);

        // Determine relay activation duration based on points
        if (points >= 0 && points <= 5) {
            relayDuration = 1; // 1 second activation
            activateRelay(relay_pin_1); // Activate relay 1
        } else if (points >= 6 && points <= 20) {
            relayDuration = 2; // 2 seconds activation
            activateRelay(relay_pin_2); // Activate relay 2
        } else if (points >= 21 && points <= 50) {
            relayDuration = 3; // 3 seconds activation
            activateRelay(relay_pin_3); // Activate relay 3
        } else if (points >= 51 && points <= 100) {
            relayDuration = 4; // 4 seconds activation
            activateRelay(relay_pin_1); // Activate relay 1
            activateRelay(relay_pin_2); // Activate relay 2
        } else {
            relayDuration = 5; // 5 seconds activation for higher points
            activateRelay(relay_pin_1); // Activate relay 1
            activateRelay(relay_pin_2); // Activate relay 2
            activateRelay(relay_pin_3); // Activate relay 3
        }

        // Send a success response
        server.send(200, "application/json", "{\"status\":\"success\"}");
    } else {
        server.send(405, "application/json", "{\"status\":\"error\",\"message\":\"Method Not Allowed\"}");
    }
}

// Activate relay
void activateRelay(int relayPin) {
    digitalWrite(relayPin, LOW); // Relay aktif LOW (sesuaikan dengan modul relay Anda)
    relayStartTime = millis();
    isRelayActive = true;
    Serial.printf("Relay on pin %d activated for %d seconds...\n", relayPin, relayDuration);
}

// Deactivate relay
void deactivateRelay(int relayPin) {
    digitalWrite(relayPin, HIGH); // Relay non-aktif HIGH (sesuaikan dengan modul relay Anda)
    Serial.printf("Relay on pin %d deactivated.\n", relayPin);
}

// Connect to Wi-Fi with static IP
void connectToWiFi() {
    // Configure static IP
    IPAddress staticIP(192, 168, 0, 116);  // IP statis yang diinginkan
    IPAddress subnet(255, 255, 255, 0);    // Subnet mask

    // Apply static IP configuration
    if (!WiFi.config(staticIP, gateway, subnet)) {
        Serial.println("Failed to configure static IP!");
        return;
    }

    // Connect to Wi-Fi
    WiFi.begin(wifi_ssid.c_str(), wifi_password.c_str());
    Serial.println("\nConnecting to Wi-Fi...");

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nConnected to Wi-Fi");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());

        // Matikan mode AP setelah terhubung ke Wi-Fi
        WiFi.softAPdisconnect(true); // true = matikan mode AP
        Serial.println("Access Point mode disabled.");
    } else {
        Serial.println("\nFailed to connect to Wi-Fi. Please check credentials.");
    }
}
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// Wi-Fi credentials
const char* ssid = "";   // Ganti dengan nama WiFi Anda
const char* password = ""; // Ganti dengan password WiFi Anda

// Relay pins
int relay_pin_1 = 4;
int relay_pin_2 = 5;
int relay_pin_3 = 2;

WebServer server(80);

unsigned long relayStartTime = 0;
int relayDuration = 0; // Duration for relay activation (in seconds)
bool isRelayActive = false;

void handleGift() {
    if (server.method() == HTTP_POST) {
        // Parse JSON from the request body
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, server.arg("plain"));

        if (error) {
            server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"Invalid JSON\"}");
            return;
        }

        const char* relay = doc["relay"]; 
        int waktu = doc["waktu"];    
        const char* user = doc["user"];  

        // Log to serial monitor
        Serial.printf("Received relay command: %s\n", relay);
        Serial.printf("Duration: %d seconds\n", waktu);
        Serial.printf("From user: %s\n", user);

        // Determine relay activation based on relay command
        if (strcmp(relay, "relay1nyala") == 0) {
            relayDuration = waktu;
            activateRelay(relay_pin_1);
        } else if (strcmp(relay, "relay2nyala") == 0) {
            relayDuration = waktu;
            activateRelay(relay_pin_2);
        } else if (strcmp(relay, "relay3nyala") == 0) {
            relayDuration = waktu;
            activateRelay(relay_pin_3);
        } else if (strcmp(relay, "semuarelaynyala") == 0) {
            relayDuration = waktu;
            activateAllRelays();
        } else {
            Serial.println("Unknown relay command received.");
        }

        // Send a success response
        server.send(200, "application/json", "{\"status\":\"success\"}");
    } else {
        server.send(405, "application/json", "{\"status\":\"error\",\"message\":\"Method Not Allowed\"}");
    }
}

void activateRelay(int relayPin) {
    digitalWrite(relayPin, LOW);
    relayStartTime = millis();
    isRelayActive = true;
    Serial.printf("Activating relay %d for %d seconds...\n", relayPin, relayDuration);
}

void activateAllRelays() {
    digitalWrite(relay_pin_1, LOW);
    digitalWrite(relay_pin_2, LOW);
    digitalWrite(relay_pin_3, LOW);

    relayStartTime = millis();
    isRelayActive = true;
    Serial.printf("Activating all relays for %d seconds...\n", relayDuration);
}

void deactivateAllRelays() {
    digitalWrite(relay_pin_1, HIGH);
    digitalWrite(relay_pin_2, HIGH);
    digitalWrite(relay_pin_3, HIGH);

    isRelayActive = false;
    Serial.println("All relays deactivated.");
}

void setup() {
    Serial.begin(115200);

    // Initialize relay pins
    pinMode(relay_pin_1, OUTPUT);
    pinMode(relay_pin_2, OUTPUT);
    pinMode(relay_pin_3, OUTPUT);

    // Deactivate all relays initially
    deactivateAllRelays();

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    Serial.println("\nConnecting to Wi-Fi...");

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }

    Serial.println("\nConnected to Wi-Fi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Set up the server routes
    server.on("/gift", HTTP_POST, handleGift);

    // Start the server
    server.begin();
    Serial.println("Server started");
}

void loop() {
    server.handleClient();

    // Non-blocking relay control
    if (isRelayActive && (millis() - relayStartTime >= relayDuration * 1000)) {
        deactivateAllRelays();
    }
}

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

// Create a web server object
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

        const char* gift = doc["gift"];
        int points = doc["points"];
        const char* user = doc["user"];

        // Log to serial monitor
        Serial.printf("Received gift: %s\n", gift);
        Serial.printf("Points: %d\n", points);
        Serial.printf("From user: %s\n", user);

        // Determine relay activation duration based on points
        switch (points) {
            case 0 ... 2:
                relayDuration = 1; // 1 second activation
                activateRelay(relay_pin_1);
                break;
            case 3 ... 19:
                relayDuration = 2; // 2 seconds activation
                activateAllRelays();
                
                break;
            case 20 ... 50:
                relayDuration = 3; // 3 seconds activation
                activateAllRelays();
                break;
            case 51 ... 100:
                relayDuration = 4; // 4 seconds activation
                activateRelay(relay_pin_1);
                break;
            default:
                relayDuration = 5; // 5 seconds activation for higher points
                activateRelay(relay_pin_2);
                break;
        }

        // Send a success response
        server.send(200, "application/json", "{\"status\":\"success\"}");
    } else {
        server.send(405, "application/json", "{\"status\":\"error\",\"message\":\"Method Not Allowed\"}");
    }
}

void activateRelay(int relayPin) {
    digitalWrite(relayPin, LOW); // Activate relay (assuming LOW triggers the relay)
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

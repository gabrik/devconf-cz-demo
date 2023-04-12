#include <Arduino.h>
#include <WiFi.h>
#include "Ultrasonic.h"


extern "C" {
#include <zenoh-pico.h>
}

// Board config
#define SENSOR 17

// WiFi config
#define SSID "SSID"
#define PASS "PASS"

// Zenoh config
#define MODE "client"
#define PEER "" // Empty means it will scout
#define KEYEXPR "demo/devconf/ultrasonic"

Ultrasonic ultrasonic(SENSOR);
z_owned_publisher_t pub;
uint8_t buf[sizeof(long)];


void serialize_long_little_endian(long num, uint8_t *buffer) {
  for (int i = 0; i < sizeof(long); i++) {
    buffer[i] = (num >> (8 * i)) & 0xFF;
  }
}

void setup()
{
    Serial.begin(115200);
    while (!Serial) {
        delay(1000);
    }

    // Set WiFi in STA mode and trigger attachment
    Serial.print("[WiFi] Init...");
    WiFi.mode(WIFI_STA);
    WiFi.begin(SSID, PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
    }
    Serial.println("[WiFi] Done");

    Serial.println("[Zenoh] init...");
    // Initialize Zenoh Session and other parameters
    z_owned_config_t config = z_config_default();
    zp_config_insert(z_config_loan(&config), Z_CONFIG_MODE_KEY, z_string_make(MODE));
    if (strcmp(PEER, "") != 0) {
        zp_config_insert(z_config_loan(&config), Z_CONFIG_PEER_KEY, z_string_make(PEER));
    }

    // Open Zenoh session
    z_owned_session_t s = z_open(z_config_move(&config));
    if (!z_session_check(&s)) {
        Serial.println("[Zenoh] Error: Unable to open session!");
        while (1) {
            ;
        }
    }
    Serial.println("[Zenoh] Session Opened");

    zp_start_read_task(z_session_loan(&s), NULL);
    zp_start_lease_task(z_session_loan(&s), NULL);

    Serial.println("[Zenoh] Tasks started");

    // Declare Zenoh publisher

    pub = z_declare_publisher(z_session_loan(&s), z_keyexpr(KEYEXPR), NULL);
    if (!z_publisher_check(&pub)) {
        Serial.print("[Zenoh] Error: Unable to declare publisher for key expression: ");
        Serial.println(KEYEXPR);
        while (1) {
            ;
        }
    }
    Serial.println("[Zenoh] Done");

    delay(300);
}


void loop()
{
    long RangeInCentimeters;
    RangeInCentimeters = ultrasonic.MeasureInCentimeters();

    Serial.print("The distance to obstacles in front is: ");
    Serial.print(RangeInCentimeters);//0~400cm
    Serial.println(" cm");
    Serial.print("Sending on: ");
    Serial.println(KEYEXPR);

    serialize_long_little_endian(RangeInCentimeters, buf);

    z_publisher_put_options_t opt = z_publisher_put_options_default();
    opt.encoding = z_encoding(Z_ENCODING_PREFIX_APP_INTEGER, NULL);
    if (z_publisher_put(z_publisher_loan(&pub), (const uint8_t *)buf, sizeof(long), &opt) < 0) {
        Serial.println("Error while publishing data");
    }

    delay(250);
}
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <WiFiNINA.h>
#include <ThingSpeak.h>

// Replace with your network credentials
char ssid[] = "M30s";
char pass[] = "vcvw3532";

// Replace with your ThingSpeak channel settings
unsigned long channelId = 2300330;
const char *thingSpeakApiKey = "EWD18Q4HSUDRBLVN";

// Raspberry Pi's IP address and port
const char *raspberryPiIp = "192.168.31.29";
const int raspberryPiPort = 12345;

// Create an instance of the MLX90614 sensor
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

const int buttonPin = 3;  // Push button connected to digital pin 3
const int ecgPin = A0;    // Analog pin connected to the ECG signal
const int analogPin = A0; // Analog pin to which the heart rate sensor is connected

WiFiClient client;  // Define the WiFiClient

void setup() {
  Serial.begin(9600);
  mlx.begin();  // Initialize the MLX90614 sensor
  pinMode(buttonPin, INPUT_PULLUP); // Set the push button pin as INPUT with an internal pull-up resistor

  // Connect to Wi-Fi
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  // Read temperature from the MLX90614 sensor
  float bodyTemperature = mlx.readObjectTempC();

  // Print the temperature to the Serial Monitor
  Serial.print("Body Temperature: ");
  Serial.print(bodyTemperature);
  Serial.println(" °C");

  // Check if the push button is pressed
  if (digitalRead(buttonPin) == LOW) {
    Serial.println("Button Pressed!");
    // You can add code here to perform some action when the button is pressed
  }

  // Read the ECG value
  int ecgValue = analogRead(ecgPin);
  // Print the ECG value to the Serial Monitor
  Serial.print("ECG Value: ");
  Serial.println(ecgValue);

  // Read the analog value from the heart rate sensor
  int sensorValue = analogRead(analogPin);

  // Calculate the heart rate (adjust the formula as needed)
  // This is a simple example; you may need to fine-tune the formula
  int heartRate = map(sensorValue, 0, 1023, 40, 180);

  // Print the heart rate value to the Serial Monitor
  Serial.print("Heart Rate: ");
  Serial.println(heartRate);

  // Send data to ThingSpeak
  ThingSpeak.begin(client);
  ThingSpeak.setField(1, heartRate);
  ThingSpeak.setField(2, bodyTemperature);
  ThingSpeak.setField(3, ecgValue);

  int writeStatus = ThingSpeak.writeFields(channelId, thingSpeakApiKey);
  if (writeStatus == 200) {
    Serial.println("Data sent to ThingSpeak successfully.");
  } else {
    Serial.println("Error sending data to ThingSpeak.");
  }

  // Send data to Raspberry Pi
  if (client.connect(raspberryPiIp, raspberryPiPort)) {
    String dataToSend = "Heart Rate: " + String(heartRate) + " BPM, Body Temp: " + String(bodyTemperature) + " °C, ECG: " + String(ecgValue);
    client.println(dataToSend);
    client.stop();
  } else {
    Serial.println("Failed to connect to Raspberry Pi.");
  }

  delay(1000); // Adjust the delay as needed between readings
}

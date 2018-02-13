#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define THROTTLE_PIN 0              // ESC an Ansdhluss 0 des PCA9685
#define STEERING_PIN 1              // Servo an Ansdhluss 1 des PCA9685
#define MINPULSE_THROTTLE 247       // Min. Pulsdauer bezogen auf 4096
#define MAXPULSE_THROTTLE 469       // Max. Pulsdauer bezogen auf 4096
#define MINPULSE_STEERING 220       // Min. Pulsdauer bezogen auf 4096
#define MAXPULSE_STEERING 460       // Max. Pulsdauer bezogen auf 4096
#define STATE_STOP_READ_COMMANDS '>'
#define STATE_READ_STEERING 'S'
#define STATE_READ_THROTTLE 'T'
#define STATE_READ_POWER 'P'
#define STATE_READ_LIGHT 'L'
#define STATE_READ_BUZZER 'B'
#define STATE_SEND_LIGHT 'L'
#define STATE_SEND_POWER 'P'
#define STATE_SEND_VOLTAGE 'V'
#define SOFT_RX 5
#define SOFT_TX 6
#define BUZZER_SIGNAL 7
#define RELAIS_LIGHT_POWER 2
#define RELAIS_MEASURE_VOLTAGE 3
#define RELAIS_CAR_POWER 4
#define MEASURE_VOLTAGE_INPUT 6

SoftwareSerial softSerial(SOFT_RX, SOFT_TX);
Adafruit_PWMServoDriver pwmCar = Adafruit_PWMServoDriver(); // Initialisierung von PCA9685

char c, state;;
String value, knownCommands;
boolean readyToReceive;
int defaultSteeringValue, defaultThrottleValue;

void setup() {
  // Initialisierung der Variablen
  readyToReceive = false;
  knownCommands = "STPLB";
  c = 'c';

  // notwendig???
  defaultSteeringValue = 90;
  defaultThrottleValue = 90;

  // Pins konfigurieren
  pinMode(RELAIS_CAR_POWER, OUTPUT);
  pinMode(RELAIS_LIGHT_POWER, OUTPUT);
  pinMode(RELAIS_MEASURE_VOLTAGE, OUTPUT);
  pinMode(BUZZER_SIGNAL, INPUT);      // ansonsten (bei OUTPUT) ist die Hupe auch bei LOW aktiv

  pwmCar.begin();         // Starten des PCA9685
  pwmCar.setPWMFreq(60);  // Festlegen der Frequenz von 60 Hz (entspricht 16,6 ms Periodendauer)

  // Kommunikation festlegen
  Serial.begin(9600);     // Serieller Monitor
  softSerial.begin(9600); // Verbindung zu HM-10
  Serial.println("RC Control gestartet: ");
}

void loop() {
  // Daten vom BLE Gerät lesen
  if (softSerial.available() > 0) {
    c = softSerial.read();

    // Kommando ausfuehren
    if (readyToReceive && (c == STATE_STOP_READ_COMMANDS)) {
      int commandValue = value.toInt();
      // Aufruf der Funktion zum Ausfuehren der Befehle
      setCommand(commandValue);
      readyToReceive = false;
    }

    // gueltigen Kommandotyp erkennen
    if (knownCommands.indexOf(c) + 1) {
      state = c;
      value = "";
      readyToReceive = true;
    } else if (readyToReceive) {
      value += c;
    }
  }

  // Aktualisierung der Akkuanzeige alle 10 Sekunden
  if ((millis() % 10000) == 0) {
    measureVoltage();
  }

}

// Umsetzung der Befehle je nach Befehlsart
void setCommand(int commandValue) {
  /*// Ausgabe am seriellen Monitor zu Testzwecken
    Serial.print("Command: ");
    Serial.print(state);
    Serial.print(" Value: ");
    Serial.println(commandValue);*/

  switch (state) {
    case STATE_READ_STEERING:
      commandValue = map(commandValue, 0, 180, MINPULSE_STEERING, MAXPULSE_STEERING);
      pwmCar.setPWM(STEERING_PIN, 0, commandValue);
      break;
    case STATE_READ_THROTTLE:
      commandValue = map(commandValue, 0, 180, MINPULSE_THROTTLE, MAXPULSE_THROTTLE);
      pwmCar.setPWM(THROTTLE_PIN, 0, commandValue);
      break;
    case STATE_READ_POWER:
      digitalWrite(RELAIS_CAR_POWER, commandValue); // Relais Auto Ein / Aus
      if (commandValue) {
        digitalWrite(RELAIS_CAR_POWER, commandValue); // Relais Auto einschalten
        commandValue = map(defaultSteeringValue, 0, 180, MINPULSE_STEERING, MAXPULSE_STEERING);
        pwmCar.setPWM(STEERING_PIN, 0, commandValue);
        commandValue = map(defaultThrottleValue, 0, 180, MINPULSE_THROTTLE, MAXPULSE_THROTTLE);
        pwmCar.setPWM(THROTTLE_PIN, 0, commandValue);
        measureVoltage();   // Aktualisierung der Akkuanzeige
      }
      break;
    case STATE_READ_LIGHT:
      digitalWrite(RELAIS_LIGHT_POWER, commandValue);
      break;
    case STATE_READ_BUZZER:
      if (commandValue)
        tone(BUZZER_SIGNAL, 800);
      else {
        noTone(BUZZER_SIGNAL);
        pinMode(BUZZER_SIGNAL, INPUT);
      }
      break;
  }
}

// Messung der Akkuspannung
void measureVoltage() {
  int voltage;
  digitalWrite(RELAIS_MEASURE_VOLTAGE, HIGH);   // Relais zur Messung ansteuern
  delay(1);                                     // Schaltzeit (0,5 ms) abwarten
  voltage = analogRead(MEASURE_VOLTAGE_INPUT);  // Wert auslesen (777-1023)
  voltage = map(voltage, 777, 1023, 0, 100);    // Wert in Bereich 0-100% skalieren
  voltage = constrain(voltage, 0, 100);         // falls nicht im Bereich - eingrenzen
  digitalWrite(RELAIS_MEASURE_VOLTAGE, LOW);    // Relais ausschalten
  sendFeedback(STATE_SEND_VOLTAGE, voltage);    // Senden der Akkuspannung zu der App
}

// Senden der Rueckmeldungen
void sendFeedback(char feedbackState, int feedbackValue) {
  String feedbackCommand = "";
  feedbackCommand += feedbackState;
  feedbackCommand += feedbackValue;
  Serial.println(feedbackCommand);   // Nur zum Testen!!!
  softSerial.print(feedbackCommand);
}







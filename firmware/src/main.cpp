#include <Arduino.h>

const int xPin = 2; // X axis connected to GPIO 2
const int yPin = 3; // Y axis connected to GPIO 3

const int numReadings = 5; // Number of readings to average
int xReadings[numReadings];
int yReadings[numReadings];
int readIndex = 0;
int xTotal = 0;
int yTotal = 0;

void setup()
{
  Serial.begin(115200);
  while (!Serial)
  {
    ; // wait for serial port to connect. Needed for native USB
  }

  for (int i = 0; i < numReadings; i++)
  {
    xReadings[i] = 0;
    yReadings[i] = 0;
  }
}

void loop()
{
  xTotal = xTotal - xReadings[readIndex];
  yTotal = yTotal - yReadings[readIndex];

  xReadings[readIndex] = analogRead(xPin);
  yReadings[readIndex] = analogRead(yPin);

  xTotal = xTotal + xReadings[readIndex];
  yTotal = yTotal + yReadings[readIndex];

  readIndex = (readIndex + 1) % numReadings;

  int xAverage = xTotal / numReadings;
  int yAverage = yTotal / numReadings;

  int xMapped = map(xAverage, 0, 4095, -100, 100);
  int yMapped = map(yAverage, 0, 4095, -100, 100);

  // Apply a dead zone
  if (abs(xMapped) < 10)
    xMapped = 0;
  if (abs(yMapped) < 10)
    yMapped = 0;

  // Send the data over serial
  Serial.print(xMapped);
  Serial.print(",");
  Serial.println(yMapped);

  delay(20); // Adjust this for responsiveness vs stability
}

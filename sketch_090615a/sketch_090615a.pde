void setup() {
// initialize the serial communication:
  Serial.begin(9600);
}

void loop() {
// Code copied from http://code.google.com/p/arduinoscope/source/browse/trunk/arduino_oscilliscope.pde
  Serial.print(analogRead(1));
  Serial.print(" ");
  Serial.print(analogRead(2));
  Serial.println();
  delay(1000); // 1Hz data should more than suffice!
}

/*
    THIS PROGRAM IS TO ARDUINO BUTTON CONTROLLER
         SEE THE DIAGRAMS TO MOUNT PROPERLY
      ----------------------------------------
         PHOTOCALL_PY BY Jaime Iranzo Ferri
*/

bool blink = false;
const int buttonPin = 2;
const int ledPin =  7;
int buttonState = 0;
int long_blink = 6;
int short_blink = 11;
int photo_shots = 1; // Amount of photo shots
int count = 0;
unsigned int blink_wait_max = 65535;

void setup()
{
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT);
  Serial.begin(9600);
}

void loop()
{
  serialReader();
  blink_led();
  read_button();
  blink_wait();
  count++;
}

void read_button()
{
  buttonState = digitalRead(buttonPin);
  if (buttonState == HIGH)
  {
    blink = true;
  }
}

void blink_wait()
{
  if ( ! blink && count >= blink_wait_max)
  {
    digitalWrite(ledPin, HIGH);
    delay(10);
    digitalWrite(ledPin, LOW);
    count = 0;
  }
}

void blink_led()
{
  if ( blink )
  {
    for (int i = 0;i<photo_shots;i++)
    {
      for (int i=0;i<long_blink;i++)
      {
        digitalWrite(ledPin, HIGH);
        delay(200);
        digitalWrite(ledPin, LOW);
        delay(300);
      }

      for (int i=0;i<short_blink;i++)
      {
        digitalWrite(ledPin, HIGH);
        delay(100);
        digitalWrite(ledPin, LOW);
        delay(100);
      }

      blink = false;
      Serial.write("ready\n");
      digitalWrite(ledPin, HIGH);
      delay(3000);
      digitalWrite(ledPin, LOW);
    }
  }
}

void serialReader()
{
  int makeSerialStringPosition;
  int inByte;
  char serialReadString[50];
  const int terminatingChar = 13; // Terminate lines with CR

  inByte = Serial.read();
  makeSerialStringPosition=0;

  if (inByte > 0 && inByte != terminatingChar)
  {
    delay(100); // Take some time to collect

    while (inByte != terminatingChar && Serial.available() > 0)
    {
      serialReadString[makeSerialStringPosition] = inByte;
      makeSerialStringPosition++;
      inByte = Serial.read();
    }

    if (inByte == terminatingChar)
    {
      serialReadString[makeSerialStringPosition] = 0;
      Serial.println(serialReadString);

      if (strcmp(serialReadString, "foto") == 0) blink = true;
      
      if (strcmp(serialReadString, "fin") == 0) blink = false;
    }
  } 
}

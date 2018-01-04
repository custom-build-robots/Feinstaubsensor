void setup() {
    Serial.begin(9600);
}

void mock_sds011() {
    int value = 0;
  
    while (1) {
        int pm_25 = value * 10;
        int pm_10 = (value + 10) * 10;
      
        unsigned char buffer[10];
        unsigned char *bp = buffer;
        *bp++ = 0xAA;
        *bp++ = 0xC0;
        *bp++ = pm_25 % 256;
        *bp++ = pm_25 / 256;
        *bp++ = pm_10 % 256;
        *bp++ = pm_10 / 256;
        *bp++ = 0x12;
        *bp++ = 0x34;
        unsigned int sum = buffer[2] + buffer[3] +  buffer[4] + buffer[5] + buffer[6] + buffer[7]; 
        *bp++ = sum % 256;
        *bp++ = 0xAB;
      
        Serial.write(buffer, 10);
        Serial.flush();
      
        delay(1000);

        value += 10;
        if (value > 2500) value = 0;
    }
}

void hello() {
    int value = 0;
  
    while (1) {
        Serial.print("Hello ");
        Serial.println(value);
        Serial.flush();
        
        delay(1000);

        value ++;
        if (value > 9999) value = 0;
    }
}

void loop() {
    mock_sds011();
}


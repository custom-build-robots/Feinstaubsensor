# Mobiler Feinstaubsensor - Software
Hier finden Sie das Python Programm fuer den Nachbau des Feinstaubsensors auf Basis eines Raspberry Pi, SDS011 Feinstaubsensors und einem GPS Empfaengers wie in der C't 1/2018 beschreiben https://www.heise.de/ct/ausgabe/2018-1-Feinstaub-unterwegs-messen-und-mit-GPS-Daten-aufzeichnen-3919188.html. 
Die Bedienung des Feinstaubsensors erfolgt ueber eine Web-Oberflaeche die durch den Flask Web-Server bereitgestellt wird.
## Komponentenliste
Die Liste der Komponenten die Sie benoetigen um den mobilen Feinstaubsensor selber bauen zu koennen finden Sie auf meinem Blog: 
https://www.byteyourlife.com/haushaltsgeraete/feinstaubsensor-komponentenliste/7369

## Version 0.1
Die erste Version der mobilen Variante des Feinstaubsensors sah bei mir wie auf dem folgenden Bild gezeigt aus.
![ByteYourLife - Feinstaubsensor](https://www.byteyourlife.com/wp-content/uploads/2017/05/Mobiler_Feinstaubsensor_03-300x225.jpg)
## Version 1.0
Die aktuelle Version des mobilen Feinstaubsensor sieht wie auf dem nachfolgenden Bild gezeigt aus.
![ByteYourLife - Feinstaubsensor](https://www.byteyourlife.com/wp-content/uploads/2017/10/Feinstaubsensor_small-300x200.jpg)
## Wunschliste
Folgende Erweiterungen wuerde ich gerne noch fuer die mobile Variante des Feinstaubsensors umsetzen. Einmal weitere Sensoren einbauen um einen Rueckschluss auf das Wetter zu erhalten sowie noch die Web-Oberflaeche optimieren.
### Luftfeuchte und Temperatur messen
Ich gehe davon aus, das abhaengig von der Luftfeuchte und Temperatur die Messwerte sich unterscheiden. Daher wuerde ich gerne diesen Daten auch noch mit erfassen. Als Sensor habe ich an einen DHT22 Sensor gedacht, der sich leicht an den Raspberry Pi anschließen laesst und guenstig in der Anschaffung ist.
### Luftdruck messen
Weiter spielt der Luftdruck wohl auch eine Rolle bei der Messung der Staeube in der Luft. Daher soll noch ein BMP085 Sensor den Luftdruck erfassen. 
### BME280 3 in 1 Sensor (Luftdruck, Luftfeuchte und Temperatur)
Mit dem Adafruit BME280 Sensor haette ich alle drei Sensoren auf einer Platine. Auch ist der I2C Bus klasse und die Ansteuerung dank der Bibliotheken von Adafruit mit Python recht einfach umzusetzen.
https://www.adafruit.com/product/2652
### Flask-SocketIO asynchrones Updates
Aktuell aktualisiert die Web-Overflaeche nur die gemessenen Werte wenn expliziet das refresh Button gedrueckt wird. Aber viel bessere waere es wenn die Werte in einem frei definierbaren Intervall aktualisiert werden also z. B. jede Sekunge.

# Mobiler Feinstaubsensor - Software
Hier finden Sie das Python Programm fuer den Nachbau des Feinstaubsensors auf Basis eines Raspberry Pi, SDS011 Feinstaubsensors und einem GPS Empfaengers. Die Bedienung des Feinstaubsensors erfolgt ueber eine Web-Oberflaeche die durch den Flask Web-Server bereitgestellt wird.
## Komponentenliste
Die Liste der Komponenten die Sie benoetigen um den mobilen Feinstaubsensor selber bauen zu koennen finden Sie auf meinem Blog: 
https://www.byteyourlife.com/haushaltsgeraete/feinstaubsensor-komponentenliste/7369

## Version 0.1
Die erste Version der mobilen Variante des Feinstaubsensors sah bei mir wie auf dem folgenden Bild gezeigt aus.
![ByteYourLife - Feinstaubsensor](https://www.byteyourlife.com/wp-content/uploads/2017/05/Mobiler_Feinstaubsensor_02-1200x640.jpg)
## Wunschliste
Folgende Erweiterungen wuerde ich gerne noch fuer die mobile Variante des Feinstaubsensors umsetzen. Einmal weitere Sensoren einbauen um einen Rueckschluss auf das Wetter zu erhalten sowie noch die Web-Oberflaeche optimieren.
### Luftfeuchte und Temperatur messen
Ich gehe davon aus, das abhaengig von der Luftfeuchte und Temperatur die Messwerte sich unterscheiden. Daher wuerde ich gerne diesen Daten auch noch mit erfassen. Als Sensor habe ich an einen DHT22 Sensor gedacht, der sich leicht an den Raspberry Pi anschließen laesst und guenstig in der Anschaffung ist.
### Luftdruck messen
Weiter spielt der Luftdruck wohl auch eine Rolle bei der Messung der Staeube in der Luft. Daher soll noch ein BMP085 Sensor den Luftdruck erfassen. 
### Flask-SocketIO asynchrones Updates
Aktuell aktualisiert die Web-Overflaeche nur die gemessenen Werte wenn expliziet das refresh Button gedrueckt wird. Aber viel bessere waere es wenn die Werte in einem frei definierbaren Intervall aktualisiert werden also z. B. jede Sekunge.

# Mobiler Feinstaubsensor - Software
Hier finden Sie das Python Programm fuer den Nachbau des Feinstaubsensors auf Basis eines Raspberry Pi, SDS011 Feinstaubsensors und einem GPS Empfaengers wie in der [C't 1/2018](https://www.heise.de/ct/ausgabe/2018-1-Feinstaub-unterwegs-messen-und-mit-GPS-Daten-aufzeichnen-3919188.html) beschrieben. 
Die Bedienung des Feinstaubsensors erfolgt ueber eine Web-Oberflaeche die durch den Flask Web-Server bereitgestellt wird.
## Komponentenliste
Die Liste der Komponenten die Sie benoetigen um den mobilen Feinstaubsensor selber bauen zu koennen finden Sie auf meinem Blog: [www.byteyourlife.com](https://www.byteyourlife.com/haushaltsgeraete/feinstaubsensor-komponentenliste/7369)

## Version 0.1
Die erste Version der mobilen Variante des Feinstaubsensors sah bei mir wie auf dem folgenden Bild gezeigt aus.
![ByteYourLife - Feinstaubsensor](https://www.byteyourlife.com/wp-content/uploads/2017/05/Mobiler_Feinstaubsensor_03-300x225.jpg)
## Version 1.0
Die aktuelle Version des mobilen Feinstaubsensor sieht wie auf dem nachfolgenden Bild gezeigt aus.
![ByteYourLife - Feinstaubsensor](https://www.byteyourlife.com/wp-content/uploads/2017/10/Feinstaubsensor_small-300x200.jpg)

## BME280 Sensor - fuer Luftdruck, Luffeuchte und Temperatur
In den Feinstaubsensor wurde noch ein Adafruit [BME280 Sensor](https://www.adafruit.com/product/2652) fuer Luftdruck, Luftfeuchte und Temperatur integriert. Die Programme wurden entsprechend angepasst. Damit der BME280 Sensor angesprochen wird und die Messwerte in die CSV Datei geschreiben werden muss das Programm "web_feinstaub_bme280.py" und die HTML Datei "index_bme280.html" verwendet werden. Entsprechend muss die Start Datei "feinstaub_start.sh" angepasst werden damit das Programm "web_feinstaub_bme280.py" automatisch nach dem Einschalten des Raspberry Pi gestartet wird.

![ByteYourLife - Feinstaubsensor](https://www.byteyourlife.com/wp-content/uploads/2017/12/Raspberry_Pi_mobiler_Feinstaubsensor_BME280_macro-768x512.jpg)

## Wunschliste
Die Wunschliste listet die Funktionen auf die ich noch gerne in das Projekt integrieren möchte.

### Flask-SocketIO asynchrones Updates
Aktuell aktualisiert die Web-Overflaeche nur die gemessenen Werte wenn expliziet das refresh Button gedrueckt wird. Aber viel bessere waere es wenn die Werte in einem frei definierbaren Intervall aktualisiert werden also z. B. jede Sekunge.

### Sleep / Measure Mode fuer den SDS011 Sensor
Ich würde sehr gerne eine Funktion in mein Programm integrieren die den SDS011 Sensor auch in den Sleep Mode versetzt wenn keine Messung erfolgen soll. Auch wäre es so möglich abhängig von der Geschwindigkeit den Messintervall des SDS011 einzustellen. Den Hinweis dazu habe ich von dem GitHub User [luetzel](https://github.com/luetzel) erhalten.
Ich habe mir das folgende Projekt jetzt genauer angeschaut und werde wohl auf diesem Code aufsetzen.
[Frank Heuer SDS011 Python](https://gitlab.com/frankrich/sds011_particle_sensor)


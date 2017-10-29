import os
import time
import serial, struct
from gps import *
#import csv
import datetime
from random import randint

from threading import Thread

from flask import Flask, jsonify, render_template, request
app = Flask(__name__)

global run
run = False

global status_text
status_text = "inaktiv"

global display_lat
global display_lon

display_lat = "keine GPS Aufzeichnung aktiv"
display_lon = "keine GPS Aufzeichnung aktiv"

global pm_10
global pm_25
pm_10 = 0
pm_25 = 0

# Default Farbe fuer die Weg-Linie in der KML Datei.
color = "#00000000"	
	
# Funktion fuer das Erfassen von Meldungen aus dem Programm heraus.
def write_log(msg):
	message = msg
	fname = "/home/pi/feinstaub/feinstaub_python_program.log"
	with open(fname,'a+') as file:
		file.write(str(message))
		file.write("\n")
		file.close()

# Hier wird die Farbe fuer die Linie festgelegt.
def color_selection(value):
	# red
	color = "#64009614"	
	if 50 <= value <= 2000:
		color = "#641400F0"
	# orange
	elif 25 <= value <= 49:
		color = "#641478FF"
	# green
	elif 0 <= value < 25:
		color = "#64009614"		
		
	return color

# Diese Funktion schreibt die KML Datei ohne die Wegstrecke anzuzeigen
def write_kml(value_pm, value_lat, value_lon, value_time, value_fname, type):	
	pm = value_pm
	lat = value_lat
	lon = value_lon
	time = value_time
	fname = value_fname
	
	try:
		if os.path.exists(fname):
			with open(fname,'a+') as file:
				file.write("   <Placemark>\n")
				file.write("       <name>"+type+": "+ pm +"</name>\n")
				file.write("       <description> Time: " + time + "</description>\n")
				file.write("       <Point>\n")
				file.write("           <coordinates>" + lon + "," + lat + ",0</coordinates>\n")
				file.write("       </Point>\n")
				file.write("   </Placemark>\n")	
				file.close()	

		else:
			with open(fname,'a+') as file:
				file.write("<?xml version='1.0' encoding='UTF-8'?>\n")
				file.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
				file.write("<Document>\n")
				file.write("   <name> Feinstaub_Punkte_" + type + "_" + datetime.datetime.now().strftime ("%Y%m%d") + ".kml </name>\n")
				file.write('\n')
				file.close()
	except Exception, e:
		write_log(str(e))

# Diese Funktion schreibt die KML Datei mit der zurueck gelegten Wegstrecke.
def write_kml_line(value_pm, value_pm_old, value_lon_old, value_lat_old, value_lat, value_lon, value_time, value_fname, type, value_color):
	pm = value_pm
	pm_old = value_pm_old
	lat_old = value_lat_old
	lon_old = value_lon_old
	lat = value_lat
	lon = value_lon
	time = value_time
	fname = value_fname
	color = value_color 
	try:
		if os.path.exists(fname):
			with open(fname,'a+') as file:
				file.write("   <Placemark>\n")
				file.write("       <LineString>\n")
				file.write("           <altitudeMode>relativeToGround</altitudeMode>\n")
				file.write("           <coordinates>" + lon + "," + lat + "," + pm + "\n           "+ lon_old+ ","+ lat_old+ "," + pm_old + "</coordinates>\n")
				file.write("       </LineString>\n")
				file.write("       <Style>\n")
				file.write("           <LineStyle>\n")
				file.write("               <color>" + color + "</color>\n")
				file.write("               <width>8</width>\n")
				file.write("           </LineStyle>\n")
				file.write("       </Style>\n")
				file.write("   </Placemark>\n")	
				file.close()	

		else:
			with open(fname,'a+') as file:
				file.write("<?xml version='1.0' encoding='UTF-8'?>\n")
				file.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
				file.write("<Document>\n")
				file.write("   <name> Feinstaub_Linie_"+type+"_" + datetime.datetime.now().strftime ("%Y%m%d") + ".kml </name>\n")
				file.write('\n')
				file.close()	
	except Exception, e:
		write_log(e)

# Diese Funktion schliesst das KML File ab.
def close_kml(file_name):
	try:
		with open(file_name,'a+') as file:
			file.write("  </Document>\n")
			file.write("</kml>\n")	
			file.close()
	except Exception, e:
		write_log(e)

def start_sensor():
	global run
	
	global display_lat
	global display_lon
	global pm_10
	global pm_25
	
	save_file = False
	# Variablen fuer die Messwerte vom Feinstaubsensor.
	byte, lastbyte = "\x00", "\x00"	
	
	# USB Geraetepfad des Feinstaubsensors bitte hier setzen.
	sds011 = "/dev/ttyUSB0"
	# GPS Koordinaten-Variable Vorgaengerwert.
	lat_old = "initial"
	lon_old = "initial"

	# Feinstaubwerte 25 und 10 als Vorgaengerwert.
	pm_old_25 = 0
	pm_old_10 = 0

	# Feinstaubwerte 25 und 10 als aktuelle Werte.
	pm_10 = 0
	pm_25 = 0

	# In diesem Abschnitt wird die serielle Verbindung zu dem Feinstaub-
	# sensor initialisiert.
	try:
		ser = serial.Serial(sds011, baudrate=9600, stopbits=1, parity="N", timeout=2)
	except Exception, e:
		write_log(e)

	try:
		ser.flushInput()
	except Exception, e:
		write_log(e)

	# Hier wird das Session Objekt fuer den GPS Stream angelegt.
	try:
		session = gps(mode=WATCH_ENABLE)	
	except Exception, e:
		write_log(e)
		
	while True:

		while run:
			if save_file == False:
				# micro-sd card paths for the kml files
				fname25 = '/home/pi/feinstaub/feinstaub_25_'+datetime.datetime.now().strftime ("%Y%m%d_%H_%M_%S")+'.kml'
				fname10 = '/home/pi/feinstaub/feinstaub_10_'+datetime.datetime.now().strftime ("%Y%m%d_%H_%M_%S")+'.kml'

				fname25_line = '/home/pi/feinstaub/feinstaub_25_line_'+datetime.datetime.now().strftime ("%Y%m%d_%H_%M_%S")+'.kml'
				fname10_line = '/home/pi/feinstaub/feinstaub_10_line_'+datetime.datetime.now().strftime ("%Y%m%d_%H_%M_%S")+'.kml'			
			save_file = True
			

			
			# start logic
			
			time.sleep(0.5)
			
			lastbyte = byte
			try:
				byte = ser.read(size=1)
			except Exception, e:
				write_log(e)


			# We got a valid packet header
			if lastbyte == "\xAA" and byte == "\xC0":
				try:
					sentence = ser.read(size=8) # Read 8 more bytes
					# Decode the packet - big endian, 2 shorts for 
					# pm2.5 and pm10, 2 reserved bytes, checksum, 
					# message tail
					readings = struct.unpack('<hhxxcc',sentence) 
				except Exception, e:
					write_log(e)
				pm_25 = readings[0]/10.0
				pm_10 = readings[1]/10.0
			
			# Lese die aus der GPS session die akt. Koordinaten
			session.next()

					

			# Nur wenn eine gueltige FIX Positon bekannt istitle
			# Zeichne die GPS Daten und Feinstaubwerte in einer
			# KML Datei auf.
			
			if -90 <= session.fix.latitude <= 90 and session.fix.latitude != 0:
				if lat_old == "initial":
					lat_old = session.fix.latitude

				if lon_old == "initial":	
					lon_old = session.fix.longitude
				
				write_kml(str(pm_25), str(session.fix.latitude), str(session.fix.longitude), str(session.utc), fname25, "25")
				write_kml(str(pm_10), str(session.fix.latitude), str(session.fix.longitude), str(session.utc), fname10, "10")
				
				color_25 = color_selection(pm_25)
				color_10 = color_selection(pm_10)
				
				time.sleep(0.2)
				
				write_kml_line(str(pm_25), str(pm_old_25), str(lon_old), str(lat_old), str(session.fix.latitude), str(session.fix.longitude), str(session.utc), fname25_line, "25", color_25)
				write_kml_line(str(pm_10), str(pm_old_10), str(lon_old), str(lat_old), str(session.fix.latitude), str(session.fix.longitude), str(session.utc), fname10_line, "10", color_10)

				lat_old = session.fix.latitude
				lon_old = session.fix.longitude
				
				display_lat = session.fix.latitude
				display_lon = session.fix.longitude
				
				pm_old_25 = pm_25
				pm_old_10 = pm_10
			else:
				display_lat = "Kein GPS fix gefunden, keine Aufzeichnung der Messwerte"
				display_lon = "Kein GPS fix gefunden, keine Aufzeichnung der Messwerte"
	
		if run == False:
			if save_file == True:
				#print "save file"
				# Hier werden die KML Dateien geschlossen.
				close_kml(fname25)
				time.sleep(0.2)	
				close_kml(fname10)
				time.sleep(0.2)	
				close_kml(fname25_line)
				time.sleep(0.2)	
				close_kml(fname10_line)
				time.sleep(0.2)	
				display_lat = "keine GPS Aufzeichnung aktiv"
				display_lon = "keine GPS Aufzeichnung aktiv"				
				save_file = False

# Diese Funktion schaltet den Raspberry Pi ab.				
def shutdownpi():
	time.sleep(3)
	os.system("sudo halt")

# Diese Funktion startet den Raspberry Pi neu.
def rebootpi():
	time.sleep(3)
	os.system("sudo reboot")

# Hier folgt der Abschnitt fuer den Flask Web-Server
@app.route('/')
def index():
	return render_template('index.html')
 
@app.route('/start/', methods=['GET'])
def start_measure():
	global run
	run = True
	global status_text
	status_text = "Aufzeichnung aktiv."
	ret_data = {"value": "Start der Aufzeichnung der Messwerte."}
	return jsonify(ret_data)


@app.route('/stopp/', methods=['GET'])
def stopp():
	global run
	run = False
	global status_text
	status_text = "Aufzeichnung inaktiv."	
	ret_data = {"value": "Aufzeichnung der Messwerte angehalten."}
	return jsonify(ret_data)

@app.route('/status/', methods=['GET'])
def status():
	global status_text
	global display_lat
	global display_lon
	global pm_10
	global pm_25
	
	ret_data = {"value": status_text, "lat": display_lat, "lon": display_lon, "pm_10": pm_10, "pm_25":pm_25}
	return jsonify(ret_data)
	
@app.route('/halt/', methods=['GET'])
def halt():
	global run
	run = False

	t_shutdown.start()
	
	ret_data = {"value": "Der Raspberry Pi schaltet sich in 10 Sekunden aus."}
	return jsonify(ret_data)

	
@app.route('/reboot/', methods=['GET'])
def reboot():
	global run
	run = False
	
	t_reboot.start()
	
	ret_data = {"value": "Der Raspberry Pi wird neugestartet"}
	return jsonify(ret_data)	
	
if __name__ == '__main__':
	t_shutdown = Thread(target=shutdownpi)
	t_reboot = Thread(target=rebootpi)	
	t_start_sensor = Thread(target=start_sensor)
	t_start_sensor.start()
	
	app.run(host='0.0.0.0', port=8181, debug=False)

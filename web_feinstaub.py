#!/usr/bin/env python
# coding: latin-1
# Autor:   Ingmar Stapel
# Datum:   20171103
# Version:   1.0
# Homepage:   https://www.byteyourlife.com/
# Dieses Programm ermoeglicht es einen mobilen Feinstaubsensor
# auf Basis eines Raspberry Pi Computers zu bauen.
# Ueber Anregungen und Verbesserungsvorschlaege wuerde
# ich mich sehr freuen.

import os
import time
import serial, struct
from gps import *

import datetime
from random import randint
import random

from threading import Thread
import threading

from flask import Flask, jsonify, render_template, request
app = Flask(__name__)

global session
session = None

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

global error_msg
error_msg = ""

# Hier wird der Speicherort fuer die KML Dateien und die LOG Dateien
# festgelegt. Aendern Sie hier zentral den Speicherort ab.
global save_path
save_path = "/home/pi/Feinstaubsensor/"

# Default Farbe fuer die Weg-Linie in der KML Datei.
color = "#00000000"	
	
# Funktion fuer das Erfassen von Fehlermeldungen 
# die waehrend dem Ablauf des Progammes entstehen koennen.
def write_log(msg):
	global dir_path
	global error_msg
	error_msg = msg
	message = msg
	fname = save_path+"feinstaub_python_program.log"
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
			# Hier ist eine sehr gute Dokumentation zu finden ueber
			# den Aufbau von KML Dateien.
			# https://developers.google.com/kml/documentation/kml_tut
				file.write("   <Placemark>\n")
				file.write("   <name>"+ pm +"</name>\n")
				file.write("    <description>"+ pm +"</description>\n")
				file.write("    <Point>\n")
				file.write("      <coordinates>" + lon + "," + lat + "," + pm + "</coordinates>\n")
				file.write("    </Point>\n")
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

# Klasse um auf den GPSD Stream via Thread zuzugreifen.
class GpsdStreamReader(threading.Thread):
	def __init__(self):
		global session
		threading.Thread.__init__(self)
		# 
		session = gps(mode=WATCH_ENABLE)
		self.current_value = None
		# Der Thread wird ausgefuehrt
		self.running = True
 
	def run(self):
		global session
		while t_gps.running:
			# Lese den naechsten Datensatz von GPSD
			session.next()	  

# Klasse um auf den SDS001 Sensor via Thread zuzugreifen.
class SDS001StreamReader(threading.Thread):
	def __init__(self):
		global byte
		global lastbyte
		global ser
		# Variablen fuer die Messwerte vom Feinstaubsensor.
		byte, lastbyte = "\x00", "\x00"	
		
		# USB Geraetepfad des Feinstaubsensors bitte hier setzen.
		sds011 = "/dev/ttyUSB0"
		threading.Thread.__init__(self)
		# Hier wird auf den Serial-USB Konverter zugegriffen
		try:
			ser = serial.Serial(sds011, baudrate=9600, stopbits=1, parity="N", timeout=2)
		except Exception, e:
			write_log("\n HL-340 USB-Serial Adapter nicht verfuegbar. \n"+str(e))

		try:
			ser.flushInput()
		except Exception, e:
			write_log(e)
		
		self.current_value = None
		# Der Thread wird ausgefuehrt
		self.running = True
 
	def run(self):
		global pm_25
		global pm_10
		global byte
		global lastbyte
		global ser
		
		while t_sds011.running:
			lastbyte = byte
			try:
				byte = ser.read(size=1)
			except Exception, e:
				write_log("\n Fehler HL-340 USB-Serial Adapter.\n"+str(e))


			# Wenn es ein gueltiges Datenpaket gibt bearbeite dieses
			if lastbyte == "\xAA" and byte == "\xC0":
				try:
					# Es werden 8 Byte eingelesen.
					sentence = ser.read(size=8) 
					# Das eingelesene Datenpaket wird dekodiert.
					readings = struct.unpack('<hhxxcc',sentence) 
				except Exception, e:
					write_log(("\n SDS011 Datenpaket kann nicht gelesen werden. \n"+str(e)))
					
				pm_25 = readings[0]/10.0
				pm_10 = readings[1]/10.0	  
			
			# Testwerte als Feinstaubwerte.
			#pm_25 = (random.randint(0,100))
			#pm_10 = pm_25
			
def start_sensor():
	global run
	global session
	global display_lat
	global display_lon
	global pm_10
	global pm_25
	global dir_path
	
	save_file = False

	# GPS Koordinaten-Variable Vorgaengerwert.
	lat_old = "initial"
	lon_old = "initial"

	# Feinstaubwerte 25 und 10 als Vorgaengerwert.
	pm_old_25 = 0
	pm_old_10 = 0

	while True:
				
		while run:
			if save_file == False:
				# micro-sd card paths for the kml files
				fname25_line = save_path+'feinstaub_25_line_'+datetime.datetime.now().strftime ("%Y%m%d_%H_%M_%S")+'.kml'
				fname10_line = save_path+'feinstaub_10_line_'+datetime.datetime.now().strftime ("%Y%m%d_%H_%M_%S")+'.kml'			
			save_file = True
			
			# Hier wird der Intervall gesetzt wie oft ein Wert
			# in die KML Datei geschrieben werden soll
			time.sleep(2)
			
			# Nur wenn eine gueltige FIX Positon bekannt istitle
			# Zeichne die GPS Daten und Feinstaubwerte in einer
			# KML Datei auf.
			
			if -90 <= session.fix.latitude <= 90 and session.fix.latitude != 0:
				if lat_old == "initial":
					lat_old = session.fix.latitude

				if lon_old == "initial":	
					lon_old = session.fix.longitude
				
				color_25 = color_selection(pm_25)
				color_10 = color_selection(pm_10)
				
				write_kml_line(str(pm_25), str(pm_old_25), str(lon_old), str(lat_old), str(session.fix.latitude), str(session.fix.longitude), str(session.utc), fname25_line, "25", color_25)
				write_kml_line(str(pm_10), str(pm_old_10), str(lon_old), str(lat_old), str(session.fix.latitude), str(session.fix.longitude), str(session.utc), fname10_line, "10", color_10)

				lat_old = session.fix.latitude
				lon_old = session.fix.longitude
				
				pm_old_25 = pm_25
				pm_old_10 = pm_10

	
		if run == False:
			if save_file == True:
				# Hier werden die KML Dateien geschlossen.
				close_kml(fname25_line)
				time.sleep(0.2)	
				close_kml(fname10_line)
				time.sleep(0.2)			
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
	global error_msg
	global session	
	display_lat = session.fix.latitude
	display_lon = session.fix.longitude	
	ret_data = {"value": status_text, "lat": display_lat, "lon": display_lon, "pm_10": pm_10, "pm_25":pm_25, "error_msg":error_msg}
	return jsonify(ret_data)
	
@app.route('/halt/', methods=['GET'])
def halt():
	global run
	run = False
	t_gps.running = False
	t_shutdown.start()
	t_gps.join()
	
	ret_data = {"value": "Der Raspberry Pi schaltet sich in 10 Sekunden aus."}
	return jsonify(ret_data)

	
@app.route('/reboot/', methods=['GET'])
def reboot():
	global run
	run = False
	t_gps.running = False
	t_reboot.start()
	t_gps.join()
	
	ret_data = {"value": "Der Raspberry Pi wird neugestartet"}
	return jsonify(ret_data)	
	
if __name__ == '__main__':

	# Start des Threads der den GPS Empfaenger ausliesst.
	t_gps = GpsdStreamReader()
	t_gps.start()
	
	# Start des Threads der den Feinstaubsensor ueber den USB-Serial
	# Konverter ausliesst.
	t_sds011 = SDS001StreamReader()
	t_sds011.start()
	
	# Kurze Pazse um zu warten bis die beiden Threads t_gps und 
	# t_sds01 starten konnten.
	time.sleep(3)
	t_start_sensor = Thread(target=start_sensor)
	t_start_sensor.start()
	
	# Initialisieren des Shutdown Threads.
	t_shutdown = Thread(target=shutdownpi)
	
	# Initialisieren des Reboot Threads.
	t_reboot = Thread(target=rebootpi)		
	
	# Starten des Flask Web-Servers.
	app.run(host='0.0.0.0', port=8181, debug=False)

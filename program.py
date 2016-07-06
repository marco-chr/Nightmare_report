__author__ = 'marco soldavini'
# Main module of nightmare reports
# This module reads settings, establish OPC connection, reads variable from the embedded systems and performs query to store the data
# It keeps tracks of communication via a watchdog tag

# Libs
import xml.etree.ElementTree as ET
import OpenOPC
import time
import numpy
import msvcrt
import psycopg2
import datetime
import os
import glob
import csv
import sys

# Custom components
import csvgen
import ftptransfer
import csvreader
import read_settings

# Custom defs
def read_variables_from_csv():
  with open('config.csv', 'rb') as csvfile:
    r = csv.reader(csvfile)
    for row in r:
      var_name = row[0]
      var_type = row[1]
      var_itemid = row[2]

      if not var_type in ['bool', 'float','string']:
        raise Exception("Invalid datatype {} for variable {}".format(var_type, var_name))

      variables[var_name] = {'itemid': var_itemid, 'name': var_name, 'type': var_type}
    print "Symbolic file parsed"

# Start
print "Nightmare reports started..."
# Settings XML File Parsing and OPC var list
variables = {}
read_variables_from_csv()
read_settings.read_config()
print "Press ESC to exit"

# OPC connection
opc = OpenOPC.client()
try:
    opc.connect(read_settings.Config_OPCServer[0])
    print "Data connection to OPC server completed"
except:
    print "Data connection to OPC server failed"
    sys.exit()

# Time reference for scan interval
time1 = time.time()

# setting status variables
abort = 0
watch_timer = time.time()
watchdog_value = False
comm_alarm = False
rec_started = False
records = 0

# db connection

conn = psycopg2.connect(read_settings.Config_DbConnectionString[0])
cur = conn.cursor()
print "Data connection to database completed"

# While loop - scanning and storing OPC values at scan rate
while (abort == 0):

    # ESC pressed?
    if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:
        abort = 1
        break

    # Server up
    if opc.ping():
        # Watchdog
        if (opc[read_settings.Config_WatchdogTag[0]] == None):
            if (watch_timer - time.time() > read_settings.Config_Watchdog_Delay):
                print "Watchdog Alarm"
                comm_alarm = True
        else:
            watch_timer = time.time()
            comm_alarm = False

        if opc[read_settings.Config_TestTag[0]] == True and rec_started == False:

             # Setting arrays for variables
            arrays = {}
            for var_name in variables:
              arrays[var_name] = []

            rec_started = True
            # Init batch variables

            batch_id = opc.read(read_settings.Config_BatchTag[0])[0]
            product_id = opc.read(read_settings.Config_ProductTag[0])[0]
            start_time = datetime.datetime.now()
            # Create test CSV files
            csvgen.csvgenerator()


        if opc[read_settings.Config_TestTag[0]] == True and rec_started == True:
            # scan time
            time2 = time.time()
            dtime = time2 - time1

            # PARAMETER DTIME = SCAN TIME
            if dtime > int(read_settings.Config_SampleTime[0]) and comm_alarm == False:
                dt = datetime.datetime.now()

                for var_name in variables:
                  opc_field = '.' + var_name
                  arrays[var_name].append((opc.read(opc_field)[0],opc.read(opc_field)[1],dt))


                time1 = time2
                print "BATCH " + batch_id + ":No. of values acquired in the current session: " + str(records)
                records = records + 1

        if opc[read_settings.Config_TestTag[0]] == False and rec_started == True:
            # store sql
            end_time = datetime.datetime.now()
            query =  "INSERT INTO batchdb (batchid, materialid, starttime, endtime) VALUES (%s, %s, %s, %s);"
            data = [batch_id,product_id,start_time,end_time]
            cur.execute(query, data)
            print "Closed BATCH " + batch_id

            # Write arrays data to the database
            for var_name in variables:
              variable = variables[var_name] # {'itemid', 'name', 'type'}

              if variable['type'] == "bool":

                query = "INSERT INTO itemsvaluedb (itemid, strvalue, quality, timeloc) VALUES (%s, %s, %s, %s);"
                for data in arrays[var_name]:
                  sql_data = (variable['itemid'],) + data
                  cur.execute(query, sql_data)

              elif variable['type'] == "float":

                query =  "INSERT INTO itemsvaluedb (itemid, numvalue, quality, timeloc) VALUES (%s, %s, %s, %s);"
                for data in arrays[var_name]:
                  sql_data = (variable['itemid'],) + data
                  cur.execute(query, sql_data)

              else:
                raise Exception("Invalid type {} for variable {}".format(variable['type'], variable['var_name']))

            conn.commit()
            print "BATCH " + batch_id + ":Monitored Variables Database Data Commit Executed"

            # FTPHOST, FTPUSER, FTPPASS, LOCALDIR, REMOTDIR
            ftptransfer.ftptransfer(read_settings.Config_FTPHostname[0],read_settings.Config_FTPUserId[0],read_settings.Config_FTPPassword[0],read_settings.Config_RemoteDir[0][0],read_settings.Config_LocalDir[0][0],True)
            print "BATCH " + batch_id + ":CSV File transferred from machine"
            # FILEMASK FOR AUDIT AND ALARMS CSV FILES
            alarmfile = max(glob.iglob(read_settings.Config_FileMask[0][0] + '*.csv'), key=os.path.getctime)
            auditfile = max(glob.iglob(read_settings.Config_FileMask[0][1] + '*.csv'), key=os.path.getctime)
            print "BATCH " + batch_id + ":CSV File parsing started"

            # SQL QUERY FOR AUDIT TRAIL AND ALARMS
            csvreader.csvparser(alarmfile,read_settings.Config_SQLStatement[0][0],cur,conn)
            print "BATCH " + batch_id + ":Alarms Database Data Commit Executed"
            csvreader.csvparser(auditfile,read_settings.Config_SQLStatement[0][1],cur,conn)
            print "BATCH " + batch_id + ":Audit Trail Database Data Commit Executed"
            rec_started = False
            try:
                os.system("python reportgen.py " + batch_id)
            except:
                print("PDF Report for batch " + batch_id + " failed")

    else:
        # scan time
        time2 = time.time()
        dtime = time2 - time1
        if dtime > 5:
            print "ERROR: OPC Server is down"
            time1=time2

# Closing OPC connection
opc.close()
# Closing db connection
conn.close()
print "Database and OPC Connection closed"
print "Quitting..."




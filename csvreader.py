__author__ = 'marco'
import csv
import psycopg2
import read_settings

def csvparser(filename,query,cursor,connection):

    csvfile = csv.reader(open(filename,'rb'),delimiter=',',quotechar='|')
    firstline = True
    for row in csvfile:
        if firstline:
            firstline = False
            continue
        else:
            data=[]
            for i in range(0,len(row)):
                data.append(row[i].rstrip())
            cursor.execute(query,data)
            connection.commit()


__author__ = 'marco'
# Fake CSV Generator for Audit Trail and Alarms
import datetime
import csv

def csvgenerator():
    now = datetime.datetime.now()+datetime.timedelta(seconds=1)
    csvname1='C:\\ftproot\\audit_' + now.strftime('%Y%m%d%H%M%S') + '.csv'
    csvfile = csv.writer(open(csvname1,'wb'),delimiter=',',escapechar=' ', quoting=csv.QUOTE_NONE)
    csvfile.writerow(['MachineId,TimeStamp,UserId,ObjectId,Description,Comment,NewValue,OldValue'])

    for i in range(0,10):
        rowstr = '01,' + now.strftime('%Y-%m-%d %H:%M:%S') + ',oper1,3,event,comment,1,0'
        csvfile.writerow([rowstr])

    csvname2='C:\\ftproot\\alarms_' + now.strftime('%Y%m%d%H%M%S') + '.csv'
    csvfile = csv.writer(open(csvname2,'wb'),delimiter=',',escapechar=' ', quoting=csv.QUOTE_NONE)
    csvfile.writerow(['TimeString,Comment,Value,State,Operator,MsgNumber,MachineId'])
    for i in range(0,20):
        rowstr = now.strftime('%Y-%m-%d %H:%M:%S') + ',comment,1,ACK,oper,43,01'
        csvfile.writerow([rowstr])
    return 0


__author__ = 'marco'

def ftptransfer(host,ftpuser,ftppass,remotePath,localPath,onlyDiff=False):

    global transferList
    import ftplib
    import os
    from sets import Set

    ftp = ftplib.FTP(host)
    ftp.login(user=ftpuser,passwd=ftppass)
    files = []

    if onlyDiff:
			lFileSet = Set(os.listdir(localPath))
			rFileSet = Set(ftp.nlst())
			transferList = list(rFileSet - lFileSet)
			print "CSV Files Missing: " + str(len(transferList))
    else:
            transferList = ftp.nlst()
    delMsg = ""
    filesMoved = 0

    for fl in transferList:
        localFile = localPath + fl
        grabFile = True
        if grabFile:
            fileObj = open(localFile,'wb')
            ftp.retrbinary("RETR " + fl,fileObj.write)
            fileObj.close()
            filesMoved += 1
    print "CSV Files Moved: " + str(filesMoved) + " on " + timeStamp()

    ftp.close()
    ftp = None

def timeStamp():
    import time
    return str(time.strftime("%a %d %b %Y %I:%M:%S %p"))

__author__ = 'marco soldavini'
import xml.etree.ElementTree as ET

def read_config():

    # Declarations of variables
    global stations
    global totalgroups
    global Config_OPCServer
    global Config_StationId
    global Config_DbConnectionString
    global Config_ConnectionURL
    global Config_Watchdog_Delay
    global Config_SampleTime
    global Config_FTPHostname
    global Config_FTPUserId
    global Config_FTPPassword
    global Config_FTPTimeout
    global Config_TestTag
    global Config_BatchTag
    global Config_ProductTag
    global Config_WatchdogTag
    global Config_RemoteDir
    global Config_LocalDir
    global Config_FileMask
    global Config_SQLStatement

    stations = 0
    totalgroups = 0
    Config_OPCServer=[]
    Config_StationId=[]
    Config_DbConnectionString=[]
    Config_ConnectionURL=[]
    Config_Watchdog_Delay=[]
    Config_SampleTime=[]
    Config_FTPHostname=[]
    Config_FTPUserId=[]
    Config_FTPPassword=[]
    Config_FTPTimeout=[]
    Config_TestTag=[]
    Config_BatchTag=[]
    Config_ProductTag=[]
    Config_WatchdogTag=[]
    Config_RemoteDir=[]
    Config_LocalDir=[]
    Config_FileMask=[]
    Config_SQLStatement=[]

    tree = ET.parse('settings.xml')
    root = tree.getroot()
    for StationId in root.iter('StationId'):
        stations = stations + 1
    print "Found ",stations, " stations configured in settings file"

    for StationId in root.iter('StationId'):
        Config_StationId.append(StationId.text)
    for OPCServer in root.iter('OPCServer'):
        Config_OPCServer.append(OPCServer.text)
    for DbConnectionString in root.iter('DbConnectionString'):
        Config_DbConnectionString.append(DbConnectionString.text)
    for ConnectionURL in root.iter('ConnectionURL'):
        Config_ConnectionURL.append(ConnectionURL.text)
    for Watchdog_Delay in root.iter('Watchdog_Delay'):
        Config_Watchdog_Delay.append(Watchdog_Delay.text)
    for SampleTime in root.iter('SampleTime'):
        Config_SampleTime.append(SampleTime.text)
    for FTPHostname in root.iter('FTPHostname'):
        Config_FTPHostname.append(FTPHostname.text)
    for FTPUserId in root.iter('FTPUserId'):
        Config_FTPUserId.append(FTPUserId.text)
    for FTPPassword in root.iter('FTPPassword'):
        Config_FTPPassword.append(FTPPassword.text)
    for FTPTimeout in root.iter('FTPTimeout'):
        Config_FTPTimeout.append(FTPTimeout.text)
    for TestTag in root.iter('TestTag'):
        Config_TestTag.append(TestTag.text)
    for BatchTag in root.iter('BatchTag'):
        Config_BatchTag.append(BatchTag.text)
    for ProductTag in root.iter('ProductTag'):
        Config_ProductTag.append(ProductTag.text)
    for WatchdogTag in root.iter('WatchdogTag'):
        Config_WatchdogTag.append(WatchdogTag.text)

    for FileGroups in root.iter('FileGroup'):
        totalgroups = totalgroups + 1
        n_groups = totalgroups / stations           # number of file groups to be retrieved from remote machine

    for i in range(0,stations):
        Config_RemoteDir.append([])
        Config_LocalDir.append([])
        Config_FileMask.append([])
        Config_SQLStatement.append([])
        for j in range(0,n_groups):
            Config_RemoteDir[i].append(root[0][i][14][j][0].text)
            Config_LocalDir[i].append(root[0][i][14][j][1].text)
            Config_FileMask[i].append(root[0][i][14][j][2].text)
            Config_SQLStatement[i].append(root[0][i][14][j][3].text)

    print "Settings File Parsed"

    return stations
    return totalgroups
    return Config_OPCServer
    return Config_DbConnectionString
    return Config_TestTag
    return Config_BatchTag
    return Config_ProductTag
    return Config_WatchdogTag
    return Config_Watchdog_Delay
    return Config_SampleTime
    return Config_FTPHostname, Config_FTPPassword, Config_FTPUserId
    return Config_FileMask
    return Config_LocalDir
    return Config_RemoteDir
    return Config_SQLStatement

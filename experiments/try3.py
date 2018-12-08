
import sys

dataPath = '../data'
databaseName = 'datacollection.db'
base_url = None

argcnt = 0
while argcnt < len(sys.argv):
    arg = sys.argv[argcnt]
    if arg == '--dataPath':
        argcnt += 1
        dataPath = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--databaseName':
        argcnt += 1
        databaseName = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--baseUrl':
        argcnt += 1
        base_url = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    argcnt += 1

if (dataPath is None or \
    databaseName is None or \
    base_url is None):
    print ("%s --dataPath <dataPath> --databaseName <databaseName> --baseUrl <base_url>" % sys.argv[0])
    print ("-----------------------------------------------------------------------------------------------------")
    print ("dataPath         Path where the database resides (default: ../data)")
    print ("databaseName     Filename of the sqlite database where the data is collected to (default: ../datacolletion.db)")
    print ("baseUrl          URL where to start crawling (mandator)")
    exit

print ("dataPath:     %s" % dataPath)
print ("databaseName: %s" % databaseName)
print ("base_url:     %s" % base_url)

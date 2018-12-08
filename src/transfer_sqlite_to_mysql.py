import mysql_decl
import sqlite_decl
import sqlalchemy
from sqlite_decl import Base, RawDataUrl, RawDataArticle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import sys

dataPath = '../data'
sqliteDbName = 'datacollection.db'
mysqlDbName = 'mediaharvest'
mysqlUserName = 'mediaharvest'
mysqlHost = 'localhost'
mysqlPassword = None
siteName = None

argcnt = 0
while argcnt < len(sys.argv):
    arg = sys.argv[argcnt]
    if arg == '--dataPath':
        argcnt += 1
        dataPath = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--sqliteDbName':
        argcnt += 1
        sqliteDbName = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--mysqlDbName':
        argcnt += 1
        mysqlDbName = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--mysqlUserName':
        argcnt += 1
        mysqlUserName = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--mysqlPassword':
        argcnt += 1
        mysqlPassword = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--mysqlHost':
        argcnt += 1
        mysqlHost = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--siteName':
        argcnt += 1
        siteName = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    argcnt += 1

if (dataPath is None or \
    sqliteDbName is None or \
    siteName is None or \
    mysqlDbName is None or \
    mysqlUserName is None or \
    mysqlPassword is None or \
    mysqlHost is None):
    print ("%s --dataPath <dataPath> --sqliteDbName <databaseName> --mysqlDbName <mysqlDbName> --siteName <siteName>" % sys.argv[0])
    print ("-----------------------------------------------------------------------------------------------------")
    print ("dataPath         Path where the database resides (default: ../data)")
    print ("sqliteDbName     Filename of the sqlite database where the data is collected to (default: ../datacolletion.db)")
    print ("mysqlDbName      DB-name in mysql where the data shall get to (default: mediaharvest)")
    print ("mysqlUserName    Username to connect with mysql database (default: mediaharvest)")
    print ("mysqlPassword    Password to connect with mysql database")
    print ("mysqlHost        Host to connect to mysql database (default: localhost)")
    print ("siteName         Name of the site crawled")
    exit

print ("%s --dataPath %s --sqliteDbName %s --mysqlDbName %s --mysqlUserName %s --mysqlPassword %s --mysqlHost %s --siteName %s" % (sys.argv[0], dataPath, sqliteDbName, mysqlDbName, mysqlUserName, mysqlPassword, mysqlHost, siteName))
print ("-----------------------------------------------------------------------------------------------------")

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

sqlite_engine = create_engine('sqlite:///%s/%s' % (dataPath, sqliteDbName))
sqlite_decl.Base.metadata.bind = sqlite_engine
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite = SqliteSession()

mysql_engine = create_engine('mysql+pymysql://%s:%s@%s/%s' % (mysqlUserName, mysqlPassword, mysqlHost, mysqlDbName))
mysql_decl.Base.metadata.bind = mysql_engine
MysqlSession = sessionmaker(bind=mysql_engine)
mysql = MysqlSession()

# find or create site
media_site = mysql.query(mysql_decl.MediaSite).filter(mysql_decl.MediaSite.name == siteName).first()
if media_site is None:
    media_site = mysql_decl.MediaSite(id = mysql_decl.MediaSite.getMaxId(mysql) + 1, name = siteName)
    mysql.add(media_site)
    mysql.commit()

for url in sqlite.query(sqlite_decl.RawDataUrl).all():
    print(url)
    raw_data_url = decl.RawDataUrl()
    raw_data_url.mediaSite = media_site
    raw_data_url.url = url.url
    raw_data_url.id = url.id
    mysql.add(raw_data_url)
    mysql.commit()

"""

for article in sqlite.query(sqlite_decl.RawDataArticle).all():
    # store file into filesystem
    filename = '../data/files/%s/%s.zip' % (article.downloadTimestamp.date().isoformat(), article.id)
    ensure_dir(filename)
    file = open(filename, 'wb')
    file.write(article.content)
    file.close()
    # store dataset into database
    raw_data_article = decl.RawDataArticle()
    raw_data_article.id = article.id
    raw_data_article.rawDataUrl_id = article.rawDataUrl_id
    raw_data_article.path = filename
    raw_data_article.downloadTimestamp = article.downloadTimestamp
    mysql.add(raw_data_article)
    mysql.commit()
"""

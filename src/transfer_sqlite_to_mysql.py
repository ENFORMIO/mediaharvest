import mysql_decl
import sqlite_decl
import sqlalchemy
import sqlite_decl
from sqlite_decl import Base, RawDataUrl, RawDataArticle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from datetime import timedelta

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
    exit()

print ("%s --dataPath %s --sqliteDbName %s --mysqlDbName %s --mysqlUserName %s --mysqlPassword %s --mysqlHost %s --siteName %s" % (sys.argv[0], dataPath, sqliteDbName, mysqlDbName, mysqlUserName, mysqlPassword, mysqlHost, siteName))
print ("-----------------------------------------------------------------------------------------------------")

starttime = datetime.utcnow()

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

sourceEngine = 'sqlite:///%s/%s' % (dataPath, sqliteDbName)
print ("source engine:         %s " % sourceEngine)
sqlite_engine = create_engine(sourceEngine)
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

urlIdsByUrl = {}
cntSourceUrls = 0
cntAddedUrls = 0
cntSourceArticles = 0
cntAddedArticles = 0

for sqlite_url in sqlite.query(sqlite_decl.RawDataUrl).all():
    cntSourceUrls += 1
    raw_data_url = mysql.query(mysql_decl.RawDataUrl).filter(and_(mysql_decl.RawDataUrl.url == sqlite_url.url, mysql_decl.RawDataUrl.mediaSite == media_site)).first()
    if raw_data_url is None:
        raw_data_url = mysql_decl.RawDataUrl()
        raw_data_url.mediaSite = media_site
        raw_data_url.url = sqlite_url.url
        raw_data_url.id = mysql_decl.RawDataUrl.getMaxId(mysql) + 1
        mysql.add(raw_data_url)
        mysql.commit()
        cntAddedUrls += 1
    urlIdsByUrl[sqlite_url.url] = raw_data_url.id


for article in sqlite.query(sqlite_decl.RawDataArticle).all():
    cntSourceArticles += 1
    raw_data_url_id = urlIdsByUrl[article.rawDataUrl.url]
    filename = '../data/files/%s/%s-%s.zip' % (article.downloadTimestamp.date().isoformat(), media_site.name, article.id)

    raw_data_article = mysql.query(mysql_decl.RawDataArticle)\
                            .filter(mysql_decl.RawDataArticle.rawDataUrl_id == raw_data_url_id)\
                            .filter(mysql_decl.RawDataArticle.downloadTimestamp > article.downloadTimestamp + timedelta(seconds=-1))\
                            .filter(mysql_decl.RawDataArticle.downloadTimestamp <= article.downloadTimestamp + timedelta(seconds=1))\
                            .first()

    if raw_data_article is None:
        raw_data_article = mysql_decl.RawDataArticle()
        raw_data_article.id = mysql_decl.RawDataArticle.getMaxId(mysql) + 1
        raw_data_article.rawDataUrl_id = raw_data_url_id
        raw_data_article.downloadTimestamp = article.downloadTimestamp
        raw_data_article.path = filename
        mysql.add(raw_data_article)
        mysql.commit()
        cntAddedArticles += 1

    # store file into filesystem
    ensure_dir(filename)
    file = open(filename, 'wb')
    file.write(article.content)
    file.close()

print ("source engine:         %s " % sourceEngine)
print ("source urls:           %s " % cntSourceUrls)
print ("added urls:            %s " % cntAddedUrls)
print ("source articles:       %s " % cntSourceArticles)
print ("added articles:        %s " % cntAddedArticles)

endtime = datetime.utcnow()

print ("runtime:         %s" % str(endtime - starttime))

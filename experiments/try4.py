#!/usr/bin/python
import grequests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlite_decl import Base, RawDataUrl, RawDataArticle
import zip
import os
import sys

try:
    from urllib.parse import urljoin
except ImportError:
     from urlparse import urljoin

dataPath = '../data'
databaseName = 'test.db'
base_url = None
urls_file = None

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
    if arg == '--urls_file':
        argcnt += 1
        urls_file = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    argcnt += 1

if (dataPath is None or \
    databaseName is None):
    print ("%s --dataPath <dataPath> --databaseName <databaseName> --baseUrl <base_url>" % sys.argv[0])
    print ("-----------------------------------------------------------------------------------------------------")
    print ("dataPath         Path where the database resides (default: ../data)")
    print ("databaseName     Filename of the sqlite database where the data is collected to (default: ../datacolletion.db)")
    exit

print ("%s --dataPath %s --databaseName %s" % (sys.argv[0], dataPath, databaseName))
print ("-----------------------------------------------------------------------------------------------------")

databasePath = '%s/%s' % (dataPath, databaseName)
engine = create_engine('sqlite:///%s' % databasePath)

if not os.path.isfile(databasePath):
    Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def store_url(url, content):
    global session
    print("attempt to find url: %s" % url)
    raw_data_url = session.query(RawDataUrl).filter(RawDataUrl.url == url).first()
    if raw_data_url is None:
        print ("adding url to raw_data_url: %s" % url)
        raw_data_url = RawDataUrl(id = RawDataUrl.getMaxId(session) + 1, url=url)
        session.add(raw_data_url)
        session.commit()
        print ("added url to raw_data_url: %s" % url)

    print ("raw_data_url %s" % str(raw_data_url))

    zipped = zip.zipped(content, 'article.html')
    raw_data_article = RawDataArticle(id = RawDataArticle.getMaxId(session) + 1, content = zipped, rawDataUrl = raw_data_url)
    raw_data_article.content = zipped
    session.add(raw_data_article)
    session.commit()

store_url('www.test.at', '<html><head><title>abc</title></head><body><h1>test</h1></body></html>')

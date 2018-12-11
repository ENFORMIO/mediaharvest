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
databaseName = 'datacollection.db'
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
    databaseName is None or \
    (base_url is None and urls_file is None)):
    print ("%s --dataPath <dataPath> --databaseName <databaseName> --baseUrl <base_url>" % sys.argv[0])
    print ("-----------------------------------------------------------------------------------------------------")
    print ("dataPath         Path where the database resides (default: ../data)")
    print ("databaseName     Filename of the sqlite database where the data is collected to (default: ../datacolletion.db)")
    print ("baseUrl          URL where to start crawling (mandator)")
    print ("urls_file        Filename of a file which holds urls to be loaded")
    exit

print ("%s --dataPath %s --databaseName %s --baseUrl %s" % (sys.argv[0], dataPath, databaseName, base_url))
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
    #print("attempt to find url: %s" % url)
    raw_data_url = session.query(RawDataUrl).filter(RawDataUrl.url == url).first()
    if raw_data_url is None:
        #print ("adding url to raw_data_url: %s" % url)
        raw_data_url = RawDataUrl(id = RawDataUrl.getMaxId(session) + 1, url=url)
        session.add(raw_data_url)
        session.commit()
        #print ("added url to raw_data_url: %s" % url)

    #print ("raw_data_url %s" % str(raw_data_url))

    zipped = zip.zipped(content, 'article.html')
    raw_data_article = RawDataArticle(id = RawDataArticle.getMaxId(session) + 1, content = zipped, rawDataUrl = raw_data_url)
    raw_data_article.content = zipped
    session.add(raw_data_article)
    session.commit()

def get_urls_from_response(r):
    if r is None:
        return []
    print(r.url)
    soup = BeautifulSoup(r.text, 'html.parser')
    store_url(r.url, str(soup))
    hrefs = [link.get('href') for link in soup.find_all('a')]
    # join host and path from r.url with found a href
    hrefs = [urljoin(r.url, href) for href in hrefs]
    soup.decompose()
    return hrefs


def print_url(args):
    print (args['url'])

def exception_handler(r,e):
        print('failed: ',r.url,'\n')
        #changing the url just for doing sth
        r.url = 'http://httpbin.org/status/200'
        res = r.send().response
        return res

def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in xrange(0, len(l), n))

def iterative_loader(follow_hrefs):
    global loadedUrls, identifiedUrls, base_url
    urls = identifiedUrls[:100]
    identifiedUrls = identifiedUrls[100:]
    rs = [grequests.get(url) for url in urls]
    responses = grequests.map(rs, size=100)
    for response in responses:
        if not response.ok:
            print ("%s: (%s - %s) -> reenqueue" % (response.url, response.status_code, response.reason))
            identifiedUrls.append(response.url)

    loadedUrls = list(sum([loadedUrls, urls], []))
    if follow_hrefs:
        url_lists = [get_urls_from_response(response) for response in responses]
        responded_urls = list(set(sum(url_lists, [])))
        responded_urls = [url for url in responded_urls if url is not None and url.startswith(base_url)]
        responded_urls = [url for url in responded_urls if not url in loadedUrls]
        identifiedUrls = list(sum([identifiedUrls, responded_urls],[]))

    print ("----------------------------------------------------")
    print ("%s identified Urls, %s loaded urls" % (len(identifiedUrls), len(loadedUrls)))
    print ("----------------------------------------------------")

loadedUrls = []
identifiedUrls = []

if urls_file is not None:
    with open(urls_file, 'r') as f:
        line = f.readline()
        while line:
            identifiedUrls.append(line)
            line = f.readline()

if base_url is not None:
    identifiedUrls.append(base_url)

follow_hrefs = (urls_file is None)

iterative_loader(follow_hrefs)
while (len(identifiedUrls) > 0):
    iterative_loader(follow_hrefs)

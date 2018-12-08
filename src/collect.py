#!/usr/bin/python
import grequests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlite_decl import Base, RawDataUrl, RawDataArticle
import zip
import os

try:
    from urllib.parse import urljoin
except ImportError:
     from urlparse import urljoin

dataPath = '../data'
databasePath = '%s/datacollection.db' % (dataPath)
engine = create_engine('sqlite:///%s' % databasePath)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def store_url(url, content):
    global session
    raw_data_url = session.query(RawDataUrl).filter(RawDataUrl.url == url).first
    if raw_data_url is None:
        raw_data_url = RawDataUrl(id = RawDataUrl.getMaxId(session) + 1, url=url)
        session.add(raw_data_url)
        session.commit()

    zipped = zip.zipped(content, 'article.html')
    raw_data_article = RawDataArticle(id = RawDataArticle.getMaxId(session) + 1, content = zipped, rawDataUrl = None)
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
    hrefs = [urlparse.urljoin(r.url, href) for href in hrefs]
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

def iterative_loader():
    global loadedUrls, identifiedUrls, base_url
    urls = identifiedUrls[:100]
    identifiedUrls = identifiedUrls[100:]
    rs = [grequests.get(url) for url in urls]
    responses = grequests.map(rs, size=100)
    loadedUrls = list(sum([loadedUrls, urls], []))
    url_lists = [get_urls_from_response(response) for response in responses]
    responded_urls = list(set(sum(url_lists, [])))
    responded_urls = [url for url in responded_urls if url is not None and url.startswith(base_url)]
    responded_urls = [url for url in responded_urls if not url in loadedUrls]
    identifiedUrls = list(sum([identifiedUrls, responded_urls],[]))

    print ("----------------------------------------------------")
    print ("%s identified Urls, %s loaded urls" % (len(identifiedUrls), len(loadedUrls)))
    print ("----------------------------------------------------")

base_url = 'https://www.krone.at'
loadedUrls = []
identifiedUrls = [base_url]

iterative_loader()
while (len(identifiedUrls) > 0):
    iterative_loader()

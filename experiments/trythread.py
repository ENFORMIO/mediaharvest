#!/usr/bin/python3
import threading
import time
import urllib
import random
import ssl
import zip

from datetime import timedelta
from datetime import datetime

from sqlite_decl import Base, RawDataUrl, RawDataArticle, ArticleCategory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from bs4 import BeautifulSoup

engine = create_engine('sqlite:///../data/datacollection2.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

minIntervalOfArticleReload = 24 # hours

class SynchronizedCollection():
    def __init__(self):
        self._lock = threading.Lock()
        self.urls = []
    def addFirst(self, obj):
        self._lock.acquire()
        self.urls.insert(0,obj)
        self._lock.release()
    def addLast(self,obj):
        self._lock.acquire()
        self.urls.append(obj)
        self._lock.release()
    def addLastIfNotExists(self,obj):
        self._lock.acquire()
        if not obj in self.urls:
            self.urls.append(obj)
        self._lock.release()
    def contains(self, obj):
        self._lock.acquire()
        isInList = (obj in self.urls)
        self._lock.release()
        return isInList
    def count(self):
        self._lock.acquire()
        result = len(self.urls)
        self._lock.release()
        return result
    def takeFirst(self):
        self._lock.acquire()
        result = None
        if len(self.urls) > 0:
            result = self.urls.pop(0)
        self._lock.release()
        return result

class SynchronizedDictionary():
    def __init__(self):
        self._dict = {}
        self._lock = threading.Lock()
    def containsKey(self, key):
        self._lock.acquire()
        result = key in self._dict
        self._lock.release()
        return result
    def add(self, key, obj):
        self._lock.acquire()
        self._dict[key] = obj
        self._lock.release()
    def pop(self, key):
        self._lock.acquire()
        result = self._dict.pop(key, None)
        self._lock.release()
        return result
    def count(self):
        self._lock.acquire()
        result = len(self._dict)
        self._lock.release()
        return result

class myUrlLoaderThread (threading.Thread):
    def __init__(self, counter):
        threading.Thread.__init__(self)
        self.counter = counter
    def run(self):
        global urlCollection
        while 1:
            url = urlCollection.takeFirst()
            if url is None:
                print ("Thread %s: exiting" % self.counter)
                return
            #print ("Thread %s: loading %s" % (self.counter, url))
            loadSoupFromUrl(self.counter, url)


class myProgressReporterThread (threading.Thread):
    def __init__(self, counter):
        threading.Thread.__init__(self)
        self.counter = counter
    def run(self):
        global urlCollection, loadedContent
        reportProgress = True
        while reportProgress:
            cnt = urlCollection.count()
            loadedCnt = loadedContent.count()
            if cnt == 0:
                reportProgress = False
            else:
                time.sleep(1.0)
                print ("Progress: %s urls found, %s urls loaded" % (cnt, loadedCnt))

def loadSoupFromUrl(threadNo, url):
    global loadedUrls, session, loadedContent

    parsedUrl = urllib.parse.urlparse(url)
    content = None
    try:
        f = urllib.request.urlopen(url)
        content = f.read()
    except ssl.SSLEOFError as err:
        print ("SSLEOFError in Thread %s: " % err)
    except urllib.error.HTTPError as err:
        print ("HTTPError in Thread %s: " % err)

    if content is None:
        return

    loadedContent.add(url, content)

    soup = BeautifulSoup(content, 'html.parser')

    for link in soup.find_all('a'):
        href = link.get('href')
        joinedUrl = urllib.parse.urljoin(url, href)
        parsedJoinedUrl = urllib.parse.urlparse(joinedUrl)
        if parsedJoinedUrl.netloc != parsedUrl.netloc:
            continue
        #print ("queuing url %s" % str(joinedUrl))
        if loadedUrls.contains(joinedUrl):
            continue

        urlCollection.addLastIfNotExists(joinedUrl)

counter = 0
urlCollection = SynchronizedCollection()
loadedContent = SynchronizedDictionary()

loadedUrls = SynchronizedCollection()
loadSoupFromUrl(0,'http://www.krone.at')

#urlCollection.addLast('https://www.krone.at/1811898')
#urlCollection.addLast('https://www.krone.at/1811775')


#for url in session.query(RawDataUrl).all():
#    urlCollection.addLast(url.url)
#    if counter >= 200:
#        break
#    counter += 1

threads = []
thread = myProgressReporterThread(0)
thread.start()
threads.append(thread)

for counter in range(100):
    thread = myUrlLoaderThread(counter + 1)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print ("Exiting Main Thread")

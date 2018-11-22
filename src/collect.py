import sys
import urllib
import urllib.request
from bs4 import BeautifulSoup
from datetime import timedelta
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy_declarative import ArticleCategory, Base, ArticleCategoryRelationship, RawDataUrl, RawDataArticle

import zip

if len(sys.argv) < 2:
    print ("usage: python3 %s <site-url>" % sys.argv[0])
    exit(0)
base_link = sys.argv[1]

engine = create_engine('sqlite:///../data/datacollection.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

minIntervalOfArticleReload = 24 # hours

links = []
dead_links = []
news_links = []
external_links = []
max_depth = 8

def loadSoupFromUrl(url, use_cache_if_available):
    raw_data_url_cached = True
    raw_data_url = session.query(RawDataUrl).filter(RawDataUrl.url == url).first()
    if raw_data_url is None:
        raw_data_url_cached = False
        raw_data_url = RawDataUrl(id = RawDataUrl.getMaxId(session) + 1,
                                  url = url)
        session.add(raw_data_url)
        session.commit()

    soup = None
    f = None
    try:
        f = urllib.request.urlopen(url)
    except urllib.error.HTTPError as err:
        print (err)
        return None

    latestDownloadedArticle = session.query(RawDataArticle).filter(RawDataArticle.rawDataUrl == raw_data_url).order_by(RawDataArticle.downloadTimestamp.desc()).first()
    latestDownloadTimestamp =  latestDownloadedArticle.downloadTimestamp if latestDownloadedArticle is not None else None

    if latestDownloadTimestamp is None or \
       latestDownloadTimestamp + timedelta(hours=minIntervalOfArticleReload) < datetime.utcnow():
        print('downloading %s content from %s...' % ("cached" if raw_data_url_cached else 'new', url))
        soup = BeautifulSoup(f.read(), 'html.parser')
        zipped = zip.zipped(str(soup), 'article.html')
        raw_data_article = RawDataArticle(id = RawDataArticle.getMaxId(session) + 1,
                                          content = zipped,
                                          rawDataUrl = raw_data_url)
        session.add(raw_data_article)
        session.commit()
    elif use_cache_if_available:
        print ('use cached content (%s) of : %s' % (latestDownloadTimestamp, url))
        soup = BeautifulSoup(latestDownloadedArticle.content, 'html.parser')

    return soup


def browse_categories():
    global base_link
    for category in session.query(ArticleCategory).all():
        print ("-----------------------------------------------------------")
        print ("harvesting category: %s" % category.name)
        print ("-----------------------------------------------------------")
        soup = loadSoupFromUrl(category.url, True)

        if soup is None:
            continue

        article_urls = []
        cached_article_urls = []

        for link in soup.find_all('a'):

            href = link.get('href')
            if href in article_urls:
                #print ('Already loaded within this crawling attempt')
                continue
            # stay on the site
            if (href.startswith(base_link) or \
                href.startswith(base_link.replace('http:', 'https:'))):
                article_urls.append(href)
                # found an article
                #print(hrefNo)
                articleSoup = loadSoupFromUrl(href, False)


def find_categories(url):
    f = None
    try:
        f=urllib.request.urlopen(url)
    except urllib.error.HTTPError as err:
        print (err)
        return


    myfile = f.read()
    #print (myfile)

    soup = BeautifulSoup(myfile, 'html.parser')
    categoryLinks = []

    for mainnavi in soup.select('div.c_navi-navbar div.c_navbar > div.c_navi-link > div.c_inner'):
        #for mainnavilink in mainnavi.select_one()
        ressort_id = mainnavi.get('data-ressort_id')
        mainnavilink = mainnavi.select_one('a')
        mainnaviname = mainnavilink.getText().strip()
        mainnaviurl = mainnavilink.get('href')

        print ("found %s =[%s]=> %s" % (mainnavilink.getText().strip(),
                                  ressort_id,
                                  mainnavilink.get('href')))

        stmt = exists().where(ArticleCategory.url == mainnaviurl)
        mainCategory = session.query(ArticleCategory).filter(stmt).first()
        if mainCategory is None:
            print ("inserting %s" % mainnaviurl)
            mainCategory = ArticleCategory(id = ArticleCategory.getMaxId(session) + 1,
                                               name = mainnaviname,
                                               media_id = ressort_id,
                                               url = mainnaviurl)
            session.add(mainCategory)
            session.commit()
        else:
            print ("already recorded")

        for sub in mainnavi.select('> div.c_sub > div.c_navi-link > div.c_inner'):
            sub_ressort_id = sub.get('data-ressort_id')
            if (sub_ressort_id == ressort_id):
                continue
            #print (sub_ressort_id)
            sub_href = sub.select_one('a').get('href')
            sub_text = sub.select_one('a').getText().strip()

            subCategory = session.query(ArticleCategory).filter(ArticleCategory.url == sub_href).first()
            if subCategory is None:
                print ("inserting %s" % sub_href)
                subCategory = ArticleCategory(id = ArticleCategory.getMaxId(session) + 1,
                                              name = sub_text,
                                              media_id = sub_ressort_id,
                                              url = sub_href)
                session.add(subCategory)
                session.commit()

            print ('       - %s =[%s]=> %s' % (sub_text, sub_ressort_id, sub_href))

            parentRelation = session.query(ArticleCategoryRelationship).filter(
                                            ArticleCategoryRelationship.cat_from == mainCategory,
                                            ArticleCategoryRelationship.cat_to == subCategory,
                                            ArticleCategoryRelationship.type == 'parent_of'
                                           ).first()
            if parentRelation is None:
                print ('inserting relationship')
                parentRelation = ArticleCategoryRelationship(id = ArticleCategoryRelationship.getMaxId(session) + 1,
                                                             cat_from = mainCategory,
                                                             cat_to = subCategory,
                                                             type = 'parent_of')
                session.add(parentRelation)
                session.commit()
            else:
                print ('relationship already there')

def browse_link(url, depth):

    if depth > max_depth:
        return
    if (url in links):
        return
    print ('browsing depth: %s %s' % (str(depth), url))
    f = None
    try:
        f = urllib.request.urlopen(url)
    except urllib.error.HTTPError as err:
        print(err)
        dead_links.append(url)
        return

    myfile = f.read()
    #print (myfile)
    soup = BeautifulSoup(myfile, 'html.parser')

    links_to_visit = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if not href in links:
            if href is None:
                continue
            if href.startswith('mailto:'):
                continue
            if href.startswith('javascript:'):
                continue
            if href.endswith('.jpg') or href.endswith('.JPG') or \
               href.endswith('.png') or href.endswith('.PNG') or \
               href.endswith('.pdf') or href.endswith('.PDF'):
                continue

            #print ("   > adding %s " % href)
            links.append(href)
            if (href.startswith('http://') or href.startswith('https://')) \
                and not href.startswith('http://www.fireworld.at'):
                external_links.append(href)
                #print ("     external href: %s" % href)
                continue

            normalized_href = href
            if not href.startswith('http'):
                normalized_href = "%s/%s" % (base_link, href)

            if normalized_href.startswith('%s/berichte/details/news/' % base_link):
                news_links.append(normalized_href)
                continue

            links_to_visit.append(normalized_href)

    for href in links_to_visit:
        browse_link(href, depth + 1)



find_categories("http://www.krone.at")
browse_categories()

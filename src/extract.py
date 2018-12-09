from mysql_decl import Base, MediaSite, RawDataUrl, RawDataArticle, ArticleExtract
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
import zip
from sqlalchemy import desc
import sys

from extractor import Extractor
from kroneExtractor import KroneExtractor

dataPath = '../data'
mysqlDbName = 'mediaharvest'
mysqlUserName = 'mediaharvest'
mysqlHost = 'localhost'
mysqlPassword = None

argcnt = 0
while argcnt < len(sys.argv):
    arg = sys.argv[argcnt]
    if arg == '--dataPath':
        argcnt += 1
        dataPath = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--mysqlHost':
        argcnt += 1
        mysqlHost = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--mysqlDbName':
        argcnt += 1
        mysqlDbName = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--mysqlUserName':
        argcnt += 1
        mysqlUserName = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    if arg == '--mysqlPassword':
        argcnt += 1
        mysqlPassword = sys.argv[argcnt] if argcnt < len(sys.argv) else None
    argcnt += 1

if (dataPath is None or \
    mysqlHost is None or \
    mysqlDbName is None or \
    mysqlUserName is None or \
    mysqlPassword is None):
    print ("%s --dataPath <dataPath> --mysqlHost <mysqlHost> --mysqlDbName <mysqlDbName> --mysqlUserName <mysqlUserName> --mysqlPassword <mysqlPassword>" % sys.argv[0])
    print ("-----------------------------------------------------------------------------------------------------")
    print ("dataPath         Path where the database resides (default: ../data)")
    print ("mysqlDbName      DB-name in mysql where the data shall get to (default: mediaharvest)")
    print ("mysqlUserName    Username to connect with mysql database (default: mediaharvest)")
    print ("mysqlPassword    Password to connect with mysql database")
    print ("mysqlHost        Host to connect to mysql database (default: localhost)")
    exit

print ("%s --dataPath %s  --mysqlHost %s --mysqlDbName %s --mysqlUserName %s --mysqlPassword %s" % (sys.argv[0], dataPath, mysqlHost, mysqlDbName, mysqlUserName, mysqlPassword))
print ("-----------------------------------------------------------------------------------------------------")

def getExtractor(siteName, htmlContent):
    if siteName == 'krone':
        return KroneExtractor(htmlContent)
    return Extractor(htmlContent)

mysql_engine = create_engine('mysql+pymysql://%s:%s@%s/%s' % (mysqlUserName, mysqlPassword, mysqlHost, mysqlDbName))
Base.metadata.bind = mysql_engine
MysqlSession = sessionmaker(bind=mysql_engine)
mysql = MysqlSession()

for rawDataUrl in mysql.query(RawDataUrl).all():
    title = None
    author = None
    publishedDate = None
    copyrightImage = None
    facebookTitle = None
    facebookDescription = None
    teaser = None
    text = None
    commenturl = None
    topics = []
    ressorts = []
    parentRessorts = []

    rawDataArticle = mysql.query(RawDataArticle)\
                          .filter(RawDataArticle.rawDataUrl_id == rawDataUrl.id)\
                          .order_by(RawDataArticle.downloadTimestamp.desc())\
                          .first()

    mediaSite = rawDataUrl.mediaSite
    filename = rawDataArticle.path
    f = open(filename, "rb")
    unzipped = zip.unzipped(f.read())
    for name in unzipped:
        htmlContent = unzipped[name].decode('utf-8')
        extractor = getExtractor(mediaSite.name, htmlContent)

        try:
            extractor = KroneExtractor(htmlContent)
            title = extractor.getTitle()
            #topics.extend(extractor.getTopics())
            #author = extractor.getAuthor()
            #publishedDate = extractor.getPublishedDate()
            #copyrightImage = extractor.getCopyrightImage()
            #facebookTitle = extractor.getOgTitle()
            #facebookDescription = extractor.getOgDescription()
            #teaser = extractor.getTeaser()
            #text = extractor.getText()
            #ressorts.extend(extractor.getRessorts())
            #parentRessorts.extend(extractor.getMainRessorts())
        except:
            pass

    articleExtract = mysql.query(ArticleExtract).filter(ArticleExtract.rawDataArticle_id == rawDataArticle.id).first()
    if articleExtract is None:
        articleExtract = ArticleExtract(id = ArticleExtract.getMaxId(mysql) + 1, \
                                        rawDataArticle = rawDataArticle, \
                                        rawDataUrl = rawDataUrl)
        mysql.add(articleExtract)

    articleExtract.title = title
    mysql.commit()

    print ('"%s"|"%s"|"%s"|"%s"|"%s"|"%s"|"%s"' % (rawDataUrl.url,
                         title,
                         author,
                         publishedDate,
                         str(topics),
                         str(ressorts),
                         str(parentRessorts)
                         ))


"""
    Auswertung 1:
        jeweils erster Datensatz:
            * Url
            * title
            * authorline
            * publishedDate
            * commentAnzahl
            * Aehnliche Themen
            * Kategorie inkl. Haupt- und Nebenkategorie




engine = create_engine('sqlite:///../data/datacollection.old.db')
Base.metadata.bind = engine

from sqlalchemy.orm import sessionmaker

DBSession = sessionmaker()
session = DBSession()

counter = 0

urls = session.query(RawDataUrl).all()
for url in urls:
    counter = 0

    title = None
    author = None
    publishedDate = None
    copyrightImage = None
    facebookTitle = None
    facebookDescription = None
    teaser = None
    text = None
    commenturl = None
    topics = []
    ressorts = []
    parentRessorts = []

    articles = session.query(RawDataArticle).filter(RawDataArticle.rawDataUrl == url).all()
    for article in articles:
        unzipped = zip.unzipped(article.content)
        for name in unzipped:
            htmlContent = unzipped[name].decode('utf-8')

            try:
                extractor = KroneExtractor(htmlContent)
                title = extractor.getTitle()
                topics.extend(extractor.getTopics())
                author = extractor.getAuthor()
                publishedDate = extractor.getPublishedDate()
                copyrightImage = extractor.getCopyrightImage()
                facebookTitle = extractor.getOgTitle()
                facebookDescription = extractor.getOgDescription()
                teaser = extractor.getTeaser()
                text = extractor.getText()
                ressorts.extend(extractor.getRessorts())
                parentRessorts.extend(extractor.getMainRessorts())
            except:
                pass
    print ('"%s"|"%s"|"%s"|"%s"|"%s"|"%s"|"%s"' % (url.url,
                         title,
                         author,
                         publishedDate,
                         str(topics),
                         str(ressorts),
                         str(parentRessorts)
                         ))
"""

from mysql_decl import Base, MediaSite, RawDataUrl, RawDataArticle, ArticleExtract
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
import zip
from sqlalchemy import desc
import sys

from extractor import Extractor
from kroneExtractor import KroneExtractor

extractionVersion = 1

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

rawDataUrls = mysql.query(RawDataUrl).all()
cntAlreadyExtractedArticles = 0
cntHerewithExtractedArticles = 0
cntRawDataUrlsProcessed = 0
cntRawDataUrls = len(rawDataUrls)

print ("rawDataUrl count:     %s" % cntRawDataUrls )

for rawDataUrl in rawDataUrls:
    cntRawDataUrlsProcessed += 1
    if (cntRawDataUrls % 10 == 0):
        print ("%3d %%: %s of %s urls processed" % (cntRawDataUrlsProcessed / cntRawDataUrls * 100, cntRawDataUrlsProcessed, cntRawDataUrls))

    title = author = publishedDate = copyrightImage = None
    ogTitle = ogDescription = None
    teaser = text = None
    topics = ressorts = parentRessorts = []

    rawDataArticle = mysql.query(RawDataArticle)\
                          .filter(RawDataArticle.rawDataUrl_id == rawDataUrl.id)\
                          .order_by(RawDataArticle.downloadTimestamp.desc())\
                          .first()

    if rawDataArticle is None:
        continue

    mediaSite = rawDataUrl.mediaSite

    if rawDataArticle.path is None:
        continue

    filename = rawDataArticle.path
    f = open(filename, "rb")
    unzipped = zip.unzipped(f.read())
    for name in unzipped:
        htmlContent = unzipped[name].decode('utf-8')
        extractor = getExtractor(mediaSite.name, htmlContent)

        try:
            extractor = KroneExtractor(htmlContent)
            title = extractor.getTitle()
            topics.extend(extractor.getTopics())
            author = extractor.getAuthor()
            #publishedDate = extractor.getPublishedDate()
            #copyrightImage = extractor.getCopyrightImage()
            ogTitle = extractor.getOgTitle()
            ogDescription = extractor.getOgDescription()
            teaser = extractor.getTeaser()
            text = extractor.getText()
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

    if articleExtract.version >= extractionVersion:
        continue

    try:
        articleExtract.version = extractionVersion
        articleExtract.title = title
        articleExtract.author = author
        articleExtract.ogTitle = ogTitle
        articleExtract.ogDescription = ogDescription
        articleExtract.teaser = teaser
        articleExtract.text = text
        articleExtract.topics =  str(topics)
        mysql.commit()
    except:
        mysql.rollback()
        continue

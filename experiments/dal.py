import sqlite_decl as decl

class RawDataUrl:
    def __init__(self, session, url):
        self._declarative = decl.RawDataUrl(id = None, url = url)
        self._session = session

    def getUrl():
        return self._declarative.url
    def getId():
        return self._declarative.id

    def findAll(self):
        result = []
        for url in self._session.query(decl.RawDataUrl).all():
            result.append(RawDataUrl(

    def insert():
        session.add(self)
        session.commit()

    def getRawDataArticles():
        return session.query(decl.RawDataArticle).filter(rawDataUrl == self._declarative)

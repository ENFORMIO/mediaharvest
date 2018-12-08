
class Extractor(object):
    def __init__(self, content):
        self._content = content

    def getTitle(self):
        return None

    def getTopics(self):
        return []

    def getAuthor(self):
        return None

    def getPublishedDate(self):
        return None

    def getCopyrightImage(self):
        return None

    def getOgTitle(self):
        return None

    def getOgDescription(self):
        return None

    def getTeaser(self):
        return None

    def getText(self):
        return None

    def getRessorts(self):
        return []

    def getMainRessorts(self):
        return []

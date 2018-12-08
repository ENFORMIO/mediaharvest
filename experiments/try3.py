import urllib
import urllib.parse


href = "/sport/eishockey/"
base_url = "https://www.heute.at"


parsedBaseUrl = urllib.parse.urlparse(base_url)
joinedUrl = urllib.parse.urljoin(base_url, href)
parsedJoinedUrl = urllib.parse.urlparse(joinedUrl)

print (joinedUrl)

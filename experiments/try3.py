try:
    from urllib.parse import urljoin
except ImportError:
     from urlparse import urljoin

href = "/sport/eishockey/"
base_url = "https://www.heute.at"

joinedUrl = urljoin(base_url, href)

print (joinedUrl)

import grequests
from bs4 import BeautifulSoup


def get_urls_from_response(r):
    soup = BeautifulSoup(r.text)
    urls = [link.get('href') for link in soup.find_all('a')]
    return urls


def print_url(args):
    print args['url']


def recursive_urls(urls):
    """
    Given a list of starting urls, recursively finds all descendant urls
    recursively
    """
    if len(urls) == 0:
        return
    rs = [grequests.get(url, hooks=dict(args=print_url)) for url in urls]
    responses = grequests.map(rs)
    url_lists = [get_urls_from_response(response) for response in responses]
    urls = sum(url_lists, [])  # flatten list of lists into a list
    recursive_urls(urls)

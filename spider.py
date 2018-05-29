#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import requests
import bs4

SELENIUM = True
try:
    import selenium.webdriver
    from selenium.common.exceptions import TimeoutException as WebTimeoutException
except ImportError:
    SELENIUM = False

# store all the visited websites
pool = set()

# the search depth of the first search
DEPTH = 2


class URL:

    """
    URL: URL string wrapper
    """
    def __init__(self, url):
# the raw url string
        self.raw = url
# accept http or https
# strip the tailing backslash
        m = re.match(r"(?:http://|https://|//)?(.+)/?", url)

        self.valid = m is not None
        if self.valid:
# fetch the host part
            self.name = m.group(1)
        else:
            self.name = None

    def http(self):
        return r"http://" + self.name

    def https(self):
        return r"https://" + self.name

    def request_string(self):
        return [self.https(), self.http()]


def record(url, text):
    # write the result into a file
    # '^' is accepted in both windows and linux filenames, but not in URI
    with os.open(url.replace('/','^'), os.O_CREAT | os.O_RDWR) as f:
        os.write(f, text)
        os.close(f)


class Node:
    """
    Node: a website in the deep-first traverse of the websites
    """
    def __init__(self, url, depth = 0):
        if depth == 0:
            pool.clear()
        self.url = url
# depth is the depth of the current node in the search
        self.depth = depth

    def visit(self, max_depth = DEPTH, response_handler=record, html_rendering=False):
        """Recurse the webpage, and send the url, along with the webpage, to the handler
            max_depth: int, 
            response_handler: function(url:str, text:str), called when the response is valid
        """
        if self.depth >= max_depth:
            return
        if self.url.name in pool:
            return
        else:
            pool.add(self.url.name)
        
        print(f"Requesting {self.url.name}...")

        if html_rendering:
            browser = selenium.webdriver.Firefox()
        
# host for relative href
        try:
            host = re.search(r"(?:(?:https?:)?//)?([^/]+)", self.url.name).group(1)
        except Exception:
            host = None

# indicate if the request is successful
        flag = False
        site = ''

        for req in self.url.request_string():
            if html_rendering:
                # render webpage
                browser.set_page_load_timeout(10)
                browser.set_script_timeout(5)
                try:
                    browser.get(req)
                except WebTimeoutException:
                    pass
                html = browser.execute_script("return new XMLSerializer().serializeToString(document)")
                browser.stop_client()
                site = bs4.BeautifulSoup(html, 'html5lib')
            else:
                try:
                    # print(f"Site: {req}")
                    r = requests.get(req, timeout = 3)
                    if r.status_code != 200:
                        print("Warning: HTTP response for {req} is {r.status_code} but 200")
                    else:
                        # print("OK")
                        flag = True
                        site = bs4.BeautifulSoup(r.content, 'html5lib')
                        break
                except requests.exceptions.Timeout:
                    # print(f"Request time out : {req}")
                    pass
                except Exception:
                    # print(f"Failed to connect : {req}")
                    pass
        print("Done")

        if not flag:
            return

        urls = []

        # handle the response
        if html_rendering:
            response_handler(self.url.name, html)
        else:
            response_handler(self.url.name, r.content.decode(encoding='utf-8'))

        # find successors
        for tag in site.find_all('a'):
            urls.append(tag.get("href"))
        
        for url in urls:
            if url is None or not len(url):
                continue
            # add host if started with a slash
            if url[0] == '/':
                url = host + url
            url = url.rstrip('/')

            # print("Link to", url)
            searchTask = URL(url)
            if not searchTask.valid:
                # print(f"Invalid URL: {url}")
                continue
            else:
                # if the website has been visited
                if searchTask.name in pool:
                    continue
                else:
                    Node(searchTask, self.depth + 1).visit(max_depth, response_handler)

def search(url, depth, handler, html_rendering=False):
    """Recurse the webpage, and send the url, along with the webpage, to the handler
            depth: int, the maximum depth of the search
            handler: function(url:str, text:str), called when the response is valid
    """
    if html_rendering and not SELENIUM:
        print("Selenium package not found, do not render")
        html_rendering = False
        
    searchTask = URL(url)
    if not searchTask.valid:
        print(f"Invalid url {url}")
        sys.exit(1)

    n = Node(searchTask)
    n.visit(depth, handler, html_rendering=html_rendering)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python spider.py [url]")
        sys.exit(0)

    search(sys.argv[1], DEPTH, record)


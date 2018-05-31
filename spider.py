#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import requests
import bs4
import threading
import time


QTWEBENGINE = True
try:
    import sys 
    from PyQt5.QtCore import QUrl, QTimer
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWebEngineWidgets import QWebEngineView

    class Renderer(QWebEngineView):
        def __init__(self):
            self.html = None
            self.ready = False
            self.app = QApplication(sys.argv)
            QWebEngineView.__init__(self)

            self.timer = QTimer()

            self.loadFinished.connect(self._loadFinished)
            self.timer.timeout.connect(self.app.processEvents)
        
        def render(self, url, timeout=10):
            QTimer.singleShot(timeout * 1000, self._loadTimeoutError)
            self.timer.start(500)
        
            self.load(QUrl(url))
            self.app.exec_()

        def _loadTimeoutError(self):
            print("Load timeout")
            self.stop()
            self.loadFinished.emit(False)

        def _update_html(self, data):
            print("HTML Updated")
            self.html = data
            self.ready = True
            self.app.quit()

        def _loadFinished(self, result):
            self.page().toHtml(self._update_html)

except ImportError:
    QTWEBENGINE = False

# store all the visited websites
pool = set()

# the search depth of the first search
DEPTH = 2

renderer = Renderer()


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

    def visit(self, max_depth = DEPTH, response_handler=record, html_rendering=False, no_expand=lambda url, doc: False):
        """Recurse the webpage, and send the url, along with the webpage, to the handler
            max_depth: int, 
            response_handler: function(url:str, text:str), called when the response is valid
            no_expand: function(url:str, doc:str), to determine whether to expand current node
        """
        if self.depth >= max_depth:
            return
        if self.url.name in pool:
            return
        else:
            pool.add(self.url.name)
        
        print(f"Requesting {self.url.name}...")
        
# host for relative href
        try:
            host = re.search(r"(?:(?:https?:)?//)?([^/]+)", self.url.name).group(1)
        except Exception:
            host = None

# indicate if the request is successful
        flag = False
        site = None
        html = ''

        for req in self.url.request_string():
            if html_rendering:
                renderer.render(req, timeout=10)
                while not renderer.ready:
                    time.sleep(1)
                html = renderer.html
                site = bs4.BeautifulSoup(html, 'html5lib')
                if html:
                    flag = True
            else:
                try:
                    # print(f"Site: {req}")
                    r = requests.get(req, timeout = 5)
                    if r.status_code != 200:
                        print(f"Warning: HTTP response for {req} is {r.status_code} but 200")
                    else:
                        # print("OK")
                        flag = True
                        html = r.content.decode('utf-8')
                        site = bs4.BeautifulSoup(html, 'html5lib')
                        break
                except requests.exceptions.Timeout:
                    # print(f"Request time out : {req}")
                    pass
                except Exception:
                    # print(f"Failed to connect : {req}")
                    pass

        if not site:
            return

        if not flag:
            return

        urls = []

        # handle the response
        response_handler(self.url.name, html)

        # find successors
        for tag in site.find_all('a'):
            urls.append(tag.get('href'))
            # print('Link to', tag.get('href'))
        
        if no_expand(self.url.name, html):
            # stop expanding
            return

        thread_pool = []
        for url in urls:
            if not url:
                continue
            # add host if started with a slash
            if url[0] == '/':
                if len(url) > 1 and url[1] == '/':
                    url = url.lstrip('/')
                else:
                    url = host + url
            url = url.rstrip('/')

            searchTask = URL(url)

            if not searchTask.valid:
                # print(f"Invalid URL: {url}")
                continue
            else:
                # if the website has been visited
                if searchTask.name in pool:
                    continue
                else:
                    thread = threading.Thread(target=Node(searchTask, self.depth + 1).visit, args=(max_depth, response_handler))
                    thread.start()
                    thread_pool.append(thread)

        while thread_pool:
            for thread in thread_pool:
                thread.join(timeout=0)
                if not thread.is_alive():
                    thread_pool.remove(thread)
            time.sleep(1)

def search(url, depth, handler, html_rendering=False):
    """Recurse the webpage, and send the url, along with the webpage, to the handler
            depth: int, the maximum depth of the search
            handler: function(url:str, text:str), called when the response is valid
    """
    if html_rendering and not QTWEBENGINE:
        print("QtWebEngine package not found, do not render")
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


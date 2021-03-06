# Topic Monitor

Requires:
```
Python >=3.6
requests
BeautifulSoup
PyQt5(Optional, for webpage rendering)
tkinter(Optional, for GUI)
```

## How to use

Command line:
```
python main.py
```

GUI version:
```
python gui_main.py
```

## Code Structure

* `spider.py`
    * Function:
        * Scrape websites
        * Optional web rendering(using selenium)
    * API:
        * `search(url, depth, handler)` : recurse the websites and pass it to the handler

* `sender.py`
    * Function:
        * Send the warning message or other notifications
    * API:
        * `class EmailSender`
            * address: Email address
            * password: password for the mail account
            * recipients: an enumerable(`list` for example) of recipients' addresses
            * `send(subject, content)` : send text message to recipients' addresses

* `analyzer.py`
    * Function:
        * Find information in text
    * API:
        * `class Pattern`: find a pattern in the document
            * `Pattern.search(self, document)`: find the pattern in the document

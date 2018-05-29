# Topic Monitor

Requires:
```
Python >=3.6
BeautifulSoup
```

## Code Structure

* `spider.py`
    * Function:
        * Scrape websites
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

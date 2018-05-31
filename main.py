import json
from spider import search
from sender import ConsoleSender, EmailSender
import analyzer
import time

import bs4

def eventloop(sender=ConsoleSender()):
    urls = [
            'www.sohu.com'
            ]
    words = ['特朗普']
    pattern = analyzer.OrPattern(*[analyzer.Contains(word) for word in words])
    pattern = pattern - analyzer.Contains('歧视')
    pattern = analyzer.filter_tag('title')(pattern)

    send_urls = set()
    send_lines = []
    def handler(url, document):
        res = pattern.search(document)
        print(res)
        if res:
            bs = bs4.BeautifulSoup(document, "html5lib")
            title = bs.find('title').get_text()
            if url not in send_urls:
                send_urls.add(url)
                send_lines.append('{}: {}'.format(title, url))
    try:
        while True:
            for url in urls:
                search(url, 2, handler, html_rendering=False)
            if (send_lines):
                sender.send('Topic Alert', """The messages you subscribed are found here:
{}""".format('\n'.join(send_lines)))
                send_lines = []
                print("Sent")
            sleep_secs = 900
            print(f'Next scan in {sleep_secs} seconds')
            time.sleep(sleep_secs)
    except KeyboardInterrupt:
        print("Stopped")

if __name__ == '__main__':
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)
            email_account = config['email_account']
            email_password = config['email_password']
            recipients = config['recipients']
            email_sender = EmailSender(email_account, email_password, recipients)
    except Exception:
        config = {
            "email_account" : "my-mail-account@example.com",
            "email_password" : "my-mail-password",
            "recipients" : ["first-recipient@example.com", "second-recipient@example.com"]
        }
        print("""Configuration file not found
please edit config.json file""")
        with open("config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)
        exit(0)
    """If it is OK, run the event loop to scrape the websites and send messages"""
    eventloop(email_sender)

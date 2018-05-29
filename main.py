import json
from spider import search
from sender import ConsoleSender, EmailSender
import analyzer
import time


def eventloop(sender=ConsoleSender()):
    words = ['Europe', 'Korea']
    pattern = analyzer.OrPattern(*[analyzer.Contains(word) for word in words])
    def handler(url, document):
        if pattern.search(document):
            sender.send('Found', document)
    try:
        while True:
            search("http://edition.cnn.com", 2, handler)
            time.sleep(60)
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
    eventloop()

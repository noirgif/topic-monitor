import tkinter
import json
from spider import search
from sender import ConsoleSender, EmailSender
import analyzer
import time

import bs4

top = tkinter.Tk()
top.title("Web Monitor and Warning Sender")

html_render = tkinter.IntVar()

frame1 = tkinter.Frame(top)
label_u = tkinter.Label(frame1, text="URL = ", width='20')
label_u.pack(side=tkinter.LEFT)
checkbox_render = tkinter.Checkbutton(frame1, text="Render", variable=html_render)
checkbox_render.pack(side=tkinter.RIGHT)
entry_url = tkinter.Entry(frame1, width='32')
entry_url.pack(side=tkinter.RIGHT)

frame2 = tkinter.Frame(top)
label_m = tkinter.Label(frame2, text="Keyword = ", width='20')
label_m.pack(side=tkinter.LEFT)
entry_key = tkinter.Entry(frame2, width='40')
entry_key.pack(side=tkinter.RIGHT)

frame3 = tkinter.Frame(top)
label_d = tkinter.Label(frame3, text="Depth = ", width='20')
label_d.pack(side=tkinter.LEFT)
entry_dep = tkinter.Entry(frame3, width='40')
entry_dep.pack(side=tkinter.RIGHT)

frame4 = tkinter.Frame(top)
label_e = tkinter.Label(frame4, text="Email = ", width='20')
label_e.pack(side=tkinter.LEFT)
entry_eml = tkinter.Entry(frame4, width='40')
entry_eml.pack(side=tkinter.RIGHT)

label_top = tkinter.Label(top)
label_sep = tkinter.Label(top)
label_bot = tkinter.Label(top)

def eventloop(sender=ConsoleSender()):
    urls = entry_url.get().split(';')
    depth = int(entry_dep.get())

    pattern = []
    for words in entry_key.get().strip().split(';'):
        if not words:
            continue
        subpattern = []
        for word in words.strip().split():
            if not word:
                continue
            # rid '-'
            neg = word[0] == '-'
            if neg:
                word = word[1:]
            lo = analyzer.TitleContains(word)
            if neg:
                lo = analyzer.NegPattern(lo)
            subpattern.append(lo)
        pattern.append(analyzer.AndPattern(*subpattern))
    pattern = analyzer.OrPattern(*pattern)

    send_urls = set()
    send_lines = []
    def handler(url, document):
        if pattern.search(document) is not None:
            bs = bs4.BeautifulSoup(document, "html5lib")
            title = bs.find('title').get_text()
            if url not in send_urls:
                send_urls.add(url)
                send_lines.append('{}: {}'.format(title, url))

    try:
        while True:
            for url in urls:
                url = url.strip()
                if url:
                    search(url, depth, handler, html_rendering=html_render.get())
            if (send_lines):
                sender.send('Topic Alert', """The messages you subscribed are found here:
{}""".format('\n'.join(send_lines)))
            send_lines = []
            time.sleep(900)
    except KeyboardInterrupt:
        print("Stopped")

def main():
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)
            email_account = config['email_account']
            email_password = config['email_password']
            # recipients = config['recipients']
            recipients = [account.strip() for account in entry_eml.get().split(';') if account.strip()]
            email_sender = EmailSender(email_account, email_password, recipients)
    except Exception:
        config = {
            "email_account" : "my-mail-account@example.com",
            "email_password" : "my-mail-password"
            # "recipients" : ["first-recipient@example.com", "second-recipient@example.com"]
        }
        print("""Configuration file not found
please edit config.json file""")
        with open("config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)
        exit(0)
    """If it is OK, run the event loop to scrape the websites and send messages"""
    eventloop(email_sender)


frame5 = tkinter.Frame(top)
btn = tkinter.Button(frame5, text="Start Monitor", command=main)
btn.pack(side=tkinter.BOTTOM)

label_top.pack()
frame1.pack()
frame2.pack()
frame3.pack()
frame4.pack()
label_sep.pack()
frame5.pack()
label_bot.pack()
top.mainloop()

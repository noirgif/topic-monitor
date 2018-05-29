"""
Send a message
"""
import re

class Sender:
    def send(self, subject, content):
        raise NotImplementedError


class ConsoleSender(Sender):
    def send(self, subject, content):
        print(subject)

class EmailSender(Sender):
    def __init__(self, address, password, recipients, host=None):
        self.address = address
        self.username, self.host = re.search("(.*)@(.*)", address).groups()
        if host:
            self.host = host
        self.password = password
        self.recipients = recipients

    def send(self, subject, content):
        """send an email
            subject: the subject of the email
            content: the content of the email
            to: the recipient of the
        """
        from smtplib import SMTP, SMTPException
        from email.message import EmailMessage
        try:
            with SMTP(self.host) as smtp:
                smtp.login(self.username, self.password)
                for recipient in self.recipients:
                    msg = EmailMessage()
                    msg.set_content(content)
                    msg['Subject'] = subject
                    msg['From'] = self.address
                    msg['To'] = recipient
                    smtp.send_message(msg)
        except SMTPException:
            return

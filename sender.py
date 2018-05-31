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
        print(content)

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
                smtp.login(self.address, self.password)
                for recipient in self.recipients:
                    msg = EmailMessage()
                    msg.set_content(content)
                    msg['Subject'] = subject
                    msg['From'] = self.address
                    msg['To'] = recipient
                    smtp.send_message(msg)
        except SMTPException as err:
            print("SMTP Error: {}".format(err))

if __name__ == '__main__':
    import json
    with open('config.json') as config_file:
        config = json.load(config_file)
    email_account = config['email_account']
    email_password = config['email_password']
    recipients = config['recipients']
    email_sender = EmailSender(email_account, email_password, recipients)
    email_sender.send("""Email module test""",
    """Testing if the email module functions normally""")

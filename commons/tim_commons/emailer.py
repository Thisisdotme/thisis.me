'''
Created on Jul 26, 2012

@author: howard
'''

import smtplib
import os
from string import Template


SENDER = 'mailer@thisis.me'
PASSWORD = 'th1sisd0tm#'


def send_template(config, template, sender, recipient, subject, substitutions=None):

  # "Sends an e-mail to the specified recipient."

  # get SMTP configuration from config
  smtp_server = config['smtp_server']
  smtp_port = config['smtp_port']

  session = smtplib.SMTP(smtp_server, smtp_port)

  session.ehlo()
  session.starttls()
  session.ehlo()

  # get user-name and password from config
  user = config['user']
  password = config['password']

  session.login(user, password)

  # load the template file
  f = open(os.path.join(config['template_dir'], template), 'r')
  template_str = f.read()
  f.close()

  template = Template(template_str)

  body = "" + template.substitute(substitutions) + ""

  headers = ["From: " + sender,
             "Subject: " + subject,
             "To: " + recipient,
             "MIME-Version: 1.0",
             "Content-Type: text/html"]
  headers = "\r\n".join(headers)

  session.sendmail(sender, recipient, headers + "\r\n\r\n" + body)

  session.quit()

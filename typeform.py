import time
import json
import operator
import os
import requests
import logging
import email
from utilities.util import Util

u = Util()

def send_email(email_address,display_url):
    sender_address=os.environ['SENDING_ADDRESS']
    password = os.environ['PASSWORD']
    message = "From: %s\r\nSubject: %s\r\nTo: %s\r\n\r\n" % (sender_address,"Welcome to SendVibe - Let's Get Started!",email_address) + \
    """Welcome to the SendVibe family!  You're going to do great here!

They way I work at the moment is that I pay attention to you as you start to draft emails.  If you begin to draft an email to somebody with whom you would like to be more assertive, I send you an email with an exercise that you can run through before you finalize the draft. 

To get us started, select 2-3 individuals with whom you would like to be more assertive in your communication. (Don't worry, those people will never know you've selected them.)

To try to speed up the process, I've attempted to select some relevant individuals from your inbox by reviewing your 1,000 most recent emails.  See how I did at guessing and make some selections by filling out this short form:

<{}>

Estimated time: 2 minutes.

If you don't make any selections or enter any email address I'll just send you an exercise whenever you create any draft.  I'll start doing that two hours from now.  So it doesn't get annoying, I'll send you a maximum of one per hour.

Can't wait to work together!

Best,
SendVibe
""".format(display_url)

    u.mail(sender_address,email_address,message,password)
    return True


FIELD = """{
      "title": "Would you like to practice assertive communication with %s?",
      "type": "multiple_choice",
      "properties": {
        "description": "As a starting place, select 2-3 individuals from this list of 9 or add your own email address in the last question",
        "randomize": false,
        "allow_multiple_selection": false,
        "allow_other_choice": false,
        "vertical_alignment": false,
        "choices": [
          {
            "label": "Let's start with %s",
            "ref": "yes"
          },
          {
            "label": "Not this person",
            "ref": "no"
          }
        ]
      },
      "validations": {
        "required": false
      }
    }
    """ 

EMAIL = """{
      "title": "Enter an email address",
      "type": "email",
      "properties": {
        "description": "We can practice assertive communication with this individual"
      },
      "validations": {
        "required": false
      }
    }"""

def set_webhook(form_id,typeform_access_token):
    uri = "https://api.typeform.com/forms/{}/webhooks/sendvibe".format(form_id)
    headers = {'Authorization': typeform_access_token,"Content-Type":"application/json"}
    data = json.dumps({"url":"https://sendvibe.work/typeform", "enabled":True})
    r2 = requests.put(uri, headers = headers, data=data)
    print r2

def get_field(address):
    return FIELD % (address,address)

def get_fields(contacts):
    return ",".join([get_field(x) for x in contacts] + [EMAIL])

def email_typeform(email_address,contacts):
    data = '{"title": "SendVibe Setup for %s", "fields" : [%s]}' % (email_address, get_fields(contacts))
    typeform_access_token = "bearer {}".format(os.environ['ACCESS_TOKEN'])
    print 
    r = requests.post("https://api.typeform.com/forms", headers = {'Authorization': typeform_access_token}, data = data).json()
    if '_links' not in r:
        logging.error("_links not in typeform response")
        logging.error(data)
        logging.error(r)
        return False
    display_url = r['_links']['display']
    form_id = display_url.split("/")[-1]
    set_webhook(form_id,typeform_access_token)
    return send_email(email_address,display_url)

if __name__ == '__main__':
    email_typeform("sendvibe@gmail.com",["cool@cool.com","dude@dude.com"])

import json
import operator
import os
import requests

FIELD = """{
      "title": "Would you like to practice assertive communication with %s?",
      "type": "multiple_choice",
      "properties": {
        "description": "As a starting place, select 2-3 individuals from this list of 9 or enter your own list at the end",
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

def get_field(address):
    return FIELD % (address,address)

def get_fields(contacts):
    return ",".join([get_field(x) for x in contacts])

def email_typeform(email_address,contacts):
    data = '{"title": "SendVibe Setup", "fields" : [%s]}' % get_fields(contacts)
    typeform_access_token = "bearer {}".format(os.environ['ACCESS_TOKEN'])
    r = requests.post("https://api.typeform.com/forms", headers = {'Authorization': typeform_access_token}, data = data) 
    
    return r.json()

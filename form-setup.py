import json
import boto3
import operator
import os
import requests

min_from = 0
min_to = 0

s3 = boto3.client('s3',region_name='us-west-2')
from_dict = {}
to_dict = {}

def scrub(txt):
    if "<" in txt and ">" in txt:
        return txt.split('<')[1].split(">")[0]
    return txt
    
def email_typeform(email_address,contacts):
    typeform_access_token = os.environ['ACCESS_TOKEN']
    r = requests.post("https://api.typeform.com/forms", headers=headers = {'X-API-TOKEN': typeform_access_token})
    data = """
    {"title": "SendVibe Setup", 
    "fields" : [{
      "ref": "mc1",
      "title": "MC1",
      "type": "multiple_choice",
      "properties": {
        "description": "Cool description for the multiple choice",
        "randomize": true,
        "allow_multiple_selection": false,
        "allow_other_choice": true,
        "vertical_alignment": false,
        "choices": [
          {
            "label": "Foo",
            "ref": "foo_choice_ref"
          },
          {
            "label": "Bar",
            "ref": "bar_choice_ref"
          }
        ]
      },
      "validations": {
        "required": false
      }
    }]}
    """
    
    print r
    return None


def assess_top_contacts(dfrom, dto,contacts_to_return):
    both = {}
    for t in dto:
        if t in dfrom and dto[t]>min_to and dfrom[t]>min_from:
            volume = dfrom[t]+dto[t]
            fraction_to = float(dto[t])/float(volume)
            both[t] = 3 * fraction_to + 2 * volume
            #print t, volume, fraction_to
    
    sorted_contacts = sorted(both.items(), key=operator.itemgetter(1))[-contacts_to_return:]
    sorted_contacts.reverse()
    return sorted_contacts


def lambda_handler(event, context):
    for record in event['Records']:
        email_address = record['Sns']['Message']
        obj = s3.get_object(Bucket='email-data-first-run',Key=email_address)
        
        for line in obj['Body'].read().split("\n"):
            for header in json.loads(line.strip())['payload']['headers']:
                if header['name'] == 'To':
                    recipient_list = [scrub(x.strip()) for x in header['value'].split(",")]
                    for recipient in recipient_list:
                        if recipient not in to_dict:
                            to_dict[recipient] = 0
                        to_dict[recipient] += 1
                if header['name'] == 'From':
                    sender_list = [scrub(x.strip()) for x in header['value'].split(",")]
                    for sender in sender_list:
                        if sender not in from_dict:
                            from_dict[sender] = 0
                        from_dict[sender] += 1
                    
        contacts = [contact[0] for contact in assess_top_contacts(from_dict,to_dict, 2)]
        email_typeform(email_address,contacts)
        #s3.delete_object(Bucket='email-data-first-run',Key=email_address)    
    return "Hi Mom!"

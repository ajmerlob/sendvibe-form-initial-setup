import typeform
import json
import boto3
import operator
import os
import requests
import logging

min_from = 0
min_to = 0
num_contacts = 9

s3 = boto3.client('s3',region_name='us-west-2')
interaction_table = boto3.resource('dynamodb').Table('last_interaction')
from_dict = {}
to_dict = {}

def scrub(txt):
    if "<" in txt and ">" in txt:
        return txt.split('<')[1].split(">")[0]
    return txt
    
def assess_top_contacts(dfrom, dto,contacts_to_return,email_address):
    both = {}
    for t in dto:
        if t == "sendvibe@gmail.com" or t == "send.vibe@gmail.com" or t == email_address:
            continue
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
                    
        contacts = [contact[0] for contact in assess_top_contacts(from_dict,to_dict, num_contacts,email_address)]
        if typeform.email_typeform(email_address,contacts):
            logging.error("everything worked: {}".format(email_address))
        else:
            logging.error("something went wrong: {}".format(email_address))
        ## App won't interact for 2 hours
        interaction_table.put_item(Item={"email_address":email_address,"time":str(time.time()+3600)})
        s3.delete_object(Bucket='email-data-first-run',Key=email_address)    
    return "Hi Mom!"

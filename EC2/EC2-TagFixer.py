#
# Script scan specific EC2 instance tags & fix them if missing
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
from botocore.exceptions import ClientError

profile_name='qa'
session = boto3.Session(profile_name=profile_name)
client = session.client('ec2')
Next_Token = None



id='i-123456789'
current_tags=[]
new_tags=[]

ec2_tags = client.describe_tags(
Filters=[
            {
        'Name': 'resource-id',
        'Values': [id],
    },

],
)

if ec2_tags["Tags"]:
        tags = ec2_tags["Tags"]
        print(tags)
        #print(type(tags))
        for x in tags:
            current_tags.append(x['Key'])
        print(current_tags)
        if 'Rapid7' not in current_tags :
            print("INFO:Rapid7 Tag is missing and adding...")
            new_tags.append({'Key':'Rapid7', 'Value':'Yes'})
        if 'Nxlog' not in current_tags :
            print("INFO:Nxlog Tag is missing and adding...")
            new_tags.append({'Key':'Nxlog', 'Value':'Yes'})
        if 'Bitdefender' not in current_tags :
            print("INFO:Bitdefender Tag is missing and adding...")
            new_tags.append({'Key':'Bitdefender', 'Value':'Yes'})
        #print(new_tags)
        
        response = client.create_tags(Resources=[id], Tags=new_tags)
else:
        print("INFO:",id, "doesn't have any tags assigned")
        #print("unexpected error in versioning: %s" % (e.response))
        #Assing Default core tags and values to the bucket
        new_tags=[{'Key': 'Rapid7', 'Value': 'Yes'}, {'Key': 'Nxlog', 'Value': 'Yes'}, {'Key': 'Bitdefender', 'Value': 'Yes'}]
        response = client.create_tags(Resources=[id], Tags=new_tags)
        print("INFO: For EC2,",id,", all core tags are assigned")
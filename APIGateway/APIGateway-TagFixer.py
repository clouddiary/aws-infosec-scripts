#
# Script checks specific tags on ApiGateway & adds them if missing
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
from botocore.exceptions import ClientError

profile_name='qa'
session = boto3.Session(profile_name=profile_name)
client = session.client('apigateway')
Next_Token = None



id='arn:aws:apigateway:us-east-1::/restapis/lbd1kquyge/stages/qa'
current_tags=[]
try:
    stage = client.get_tags(resourceArn=id)
    if stage["tags"]:
            tags = stage["tags"]
            #print(type(tags))
            for x in tags:
                current_tags.append(x)
            if 'API-Xray' not in current_tags :
                print("INFO:API-Xray Tag is missing and adding...")
                tags['API-Xray']='Yes'
            if 'API-AccessLogging' not in current_tags :
                print("INFO:API-AccessLogging Tag is missing and adding...")
                tags['API-AccessLogging']='No'
            
            response = client.tag_resource(resourceArn=id,tags=tags)
except:
    print("INFO:",id, "doesn't have any tags assigned")
    #print("unexpected error in versioning: %s" % (e.response))
    #Assing Default core tags and values to the bucket
    tags={'API-AccessLogging': 'No', 'API-Xray':'Yes'}
    response = client.tag_resource(resourceArn=id,tags=tags)
    print("INFO: For API,",id,", all core tags are assigned")
#
# Script checks specific tags (Ex. WAF, SSL Policy) o ALB & adds them if missing
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
from botocore.exceptions import ClientError

profile_name='qa'
session = boto3.Session(profile_name=profile_name)
elbclient = session.client('elbv2')

elbName = "arn:aws:elasticloadbalancing:us-east-1:123456789:loadbalancer/app/System-SubSystem/123456789"

try:
    #Get the tags associated with the ALB
    all_tags = elbclient.describe_tags(ResourceArns=[elbName])
    tags = all_tags["TagDescriptions"][0]['Tags']
    current_tags=[]
    #Collect all the tags associated with the ALB
    for x in tags:
        current_tags.append(x['Key'])
    #Check ALB tags and add if any of the core tags are missing    
    if 'WAF' not in current_tags :
        print("INFO:WAF Tag is missing and adding...")
        tags.append({'Key': 'WAF', 'Value': 'Yes'})
    if 'SSLPolicy' not in current_tags :
        print("INFO:SSLPolicy Tag is missing and adding...")
        tags.append({'Key': 'SSLPolicy', 'Value': 'Yes'})
    
    response = elbclient.add_tags(ResourceArns=[elbName],Tags=tags)


except ClientError as e:
    print("INFO:",elbName," doesn't have any tags assigned")
    #print("unexpected error in versioning: %s" % (e.response))
    #Assing Default core tags and values to the ALB
    tags=[{'Key': 'WAF', 'Value': 'Yes'}, {'Key': 'SSLPolicy', 'Value': 'Yes'}]
    response = elbclient.add_tags(ResourceArns=[elbName],Tags=tags)
    print("INFO: For bucket,",elbName,", all core tags are assigned")

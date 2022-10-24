
#
# Script checks specific tags on VPC & adds them if missing
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
from botocore.exceptions import ClientError

profile_name='qa'
session = boto3.Session(profile_name=profile_name)
ec2 = session.resource('ec2')

id = "vpc-123456"
vpc = ec2.Vpc(id)


try:
    #Get the tags associated with the VPC
    all_tags = vpc.tags
    print(all_tags)
    tags = all_tags
    current_tags=[]
    #Collect all the tags associated with the VPC
    for x in tags:
        current_tags.append(x['Key'])
    #Check VPC tags and add if any of the core tags are missing    
    if 'VPC-FlowLog' not in current_tags :
        print("INFO:VPC-FlowLog Tag is missing and adding...")
        tags.append({'Key': 'VPC-FlowLog', 'Value': 'Yes'})
    print(tags)
    
    response = vpc.create_tags(Tags=tags)


except ClientError as e:
    print("INFO:",id," doesn't have any tags assigned")
    #print("unexpected error in versioning: %s" % (e.response))
    #Assing Default core tags and values to the VPC
    tags=[{'Key': 'VPC-FlowLog', 'Value': 'Yes'}]
    response = vpc.create_tags(Tags=tags)
    print("INFO: For VPC,",id,", all core tags are assigned")
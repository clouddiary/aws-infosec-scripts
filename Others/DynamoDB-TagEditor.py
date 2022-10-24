#
# Script checks specific tags on DynamoDB & adds them if missing
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
from botocore.exceptions import ClientError

profile_name='qa'
session = boto3.Session(profile_name=profile_name)
dbclient= session.client('dynamodb')

dynamodbName = "Inventory"

try:
    response = dbclient.describe_table(TableName=dynamodbName)
    dynamodbArn = response['Table']['TableArn']
        
    #Get the tags associated with the DynamoDB
    all_tags = dbclient.list_tags_of_resource(ResourceArn=dynamodbArn)
    tags = all_tags['Tags']
    current_tags=[]
    #Collect all the tags associated with the DynamoDB
    for x in tags:
        current_tags.append(x['Key'])
    #Check DynamoDB tags and add if any of the core tags are missing    
    if 'PITR' not in current_tags :
        print("INFO:PITR Tag is missing and adding...")
        tags.append({'Key': 'PITR', 'Value': 'No'})
    print(tags)
    
    response = dbclient.tag_resource(ResourceArn=dynamodbArn,Tags=tags)

except ClientError as e:
    print("INFO:",dynamodbArn," doesn't have any tags assigned")
    #print("unexpected error in versioning: %s" % (e.response))
    #Assing Default core tags and values to the DynamoDB
    tags=[{'Key': 'PITR', 'Value': 'No'}]
    response = dbclient.tag_resource(ResourceArn=dynamodbArn,Tags=tags)
    print("INFO: For DynamoDB,",dynamodbArn,", all core tags are assigned")

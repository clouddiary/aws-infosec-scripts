
#
# Script checks specific tags on S3 bucket & adds them if missing
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
from botocore.exceptions import ClientError

profile_name='qa'
session = boto3.Session(profile_name=profile_name)
s3client = session.client('s3')

bucketName = "deleteaftertesting"

try:
    #Get the tags associated with the bucket
    all_tags = s3client.get_bucket_tagging(Bucket=bucketName)
    tags = all_tags["TagSet"]
    current_tags=[]
    #Collect all the tags associated with the bucket
    for x in tags:
        current_tags.append(x['Key'])
    #Check bucket tags and add if any of the core tags are missing    
    if 'LifeCycle' not in current_tags :
        print("INFO:LifeCycle Tag is missing and adding...")
        tags.append({'Key': 'LifeCycle', 'Value': 'Yes'})
    if 'Logging' not in current_tags :
        print("INFO:Logging Tag is missing and adding...")
        tags.append({'Key': 'Logging', 'Value': 'No'})
    if 'Versioning' not in current_tags :
        print("INFO:Versioning Tag is missing and adding...")
        tags.append({'Key': 'Versioning', 'Value': 'No'})
    if 'Encryption' not in current_tags :
        print("INFO:Encryption Tag is missing and adding...")
        tags.append({'Key': 'Encryption', 'Value': 'Yes'})
    if 'PublicAccess' not in current_tags :
        print("INFO:PublicAccess Tag is missing and adding...")
        tags.append({'Key': 'PublicAccess', 'Value': 'No'})
    
    tag_template = {'TagSet':tags}
    response = s3client.put_bucket_tagging(Bucket=bucketName,Tagging= tag_template)

except ClientError as e:
        print("INFO:",bucketName," doesn't have any tags assigned")
        #print("unexpected error in versioning: %s" % (e.response))
        #Assing Default core tags and values to the bucket
        tags=[{'Key': 'LifeCycle', 'Value': 'Yes'}, {'Key': 'Logging', 'Value': 'No'}, {'Key': 'Versioning', 'Value': 'No'}, {'Key': 'Encryption', 'Value': 'Yes'}, {'Key': 'PublicAccess', 'Value': 'No'}]
        tags_template = {'TagSet':tags}
        response = s3client.put_bucket_tagging(Bucket=bucketName,Tagging=tags_template)
        print("INFO: For bucket,",bucketName,", all core tags are assigned")
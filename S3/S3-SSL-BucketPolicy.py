
#
# Script scans specific s3 bucket for required security controls on bucket policy & adds it if missing
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
import xlsxwriter
import subprocess
import re
from botocore.exceptions import ClientError

profile_name='qa'

session = boto3.Session(profile_name=profile_name)
s3client = session.client('s3')
response = s3client.list_buckets()
print("Generating S3 Inventory....")

'''
while True:
    if response and response['Buckets']:
        for bucket in response['Buckets']:
            bucketName = bucket['Name']
            #print("bucketName",bucketName)
            try:
                response = s3client.get_bucket_policy(Bucket=bucketName)
                print("INFO: Bucket Policy exists ", bucketName)
            except ClientError as e:
                response =""
                #print("INFO: No Bucket Policy for", bucketName, ". Adding one..")

    if 'NextToken' in response and response['NextToken'] is not None:
        response = s3client.list_buckets(NextToken=response['NextToken'])
    else:
        break;
'''

bucketName = "sample-20-na"

s3client = boto3.client('s3')
try:
    response = s3client.get_bucket_policy(Bucket=bucketName, ExpectedBucketOwner="1234567890")
    print(response['Policy'])
    policy1 = json.loads(response['Policy'])
    print(policy1)
    print("INFO: There is a Policy for", bucketName)
    bucketResource1 = "arn:aws:s3:::"+bucketName
    bucketResource2 = "arn:aws:s3:::"+bucketName+"/*"

    print(policy1['Statement'])
    print(type(policy1['Statement']))
    new_policy = policy1['Statement'].append(
        {
            "Sid":"AllowSSLRequestsOnly",
            "Action":"s3:*",
            "Effect":"Deny",
            "Resource":[
            bucketResource1,
            bucketResource2
            ],
            "Condition":{
            "Bool":{
                "aws:SecureTransport":"false"
            }
            },
            "Principal":"*"
        }
    )
    #print(policy1)
    s3client.delete_public_access_block(Bucket=bucketName)
    s3client.put_bucket_policy(Bucket=bucketName, Policy=json.dumps(policy1))
    s3client.put_public_access_block(
    Bucket=bucketName,
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
    )    
    
except ClientError as e:
    print("$$$$$$$$$$$$unexpected error in versioning: %s" % (e.response))
    print("INFO: No Bucket Policy for", bucketName, ". Adding one..")
    bucketResource1 = "arn:aws:s3:::"+bucketName
    bucketResource2 = "arn:aws:s3:::"+bucketName+"/*"
    bucket_policy = {
    "Version":"2012-10-17",
    "Statement":[
        {
            "Sid":"AllowSSLRequestsOnly",
            "Action":"s3:*",
            "Effect":"Allow",
            "Resource":[
            bucketResource1,
            bucketResource2
            ],
            "Condition":{
            "Bool":{
                "aws:SecureTransport":"false"
            }
            },
            "Principal":"*"
        }
    ]
    }
    print(bucket_policy)
    s3client.delete_public_access_block(Bucket=bucketName)
    s3client.put_bucket_policy(Bucket=bucketName, Policy=json.dumps(bucket_policy), ExpectedBucketOwner="1234567890")
    s3client.put_public_access_block(
    Bucket=bucketName,
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
    )
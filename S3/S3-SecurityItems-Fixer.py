#
# Script pulls all s3 buckets with fixes security controls (if not set correctly) like Versioning, Encryption, Logging, PublicAccess & LifeCycle
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
import xlsxwriter
import subprocess
import re
from botocore.exceptions import ClientError

## Update local aws cli profile name here
profile_name='qa'
xlsx_filename='tezs-qa.xlsx'
title='crx-dev'
session = boto3.Session(profile_name=profile_name)
s3client = session.client('s3')
response = s3client.list_buckets()
print("helo")

#
# Create the Spread Sheet
#

workbook = xlsxwriter.Workbook(xlsx_filename)
bold = workbook.add_format({'bold': True})
row = 0
SheetName = 'S3 Info'
worksheet = workbook.add_worksheet('S3Info')
worksheet.write(row, 0, 'BucketName', bold)
worksheet.write(row, 1, 'Versioning', bold)
worksheet.write(row, 2, 'Encryption', bold)
worksheet.write(row, 3, 'Logging', bold)
worksheet.write(row, 4, 'PublicAccess', bold)
worksheet.write(row, 5, 'LifeCycle', bold)

#worksheet.write(row, 1, 'InstanceName', bold)

row += 1

bucketName="s3bucketfixer123"

'''
while True:
        if response and response['Buckets']:
            for bucket in response['Buckets']:
                bucketName = bucket['Name']
'''
try:
    response = s3client.get_bucket_versioning(Bucket=bucketName)                    
    if 'Status' in response:
        worksheet.write(row, 0, bucketName)
        worksheet.write(row, 1, "Versioning Enabled")
    else:
        worksheet.write(row, 0, bucketName)
        worksheet.write(row, 1, "Versioning not Enabled")
        version_response = s3client.put_bucket_versioning(Bucket=bucketName, VersioningConfiguration={'MFADelete': 'Disabled', 'Status': 'Enabled',},)
except ClientError as e:
        print("unexpected error in versioning: %s" % (e.response))

try:
    response = s3client.get_bucket_encryption(Bucket=bucketName)
    worksheet.write(row, 2, "Encryption Enabled")
except ClientError as e:
    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
        worksheet.write(row, 2, "Encryption Not Enabled")
        encryption_response = s3client.put_bucket_encryption(Bucket=bucketName,ServerSideEncryptionConfiguration={'Rules': [{
            'ApplyServerSideEncryptionByDefault': {
                'SSEAlgorithm': 'AES256'
            }}]
        })
    else:
        worksheet.write(row, 2, "Unexpected Error")

try:
    response = s3client.get_bucket_logging(Bucket=bucketName)                    
    if 'LoggingEnabled' in response:                        
        worksheet.write(row, 3, "Logging Enabled")
    else:                        
        worksheet.write(row, 3, "Logging not Enabled")
except ClientError as e:
        print("unexpected error in logging: %s" % (e.response))

try:
    response = s3client.get_public_access_block(Bucket=bucketName)
    worksheet.write(row, 4, "Restricted Bucket")
except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
        worksheet.write(row, 4, "Public Bucket")
        access_response = s3client.put_public_access_block(Bucket=bucketName,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            },
        )
    else:
        worksheet.write(row, 4, "Unexpected Error")

try:
    response = s3client.get_bucket_lifecycle(Bucket=bucketName)
    worksheet.write(row, 5, "LifeCycle Configured")
except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
        worksheet.write(row, 5, "No LifeCycle Configured")
        
        lifecycle_response = s3client.put_bucket_lifecycle_configuration(
            Bucket=bucketName,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'ID':'Bucket-Standard-Rule',
                        'Status': 'Enabled',
                        'Prefix':'',
                        'Transitions': [{
                            'Days': 30,
                            'StorageClass': 'INTELLIGENT_TIERING',
                        },
                        {
                            'Days': 365,
                            'StorageClass': 'ONEZONE_IA',
                        }],
                        'NoncurrentVersionTransitions': [{
                        'NoncurrentDays': 180,
                        'StorageClass': 'GLACIER',
                        }],
                        'NoncurrentVersionExpiration': {
                        'NoncurrentDays': 365
                        },
                        'AbortIncompleteMultipartUpload': {
                            'DaysAfterInitiation': 30
                        },
                    }
                ]
            }
        ) 
    else:
        worksheet.write(row, 5, "Unexpected Error")
                   
'''                
                row += 1

        if 'NextToken' in response and response['NextToken'] is not None:
            response = s3client.list_buckets(NextToken=response['NextToken'])
        else:
            break;
'''
workbook.close()            
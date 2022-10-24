

#
# Script checks specific tags on RDS cluster & adds them if missing
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
from botocore.exceptions import ClientError

profile_name='qa'
session = boto3.Session(profile_name=profile_name)
rds = session.client('rds')

#id = "cluster-BUXUBYGSTJQ7NF5AWOEWU5D7IM"
id = "cluster-4DNLROMXTJBZGKB4XNHPKOSIIU"
try:
    #Get RDS Arn name
    
    #response = rds.describe_db_clusters(Filters=[
    #    {'Name':'dbi-resource-id',
    #    'Values':[id]
    #    }])
    
    #response = rds.describe_db_clusters(DBClusterIdentifier=id)
    response = rds.describe_db_clusters()
    #print("response.....", response)
    for dbc in response['DBClusters']:        
        if(dbc['DbClusterResourceId'] == id):
            print("-------------")
            print(dbc['DbClusterResourceId'])
            print(dbc['DBClusterArn'])
            tags = dbc['TagList']
            current_tags=[]
            for x in tags:
                current_tags.append(x['Key'])
            if 'RDS-Backup' not in current_tags :
                print("INFO:RDS-Backup Tag is missing and adding...")
                tags.append({'Key': 'RDS-Backup', 'Value': 'No'})
            if 'RDS-DeleteProtection' not in current_tags :
                print("INFO:RDS-DeleteProtection Tag is missing and adding...")
                tags.append({'Key': 'RDS-DeleteProtection', 'Value': 'Yes'})

            response = rds.add_tags_to_resource(ResourceName=dbc['DBClusterArn'],Tags=tags)
            print(tags)
        
        
    '''
    ResourceArn = response['DBInstances'][0]['DBInstanceArn']
    #Get the tags associated with the RDS
    all_tags = rds.list_tags_for_resource(ResourceName=ResourceArn)
    print(all_tags)
    tags = all_tags['TagList']
    current_tags=[]
    #Collect all the tags associated with the RDS
    for x in tags:
        current_tags.append(x['Key'])
    #Check RDS tags and add if any of the core tags are missing    
    if 'RDS-Backup' not in current_tags :
        print("INFO:RDS-Backup Tag is missing and adding...")
        tags.append({'Key': 'RDS-Backup', 'Value': 'No'})
    if 'RDS-DeleteProtection' not in current_tags :
        print("INFO:RDS-DeleteProtection Tag is missing and adding...")
        tags.append({'Key': 'RDS-DeleteProtection', 'Value': 'Yes'})
    print(tags)
    #response = rds.add_tags_to_resource(ResourceName=ResourceArn,Tags=tags)
    '''

except ClientError as e:
    print("INFO:",ResourceArn," doesn't have any tags assigned")
    print("unexpected error in versioning: %s" % (e.response))
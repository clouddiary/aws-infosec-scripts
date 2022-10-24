#
# Script pulls all EC2 instances & check if they have role with policy AmazonSSMManagedInstanceCore & ApplyPatches tags set
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
import xlsxwriter
from botocore.exceptions import ClientError
#from botocore.exceptions import TypeError

## Update local aws cli profile name here
profile_name='qa'
session = boto3.Session(profile_name=profile_name)
ec2 = session.resource('ec2')
client = session.client('ec2')
iam_client = session.client('iam')


#
# Create the Spread Sheet
#
workbook = xlsxwriter.Workbook('tezs-qa.xlsx')
bold = workbook.add_format({'bold': True})
row = 0
SheetName = 'EC2 Instances'
worksheet = workbook.add_worksheet('Fix for Patching')
worksheet.write(row, 0, 'InstanceId', bold)
worksheet.write(row, 1, 'Fix', bold)

running_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])

for instance in running_instances:
    
    isRole_good = 0
    #print (instance.id)
    response = client.describe_instances(InstanceIds=[instance.id])
    try:
        tag_count = 0
        for tag in instance.tags:
            if 'ApplyPatches'in tag['Key']:
                if tag['Key'] == "ApplyPatches" :
                    tag_count += 1
        if tag_count != 1:
            row += 1
            print(instance.id,"Instace doesn't have \"ApplyPatches\" tag")
            worksheet.write(row, 0, instance.id)
            worksheet.write(row, 1, "ApplyPatches tag")
                
                    #print()
    except TypeError:
        print("Instance ID: ",instance.id, " No Tages defined")

all_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])

for instance in all_instances:
    isRole_good = 0
    #print(instance.id,instance.iam_instance_profile['Arn'] )
    try:
        role = instance.iam_instance_profile['Arn'].split("/",1)[1]
    except TypeError:
        row += 1
        print(instance.id, "No role")
        worksheet.write(row, 0, instance.id)
        worksheet.write(row, 1, "No Role")

    try:
        role_response = iam_client.list_attached_role_policies(RoleName=role)
        #print(role_response)
        for policy in role_response['AttachedPolicies']:
            if policy['PolicyName'] == "AmazonSSMManagedInstanceCore":
                isRole_good += 1
        if (isRole_good != 1):
            row += 1
            worksheet.write(row, 0, instance.id)
            worksheet.write(row, 1, role)

            print (instance.id, role, "fix it")
    except ClientError:
        row += 1
        worksheet.write(row, 0, instance.id)
        worksheet.write(row, 1, role)
        print(instance.id, role,"check/fix it")

workbook.close()
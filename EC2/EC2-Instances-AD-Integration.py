
#
# Script finds out what all EC2 instances are joined to AD or not
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
import xlsxwriter
import subprocess
import re
import time

## Update local aws cli profile name here
profile_name='qa'
xlsx_filename='QA-EC2-AD-Inventory.xlsx'
title='QA-EC2-AD-Inventory'

session = boto3.Session(profile_name=profile_name)
ec2 = session.resource('ec2')
client = session.client('ssm')

#
# Create the Spread Sheet
#
#workbook = xlsxwriter.Workbook('Automated-SSM-Patch-Inventory-Dev.xlsx')
workbook = xlsxwriter.Workbook(xlsx_filename)
bold = workbook.add_format({'bold': True})
row = 0
SheetName = 'EC2 Instances'
worksheet = workbook.add_worksheet('ADStatus')
worksheet.write(row, 0, 'InstanceId', bold)
worksheet.write(row, 1, 'InstanceName', bold)
worksheet.write(row, 2, 'Auto Scaling?', bold)
worksheet.write(row, 3, 'System', bold)
worksheet.write(row, 4, 'Environment', bold)
worksheet.write(row, 5, 'Platform', bold)
worksheet.write(row, 6, 'AD Integration', bold)

row += 1

running_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}],  
    )

## Uncomment below section If you want to know AD status for specific instance Id - If you uncomment this section, make sure to comment above one.
#running_instances = ec2.instances.filter(
#    InstanceIds=[
#        'i-0b5a20462cca6b0b5',
#        'i-0f094f5872f54fadd',
#        'i-0dca8b71105d1d27b'
#    ]
#    )

for instance in running_instances:
    print (instance.id)
    worksheet.write(row, 0, instance.id)
    worksheet.write(row, 4, title)
    worksheet.write(row, 5, instance.platform)

    if (instance.platform == 'windows'):
        print("Windows")
        try:
            response = client.send_command(InstanceIds=[instance.id],
                 DocumentName="AWS-RunPowerShellScript",
                Parameters={
                    'commands':['if ($(systeminfo | findstr /B "Domain" | Measure).Count -gt 0){','Write-Host "AD"','}']
                   },
            )
            command_id = response['Command']['CommandId']
            time.sleep(10)
            output = client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance.id
            )
            if ("AD" in output['StandardOutputContent'] ):
                print ("AD Integrated")
                worksheet.write(row, 6, 'AD Integrated')
            else:
                print ("AD not Integrated")
                worksheet.write(row, 6, 'AD not Integrated')
        except:
            print("Not Managed by SSM")
            worksheet.write(row, 6, "SSM Not Reachable")

    else:
        try:
            response = client.send_command(InstanceIds=[instance.id],
                 DocumentName="AWS-RunShellScript",

                ## tezs.internal is my internal domain where all ec2 are joined.
                Parameters={
                    'commands':['if grep -q "tezs.internal" /etc/resolv.conf ; then','echo "AD"','fi']
                    #'commands':['pgrep -f BitDefender &> /dev/null && echo "BD"','pgrep -f nxlog &> /dev/null && echo "NXLog"','pgrep -f ir_agent &> /dev/null && echo "Rapid7"',]
                   },
            )
            command_id = response['Command']['CommandId']
            time.sleep(10)
            output = client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance.id
            )
        
            print(output)
            if ("AD" in output['StandardOutputContent'] ):
                print ("AD Integrated")
                worksheet.write(row, 6, 'AD Integrated')
            else:
                print ("AD not Integrated")
                worksheet.write(row, 6, 'AD not Integrated')
        except:
            print("Not Managed by SSM")
            worksheet.write(row, 6, "SSM Not Reachable")

 
    try:
        for tag in instance.tags:
            if 'Name'in tag['Key']:
                if tag['Key'] == "Name" :
                    name = tag['Value']
                    print(name)
                    worksheet.write(row, 1, name, bold)
            if 'aws:autoscaling:groupName' in tag['Key'] :
                asg = tag['Value']
                worksheet.write(row, 2, asg)
            if 'System'in tag['Key']:
                if tag['Key'] == "System" :
                    name = tag['Value']
                    worksheet.write(row, 3, name)
            if 'ApplyPatches'in tag['Key']:
                if tag['Value'] == "Appliance" :
                    worksheet.write(row, 3, "Appliance")
                if tag['Value'] == "Delete" :
                    worksheet.write(row, 3, "Delete")
              
               
    except TypeError:
        print("Tags not available")
        
    row += 1

workbook.close()
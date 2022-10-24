#
# Script pulls EC2 instance & check status for various security controls on each instances & dumps out in an excel sheet.
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
xlsx_filename='tezs-qa-security-inventory.xlsx'
title='tezs-qa'

session = boto3.Session(profile_name=profile_name)
ec2 = session.resource('ec2')
client = session.client('ssm')

#
# Create the Spread Sheet
workbook = xlsxwriter.Workbook(xlsx_filename)
bold = workbook.add_format({'bold': True})
row = 0
SheetName = 'EC2 Instances'
worksheet = workbook.add_worksheet('PatchingStatus')
worksheet.write(row, 0, 'InstanceId', bold)
worksheet.write(row, 1, 'InstanceName', bold)
worksheet.write(row, 2, 'Auto Scaling?', bold)
worksheet.write(row, 3, 'PatchingStatus', bold)
worksheet.write(row, 4, 'EnpointSecurity', bold)
worksheet.write(row, 5, 'NXLog', bold)
worksheet.write(row, 6, 'Instance Type', bold)
worksheet.write(row, 7, 'WAF', bold)
worksheet.write(row, 8, 'Hardening', bold)
worksheet.write(row, 9, 'ImageID', bold)
worksheet.write(row, 10, 'System', bold)
worksheet.write(row, 11, 'Environment', bold)
worksheet.write(row, 12, 'Rapid7', bold)


row += 1


running_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])
    #,
    #{'Name':'tag:System', 'Values':['XYZ']}])

for instance in running_instances:
    print (instance.id)
    worksheet.write(row, 0, instance.id)
    worksheet.write(row, 6, instance.instance_type)
    worksheet.write(row, 9, instance.image_id)
    worksheet.write(row, 11, title)

    if (instance.platform == 'windows'):
        print("Windows")
        try:
            response = client.send_command(InstanceIds=[instance.id],
                 DocumentName="AWS-RunPowerShellScript",
                Parameters={
                    'commands':['if ($(Get-Service  | Where-Object {$_.Status -eq \'Running\' -and $_.Name -eq \'EPSecurityService\'} | Measure).Count -gt 0){','Write-Host "BD"','}','if ($(Get-Service  | Where-Object {$_.Status -eq \'Running\' -and $_.Name -eq \'nxlog\'} | Measure).Count -gt 0){','Write-Host "NXLog"','}','if ($(Get-Service  | Where-Object {$_.Status -eq \'Running\' -and $_.Name -eq \'ir_agent\'} | Measure).Count -gt 0){','Write-Host "Rapid7"','}']
                   },
            )
            command_id = response['Command']['CommandId']
            time.sleep(10)
            output = client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance.id
            )
            if ("BD" in output['StandardOutputContent'] ):
                print ("BD installed")
                worksheet.write(row, 4, "BD installed")
            else:
                print ("BD not installed")
                worksheet.write(row, 4, "BD not installed")

            if ("NXLog" in output['StandardOutputContent'] ):
                print ("NXLog installed")
                worksheet.write(row, 5, 'NXLog installed')
            else:
                print ("NXLog not installed")
                worksheet.write(row, 5, 'NXLog not installed')

            if ("Rapid7" in output['StandardOutputContent'] ):
                print ("Rapid7 installed")
                worksheet.write(row, 12, 'Rapid7 installed')
            else:
                print ("Rapid7 not installed")
                worksheet.write(row, 12, 'Rapid7 not installed')
        except:
            print("Not Managed by SSM")
            worksheet.write(row, 4, "Not Reachable")
            worksheet.write(row, 5, "Not Reachable")

    else:
        try:
            response = client.send_command(InstanceIds=[instance.id],
                 DocumentName="AWS-RunShellScript",
                Parameters={
                    #'commands':['if [ -e /etc/nxlog.conf ] || [ -e /opt/nxlog/etc/nxlog.conf ]; then','echo "NXLog"','fi','if [ -e /var/bitdefender/installer ]; then','echo "BD"','fi','if [ -e /opt/rapid7/ir_agent/ir_agent ]; then','echo "Rapid7"','fi']
                    'commands':['pgrep -f BitDefender &> /dev/null && echo "BD"','pgrep -f nxlog &> /dev/null && echo "NXLog"','pgrep -f ir_agent &> /dev/null && echo "Rapid7"',]
                   },
            )
            command_id = response['Command']['CommandId']
            time.sleep(10)
            output = client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance.id
            )
        
            print(output)
            if ("NXLog" in output['StandardOutputContent'] ):
                print ("NXLog installed")
                worksheet.write(row, 5, 'NXLog installed')
            else:
                print ("NXLog not installed")
                worksheet.write(row, 5, 'NXLog not installed')

            if ("BD" in output['StandardOutputContent'] ):
                print ("BD installed")
                worksheet.write(row, 4, "BD installed")
            else:
                print ("BD not installed")
                worksheet.write(row, 4, "BD not installed")
            if ("Rapid7" in output['StandardOutputContent'] ):
                print ("Rapid7 installed")
                worksheet.write(row, 12, "Rapid7 installed")
            else:
                print ("Rapid7 not installed")
                worksheet.write(row, 12, "Rapid7 not installed")
        except:
            print("Not Managed by SSM")
            worksheet.write(row, 4, "Not Reachable")
            worksheet.write(row, 5, "Not Reachable")

    if instance.image_id == "ami-0b469ce265686ac64":
        worksheet.write(row, 8, "Yes")
    else:
        worksheet.write(row, 8, "No")

    response1 = client.describe_instance_patch_states(InstanceIds=[instance.id])
    for patch_info in response1['InstancePatchStates']:
        print(patch_info)
        print(patch_info['InstanceId'],patch_info['BaselineId'],patch_info['InstalledCount'], patch_info['InstalledOtherCount'], patch_info['InstalledPendingRebootCount'], patch_info['InstalledRejectedCount'], patch_info['MissingCount'],patch_info['FailedCount'])
        if(patch_info['MissingCount'] == 0):
            worksheet.write(row, 3, "Patch-Compliant")
        else:
            worksheet.write(row, 3, "Patch-NonCompliant")
    

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
                    worksheet.write(row, 10, name)
              
               
    except TypeError:
        worksheet.write(row, 3, "Not Reachable")
        
    row += 1

workbook.close()
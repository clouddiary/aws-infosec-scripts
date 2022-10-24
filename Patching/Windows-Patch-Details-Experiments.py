#
# Script pulls missing patches details
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
import xlsxwriter
import subprocess
import re

## Update local aws cli profile name here
profile_name='qa'
session = boto3.Session(profile_name=profile_name)
ec2 = session.resource('ec2')
client = session.client('ssm')

#
# Create the Spread Sheet
#
patches_complete_info = dict() 
Patches = ['KB4103723','KB4552926','KB4562561','kernel.x86_64','KB4552926','KB4562561']
Patches = list(set(Patches))

for KB in Patches:
    print (KB)
    if(re.match(r"^KB", KB)):
        print("from matching",KB) 
        paginator = client.get_paginator('describe_available_patches')
        response_iterator = paginator.paginate(
        Filters=[
            {
                'Key': 'PATCH_ID',
                'Values': [KB]
            }
        ])

        for patch_info in response_iterator:
            print(patch_info['Patches'][0]['ReleaseDate'],patch_info['Patches'][0]['Title'])
            patches_complete_info.setdefault(KB, []).append(str(patch_info['Patches'][0]['ReleaseDate']).split(' ', 1)[0])
            patches_complete_info.setdefault(KB, []).append(patch_info['Patches'][0]['Title'])
    else:
         patches_complete_info[KB]=["NA","NA"]
print(patches_complete_info)

for patch,value in patches_complete_info.items():
    print(patch,value[0],value[1])
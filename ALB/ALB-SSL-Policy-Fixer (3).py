#
# Script scans all ALBs in an account & verifies if specific WAf Id attached or not
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3
import json
import xlsxwriter
import subprocess
import re
from botocore.exceptions import ClientError


profile_name='qa'
xlsx_filename='TEZS-WAF.xlsx'
title='tez-qa'
session = boto3.Session(profile_name=profile_name)

workbook = xlsxwriter.Workbook(xlsx_filename)
bold = workbook.add_format({'bold': True})
row = 0
SheetName = 'ALB Info'
worksheet = workbook.add_worksheet('ALBInfo')
worksheet.write(row, 0, 'ALBName', bold)
worksheet.write(row, 1, 'ALBArn', bold)
worksheet.write(row, 2, 'Status', bold)


row += 1


albs = session.client('elbv2')
mywaf = session.client('waf-regional')
#waf = session.client('wafv2')
All_Albs = albs.describe_load_balancers()


#Dev WAF ACL ID
dev_wafacl_id = "6afbb7b0-8cac-42ec-97e1-8a66f337da96"
#Dev WAF ACL ID
qa_wafacl_id = ""
#Dev WAF ACL ID
uat_wafacl_id = ""
#Dev WAF ACL ID
prod_wafacl_id = ""

'''
try:
    mywaf.associate_web_acl(
                WebACLId = wafacl_id,
                ResourceArn = loadbalancer_arn
                )
except ClientError as e:
    print("unexpected error: %s" % (e.response))

'''

while True:
    for alb in All_Albs["LoadBalancers"]:
        arn = alb["LoadBalancerArn"]
        albName = alb["LoadBalancerName"]

        # Checking Waf    
        try:
            response = mywaf.get_web_acl_for_resource(ResourceArn=arn)
            #print(response)
            if ("WebACLSummary" in response):
                print('AlbWaf is compliant')
                worksheet.write(row, 0, albName)
                worksheet.write(row, 1, arn)
                worksheet.write(row, 2, 'Complaint')
            else:
                worksheet.write(row, 0, albName)
                worksheet.write(row, 1, arn)
                worksheet.write(row, 2, 'Non-Complaint')
                #mywaf.client.associate_web_acl(
                #    WebACLId= dev_wafacl_id,
                #    ResourceArn= alb["LoadBalancerArn"]
                #)
        except ClientError as e:
                print("Problem ALB is: ",albName)
                worksheet.write(row, 0, albName)
                worksheet.write(row, 1, arn)
                worksheet.write(row, 2, 'Problem')
                print("unexpected error: %s" % (e.response))
        row += 1
        
    
                        

    if 'NextToken' in All_Albs and All_Albs['NextToken'] is not None:
        All_Albs = albs.describe_load_balancers(NextToken=All_Albs['NextToken'])
    else:
        break;

workbook.close()    
#
# Script lists Api gateway custom domains along with its SSL policy
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import sys
import boto3
from datetime import datetime
import argparse
import xlsxwriter
import json
from botocore.exceptions import ClientError

xlsx_filename='API-SSL-Info.xlsx'
profile_name='qa'
session = boto3.Session(profile_name=profile_name)
client = session.client('apigateway')

workbook = xlsxwriter.Workbook(xlsx_filename)
bold = workbook.add_format({'bold': True})
row = 0
SheetName = 'API Info'
worksheet = workbook.add_worksheet('APIInfo')
worksheet.write(row, 0, 'DomainName', bold)
worksheet.write(row, 1, 'TLS', bold)

row += 1

Next_Token = None
paginator = client.get_paginator('get_domain_names')

while True:
    
    response_iterator = paginator.paginate(
        PaginationConfig={
            'MaxItems': 100,
            'PageSize': 100,
            'StartingToken': Next_Token
        }
    )
    for page in response_iterator:
        #api_items = page['items']
        for item in page['items']:
            print(item['domainName'],item['securityPolicy'])
            worksheet.write(row, 0, item['domainName'])
            worksheet.write(row, 1, item['securityPolicy'])
            row += 1     
        try:
            Next_Token = page['nextToken']
            print(Next_Token)
        except KeyError:
            workbook.close()
            sys.exit()

workbook.close()
#
# Script fetches all ALBs & fixes SSL policy if its not set to ELBSecurityPolicy-TLS-1-2-Ext-2018-06 
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.
import sys
import boto3
import json
import xlsxwriter
import subprocess
import re
import time
from botocore.exceptions import ClientError

profile_name='qa'
xlsx_filename='TEZS-QA-EC2-ALBs.xlsx'
title='tez-qa'
session = boto3.Session(profile_name=profile_name)
#client = session.client('elb')
albs = session.client('elbv2')

#
# Create the Spread Sheet
#


# Loop through the v2 loadbalancers and print the details.


All_Albs = albs.describe_load_balancers()
while True:

    for alb in All_Albs["LoadBalancers"]:
                arn = alb["LoadBalancerArn"]
                albName = alb["LoadBalancerName"]
                try:        
                    listners=albs.describe_listeners(LoadBalancerArn=arn)
                    alblistner = listners["Listeners"]
                    for listner in alblistner:
                        #if listner["Protocol"] == 'HTTPS' and arn == "arn:aws:elasticloadbalancing:us-east-1:123456789:loadbalancer/app/testapp/f01f4d21e088ec0c" and listner["SslPolicy"] != "ELBSecurityPolicy-TLS-1-2-Ext-2018-06":
                        if listner["Protocol"] == 'HTTPS' and listner["SslPolicy"] != "ELBSecurityPolicy-TLS-1-2-Ext-2018-06":
                            print("ALB Name: ",albName,"Arn: ",arn,"SslPolicy: ",listner["SslPolicy"] )
                            response = albs.modify_listener(ListenerArn=listner["ListenerArn"], SslPolicy="ELBSecurityPolicy-TLS-1-2-Ext-2018-06")                            
                            
                except ClientError as e:
                        print("unexpected error: %s" % (e.response))

    if 'NextToken' in All_Albs and All_Albs['NextToken'] is not None:
        All_Albs = albs.describe_load_balancers(NextToken=All_Albs['NextToken'])
    else:
        break;
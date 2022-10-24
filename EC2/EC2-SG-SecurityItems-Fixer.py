#
# Script scans specific SG for Inbound 0.0.0.0/0 or 10.0.0.0/8 IP ranges & fixes it if found.
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import json
import boto3
from botocore.exceptions import ClientError

profile_name='qa'
session = boto3.Session(profile_name=profile_name)

ec2 = session.client('ec2')
my_sec_grp = ec2.describe_security_groups(GroupIds = ['sg-123456789'])
#print(my_sec_grp)
securityGroup = my_sec_grp["SecurityGroups"]
if "IpPermissions" in securityGroup[0]:
    inbounds = securityGroup[0]
    if "IpPermissions" in inbounds:
        #print (securityGroup[0]["GroupName"],securityGroup[0]["GroupId"])
        #print (inbounds["IpPermissions"])
        for rule in inbounds["IpPermissions"]:
            port = 'No Port'
            ipranges = rule["IpRanges"]
            iprotocol = rule["IpProtocol"]
            if "FromPort" in rule:
                port = rule["FromPort"]
            for iprange in ipranges:
                if iprange['CidrIp'] == '0.0.0.0/0' or iprange['CidrIp'] == '10.0.0.0/8':
                    print (securityGroup[0]["GroupName"],securityGroup[0]["GroupId"])
                    #print (inbounds["IpPermissions"])
                    #print(ipranges)
                    print(iprotocol,':',port,':',ipranges)
                    #print(port)
                    
                    print(port)
                    if port == 82:
                        print("response = ec2.revoke_security_group_ingress()")
                        response = ec2.revoke_security_group_ingress(
                                   #CidrIp=iprange['CidrIp'],
                                   #FromPort=port,
                                   GroupId=securityGroup[0]["GroupId"],
                                   IpPermissions=[
                                       {
                                           'FromPort':port,
                                           'ToPort':port,
                                           'IpProtocol':iprotocol,
                                           'IpRanges': [
                                                {
                                                    'CidrIp': iprange['CidrIp'],
                                                    #'Description': 'string'
                                                },
                                            ],
                                       }
                                   ]
                        )
                        response2 = ec2.authorize_security_group_ingress(
                                   #CidrIp=iprange['CidrIp'],
                                   #FromPort=port,
                                   GroupId=securityGroup[0]["GroupId"],
                                   IpPermissions=[
                                       {
                                           'FromPort':port,
                                           'ToPort':port,
                                           'IpProtocol':iprotocol,
                                           'IpRanges': [
                                                {
                                                    'CidrIp': '10.10.0.0/16',
                                                    'Description': 'Allowing CRX IP ranges only'
                                                },
                                            ],
                                       }
                                   ]
                        )
                    print('-----------------------------')
                                                
                            


'''
def lambda_handler(event, context):
    ec2=boto3.client("ec2")
    
    # =============================================check EC2 SG ==========================================================
    All_Ec2 = ec2.describe_instances()
    ec2count = 0
    while True:
        try:
            for reservation in All_Ec2["Reservations"]:
                for instance in reservation['Instances']:
                    if instance["State"]["Name"] == 'running':
                        ec2count = ec2count + 1
                        for securityGroup in instance['SecurityGroups']:
                            comp = 1
                            my_sec_grp = ec2.describe_security_groups(GroupIds = [securityGroup["GroupId"]])
                            securitygroup = my_sec_grp["SecurityGroups"]
                            if "IpPermissions" in securitygroup[0]:
                                inbounds = securitygroup[0]
                                if "IpPermissions" in inbounds:
                                    print (securityGroup["GroupName"] + '-----' + securityGroup["GroupId"])
                                    print (inbounds["IpPermissions"])
                                    for rule in inbounds["IpPermissions"]:
                                        port = 'No Port'
                                        ipranges = rule["IpRanges"]
                                        iprotocol = rule["IpProtocol"]
                                        if "FromPort" in rule:
                                            port = rule["FromPort"]
                                        for iprange in ipranges:
                                            if iprange['CidrIp'] == '0.0.0.0/0' or iprange['CidrIp'] == '10.0.0.0/8':
                                                print (securityGroup["GroupName"] + '-----' + securityGroup["GroupId"])
                                                print (inbounds["IpPermissions"])
                                                print(ipranges)
                                                print(iprotocol)
                                                print(port)
                                                print('-----------------------------')
                                                
                                # if comp == 0:
                                #     print(securityGroup["GroupName"] + securityGroup["GroupId"] + '  EC2 SG Is Not Compliance')
                                #     ('-----------------------------------------------------')
                                # else:
                                #     print(securityGroup["GroupName"] + securityGroup["GroupId"] + '  EC2 SG Is Compliance')
                                # print ('-----------------------------------------------------')  
                    
        except ClientError as e:
                        print("unexpected error: %s" % (e.response))
            
      

        if 'NextToken' in All_Ec2 and All_Ec2['NextToken'] is not None:
            All_Ec2 = ec2.describe_instances()(NextToken=All_Ec2['NextToken'])
        else:
            break;
            
    print ("Ec2Count: " + str(ec2count))
    '''
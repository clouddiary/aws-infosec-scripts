#
# Script fetches EC2 instances & send run commands to execute netstand commands to know IN/Out traffic ports
#
# AWS CLI profile needs to be created on machine where script will run & pass profile name.

import boto3, os, sys, logging, time
from boto3 import Session

session = boto3.Session(profile_name='qa')
region = "us-east-1"
client = session.client('ec2', region_name=region)
ssm_client = session.client('ssm', region_name=region)

# used to do dry_run
testing = os.environ.get('TESTING')
print(f"Testing = {testing}")

# logger
def setup_logger(region):
    data = {'region': region}

    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(region)s] : %(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger = logging.LoggerAdapter(logger, data)
    return logger

# initialize the logger 
logger = setup_logger(region)
instances = client.describe_instances(Filters = [
        {
            'Name': 'instance-state-name', 
            'Values': ['running']
        }
    ])

running_instance = ["i-07ffd19aa5e85d568"]

try:
    logger.warning(f"Executing commands on the following instances:  {','.join(running_instance)}")
    response = ssm_client.send_command(
                InstanceIds=[r for r in running_instance],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': ["sudo chkconfig >> /home/ssm-user/chkconfig.txt","sudo netstat -anp | egrep -i 'listen' | grep -vi ing >> /home/ssm-user/netstat.txt","INS_ID=$(curl http://169.254.169.254/latest/meta-data/instance-id)", "aws s3 cp /home/ssm-user/chkconfig.txt s3://tmgprod-infrastructure-operations/stats/chkconfig/$INS_ID.txt", "aws s3 cp /home/ssm-user/netstat.txt s3://tmgprod-infrastructure-operations/stats/netstat/$INS_ID.txt"]},)
    command_id = response['Command']['CommandId']
    logger.info(f"Command id: {command_id}")
    # for instance in running_instance:
    #     command_invocation_result = ssm_client.get_command_invocation(CommandId=command_id, InstanceId=instance)        
    #     time.sleep(5)   
    #     if(command_invocation_result['ResponseCode'] == -1):
    #         logger.info(f"{command_invocation_result['Status']}")
    #         time.sleep(5)
    #     logger.info(f"{command_invocation_result['Status']}")

except Exception as e:
    logger.error(f"Failed to execute commands on the following instances:{','.join(running_instance)} with error {e}!")

# running_instance = []

# if len(instances['Reservations']) == 0:
#     logger.info(f"No Instances found!")
#     exit()

# for instance in instances['Reservations']:
#     for i in instance['Instances']:
#             running_instance.append(i['InstanceId'])
        
# if testing == "True":
#     logger.info(f"Executing commands on the following instances: {','.join(running_instance)}")
# else:
#     try:
#         logger.warning(f"Executing commands on the following instances:  {','.join(running_instance)}")
#         response = ssm_client.send_command(
#                     InstanceIds=[r for r in running_instance],
#                     DocumentName="AWS-RunShellScript",
#                     Parameters={'commands': ["sudo yum update -y",
#                                              "echo 'File Created by SSM agent!' > text.txt"]},)
#         command_id = response['Command']['CommandId']
#         logger.info(f"Command id: {command_id}")
#         #for instance in running_instance:
#         #command_invocation_result = ssm_client.get_command_invocation(CommandId=command_id, InstanceId=instance)
#         command_invocation_result = ssm_client.get_command_invocation(CommandId=command_id, InstanceId=instance)
#         time.sleep(5)   
#         if(command_invocation_result['ResponseCode'] == -1):
#             logger.info(f"{command_invocation_result['Status']}")
#             time.sleep(5)
#         logger.info(f"{command_invocation_result['Status']}")

#     except Exception as e:
#         logger.error(f"Failed to execute commands on the following instances:{','.join(running_instance)} with error {e}!")
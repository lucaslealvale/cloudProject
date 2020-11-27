# PROJETO DE COMPUTAÇÃO EM NUVEM
# PROFESSOR RAUL IKEDA
# AUTOR: LUCAS LEAL VALE
# TODO

import time
import boto3
from botocore.exceptions import ClientError

def getIP(group, id):
    response = group.describe_instances()
    for a in response['Reservations']:
        for i in a['Instances']:
            if i['InstanceId'] == id:
                if i['State']['Name'] == 'running':
                    return(i['PublicIpAddress'])
        
def getOwner(group,name):
    id_inst_list = []

    response = group.describe_instances()
    for a in response['Reservations']:
        for i in a['Instances']:
            #print(i['State']['Name'])
            if i['State']['Name'] != 'terminated':
                for j in i['Tags']:
                    if j['Value'] == name:
                        id_inst_list.append(i['InstanceId'])
                         
    return(id_inst_list)
                    
def terminate_instance(group,ids):
    
    try:
        group.instances.filter(InstanceIds=[ids]).terminate()
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            print("instancia ja pausada")
            raise

def terminate_AutoScaling_group(client,nameAutoScalig):
    response = client.delete_auto_scaling_group(
        AutoScalingGroupName=nameAutoScalig,
        ForceDelete=True
    )
    return response

def terminate_launch_config(client,name_launch_config):
    response = client.delete_launch_configuration(
        LaunchConfigurationName=name_launch_config
    )
    return response

def terminate_load_balancer(client,name):
    response = client.delete_load_balancer(
    LoadBalancerName= name
    )
    return response

def create_LoadBalancer(group, name,securityGroup):
    response = group.create_load_balancer(
        LoadBalancerName= name,
        Listeners=[
            {
                'Protocol': 'HTTP',
                'LoadBalancerPort': 80,
                'InstancePort': 8080,
            },
        ],
        AvailabilityZones=[
            'us-east-1a','us-east-1b','us-east-1c',
            'us-east-1d' ,'us-east-1e','us-east-1f',
        ],
        SecurityGroups=[
            securityGroup,
        ],
    )
    return response['DNSName']

def check_load_balance(client):
    response = client.describe_load_balancers()
    for i in response['LoadBalancerDescriptions']:
        if(i['LoadBalancerName'] == 'loadbalancelucas1'):
            return(response['LoadBalancerDescriptions'][0]['LoadBalancerName'])

def check_autoScaling(client):
    response = client.describe_auto_scaling_groups()
    for i in response['AutoScalingGroups']:
        if(i['AutoScalingGroupName'] == 'Django-Lucas-AutoScale'):
            return(response['AutoScalingGroups'][0]['AutoScalingGroupName'])
        
def check_launch_config(client):
    response = client.describe_launch_configurations()
    for i in response['LaunchConfigurations']:
        if(i['LaunchConfigurationName'] == 'Django-Lucas-AutoScale'):
            return(response['LaunchConfigurations'][0]['LaunchConfigurationName'])

def get_vpcs(client):
    response = client.describe_vpcs()
    for i in response['Vpcs']:
        return i['VpcId']

def terminate_security_group(client,name):
    response = client.delete_security_group(
    GroupName = name,
    )
    return response

def getSecurityGroups(client,scname):
    response = client.describe_security_groups()
    for i in response['SecurityGroups']:
        if i['GroupName'] == scname:
            return i['GroupName']

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# RESOURCES

ec2_NorthVirginia = boto3.resource('ec2', region_name='us-east-1')
ec2_Ohio = boto3.resource('ec2', region_name='us-east-2')

# CLIENTS

ec2_Ohio_cli = boto3.client('ec2', region_name='us-east-2')
ec2_NorthVirginia_cli = boto3.client('ec2', region_name='us-east-1')

elb = boto3.client('elb',region_name='us-east-1')
autoscalingCli = boto3.client('autoscaling',region_name='us-east-1')

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# PREPARANDO O TERRENO - DELETING PREVIOUS INSTANCES IF EXIST

print("deletando instancias")

myInstancesNorthVirginia = getOwner(ec2_NorthVirginia_cli,'lucas2')
if len(myInstancesNorthVirginia) > 0:
    for i in myInstancesNorthVirginia:
        terminate_instance(ec2_NorthVirginia,i)
    print("Previous NV Instances terminated")
else: 
    print("There where no instances to terminate in NV")

myInstancesOhio = getOwner(ec2_Ohio_cli,'lucas1')
if len(myInstancesOhio) > 0:
    for j in myInstancesOhio:
        terminate_instance(ec2_Ohio,j)
    print("Previous Ohio Instances terminated")
else: 
    print("There where no instances to terminate in Ohio")

check_load=check_load_balance(elb)
if(check_load != None ):
    terminate_load_balancer(elb,check_load)

check_auto = check_autoScaling(autoscalingCli)
if(check_auto != None ):
    terminate_AutoScaling_group(autoscalingCli,check_auto)

check_launch = check_launch_config(autoscalingCli)
if(check_launch != None ):
    terminate_launch_config(autoscalingCli,check_launch)

time.sleep(180)

mySecurityGroupOhio = getSecurityGroups(ec2_Ohio_cli,'securityOhioLucas')
mySecurityGroupNV = getSecurityGroups(ec2_NorthVirginia_cli,'securityVirginiaLucas')
print(mySecurityGroupNV)
print(mySecurityGroupOhio)

if(mySecurityGroupNV != None ):
    terminate_security_group(ec2_NorthVirginia_cli,mySecurityGroupNV)
if(mySecurityGroupOhio != None ):
    terminate_security_group(ec2_Ohio_cli,mySecurityGroupOhio)

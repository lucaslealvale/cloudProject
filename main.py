# PROJETO DE COMPUTAÇÃO EM NUVEM
# PROFESSOR RAUL IKEDA
# AUTOR: LUCAS LEAL VALE
# TODO

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# REFERENCIAS:
# CREATE POSTGRESS USER ------>https://stackoverflow.com/questions/18715345/how-to-create-a-user-for-postgres-from-the-command-line-for-bash-automation
# COMO EDITAR ARQUIVOS VIA COMMAND LINE  -----> https://askubuntu.com/questions/148421/how-to-programmatically-edit-a-file-using-only-terminal 
# boto3 documentation ---> https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
# aulas e roteiros da materia de cloud
# aspas dentro de aspas dentrro de aspas ----> https://stackoverflow.com/questions/3834839/how-can-i-escape-a-double-quote-inside-double-quotes
# CREATE DATABASE POSTGRES -----> https://stackoverflow.com/questions/30641512/create-database-from-command-line
# edit file in the last line----->https://unix.stackexchange.com/questions/20573/sed-insert-text-after-the-last-line
# EDIT FILE PYTHON ---> https://www.kite.com/python/answers/how-to-edit-a-specific-line-in-a-text-file-in-python
#-----------------------------------------------------------------------------------------------------------------------------------------------------
import time
import boto3
from botocore.exceptions import ClientError

def reboot(group, id_instance):
    try:
        group.reboot_instances(InstanceIds=[id_instance], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            print("You don't have permission to reboot instances.")
            raise

    try:
        response = group.reboot_instances(InstanceIds=[id_instance], DryRun=False)
        print('Success', response)
    except ClientError as e:
        print('Error', e)

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
                    
def create_instance(group,ami, mincount, maxcount, machine, owner,name,security_group, startUP):
    response = group.run_instances(ImageId=ami, MinCount=mincount, MaxCount=maxcount,SecurityGroupIds=[security_group,], InstanceType = machine, TagSpecifications=[
        {
            'ResourceType':'instance',
            'Tags': [
                {
                    'Key': 'owner',
                    'Value': owner
                },
                {
                    'Key': 'Name',
                    'Value': name
                },
            ]
        },
    ], UserData = startUP
    )
    return (response['Instances'][0]['InstanceId'])

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

def create_image(group,instID):   
    response = group.create_image(
        Description='imagem django lucas',
        InstanceId=instID,
        Name='django-lucas',
    )
    return(response['ImageId'])

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

def create_autoScalingGroup(group, instDjango, loadbalance, owner,name):
    response = group.create_auto_scaling_group(
        AutoScalingGroupName='Django-Lucas-AutoScale',

        InstanceId=instDjango,
        MinSize=1,
        MaxSize=5,
        DesiredCapacity=1,
        DefaultCooldown=300,
        LoadBalancerNames=[
            loadbalance,
        ],Tags = [
                {
                    'Key': 'owner',
                    'Value': owner
                },
                {
                    'Key': 'Name',
                    'Value': name
                },
                
            ],
    )
    return response

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

def create_security_group(client,name,vpc,owner):
    response = client.create_security_group(
    Description='Security group de Lucas',
    GroupName=name,
    VpcId=vpc,
    TagSpecifications=[
        {
            'ResourceType': 'security-group',
            'Tags': [
                {
                    'Key': 'owner',
                    'Value': owner
                },
            ]
        },
    ],
    )
    return response['GroupId']

def terminate_security_group(client,name):
    response = client.delete_security_group(
    GroupName = name,
    )
    return response

def gates(client,id):
    response = client.authorize_security_group_ingress(
    GroupId=id,
    IpPermissions=[
        {
            'FromPort': 8080,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'string'
                },
            ],
            'ToPort': 8080,
            
        },
        {
            'FromPort': 5432,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'string'
                },
            ],
            'ToPort': 5432,
            
        },
        {
            'FromPort': 80,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'string'
                },
            ],
            'ToPort': 80,
            
        },
    ],)
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

mySecurityGroupOhio = getSecurityGroups(ec2_Ohio_cli,'securityOhioLucas')
mySecurityGroupNV = getSecurityGroups(ec2_NorthVirginia_cli,'securityVirginiaLucas')

time.sleep(60)

if(mySecurityGroupNV != None ):
    terminate_security_group(ec2_NorthVirginia_cli,mySecurityGroupNV)
if(mySecurityGroupOhio != None ):
    terminate_security_group(ec2_Ohio_cli,mySecurityGroupOhio)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#Security Groups

vpcOhio = get_vpcs(ec2_Ohio_cli)
vpcNV   = get_vpcs(ec2_NorthVirginia_cli)

security_group_NorthVirginia = create_security_group(ec2_NorthVirginia_cli,'securityVirginiaLucas',vpcNV,'lucas')
security_group_Ohio = create_security_group(ec2_Ohio_cli,'securityOhioLucas',vpcOhio,'lucas')
portsNV = gates(ec2_NorthVirginia_cli, security_group_NorthVirginia)
portsOhio = gates(ec2_Ohio_cli, security_group_Ohio)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#CREATING INSTANCE POSTGRESQL

postgres = create_instance(ec2_Ohio_cli, 'ami-0dd9f0e7df0f0a138',1,1,'t2.micro', 'lucas1','postgres-LUCAS','securityOhioLucas', open('startup.sh').read())
print("Subindo Postgres...")

waiter = ec2_Ohio_cli.get_waiter('instance_status_ok')
waiter.wait(InstanceIds=[
        postgres,
    ],)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# SELECIONANDO IP do PostgreSQL PARA O DJANGO

ip4django = getIP(ec2_Ohio_cli, postgres)
start = open("startupNV.sh", "r")
lines = start.readlines()
lines[6] = ("sudo sed -i 's/node1/{0}/g' /home/ubuntu/tasks/portfolio/settings.py\n").format(ip4django)
start = open("startupNV.sh", "w")
start.writelines(lines)
start.close()

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREATING INSTANCES DJANGO

django = create_instance(ec2_NorthVirginia_cli, 'ami-0817d428a6fb68645',1,1,'t2.micro', 'lucas2','django-LUCAS','securityVirginiaLucas', open('startupNV.sh').read())
print("Subindo Django...")

waiter = ec2_NorthVirginia_cli.get_waiter('instance_status_ok')
waiter.wait(InstanceIds=[
        django,
    ],)

django_IP = getIP(ec2_NorthVirginia_cli, django)
print("Para acessar o DB online via django original-> http://{0}:8080/admin".format(django_IP))

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREATING LOAD BALANCE

loadbalance = create_LoadBalancer(elb, 'loadbalancelucas1',security_group_NorthVirginia)
print("loadbalancer")
print("Para acessar o DB via load banlancer online -> http://{0}:80/admin".format(loadbalance))

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREATING AutoScalingGroup

autoscaling = create_autoScalingGroup(autoscalingCli,django,'loadbalancelucas1', 'lucas2','lucas2')
print("autoscaling")
check_autoScaling(autoscalingCli)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
print("em cerca de 10 minutos o load balancer estara online!")
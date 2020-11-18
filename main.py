# PROJETO DE COMPUTAÇÃO EM NUVEM
# PROFESSOR RAUL IKEDA
# AUTOR: LUCAS LEAL VALE

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
                    
def getOwner(group):
    response = group.describe_instances()
    for a in response['Reservations']:
        for i in a['Instances']:
            if i['KeyName'] == 'lucask':
                if i['State']['Name'] == 'running':
                    return(i['InstanceId'])
                    
                    
def create_instance(group,ami, mincount, maxcount, machine, owner,name, myKey,security_group, startUP):
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
    ], KeyName=myKey, UserData = startUP
    )
    return (response['Instances'][0]['InstanceId'])

def stop_instance(group,ids):
    
    try:
        group.instances.filter(InstanceIds=[ids]).terminate()
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            print("instancia ja pausada")
            raise

def  check_instances(group):
    id_inst_list = []
    instances = group.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])


    for instance in instances:
            id_inst_list.append(instance.id)
            print(instance.id, instance.instance_type)

    return(id_inst_list)

def create_image(group,instID):   
    response = group.create_image(
        Description='imagem django lucas',
        InstanceId=instID,
        Name='django-lucas',
    )
    return(response['ImageId'])


def create_LoadBalancer(group, name):
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
            'sg-017d1eb931b861ac5',
        ],
    )
    return response

def create_autoScalingGroup(group, instDjango, loadbalance):
    response = group.create_auto_scaling_group(
        AutoScalingGroupName='Django-Lucas-AutoScale',

        InstanceId=instDjango,
        MinSize=1,
        MaxSize=5,
        DesiredCapacity=1,
        DefaultCooldown=300,
        LoadBalancerNames=[
            loadbalance,
        ],
    )
    print(response)
    return response

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# RESOURCES
ec2_NorthVirginia = boto3.resource('ec2', region_name='us-east-1')
ec2_Ohio = boto3.resource('ec2', region_name='us-east-2')
# CLIENTS
ec2_Ohio_cli = boto3.client('ec2', region_name='us-east-2')
ec2_NorthVirginia_cli = boto3.client('ec2', region_name='us-east-1')

elb = boto3.client('elb',region_name='us-east-1')
autoscaling = boto3.client('autoscaling',region_name='us-east-1')

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREATING INSTANCE POSTGRESQL
postgres = create_instance(ec2_Ohio_cli, 'ami-0dd9f0e7df0f0a138',1,1,'t2.micro', 'lucas','postgres-LUCAS','lucask','sg-e4539d98', open('startup.sh').read())

print("Subindo Postgres...")

waiter = ec2_Ohio_cli.get_waiter('instance_status_ok')
waiter.wait(InstanceIds=[
        postgres,
    ],)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# SELECIONANDO IP PARA O DJANGO
ip4django = getIP(ec2_Ohio_cli, postgres)
start = open("startupNV.sh", "r")
lines = start.readlines()
lines[6] = ("sudo sed -i 's/node1/{0}/g' /home/ubuntu/tasks/portfolio/settings.py\n").format(ip4django)
start = open("startupNV.sh", "w")
start.writelines(lines)
start.close()

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREATING INSTANCES DJANGO
django = create_instance(ec2_NorthVirginia_cli, 'ami-0817d428a6fb68645',1,1,'t2.micro', 'lucas','django-LUCAS','lucaslealk','sg-017d1eb931b861ac5', open('startupNV.sh').read())
print("Subindo Django...")

waiter = ec2_NorthVirginia_cli.get_waiter('instance_status_ok')
waiter.wait(InstanceIds=[
        django,
    ],)

django_IP = getIP(ec2_NorthVirginia_cli, django)
print("Para acessar o DB online -> http://{0}:8080/admin".format(django_IP))

# print('criando image...')
# djangoImageId = create_image(ec2_NorthVirginia_cli,django)

# waiter = ec2_NorthVirginia_cli.get_waiter('image_available')
# waiter.wait(
#     ImageIds=[
#         djangoImageId,]
# )
# print("imagem criada!")

# stop_instance(ec2_NorthVirginia, django)


#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREATING LOAD BALANCE
loadbalance = create_LoadBalancer(elb, 'loadbalancelucas1')
print("pararatimbum")
autoscaling = create_autoScalingGroup(autoscaling,django,'loadbalancelucas1')
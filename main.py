# PROJETO DE COMPUTAÇÃO EM NUVEM
# PROFESSOR RAUL IKEDA
# AUTOR: LUCAS LEAL VALE
# REFERENCIAS:
# CREATE POSTGRESS USER ------>https://stackoverflow.com/questions/18715345/how-to-create-a-user-for-postgres-from-the-command-line-for-bash-automation
# COMO EDITAR ARQUIVOS VIA COMMAND LINE  -----> https://askubuntu.com/questions/148421/how-to-programmatically-edit-a-file-using-only-terminal 
# boto3 documentation ---> https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
# aulas e roteiros da materia de cloud
# aspas dentro de aspas dentrro de aspas ----> https://stackoverflow.com/questions/3834839/how-can-i-escape-a-double-quote-inside-double-quotes
# CREATE DATABASE POSTGRES -----> https://stackoverflow.com/questions/30641512/create-database-from-command-line
# edit file in the last line----->https://unix.stackexchange.com/questions/20573/sed-insert-text-after-the-last-line
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


def describe_instance(group):
    response = group.describe_instances()
    print(response)

def create_instance(group,ami, mincount, maxcount, machine, owner,name, myKey,security_group, startUP):
    group.create_instances(ImageId=ami, MinCount=mincount, MaxCount=maxcount,SecurityGroupIds=[security_group,], InstanceType = machine, TagSpecifications=[
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

    

def stop_instance(group,ids):
    
    try:
        group.instances.filter(InstanceIds=ids).terminate()
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            print("instancia ja pausada")
            raise

def  check_instances(group):

    instances = group.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    for instance in instances:

        print(instance.id, instance.instance_type)
      

ec2 = boto3.resource('ec2')

ec2_NorthVirginia = boto3.resource('ec2', region_name='us-east-1')
ec2_Ohio = boto3.resource('ec2', region_name='us-east-2')

#ubuntu 18 instance type NORTH VIRGINIA - ami-0817d428a6fb68645 
#ubuntu 18 instance type OHIO - ami-0dd9f0e7df0f0a138 
#mockzada
user_data = '''#!/bin/bash
echo 'test' > /tmp/hello'''




create_instance(ec2_Ohio, 'ami-0dd9f0e7df0f0a138',1,1,'t2.micro', 'lucas','postgres','lucask','sg-e4539d98', open('startup.sh').read())


create_instance(ec2_NorthVirginia, 'ami-0817d428a6fb68645',1,1,'t2.micro', 'lucas','ORM_jango','lucaslealk','sg-017d1eb931b861ac5', open('startupNV.sh').read())

check_instances(ec2)


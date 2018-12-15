"""
Create new databases and users in the shared MariaDB instance
for provisioning of new Wordpress Installations

Database name and User name are equal to CloudFormation Stack Name
and will be deleted along with the Stack
"""
import os
import json
from uuid import uuid4

import requests
import mysql.connector as mariadb

config = {
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_ENDPOINT'],
    'use_pure': True
}


def handler(event, context):
    """Manages databases and users for Wordpress application in MariaDB"""
    print(f"Function ARN: {context.invoked_function_arn}")
    print(f"Event: {json.dumps(event)}")

    try:
        global mariadb_connection, cursor
        mariadb_connection = mariadb.connect(**config)
        cursor = mariadb_connection.cursor()
    except mariadb.Error as err:
        print(f"Error: {err}")
        send_response(
            event, status='FAILED', reason="Error connecting to database")

    try:
        request_type = event['RequestType']
        # stack_name is used for both database and user name
        stack_name = event['ResourceProperties']['StackName'].replace('-', '_')

        # if deleting stack, delete the database and user for this stack
        if request_type == 'Delete':
            print('Deleting database and user...')
            return delete_database(event, stack_name)
        # otherwise create database and user for this stack
        print('Creating database and user...')
        return create_database(event, stack_name)

    except KeyError as err:
        print(f"Error: {err}")
        send_response(event, status='FAILED', reason="Error accessing data")
    finally:
        mariadb_connection.close()


def create_database(event, stack_name):
    """Create new database and user for Wordpress application"""
    try:
        vpc_mask = os.environ['VPC_CIDR'][:-2] + "255.255.0.0"
        password = str(uuid4()).replace('-', '')
        # using stack_name prevents against SQL injections
        # as it only allows alphanumerical characters and "-"
        # and the commands fail with %s param substitution because of quotes
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {stack_name}")
        cursor.execute(
            "INSERT INTO mysql.user (User,Host,authentication_string,ssl_cipher,x509_issuer, x509_subject) VALUES(%s, %s, PASSWORD(%s),'','','')",
            (stack_name, vpc_mask, password))
        cursor.execute("FLUSH PRIVILEGES")
        cursor.execute(
            f"GRANT ALL PRIVILEGES ON {stack_name}.* TO %s@%s IDENTIFIED BY %s",
            (stack_name, vpc_mask, password))
        cursor.execute("FLUSH PRIVILEGES")
        mariadb_connection.commit()

        response_data = {
            'DB_ENDPOINT': os.environ['DB_ENDPOINT'],
            'DB_NAME': stack_name,
            'DB_USER': stack_name,
            'DB_PASSWORD': password
        }

        send_response(event, status='SUCCESS', data=response_data)

    except mariadb.Error as err:
        print(f"Error: {err}")
        send_response(
            event, status='FAILED', reason="Error creating database and user")
    finally:
        mariadb_connection.close()


def delete_database(event, stack_name):
    """Delete existing database and user for Wordpress application"""
    try:
        vpc_mask = os.environ['VPC_CIDR'][:-2] + "255.255.0.0"
        # using stack_name prevents against SQL injections
        # as it only allows alphanumerical characters and "-"
        # and the commands fail with %s param substitution because of single quotes
        cursor.execute(f"DROP DATABASE IF EXISTS {stack_name}")
        cursor.execute("DROP USER IF EXISTS %s@%s", (stack_name, vpc_mask))
        mariadb_connection.commit()

        send_response(event, status='SUCCESS')

    except mariadb.Error as err:
        print(f"Error: {err}")
        send_response(
            event, status='FAILED', reason="Error deleting database or user")
    finally:
        mariadb_connection.close()


def send_response(event, status, reason="", data=None):
    """Send a Success or Failure event back to CFN stack"""
    if data is None:
        data = {}

    if status == 'FAILED':
        print(f'FAILED: {reason}')

    payload = {
        'StackId': event['StackId'],
        'Status': status,
        'Reason': reason,
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'PhysicalResourceId':
        event.get('PhysicalResourceId', None)
        or event['LogicalResourceId'] + str(uuid4()),
        'Data': data
    }

    json_payload = json.dumps(payload)

    print(f"Sending {json_payload} to {event['ResponseURL']}")
    requests.put(event['ResponseURL'], data=json_payload)

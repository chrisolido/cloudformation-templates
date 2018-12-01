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

def handler(event, context):
    db_endpoint = os.environ['DB_ENDPOINT']
    db_name = os.environ['DB_NAME']
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']

    response_data = {
        'DB_ENDPOINT': db_endpoint,
        'DB_NAME': db_name,
        'DB_USER': db_user,
        'DB_PASSWORD': db_password
    }

    send_response(event, status='SUCCESS', data=response_data)


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
        'PhysicalResourceId': event['LogicalResourceId'] + str(uuid4()),
        'Data': data
    }

    json_payload = json.dumps(payload)

    print(f"Sending {json_payload} to {event['ResponseURL']}")
    requests.put(event['ResponseURL'], data=json_payload)
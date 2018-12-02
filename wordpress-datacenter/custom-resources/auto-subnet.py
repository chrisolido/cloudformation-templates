"""
Allocate Subnet CIDR within a VPC CIDR Block

Uses DynamoDB for persistence of allocated CIDR
"""
import os
import json
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Key, Attr

import requests
from netaddr import IPNetwork

vpc_cidr = os.environ['VPC_CIDR']
table_name = os.environ['DYNAMO_TABLE_NAME']
region = os.environ['DYNAMO_REGION']

dynamodb_table = boto3.resource(
    'dynamodb', region_name=region).Table(table_name)


def handler(event, context):
    """Allocate 2 IP ranges from a VPC CIDR Block"""
    print(f"Function ARN: {context.invoked_function_arn}")
    print(f"Event: {json.dumps(event)}")

    stack_id = event['StackId']
    request_type = event['RequestType']

    # if deleting stack, remove the subnet allocations for this stack
    if request_type == 'Delete':
        print("Deleting Subnets...")
        return delete_subnets(event, stack_id)
    # otherwise allocate subnets for this stack
    print("Allocating Subnets...")
    return allocate_subnets(event, stack_id)


def delete_subnets(event, stack_id):
    """Delete any subnets in DynamoDB for stack"""
    try:
        response = dynamodb_table.scan(
            FilterExpression=Attr('StackId').eq(stack_id))

        print('Deleting items...')
        for item in response['Items']:
            print(item)
            dynamodb_table.delete_item(Key={'Cidr': item['Cidr']})

        send_response(event, status='SUCCESS')

    except Exception as err:
        print(f"Error: {err}")
        send_response(
            event,
            status='FAILED',
            reason='Failed to delete allocated subnets in DynamoDB')


def allocate_subnets(event, stack_id):
    """Allocate subnets in DynamoDB for stack"""
    ipnet = IPNetwork(vpc_cidr)
    subnet_mask = 24
    subnets = ipnet.subnet(subnet_mask)
    subnets_allocated = 0
    number_to_allocate = 2

    try:
        for subnet in subnets:
            if subnets_allocated == number_to_allocate:
                break
            if cidr_is_reserved(subnet):
                continue
            if cidr_is_in_table(subnet):
                continue

            use_subnet(subnet, stack_id)  # store the allocation in the DB
            print(f"Subnets Allocated {subnets_allocated} - {str(subnet)}")
            subnets_allocated += 1

        # read all the subnets for this stack from table
        response = dynamodb_table.query(
            IndexName='StackCidrRanges',
            KeyConditionExpression=Key('StackId').eq(stack_id))

        if len(response['Items']) < number_to_allocate:
            send_response(
                event,
                status='FAILED',
                reason=
                f"Couldn't obtain {number_to_allocate} CIDR for stack from DynamoDB query"
            )
            return

        print('Response from DynamoDB: ')
        for item in response['Items']:
            print(item)

        response_data = {
            'AppPublicCIDR1': response['Items'][0]['Cidr'],
            'AppPublicCIDR2': response['Items'][1]['Cidr'],
        }
        send_response(event, status='SUCCESS', data=response_data)

    except Exception as err:
        send_response(event, status='FAILED', reason="Failed allocate subnets")
        print(f"Error: {err}")


def use_subnet(cidr, stack_id):
    """Add the subnet to DynamoDB"""
    cidr = str(cidr)
    dynamodb_table.put_item(Item={
        'Cidr': cidr,
        'StackId': str(stack_id),
    })


def cidr_is_in_table(cidr):
    """Check if the CIDR is already allocated """
    cidr = str(cidr)
    response = dynamodb_table.query(
        KeyConditionExpression=Key('Cidr').eq(cidr))
    items = response['Items']

    return len(items) > 0


def cidr_is_reserved(cidr):
    """Check if CIDR is already reserved"""
    cidr = str(cidr)
    reserved_cidrs = json.loads(os.getenv('RESERVED_CIDRS', '[]'))

    return cidr in reserved_cidrs


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

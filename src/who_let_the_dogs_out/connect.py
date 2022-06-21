import time
from os import getenv

import boto3

dynamodb_client = boto3.client('dynamodb')


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    username = event['requestContext']['authorizer']['username']
    __add_connection_id(connection_id, username)

    return {
        'statusCode': 200,
        'body': 'Connected!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }


def __add_connection_id(connection_id, username):
    two_hours_in_seconds = 2 * 60 * 60
    time_to_live = int(time.time()) + two_hours_in_seconds
    dynamodb_client.put_item(
        TableName=getenv('CONNECTION_TABLE_NAME'),
        Item={
            'connection_id': {'S': connection_id},
            'username': {'S': username},
            'ttl': {'N': str(time_to_live)}
        }
    )

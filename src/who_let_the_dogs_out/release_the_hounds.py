import json
import time
from os import getenv

import boto3
from botocore.exceptions import ClientError

from src.who_let_the_dogs_out.dog_message import DogMessage

dynamodb_client = boto3.client('dynamodb')
apigateway_client = boto3.client('apigatewaymanagementapi', endpoint_url=getenv("ENDPOINT_URL"))


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    owner_id = json.loads(event['body'])['data']
    __add_dog(connection_id, owner_id)
    return {
        'statusCode': 200,
        'body': 'Added Dog!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }


def __add_dog(connection_id, owner_id):
    thirty_minutes_in_seconds = 30 * 60
    time_to_live = int(time.time()) + thirty_minutes_in_seconds
    dynamodb_client.put_item(
        TableName=getenv('DOG_TABLE_NAME'),
        Item={
            'owner_id': {'S': owner_id},
            'ttl': {'N': str(time_to_live)}
        }
    )
    __notify_connections(connection_id, DogMessage(owner_id, time_to_live))


def __notify_connections(connection_id, dog_message):
    connections = __get_current_connections(connection_id)
    message_payload = json.dumps([dog_message.get_payload()]).encode('utf-8')
    for connection in connections:
        try:
            apigateway_client.post_to_connection(Data=message_payload, ConnectionId=connection)
        except ClientError:
            print(f'Error sending to connection {connection}')


def __get_current_connections(connection_id):
    scan_results = dynamodb_client.scan(
        TableName=getenv('CONNECTION_TABLE_NAME'),
        ProjectionExpression='connection_id'
    )

    connection_ids = map(lambda item: item['connection_id']['S'], scan_results['Items'])

    return filter(lambda candidate_connection: connection_id != candidate_connection, connection_ids)

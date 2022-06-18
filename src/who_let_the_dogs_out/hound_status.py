import json
from os import getenv

import boto3

from src.who_let_the_dogs_out.dog_message import DogMessage

dynamodb_client = boto3.client('dynamodb')
apigateway_client = boto3.client('apigatewaymanagementapi',
                                 endpoint_url=getenv("ENDPOINT_URL").replace('wss', 'https', 1))


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    __post_current_state_to_connection(connection_id)

    return {
        'statusCode': 200,
        'body': 'Success!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }


def __post_current_state_to_connection(connection_id):
    scan_results = dynamodb_client.scan(TableName=getenv('DOG_TABLE_NAME'))

    dog_messages = list(
        map(lambda item: DogMessage(item['owner_id']['S'], item['ttl']['N']).get_payload(), scan_results['Items'])
    )
    message_payload = json.dumps(dog_messages).encode('utf-8')
    apigateway_client.post_to_connection(Data=message_payload, ConnectionId=connection_id)

from os import getenv

import boto3

dynamodb_client = boto3.client('dynamodb')


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    __remove_connection_id(connection_id)
    return {
        'statusCode': 200,
        'body': 'Disconnected!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }


def __remove_connection_id(connection_id):
    dynamodb_client.delete_item(
        TableName=getenv('CONNECTION_TABLE_NAME'),
        Key={
            'connection_id': {'S': connection_id}
        }
    )

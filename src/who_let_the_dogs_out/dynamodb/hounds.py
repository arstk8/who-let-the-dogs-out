from os import getenv

import boto3
from boto3.dynamodb.conditions import Key

from src.who_let_the_dogs_out.model.dog_message import DogMessage

dynamodb_client = boto3.resource('dynamodb')
dog_table = dynamodb_client.Table(getenv('DOG_TABLE_NAME'))


def get_dogs_out_in_neighbor_group(neighbor_group):
    query_results = dog_table.query(
        KeyConditionExpression=Key('neighbor_group').eq(neighbor_group)
    )

    return set(
        map(
            lambda item: DogMessage(item['username'], item['ttl']),
            query_results['Items']
        )
    )


def add_dog(username, neighbor_group, time_to_live):
    dog_table.put_item(
        Item={
            'neighbor_group': neighbor_group,
            'username': username,
            'ttl': time_to_live
        }
    )

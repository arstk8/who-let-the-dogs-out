
import os
import boto3
from boto3.dynamodb.conditions import Key

from src.who_let_the_dogs_out.model.dog_message import DogMessage


class Hounds:

    def __init__(self):
        dynamodb_client = boto3.resource('dynamodb')
        self.dog_table = dynamodb_client.Table(os.getenv('DOG_TABLE_NAME'))

    def get_dogs_out_in_neighbor_group(self, neighbor_group):
        query_results = self.dog_table.query(
            KeyConditionExpression=Key('neighbor_group').eq(neighbor_group)
        )

        return list(
            map(
                lambda item: DogMessage(item['username'], item['ttl']),
                query_results['Items']
            )
        )

    def add_dog(self, username, neighbor_group, time_to_live):
        self.dog_table.put_item(
            Item={
                'neighbor_group': neighbor_group,
                'username': username,
                'ttl': time_to_live
            }
        )

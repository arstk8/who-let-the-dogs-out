import time

import os

import boto3
from boto3.dynamodb.conditions import Key


class Users:

    def __init__(self):
        dynamodb_client = boto3.resource('dynamodb')
        self.users_table = dynamodb_client.Table(os.getenv('USERS_TABLE_NAME'))

    def add_user(self, neighbor_group, username):
        thirty_days_in_seconds = 30 * 24 * 60 * 60
        time_to_live = int(time.time()) + thirty_days_in_seconds

        self.users_table.put_item(
            Item={
                'neighbor_group': neighbor_group,
                'username': username,
                'ttl': time_to_live
            }
        )

    def get_users_in_neighbor_group(self, neighbor_group):
        query_results = self.users_table.query(
            KeyConditionExpression=Key('neighbor_group').eq(neighbor_group),
            ProjectionExpression='username'
        )

        return list(map(lambda item: item['username'], query_results['Items']))

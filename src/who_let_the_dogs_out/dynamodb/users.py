import time
from os import getenv

import boto3
from boto3.dynamodb.conditions import Key

dynamodb_client = boto3.resource('dynamodb')
users_table = dynamodb_client.Table(getenv('USERS_TABLE_NAME'))


def add_user(neighbor_group, username):
    thirty_days_in_seconds = 30 * 24 * 60 * 60
    time_to_live = int(time.time()) + thirty_days_in_seconds

    users_table.put_item(
        Item={
            'neighbor_group': neighbor_group,
            'username': username,
            'ttl': time_to_live
        }
    )


def get_users_in_neighbor_group(neighbor_group):
    query_results = users_table.query(
        KeyConditionExpression=Key('neighbor_group').eq(neighbor_group),
        ProjectionExpression='username'
    )

    return list(map(lambda item: item['username'], query_results['Items']))

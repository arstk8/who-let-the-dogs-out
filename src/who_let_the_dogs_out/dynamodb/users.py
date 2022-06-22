from os import getenv

import boto3
from boto3.dynamodb.conditions import Key

dynamodb_client = boto3.resource('dynamodb')
users_table = dynamodb_client.Table(getenv('USERS_TABLE_NAME'))


def get_users_in_neighbor_group(neighbor_group):
    query_results = users_table.query(
        KeyConditionExpression=Key('neighbor_group').eq(neighbor_group),
        ProjectionExpression='username'
    )

    return list(map(lambda item: item['username'], query_results['Items']))

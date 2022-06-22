import time
from os import getenv

import boto3
from boto3.dynamodb.conditions import Attr

dynamodb_client = boto3.resource('dynamodb')
connection_table = dynamodb_client.Table(getenv('CONNECTION_TABLE_NAME'))


def add_connection_id(connection_id, neighbor_group):
    two_hours_in_seconds = 2 * 60 * 60
    time_to_live = int(time.time()) + two_hours_in_seconds
    connection_table.put_item(
        Item={
            'connection_id': connection_id,
            'neighbor_group': neighbor_group,
            'ttl': time_to_live
        }
    )


def remove_connection_id(connection_id):
    connection_table.delete_item(
        Key={
            'connection_id': connection_id
        }
    )


def get_current_connections(connection_id, neighbor_group):
    scan_items = []

    scan_results = connection_table.scan(
        ProjectionExpression='connection_id',
        FilterExpression=Attr('connection_id').ne(connection_id) & Attr('neighbor_group').eq(neighbor_group)
    )
    scan_items.extend(scan_results['Items'])

    while 'LastEvaluatedKey' in scan_results:
        scan_results = connection_table.scan(
            ProjectionExpression='connection_id',
            FilterExpression=Attr('connection_id').ne(connection_id) & Attr('neighbor_group').eq(neighbor_group),
            ExclusiveStartKey=scan_results['LastEvaluatedKey']
        )
        scan_items.extend(scan_results['Items'])

    return list(map(lambda connection: connection['connection_id'], scan_items))

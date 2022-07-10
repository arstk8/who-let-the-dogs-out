import os
import time

import boto3
from boto3.dynamodb.conditions import Attr, Key


class Connections:

    def __init__(self):
        dynamodb_client = boto3.resource('dynamodb')
        self.connection_table = dynamodb_client.Table(os.getenv('CONNECTION_TABLE_NAME'))

    def add_connection_id(self, connection_id, neighbor_group, username):
        two_hours_in_seconds = 2 * 60 * 60
        time_to_live = int(time.time()) + two_hours_in_seconds
        self.connection_table.put_item(
            Item={
                'connection_id': connection_id,
                'neighbor_group': neighbor_group,
                'username': username,
                'ttl': time_to_live
            }
        )

    def remove_connection_id(self, connection_id):
        self.connection_table.delete_item(
            Key={
                'connection_id': connection_id
            }
        )

    def get_connection_data(self, connection_id):
        query_results = self.connection_table.query(
            KeyConditionExpression=Key('connection_id').eq(connection_id)
        )

        if query_results['Count'] <= 0:
            return None

        item = query_results['Items'][0]
        return {'neighborGroup': item['neighbor_group'], 'username': item['username']}

    def get_current_connections(self, connection_id, neighbor_group):
        scan_items = []

        scan_results = self.connection_table.scan(
            ProjectionExpression='connection_id',
            FilterExpression=Attr('neighbor_group').eq(neighbor_group)
        )
        scan_items.extend(scan_results['Items'])

        while 'LastEvaluatedKey' in scan_results:
            scan_results = self.connection_table.scan(
                ProjectionExpression='connection_id',
                FilterExpression=Attr('neighbor_group').eq(neighbor_group),
                ExclusiveStartKey=scan_results['LastEvaluatedKey']
            )
            scan_items.extend(scan_results['Items'])

        return list(map(lambda connection: connection['connection_id'], scan_items))

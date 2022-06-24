import os

import boto3
import simplejson as json
from botocore.exceptions import ClientError


class Notifier:

    def __init__(self):
        self.apigateway_client = boto3.client('apigatewaymanagementapi',
                                              endpoint_url=os.getenv('ENDPOINT_URL').replace('wss', 'https', 1))

    def notify_connections(self, connections, payload):
        encoded_payload = json.dumps(payload, use_decimal=True).encode('utf-8')
        for connection in connections:
            try:
                self.apigateway_client.post_to_connection(Data=encoded_payload, ConnectionId=connection)
            except ClientError:
                print(f'Error sending to connection {connection}')

from decimal import Decimal
from unittest.mock import call

from botocore.exceptions import ClientError

from src.who_let_the_dogs_out.api_gateway.notifier import Notifier
from test.who_let_the_dogs_out.common_fixtures import AwsFixtures, BasicPythonFixtures


class TestHandler(AwsFixtures, BasicPythonFixtures):

    def test_notify_single_connection(self, apigateway_client):
        connection_id = 'some connection'
        Notifier().notify_connections(
            [connection_id],
            [{'someKey': 'someValue'}]
        )

        apigateway_client.post_to_connection.assert_called_once_with(
            Data='[{"someKey": "someValue"}]'.encode('utf-8'),
            ConnectionId=connection_id
        )

    def test_notify_multiple_connections(self, apigateway_client):
        connection_ids = ['some connection', 'some other connection']
        Notifier().notify_connections(
            connection_ids,
            [{'someKey': 'someValue'}]
        )

        assert apigateway_client.post_to_connection.call_args_list == [
            call(
                Data='[{"someKey": "someValue"}]'.encode('utf-8'),
                ConnectionId=connection_ids[0]
            ),
            call(
                Data='[{"someKey": "someValue"}]'.encode('utf-8'),
                ConnectionId=connection_ids[1]
            )
        ]

    def test_notify_with_object_containing_decimal(self, apigateway_client):
        connection_id = 'some connection'
        Notifier().notify_connections(
            [connection_id],
            [{'someKey': Decimal(1234)}]
        )

        apigateway_client.post_to_connection.assert_called_once_with(
            Data='[{"someKey": 1234}]'.encode('utf-8'),
            ConnectionId=connection_id
        )

    def test_failure_doesnt_affect_subsequent_connections(self, apigateway_client):
        connection_ids = ['some connection', 'some other connection']
        apigateway_client.post_to_connection.side_effect = [ClientError({'get': 'some error'}, 'some operation'), None]

        Notifier().notify_connections(
            connection_ids,
            [{'someKey': 'someValue'}]
        )

        assert apigateway_client.post_to_connection.call_args_list == [
            call(
                Data='[{"someKey": "someValue"}]'.encode('utf-8'),
                ConnectionId=connection_ids[0]
            ),
            call(
                Data='[{"someKey": "someValue"}]'.encode('utf-8'),
                ConnectionId=connection_ids[1]
            )
        ]

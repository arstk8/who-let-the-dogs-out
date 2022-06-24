import os
from decimal import Decimal
from unittest.mock import call

import boto3
import pytest
from botocore.exceptions import ClientError

from src.who_let_the_dogs_out.api_gateway.notifier import Notifier


class Fixtures:
    MOCK_ENDPOINT_URL_SANS_WSS = 'someurl'
    MOCK_ENDPOINT_URL = f'wss://{MOCK_ENDPOINT_URL_SANS_WSS}'

    @pytest.fixture(autouse=True)
    def get_env(self, mocker):
        get_env = mocker.patch.object(os, os.getenv.__name__)

        def stub(variable_name):
            if 'ENDPOINT_URL' == variable_name:
                return self.MOCK_ENDPOINT_URL

        get_env.side_effect = stub
        return get_env

    @pytest.fixture
    def apigateway_client(self, mocker):
        return mocker.Mock()

    @pytest.fixture(autouse=True)
    def boto3_client(self, mocker, apigateway_client):
        boto3_resource = mocker.patch.object(boto3, boto3.client.__name__)

        def stub(resource_name, endpoint_url):
            if resource_name == 'apigatewaymanagementapi' and f'https://{self.MOCK_ENDPOINT_URL_SANS_WSS}' == endpoint_url:
                return apigateway_client

        boto3_resource.side_effect = stub
        return boto3_resource


class TestHandler(Fixtures):

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

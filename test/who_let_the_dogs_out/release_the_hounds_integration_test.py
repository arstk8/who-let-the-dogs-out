import os
import time
from unittest.mock import call

import boto3
import pytest
import simplejson as json
from boto3.dynamodb.conditions import Key, Attr


class Fixtures:
    MOCK_CONNECTION_TABLE = 'some connection table'
    MOCK_DOG_TABLE = 'some dog table'
    MOCK_ENDPOINT_URL = 'some endpoint url'
    MOCK_CONNECTION_ID1 = 'some id'
    MOCK_CONNECTION_ID2 = 'some other id'
    MOCK_CONNECTION_ID3 = 'yet another id'
    MOCK_NEIGHBOR_GROUP = 'some group'
    MOCK_USERNAME = 'some user'
    MOCK_TTL = 12345
    MOCK_TIME_VALUE = 1337

    @pytest.fixture(autouse=True)
    def get_env(self, mocker):
        get_env = mocker.patch.object(os, os.getenv.__name__)

        def stub(variable_name):
            if 'CONNECTION_TABLE_NAME' == variable_name:
                return self.MOCK_CONNECTION_TABLE
            elif 'DOG_TABLE_NAME' == variable_name:
                return self.MOCK_DOG_TABLE
            elif 'ENDPOINT_URL' == variable_name:
                return self.MOCK_ENDPOINT_URL

        get_env.side_effect = stub
        return get_env

    @pytest.fixture
    def connections_table(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def dog_table(self, mocker):
        return mocker.Mock()

    @pytest.fixture(autouse=True)
    def dynamodb_client(self, mocker, connections_table, dog_table):
        dynamodb_client = mocker.Mock()

        def stub(table_name):
            if self.MOCK_CONNECTION_TABLE == table_name:
                return connections_table
            elif self.MOCK_DOG_TABLE == table_name:
                return dog_table

        dynamodb_client.Table.side_effect = stub
        return dynamodb_client

    @pytest.fixture(autouse=True)
    def boto3_resource(self, mocker, dynamodb_client):
        boto3_resource = mocker.patch.object(boto3, boto3.resource.__name__)

        def stub(resource_name):
            if 'dynamodb' == resource_name:
                return dynamodb_client

        boto3_resource.side_effect = stub
        return boto3_resource

    @pytest.fixture
    def apigateway_client(self, mocker):
        return mocker.Mock()

    @pytest.fixture(autouse=True)
    def boto3_client(self, mocker, apigateway_client):
        boto3_resource = mocker.patch.object(boto3, boto3.client.__name__)

        def stub(resource_name, endpoint_url):
            if 'apigatewaymanagementapi' == resource_name and self.MOCK_ENDPOINT_URL == endpoint_url:
                return apigateway_client

        boto3_resource.side_effect = stub
        return boto3_resource

    @pytest.fixture(autouse=True)
    def time_mock(self, mocker):
        time_mock = mocker.patch.object(time, time.time.__name__)
        time_mock.return_value = self.MOCK_TIME_VALUE
        return time_mock


class TestHandler(Fixtures):

    def test_handle(self, connections_table, dog_table, apigateway_client):
        from src.who_let_the_dogs_out.release_the_hounds import handle

        # noinspection PyPep8Naming
        def connections_query_stub(KeyConditionExpression):
            if Key('connection_id').eq(self.MOCK_CONNECTION_ID1) == KeyConditionExpression:
                return {
                    'Items': [
                        {
                            'neighbor_group': self.MOCK_NEIGHBOR_GROUP,
                            'username': self.MOCK_USERNAME
                        }
                    ],
                    'Count': 1
                }

        connections_table.query.side_effect = connections_query_stub

        # noinspection PyPep8Naming
        def connections_scan_stub(ProjectionExpression, FilterExpression):
            if 'connection_id' == ProjectionExpression and Attr('connection_id').ne(self.MOCK_CONNECTION_ID1) & Attr(
                    'neighbor_group').eq(self.MOCK_NEIGHBOR_GROUP) == FilterExpression:
                return {
                    'Items': [
                        {
                            'connection_id': self.MOCK_CONNECTION_ID2
                        },
                        {
                            'connection_id': self.MOCK_CONNECTION_ID3
                        }
                    ]
                }

        connections_table.scan.side_effect = connections_scan_stub

        return_value = handle({
            'requestContext': {
                'connectionId': self.MOCK_CONNECTION_ID1
            },
            'body': json.dumps({
                'data': {
                    'neighborGroup': self.MOCK_NEIGHBOR_GROUP,
                    'username': self.MOCK_USERNAME
                }
            })

        }, {})

        assert return_value == {
            'statusCode': 200,
            'body': 'Added Dog!',
            'headers': {
                'Content-Type': 'application/json'
            }
        }

        dog_table.put_item.assert_called_once_with(
            Item={
                'neighbor_group': self.MOCK_NEIGHBOR_GROUP,
                'username': self.MOCK_USERNAME,
                'ttl': self.MOCK_TIME_VALUE + 1800
            }
        )

        assert apigateway_client.post_to_connection.call_args_list == [
            call(
                Data=json.dumps(
                    [{'username': self.MOCK_USERNAME, 'timeToLive': self.MOCK_TIME_VALUE + 30 * 60}]
                ).encode('utf-8'),
                ConnectionId=self.MOCK_CONNECTION_ID2
            ),
            call(
                Data=json.dumps(
                    [{'username': self.MOCK_USERNAME, 'timeToLive': self.MOCK_TIME_VALUE + 30 * 60}]
                ).encode('utf-8'),
                ConnectionId=self.MOCK_CONNECTION_ID3
            )
        ]

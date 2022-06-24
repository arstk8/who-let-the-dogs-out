import os

import boto3
import pytest
import simplejson as json
from boto3.dynamodb.conditions import Key

from src.who_let_the_dogs_out.model.dog_message import DogMessage


class Fixtures:
    MOCK_CONNECTION_TABLE = 'some connection table'
    MOCK_DOG_TABLE = 'some dog table'
    MOCK_ENDPOINT_URL = 'some endpoint url'
    MOCK_NEIGHBOR_GROUP = 'some group'
    MOCK_USERNAME1 = 'some user'
    MOCK_USERNAME2 = 'some other user'
    MOCK_TTL1 = 12345
    MOCK_TTL2 = 54231

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
        boto3_client = mocker.patch.object(boto3, boto3.client.__name__)

        def stub(resource_name, endpoint_url):
            if 'apigatewaymanagementapi' == resource_name and self.MOCK_ENDPOINT_URL == endpoint_url:
                return apigateway_client

        boto3_client.side_effect = stub
        return boto3_client


class TestHandler(Fixtures):
    MOCK_CONNECTION_ID = 'some id'

    def test_handle(self, connections_table, dog_table, apigateway_client):
        from src.who_let_the_dogs_out.hound_status import handle

        # noinspection PyPep8Naming
        def connections_stub(KeyConditionExpression):
            if Key('connection_id').eq(self.MOCK_CONNECTION_ID) == KeyConditionExpression:
                return {
                    'Items': [
                        {
                            'neighbor_group': self.MOCK_NEIGHBOR_GROUP,
                            'username': self.MOCK_USERNAME1
                        }
                    ],
                    'Count': 1
                }

        connections_table.query.side_effect = connections_stub

        # noinspection PyPep8Naming
        def dog_stub(KeyConditionExpression):
            if Key('neighbor_group').eq(self.MOCK_NEIGHBOR_GROUP) == KeyConditionExpression:
                return {
                    'Items': [
                        {
                            'username': self.MOCK_USERNAME1,
                            'ttl': self.MOCK_TTL1
                        },
                        {
                            'username': self.MOCK_USERNAME2,
                            'ttl': self.MOCK_TTL2
                        }
                    ],
                    'Count': 2
                }

        dog_table.query.side_effect = dog_stub

        return_value = handle({
            'requestContext': {
                'connectionId': self.MOCK_CONNECTION_ID
            },
            'body': json.dumps({
                'data': {
                    'neighborGroup': self.MOCK_NEIGHBOR_GROUP,
                    'username': self.MOCK_USERNAME1
                }
            })

        }, {})

        assert return_value == {
            'statusCode': 200,
            'body': 'Success!',
            'headers': {
                'Content-Type': 'application/json'
            }
        }

        apigateway_client.post_to_connection.assert_called_once_with(
            Data=json.dumps([
                DogMessage(self.MOCK_USERNAME1, self.MOCK_TTL1).get_payload(),
                DogMessage(self.MOCK_USERNAME2, self.MOCK_TTL2).get_payload()
            ]).encode('utf-8'),
            ConnectionId=self.MOCK_CONNECTION_ID
        )

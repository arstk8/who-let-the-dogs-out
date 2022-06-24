import os

import boto3
import pytest


class Fixtures:
    MOCK_CONNECTION_TABLE = 'some connection table'

    @pytest.fixture(autouse=True)
    def boto3_resource(self, mocker, dynamodb_client):
        boto3_resource = mocker.patch.object(boto3, boto3.resource.__name__)

        def stub(resource_name):
            if 'dynamodb' == resource_name:
                return dynamodb_client

        boto3_resource.side_effect = stub
        return boto3_resource

    @pytest.fixture(autouse=True)
    def get_env(self, mocker):
        get_env = mocker.patch.object(os, os.getenv.__name__)

        def stub(variable_name):
            if 'CONNECTION_TABLE_NAME' == variable_name:
                return self.MOCK_CONNECTION_TABLE

        get_env.side_effect = stub
        return get_env

    @pytest.fixture(autouse=True)
    def dynamodb_client(self, mocker, connections_table):
        dynamodb_client = mocker.Mock()

        def stub(table_name):
            if self.MOCK_CONNECTION_TABLE == table_name:
                return connections_table

        dynamodb_client.Table.side_effect = stub
        return dynamodb_client

    @pytest.fixture
    def connections_table(self, mocker):
        return mocker.Mock()


class TestHandler(Fixtures):
    MOCK_CONNECTION_ID = 'some id'

    def test_handle(self, connections_table):
        from src.who_let_the_dogs_out.disconnect import handle
        return_value = handle({
            'requestContext': {
                'connectionId': self.MOCK_CONNECTION_ID
            }
        }, {})

        assert return_value == {
            'statusCode': 200,
            'body': 'Disconnected!',
            'headers': {
                'Content-Type': 'application/json'
            }
        }

        connections_table.delete_item.assert_called_once_with(
            Key={
                'connection_id': self.MOCK_CONNECTION_ID
            }
        )

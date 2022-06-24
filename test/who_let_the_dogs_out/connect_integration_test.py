import os
import time

import boto3
import pytest


class Fixtures:
    MOCK_CONNECTION_TABLE = 'some connection table'
    MOCK_USERS_TABLE = 'some users table'
    MOCK_TIME_VALUE = 1337

    @pytest.fixture(autouse=True)
    def get_env(self, mocker):
        get_env = mocker.patch.object(os, os.getenv.__name__)

        def stub(variable_name):
            if 'CONNECTION_TABLE_NAME' == variable_name:
                return self.MOCK_CONNECTION_TABLE
            elif 'USERS_TABLE_NAME' == variable_name:
                return self.MOCK_USERS_TABLE

        get_env.side_effect = stub
        return get_env

    @pytest.fixture
    def connections_table(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def users_table(self, mocker):
        return mocker.Mock()

    @pytest.fixture(autouse=True)
    def dynamodb_client(self, mocker, connections_table, users_table):
        dynamodb_client = mocker.Mock()

        def stub(table_name):
            if self.MOCK_CONNECTION_TABLE == table_name:
                return connections_table
            elif self.MOCK_USERS_TABLE == table_name:
                return users_table

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

    @pytest.fixture(autouse=True)
    def time_mock(self, mocker):
        time_mock = mocker.patch.object(time, time.time.__name__)
        time_mock.return_value = self.MOCK_TIME_VALUE
        return time_mock


class TestHandler(Fixtures):
    MOCK_CONNECTION_ID = 'some id'
    MOCK_NEIGHBOR_GROUP = 'some group'
    MOCK_USERNAME = 'some user'

    def test_handle(self, connections_table, users_table):
        from src.who_let_the_dogs_out.connect import handle
        return_value = handle({
            'requestContext': {
                'connectionId': self.MOCK_CONNECTION_ID
            },
            'headers': {
                'neighbor-group': self.MOCK_NEIGHBOR_GROUP,
                'username': self.MOCK_USERNAME
            }
        }, {})

        assert return_value == {
            'statusCode': 200,
            'body': 'Connected!',
            'headers': {
                'Content-Type': 'application/json'
            }
        }

        connections_table.put_item.assert_called_once_with(Item={
            'connection_id': self.MOCK_CONNECTION_ID,
            'neighbor_group': self.MOCK_NEIGHBOR_GROUP,
            'username': self.MOCK_USERNAME,
            'ttl': self.MOCK_TIME_VALUE + 7200
        })
        users_table.put_item.assert_called_once_with(Item={
            'neighbor_group': self.MOCK_NEIGHBOR_GROUP,
            'username': self.MOCK_USERNAME,
            'ttl': self.MOCK_TIME_VALUE + 2592000
        })

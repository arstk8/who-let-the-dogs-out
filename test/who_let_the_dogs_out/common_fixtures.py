import os
import time

import boto3
import pytest

MOCK_CONNECTION_TABLE = 'some connection table'
MOCK_DOG_TABLE = 'some dog table'
MOCK_USERS_TABLE = 'some users table'

MOCK_ENDPOINT_URL_SANS_WSS = 'someurl'
MOCK_ENDPOINT_URL = f'wss://{MOCK_ENDPOINT_URL_SANS_WSS}'


class AwsFixtures:

    @pytest.fixture
    def connections_table(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def dog_table(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def users_table(self, mocker):
        return mocker.Mock()

    @pytest.fixture(autouse=True)
    def dynamodb_client(self, mocker, connections_table, dog_table, users_table):
        dynamodb_client = mocker.Mock()

        def stub(table_name):
            if MOCK_CONNECTION_TABLE == table_name:
                return connections_table
            elif MOCK_USERS_TABLE == table_name:
                return users_table
            elif MOCK_DOG_TABLE == table_name:
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
            if 'apigatewaymanagementapi' == resource_name and f'https://{MOCK_ENDPOINT_URL_SANS_WSS}' == endpoint_url:
                return apigateway_client

        boto3_resource.side_effect = stub
        return boto3_resource


class BasicPythonFixtures:
    MOCK_CLOUDFRONT_SECRET = 'some secret'

    MOCK_TIME_VALUE = 1337

    @pytest.fixture(autouse=True)
    def time_mock(self, mocker):
        time_mock = mocker.patch.object(time, time.time.__name__)
        time_mock.return_value = self.MOCK_TIME_VALUE
        return time_mock

    @pytest.fixture(autouse=True)
    def get_env(self, mocker):
        get_env = mocker.patch.object(os, os.getenv.__name__)

        def stub(variable_name):
            if 'CONNECTION_TABLE_NAME' == variable_name:
                return MOCK_CONNECTION_TABLE
            elif 'DOG_TABLE_NAME' == variable_name:
                return MOCK_DOG_TABLE
            elif 'USERS_TABLE_NAME' == variable_name:
                return MOCK_USERS_TABLE
            elif 'ENDPOINT_URL' == variable_name:
                return MOCK_ENDPOINT_URL
            elif 'CLOUDFRONT_SECRET' == variable_name:
                return self.MOCK_CLOUDFRONT_SECRET

        get_env.side_effect = stub
        return get_env

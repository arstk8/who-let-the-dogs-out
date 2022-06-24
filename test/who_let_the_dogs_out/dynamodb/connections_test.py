import os

import boto3
import pytest
from boto3.dynamodb.conditions import Key, Attr


class Fixtures:
    MOCK_CONNECTION_TABLE = 'some connection table'

    @pytest.fixture(autouse=True)
    def get_env(self, mocker):
        get_env = mocker.patch.object(os, os.getenv.__name__)

        def stub(variable_name):
            if 'CONNECTION_TABLE_NAME' == variable_name:
                return self.MOCK_CONNECTION_TABLE

        get_env.side_effect = stub
        return get_env

    @pytest.fixture
    def connections_table(self, mocker):
        return mocker.Mock()

    @pytest.fixture(autouse=True)
    def dynamodb_client(self, mocker, connections_table):
        dynamodb_client = mocker.Mock()

        def stub(table_name):
            if self.MOCK_CONNECTION_TABLE == table_name:
                return connections_table

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


class TestHandler(Fixtures):
    MOCK_CONNECTION_ID1 = 'some connection id'
    MOCK_CONNECTION_ID2 = 'some other connection id'
    MOCK_CONNECTION_ID3 = 'yet another connection id'
    MOCK_CONNECTION_ID4 = 'still another connection id'
    MOCK_NEIGHBOR_GROUP = 'some neighbor group'
    MOCK_USERNAME = 'some username'

    def test_get_connection_data_when_one_connection_exists_returns_its_data(self, connections_table):
        from src.who_let_the_dogs_out.dynamodb.connections import Connections

        # noinspection PyPep8Naming
        def stub(KeyConditionExpression):
            if Key('connection_id').eq(self.MOCK_CONNECTION_ID1) == KeyConditionExpression:
                return {
                    'Count': 1,
                    'Items': [{'neighbor_group': self.MOCK_NEIGHBOR_GROUP, 'username': self.MOCK_USERNAME}]
                }

        connections_table.query.side_effect = stub

        assert Connections().get_connection_data(self.MOCK_CONNECTION_ID1) == {
            'neighborGroup': self.MOCK_NEIGHBOR_GROUP,
            'username': self.MOCK_USERNAME
        }

    def test_get_connection_data_when_multiple_connections_exist_returns_first_data(self, connections_table):
        from src.who_let_the_dogs_out.dynamodb.connections import Connections

        # noinspection PyPep8Naming
        def stub(KeyConditionExpression):
            if Key('connection_id').eq(self.MOCK_CONNECTION_ID1) == KeyConditionExpression:
                return {
                    'Count': 3,
                    'Items': [
                        {'neighbor_group': self.MOCK_NEIGHBOR_GROUP, 'username': self.MOCK_USERNAME},
                        {'neighbor_group': 'some other group', 'username': 'some other username'},
                        {'neighbor_group': 'yet another group', 'username': 'yet another username'}
                    ]
                }

        connections_table.query.side_effect = stub

        assert Connections().get_connection_data(self.MOCK_CONNECTION_ID1) == {
            'neighborGroup': self.MOCK_NEIGHBOR_GROUP,
            'username': self.MOCK_USERNAME
        }

    def test_get_connection_data_when_not_exists_returns_none(self, connections_table):
        from src.who_let_the_dogs_out.dynamodb.connections import Connections

        # noinspection PyPep8Naming
        def stub(KeyConditionExpression):
            if Key('connection_id').eq(self.MOCK_CONNECTION_ID1) == KeyConditionExpression:
                return {'Count': 0, 'Items': []}

        connections_table.query.side_effect = stub

        assert Connections().get_connection_data(self.MOCK_CONNECTION_ID1) is None

    def test_get_current_connections_one_page(self, connections_table):
        from src.who_let_the_dogs_out.dynamodb.connections import Connections

        # noinspection PyPep8Naming
        def stub(ProjectionExpression, FilterExpression, ExclusiveStartKey=None):
            if 'connection_id' == ProjectionExpression \
                    and Attr('connection_id').ne(self.MOCK_CONNECTION_ID1) \
                    & Attr('neighbor_group').eq(self.MOCK_NEIGHBOR_GROUP) == FilterExpression \
                    and ExclusiveStartKey is None:
                return {
                    'Items': [
                        {'connection_id': self.MOCK_CONNECTION_ID2},
                        {'connection_id': self.MOCK_CONNECTION_ID3},
                        {'connection_id': self.MOCK_CONNECTION_ID4}
                    ]
                }

        connections_table.scan.side_effect = stub
        assert Connections().get_current_connections(self.MOCK_CONNECTION_ID1, self.MOCK_NEIGHBOR_GROUP) == [
            self.MOCK_CONNECTION_ID2,
            self.MOCK_CONNECTION_ID3,
            self.MOCK_CONNECTION_ID4
        ]

    def test_get_current_connections_multiple_pages(self, connections_table):
        from src.who_let_the_dogs_out.dynamodb.connections import Connections

        # noinspection PyPep8Naming
        def stub(ProjectionExpression, FilterExpression, ExclusiveStartKey=None):
            if 'connection_id' == ProjectionExpression \
                    and Attr('connection_id').ne(self.MOCK_CONNECTION_ID1) \
                    & Attr('neighbor_group').eq(self.MOCK_NEIGHBOR_GROUP) == FilterExpression:
                if ExclusiveStartKey is None:
                    return {
                        'Items': [{'connection_id': self.MOCK_CONNECTION_ID2}],
                        'LastEvaluatedKey': self.MOCK_CONNECTION_ID2
                    }
                elif ExclusiveStartKey == self.MOCK_CONNECTION_ID2:
                    return {
                        'Items': [{'connection_id': self.MOCK_CONNECTION_ID3}],
                        'LastEvaluatedKey': self.MOCK_CONNECTION_ID3
                    }
                elif ExclusiveStartKey == self.MOCK_CONNECTION_ID3:
                    return {
                        'Items': [{'connection_id': self.MOCK_CONNECTION_ID4}]
                    }

        connections_table.scan.side_effect = stub
        assert Connections().get_current_connections(self.MOCK_CONNECTION_ID1, self.MOCK_NEIGHBOR_GROUP) == [
            self.MOCK_CONNECTION_ID2,
            self.MOCK_CONNECTION_ID3,
            self.MOCK_CONNECTION_ID4
        ]

from unittest.mock import call

import simplejson as json
from boto3.dynamodb.conditions import Key, Attr

from test.who_let_the_dogs_out.common_fixtures import AwsFixtures, BasicPythonFixtures


class TestHandler(AwsFixtures, BasicPythonFixtures):
    MOCK_CONNECTION_ID1 = 'some id'
    MOCK_CONNECTION_ID2 = 'some other id'
    MOCK_CONNECTION_ID3 = 'yet another id'
    MOCK_NEIGHBOR_GROUP = 'some group'
    MOCK_USERNAME = 'some user'
    MOCK_TTL = 12345

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
                Data=json.dumps({
                    'action': 'release',
                    'data': [{'username': self.MOCK_USERNAME, 'timeToLive': self.MOCK_TIME_VALUE + 30 * 60}]
                }
                ).encode('utf-8'),
                ConnectionId=self.MOCK_CONNECTION_ID2
            ),
            call(
                Data=json.dumps({
                    'action': 'release',
                    'data': [{'username': self.MOCK_USERNAME, 'timeToLive': self.MOCK_TIME_VALUE + 30 * 60}]
                }).encode('utf-8'),
                ConnectionId=self.MOCK_CONNECTION_ID3
            )
        ]

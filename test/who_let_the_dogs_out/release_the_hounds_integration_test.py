from unittest.mock import call

import simplejson as json

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

        AwsFixtures.stub_connection_query(connections_table, self.MOCK_CONNECTION_ID1, [
            {
                'neighbor_group': self.MOCK_NEIGHBOR_GROUP,
                'username': self.MOCK_USERNAME
            }
        ])

        AwsFixtures.stub_connection_scan(connections_table, self.MOCK_NEIGHBOR_GROUP, [
            {
                'connection_id': self.MOCK_CONNECTION_ID1
            },
            {
                'connection_id': self.MOCK_CONNECTION_ID2
            },
            {
                'connection_id': self.MOCK_CONNECTION_ID3
            }
        ])

        return_value = handle({
            'requestContext': {
                'connectionId': self.MOCK_CONNECTION_ID1
            }
        }, {
            'neighborGroup': self.MOCK_NEIGHBOR_GROUP,
            'username': self.MOCK_USERNAME
        })

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

        data = [{'username': self.MOCK_USERNAME, 'timeToLive': self.MOCK_TIME_VALUE + 30 * 60}]
        assert apigateway_client.post_to_connection.call_args_list == [
            call(
                Data=json.dumps({'action': 'release', 'data': data}).encode('utf-8'),
                ConnectionId=self.MOCK_CONNECTION_ID1
            ),
            call(
                Data=json.dumps({'action': 'release', 'data': data}).encode('utf-8'),
                ConnectionId=self.MOCK_CONNECTION_ID2
            ),
            call(
                Data=json.dumps({'action': 'release', 'data': data}).encode('utf-8'),
                ConnectionId=self.MOCK_CONNECTION_ID3
            )
        ]

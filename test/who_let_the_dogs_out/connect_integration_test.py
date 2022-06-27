from test.who_let_the_dogs_out.common_fixtures import AwsFixtures, BasicPythonFixtures


class TestHandler(AwsFixtures, BasicPythonFixtures):
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

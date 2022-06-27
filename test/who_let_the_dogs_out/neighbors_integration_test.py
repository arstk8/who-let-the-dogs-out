import simplejson as json
from boto3.dynamodb.conditions import Key

from test.who_let_the_dogs_out.common_fixtures import AwsFixtures, BasicPythonFixtures


class TestHandler(AwsFixtures, BasicPythonFixtures):
    MOCK_NEIGHBOR_GROUP = 'some group'
    MOCK_USERNAME1 = 'some user'
    MOCK_USERNAME2 = 'some other user'
    MOCK_CONNECTION_ID = 'some id'

    def test_handle(self, connections_table, users_table, apigateway_client):
        from src.who_let_the_dogs_out.neighbors import handle

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
        def users_stub(KeyConditionExpression, ProjectionExpression):
            if Key('neighbor_group').eq(
                    self.MOCK_NEIGHBOR_GROUP) == KeyConditionExpression and 'username' == ProjectionExpression:
                return {
                    'Items': [
                        {
                            'username': self.MOCK_USERNAME1
                        },
                        {
                            'username': self.MOCK_USERNAME2
                        }
                    ]
                }

        users_table.query.side_effect = users_stub

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
            Data=json.dumps([self.MOCK_USERNAME1, self.MOCK_USERNAME2]).encode('utf-8'),
            ConnectionId=self.MOCK_CONNECTION_ID
        )

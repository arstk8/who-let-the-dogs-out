import simplejson as json
from boto3.dynamodb.conditions import Key

from src.who_let_the_dogs_out.model.dog_message import DogMessage
from test.who_let_the_dogs_out.common_fixtures import AwsFixtures, BasicPythonFixtures


class TestHandler(AwsFixtures, BasicPythonFixtures):
    MOCK_CONNECTION_ID = 'some id'
    MOCK_NEIGHBOR_GROUP = 'some group'
    MOCK_USERNAME1 = 'some user'
    MOCK_USERNAME2 = 'some other user'
    MOCK_TTL1 = 12345
    MOCK_TTL2 = 54231

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
            Data=json.dumps({
                'action': 'status',
                'data': [
                    DogMessage(self.MOCK_USERNAME1, self.MOCK_TTL1).get_payload(),
                    DogMessage(self.MOCK_USERNAME2, self.MOCK_TTL2).get_payload()
                ]
            }).encode('utf-8'),
            ConnectionId=self.MOCK_CONNECTION_ID
        )

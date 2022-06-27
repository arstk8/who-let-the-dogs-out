from test.who_let_the_dogs_out.common_fixtures import AwsFixtures, BasicPythonFixtures


class TestHandler(AwsFixtures, BasicPythonFixtures):
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

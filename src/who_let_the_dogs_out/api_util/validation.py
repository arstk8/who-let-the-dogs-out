import simplejson as json

from src.who_let_the_dogs_out.dynamodb.connections import Connections


class Validator:
    def __init__(self, function):
        self.function = function

    def validate(self, event, _, user_data, connection_data):
        if connection_data is None \
                or connection_data['neighborGroup'] != user_data['neighborGroup'] \
                or connection_data['username'] != user_data['username']:
            return {
                'statusCode': 403,
                'body': 'User does not match the user for this connection!',
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        return self.function(event, _)


class ValidateUserData:

    def __init__(self, function):
        self.validator = Validator(function)
        self.connections = Connections()

    def __call__(self, event, _):
        connection_id = event['requestContext']['connectionId']
        user_data = json.loads(event['body'])['data']
        connection_data = self.connections.get_connection_data(connection_id)

        return self.validator.validate(event, _, user_data, connection_data)

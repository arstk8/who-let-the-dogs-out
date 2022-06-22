import simplejson as json

from src.who_let_the_dogs_out.dynamodb.connections import get_connection_data


def validate_user_data(func):
    def wrapper(event, _):
        connection_id = event['requestContext']['connectionId']
        user_data = json.loads(event['body'])['data']
        connection_data = get_connection_data(connection_id)

        if connection_data is None \
                or connection_data['neighborGroup'] != user_data['neighborGroup'] \
                or connection_data['username'] != user_data['username']:
            return {
                'statusCode': 400,
                'body': 'User does not match the user for this connection!',
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        return func(event, _)

    return wrapper

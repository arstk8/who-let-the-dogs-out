import simplejson as json

from src.who_let_the_dogs_out.api_gateway.notify import notify_connections
from src.who_let_the_dogs_out.dynamodb.hounds import get_dogs_out_in_neighbor_group


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    user_data = json.loads(event['body'])['data']
    __post_current_state_to_connection(connection_id, user_data)

    return {
        'statusCode': 200,
        'body': 'Success!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }


def __post_current_state_to_connection(connection_id, user_data):
    neighbor_group = user_data['neighborGroup']

    dogs_out_in_neighbor_group = get_dogs_out_in_neighbor_group(neighbor_group)

    dog_messages = list(
        map(lambda dog_message: dog_message.get_payload(), dogs_out_in_neighbor_group)
    )

    notify_connections([connection_id], dog_messages)

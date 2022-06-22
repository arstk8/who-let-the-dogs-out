import simplejson as json

from src.who_let_the_dogs_out.api_gateway.notify import notify_connections
from src.who_let_the_dogs_out.dynamodb.users import get_users_in_neighbor_group


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    data = json.loads(event['body'])['data']
    __post_current_state_to_connection(connection_id, data)

    return {
        'statusCode': 200,
        'body': 'Success!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }


def __post_current_state_to_connection(connection_id, data):
    neighbor_group = data['neighborGroup']
    dogs_out_in_neighbor_group = get_users_in_neighbor_group(neighbor_group)
    notify_connections([connection_id], dogs_out_in_neighbor_group)

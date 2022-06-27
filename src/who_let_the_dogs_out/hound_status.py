import simplejson as json

from src.who_let_the_dogs_out.api_gateway.notifier import Notifier
from src.who_let_the_dogs_out.api_util.validation import ValidateUserData
from src.who_let_the_dogs_out.dynamodb.hounds import Hounds

hounds = Hounds()
notifier = Notifier()


@ValidateUserData
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

    dogs_out_in_neighbor_group = hounds.get_dogs_out_in_neighbor_group(neighbor_group)

    dog_messages = list(
        map(lambda dog_message: dog_message.get_payload(), dogs_out_in_neighbor_group)
    )

    notifier.notify_connections(
        [connection_id],
        {
            'action': 'status',
            'data': dog_messages
        }
    )

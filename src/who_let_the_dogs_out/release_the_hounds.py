import time

from src.who_let_the_dogs_out.api_gateway.notifier import Notifier
from src.who_let_the_dogs_out.api_util.user_data import UserDataSupplier
from src.who_let_the_dogs_out.dynamodb.connections import Connections
from src.who_let_the_dogs_out.dynamodb.hounds import Hounds
from src.who_let_the_dogs_out.model.dog_message import DogMessage

connections = Connections()
hounds = Hounds()
notifier = Notifier()


@UserDataSupplier
def handle(event, user_data):
    connection_id = event['requestContext']['connectionId']

    __add_dog(connection_id, user_data)
    return {
        'statusCode': 200,
        'body': 'Added Dog!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }


def __add_dog(connection_id, user_data):
    username = user_data['username']
    neighbor_group = user_data['neighborGroup']

    thirty_minutes_in_seconds = 30 * 60
    time_to_live = int(time.time()) + thirty_minutes_in_seconds

    hounds.add_dog(username, neighbor_group, time_to_live)
    __notify_connections(connection_id, neighbor_group, DogMessage(username, time_to_live))


def __notify_connections(connection_id, neighbor_group, dog_message):
    connections_ids = connections.get_current_connections(connection_id, neighbor_group)
    notifier.notify_connections(
        connections_ids,
        {
            'action': 'release',
            'data': [dog_message.get_payload()]
        }
    )

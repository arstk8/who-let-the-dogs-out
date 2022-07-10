from src.who_let_the_dogs_out.api_gateway.notifier import Notifier
from src.who_let_the_dogs_out.api_util.user_data import UserDataSupplier
from src.who_let_the_dogs_out.dynamodb.users import Users

notifier = Notifier()
users = Users()


@UserDataSupplier
def handle(event, user_data):
    connection_id = event['requestContext']['connectionId']
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
    dogs_out_in_neighbor_group = users.get_users_in_neighbor_group(neighbor_group)
    notifier.notify_connections(
        [connection_id],
        {
            'action': 'neighbors',
            'data': dogs_out_in_neighbor_group
        }
    )

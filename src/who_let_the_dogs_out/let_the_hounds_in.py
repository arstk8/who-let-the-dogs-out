from src.who_let_the_dogs_out.api_util.user_data import UserDataSupplier
from src.who_let_the_dogs_out.hound_updater import HoundUpdater

hound_updater = HoundUpdater('unrelease')


@UserDataSupplier
def handle(event, user_data):
    connection_id = event['requestContext']['connectionId']

    hound_updater.update_hound(connection_id, user_data, None)
    return {
        'statusCode': 200,
        'body': 'Set Dog to In!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }

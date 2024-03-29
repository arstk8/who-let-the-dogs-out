import time

from src.who_let_the_dogs_out.api_util.user_data import UserDataSupplier
from src.who_let_the_dogs_out.hound_updater import HoundUpdater

hound_updater = HoundUpdater('release')


@UserDataSupplier
def handle(event, user_data):
    connection_id = event['requestContext']['connectionId']

    thirty_minutes_in_seconds = 30 * 60
    time_to_live = int(time.time()) + thirty_minutes_in_seconds
    hound_updater.update_hound(connection_id, user_data, time_to_live)
    return {
        'statusCode': 200,
        'body': 'Added Dog!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }

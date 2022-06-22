from src.who_let_the_dogs_out.dynamodb.connections import remove_connection_id


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    remove_connection_id(connection_id)
    return {
        'statusCode': 200,
        'body': 'Disconnected!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }

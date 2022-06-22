from src.who_let_the_dogs_out.dynamodb.connections import add_connection_id


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    neighbor_group = event['headers']['neighbor-group']
    username = event['headers']['username']
    add_connection_id(connection_id, neighbor_group, username)

    return {
        'statusCode': 200,
        'body': 'Connected!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }

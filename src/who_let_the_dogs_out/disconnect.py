from src.who_let_the_dogs_out.dynamodb.connections import Connections

connections = Connections()


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    connections.remove_connection_id(connection_id)
    return {
        'statusCode': 200,
        'body': 'Disconnected!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }

from src.who_let_the_dogs_out.dynamodb.connections import Connections
from src.who_let_the_dogs_out.dynamodb.users import Users

connections = Connections()
users = Users()


def handle(event, _):
    connection_id = event['requestContext']['connectionId']
    neighbor_group = event['queryStringParameters']['neighborGroup']
    username = event['queryStringParameters']['username']
    connections.add_connection_id(connection_id, neighbor_group, username)
    users.add_user(neighbor_group, username)

    return {
        'statusCode': 200,
        'body': 'Connected!',
        'headers': {
            'Content-Type': 'application/json'
        }
    }

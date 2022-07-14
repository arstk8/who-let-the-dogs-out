from src.who_let_the_dogs_out.api_gateway.notifier import Notifier
from src.who_let_the_dogs_out.dynamodb.connections import Connections
from src.who_let_the_dogs_out.dynamodb.hounds import Hounds
from src.who_let_the_dogs_out.model.dog_message import DogMessage


class HoundUpdater:
    def __init__(self, action):
        self.action = action
        self.connections = Connections()
        self.hounds = Hounds()
        self.notifier = Notifier()

    def update_hound(self, connection_id, user_data, time_to_live):
        username = user_data['username']
        neighbor_group = user_data['neighborGroup']

        if time_to_live:
            self.hounds.add_dog(neighbor_group, username, time_to_live)
        else:
            self.hounds.remove_dog(neighbor_group, username)

        self.__notify_connections(connection_id, neighbor_group, DogMessage(username, time_to_live))

    def __notify_connections(self, connection_id, neighbor_group, dog_message):
        connections_ids = self.connections.get_current_connections(connection_id, neighbor_group)
        self.notifier.notify_connections(
            connections_ids,
            {
                'action': self.action,
                'data': [dog_message.get_payload()]
            }
        )

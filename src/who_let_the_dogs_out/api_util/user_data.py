from src.who_let_the_dogs_out.dynamodb.connections import Connections


class SupplyUserData:
    def __init__(self, function):
        self.function = function

    def validate(self, event, _, connection_data):
        return self.function(event, connection_data)


class UserDataSupplier:

    def __init__(self, function):
        self.suppy_user_data = SupplyUserData(function)
        self.connections = Connections()

    def __call__(self, event, _):
        connection_id = event['requestContext']['connectionId']
        connection_data = self.connections.get_connection_data(connection_id)

        return self.suppy_user_data.validate(event, _, connection_data)

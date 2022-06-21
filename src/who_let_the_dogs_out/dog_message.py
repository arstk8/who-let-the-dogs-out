class DogMessage:
    def __init__(self, username, time_to_live):
        self.username = username
        self.time_to_live = time_to_live

    def get_payload(self):
        return {'username': self.username, 'timeToLive': self.time_to_live}

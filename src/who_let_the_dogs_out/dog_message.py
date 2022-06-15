class DogMessage:
    def __init__(self, owner_id, time_to_live):
        self.owner_id = owner_id
        self.time_to_live = time_to_live

    def get_payload(self):
        return {'ownerId': self.owner_id, 'timeToLive': self.time_to_live}

class Entity:
    """
    This class represents a generic entity which has an id.
    """
    def __init__(self):
        self._uuid = None

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        """
        Set the UUID of the entity.

        :param value: The UUID of the entity
        """
        self._uuid = value

    def deserialize(self, data: dict):
        """
        Deserialize an entity into an Entity object.

        :param data: The JSON data to deserialize
        """
        self.uuid = data['id']

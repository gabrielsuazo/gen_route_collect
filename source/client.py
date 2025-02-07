import math
import random

from source.params import SIZE_X, SIZE_Y, CLIENT_VOLUME_RANGE


class Client:
    """
    Clients are the points in the route that the collection truck has to visit. They each have an id, a volume of
    material, coordinates on the (x,y) plane, and a maximum capacity before they are overloaded.
    """

    def __init__(self, client_id: int, volume: int = 0, coordinates: (int, int) = (0, 0), capacity: int = 0):
        self.client_id = client_id
        self.volume = volume
        self.coordinates = coordinates
        self.capacity = capacity

    def __repr__(self):
        return f"Client {self.client_id} at {self.coordinates}"

    def randomize_client_params(self):
        """
        Randomize the volume, coordinates and capacity of the client, within the set ranges
        :return:
        """
        self.volume = random.randrange(CLIENT_VOLUME_RANGE[0], CLIENT_VOLUME_RANGE[1])
        coordx = random.randrange(SIZE_X)
        coordy = random.randrange(SIZE_Y)
        self.coordinates = (coordx, coordy)
        self.capacity = random.randrange(self.volume, CLIENT_VOLUME_RANGE[1])


class ClientNode:
    """
    Client nodes store the client information, as well as the previous and the next nodes on the client list of a route.
    """

    def __init__(self, client: Client):
        self.client = client
        self.next = None
        self.prev = None


def calculate_distance_between_clients(first_client: Client, second_client: Client) -> float:
    """
    Calculated the Euclidean distance between two clients on the xy plane
    :param first_client: First client
    :param second_client: Second client
    :return: The distance value
    """
    return math.sqrt(
        (first_client.coordinates[0] - second_client.coordinates[0]) ** 2 +
        (first_client.coordinates[1] - second_client.coordinates[1]) ** 2
    )

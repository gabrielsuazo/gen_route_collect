import numpy.typing as npt
from itertools import permutations

from source.client import ClientNode, Client
from source.params import MAXIMUM_VOLUME


class Route:
    """
    Routes are ordered lists of clients to visit, starting and ending at the initial point. They are described by a
    linked list of clients, and the total distance cost of that route. The head and end of a list will always be the
    starting point
    """

    def __init__(self, starting_point: Client, ordered_client_list: tuple[Client], distance_matrix: npt.NDArray[float]):
        self.head = ClientNode(starting_point)
        self.end = ClientNode(starting_point)
        self.link_nodes(ordered_client_list)
        self.distance_matrix = distance_matrix
        self.distance = self.calculate_distance_cost()

    def link_nodes(self, ordered_client_list: tuple[Client]):
        """
        Connect the client nodes in the list order, putting the starting point at the head and end.
        :param ordered_client_list: List of clients in order of visit
        :return:
        """
        current_node = self.head
        for client in ordered_client_list:
            client_node = ClientNode(client)
            current_node.next = client_node
            current_node = client_node
        current_node.next = self.end

    def calculate_distance_cost(self) -> float:
        """
        Calculate the distance cost of the route
        :return: The distance cost
        """
        distance = 0.0
        current_node = self.head
        while current_node.next is not None:
            distance += self.distance_matrix[current_node.client.client_id][current_node.next.client.client_id]
            current_node = current_node.next
        return distance


class ClientSet:
    """
    Client sets are groups of clients to visit, the sum of volume of material for each client, and the maximum volume
    allowed. We are able to generate the best route for a set by calculating the cost of all possible permutations.
    As sets will not have that many clients, this is computationally feasible.
    """

    def __init__(self, maximum_volume: int = MAXIMUM_VOLUME):
        self.client_set = set()
        self.volume = 0
        self.maximum_volume = maximum_volume
        self.best_route = None

    def try_add_client(self, client: Client) -> bool:
        """
        Try to add new a client to the route. If the volume exceeded the limit, the client is not added
        :param client: Client to add
        :return: True is client is added, False otherwise
        """
        if client not in self.client_set:
            new_volume = self.calculate_volume_on_insertion(client)
            if new_volume > self.maximum_volume:
                return False
            self.client_set.add(client)
            self.volume = new_volume
            return True
        return False

    def calculate_volume_on_insertion(self, added_client: Client) -> int:
        """
        Calculate new total volume of the route if the given client is added to the list.
        :param added_client: New client to add
        :return: The new total volume value if the client is added
        """
        return self.volume + added_client.volume

    def update_volume_on_removal(self, removed_client: Client):
        """
        Update new total volume of the route after removing an existing client from the set
        :param removed_client: Removed client
        :return:
        """
        self.volume -= removed_client.volume

    def check_has_client(self, client: Client) -> bool:
        """
        Check if the set has the given client.
        :param client: Client to check
        :return: True if set contains client, false if not
        """
        return client in self.client_set

    def generate_best_route(self, starting_point: Client, distance_matrix: npt.NDArray[float]):
        """
        Generate all possible routes from the client set and safe the best one in terms of distance cost
        :param starting_point: The start and end point of the route
        :param distance_matrix: The distance cost matrix
        :return:
        """
        client_permutations = permutations(self.client_set)
        lowest_distance = float("inf")
        best_route = None
        for client_permutation in client_permutations:
            route = Route(starting_point, client_permutation, distance_matrix)
            if route.distance < lowest_distance:
                lowest_distance = route.distance
                best_route = route
        self.best_route = best_route


def try_exchange_clients(first_set: ClientSet, second_set: ClientSet,
                         first_client: Client, second_client: Client) -> bool:
    """
    Try to exchange clients between two sets. If the volume is exceeded in any of the set, the exchange is not done.
    :param first_set: First set in exchange
    :param second_set: Second set in exchange
    :param first_client: Client in the first set
    :param second_client: Client in the second set
    :return: True if exchange was successful, false otherwise
    """
    new_first_volume = first_set.volume + second_client.volume - first_client.volume
    if new_first_volume <= first_set.maximum_volume:
        new_second_volume = second_set.volume + first_client.volume - second_client.volume
        if new_second_volume <= second_set.maximum_volume:
            first_set.volume = new_first_volume
            second_set.volume = new_second_volume
            first_set.client_set.remove(first_client)
            first_set.client_set.add(second_client)
            second_set.client_set.remove(second_client)
            second_set.client_set.add(first_client)
            return True
    return False

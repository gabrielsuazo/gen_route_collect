import random
import numpy.typing as npt
from itertools import permutations

from source.client import Client
from source.params import MAXIMUM_VOLUME


class Route:
    """
    Routes are ordered lists of clients to visit, starting and ending at the initial point. They are described by an
    ordered list of clients, the start/end point and the total distance cost of that route.
    """

    def __init__(self, starting_point: Client, ordered_client_list: tuple[Client], distance_matrix: npt.NDArray[float]):
        self.starting_point = starting_point
        self.ordered_client_list = ordered_client_list
        self.distance_matrix = distance_matrix
        self.distance = self.calculate_distance_cost()

    def calculate_distance_cost(self) -> float:
        """
        Calculate the distance cost of the route
        :return: The distance cost
        """
        distance = self.distance_matrix[self.starting_point.client_id][self.ordered_client_list[0].client_id]
        for current_client, next_client in zip(self.ordered_client_list, self.ordered_client_list[1:]):
            distance += self.distance_matrix[current_client.client_id][next_client.client_id]
        distance += self.distance_matrix[
            self.ordered_client_list[len(self.ordered_client_list)-1].client_id][self.starting_point.client_id]
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

    def remove_client(self, client: Client):
        """
        Remove client from the set. Raise exception if the client was not in the set
        :param client: Client to remove
        :return:
        """
        if client not in self.client_set:
            raise Exception(f"Error on removal: Client {client} not in set {self.client_set}")
        self.client_set.remove(client)
        self.update_volume_on_removal(client)

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


def try_merging_sets(first_set: ClientSet, second_set: ClientSet) -> bool:
    """
    Try to merge two sets. If the combined volume exceeds the first set's maximum, the merge is not done
    :param first_set: First set to merge
    :param second_set: Second set to merge
    :return: True if merge was successful, False otherwise
    """
    new_volume = first_set.volume + second_set.volume
    if new_volume <= first_set.volume:
        first_set.client_set = first_set.client_set.union(second_set.client_set)
        first_set.volume = new_volume
        second_set.client_set.clear()
        second_set.volume = 0
        return True
    return False


def try_divide_set(client_set: ClientSet) -> tuple[ClientSet, None] | tuple[ClientSet, ClientSet]:
    """
    Try to divide set into two subsets. Returns the original set and none if the set doesn't have at least two clients
    :param client_set: Client set to divide
    :return: Two client subsets, or the original set and none if division fails
    """
    if len(client_set.client_set) < 1:
        return client_set, None

    new_client_set = ClientSet()
    for i in range(len(client_set.client_set) // 2):
        client = random.choice(tuple(client_set.client_set))
        client_set.remove_client(client)
        new_client_set.try_add_client(client)
    return client_set, new_client_set

import copy
import random
import numpy.typing as npt

from source.client import Client
from source.params import MUTATION_RETRY_NUMBER, CHANCE_OF_MUTATION
from source.route import ClientSet, try_exchange_clients, try_merging_sets, try_divide_set


class Partition:
    """
    A partitions is a set of routes proposing a solution to the problem. Once completed, the routes have to include all
    the clients. The distance represented the total added distance of all routes
    """

    def __init__(self):
        self.distance = float('inf')
        self.is_complete = False
        self.client_sets = []

    def add_client_set(self, client_set: ClientSet):
        """
        Add client set to the list of sets
        :param client_set: Client set to add
        :return:
        """
        self.client_sets.append(client_set)

    def check_completion(self, clients_array):
        """
        Check if the partition contains all the clients and set the is_complete value accordingly. We skip over the
        first client, which is the starting point
        :param clients_array: Clients to check
        :return:
        """
        for client in clients_array[1:]:
            has_client = False
            for client_set in self.client_sets:
                if client_set.check_has_client(client):
                    has_client = True
                    continue
            if not has_client:
                self.is_complete = False
                return
        self.is_complete = True

    def try_client_exchange_mutation(self, retry_counter: int = MUTATION_RETRY_NUMBER) -> bool:
        """
        Try to exchange clients between two sets in the partition
        :param retry_counter: Number of retries allowed
        :return: True if exchange was successful, False if it is still a failure after all the retries
        """
        for i in range(retry_counter):
            client_sets = random.sample(self.client_sets, 2)
            first_client = random.choice(tuple(client_sets[0].client_set))
            second_client = random.choice(tuple(client_sets[1].client_set))
            if try_exchange_clients(client_sets[0], client_sets[1], first_client, second_client):
                return True
        return False

    def try_client_transfer_mutation(self, retry_counter: int = MUTATION_RETRY_NUMBER) -> bool:
        """
        Try to transfer one client from one set to another set in the partition
        :param retry_counter: Number of retries allowed
        :return: True if exchange was successful, False if it is still a failure after all the retries
        """
        for i in range(retry_counter):
            client_sets = random.sample(self.client_sets, 2)
            transfer_client = random.choice(tuple(client_sets[0].client_set))
            if client_sets[1].try_add_client(transfer_client):
                client_sets[0].remove_client(transfer_client)
                if len(client_sets[0].client_set) == 0:
                    self.client_sets.remove(client_sets[0])
                return True
        return False

    def try_set_merge_mutation(self, retry_counter: int = MUTATION_RETRY_NUMBER) -> bool:
        """
        Try to merge two sets in the partition together
        :param retry_counter: Number of retries allowed
        :return: True if exchange was successful, False if it is still a failure after all the retries
        """
        for i in range(retry_counter):
            client_sets = random.sample(self.client_sets, 2)
            if try_merging_sets(client_sets[0], client_sets[1]):
                self.client_sets.remove(client_sets[1])
                return True
        return False

    def try_set_division_mutation(self, retry_counter: int = MUTATION_RETRY_NUMBER) -> bool:
        """
        Try to divide a set from the partition into two sets
        :return: True if division was successful, False if it is still a failure after all the retries
        """
        for i in range(retry_counter):
            client_set = random.choice(self.client_sets)
            new_sets = try_divide_set(client_set)
            if new_sets[1] is not None:
                self.client_sets.remove(client_set)
                self.client_sets.append(new_sets[0])
                self.client_sets.append(new_sets[1])
                return True
        return False

    def random_mutation(self):
        """
        Mutate the partition. Each mutation has an equal chance to occur. It is possible for multiple or all mutations
        to occur simultaneously.
        :return:
        """
        if random.random() < CHANCE_OF_MUTATION:
            self.try_set_division_mutation()
        if random.random() < CHANCE_OF_MUTATION:
            self.try_client_exchange_mutation()
        if random.random() < CHANCE_OF_MUTATION:
            self.try_client_transfer_mutation()
        if random.random() < CHANCE_OF_MUTATION:
            self.try_set_merge_mutation()

    def calculate_distance(self, starting_point: Client, distance_matrix: npt.NDArray[float]):
        """
        Generate the best route of each client set and sum the total distance of all routes
        :param starting_point: Given starting point of routes
        :param distance_matrix: Distance cost matrix
        :return:
        """
        self.distance = 0
        for client_set in self.client_sets:
            client_set.generate_best_route(starting_point, distance_matrix)
            self.distance += client_set.best_route.distance


def clone_partition(partition: Partition) -> Partition:
    """
    Create a copy of the given partition.
    :param partition: Partition to copy
    :return: The copy of the partition
    """
    clone = Partition()
    clone.client_sets = copy.deepcopy(partition.client_sets)
    clone.is_complete = partition.is_complete
    clone.distance = partition.distance
    return clone

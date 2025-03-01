import numpy as np
import numpy.typing as npt

from source.client import Client, calculate_distance_between_clients
from source.display import graph_partition
from source.params import SIZE_X, SIZE_Y, BEST_PROPORTION
from source.partition import Partition
from source.population import Population
from source.route import ClientSet


class Simulator:
    """
    Define and run the simulation.
    """

    def __init__(self, clients_number: int, population_number: int):
        self.starting_point = Client(client_id=0, volume=0, coordinates=(SIZE_X / 2, SIZE_Y / 2), capacity=0)
        self.current_optimal_distance = float('inf')
        self.current_optimal_partition = Partition()
        self.track_list_distances = []
        self.clients_number = clients_number
        self.client_array = self.generate_clients()
        self.distance_matrix = self.generate_distance_matrix()
        self.population_number = population_number
        self.best_number = int(self.population_number*BEST_PROPORTION)

    def generate_clients(self) -> npt.NDArray[Client]:
        """
        Generate a random list of clients (including the starting point)
        :return: The generated list of clients
        """
        client_array = np.ndarray((self.clients_number + 1,), dtype=Client)
        client_array[0] = self.starting_point
        for i in range(1, self.clients_number + 1):
            new_client = Client(i)
            new_client.randomize_client_params()
            client_array[i] = new_client
        return client_array

    def generate_distance_matrix(self) -> npt.NDArray[float]:
        """
        Calculate the distance cost matrix given the list of clients
        :return: The distance cost matrix
        """
        distance_matrix = np.zeros((self.clients_number + 1, self.clients_number + 1), dtype=np.float64)
        for i in range(self.clients_number):
            for j in range(i + 1, self.clients_number + 1):
                distance = calculate_distance_between_clients(self.client_array[i], self.client_array[j])
                distance_matrix[i][j] = distance
                distance_matrix[j][i] = distance
        return distance_matrix

    def start_simulation(self):
        """
        Start the simulation by generating the initial partition, and creating the first generation by copying and
        mutating this first individual
        :return:
        """
        initial_partition = self.create_initial_routes_partition()
        population = Population(initial_partition, self.population_number, self.best_number)
        while True:
            self.current_optimal_partition = population.best_array[self.best_number-1]
            self.current_optimal_distance = self.current_optimal_partition.distance
            self.track_list_distances.append(self.current_optimal_distance)
            graph_partition(self.current_optimal_partition, True)
            next_gen = population.create_new_generation()
            population.update_best_array(next_gen, self.starting_point, self.distance_matrix)

    def get_remaining_highest_volume_client(self, taken_clients: list[Client]) -> Client:
        """
        Returns the client with the highest volume among those that are not taken
        :param taken_clients: List of taken clients
        :return: The client with the highest volume, None if all the clients are taken
        """
        highest_volume = 0
        highest_client = None
        for client in self.client_array:
            if client not in taken_clients:
                if client.volume > highest_volume:
                    highest_volume = client.volume
                    highest_client = client
        return highest_client

    def get_remaining_closest_distance_client(self, taken_clients: list[Client], neighbor_client: Client) -> Client:
        """
        Returns the client closest to the given neighbor client, among those that are not taken
        :param taken_clients: List of taken clients
        :param neighbor_client: Given neighbor client
        :return:
        """
        lowest_distance = float("inf")
        closest_client = None
        for i in range(self.clients_number+1):
            client = self.client_array[i]
            if client not in taken_clients:
                distance = self.distance_matrix[neighbor_client.client_id][i]
                if distance < lowest_distance:
                    lowest_distance = distance
                    closest_client = client
        return closest_client

    def create_initial_routes_partition(self):
        """
        Create the initial individual partition. We take a heuristic approach by creating sets starting with the
        highest client available and adding the closest neighbors until the set is close to being full. This approach
        allows us to start with a number of sets that should be close to optimal (no more than 2 times the optimal)
        :return: The initial partition of client sets
        """
        taken_clients = [self.starting_point]
        partition = Partition()
        while len(taken_clients) < self.clients_number+1:
            client = self.get_remaining_highest_volume_client(taken_clients)
            client_set = ClientSet()
            # We insert the closest node until an insert fails because the max volume was surpassed, or all clients have
            # been inserted to a route
            while len(taken_clients) < self.clients_number+1 and client_set.try_add_client(client):
                taken_clients.append(client)
                client = self.get_remaining_closest_distance_client(taken_clients, client)
            partition.add_client_set(client_set)
        partition.check_completion(self.client_array)
        if not partition.is_complete:
            raise Exception("Error in creating initial partition: not complete")
        partition.calculate_distance(self.starting_point, self.distance_matrix)
        return partition

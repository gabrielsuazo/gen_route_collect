import numpy as np
import numpy.typing as npt
import random

from source.client import Client
from source.partition import Partition, clone_partition


class Population:
    """
    A population is a group of partitions. Each new generation, a new population will be created from the existing one
    through selection, cloning and mutations.
    """

    def __init__(self, initial_partition: Partition, total_number: int, best_number: int):
        self.total_number = total_number
        self.best_number = best_number
        self.best_array = self.initialize_best_array(initial_partition)

    def initialize_best_array(self, initial_partition: Partition) -> npt.NDArray[Partition]:
        """
        Initialize the array containing that will contain the best partition of each generation. At the start, it is
        populated with clones of the initial partition.
        :param initial_partition: Initial partition to clone.
        :return: The best array.
        """
        best_array = np.ndarray((self.best_number,), dtype=Partition)
        for i in range(len(best_array)):
            best_array[i] = clone_partition(initial_partition)
        return best_array

    def create_new_generation(self) -> npt.NDArray[Partition]:
        """
        Create the new generation by cloning and mutating the partitions of the best array.
        :return: A new array containing the mutated clones
        """
        next_gen = np.ndarray((self.total_number - self.best_number,), dtype=Partition)
        for i in range(len(next_gen)):
            random_best_partition = random.choice(self.best_array)
            clone = clone_partition(random_best_partition)
            clone.random_mutation()
            next_gen[i] = clone
        return next_gen

    def update_best_array(self,
                          next_gen: npt.NDArray[Partition],
                          starting_point: Client,
                          distance_matrix: npt.NDArray[float]):
        """
        Update the best array by adding in decreasing order by distance the new partition that make the cut. The last
        partition of the best array will thus be the best partition of the generation.
        :param next_gen: The new generation of partition to test.
        :param starting_point: Starting point of the problem.
        :param distance_matrix: Distance matrix of costs
        :return:
        """
        for partition in next_gen:
            partition.calculate_distance(starting_point, distance_matrix)
            i = 0
            while i < len(self.best_array) and partition.distance < self.best_array[i].distance:
                i += 1
            if i != 0:
                print("Here! value of i is " + str(i))
                self.insert_best_at_index(partition, i-1)

    def insert_best_at_index(self, partition: Partition, index: int):
        """
        Insert a partition to the best array at the given index, moving all the others accordingly.
        :param partition: Partition to insert.
        :param index: Index of insertion
        :return:
        """
        for j in range(1, index + 1):
            self.best_array[j - 1] = self.best_array[j]
        self.best_array[index] = partition

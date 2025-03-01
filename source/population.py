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
        best_array = np.ndarray((self.best_number,), dtype=Partition)
        for i in range(len(best_array)):
            best_array[i] = clone_partition(initial_partition)
        return best_array

    def create_new_generation(self) -> npt.NDArray[Partition]:
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
        for partition in next_gen:
            partition.calculate_distance(starting_point, distance_matrix)
            for i in range(len(self.best_array)):
                if partition.distance < self.best_array[i].distance:
                    continue
                if i != 0:
                    self.insert_best_at_index(partition, i)

    def insert_best_at_index(self, partition: Partition, index: int):
        for j in range(1, index + 1):
            self.best_array[j - 1] = self.best_array[j]
        self.best_array[index] = partition

import numpy as np

from source.client import Client
from source.partition import Partition, clone_partition
from source.population import Population
from source.route import ClientSet


def test_initialize_best_array():
    partition = Partition()
    client_1 = Client(0)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    partition.add_client_set(client_set_1)
    population = Population(partition, 10, 3)
    assert len(population.best_array) == 3
    for clone in population.best_array:
        assert len(clone.client_sets) == 1
        assert client_set_1 in clone.client_sets


def test_create_new_generation():
    partition = Partition()
    client_1 = Client(0)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    partition.add_client_set(client_set_1)
    population = Population(partition, 10, 3)
    next_gen = population.create_new_generation()
    assert len(next_gen) == 7
    for clone in next_gen:
        assert len(clone.client_sets) == 1
        assert client_set_1 in clone.client_sets


def test_update_best_array():
    partition = Partition()
    starting_point = Client(0)
    client_set_1 = ClientSet()
    client_set_2 = ClientSet()
    client_set_all = ClientSet()
    for i in range(1, 5):
        if i // 2 == 0:
            client_set_1.try_add_client(Client(i))
        else:
            client_set_2.try_add_client(Client(i))
        client_set_all.try_add_client(Client(i))
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    distance_matrix = np.full((5, 5), 5.0)
    partition.calculate_distance(starting_point, distance_matrix)
    population = Population(partition, 10, 3)

    next_gen = np.ndarray((7,), dtype=Partition)
    best_partition = Partition()
    best_partition.add_client_set(client_set_all)
    next_gen[0] = best_partition
    for i in range(1, 7):
        next_gen[i] = clone_partition(partition)
    population.update_best_array(next_gen, starting_point, distance_matrix)
    assert population.best_array[2] == best_partition
    population.update_best_array(next_gen, starting_point, distance_matrix)
    assert population.best_array[1] == best_partition
    population.update_best_array(next_gen, starting_point, distance_matrix)
    assert population.best_array[0] == best_partition


def test_insert_best_at_index():
    partition_1 = Partition()
    partition_2 = Partition()
    client_set_1 = ClientSet()
    client_set_2 = ClientSet()
    client_set_all = ClientSet()
    for i in range(1, 5):
        if i // 2 == 0:
            client_set_1.try_add_client(Client(i))
        else:
            client_set_2.try_add_client(Client(i))
        client_set_all.try_add_client(Client(i))
    partition_1.add_client_set(client_set_1)
    partition_1.add_client_set(client_set_2)
    partition_2.add_client_set(client_set_all)
    population = Population(partition_1, 10, 3)
    population.insert_best_at_index(partition_2, 0)
    assert population.best_array[0] == partition_2
    assert population.best_array[1] == partition_1
    assert population.best_array[2] == partition_1
    population.insert_best_at_index(partition_2, 1)
    assert population.best_array[0] == partition_1
    assert population.best_array[1] == partition_2
    assert population.best_array[2] == partition_1
    population.insert_best_at_index(partition_2, 2)
    assert population.best_array[0] == partition_2
    assert population.best_array[1] == partition_1
    assert population.best_array[2] == partition_2
    population.insert_best_at_index(partition_1, 1)
    assert population.best_array[0] == partition_1
    assert population.best_array[1] == partition_1
    assert population.best_array[2] == partition_2

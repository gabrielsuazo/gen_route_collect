from source.client import Client
from source.params import MAXIMUM_VOLUME
from source.partition import Partition, clone_partition
from source.route import ClientSet
import numpy as np


def test_add_client_set():
    """
    Test of partition.add_client()
    :return:
    """
    partition = Partition()
    assert len(partition.client_sets) == 0
    client_set = ClientSet()
    partition.add_client_set(client_set)
    assert len(partition.client_sets) == 1
    assert client_set in partition.client_sets


def test_check_completion_1():
    """
    Test of partition.check_completion()
    :return:
    """
    clients = np.array([Client(i) for i in range(10)])
    partition = Partition()
    for client in clients:
        partition.check_completion(clients)
        assert not partition.is_complete
        client_set = ClientSet()
        client_set.try_add_client(client)
        partition.add_client_set(client_set)
    partition.check_completion(clients)
    assert partition.is_complete


def test_check_completion_2():
    """
    Test of partition.check_completion()
    :return:
    """
    clients = np.array([Client(i) for i in range(10)])
    partition = Partition()
    client_set = ClientSet()
    partition.add_client_set(client_set)
    for client in clients:
        partition.check_completion(clients)
        assert not partition.is_complete
        client_set.try_add_client(client)
    partition.check_completion(clients)
    assert partition.is_complete


def test_try_client_exchange_mutation_success():
    """
    Test of success of partition.try_client_exchange_mutation()
    :return:
    """
    partition = Partition()
    client_1 = Client(0)
    client_2 = Client(1)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    client_set_2 = ClientSet()
    client_set_2.try_add_client(client_2)
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    assert partition.try_client_exchange_mutation()
    assert len(partition.client_sets) == 2
    assert client_set_1.check_has_client(client_2)
    assert client_set_2.check_has_client(client_1)


def test_try_client_exchange_mutation_fail():
    """
    Test of fail of partition.try_client_exchange_mutation()
    :return:
    """
    partition = Partition()
    client_1 = Client(0)
    client_2 = Client(1)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    client_1.volume = MAXIMUM_VOLUME + 1  # will cause fail during exchange
    client_set_2 = ClientSet()
    client_set_2.try_add_client(client_2)
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    assert not partition.try_client_exchange_mutation()
    assert len(partition.client_sets) == 2
    assert client_set_1.check_has_client(client_1)
    assert client_set_2.check_has_client(client_2)


def test_try_client_transfer_mutation_success():
    """
    Test of success of partition.try_client_transfer_mutation()
    :return:
    """
    partition = Partition()
    client_1 = Client(0)
    client_2 = Client(1)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    client_set_2 = ClientSet()
    client_set_2.try_add_client(client_2)
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    assert partition.try_client_transfer_mutation()
    assert len(partition.client_sets) == 1
    assert ((client_set_1.check_has_client(client_2) and len(client_set_2.client_set) == 0)
            or (client_set_2.check_has_client(client_1) and len(client_set_1.client_set) == 0))


def test_try_client_transfer_mutation_fail():
    """
    Test of fail of partition.try_client_transfer_mutation()
    :return:
    """
    partition = Partition()
    client_1 = Client(0)
    client_2 = Client(1)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    client_1.volume = MAXIMUM_VOLUME + 1  # will cause fail during transfer
    client_set_2 = ClientSet()
    client_set_2.try_add_client(client_2)
    client_2.volume = MAXIMUM_VOLUME + 1  # will cause fail during transfer
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    assert not partition.try_client_transfer_mutation()
    assert len(partition.client_sets) == 2
    assert client_set_1.check_has_client(client_1)
    assert client_set_2.check_has_client(client_2)


def test_try_set_merge_mutation_success():
    """
    Test of success of partition.try_set_merge_mutation()
    :return:
    """
    partition = Partition()
    client_1 = Client(0)
    client_2 = Client(1)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    client_set_2 = ClientSet()
    client_set_2.try_add_client(client_2)
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    assert partition.try_set_merge_mutation()
    assert len(partition.client_sets) == 1
    assert ((client_set_1.check_has_client(client_2) and len(client_set_2.client_set) == 0)
            or (client_set_2.check_has_client(client_1) and len(client_set_1.client_set) == 0))


def test_try_set_merge_mutation_fail():
    """
    Test of fail of partition.try_set_merge_mutation()
    :return:
    """
    partition = Partition()
    client_1 = Client(0)
    client_2 = Client(1)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    client_set_1.volume = MAXIMUM_VOLUME + 1  # will cause fail during merge
    client_set_2 = ClientSet()
    client_set_2.try_add_client(client_2)
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    assert not partition.try_set_merge_mutation()
    assert len(partition.client_sets) == 2
    assert client_set_1.check_has_client(client_1)
    assert client_set_2.check_has_client(client_2)


def test_try_set_division_mutation_success():
    """
    Test of success of partition.try_set_division_mutation()
    :return:
    """
    partition = Partition()
    client_1 = Client(0)
    client_2 = Client(1)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    client_set_1.try_add_client(client_2)
    partition.add_client_set(client_set_1)
    assert partition.try_set_division_mutation()
    assert len(partition.client_sets) == 2
    assert len(client_set_1.client_set) == 1
    assert ((client_set_1.check_has_client(client_1) and not client_set_1.check_has_client(client_2))
            or (client_set_1.check_has_client(client_2) and not client_set_1.check_has_client(client_1)))


def test_try_set_division_mutation_fail():
    """
    Test of fail of partition.try_set_division_mutation()
    :return:
    """
    partition = Partition()
    client_1 = Client(0)
    client_2 = Client(1)
    client_set_1 = ClientSet()
    client_set_1.try_add_client(client_1)
    client_set_2 = ClientSet()
    client_set_2.try_add_client(client_2)
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    assert not partition.try_set_division_mutation()
    assert len(partition.client_sets) == 2
    assert ((client_set_1.check_has_client(client_1) and not client_set_1.check_has_client(client_2))
            and (client_set_2.check_has_client(client_2) and not client_set_2.check_has_client(client_1)))


def test_calculate_distance_1():
    """
    Test of partition.calculate_distance()
    :return:
    """
    partition = Partition()
    starting_point = Client(0)
    client_set = ClientSet()
    for i in range(1, 5):
        client_set.try_add_client(Client(i))
    partition.add_client_set(client_set)
    distance_matrix = np.full((5, 5), 5.0)
    partition.calculate_distance(starting_point, distance_matrix)
    assert partition.distance == 25.0
    distance_matrix = np.full((5, 5), 8.0)
    partition.calculate_distance(starting_point, distance_matrix)
    assert partition.distance == 40.0


def test_calculate_distance_2():
    """
    Test of partition.calculate_distance()
    :return:
    """
    partition = Partition()
    starting_point = Client(0)
    client_set_1 = ClientSet()
    client_set_2 = ClientSet()
    for i in range(1, 5):
        if i // 2 == 0:
            client_set_1.try_add_client(Client(i))
        else:
            client_set_2.try_add_client(Client(i))
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    distance_matrix = np.full((5, 5), 5.0)
    partition.calculate_distance(starting_point, distance_matrix)
    assert partition.distance == 30.0
    distance_matrix = np.full((5, 5), 8.0)
    partition.calculate_distance(starting_point, distance_matrix)
    assert partition.distance == 48.0


def test_clone_partition():
    """
    Test of clone_partition()
    :return:
    """
    partition = Partition()
    client_set_1 = ClientSet()
    client_set_2 = ClientSet()
    for i in range(1, 5):
        client = Client(i)
        client.capacity = i*10
        client.volume = i*5
        client.coordinates = (i, i)
        if i // 2 == 0:
            client_set_1.try_add_client(client)
        else:
            client_set_2.try_add_client(client)
    partition.add_client_set(client_set_1)
    partition.add_client_set(client_set_2)
    partition.distance = 10.0
    partition.is_complete = True
    clone = clone_partition(partition)
    assert clone.distance == 10.0
    assert clone.is_complete
    assert len(clone.client_sets) == 2
    assert client_set_1 in clone.client_sets
    assert client_set_2 in clone.client_sets

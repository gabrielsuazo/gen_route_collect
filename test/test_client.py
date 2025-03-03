from source.client import Client, calculate_distance_between_clients
from source.params import SIZE_X, SIZE_Y, CLIENT_VOLUME_RANGE


def test_randomize_client_params():
    """
    Test of client.randomize_client_params()
    :return:
    """
    client = Client(0)
    client.randomize_client_params()
    assert client.client_id == 0
    assert 0 <= client.coordinates[0] <= SIZE_X
    assert 0 <= client.coordinates[1] <= SIZE_Y
    assert CLIENT_VOLUME_RANGE[0] <= client.volume <= CLIENT_VOLUME_RANGE[1]
    assert client.volume <= client.capacity <= CLIENT_VOLUME_RANGE[1]


def test_calculate_distance_between_clients():
    """
    Test of calculate_distance_between_clients()
    :return:
    """
    client_1 = Client(0)
    client_1.coordinates = (0, 0)
    client_2 = Client(1)
    client_2.coordinates = (3, 4)
    assert calculate_distance_between_clients(client_1, client_2) == 5.0

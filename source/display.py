import numpy.typing as npt
from matplotlib import pyplot as plt

from source.client import Client
from source.params import CLIENT_VOLUME_RANGE, STARTING_POINT_COLOR, CLIENTS_COLORS, ROUTE_COLORS
from source.partition import Partition
from source.route import Route


def graph_clients_array(client_array: npt.NDArray[Client], show: bool = False):
    """
    Function to display graph with starting point and clients
    :param client_array: Client array to display
    :param show: Boolean to show or not
    :return:
    """
    for client in client_array:
        coord = client.coordinates
        x = coord[0]
        y = coord[1]
        if client.volume == 0:
            plt.scatter(x, y, marker='^', c=STARTING_POINT_COLOR)
        elif client.volume <= CLIENT_VOLUME_RANGE[0] + (CLIENT_VOLUME_RANGE[1] - CLIENT_VOLUME_RANGE[0]) / 3:
            plt.scatter(x, y, c=CLIENTS_COLORS[0])
        elif client.volume <= CLIENT_VOLUME_RANGE[0] + 2 * (CLIENT_VOLUME_RANGE[1] - CLIENT_VOLUME_RANGE[0]) / 3:
            plt.scatter(x, y, c=CLIENTS_COLORS[1])
        else:
            plt.scatter(x, y, c=CLIENTS_COLORS[2])
    if show:
        plt.show()


def graph_route(route: Route, color: str, show: bool = False):
    """
    Function to display route visiting clients and returning to the starting point
    :param route: Route to display
    :param color: Color of the route
    :param show: Boolean to show or not
    :return:
    """
    plt.plot((route.starting_point.coordinates[0], route.ordered_client_list[0].coordinates[0]),
             (route.starting_point.coordinates[1], route.ordered_client_list[0].coordinates[1]), c=color)
    for current_client, next_client in zip(route.ordered_client_list, route.ordered_client_list[1:]):
        plt.plot((current_client.coordinates[0], next_client.coordinates[0]),
                 (current_client.coordinates[1], next_client.coordinates[1]), c=color)
    plt.plot(
        (route.ordered_client_list[len(route.ordered_client_list)-1].coordinates[0],
         route.starting_point.coordinates[0]),
        (route.ordered_client_list[len(route.ordered_client_list)-1].coordinates[1],
         route.starting_point.coordinates[1]),
        c=color
    )
    if show:
        plt.show()


def graph_partition(partition: Partition, show: bool = False):
    """
    Function to display a partition with its set of best routes
    :param partition:
    :param colors:
    :param show:
    :return:
    """
    color_counter = 0
    for client_set in partition.client_sets:
        route = client_set.best_route
        color = ROUTE_COLORS[color_counter]
        graph_route(route, color, False)
        if color_counter == len(ROUTE_COLORS) - 1:
            color_counter = 0
        else:
            color_counter += 1
    if show:
        plt.show()

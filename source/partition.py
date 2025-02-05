from source.route import ClientSet


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

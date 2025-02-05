from source.display import graph_clients_array
from source.simulator import Simulator


def main():
    simulator = Simulator(clients_number=20)
    print(simulator.client_array)
    graph_clients_array(simulator.client_array)
    simulator.start_simulation()


if __name__ == "__main__":
    main()

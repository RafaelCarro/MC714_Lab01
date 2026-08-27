import random
import simpy

from Server import Server
from enum import Enum

class Strategy(Enum):
    RANDOM = "random"
    ROUND_ROBIN = "round_robin"
    SHORTEST_QUEUE = "shortest_queue"

class LoadBalancer():
    def __init__(self, env: simpy.Environment, servers: list[Server], strategy: Strategy, process_time: int = 0.00):
        """ A class that represent our load balancer.

        Attributes:
            env (Environment): SimPy environment for the simulation to run.
            servers (List[Server]): Instances of servers that the LoadBalancer can allocate requests.
            strategy (Strategy): Strategy used to balance requests between servers.
            process_time (int): Time eeded to route a request. 
        """

        self.env = env
        self.servers = servers
        self.strategy = strategy
        self.process_time = process_time

        self.num_servers = len(servers)
        self.total_requests = 0

    def route_request(self, request_id):
        """ Routes a request to a server by Strategy criteria.

        Routing takes "process_time" time units to complete

        Args:
            request_id (int): Id to identificate different request in the network.
        """
        dest_server = self.server_router()
        self.env.process(dest_server.run_request(request_id))
        print(f"{self.env.now:.3f} - ROUTER: Sent request {request_id} to Server {dest_server.name}")

    def server_router(self) -> Server:
        """ Gets the next server to be routed following LoadBalancer Strategy.

        Possible strategies:
            - RANDOM: Returns a random server
            - ROUND_ROBIN: Cycles sequentially between servers
            - SHORTEST_QUEUE: Returns the server minimum capacity 
            used and minimum queue length in case of draws.

        Returns:
            dest_server (Server): Next server to be routed.
        """

        if self.strategy == Strategy.RANDOM:
            return random.choice(self.servers)

        elif self.strategy == Strategy.ROUND_ROBIN:
            server_idx = self.total_requests % self.num_servers
            self.total_requests += 1
            return self.servers[server_idx]

        elif self.strategy == Strategy.SHORTEST_QUEUE:
            dest_server = self._get_min_queue_server()
            self.total_requests += 1
            return dest_server

    def _get_min_queue_server(self):
        min_server = self.servers[0]

        for s in self.servers:
            if len(s.resource.users) < len(min_server.resource.users):
                min_server = s
            elif len(s.resource.users) == len(min_server.resource.users) and \
            len(s.resource.queue) < len(min_server.resource.queue):
                min_server = s

        return min_server
        

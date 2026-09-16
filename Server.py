import random
import simpy

class Server():
    """ A class that represent our servers.

    Attributes:
        env (Environment): SimPy environment for the simulation to run.
        name (string): Name of the server.
        process_time_lambda (float): λ coefficent to determine the time needed to the server to process a request.
        resource (Resource): SimPy resource representing the capacity of slots of resources of the Server.
    """

    def __init__(self, env: simpy.Environment, name: str, metrics, capacity: int = 0, process_time_lambda: float = 1.0):
        """ Initialize the server with the necessary parameters.

        Args:
            env (Environment): SimPy environment for the simulation to run.
            name (string): Name of the server.
            process_time (float): Time needed to the server to process a request.
            capacity (int): Number of requests that the server can process before enqueuing.
        """
        self.env = env
        self.name = name
        self.process_time_lambda = process_time_lambda
        self.resource = simpy.Resource(env, capacity=capacity)
        self.metrics = metrics

    def run_request(self, request_id):
        """ Run a request through the server to process. Logs the start and end times alongside the server capacity.

        Args:
            request_id (int): Id to identificate different request in the network.
        """
        with self.resource.request() as req:
            yield req
            #print(f"{self.env.now:.3f} - Server {self.name}: Started processing request {request_id}. Capacity [{self.resource.count}/{self.resource.capacity}] - Queue [{len(self.resource.queue)}]")
            self.metrics.log_request_start(request_id, self.env.now)
            yield self.env.timeout(random.expovariate(self.process_time_lambda))
            #print(f"{self.env.now:.3f} - Server {self.name}: Finished processing request {request_id}. Capacity [{self.resource.count}/{self.resource.capacity}] - Queue [{len(self.resource.queue)}]")
            self.metrics.log_request_end(request_id, self.env.now)


    def get_stats(self):
        return (self.resource.users, self.resource.queue, self.resource.capacity)
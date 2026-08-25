import simpy

class Server():
    """ A class that represent our servers.

    Attributes:
        env (Environment): SimPy environment for the simulation to run.
        name (string): Name of the server.
        process_time (float): Time needed to the server to process a request.
        resource (Resource): SimPy resource representing the capacity of slots of resources of the Server.
    """

    def __init__(self, env, name, capacity, process_time):
        """ Initialize the server with the necessary parameters.

        Args:
            env (Environment): SimPy environment for the simulation to run.
            name (string): Name of the server.
            process_time (float): Time needed to the server to process a request.
            capacity (int): Number of requests that the server can process before enqueuing.
        """
        self.env = env
        self.name = name
        self.process_time = process_time
        self.resource = simpy.Resource(env, capacity=capacity)

    def run_request(self, request_id):
        """ Run a request through the server to process. Logs the start and end times alongside the server capacity.

        Args:
            request_id (int): Id to identificate different request in the network.
        """
        with self.resource.request() as req:
            yield req
            print(f"{self.env.now:.3f} - Server {self.name}: Started processing request {request_id}. Capacity [{self.resource.count}/{self.resource.capacity}] - Queue [{len(self.resource.queue)}]")
            yield self.env.timeout(self.process_time)
            print(f"{self.env.now:.3f} - Server {self.name}: Finished processing request {request_id}. Capacity [{self.resource.count}/{self.resource.capacity}] - Queue [{len(self.resource.queue)}]")

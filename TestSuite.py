import LoadBalancer
import simpy
import random
import Utils

from LoadBalancer import LoadBalancer, Strategy
from Server import Server
from Metrics import SimulationMetrics
def startTest(
        number_of_servers: int = 3,
        server_process_time_lambda: float = 1.0,
        server_capacity: int = 1,
        load_balancer_strategy: Strategy = Strategy.RANDOM,
        load_balancer_proccess_time: float = 0.0,
        arrival_time_lambda: float = 0.6,
        simulation_time_limit: float = 5000.0,
        warmup_time: float = 500.0,
        random_seed: int = 42):
    """ Run a complete server and Load Balancer simulation with the given configuration.

        Args:
            number_of_servers (int): Number of servers available to process requests.
            server_process_time_lambda (float): λ coefficient used to determine the
                server request processing time.
            server_capacity (int): Maximum number of requests that each server can
                process simultaneously.
            load_balancer_strategy (Strategy): Strategy used by the Load Balancer to
                select a server for each incoming request.
            load_balancer_proccess_time (float): Time required by the Load Balancer
                to process and forward a request.
            arrival_time_lambda (float): λ coefficient used to determine the time
                between request arrivals.
            simulation_time_limit (float): Maximum simulation time for the test.
            random_seed (int): Seed used to initialize the random number generator
                for reproducible simulation results.
    """
    random.seed(random_seed)
    
    env = simpy.Environment()
    metrics = SimulationMetrics(number_of_servers, simulation_time_limit)
    servers = [Server(env, str(i), metrics, server_capacity, server_process_time_lambda, ) for i in range(number_of_servers)]
    LB = LoadBalancer(env, servers, load_balancer_strategy, metrics, load_balancer_proccess_time, )

    env.process(Utils.request_generator(env, LB, metrics, arrival_time_lambda))

    print("Starting test with following parameters:\n" \
        f"number of servers: {number_of_servers}\n" \
        f"lambda of process time: {server_process_time_lambda}\n" \
        f"server capacity: {server_capacity}\n" \
        f"load balancer strategy: {load_balancer_strategy}\n" \
        f"time to load balancer process requests: {load_balancer_proccess_time}\n" \
        f"lambda of arrival intervals: {arrival_time_lambda}\n" \
        f"simulation time limit: {simulation_time_limit}\n" \
        f"random seed: {random_seed}\n")
    
    env.run(until=simulation_time_limit)

    print("\nFinishing test\n")

    return metrics
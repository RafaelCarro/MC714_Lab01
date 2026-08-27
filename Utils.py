import random
import simpy

from LoadBalancer import LoadBalancer

def request_generator(env: simpy.Environment, load_balancer: LoadBalancer, arrival_time_lambda: float = 0.6):
    """ Generate requests to send to Load Balancer following a Poisson distribution, commanded by the arrival_time_lambda.

    Args:
        env (Environment): SimPy environment for the simulation to run.
        load_balancer (LoadBalancer): LoadBalancer that will route the request to the servers.
        arrival_time_lambda (float): λ coefficent to determine the time between request arrivals.
    """
    request_id = 0

    while True:
        interarrival_time = random.expovariate(arrival_time_lambda)

        yield env.timeout(interarrival_time)

        load_balancer.route_request(request_id)
        request_id += 1

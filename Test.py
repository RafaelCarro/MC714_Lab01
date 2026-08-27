import simpy
import Utils

from LoadBalancer import LoadBalancer, Strategy
from Server import Server

# Test file, remove before submitting
def main():
    env = simpy.Environment()
    servers = [Server(env, str(i), 1, 1.0) for i in range(3)]
    LB = LoadBalancer(env, servers, Strategy.RANDOM, 0.0001)

    env.process(Utils.request_generator(env, LB, 0.6))

    env.run(until=200)

main()
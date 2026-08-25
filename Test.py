from Server import Server
from LoadBalancer import LoadBalancer, Strategy
import simpy

# Test file, remove before submitting
def main():
    env = simpy.Environment()
    servers = [Server(env, str(i), 15, 0.05) for i in range(3)]
    LB = LoadBalancer(env, servers, Strategy.SHORTEST_QUEUE, 0.0001)

    for i in range(1, 120):
        env.process(LB.route_request(i))
    env.run()

main()
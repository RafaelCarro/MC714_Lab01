from Server import Server
import simpy

# Test file, remove before submitting
def main():
    env = simpy.Environment()
    server_1 = Server(env, '1', 15, 0.05)
    for i in range(1, 22):
        env.process(server_1.run_request(i))
    env.run()

main()
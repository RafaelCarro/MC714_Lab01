import TestSuite
from LoadBalancer import Strategy
# Test file, remove before submitting
def main():

    lambdas = [0.6, 1.2, 1.8, 2.4, 2.7]
    strategies = [Strategy.RANDOM, Strategy.ROUND_ROBIN, Strategy.SHORTEST_QUEUE]
    simulation_time = 5000.0
    warmup_time = 500.0

    print("Iniciando a bateria de testes...\n")

    for arrival_lambda in lambdas:
        for strategy in strategies:
            print(f"{'='*60}")
            print(f"Configuração: Lambda = {arrival_lambda:.1f} | Estratégia = {strategy.name}")
            print(f"{'='*60}")

            metrics = TestSuite.startTest(
                    number_of_servers=3,
                    load_balancer_strategy=strategy,
                    arrival_time_lambda=arrival_lambda,
                    simulation_time_limit=simulation_time,
                    warmup_time=warmup_time,
                )

            print(metrics.calculateMetrics(warmup_time))

            






main()
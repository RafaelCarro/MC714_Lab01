import TestSuite
from LoadBalancer import Strategy
from Metrics import SimulationMetrics

# Change this value to get the lambda = 3.3 results
RUN_LAMBDA_3_3 = False

def main():

    lambdas = [0.6, 1.2, 1.8, 2.4, 2.7]
    seeds = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23]
    strategies = [Strategy.RANDOM, Strategy.ROUND_ROBIN, Strategy.SHORTEST_QUEUE]
    simulation_time = 5000.0
    warmup_time = 500.0
    results = []

    print("Iniciando a bateria de testes...\n")

    for arrival_lambda in lambdas:
        for strategy in strategies:
            for seed in seeds:
                print(f"{'='*60}")
                print(
                    f"Configuração: Lambda = {arrival_lambda:.1f} | "
                    f"Estratégia = {strategy.name} | Seed = {seed}"
                )
                print(f"{'='*60}")

                metrics = TestSuite.startTest(
                    number_of_servers=3,
                    load_balancer_strategy=strategy,
                    arrival_time_lambda=arrival_lambda,
                    simulation_time_limit=simulation_time,
                    warmup_time=warmup_time,
                    random_seed=seed,
                )

                result = metrics.calculateMetrics(warmup_time)
                results.append(result)
                print(result)

    if RUN_LAMBDA_3_3 :
        for strategy in strategies:
            for seed in seeds:
                print(f"{'='*60}")
                print(
                    f"Configuração: Lambda = {arrival_lambda:.1f} | "
                    f"Estratégia = {strategy.name} | Seed = {seed}"
                )
                print(f"{'='*60}")

                metrics = TestSuite.startTest(
                    number_of_servers=3,
                    load_balancer_strategy=strategy,
                    arrival_time_lambda=3.3,
                    simulation_time_limit=simulation_time,
                    warmup_time=warmup_time,
                    random_seed=seed,
                )

                result = metrics.calculateMetrics(warmup_time)
                results.append(result)
                print(result)
            

    report_path = SimulationMetrics.generate_report(results)
    print(f"Relatorio salvo em: {report_path}")

main()
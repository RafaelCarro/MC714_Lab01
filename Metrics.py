import csv
import math
import os
from collections import defaultdict

import matplotlib.pyplot as plt


class SimulationMetrics:
    """Collect request events and calculate simulation performance metrics."""

    def __init__(self, number_of_servers, simulation_time_limit,
                 strategy=None, arrival_lambda=None):
        """Initialize metric collection for one simulation configuration."""
        self.number_of_servers = number_of_servers
        self.simulation_time_limit = simulation_time_limit
        self.strategy = strategy
        self.arrival_lambda = arrival_lambda
        self.requests_logs = {}

    def log_request_arrival(self, request_id, arrival_time):
        """Create a log entry when a request enters the system."""
        self.requests_logs[request_id] = {
            "arrival_time": arrival_time,
            "start_time": None,
            "end_time": None,
            "server_name": None
        }

    def log_request_server(self, request_id, server_name):
        """Record the server selected to process a request."""
        self.requests_logs[request_id]["server_name"] = server_name

    def log_request_start(self, request_id, start_time):
        """Record when a server starts processing a request."""
        self.requests_logs[request_id]["start_time"] = start_time

    def log_request_end(self, request_id, end_time):
        """Record when a request finishes processing."""
        self.requests_logs[request_id]["end_time"] = end_time

    def calculateMetrics(self, warmup_time):
        """Calculate throughput, response time, queue size, and utilization."""

        time_window = self.simulation_time_limit - warmup_time

        finished_requests = 0
        total_response_time = 0.0
        total_window_service_time = 0
        total_window_number_requests_time = 0
        server_window_service_time = defaultdict(float)

        # Accumulate request and service times over the measurement window.
        for req, log in self.requests_logs.items():
            arrival = log["arrival_time"]
            start = log["start_time"]
            end = log["end_time"]

            if arrival >= self.simulation_time_limit:
                continue

            # Integrate N(t) by summing the time each request remains in the
            # system during the measurement window. Requests still active at
            # the simulation limit are counted until that limit.
            request_end = (
                min(end, self.simulation_time_limit)
                if end is not None else self.simulation_time_limit
            )
            request_start = max(arrival, warmup_time)
            if request_end > request_start:
                total_window_number_requests_time += request_end - request_start

            if end is None:
                continue

            # Requests arriving during warm-up must not affect request-based
            # metrics, even when they finish after the warm-up period.
            if arrival >= warmup_time and end > warmup_time:
                finished_requests += 1
                total_response_time += (end - arrival)

            if start is not None:
                start = max(start, warmup_time)
                end = min(end, self.simulation_time_limit)


                if (end - start) > 0:
                    total_window_service_time += (end - start)
                    server_window_service_time[log["server_name"]] += end - start

        # Convert the accumulated values into averages for the time window.
        throughput = finished_requests / time_window if time_window > 0 else 0

        e_response_time = (
            total_response_time / finished_requests
            if finished_requests > 0 else 0
        )

        e_number_requests = (
            total_window_number_requests_time / time_window
            if time_window > 0 else 0
        )

        system_total_capacity = self.number_of_servers * time_window
        utility = (
            total_window_service_time / system_total_capacity
            if system_total_capacity > 0 else 0
        )
        server_utilization = {
            str(server): server_window_service_time[str(server)] / time_window
            if time_window > 0 else 0
            for server in range(self.number_of_servers)
        }

        return {
            "strategy": self.strategy.value if hasattr(self.strategy, "value")
            else self.strategy,
            "arrival_lambda": self.arrival_lambda,
            "time_window": time_window,
            "finished_requests": finished_requests,
            "throughput": throughput,
            "expected_response_time": e_response_time,
            "average_requests_in_system": e_number_requests,
            "utility": utility,
            "server_utilization": server_utilization,
        }

    @staticmethod
    def aggregate_results(results):
        """Calculate means and 95% confidence intervals per configuration."""
        if not results:
            raise ValueError("At least one simulation result is required")

        # These metrics are aggregated across independent simulation replicas.
        metric_names = [
            "throughput",
            "expected_response_time",
            "average_requests_in_system",
        ]
        grouped_results = defaultdict(list)
        for result in results:
            key = (result.get("strategy"), result.get("arrival_lambda"))
            grouped_results[key].append(result)

        # The critical value for a 95% two-sided t interval with 9 degrees
        # of freedom is used because the experiment has ten replicas.
        t_critical = 2.262
        aggregated_results = []

        # Group replicas by strategy and arrival rate before computing statistics.
        for (strategy, arrival_lambda), replicas in sorted(grouped_results.items()):
            aggregated = {
                "strategy": strategy,
                "arrival_lambda": arrival_lambda,
                "replicas": len(replicas),
            }
            for metric_name in metric_names:
                values = [result.get(metric_name, 0) for result in replicas]
                mean = sum(values) / len(values)
                if len(values) > 1:
                    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
                    standard_error = math.sqrt(variance / len(values))
                    confidence_interval = t_critical * standard_error
                else:
                    confidence_interval = 0.0
                aggregated[f"{metric_name}_mean"] = mean
                aggregated[f"{metric_name}_ci95"] = confidence_interval
                aggregated[f"{metric_name}_ci95_lower"] = mean - confidence_interval
                aggregated[f"{metric_name}_ci95_upper"] = mean + confidence_interval
            server_names = sorted({
                server_name
                for replica in replicas
                for server_name in replica.get("server_utilization", {})
            })
            for server_name in server_names:
                values = [
                    replica.get("server_utilization", {}).get(server_name, 0)
                    for replica in replicas
                ]
                mean = sum(values) / len(values)
                if len(values) > 1:
                    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
                    confidence_interval = t_critical * math.sqrt(variance / len(values))
                else:
                    confidence_interval = 0.0
                prefix = f"server_{server_name}_utilization"
                aggregated[f"{prefix}_mean"] = mean
                aggregated[f"{prefix}_ci95"] = confidence_interval
                aggregated[f"{prefix}_ci95_lower"] = mean - confidence_interval
                aggregated[f"{prefix}_ci95_upper"] = mean + confidence_interval
            aggregated_results.append(aggregated)

        return aggregated_results

    @staticmethod
    def generate_report(results, output_dir="results"):
        """Save aggregated metrics to CSV and generate comparison charts."""
        aggregated_results = SimulationMetrics.aggregate_results(results)
        os.makedirs(output_dir, exist_ok=True)
        # Keep the exported metric columns consistent across all configurations.
        metric_names = [
            "throughput",
            "expected_response_time",
            "average_requests_in_system",
        ]
        columns = ["strategy", "arrival_lambda", "replicas"]
        for metric_name in metric_names:
            columns.extend([
                f"{metric_name}_mean",
                f"{metric_name}_ci95",
                f"{metric_name}_ci95_lower",
                f"{metric_name}_ci95_upper",
            ])
        server_names = sorted({
            server_name
            for result in results
            for server_name in result.get("server_utilization", {})
        })
        for server_name in server_names:
            prefix = f"server_{server_name}_utilization"
            columns.extend([
                f"{prefix}_mean",
                f"{prefix}_ci95",
                f"{prefix}_ci95_lower",
                f"{prefix}_ci95_upper",
            ])
        csv_path = os.path.join(output_dir, "metrics.csv")

        # Write numerical results separately from the analytical reference curve.
        with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(aggregated_results)

        strategies = sorted({str(result.get("strategy")) for result in aggregated_results})
        analytical_random_response_time = {
            0.6: 1.25,
            1.2: 1.6667,
            1.8: 2.5,
            2.4: 5.0,
            2.7: 10.0,
        }
        # Plot each metric and add confidence intervals for simulated values.
        for metric_name in metric_names:
            figure, axis = plt.subplots(figsize=(9, 6))
            for strategy in strategies:
                strategy_results = sorted(
                    (result for result in aggregated_results
                     if str(result.get("strategy")) == strategy),
                    key=lambda result: result.get("arrival_lambda") or 0,
                )
                means = [result[f"{metric_name}_mean"] for result in strategy_results]
                confidence_intervals = [
                    result[f"{metric_name}_ci95"] for result in strategy_results
                ]
                axis.plot(
                    [result.get("arrival_lambda") for result in strategy_results],
                    means,
                    marker="o",
                    label=strategy,
                )
                axis.errorbar(
                    [result.get("arrival_lambda") for result in strategy_results],
                    means,
                    yerr=confidence_intervals,
                    fmt="none",
                    capsize=4,
                    alpha=0.7,
                )
            if metric_name == "expected_response_time":
                # Analytical E[R] for the random strategy is a fixed reference.
                axis.plot(
                    list(analytical_random_response_time),
                    list(analytical_random_response_time.values()),
                    marker="o",
                    linestyle="--",
                    label="modeled random",
                )
            axis.set_title(metric_name.replace("_", " ").title())
            axis.set_xlabel("Arrival lambda")
            axis.set_ylabel(metric_name.replace("_", " "))
            axis.grid(True, alpha=0.3)
            axis.legend()
            figure.tight_layout()
            figure.savefig(
                os.path.join(output_dir, f"metrics_{metric_name}.png"),
                dpi=150,
            )
            plt.close(figure)

        # Generate a separate chart for the utilization of each server.
        figure, axis = plt.subplots(figsize=(9, 6))
        for strategy in strategies:
            strategy_results = sorted(
                (result for result in aggregated_results
                 if str(result.get("strategy")) == strategy),
                key=lambda result: result.get("arrival_lambda") or 0,
            )
            for server_name in server_names:
                prefix = f"server_{server_name}_utilization"
                means = [result[f"{prefix}_mean"] for result in strategy_results]
                confidence_intervals = [
                    result[f"{prefix}_ci95"] for result in strategy_results
                ]
                axis.plot(
                    [result.get("arrival_lambda") for result in strategy_results],
                    means,
                    marker="o",
                    label=f"{strategy} - U{server_name}",
                )
                axis.errorbar(
                    [result.get("arrival_lambda") for result in strategy_results],
                    means,
                    yerr=confidence_intervals,
                    fmt="none",
                    capsize=4,
                    alpha=0.7,
                )
        axis.set_title("Server Utilization (Ui)")
        axis.set_xlabel("Arrival lambda")
        axis.set_ylabel("Utilization")
        axis.grid(True, alpha=0.3)
        axis.legend()
        figure.tight_layout()
        figure.savefig(os.path.join(output_dir, "metrics_server_utilization.png"), dpi=150)
        plt.close(figure)

        return csv_path

    

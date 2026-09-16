class SimulationMetrics:
    def __init__(self, number_of_servers, simulation_time_limit):
        self.number_of_servers = number_of_servers
        self.simulation_time_limit = simulation_time_limit
        self.requests_logs = {}

    def log_request_arrival(self, request_id, arrival_time):
        self.requests_logs[request_id] = {
            "arrival_time": arrival_time,
            "start_time": None,
            "end_time": None,
            "server_name": None
        }

    def log_request_server(self, request_id, server_name):
        self.requests_logs[request_id]["server_name"] = server_name

    def log_request_start(self, request_id, start_time):
        self.requests_logs[request_id]["start_time"] = start_time

    def log_request_end(self, request_id, end_time):
        self.requests_logs[request_id]["end_time"] = end_time

    def calculateMetrics(self, warmup_time):

        time_window = self.simulation_time_limit - warmup_time

        finished_requests = 0
        total_response_time = 0.0
        total_window_service_time = 0

        for req, log in self.requests_logs.items():
            arrival = log["arrival_time"]
            start = log["start_time"]
            end = log["end_time"]

            if end is None:
                continue

            if end > warmup_time:
                finished_requests += 1                  # Used to calculate Throughput
                total_response_time += (end - arrival)  #Used to calculate E[R]

            if start is not None:
                start = max(start, warmup_time)
                end = min(end, self.simulation_time_limit)


                if (end - start) > 0:
                    total_window_service_time += (end - start)

        throughput = finished_requests / time_window

        e_response_time = total_response_time / finished_requests

        e_number_requests = throughput * e_response_time

        system_total_capacity = self.number_of_servers * time_window
        utility = total_window_service_time / system_total_capacity

        return {
            "time_window": time_window,
            "finished_requests": finished_requests,
            "throughput": throughput,
            "expected_response_time": e_response_time,
            "expected_number_requests": e_number_requests,
            "utility": utility 
        }


    
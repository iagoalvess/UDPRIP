class RoutingTable:
    def __init__(self, self_ip):
        self.self_ip = self_ip
        self.routes = {}  # exemplo: {'127.0.1.3': ('127.0.1.2', 20, '127.0.1.2')}

    def add_direct_route(self, neighbor_ip, weight):
        self.routes[neighbor_ip] = (neighbor_ip, weight, neighbor_ip)

    def update_route(self, destination, next_hop, cost, learned_from):
        current = self.routes.get(destination)
        if (
            current is None
            or cost < current[1]
            or (
                cost == current[1] and next_hop < current[0]
            )  # desempate
        ):
            self.routes[destination] = (next_hop, cost, learned_from)

    def remove_routes_from(self, neighbor_ip):
        to_remove = [
            dest for dest, (_, _, src) in self.routes.items() if src == neighbor_ip
        ]
        for dest in to_remove:
            del self.routes[dest]

    def build_update_message(self, source_ip, dest_ip, link_weight):
        distances = {}
        for dest, (next_hop, total_cost, learned_from) in self.routes.items():
            if learned_from == dest_ip:
                continue
            distances[dest] = total_cost
        distances[self.self_ip] = 0  # inclui a si mesmo com distância 0
        return {
            "type": "update",
            "source": source_ip,
            "destination": dest_ip,
            "distances": distances,
        }

    def get_next_hop(self, destination):
        route = self.routes.get(destination)
        return route[0] if route else None

    def get_distance(self, destination):
        route = self.routes.get(destination)
        return route[1] if route else float("inf")

    def has_route(self, destination):
        return destination in self.routes

    def __str__(self):
        return "\n".join(
            f"{dst} -> {nxt} (cost={c})" for dst, (nxt, c, _) in self.routes.items()
        )

import random

class RoutingTable:
    def __init__(self, self_ip):
        self.self_ip = self_ip
        self.routes = {}

    def add_direct_route(self, neighbor_ip, weight):
        if neighbor_ip in self.routes:
            current_entry = self.routes[neighbor_ip]
            if current_entry["cost"] > weight:
                self.routes[neighbor_ip] = {
                    "cost": weight,
                    "next_hops": [(neighbor_ip, neighbor_ip)],
                }
            elif current_entry["cost"] == weight:
                if (neighbor_ip, neighbor_ip) not in current_entry["next_hops"]:
                    current_entry["next_hops"].append((neighbor_ip, neighbor_ip))
        else:
            self.routes[neighbor_ip] = {
                "cost": weight,
                "next_hops": [(neighbor_ip, neighbor_ip)],
            }

    def update_route(self, destination, next_hop, cost, learned_from):
        if destination == self.self_ip:
            return
        current_entry = self.routes.get(destination)
        new_cost = cost

        if current_entry is None:
            self.routes[destination] = {
                "cost": new_cost,
                "next_hops": [(next_hop, learned_from)],
            }
        else:
            current_cost = current_entry["cost"]
            if new_cost < current_cost:
                self.routes[destination] = {
                    "cost": new_cost,
                    "next_hops": [(next_hop, learned_from)],
                }
            elif new_cost == current_cost:
                if (next_hop, learned_from) not in current_entry["next_hops"]:
                    current_entry["next_hops"].append((next_hop, learned_from))

    def remove_routes_from(self, neighbor_ip):
        for dest, entry in list(self.routes.items()):
            entry['next_hops'] = [
                (nh, lf) for (nh, lf) in entry['next_hops']
                if lf != neighbor_ip
            ]
            if not entry['next_hops']:
                del self.routes[dest]

    def remove_routes_without_list_neighbor(self, neighbor_id, list_neighbor):
        for dest, entry in list(self.routes.items()):
            entry['next_hops'] = [
                (nh, lf) for (nh, lf) in entry['next_hops']
                if not (lf == neighbor_id and dest not in list_neighbor)
            ]
            if not entry['next_hops']:
                del self.routes[dest]

    def build_update_message(self, source, dest_ip, link_weight):
        distances = {}
        for dest, entry in self.routes.items():
            learned_froms = [lf for (_, lf) in entry["next_hops"]]
            if dest_ip in learned_froms:
                continue
            distances[dest] = entry["cost"]
        distances[self.self_ip] = link_weight
        return {
            "type": "update",
            "source": source.address,
            "destination": dest_ip,
            "distances": distances,
        }

    def get_next_hop(self, destination):
        entry = self.routes.get(destination)
        if entry and entry["next_hops"]:
            return random.choice(entry["next_hops"])[0]
        return None

    def get_distance(self, destination):
        route = self.routes.get(destination)
        return route[1] if route else float("inf")

    def has_route(self, destination):
        return destination in self.routes

    def __str__(self):
        return "\n".join(
            f"{dest} -> cost={entry['cost']}, next_hops={entry['next_hops']}" 
            for dest, entry in self.routes.items()
        )

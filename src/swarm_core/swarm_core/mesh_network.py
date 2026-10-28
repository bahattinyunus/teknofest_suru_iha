#!/usr/bin/env python3
"""
Decentralized Ad-Hoc Mesh Networking & RF Propagation Engine for UAV Swarms.
Simulates realistic inter-drone RF link quality (RSSI), multi-hop packet routing,
packet loss, and electronic warfare (EW) jamming interference.
"""

import math
from typing import Dict, List, Tuple, Optional, Set, Any
from swarm_core.algorithms import Vector3


class MeshPacket:
    """Standard message packet routed across the swarm mesh."""
    def __init__(self,
                 source_id: int,
                 dest_id: int,
                 payload_type: str,
                 data: Any,
                 hop_limit: int = 5):
        self.source_id = source_id
        self.dest_id = dest_id
        self.payload_type = payload_type
        self.data = data
        self.hop_limit = hop_limit
        self.hops_taken: List[int] = [source_id]


class RadioChannel:
    """RF Propagation Model (Log-Distance Path Loss with Shadowing)."""
    def __init__(self,
                 freq_ghz: float = 2.4,
                 tx_power_dbm: float = 20.0,
                 rx_sensitivity_dbm: float = -85.0,
                 path_loss_exponent: float = 2.2):
        self.freq_ghz = freq_ghz
        self.tx_power_dbm = tx_power_dbm
        self.rx_sensitivity_dbm = rx_sensitivity_dbm
        self.path_loss_exp = path_loss_exponent
        # Reference path loss at 1 meter (Friis free-space equation)
        # PL0 = 20*log10(4*pi*d*f / c) = 20*log10(d) + 20*log10(f_MHz) - 27.55
        freq_mhz = freq_ghz * 1000.0
        self.pl_0 = 20.0 * math.log10(1.0) + 20.0 * math.log10(freq_mhz) - 27.55

    def calculate_rssi(self, distance_m: float) -> float:
        """Calculates received signal strength indicator (dBm) at given distance."""
        d = max(0.5, distance_m)
        path_loss = self.pl_0 + 10.0 * self.path_loss_exp * math.log10(d)
        rssi = self.tx_power_dbm - path_loss
        return rssi

    def can_communicate_direct(self, distance_m: float, noise_dbm: float = 0.0) -> bool:
        """Determines if a direct link can be closed above receiver sensitivity."""
        rssi = self.calculate_rssi(distance_m) - noise_dbm
        return rssi >= self.rx_sensitivity_dbm


class DecentralizedMeshNetwork:
    """
    Multi-Agent Ad-Hoc Mesh Routing & Packet Forwarding Engine.
    Discovers optimal multi-hop routes across swarm nodes when direct line-of-sight is lost.
    """
    def __init__(self,
                 max_direct_range_m: float = 35.0,
                 radio: Optional[RadioChannel] = None):
        self.max_direct_range = max_direct_range_m
        self.radio = radio or RadioChannel()
        self.node_positions: Dict[int, Vector3] = {}
        # Jammers: list of (center_pos, power_dbm, radius_m)
        self.jammers: List[Tuple[Vector3, float, float]] = []

    def update_node_position(self, node_id: int, pos: Vector3):
        self.node_positions[node_id] = pos

    def add_ew_jammer(self, pos: Vector3, power_dbm: float = 30.0, radius_m: float = 20.0):
        """Injects an electronic warfare jamming source creating local noise."""
        self.jammers.append((pos, power_dbm, radius_m))

    def get_jammer_noise_at(self, pos: Vector3) -> float:
        """Calculates cumulative jamming noise floor at position."""
        total_noise = 0.0
        for j_pos, pwr, radius in self.jammers:
            dist = pos.distance_to(j_pos)
            if dist < radius:
                # Noise intensity decreases linearly towards edge of jamming bubble
                noise = pwr * (1.0 - dist / radius)
                total_noise += noise
        return total_noise

    def are_connected_direct(self, id1: int, id2: int) -> bool:
        if id1 not in self.node_positions or id2 not in self.node_positions:
            return False

        p1 = self.node_positions[id1]
        p2 = self.node_positions[id2]
        dist = p1.distance_to(p2)

        if dist > self.max_direct_range:
            return False

        # Check jamming interference at midpoint
        midpoint = (p1 + p2) / 2.0
        noise = self.get_jammer_noise_at(midpoint)

        return self.radio.can_communicate_direct(dist, noise_dbm=noise)

    def build_adjacency_graph(self) -> Dict[int, Set[int]]:
        """Constructs network connectivity graph of all active nodes."""
        nodes = list(self.node_positions.keys())
        graph: Dict[int, Set[int]] = {nid: set() for nid in nodes}

        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                if self.are_connected_direct(n1, n2):
                    graph[n1].add(n2)
                    graph[n2].add(n1)

        return graph

    def find_multi_hop_route(self, source_id: int, dest_id: int) -> Optional[List[int]]:
        """
        Computes the shortest multi-hop forwarding route (BFS shortest path).
        Returns list of node IDs along the route [source, hop1, hop2, ..., dest], or None.
        """
        if source_id == dest_id:
            return [source_id]

        graph = self.build_adjacency_graph()
        if source_id not in graph or dest_id not in graph:
            return None

        # Standard Breadth-First Search for minimal hop count
        queue = [[source_id]]
        visited = {source_id}

        while queue:
            path = queue.pop(0)
            node = path[-1]

            if node == dest_id:
                return path

            for neighbor in sorted(list(graph.get(node, set()))):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        return None  # No path found (network partitioned)

    def route_packet(self, packet: MeshPacket) -> Tuple[bool, Optional[List[int]]]:
        """
        Attempts to route packet across the mesh.
        Returns: (success, route_taken)
        """
        route = self.find_multi_hop_route(packet.source_id, packet.dest_id)
        if route is None:
            return False, None

        if len(route) - 1 > packet.hop_limit:
            return False, None  # Exceeded TTL / hop limit

        packet.hops_taken = route
        return True, route

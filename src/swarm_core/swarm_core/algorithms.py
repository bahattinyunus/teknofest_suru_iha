"""
Algorithmic engines for autonomous drone swarms.
Includes Reynolds' Boids flocking, Multi-agent Formation Control,
Artificial Potential Fields (APF), Search & Rescue Patterns,
and Byzantine / Anomaly Detection for Cyber-Physical Security.
"""

import math
from typing import Dict, List, Tuple, Optional, Any, Set


class Vector3:
    """Lightweight 3D Vector for mathematical calculations."""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> 'Vector3':
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> 'Vector3':
        if scalar == 0:
            return Vector3(0.0, 0.0, 0.0)
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def magnitude_xy(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self) -> 'Vector3':
        mag = self.magnitude()
        if mag == 0:
            return Vector3(0.0, 0.0, 0.0)
        return self / mag

    def distance_to(self, other: 'Vector3') -> float:
        return (self - other).magnitude()

    def distance_xy_to(self, other: 'Vector3') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def clamp(self, max_val: float) -> 'Vector3':
        mag = self.magnitude()
        if mag > max_val and mag > 0:
            return (self / mag) * max_val
        return Vector3(self.x, self.y, self.z)

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


class BoidsController:
    """
    Bio-inspired Reynolds' Flocking model with Goal Attraction.
    Implements:
      1. Separation: steer to avoid crowding local flockmates.
      2. Alignment: steer towards the average heading/velocity of local flockmates.
      3. Cohesion: steer to move toward average position (center of mass) of local flockmates.
      4. Migration / Goal Attraction: steer towards target waypoint.
    """
    def __init__(self,
                 cohesion_weight: float = 1.0,
                 alignment_weight: float = 1.0,
                 separation_weight: float = 1.8,
                 goal_weight: float = 1.2,
                 perception_radius: float = 15.0,
                 safe_distance: float = 3.0,
                 max_speed: float = 5.0):
        self.cohesion_weight = cohesion_weight
        self.alignment_weight = alignment_weight
        self.separation_weight = separation_weight
        self.goal_weight = goal_weight
        self.perception_radius = perception_radius
        self.safe_distance = safe_distance
        self.max_speed = max_speed

    def compute_velocity(self,
                         current_pos: Vector3,
                         current_vel: Vector3,
                         neighbors: Dict[str, Tuple[Vector3, Vector3]],
                         goal_pos: Optional[Vector3] = None) -> Vector3:
        """
        Calculates flocking velocity command.
        neighbors: dict of neighbor_id -> (position_vec, velocity_vec)
        """
        if not neighbors and goal_pos is None:
            return Vector3(0.0, 0.0, 0.0)

        separation = Vector3(0.0, 0.0, 0.0)
        alignment = Vector3(0.0, 0.0, 0.0)
        cohesion_center = Vector3(0.0, 0.0, 0.0)
        neighbor_count = 0

        for n_id, (n_pos, n_vel) in neighbors.items():
            dist = current_pos.distance_to(n_pos)
            if 0.01 < dist <= self.perception_radius:
                neighbor_count += 1
                
                # Separation: inverse distance weighting for strong repulsion at close range
                if dist < self.safe_distance:
                    diff = current_pos - n_pos
                    # Repulsion inversely proportional to distance
                    repulsion = diff.normalized() * ((self.safe_distance - dist) / self.safe_distance)
                    separation = separation + repulsion
                
                # Alignment: accumulate neighbor velocities
                alignment = alignment + n_vel

                # Cohesion: accumulate neighbor positions
                cohesion_center = cohesion_center + n_pos

        force = Vector3(0.0, 0.0, 0.0)

        if neighbor_count > 0:
            # Finalize cohesion
            center_of_mass = cohesion_center / neighbor_count
            cohesion_force = (center_of_mass - current_pos).normalized() * self.cohesion_weight
            
            # Finalize alignment
            avg_velocity = alignment / neighbor_count
            alignment_force = (avg_velocity - current_vel).normalized() * self.alignment_weight

            # Finalize separation
            separation_force = separation * self.separation_weight

            force = force + cohesion_force + alignment_force + separation_force

        # Goal attraction
        if goal_pos is not None:
            goal_dist = current_pos.distance_to(goal_pos)
            if goal_dist > 0.1:
                goal_force = (goal_pos - current_pos).normalized() * self.goal_weight
                force = force + goal_force

        return force.clamp(self.max_speed)


class FormationController:
    """
    Leader-Follower and Virtual-Leader Multi-Agent Formation Engine.
    Supports V-Shape, Line, Column, Circle, and Matrix/Grid formations.
    """
    SUPPORTED_FORMATIONS = ['V_SHAPE', 'LINE', 'COLUMN', 'CIRCLE', 'GRID']

    def __init__(self,
                 formation_type: str = 'V_SHAPE',
                 spacing: float = 3.5,
                 kp: float = 1.0,
                 max_speed: float = 5.0):
        self.formation_type = formation_type.upper()
        self.spacing = spacing
        self.kp = kp
        self.max_speed = max_speed

    def get_slot_offset(self,
                        slot_index: int,
                        total_agents: int = 5,
                        heading_rad: float = 0.0) -> Vector3:
        """
        Computes 3D slot offset in body/world frame given drone slot_index (1-indexed).
        slot_index=1 is typically leader at origin (0, 0, 0).
        """
        if slot_index <= 1:
            return Vector3(0.0, 0.0, 0.0)

        offset_x, offset_y, offset_z = 0.0, 0.0, 0.0

        if self.formation_type == 'V_SHAPE':
            # V-Shape: leader at tip, followers alternating right (+y) and left (-y) behind leader
            wing_idx = (slot_index - 1 + 1) // 2  # 1, 1, 2, 2, 3, 3...
            side = 1.0 if (slot_index % 2 == 0) else -1.0
            angle_rad = math.radians(35.0)  # 35 deg swept wing
            offset_x = -wing_idx * self.spacing * math.cos(angle_rad)
            offset_y = side * wing_idx * self.spacing * math.sin(angle_rad)

        elif self.formation_type == 'LINE':
            # Horizontal rank / line abreast: across Y axis centered on leader
            # e.g., slot 2 -> +spacing, slot 3 -> -spacing, slot 4 -> +2*spacing...
            wing_idx = (slot_index - 1 + 1) // 2
            side = 1.0 if (slot_index % 2 == 0) else -1.0
            offset_x = 0.0
            offset_y = side * wing_idx * self.spacing

        elif self.formation_type == 'COLUMN':
            # Single file behind the leader along -X axis
            idx = slot_index - 1
            offset_x = -idx * self.spacing
            offset_y = 0.0

        elif self.formation_type == 'CIRCLE':
            # Escort ring / circular perimeter around center
            num_followers = max(1, total_agents - 1)
            angle = 2.0 * math.pi * (slot_index - 2) / num_followers
            radius = self.spacing * 1.5
            offset_x = radius * math.cos(angle)
            offset_y = radius * math.sin(angle)

        elif self.formation_type == 'GRID':
            # 2D Grid / Matrix formation
            cols = 3
            idx = slot_index - 1
            row = idx // cols
            col = idx % cols
            offset_x = -row * self.spacing
            offset_y = (col - (cols - 1) / 2.0) * self.spacing

        else:
            # Default to V_SHAPE fallback
            wing_idx = (slot_index - 1 + 1) // 2
            side = 1.0 if (slot_index % 2 == 0) else -1.0
            offset_x = -wing_idx * self.spacing * math.cos(math.radians(35.0))
            offset_y = side * wing_idx * self.spacing * math.sin(math.radians(35.0))

        # Rotate local offset by leader heading angle (heading_rad)
        rot_x = offset_x * math.cos(heading_rad) - offset_y * math.sin(heading_rad)
        rot_y = offset_x * math.sin(heading_rad) + offset_y * math.cos(heading_rad)

        return Vector3(rot_x, rot_y, offset_z)

    def compute_velocity(self,
                         current_pos: Vector3,
                         leader_pos: Vector3,
                         leader_vel: Vector3,
                         slot_index: int,
                         total_agents: int = 5,
                         leader_heading: float = 0.0) -> Vector3:
        """Calculates tracking velocity to maintain formation slot relative to leader."""
        offset = self.get_slot_offset(slot_index, total_agents, leader_heading)
        target_pos = leader_pos + offset

        error = target_pos - current_pos
        cmd_vel = (error * self.kp) + leader_vel
        return cmd_vel.clamp(self.max_speed)


class ArtificialPotentialField:
    """
    Artificial Potential Field (APF) with dynamic goal attraction,
    obstacle repulsion (LIDAR / sensor ranges), and velocity damping.
    """
    def __init__(self,
                 k_att: float = 1.0,
                 k_rep: float = 2.5,
                 d_safe: float = 3.0,
                 k_damping: float = 0.2,
                 max_speed: float = 5.0):
        self.k_att = k_att
        self.k_rep = k_rep
        self.d_safe = d_safe
        self.k_damping = k_damping
        self.max_speed = max_speed

    def compute_repulsion_from_scan(self,
                                    ranges: List[float],
                                    angle_min: float,
                                    angle_increment: float,
                                    range_min: float = 0.1) -> Vector3:
        """Computes obstacle repulsive force vector from 2D LiDAR scan ranges."""
        rep_x = 0.0
        rep_y = 0.0
        angle = angle_min

        for r in ranges:
            if range_min < r < self.d_safe:
                # Potential gradient: (1/r - 1/d_safe) * (1/r^2)
                magnitude = self.k_rep * (1.0 / max(r, 0.05) - 1.0 / self.d_safe) * (1.0 / max(r**2, 0.05))
                magnitude = min(magnitude, 10.0) # Clamp extreme forces
                rep_x -= magnitude * math.cos(angle)
                rep_y -= magnitude * math.sin(angle)
            angle += angle_increment

        return Vector3(rep_x, rep_y, 0.0)

    def compute_force(self,
                      current_pos: Vector3,
                      target_pos: Vector3,
                      current_vel: Vector3,
                      obstacle_ranges: Optional[List[float]] = None,
                      angle_min: float = -math.pi,
                      angle_inc: float = 0.01) -> Vector3:
        """Calculates total potential field control command."""
        # Attractive force to target
        dist_to_goal = current_pos.distance_to(target_pos)
        if dist_to_goal > 0.05:
            att_force = (target_pos - current_pos).normalized() * min(self.k_att * dist_to_goal, self.max_speed)
        else:
            att_force = Vector3(0.0, 0.0, 0.0)

        # Repulsive force from obstacles
        rep_force = Vector3(0.0, 0.0, 0.0)
        if obstacle_ranges:
            rep_force = self.compute_repulsion_from_scan(obstacle_ranges, angle_min, angle_inc)

        # Damping force to prevent oscillation near equilibrium
        damping = current_vel * self.k_damping

        total = att_force + rep_force - damping
        return total.clamp(self.max_speed)


class SearchPatternGenerator:
    """
    Search & Rescue Area Coverage Trajectory Generator.
    Supports Archimedean Expanding Spiral and Lawnmower (Boustrophedon) patterns.
    """
    @staticmethod
    def archimedean_spiral(t_seconds: float,
                           a: float = 0.5,
                           b: float = 0.2,
                           altitude: float = 10.0) -> Tuple[Vector3, Vector3]:
        """
        Computes position and velocity on Archimedean spiral: r = a + b * theta.
        Returns: (target_position, feedforward_velocity)
        """
        theta = b * t_seconds
        r = a * theta
        x = r * math.cos(theta)
        y = r * math.sin(theta)

        # Analytic derivative
        vx = a * b * math.cos(theta) - r * b * math.sin(theta)
        vy = a * b * math.sin(theta) + r * b * math.cos(theta)

        return Vector3(x, y, altitude), Vector3(vx, vy, 0.0)

    @staticmethod
    def lawnmower_grid(t_seconds: float,
                       width: float = 100.0,
                       height: float = 100.0,
                       lane_width: float = 10.0,
                       speed: float = 3.0,
                       altitude: float = 10.0) -> Tuple[Vector3, Vector3]:
        """
        Computes position and velocity for back-and-forth boustrophedon sweep.
        """
        total_lanes = max(1, int(height / lane_width))
        distance_travelled = t_seconds * speed
        lane_length = width

        # Simple continuous sweep mapping
        cycle_len = lane_length + lane_width
        lane_idx = int(distance_travelled / cycle_len) % total_lanes
        pos_in_lane = distance_travelled % cycle_len

        if pos_in_lane <= lane_length:
            if lane_idx % 2 == 0:
                x = pos_in_lane
                vx = speed
            else:
                x = lane_length - pos_in_lane
                vx = -speed
            y = lane_idx * lane_width
            vy = 0.0
        else:
            turn_progress = (pos_in_lane - lane_length) / lane_width
            x = lane_length if (lane_idx % 2 == 0) else 0.0
            y = (lane_idx + turn_progress) * lane_width
            vx = 0.0
            vy = speed

        return Vector3(x, y, altitude), Vector3(vx, vy, 0.0)


class AnomalyDetector:
    """
    Cyber-Physical Security & Byzantine Fault Detection for Swarm Nodes.
    Detects rogue drones, GNSS spoofing, teleportation, and physical constraint violations.
    """
    def __init__(self,
                 max_physical_speed: float = 20.0,
                 max_altitude: float = 120.0,
                 min_altitude: float = 0.0,
                 max_acceleration: float = 15.0):
        self.max_physical_speed = max_physical_speed
        self.max_altitude = max_altitude
        self.min_altitude = min_altitude
        self.max_acceleration = max_acceleration
        self.history: Dict[str, Tuple[Vector3, float]] = {}  # id -> (pos, timestamp)
        self.flagged_nodes: set = set()

    def inspect_neighbor(self,
                         node_id: str,
                         new_pos: Vector3,
                         timestamp: float) -> Tuple[bool, Optional[str]]:
        """
        Validates telemetry from neighbor.
        Returns: (is_valid, failure_reason)
        """
        # Altitude safety bounds check
        if new_pos.z < self.min_altitude or new_pos.z > self.max_altitude:
            self.flagged_nodes.add(node_id)
            return False, f"Node {node_id} altitude {new_pos.z:.1f}m outside legal bounds [{self.min_altitude}, {self.max_altitude}]"

        if node_id in self.history:
            prev_pos, prev_time = self.history[node_id]
            dt = timestamp - prev_time

            if dt > 0.001:
                displacement = new_pos.distance_to(prev_pos)
                apparent_speed = displacement / dt

                # Kinematic violation (Teleportation / GNSS Spoofing indicator)
                if apparent_speed > self.max_physical_speed:
                    self.flagged_nodes.add(node_id)
                    return False, f"Spoofing / Teleportation detected for {node_id}: speed {apparent_speed:.1f}m/s > max {self.max_physical_speed}m/s"

        self.history[node_id] = (new_pos, timestamp)
        return True, None

    def is_flagged(self, node_id: str) -> bool:
        return node_id in self.flagged_nodes

    def clear_flag(self, node_id: str):
        self.flagged_nodes.discard(node_id)


class FailSafeManager:
    """
    Manages autonomous health checks and safety overrides:
    - Return to Launch (RTL) on communication blackout or low battery
    - Emergency Land on critical hardware failure
    """
    def __init__(self,
                 heartbeat_timeout: float = 3.0,
                 min_battery_voltage: float = 14.0):
        self.heartbeat_timeout = heartbeat_timeout
        self.min_battery_voltage = min_battery_voltage
        self.current_state = 'NORMAL'  # NORMAL, DEGRADED, RTL, LAND

    def evaluate(self,
                 last_heartbeat_age: float,
                 battery_voltage: float = 16.0,
                 spoofing_active: bool = False) -> str:
        """Returns the appropriate operational or failsafe state."""
        if battery_voltage < self.min_battery_voltage:
            self.current_state = 'LAND'
            return self.current_state

        if last_heartbeat_age > self.heartbeat_timeout or spoofing_active:
            self.current_state = 'RTL'
            return self.current_state

        self.current_state = 'NORMAL'
        return self.current_state


class LeaderElectionEngine:
    """
    Decentralized Consensus & Dynamic Leader Election for Multi-UAV Swarms.
    Ensures autonomous fault-recovery if the primary flight leader crashes,
    runs out of battery, or is jammed by electronic warfare.
    """
    def __init__(self,
                 self_id: int,
                 initial_leader_id: int = 1,
                 heartbeat_timeout: float = 2.0):
        self.self_id = int(self_id)
        self.current_leader_id = int(initial_leader_id)
        self.heartbeat_timeout = heartbeat_timeout
        self.last_leader_heartbeat = 0.0
        self.term = 1

    def record_leader_heartbeat(self, leader_id: int, timestamp: float):
        if leader_id == self.current_leader_id:
            self.last_leader_heartbeat = timestamp

    def evaluate_election(self, timestamp: float, active_drone_ids: List[int]) -> int:
        """
        Evaluates leader health and conducts election if current leader timed out.
        Returns the active leader ID.
        """
        all_candidates = set(active_drone_ids)
        all_candidates.add(self.self_id)

        # If current leader is self, maintain leadership
        if self.current_leader_id == self.self_id:
            return self.self_id

        # Check if current leader timed out
        time_since_hb = timestamp - self.last_leader_heartbeat
        if time_since_hb > self.heartbeat_timeout:
            # Current leader is lost. Elect active candidate with lowest ID (Bully / deterministic Raft)
            eligible = sorted(list(all_candidates))
            if eligible:
                new_leader = eligible[0]
                if new_leader != self.current_leader_id:
                    self.current_leader_id = new_leader
                    self.term += 1
                    self.last_leader_heartbeat = timestamp
            return self.current_leader_id

        return self.current_leader_id

    def is_leader(self) -> bool:
        return self.self_id == self.current_leader_id


class GeofenceManager:
    """
    3D Geofence & Keep-Out No-Fly Zone (NFZ) Safety Enforcer.
    Calculates safety boundary repulsion forces to prevent flyaways.
    """
    def __init__(self,
                 bounds: Tuple[float, float, float, float, float, float] = (-50.0, 50.0, -50.0, 50.0, 0.5, 30.0),
                 safety_margin: float = 4.0,
                 k_barrier: float = 3.5):
        # bounds: (xmin, xmax, ymin, ymax, zmin, zmax)
        self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax = bounds
        self.safety_margin = safety_margin
        self.k_barrier = k_barrier
        # NFZs: list of (center_x, center_y, radius, min_z, max_z)
        self.nfzs: List[Tuple[float, float, float, float, float]] = []

    def add_nfz(self, x: float, y: float, radius: float, min_z: float = 0.0, max_z: float = 40.0):
        self.nfzs.append((x, y, radius, min_z, max_z))

    def is_inside(self, pos: Vector3) -> bool:
        return (self.xmin <= pos.x <= self.xmax and
                self.ymin <= pos.y <= self.ymax and
                self.zmin <= pos.z <= self.zmax)

    def is_in_nfz(self, pos: Vector3) -> bool:
        for cx, cy, r, min_z, max_z in self.nfzs:
            if min_z <= pos.z <= max_z:
                dist_xy = math.sqrt((pos.x - cx)**2 + (pos.y - cy)**2)
                if dist_xy < r:
                    return True
        return False

    def compute_boundary_force(self, pos: Vector3) -> Vector3:
        """Computes restorative repulsive force vector when approaching boundaries or NFZs."""
        fx, fy, fz = 0.0, 0.0, 0.0

        # X bounds
        if pos.x < self.xmin + self.safety_margin:
            dist = max(0.01, pos.x - self.xmin)
            fx += self.k_barrier * ((self.safety_margin - dist) / self.safety_margin)
        elif pos.x > self.xmax - self.safety_margin:
            dist = max(0.01, self.xmax - pos.x)
            fx -= self.k_barrier * ((self.safety_margin - dist) / self.safety_margin)

        # Y bounds
        if pos.y < self.ymin + self.safety_margin:
            dist = max(0.01, pos.y - self.ymin)
            fy += self.k_barrier * ((self.safety_margin - dist) / self.safety_margin)
        elif pos.y > self.ymax - self.safety_margin:
            dist = max(0.01, self.ymax - pos.y)
            fy -= self.k_barrier * ((self.safety_margin - dist) / self.safety_margin)

        # Z bounds (Floor & Ceiling)
        if pos.z < self.zmin + 1.5:
            fz += self.k_barrier * 1.5
        elif pos.z > self.zmax - self.safety_margin:
            dist = max(0.01, self.zmax - pos.z)
            fz -= self.k_barrier * ((self.safety_margin - dist) / self.safety_margin)

        # NFZ avoidance
        for cx, cy, r, min_z, max_z in self.nfzs:
            if min_z <= pos.z <= max_z:
                dist_xy = math.sqrt((pos.x - cx)**2 + (pos.y - cy)**2)
                effective_radius = r + self.safety_margin
                if dist_xy < effective_radius:
                    d = max(0.05, dist_xy)
                    rep = self.k_barrier * ((effective_radius - d) / self.safety_margin)
                    fx += rep * ((pos.x - cx) / d)
                    fy += rep * ((pos.y - cy) / d)

        return Vector3(fx, fy, fz)


class TargetTracker:
    """
    Cooperative Multi-Agent Target Recognition & Consensus Engine.
    Tracks detected competition ground targets / QR markers and eliminates false positives.
    """
    def __init__(self, confirmation_threshold: int = 2, proximity_radius: float = 5.0):
        self.confirmation_threshold = confirmation_threshold
        self.proximity_radius = proximity_radius
        # targets: target_id -> {'pos': Vector3, 'detectors': set, 'confirmed': bool, 'timestamp': float}
        self.targets: Dict[str, Dict[str, Any]] = {}

    def report_detection(self, target_id: str, pos: Vector3, detector_id: int, timestamp: float) -> bool:
        """
        Registers a detection report from a drone.
        Returns True if target achieved multi-agent confirmed status.
        """
        if target_id not in self.targets:
            self.targets[target_id] = {
                'pos': pos,
                'detectors': {detector_id},
                'confirmed': False,
                'timestamp': timestamp
            }
        else:
            t = self.targets[target_id]
            # Verify proximity to existing estimate
            if t['pos'].distance_to(pos) <= self.proximity_radius:
                t['detectors'].add(detector_id)
                # Running average position
                t['pos'] = (t['pos'] + pos) / 2.0
                t['timestamp'] = timestamp

        target = self.targets[target_id]
        if len(target['detectors']) >= self.confirmation_threshold:
            target['confirmed'] = True
            return True
        return False

    def get_confirmed_targets(self) -> List[Dict[str, Any]]:
        return [{'id': tid, 'pos': d['pos'], 'detectors': list(d['detectors'])}
                for tid, d in self.targets.items() if d['confirmed']]

#!/usr/bin/env python3
"""
Teknofest Swarm Commander Node
Autonomous Swarm Intelligence Core for Multi-UAV Systems.
Supports:
  - Bio-inspired Reynolds' Flocking (Boids with Cohesion, Alignment, Separation, Goal Attraction)
  - Multi-Agent Formations (V-Shape, Line, Column, Circle, Grid)
  - Artificial Potential Fields (APF) with Obstacle Repulsion
  - Autonomous Search & Rescue (SAR) Coverage Patterns
  - Cyber-Physical Security & Byzantine / GNSS Spoofing Intrusion Detection (IDS)
  - Autonomous Fail-Safe & Return-To-Launch (RTL) State Management
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from mavros_msgs.msg import State
from sensor_msgs.msg import LaserScan
import math
import json
import time
from datetime import datetime

from swarm_core.algorithms import (
    Vector3,
    BoidsController,
    FormationController,
    ArtificialPotentialField,
    SearchPatternGenerator,
    AnomalyDetector,
    FailSafeManager,
    LeaderElectionEngine,
    GeofenceManager,
    TargetTracker
)
from swarm_core.precision_engagement import PrecisionEngagementController


class SwarmCommander(Node):
    def __init__(self):
        super().__init__('swarm_commander')
        self.get_logger().info('Initializing Elite Swarm Commander Node...')

        # Declare ROS 2 parameters
        self.declare_parameter('swarm_id', 1)
        self.declare_parameter('total_drones', 5)
        self.declare_parameter('leader_id', 1)
        self.declare_parameter('cohesion_weight', 1.0)
        self.declare_parameter('alignment_weight', 1.0)
        self.declare_parameter('separation_weight', 1.8)
        self.declare_parameter('goal_weight', 1.2)
        self.declare_parameter('obstacle_weight', 2.5)
        self.declare_parameter('safe_distance', 3.0)
        self.declare_parameter('max_speed', 5.0)
        self.declare_parameter('perception_radius', 20.0)
        self.declare_parameter('mission_mode', 'BOIDS')  # BOIDS, FORMATION, SEARCH, APF, RTL
        self.declare_parameter('formation_type', 'V_SHAPE')  # V_SHAPE, LINE, COLUMN, CIRCLE, GRID
        self.declare_parameter('formation_spacing', 3.5)
        self.declare_parameter('search_pattern', 'SPIRAL')  # SPIRAL, LAWNMOWER
        self.declare_parameter('target_x', 0.0)
        self.declare_parameter('target_y', 0.0)
        self.declare_parameter('target_z', 10.0)
        self.declare_parameter('enable_logging', True)
        self.declare_parameter('log_interval', 1.0)
        self.declare_parameter('enable_security_ids', True)
        self.declare_parameter('failsafe_enabled', True)
        self.declare_parameter('enable_dynamic_election', True)
        self.declare_parameter('enable_geofence', True)
        self.declare_parameter('uav_role', 'STANDARD')  # SCOUT, RELAY, INTERCEPTOR, STANDARD

        self.swarm_id = self.get_parameter('swarm_id').value
        self.leader_id = self.get_parameter('leader_id').value
        self.uav_role = self.get_parameter('uav_role').value

        # Initialize Algorithmic Controllers
        self.boids = BoidsController(
            cohesion_weight=self.get_parameter('cohesion_weight').value,
            alignment_weight=self.get_parameter('alignment_weight').value,
            separation_weight=self.get_parameter('separation_weight').value,
            goal_weight=self.get_parameter('goal_weight').value,
            perception_radius=self.get_parameter('perception_radius').value,
            safe_distance=self.get_parameter('safe_distance').value,
            max_speed=self.get_parameter('max_speed').value
        )

        self.formation = FormationController(
            formation_type=self.get_parameter('formation_type').value,
            spacing=self.get_parameter('formation_spacing').value,
            kp=1.0,
            max_speed=self.get_parameter('max_speed').value
        )

        self.apf = ArtificialPotentialField(
            k_att=1.0,
            k_rep=self.get_parameter('obstacle_weight').value,
            d_safe=self.get_parameter('safe_distance').value,
            k_damping=0.2,
            max_speed=self.get_parameter('max_speed').value
        )

        self.anomaly_detector = AnomalyDetector(
            max_physical_speed=25.0,
            max_altitude=150.0,
            min_altitude=0.0
        )

        self.failsafe = FailSafeManager(heartbeat_timeout=3.0)

        self.election_engine = LeaderElectionEngine(
            self_id=self.swarm_id,
            initial_leader_id=self.leader_id,
            heartbeat_timeout=2.0
        )

        self.geofence = GeofenceManager(
            bounds=(-50.0, 50.0, -50.0, 50.0, 0.5, 30.0),
            safety_margin=4.0,
            k_barrier=3.5
        )

        self.target_tracker = TargetTracker()
        self.engagement_controller = PrecisionEngagementController(
            cruise_alt=self.get_parameter('target_z').value,
            drop_alt=2.0,
            approach_speed=self.get_parameter('max_speed').value * 0.8
        )

        # Internal State
        self.current_state = State()
        self.latest_scan = None
        self.current_pose = PoseStamped()
        self.current_vel = Vector3(0.0, 0.0, 0.0)
        self.prev_pose_time = time.time()
        self.home_pos = Vector3(0.0, 0.0, 10.0)
        self.home_set = False

        # Neighbors storage: id -> {'pos': Vector3, 'vel': Vector3, 'time': float}
        self.neighbors = {}

        self.start_time = self.get_clock().now()
        self.last_log_time = self.get_clock().now()
        self.mission_data = []

        # Telemetry Logging Setup
        self.enable_logging = self.get_parameter('enable_logging').value
        if self.enable_logging:
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.log_file = f"mission_log_drone_{self.swarm_id}_{timestamp_str}.json"
            self.get_logger().info(f"Telemetry logging active: {self.log_file}")

        # Publishers
        self.vel_pub = self.create_publisher(
            Twist,
            'mavros/setpoint_velocity/cmd_vel_unstamped',
            10
        )

        self.my_pose_pub = self.create_publisher(
            PoseStamped,
            '/swarm/positions',
            10
        )

        # Subscribers
        self.state_sub = self.create_subscription(
            State,
            'mavros/state',
            self.state_cb,
            10
        )

        self.local_pose_sub = self.create_subscription(
            PoseStamped,
            'mavros/local_position/pose',
            self.local_pose_cb,
            10
        )

        self.swarm_pose_sub = self.create_subscription(
            PoseStamped,
            '/swarm/positions',
            self.swarm_pose_cb,
            10
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_cb,
            10
        )

        # Main Control Loop (10 Hz)
        self.control_timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info(f"Swarm Drone [{self.swarm_id}] operational in mode [{self.get_parameter('mission_mode').value}].")

    def state_cb(self, msg: State):
        self.current_state = msg

    def scan_cb(self, msg: LaserScan):
        self.latest_scan = msg

    def local_pose_cb(self, msg: PoseStamped):
        """Processes own local pose from MAVROS, estimates velocity, and broadcasts."""
        now_sec = time.time()
        dt = now_sec - self.prev_pose_time

        if dt > 0.001:
            vx = (msg.pose.position.x - self.current_pose.pose.position.x) / dt
            vy = (msg.pose.position.y - self.current_pose.pose.position.y) / dt
            vz = (msg.pose.position.z - self.current_pose.pose.position.z) / dt
            self.current_vel = Vector3(vx, vy, vz)

        self.current_pose = msg
        self.prev_pose_time = now_sec

        if not self.home_set and msg.pose.position.z > 0.5:
            self.home_pos = Vector3(msg.pose.position.x, msg.pose.position.y, msg.pose.position.z)
            self.home_set = True

        # Broadcast position to swarm mesh with drone ID in frame_id
        broadcast_msg = PoseStamped()
        broadcast_msg.header.stamp = self.get_clock().now().to_msg()
        broadcast_msg.header.frame_id = str(self.swarm_id)
        broadcast_msg.pose = msg.pose
        self.my_pose_pub.publish(broadcast_msg)

    def swarm_pose_cb(self, msg: PoseStamped):
        """Receives poses from peer drones, applies security filtering and estimates neighbor velocity."""
        sender_id = msg.header.frame_id
        if not sender_id or sender_id == str(self.swarm_id):
            return

        now_sec = time.time()
        new_pos = Vector3(msg.pose.position.x, msg.pose.position.y, msg.pose.position.z)

        # Cyber-Physical Security / Intrusion Detection check
        if self.get_parameter('enable_security_ids').value:
            is_valid, reason = self.anomaly_detector.inspect_neighbor(sender_id, new_pos, now_sec)
            if not is_valid:
                self.get_logger().warn(f"SECURITY ALERT: Discarding malicious node {sender_id}: {reason}")
                if sender_id in self.neighbors:
                    del self.neighbors[sender_id]
                return

        # Estimate neighbor velocity
        n_vel = Vector3(0.0, 0.0, 0.0)
        if sender_id in self.neighbors:
            prev = self.neighbors[sender_id]
            dt = now_sec - prev['time']
            if dt > 0.001:
                n_vel = (new_pos - prev['pos']) / dt

        # Record leader heartbeat for dynamic election
        if sender_id == str(self.leader_id):
            self.election_engine.record_leader_heartbeat(self.leader_id, now_sec)

        # Distance filter (only keep neighbors within perception radius)
        curr_vec = Vector3(
            self.current_pose.pose.position.x,
            self.current_pose.pose.position.y,
            self.current_pose.pose.position.z
        )
        if curr_vec.distance_to(new_pos) <= self.get_parameter('perception_radius').value:
            self.neighbors[sender_id] = {
                'pos': new_pos,
                'vel': n_vel,
                'time': now_sec
            }
        elif sender_id in self.neighbors:
            del self.neighbors[sender_id]

    def prune_stale_neighbors(self):
        """Removes peers that have not reported telemetry within 2.5 seconds."""
        now_sec = time.time()
        stale_ids = [n_id for n_id, data in self.neighbors.items() if (now_sec - data['time']) > 2.5]
        for s_id in stale_ids:
            del self.neighbors[s_id]

    def calculate_obstacle_avoidance(self) -> Vector3:
        """Calculates obstacle repulsion from 2D LaserScan."""
        if not self.latest_scan or not self.latest_scan.ranges:
            return Vector3(0.0, 0.0, 0.0)

        return self.apf.compute_repulsion_from_scan(
            ranges=list(self.latest_scan.ranges),
            angle_min=self.latest_scan.angle_min,
            angle_increment=self.latest_scan.angle_increment,
            range_min=self.latest_scan.range_min
        )

    def calculate_boids_cmd(self) -> Vector3:
        """Calculates comprehensive Boids flocking velocity with goal attraction."""
        curr_pos = Vector3(
            self.current_pose.pose.position.x,
            self.current_pose.pose.position.y,
            self.current_pose.pose.position.z
        )

        neighbors_map = {n_id: (d['pos'], d['vel']) for n_id, d in self.neighbors.items()}

        goal = Vector3(
            self.get_parameter('target_x').value,
            self.get_parameter('target_y').value,
            self.get_parameter('target_z').value
        )
        return self.boids.compute_velocity(curr_pos, self.current_vel, neighbors_map, goal)

    def calculate_formation_cmd(self) -> Vector3:
        """Calculates Leader-Follower formation tracking velocity."""
        curr_pos = Vector3(
            self.current_pose.pose.position.x,
            self.current_pose.pose.position.y,
            self.current_pose.pose.position.z
        )

        # If this drone is the leader, navigate towards mission target or flock
        if self.swarm_id == self.leader_id:
            target = Vector3(
                self.get_parameter('target_x').value,
                self.get_parameter('target_y').value,
                self.get_parameter('target_z').value
            )
            err = target - curr_pos
            return (err * 0.8).clamp(self.get_parameter('max_speed').value)

        # Follower logic
        leader_key = str(self.leader_id)
        if leader_key in self.neighbors:
            leader_pos = self.neighbors[leader_key]['pos']
            leader_vel = self.neighbors[leader_key]['vel']
            total_agents = self.get_parameter('total_drones').value

            # Heading estimation from velocity
            heading = math.atan2(leader_vel.y, leader_vel.x) if leader_vel.magnitude_xy() > 0.1 else 0.0

            return self.formation.compute_velocity(
                current_pos=curr_pos,
                leader_pos=leader_pos,
                leader_vel=leader_vel,
                slot_index=self.swarm_id,
                total_agents=total_agents,
                leader_heading=heading
            )

        # Fallback to Boids if leader is temporarily out of range
        return self.calculate_boids_cmd()

    def calculate_search_cmd(self) -> Vector3:
        """Computes velocity for Search & Rescue coverage pattern."""
        pattern = self.get_parameter('search_pattern').value
        t_sec = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        curr_pos = Vector3(
            self.current_pose.pose.position.x,
            self.current_pose.pose.position.y,
            self.current_pose.pose.position.z
        )

        if pattern == 'LAWNMOWER':
            target_pos, ff_vel = SearchPatternGenerator.lawnmower_grid(
                t_seconds=t_sec,
                width=80.0,
                height=80.0,
                lane_width=12.0,
                speed=self.get_parameter('max_speed').value * 0.6
            )
        else:  # Default: SPIRAL
            target_pos, ff_vel = SearchPatternGenerator.archimedean_spiral(
                t_seconds=t_sec,
                a=0.6,
                b=0.25,
                altitude=self.get_parameter('target_z').value
            )

        err = target_pos - curr_pos
        cmd = (err * 0.6) + ff_vel
        return cmd.clamp(self.get_parameter('max_speed').value)

    def calculate_apf_cmd(self) -> Vector3:
        """Computes velocity via Artificial Potential Field towards target waypoint."""
        curr_pos = Vector3(
            self.current_pose.pose.position.x,
            self.current_pose.pose.position.y,
            self.current_pose.pose.position.z
        )
        target_pos = Vector3(
            self.get_parameter('target_x').value,
            self.get_parameter('target_y').value,
            self.get_parameter('target_z').value
        )
        ranges = list(self.latest_scan.ranges) if self.latest_scan else None
        angle_min = self.latest_scan.angle_min if self.latest_scan else -math.pi
        angle_inc = self.latest_scan.angle_increment if self.latest_scan else 0.01

        return self.apf.compute_force(
            current_pos=curr_pos,
            target_pos=target_pos,
            current_vel=self.current_vel,
            obstacle_ranges=ranges,
            angle_min=angle_min,
            angle_inc=angle_inc
        )

    def calculate_rtl_cmd(self) -> Vector3:
        """Fail-Safe Return-to-Launch navigation."""
        curr_pos = Vector3(
            self.current_pose.pose.position.x,
            self.current_pose.pose.position.y,
            self.current_pose.pose.position.z
        )
        err = self.home_pos - curr_pos
        return (err * 0.7).clamp(self.get_parameter('max_speed').value)

    def control_loop(self):
        """Main periodic control loop at 10 Hz."""
        self.prune_stale_neighbors()
        mode = self.get_parameter('mission_mode').value
        curr_pos = Vector3(
            self.current_pose.pose.position.x,
            self.current_pose.pose.position.y,
            self.current_pose.pose.position.z
        )

        # Autonomous Dynamic Leader Election evaluation
        if self.get_parameter('enable_dynamic_election').value:
            now_sec = time.time()
            active_ids = [int(nid) for nid in self.neighbors.keys() if nid.isdigit()]
            new_leader = self.election_engine.evaluate_election(now_sec, active_ids)
            if new_leader != self.leader_id:
                self.get_logger().info(f"Otonom Lider Değişimi: Yeni Lider İHA-{new_leader}")
                self.leader_id = new_leader

        # Evaluate FailSafe state
        if self.get_parameter('failsafe_enabled').value:
            # Check if active neighbors exist or communication is degraded
            age = 0.0 if self.neighbors else 4.0
            fs_state = self.failsafe.evaluate(last_heartbeat_age=age)
            if fs_state == 'RTL':
                mode = 'RTL'

        # Compute velocity command by mode
        if mode == 'FORMATION':
            cmd_vec = self.calculate_formation_cmd()
        elif mode == 'SEARCH':
            cmd_vec = self.calculate_search_cmd()
        elif mode == 'APF':
            cmd_vec = self.calculate_apf_cmd()
        elif mode == 'ENGAGE':
            cmd_vec, eng_state, is_done = self.engagement_controller.update(curr_pos, time.time())
            if is_done:
                self.get_logger().info("Hedef Görevi Tamamlandı, Formasyona Dönülüyor...")
                mode = 'FORMATION'
        elif mode == 'RTL':
            cmd_vec = self.calculate_rtl_cmd()
        else:
            cmd_vec = self.calculate_boids_cmd()

        # Add obstacle avoidance repulsive force (except for APF which does it internally)
        if mode != 'APF':
            obs_force = self.calculate_obstacle_avoidance()
            cmd_vec = cmd_vec + obs_force

        # Geofence boundary & Keep-Out NFZ enforcement
        if self.get_parameter('enable_geofence').value:
            geo_force = self.geofence.compute_boundary_force(curr_pos)
            cmd_vec = cmd_vec + geo_force

        cmd_vec = cmd_vec.clamp(self.get_parameter('max_speed').value)

        # Publish Twist command
        twist_msg = Twist()
        twist_msg.linear.x = cmd_vec.x
        twist_msg.linear.y = cmd_vec.y
        twist_msg.linear.z = cmd_vec.z
        self.vel_pub.publish(twist_msg)

        # Telemetry Recording
        if self.enable_logging:
            now = self.get_clock().now()
            dt = (now - self.last_log_time).nanoseconds / 1e9
            if dt >= self.get_parameter('log_interval').value:
                record = {
                    "timestamp": now.to_msg().sec,
                    "drone_id": self.swarm_id,
                    "uav_role": self.uav_role,
                    "mode": mode,
                    "pose": {
                        "x": self.current_pose.pose.position.x,
                        "y": self.current_pose.pose.position.y,
                        "z": self.current_pose.pose.position.z
                    },
                    "velocity": {
                        "x": cmd_vec.x,
                        "y": cmd_vec.y,
                        "z": cmd_vec.z
                    },
                    "neighbors_count": len(self.neighbors),
                    "active_leader_id": self.leader_id,
                    "geofence_inside": self.geofence.is_inside(curr_pos),
                    "anomalous_nodes": list(self.anomaly_detector.flagged_nodes),
                    "failsafe_status": self.failsafe.current_state
                }
                self.mission_data.append(record)
                self.last_log_time = now

                try:
                    with open(self.log_file, 'w') as f:
                        json.dump(self.mission_data, f, indent=4)
                except Exception as e:
                    self.get_logger().error(f"Failed to write telemetry: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = SwarmCommander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Fast Swarm SITL & Kinematic Simulator Engine
Simulates multi-UAV physics, LiDAR raycasting, MAVLink telemetry,
and ROS 2 topic bridges for rapid algorithm benchmarking without requiring Gazebo.
"""

import math
import time
from typing import List, Dict, Any

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import PoseStamped, Twist
    from mavros_msgs.msg import State
    from sensor_msgs.msg import LaserScan
    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False


class SimulatedUAV:
    def __init__(self, uav_id: int, init_x: float, init_y: float, init_z: float = 10.0):
        self.id = uav_id
        self.x = init_x
        self.y = init_y
        self.z = init_z
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.cmd_vx = 0.0
        self.cmd_vy = 0.0
        self.cmd_vz = 0.0

    def update(self, dt: float):
        # 1st-order drag & velocity response
        response_rate = 3.0  # rad/s
        self.vx += (self.cmd_vx - self.vx) * min(1.0, dt * response_rate)
        self.vy += (self.cmd_vy - self.vy) * min(1.0, dt * response_rate)
        self.vz += (self.cmd_vz - self.vz) * min(1.0, dt * response_rate)

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z = max(0.0, self.z + self.vz * dt)


class FastSwarmSim:
    """Multi-UAV physical dynamics & LiDAR simulation."""
    def __init__(self, num_drones: int = 5):
        self.num_drones = num_drones
        self.drones: Dict[int, SimulatedUAV] = {}
        # Obstacles: (x, y, radius)
        self.obstacles = [
            (15.0, 10.0, 1.5),
            (-20.0, -15.0, 1.5),
            (0.0, 25.0, 2.0)
        ]

        # Initialize drones on launch line with 3m spacing
        for i in range(1, num_drones + 1):
            init_x = -15.0
            init_y = (i - 1 - (num_drones - 1) / 2.0) * 3.5
            self.drones[i] = SimulatedUAV(i, init_x, init_y, 10.0)

    def step(self, dt: float = 0.05):
        for drone in self.drones.values():
            drone.update(dt)

    def generate_lidar_scan(self, drone: SimulatedUAV, num_rays: int = 36) -> List[float]:
        """Raycasts 2D laser scan against cylindrical obstacles."""
        ranges = [30.0] * num_rays
        angle_step = (2.0 * math.pi) / num_rays

        for ray_idx in range(num_rays):
            angle = ray_idx * angle_step
            ray_dx = math.cos(angle)
            ray_dy = math.sin(angle)

            for ox, oy, r in self.obstacles:
                # Vector from drone to obstacle
                to_ox = ox - drone.x
                to_oy = oy - drone.y

                # Projection of obstacle center onto ray
                proj = to_ox * ray_dx + to_oy * ray_dy
                if proj > 0:
                    # Perpendicular distance to ray
                    perp_sq = (to_ox**2 + to_oy**2) - (proj**2)
                    if perp_sq < (r**2):
                        dist_to_surface = max(0.1, proj - math.sqrt(r**2 - perp_sq))
                        if dist_to_surface < ranges[ray_idx]:
                            ranges[ray_idx] = dist_to_surface

        return ranges


if HAS_ROS2:
    class MockSITLBridgeNode(Node):
        def __init__(self):
            super().__init__('mock_sitl_bridge')
            self.declare_parameter('num_drones', 5)
            n_drones = self.get_parameter('num_drones').value

            self.sim = FastSwarmSim(num_drones=n_drones)
            self.get_logger().info(f"Hızlı Çoklu İHA SITL Simülatörü Başlatıldı ({n_drones} İHA)")

            self.pose_publishers = {}
            self.scan_publishers = {}
            self.vel_subscribers = {}

            for d_id in self.sim.drones.keys():
                # Publish local pose: /drone_i/mavros/local_position/pose
                ns = f"drone_{d_id}"
                self.pose_publishers[d_id] = self.create_publisher(
                    PoseStamped, f"/{ns}/mavros/local_position/pose", 10
                )
                self.scan_publishers[d_id] = self.create_publisher(
                    LaserScan, f"/{ns}/scan", 10
                )
                # Subscribe to velocity command
                self.vel_subscribers[d_id] = self.create_subscription(
                    Twist,
                    f"/{ns}/mavros/setpoint_velocity/cmd_vel_unstamped",
                    lambda msg, uid=d_id: self.cmd_vel_cb(uid, msg),
                    10
                )

            # Simulation physics loop at 20 Hz
            self.sim_timer = self.create_timer(0.05, self.sim_loop)

        def cmd_vel_cb(self, uid: int, msg: Twist):
            if uid in self.sim.drones:
                self.sim.drones[uid].cmd_vx = msg.linear.x
                self.sim.drones[uid].cmd_vy = msg.linear.y
                self.sim.drones[uid].cmd_vz = msg.linear.z

        def sim_loop(self):
            self.sim.step(dt=0.05)
            now_msg = self.get_clock().now().to_msg()

            for uid, drone in self.sim.drones.items():
                # Publish pose
                p_msg = PoseStamped()
                p_msg.header.stamp = now_msg
                p_msg.header.frame_id = str(uid)
                p_msg.pose.position.x = drone.x
                p_msg.pose.position.y = drone.y
                p_msg.pose.position.z = drone.z
                self.pose_publishers[uid].publish(p_msg)

                # Publish LiDAR scan
                scan_ranges = self.sim.generate_lidar_scan(drone)
                s_msg = LaserScan()
                s_msg.header.stamp = now_msg
                s_msg.header.frame_id = f"drone_{uid}_lidar"
                s_msg.angle_min = 0.0
                s_msg.angle_max = 2.0 * math.pi
                s_msg.angle_increment = (2.0 * math.pi) / len(scan_ranges)
                s_msg.range_min = 0.1
                s_msg.range_max = 30.0
                s_msg.ranges = scan_ranges
                self.scan_publishers[uid].publish(s_msg)


def main(args=None):
    if HAS_ROS2:
        rclpy.init(args=args)
        node = MockSITLBridgeNode()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()
    else:
        print("[!] rclpy bulunamadı, simülasyon test döngüsü başlatılıyor...")
        sim = FastSwarmSim(num_drones=3)
        for step in range(5):
            sim.step(0.1)
            print(f"Step {step}: Drone-1 Pos: ({sim.drones[1].x:.2f}, {sim.drones[1].y:.2f})")


if __name__ == '__main__':
    main()

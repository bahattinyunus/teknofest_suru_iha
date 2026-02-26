#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import time
import os

class SwarmDashboard(Node):
    def __init__(self):
        super().__init__('swarm_dashboard')
        self.get_logger().info('Swarm Telemetry Dashboard Initializing...')
        
        # Subscribe to swarm positions
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/swarm/positions',
            self.pose_cb,
            10
        )
        
        self.drones = {} # ID -> (X, Y, Z, Last Update Time)
        
        # Refresh screen at 2 Hz
        self.display_timer = self.create_timer(0.5, self.update_display)

    def pose_cb(self, msg):
        drone_id = msg.header.frame_id
        if drone_id:
            x = msg.pose.position.x
            y = msg.pose.position.y
            z = msg.pose.position.z
            self.drones[drone_id] = (x, y, z, time.time())

    def update_display(self):
        # Clear terminal screen (cross-platform compatible)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("="*50)
        print("🚁 TEKNOFEST SWARM COMMAND CENTER - TELEMETRY")
        print("="*50)
        
        current_time = time.time()
        active_count = 0
        
        if not self.drones:
            print("\n  [!] Waiting for swarm data streams...\n")
        else:
            print(f"{'ID':<10} | {'X (m)':<10} | {'Y (m)':<10} | {'Z (m)':<10} | {'STATUS'}")
            print("-" * 50)
            
            # Sort by ID
            sorted_drones = sorted(self.drones.items(), key=lambda item: item[0])
            for d_id, (x, y, z, last_time) in sorted_drones:
                # Check health (if no message for 2 seconds, assume degraded/lost)
                if current_time - last_time > 2.0:
                    status = "🔴 LOST"
                else:
                    status = "🟢 ACTIVE"
                    active_count += 1
                    
                print(f"Drone-{d_id:<4} | {x:>8.2f} | {y:>8.2f} | {z:>8.2f} | {status}")
        
        print("-" * 50)
        print(f"Total Drones Tracked : {len(self.drones)}")
        print(f"Active Drones        : {active_count}")
        print("="*50)

def main(args=None):
    rclpy.init(args=args)
    node = SwarmDashboard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nDashboard closed via user interrupt.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

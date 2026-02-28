#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from mavros_msgs.msg import State
from sensor_msgs.msg import LaserScan
import math
import json
import os
import time
from datetime import datetime

class SwarmCommander(Node):
    def __init__(self):
        super().__init__('swarm_commander')
        self.get_logger().info('Sürü Komutanı Başlatıldı, Boids (Sürü) Algoritması aktif...')
        
        # Sürü parametreleri (Boids algoritması için)
        self.declare_parameter('swarm_id', 1)
        self.declare_parameter('cohesion_weight', 1.0)
        self.declare_parameter('alignment_weight', 1.0)
        self.declare_parameter('separation_weight', 1.6)
        self.declare_parameter('obstacle_weight', 2.5)
        self.declare_parameter('safe_distance', 3.0)
        self.declare_parameter('max_speed', 5.0)
        self.declare_parameter('perception_radius', 15.0)
        self.declare_parameter('enable_logging', True)
        self.declare_parameter('log_interval', 1.0) # Saniyede bir kayıt
        
        self.swarm_id = self.get_parameter('swarm_id').value
        
        # Abonelikler (Subscribers)
        self.state_sub = self.create_subscription(
            State,
            'mavros/state',
            self.state_cb,
            10
        )
        
        # Diğer İHA'ların konumlarını dinleme simülasyonu
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/swarm/positions',
            self.pose_cb,
            10
        )
        
        # Yayıncılar (Publishers)
        self.vel_pub = self.create_publisher(
            Twist,
            'mavros/setpoint_velocity/cmd_vel_unstamped',
            10
        )
        
        # Kendi konumunu diğerlerine yayınlama
        self.my_pose_pub = self.create_publisher(
            PoseStamped,
            '/swarm/positions',
            10
        )
        
        # Engel/Çarpışma uyarılarını dinleme (Lidar simülasyonu)
        self.scan_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_cb,
            10
        )
        
        self.current_state = State()
        self.latest_scan = None
        self.neighbors = {} # id -> pose map
        self.current_pose = PoseStamped()
        
        # Telemetri Kaydı Hazırlığı
        self.enable_logging = self.get_parameter('enable_logging').value
        if self.enable_logging:
            self.log_file = f"mission_log_drone_{self.swarm_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.get_logger().info(f"Telemetri kaydı aktif: {self.log_file}")
            self.mission_data = []
            self.last_log_time = self.get_clock().now()
        
        # Kontrol döngüsü (10 Hz)
        self.control_timer = self.create_timer(0.1, self.control_loop) 
        
    def state_cb(self, msg):
        self.current_state = msg

    def scan_cb(self, msg):
        self.latest_scan = msg

    def calculate_obstacle_repulsion(self):
        """Lidar/Mesafe sensöründen gelen engellerden kaçış vektörü"""
        force = [0.0, 0.0]
        if not self.latest_scan:
            return force
            
        safe_dist = self.get_parameter('safe_distance').value
        obs_weight = self.get_parameter('obstacle_weight').value
        
        angle = self.latest_scan.angle_min
        for r in self.latest_scan.ranges:
            if self.latest_scan.range_min < r < safe_dist:
                # İtici kuvvet, mesafenin tersi ile orantılı
                magnitude = (safe_dist - r) / safe_dist * obs_weight
                force[0] -= magnitude * math.cos(angle)
                force[1] -= magnitude * math.sin(angle)
            angle += self.latest_scan.angle_increment
            
        return force

    def pose_cb(self, msg):
        # Gerçekte frame_id veya drone ID üzerinden ayrım yapılır
        sender_id = msg.header.frame_id
        if sender_id and sender_id != str(self.swarm_id):
            # Mesafe bazlı filtreleme (Sadece belirli yarıçaptakileri komşu say)
            dx = self.current_pose.pose.position.x - msg.pose.position.x
            dy = self.current_pose.pose.position.y - msg.pose.position.y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist < self.get_parameter('perception_radius').value:
                self.neighbors[sender_id] = msg
            elif sender_id in self.neighbors:
                del self.neighbors[sender_id] # Menzil dışına çıktıysa sil

    def calculate_boids_velocity(self):
        """Boids algoritması hesaplamaları (Cohesion, Alignment, Separation)."""
        cohesion = [0.0, 0.0, 0.0]
        alignment = [0.0, 0.0, 0.0]
        separation = [0.0, 0.0, 0.0]
        
        if not self.neighbors:
            return Twist() # Komşu yoksa varsayılan hızı koru veya dur
            
        c_weight = self.get_parameter('cohesion_weight').value
        a_weight = self.get_parameter('alignment_weight').value
        s_weight = self.get_parameter('separation_weight').value
        radius = self.get_parameter('perception_radius').value
        
        count = 0
        for n_id, n_pose in self.neighbors.items():
            dx = self.current_pose.pose.position.x - n_pose.pose.position.x
            dy = self.current_pose.pose.position.y - n_pose.pose.position.y
            dist = math.sqrt(dx**2 + dy**2)
            
            if 0.1 < dist < radius:
                # Separation: Yakın komşulardan uzaklaş
                separation[0] += dx / dist
                separation[1] += dy / dist
                
                # Cohesion: Sürünün merkezine yönel
                cohesion[0] += n_pose.pose.position.x
                cohesion[1] += n_pose.pose.position.y
                
                count += 1
                
        cmd_vel = Twist()
        if count > 0:
            cohesion[0] = (cohesion[0] / count - self.current_pose.pose.position.x) * c_weight
            cohesion[1] = (cohesion[1] / count - self.current_pose.pose.position.y) * c_weight
            
            separation[0] *= s_weight
            separation[1] *= s_weight
            
            # Sürü rotası birleşimi
            cmd_vel.linear.x = cohesion[0] + separation[0]
            cmd_vel.linear.y = cohesion[1] + separation[1]
            
            # --- Faz 3: Engelden Kaçınma Eklentisi ---
            obs_force = self.calculate_obstacle_repulsion()
            cmd_vel.linear.x += obs_force[0]
            cmd_vel.linear.y += obs_force[1]
            
            # Hız sınırlandırma (Max Speed clamp)
            max_speed = self.get_parameter('max_speed').value
            speed = math.sqrt(cmd_vel.linear.x**2 + cmd_vel.linear.y**2)
            if speed > max_speed:
                cmd_vel.linear.x = (cmd_vel.linear.x / speed) * max_speed
                cmd_vel.linear.y = (cmd_vel.linear.y / speed) * max_speed
                
        return cmd_vel

    def control_loop(self):
        # FCU bağlantısı veya simülasyon aktif ise hesaplamayı yayınla
        # Prototipe göre OFFBOARD modda veya her daim yayınlayabiliriz.
        cmd = self.calculate_boids_velocity()
        self.vel_pub.publish(cmd)
        
        # Test için hafif loglama
        # self.get_logger().debug(f"Hız: X:{cmd.linear.x:.2f} Y:{cmd.linear.y:.2f}")
        
        # Telemetri Kaydı (JSON)
        if self.enable_logging:
            now = self.get_clock().now()
            if (now - self.last_log_time).nanoseconds / 1e9 >= self.get_parameter('log_interval').value:
                record = {
                    "timestamp": now.to_msg().sec,
                    "pose": {
                        "x": self.current_pose.pose.position.x,
                        "y": self.current_pose.pose.position.y,
                        "z": self.current_pose.pose.position.z
                    },
                    "velocity": {
                        "x": cmd.linear.x,
                        "y": cmd.linear.y
                    },
                    "neighbors_count": len(self.neighbors)
                }
                self.mission_data.append(record)
                self.last_log_time = now
                
                # Periyodik dosya kaydı (güvenlik için)
                with open(self.log_file, 'w') as f:
                    json.dump(self.mission_data, f, indent=4)

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

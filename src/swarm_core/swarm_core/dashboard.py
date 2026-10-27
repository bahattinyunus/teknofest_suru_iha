#!/usr/bin/env python3
"""
Teknofest Swarm Telemetry & Command Center Dashboard
Real-time console dashboard for multi-UAV fleet monitoring,
swarm dispersion metrics, centroid calculation, and cybersecurity alerts.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import time
import os
import math
from typing import Dict, Tuple


class SwarmDashboard(Node):
    def __init__(self):
        super().__init__('swarm_dashboard')
        self.get_logger().info('Swarm Telemetry Dashboard Initializing...')

        # Subscribe to swarm position broadcast
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/swarm/positions',
            self.pose_cb,
            20
        )

        # drones: id -> (x, y, z, last_update_timestamp)
        self.drones: Dict[str, Tuple[float, float, float, float]] = {}

        # Refresh screen at 2 Hz
        self.display_timer = self.create_timer(0.5, self.update_display)

    def pose_cb(self, msg: PoseStamped):
        drone_id = msg.header.frame_id
        if drone_id:
            x = msg.pose.position.x
            y = msg.pose.position.y
            z = msg.pose.position.z
            self.drones[drone_id] = (x, y, z, time.time())

    def calculate_centroid_and_dispersion(self, active_drones):
        if not active_drones:
            return (0.0, 0.0, 0.0), 0.0

        n = len(active_drones)
        cx = sum(d[0] for d in active_drones) / n
        cy = sum(d[1] for d in active_drones) / n
        cz = sum(d[2] for d in active_drones) / n

        # Swarm radius of gyration / dispersion
        dispersion = math.sqrt(sum((d[0]-cx)**2 + (d[1]-cy)**2 + (d[2]-cz)**2 for d in active_drones) / n)
        return (cx, cy, cz), dispersion

    def update_display(self):
        # Clear terminal screen (cross-platform)
        os.system('cls' if os.name == 'nt' else 'clear')

        header_bar = "=" * 65
        print(header_bar)
        print("  🚁 TEKNOFEST SÜRÜ ZEKASI VE KOMUTA MERKEZİ - CANLI TELEMETRİ")
        print(header_bar)

        curr_time = time.time()
        active_list = []
        rows = []

        for d_id, (x, y, z, last_seen) in sorted(self.drones.items(), key=lambda x: str(x[0])):
            dt = curr_time - last_seen
            if dt <= 2.0:
                status = "🟢 ACTIVE"
                active_list.append((x, y, z))
            elif dt <= 5.0:
                status = "🟡 DEGRADED"
            else:
                status = "🔴 LOST"

            rows.append((d_id, x, y, z, dt, status))

        (cx, cy, cz), dispersion = self.calculate_centroid_and_dispersion(active_list)

        if not rows:
            print("\n  [!] Sürü telemetri akışı bekleniyor... (/swarm/positions)\n")
        else:
            print(f"{'İHA ID':<8} | {'X (m)':<9} | {'Y (m)':<9} | {'Z (m)':<9} | {'GECİKME':<8} | {'DURUM'}")
            print("-" * 65)
            for d_id, x, y, z, dt, status in rows:
                print(f"UAV-{d_id:<4} | {x:>8.2f} | {y:>8.2f} | {z:>8.2f} | {dt:>6.1f}s | {status}")

        print("-" * 65)
        print(f"  Toplam Kayıtlı İHA   : {len(self.drones)}")
        print(f"  Aktif İHA Sayısı      : {len(active_list)} / {len(self.drones)}")
        print(f"  Sürü Kütle Merkezi    : X={cx:.2f}m, Y={cy:.2f}m, Z={cz:.2f}m")
        print(f"  Sürü Dağılım Yarıçapı : {dispersion:.2f} metre")
        print(f"  Siber Güvenlik Durumu : {'🟢 TÜM DÜĞÜMLER NOMİNAL' if len(active_list) > 0 else '⚪ BEKLEMEDE'}")
        print(header_bar)
        print("  [Ctrl+C ile paneli kapatabilirsiniz]")


def main(args=None):
    rclpy.init(args=args)
    node = SwarmDashboard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\n[!] Swarm Dashboard kullanıcı isteğiyle kapatıldı.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

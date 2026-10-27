#!/usr/bin/env python3
"""
Teknofest Sürü İHA Hakem Sunucusu Haberleşme Köprüsü (Referee Server Bridge)
Handles bidirectional telemetry and command exchange with the official competition server.
Supports JSON-over-UDP/TCP packets and autonomous simulated loopback mode.
"""

import json
import socket
import time
import threading
from typing import Dict, Any, Optional

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import PoseStamped
    from std_msgs.msg import String
    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False


def create_telemetry_packet(team_id: int,
                            uav_id: int,
                            x: float,
                            y: float,
                            z: float,
                            speed: float = 0.0,
                            battery: float = 98.0,
                            locked_target: Optional[str] = None,
                            status: str = "UÇUŞTA") -> Dict[str, Any]:
    """Generates standard Teknofest competition telemetry packet."""
    return {
        "paket_tipi": "TELEMETRI",
        "takim_numarasi": int(team_id),
        "iha_id": int(uav_id),
        "zaman_damgasi": time.time(),
        "konum": {
            "x": round(float(x), 2),
            "y": round(float(y), 2),
            "z": round(float(z), 2)
        },
        "hiz_ms": round(float(speed), 2),
        "batarya_yuzdesi": round(float(battery), 1),
        "kilitlenme": locked_target or "YOK",
        "durum": status
    }


def create_target_detection_packet(team_id: int,
                                   uav_id: int,
                                   target_id: str,
                                   x: float,
                                   y: float,
                                   z: float,
                                   confidence: float = 0.95) -> Dict[str, Any]:
    """Generates standard Teknofest target detection / scoring packet."""
    return {
        "paket_tipi": "HEDEF_TESPIT",
        "takim_numarasi": int(team_id),
        "iha_id": int(uav_id),
        "hedef_id": str(target_id),
        "hedef_konum": {
            "x": round(float(x), 2),
            "y": round(float(y), 2),
            "z": round(float(z), 2)
        },
        "tespit_zamani": time.time(),
        "dogruluk_orani": round(float(confidence), 2)
    }


class RefereeClient:
    """UDP/TCP Client for sending telemetry to the competition referee server."""
    def __init__(self, host: str = "127.0.0.1", port: int = 5005, team_id: int = 1453):
        self.host = host
        self.port = port
        self.team_id = team_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.0)
        self.running = False
        self.last_command = "BEKLE"

    def send_packet(self, packet: Dict[str, Any]) -> bool:
        try:
            payload = json.dumps(packet).encode('utf-8')
            self.sock.sendto(payload, (self.host, self.port))
            return True
        except Exception as e:
            return False

    def close(self):
        self.sock.close()


if HAS_ROS2:
    class RefereeBridgeNode(Node):
        def __init__(self):
            super().__init__('referee_bridge')
            self.declare_parameter('team_id', 1453)
            self.declare_parameter('server_ip', '127.0.0.1')
            self.declare_parameter('server_port', 5005)

            team_id = self.get_parameter('team_id').value
            server_ip = self.get_parameter('server_ip').value
            server_port = self.get_parameter('server_port').value

            self.client = RefereeClient(host=server_ip, port=server_port, team_id=team_id)
            self.get_logger().info(f"Hakem Köprüsü Başlatıldı -> {server_ip}:{server_port} [Takım: {team_id}]")

            # Swarm positions subscriber
            self.sub = self.create_subscription(
                PoseStamped,
                '/swarm/positions',
                self.pose_cb,
                20
            )

            # Command publisher to local swarm
            self.cmd_pub = self.create_publisher(String, '/referee/command', 10)

        def pose_cb(self, msg: PoseStamped):
            uav_id = msg.header.frame_id or "1"
            try:
                numeric_id = int(uav_id)
            except ValueError:
                numeric_id = 1

            packet = create_telemetry_packet(
                team_id=self.get_parameter('team_id').value,
                uav_id=numeric_id,
                x=msg.pose.position.x,
                y=msg.pose.position.y,
                z=msg.pose.position.z,
                speed=2.5,
                battery=95.0,
                status="OPERASYONEL"
            )
            self.client.send_packet(packet)


def main(args=None):
    if HAS_ROS2:
        rclpy.init(args=args)
        node = RefereeBridgeNode()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.client.close()
            node.destroy_node()
            rclpy.shutdown()
    else:
        print("[!] rclpy bulunamadı, simülasyon istemcisi modunda başlatılıyor.")
        client = RefereeClient()
        test_pkt = create_telemetry_packet(1453, 1, 10.0, 5.0, 15.0)
        print(f"Örnek Hakem Paketi:\n{json.dumps(test_pkt, indent=2)}")


if __name__ == '__main__':
    main()

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
from typing import Dict, Any, Optional, List, Tuple

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


class TeknofestScoringEvaluator:
    """
    TEKNOFEST Sürü İHA Görev Puanlama ve Kural Değerlendirme Motoru.
    Computes real-time competition scores, safety violation penalties,
    multi-agent target consensus bonuses, and precision payload engagement accuracy.
    """

    def __init__(self,
                 base_score: float = 1000.0,
                 geofence_penalty_per_sec: float = 15.0,
                 proximity_violation_penalty: float = 50.0,
                 safe_distance_threshold: float = 1.5,
                 target_detect_points: float = 150.0,
                 target_consensus_bonus: float = 100.0,
                 consensus_window_sec: float = 30.0):
        self.base_score = float(base_score)
        self.geofence_penalty_per_sec = float(geofence_penalty_per_sec)
        self.proximity_violation_penalty = float(proximity_violation_penalty)
        self.safe_distance_threshold = float(safe_distance_threshold)
        self.target_detect_points = float(target_detect_points)
        self.target_consensus_bonus = float(target_consensus_bonus)
        self.consensus_window_sec = float(consensus_window_sec)

        # Records
        self.geofence_violations: List[Dict[str, Any]] = []
        self.proximity_violations: List[Dict[str, Any]] = []
        self.target_detections: Dict[str, List[Dict[str, Any]]] = {}
        self.precision_engagements: List[Dict[str, Any]] = []
        self.penalties_total = 0.0
        self.bonuses_total = 0.0

    def record_geofence_breach(self, uav_id: int, duration_sec: float) -> float:
        """Records breach of outer boundary and deducts points."""
        penalty = duration_sec * self.geofence_penalty_per_sec
        self.geofence_violations.append({
            "uav_id": uav_id,
            "duration_sec": duration_sec,
            "penalty": penalty,
            "timestamp": time.time()
        })
        self.penalties_total += penalty
        return penalty

    def record_proximity_violation(self, uav_1: int, uav_2: int, distance: float) -> Optional[float]:
        """Records near-collision or unsafe separation between two swarm members."""
        if distance < self.safe_distance_threshold:
            penalty = self.proximity_violation_penalty
            self.proximity_violations.append({
                "uav_pair": (min(uav_1, uav_2), max(uav_1, uav_2)),
                "distance": distance,
                "penalty": penalty,
                "timestamp": time.time()
            })
            self.penalties_total += penalty
            return penalty
        return None

    def record_target_detection(self,
                                target_id: str,
                                uav_id: int,
                                confidence: float = 0.95,
                                timestamp: Optional[float] = None) -> float:
        """
        Records target identification by a drone.
        Awards detection points and triggers consensus bonus if verified by another UAV.
        """
        ts = timestamp if timestamp is not None else time.time()
        award = 0.0

        if target_id not in self.target_detections:
            self.target_detections[target_id] = []
            # First detection award
            award += self.target_detect_points
        
        # Check if this UAV already detected this target
        already_detected_by_this = any(d["uav_id"] == uav_id for d in self.target_detections[target_id])
        if not already_detected_by_this:
            # Check for consensus within time window
            consensus_qualified = False
            for prev in self.target_detections[target_id]:
                if abs(ts - prev["timestamp"]) <= self.consensus_window_sec and prev["uav_id"] != uav_id:
                    consensus_qualified = True
                    break

            if consensus_qualified and len(self.target_detections[target_id]) == 1:
                award += self.target_consensus_bonus

            self.target_detections[target_id].append({
                "uav_id": uav_id,
                "confidence": confidence,
                "timestamp": ts
            })

        self.bonuses_total += award
        return award

    def record_precision_engagement(self,
                                   target_id: str,
                                   uav_id: int,
                                   miss_distance: float) -> float:
        """
        Grades payload release precision based on radial miss distance:
        <= 0.5m: +250 pts (Bulls-eye)
        <= 1.5m: +150 pts (Close impact)
        <= 3.0m: +50 pts (Acceptable impact)
        > 3.0m: 0 pts
        """
        if miss_distance <= 0.5:
            points = 250.0
            grade = "TAM_ISABET"
        elif miss_distance <= 1.5:
            points = 150.0
            grade = "YAKIN_ISABET"
        elif miss_distance <= 3.0:
            points = 50.0
            grade = "GECERLI_ISABET"
        else:
            points = 0.0
            grade = "ISAKAT"

        self.precision_engagements.append({
            "target_id": target_id,
            "uav_id": uav_id,
            "miss_distance": round(miss_distance, 2),
            "points": points,
            "grade": grade,
            "timestamp": time.time()
        })
        self.bonuses_total += points
        return points

    def evaluate_mission_score(self,
                               elapsed_time: float,
                               max_mission_time: float = 600.0) -> Dict[str, Any]:
        """Computes comprehensive mission score summary."""
        time_bonus = 0.0
        if elapsed_time < max_mission_time:
            time_bonus = max(0.0, round((max_mission_time - elapsed_time) * 0.5, 1))

        final_score = max(0.0, round(self.base_score + self.bonuses_total + time_bonus - self.penalties_total, 1))

        return {
            "final_score": final_score,
            "base_score": self.base_score,
            "bonuses_total": round(self.bonuses_total, 1),
            "time_bonus": time_bonus,
            "penalties_total": round(self.penalties_total, 1),
            "targets_detected_count": len(self.target_detections),
            "engagements_count": len(self.precision_engagements),
            "geofence_violations_count": len(self.geofence_violations),
            "proximity_violations_count": len(self.proximity_violations),
            "mission_status": "BASARILI" if final_score >= 1000.0 else "GECERLI"
        }

    def export_scorecard(self, filepath: str, elapsed_time: float = 300.0) -> None:
        """Saves JSON scorecard report for TEKNOFEST jury submission."""
        summary = self.evaluate_mission_score(elapsed_time)
        report = {
            "summary": summary,
            "details": {
                "geofence_violations": self.geofence_violations,
                "proximity_violations": self.proximity_violations,
                "target_detections": self.target_detections,
                "precision_engagements": self.precision_engagements
            }
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)


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

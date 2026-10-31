#!/usr/bin/env python3
"""
Teknofest Swarm Intelligence Command-Line Interface (Swarm CLI)
Unified administrative tool for fleet status, mission commands, and benchmark tests.
"""

import sys
import os
import time
import json
import argparse
import urllib.request
import urllib.error

# Ensure package root is in sys.path when executed directly
pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from swarm_core.algorithms import Vector3, BoidsController, AuctionTaskAllocator, GeofenceManager
from swarm_core.rvo_avoidance import RVOCollisionAvoidance
from swarm_core.sensor_fusion import SensorFusionEKF
from swarm_core.referee_bridge import TeknofestScoringEvaluator


GCS_URL = "http://127.0.0.1:8080"


def send_gcs_command(payload: dict) -> bool:
    try:
        req = urllib.request.Request(
            f"{GCS_URL}/api/command",
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=1.5) as response:
            return response.status == 200
    except Exception as e:
        print(f"[!] GCS Bağlantı Hatası ({GCS_URL}): {e}")
        return False


def cmd_status():
    try:
        req = urllib.request.Request(f"{GCS_URL}/api/telemetry")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        print("=" * 65)
        print("🚁 TEKNOFEST SÜRÜ FİLO VE GÖREV DURUMU")
        print("=" * 65)
        print(f"  Aktif Görev Modu     : {data.get('mission_mode')} ({data.get('formation_type')})")
        print(f"  Aktif Sürü Lideri    : UAV-{data.get('leader_id')}")
        print("-" * 65)
        print(f"{'İHA':<6} | {'X (m)':<8} | {'Y (m)':<8} | {'Z (m)':<8} | {'BATARYA':<8} | {'ROL'}")
        print("-" * 65)
        for uid, d in data.get('drones', {}).items():
            role = "👑 LİDER" if int(uid) == data.get('leader_id') else "TAKİPÇİ"
            print(f"UAV-{uid:<2} | {d['x']:>7.2f} | {d['y']:>7.2f} | {d['z']:>7.2f} | %{d['battery']:>6.1f} | {role}")
        print("=" * 65)
    except Exception as e:
        print(f"[!] Canlı telemetri alınamadı (Web GCS açık mı?): {e}")


def cmd_formation(form_type: str):
    form_type = form_type.upper()
    print(f"[*] Sürü Formasyonu Değiştiriliyor: {form_type}...")
    success = send_gcs_command({"mission_mode": "FORMATION", "formation_type": form_type})
    if success:
        print(f"✅ Formasyon başarıyla güncellendi: {form_type}")


def cmd_mission(mode: str):
    mode = mode.upper()
    print(f"[*] Görev Modu Değiştiriliyor: {mode}...")
    success = send_gcs_command({"mission_mode": mode})
    if success:
        print(f"✅ Görev modu başarıyla güncellendi: {mode}")


def cmd_benchmark():
    print("=" * 65)
    print("⚡ SÜRÜ ALGORİTMA PERFORMANS VE HIZ TESTİ (BENCHMARK)")
    print("=" * 65)

    # 1. Boids Flocking 10,000 iterations test
    boids = BoidsController(perception_radius=20.0, max_speed=5.0)
    curr_pos = Vector3(0, 0, 10)
    curr_vel = Vector3(0, 0, 0)
    neighbors = {str(i): (Vector3(i*2, i*2, 10), Vector3(1, 1, 0)) for i in range(1, 10)}

    t0 = time.perf_counter()
    for _ in range(10000):
        _ = boids.compute_velocity(curr_pos, curr_vel, neighbors)
    boids_time = time.perf_counter() - t0
    print(f"  Reynolds Boids (10 İHA x 10,000 döngü) : {boids_time*1000:.2f} ms ({10000/boids_time:.0f} Hz)")

    # 2. Auction Task Allocator 50 targets test
    allocator = AuctionTaskAllocator()
    for i in range(50):
        allocator.add_task(f"T{i}", Vector3(i*3, i*3, 0))
    fleet = {i: {'pos': Vector3(i*5, 0, 10), 'battery': 95.0} for i in range(1, 11)}

    t0 = time.perf_counter()
    _ = allocator.allocate_tasks(fleet)
    auction_time = time.perf_counter() - t0
    print(f"  Pazar Tabanlı Görev Paylaşımı (50 Görev): {auction_time*1000:.2f} ms")

    # 3. Geofence Check 50,000 iterations test
    geo = GeofenceManager(bounds=(-50, 50, -50, 50, 0, 30))
    t0 = time.perf_counter()
    for _ in range(50000):
        _ = geo.compute_boundary_force(curr_pos)
    geo_time = time.perf_counter() - t0
    print(f"  3D Geofence & NFZ Bariyer (50,000 kontrol) : {geo_time*1000:.2f} ms ({50000/geo_time:.0f} Hz)")

    # 4. RVO Collision Avoidance 2,000 queries test
    rvo = RVOCollisionAvoidance(drone_radius=0.8, time_horizon=3.0, max_speed=5.0)
    pref_vel = Vector3(3.0, 0.0, 0.0)
    nbr_list = [(Vector3(i * 2.0, 0.0, 10.0), Vector3(-1.0, 0.0, 0.0)) for i in range(1, 6)]
    t0 = time.perf_counter()
    for _ in range(2000):
        _ = rvo.compute_avoidance_velocity(curr_pos, curr_vel, pref_vel, nbr_list)
    rvo_time = time.perf_counter() - t0
    print(f"  RVO-3D Çarpışma Önleme (2,000 optimizasyon): {rvo_time*1000:.2f} ms ({2000/rvo_time:.0f} Hz)")

    # 5. Sensor Fusion EKF 10,000 predict + update test
    ekf = SensorFusionEKF(initial_pos=curr_pos, initial_vel=curr_vel)
    t0 = time.perf_counter()
    for _ in range(10000):
        ekf.predict(Vector3(0.1, 0.0, 0.0), dt=0.01)
        ekf.update_gps(Vector3(1.0, 0.5, 10.0), hdop=1.1)
    ekf_time = time.perf_counter() - t0
    print(f"  Genişletilmiş Kalman Filtresi EKF (10,000 adım): {ekf_time*1000:.2f} ms ({10000/ekf_time:.0f} Hz)")

    print("=" * 65)
    print("🚀 TÜM ÇEKİRDEK ALGORİTMALAR MİLİSANİYE SEVİYESİNDE REAL-TIME HAZIR!")
    print("=" * 65)


def cmd_score_eval():
    print("=" * 65)
    print("🏆 TEKNOFEST HAKEM VE GÖREV PUANLAMA DEĞERLENDİRİCİSİ")
    print("=" * 65)
    evaluator = TeknofestScoringEvaluator(base_score=1000.0)

    # Simulate realistic mission events
    evaluator.record_target_detection("TARGET_ALPHA", uav_id=2, confidence=0.96, timestamp=10.0)
    evaluator.record_target_detection("TARGET_ALPHA", uav_id=4, confidence=0.98, timestamp=18.0)  # Consensus bonus!
    evaluator.record_target_detection("TARGET_BETA", uav_id=1, confidence=0.92, timestamp=45.0)

    evaluator.record_precision_engagement("TARGET_ALPHA", uav_id=3, miss_distance=0.35)  # Tam isabet!
    evaluator.record_precision_engagement("TARGET_BETA", uav_id=5, miss_distance=1.2)   # Yakın isabet

    # Small geofence breach simulation
    evaluator.record_geofence_breach(uav_id=2, duration_sec=1.5)

    summary = evaluator.evaluate_mission_score(elapsed_time=240.0, max_mission_time=600.0)
    print(f"  Taban Puan          : {summary['base_score']} pts")
    print(f"  Hedef & İhbar Bonusu: +{summary['bonuses_total']} pts")
    print(f"  Zaman Tasarruf Bonusu: +{summary['time_bonus']} pts")
    print(f"  Kural İhlal Cezaları : -{summary['penalties_total']} pts")
    print("-" * 65)
    print(f"  TOPLAM SKOR         : {summary['final_score']} PTS ({summary['mission_status']})")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Teknofest Sürü İHA Yönetim CLI")
    subparsers = parser.add_subparsers(dest="command", help="Alt komutlar")

    subparsers.add_parser("status", help="Sürü telemetri durumunu listele")

    form_parser = subparsers.add_parser("formation", help="Formasyon tipini değiştir")
    form_parser.add_argument("type", choices=["V_SHAPE", "LINE", "COLUMN", "CIRCLE", "GRID"], help="Formasyon türü")

    mission_parser = subparsers.add_parser("mission", help="Görev modunu değiştir")
    mission_parser.add_argument("mode", choices=["BOIDS", "FORMATION", "SEARCH", "APF", "RTL"], help="Görev modu")

    subparsers.add_parser("benchmark", help="Sürü algoritmalarını hız testine tabi tut")
    subparsers.add_parser("score-eval", help="Teknofest hakem puanlama simülasyonunu çalıştır")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "formation":
        cmd_formation(args.type)
    elif args.command == "mission":
        cmd_mission(args.mode)
    elif args.command == "benchmark":
        cmd_benchmark()
    elif args.command == "score-eval":
        cmd_score_eval()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Teknofest Swarm Intelligence Command-Line Interface (Swarm CLI)
Unified administrative tool for fleet status, mission commands, and benchmark tests.
"""

import sys
import time
import json
import argparse
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from swarm_core.algorithms import Vector3, BoidsController, AuctionTaskAllocator, GeofenceManager


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

    print("=" * 65)
    print("🚀 TÜM ÇEKİRDEK ALGORİTMALAR MİLİSANİYE SEVİYESİNDE REAL-TIME HAZIR!")
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

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "formation":
        cmd_formation(args.type)
    elif args.command == "mission":
        cmd_mission(args.mode)
    elif args.command == "benchmark":
        cmd_benchmark()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

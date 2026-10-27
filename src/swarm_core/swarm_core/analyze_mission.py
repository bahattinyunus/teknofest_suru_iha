#!/usr/bin/env python3
"""
Teknofest Mission Log Analysis and KPI Evaluation Tool
Analyzes flight trajectory, swarm cohesion, speed limits,
safety proximity violations, and cyber-defense event logs.
"""

import json
import math
import sys
import os
import argparse
from typing import List, Dict, Any, Optional


def load_log(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Log dosyası bulunamadı: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Geçersiz log formatı: JSON bir liste içermelidir.")
    return data


def compute_metrics(data: List[Dict[str, Any]], safe_distance: float = 3.0) -> Dict[str, Any]:
    if not data:
        return {}

    total_dist_3d = 0.0
    total_dist_2d = 0.0
    speeds = []
    neighbor_counts = []
    anomalies_detected = set()
    failsafe_events = 0
    prev_pose = None
    first_time = data[0].get('timestamp', 0)
    last_time = data[-1].get('timestamp', 0)
    duration_sec = max(0, last_time - first_time)

    for entry in data:
        curr_pose = entry.get('pose', {'x': 0, 'y': 0, 'z': 0})
        vel = entry.get('velocity', {'x': 0, 'y': 0, 'z': 0})
        speed = math.sqrt(vel.get('x', 0)**2 + vel.get('y', 0)**2 + vel.get('z', 0)**2)
        speeds.append(speed)

        if prev_pose:
            dx = curr_pose['x'] - prev_pose['x']
            dy = curr_pose['y'] - prev_pose['y']
            dz = curr_pose['z'] - prev_pose['z']
            total_dist_3d += math.sqrt(dx**2 + dy**2 + dz**2)
            total_dist_2d += math.sqrt(dx**2 + dy**2)

        prev_pose = curr_pose

        n_count = entry.get('neighbors_count', 0)
        neighbor_counts.append(n_count)

        anomalies = entry.get('anomalous_nodes', [])
        for a in anomalies:
            anomalies_detected.add(str(a))

        if entry.get('failsafe_status', 'NORMAL') != 'NORMAL':
            failsafe_events += 1

    avg_speed = sum(speeds) / len(speeds) if speeds else 0.0
    max_speed = max(speeds) if speeds else 0.0
    avg_neighbors = sum(neighbor_counts) / len(neighbor_counts) if neighbor_counts else 0.0

    return {
        "record_count": len(data),
        "duration_seconds": duration_sec,
        "total_distance_3d_m": round(total_dist_3d, 2),
        "total_distance_2d_m": round(total_dist_2d, 2),
        "average_speed_mps": round(avg_speed, 2),
        "max_speed_mps": round(max_speed, 2),
        "average_neighbors": round(avg_neighbors, 2),
        "failsafe_trigger_count": failsafe_events,
        "anomalies_detected": list(anomalies_detected)
    }


def print_cli_summary(metrics: Dict[str, Any], file_path: str):
    print("=" * 60)
    print(f"📊 SÜRÜ MİSYON VE TELEMETRİ ANALİZİ: {os.path.basename(file_path)}")
    print("=" * 60)
    print(f"  Toplam Kayıt Sayısı      : {metrics.get('record_count', 0)}")
    print(f"  Tahmini Görev Süresi     : {metrics.get('duration_seconds', 0)} sn")
    print(f"  Toplam Kat Edilen Mesafe  : {metrics.get('total_distance_3d_m', 0.0)} m")
    print(f"  Ortalama Hız             : {metrics.get('average_speed_mps', 0.0)} m/s")
    print(f"  Maksimum Hız (Tepe)      : {metrics.get('max_speed_mps', 0.0)} m/s")
    print(f"  Ortalama Komşu Bağlantısı: {metrics.get('average_neighbors', 0.0)} düğüm")
    print(f"  Fail-Safe Müdahaleleri   : {metrics.get('failsafe_trigger_count', 0)}")
    
    anomalies = metrics.get('anomalies_detected', [])
    if anomalies:
        print(f"  ⚠️ Tespit Edilen Saldırgan Düğümler: {', '.join(anomalies)}")
    else:
        print("  🛡️ Siber Güvenlik Durumu : İhlal tespit edilmedi (Nominal)")
    print("=" * 60)


def generate_markdown_report(metrics: Dict[str, Any], file_path: str, output_path: str):
    md_content = f"""# 🚁 Sürü Görev Sonrası Analiz Raporu

**Analiz Edilen Log:** `{os.path.basename(file_path)}`  
**Oluşturulma Tarihi:** Otomatik CI/CD Üretimi  

---

## 📈 Temel Performans Göstergeleri (KPIs)

| Metrik | Değer | Birim | Hedef Standart |
| :--- | :--- | :--- | :--- |
| **Toplam Mesafe (3D)** | {metrics.get('total_distance_3d_m', 0)} | metre | - |
| **Toplam Süre** | {metrics.get('duration_seconds', 0)} | saniye | - |
| **Ortalama Hız** | {metrics.get('average_speed_mps', 0)} | m/s | < 5.0 m/s |
| **Maksimum Hız** | {metrics.get('max_speed_mps', 0)} | m/s | Sınır: 15.0 m/s |
| **Ortalama Sürü Bağlantısı** | {metrics.get('average_neighbors', 0)} | İHA | >= 2.0 İHA |
| **Fail-Safe Tetiklenmeleri** | {metrics.get('failsafe_trigger_count', 0)} | olay | 0 (İdeal) |

## 🛡️ Güvenlik ve Ağ Sağlığı
- **Saldırgan / Sahtelenmiş Düğümler:** `{len(metrics.get('anomalies_detected', []))}` adet
- **Rogue Düğüm Kimlikleri:** `{metrics.get('anomalies_detected', [])}`

---
*Bu rapor Teknofest Sürü Zekası Komuta Merkezi otomatik analiz aracı tarafından oluşturulmuştur.*
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ Markdown raporu kaydedildi: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Teknofest Sürü Görev Telemetri Analiz Aracı")
    parser.add_argument("log_file", help="Analiz edilecek .json log dosyası")
    parser.add_argument("--report", help="Markdown formatında rapor üret (.md dosyası)", default=None)
    parser.add_argument("--export-summary", help="KPI özetini JSON olarak kaydet", default=None)

    args = parser.parse_args()

    try:
        data = load_log(args.log_file)
        metrics = compute_metrics(data)
        print_cli_summary(metrics, args.log_file)

        if args.report:
            generate_markdown_report(metrics, args.log_file, args.report)

        if args.export_summary:
            with open(args.export_summary, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=4)
            print(f"✅ JSON KPI özeti kaydedildi: {args.export_summary}")

    except Exception as e:
        print(f"Hata: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

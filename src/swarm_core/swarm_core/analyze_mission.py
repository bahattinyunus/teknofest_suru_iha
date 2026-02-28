#!/usr/bin/env python3
import json
import math
import sys
import os

def analyze_log(file_path):
    if not os.path.exists(file_path):
        print(f"Hata: {file_path} bulunamadı.")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)

    if not data:
        print("Log dosyası boş.")
        return

    total_distance = 0.0
    prev_pose = None
    avg_neighbors = 0.0
    max_speed = 0.0

    for record in data:
        curr_pose = record['pose']
        if prev_pose:
            dist = math.sqrt(
                (curr_pose['x'] - prev_pose['x'])**2 +
                (curr_pose['y'] - prev_pose['y'])**2 +
                (curr_pose['z'] - prev_pose['z'])**2
            )
            total_distance += dist

        avg_neighbors += record['neighbors_count']
        
        speed = math.sqrt(record['velocity']['x']**2 + record['velocity']['y']**2)
        if speed > max_speed:
            max_speed = speed
            
        prev_pose = curr_pose

    avg_neighbors /= len(data)

    print(f"--- Sürü Görev Analizi: {file_path} ---")
    print(f"Toplam Kayıt Sayısı: {len(data)}")
    print(f"Toplam Kat Edilen Mesafe: {total_distance:.2f} metre")
    print(f"Ortalama Komşu Sayısı: {avg_neighbors:.2f}")
    print(f"Maksimum Hız: {max_speed:.2f} m/s")
    print("-------------------------------------------")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python3 analyze_mission.py <log_dosyasi.json>")
    else:
        analyze_log(sys.argv[1])

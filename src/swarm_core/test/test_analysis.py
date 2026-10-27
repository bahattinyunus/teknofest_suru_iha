import pytest
import os
import tempfile
import json
from swarm_core.analyze_mission import compute_metrics, load_log


def test_compute_metrics_empty():
    metrics = compute_metrics([])
    assert metrics == {}


def test_compute_metrics_with_data():
    sample_data = [
        {
            "timestamp": 100,
            "drone_id": 1,
            "mode": "BOIDS",
            "pose": {"x": 0.0, "y": 0.0, "z": 10.0},
            "velocity": {"x": 2.0, "y": 0.0, "z": 0.0},
            "neighbors_count": 3,
            "anomalous_nodes": [],
            "failsafe_status": "NORMAL"
        },
        {
            "timestamp": 105,
            "drone_id": 1,
            "mode": "BOIDS",
            "pose": {"x": 10.0, "y": 0.0, "z": 10.0},
            "velocity": {"x": 2.0, "y": 0.0, "z": 0.0},
            "neighbors_count": 3,
            "anomalous_nodes": ["rogue_9"],
            "failsafe_status": "NORMAL"
        }
    ]

    metrics = compute_metrics(sample_data)
    assert metrics["record_count"] == 2
    assert metrics["duration_seconds"] == 5
    assert metrics["total_distance_3d_m"] == 10.0
    assert metrics["average_speed_mps"] == 2.0
    assert metrics["average_neighbors"] == 3.0
    assert "rogue_9" in metrics["anomalies_detected"]


def test_load_log_roundtrip():
    data = [{"timestamp": 1, "pose": {"x": 1, "y": 2, "z": 3}}]
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as tmp:
        json.dump(data, tmp)
        tmp_name = tmp.name

    try:
        loaded = load_log(tmp_name)
        assert len(loaded) == 1
        assert loaded[0]["timestamp"] == 1
    finally:
        os.remove(tmp_name)

from swarm_core.referee_bridge import (
    create_telemetry_packet,
    create_target_detection_packet,
    RefereeClient,
    TeknofestScoringEvaluator
)


def test_telemetry_packet():
    pkt = create_telemetry_packet(
        team_id=1453,
        uav_id=2,
        x=15.5,
        y=-20.3,
        z=12.0,
        speed=4.2,
        battery=88.5,
        locked_target="QR_A1",
        status="OPERASYONEL"
    )

    assert pkt["paket_tipi"] == "TELEMETRI"
    assert pkt["takim_numarasi"] == 1453
    assert pkt["iha_id"] == 2
    assert pkt["konum"]["x"] == 15.5
    assert pkt["konum"]["y"] == -20.3
    assert pkt["konum"]["z"] == 12.0
    assert pkt["hiz_ms"] == 4.2
    assert pkt["batarya_yuzdesi"] == 88.5
    assert pkt["kilitlenme"] == "QR_A1"
    assert pkt["durum"] == "OPERASYONEL"


def test_target_detection_packet():
    pkt = create_target_detection_packet(
        team_id=1453,
        uav_id=1,
        target_id="HEDEF_KIRMIZI_1",
        x=25.0,
        y=30.0,
        z=0.0,
        confidence=0.98
    )

    assert pkt["paket_tipi"] == "HEDEF_TESPIT"
    assert pkt["hedef_id"] == "HEDEF_KIRMIZI_1"
    assert pkt["dogruluk_orani"] == 0.98
    assert pkt["hedef_konum"]["x"] == 25.0


def test_referee_client_creation():
    client = RefereeClient(host="127.0.0.1", port=9999, team_id=100)
    assert client.team_id == 100
    client.close()


def test_scoring_evaluator_detection_and_consensus(tmp_path):
    evaluator = TeknofestScoringEvaluator(base_score=1000.0)

    # 1. First drone detects target -> +150
    pts1 = evaluator.record_target_detection("T_RED", uav_id=1, confidence=0.95, timestamp=10.0)
    assert pts1 == 150.0

    # 2. Second drone confirms within 30s -> +100 bonus
    pts2 = evaluator.record_target_detection("T_RED", uav_id=2, confidence=0.97, timestamp=25.0)
    assert pts2 == 100.0

    # 3. Third drone detects after consensus already awarded -> 0 extra consensus
    pts3 = evaluator.record_target_detection("T_RED", uav_id=3, confidence=0.90, timestamp=30.0)
    assert pts3 == 0.0

    # 4. Precision engagement
    eng_pts = evaluator.record_precision_engagement("T_RED", uav_id=1, miss_distance=0.42)
    assert eng_pts == 250.0  # TAM_ISABET

    eng_pts2 = evaluator.record_precision_engagement("T_RED", uav_id=2, miss_distance=1.1)
    assert eng_pts2 == 150.0  # YAKIN_ISABET

    # Summary
    res = evaluator.evaluate_mission_score(elapsed_time=200.0, max_mission_time=600.0)
    # base 1000 + 150 + 100 + 250 + 150 + time_bonus (600-200)*0.5=200 => 1850.0
    assert res["final_score"] == 1850.0
    assert res["mission_status"] == "BASARILI"

    # Export test
    out_file = str(tmp_path / "scorecard.json")
    evaluator.export_scorecard(out_file)
    assert tmp_path.joinpath("scorecard.json").exists()


def test_scoring_evaluator_penalties():
    evaluator = TeknofestScoringEvaluator(base_score=1000.0)

    # Geofence breach 3 seconds -> 3 * 15 = 45 penalty
    pen = evaluator.record_geofence_breach(uav_id=2, duration_sec=3.0)
    assert pen == 45.0

    # Proximity violation (< 1.5m) -> 50 penalty
    prox_pen = evaluator.record_proximity_violation(uav_1=1, uav_2=3, distance=1.1)
    assert prox_pen == 50.0

    # Safe proximity (> 1.5m) -> None
    no_pen = evaluator.record_proximity_violation(uav_1=1, uav_2=4, distance=3.2)
    assert no_pen is None

    res = evaluator.evaluate_mission_score(elapsed_time=600.0, max_mission_time=600.0)
    assert res["penalties_total"] == 95.0
    assert res["final_score"] == 1000.0 - 95.0

import pytest
from swarm_core.referee_bridge import (
    create_telemetry_packet,
    create_target_detection_packet,
    RefereeClient
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

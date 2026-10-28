import pytest
from swarm_core.algorithms import Vector3
from swarm_core.mesh_network import DecentralizedMeshNetwork, RadioChannel, MeshPacket


def test_radio_channel_rssi():
    radio = RadioChannel(freq_ghz=2.4, tx_power_dbm=20.0, rx_sensitivity_dbm=-85.0)

    # Signal gets weaker as distance increases
    rssi_close = radio.calculate_rssi(5.0)
    rssi_far = radio.calculate_rssi(30.0)
    assert rssi_close > rssi_far

    # Direct communication check
    assert radio.can_communicate_direct(10.0) is True
    # Excessive distance or extreme noise drops connection
    assert radio.can_communicate_direct(10.0, noise_dbm=80.0) is False


def test_mesh_network_direct_and_multihop():
    mesh = DecentralizedMeshNetwork(max_direct_range_m=30.0)

    # 3 collinear drones: Drone 1 at 0, Drone 2 at 20, Drone 3 at 40
    mesh.update_node_position(1, Vector3(0.0, 0.0, 10.0))
    mesh.update_node_position(2, Vector3(20.0, 0.0, 10.0))
    mesh.update_node_position(3, Vector3(40.0, 0.0, 10.0))

    # 1 and 2 are 20m apart -> Direct connected
    assert mesh.are_connected_direct(1, 2) is True
    # 2 and 3 are 20m apart -> Direct connected
    assert mesh.are_connected_direct(2, 3) is True
    # 1 and 3 are 40m apart (>30m max range) -> NOT direct connected
    assert mesh.are_connected_direct(1, 3) is False

    # Multi-hop route from 1 to 3 must go via 2: [1, 2, 3]
    route = mesh.find_multi_hop_route(1, 3)
    assert route == [1, 2, 3]

    # Packet routing test
    pkt = MeshPacket(source_id=1, dest_id=3, payload_type="TELEMETRY", data="OK")
    success, route_taken = mesh.route_packet(pkt)
    assert success is True
    assert route_taken == [1, 2, 3]


def test_mesh_network_ew_jamming():
    mesh = DecentralizedMeshNetwork(max_direct_range_m=30.0)

    mesh.update_node_position(1, Vector3(0.0, 0.0, 10.0))
    mesh.update_node_position(2, Vector3(15.0, 0.0, 10.0))

    # Initially connected
    assert mesh.are_connected_direct(1, 2) is True

    # Inject high-power EW jammer right between them at (7.5, 0, 10)
    mesh.add_ew_jammer(pos=Vector3(7.5, 0.0, 10.0), power_dbm=60.0, radius_m=20.0)

    # Due to jamming noise, direct link is severed
    assert mesh.are_connected_direct(1, 2) is False
    assert mesh.find_multi_hop_route(1, 2) is None

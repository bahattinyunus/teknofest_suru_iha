import pytest
from swarm_core.algorithms import (
    Vector3,
    BoidsController,
    FormationController,
    GeofenceManager,
    AuctionTaskAllocator,
    LeaderElectionEngine
)
from swarm_core.vision_pipeline import SwarmVisionEngine
from swarm_core.precision_engagement import PrecisionEngagementController
from swarm_core.mesh_network import DecentralizedMeshNetwork


def test_full_mission_lifecycle_integration():
    # 1. Initialize 5 Drones Fleet in V-Formation
    num_drones = 5
    formation = FormationController(formation_type='V_SHAPE', spacing=3.5)
    geofence = GeofenceManager(bounds=(-50, 50, -50, 50, 0.5, 30.0))
    mesh = DecentralizedMeshNetwork(max_direct_range_m=35.0)

    drone_positions = {
        1: Vector3(0.0, 0.0, 10.0),      # Leader
        2: Vector3(-2.8, 2.0, 10.0),    # Scout
        3: Vector3(-2.8, -2.0, 10.0),   # Interceptor
        4: Vector3(-5.6, 4.0, 10.0),    # Interceptor
        5: Vector3(-5.6, -4.0, 10.0)    # Reserve
    }

    for uid, pos in drone_positions.items():
        mesh.update_node_position(uid, pos)
        assert geofence.is_inside(pos) is True

    # Check network connectivity: full swarm should have a connected mesh
    graph = mesh.build_adjacency_graph()
    assert all(len(neighbors) > 0 for neighbors in graph.values())

    # 2. Scout detects ground target at (15.0, 15.0, 0.0)
    vision = SwarmVisionEngine()
    ground_truth = [{'id': 'TARGET_X', 'pos': Vector3(15.0, 15.0, 0.0)}]
    # Move Scout near target
    drone_positions[2] = Vector3(14.0, 14.0, 10.0)
    detections = vision.scan_synthetic_frame(drone_positions[2], ground_truth)
    assert len(detections) == 1
    target_id, est_pos, conf = detections[0]
    assert target_id == 'TARGET_X'

    # 3. Market-based auction allocates Interceptor Drone 3 to target
    allocator = AuctionTaskAllocator()
    allocator.add_task(target_id, est_pos)
    fleet_status = {
        uid: {'pos': pos, 'battery': 95.0}
        for uid, pos in drone_positions.items()
    }
    assignments = allocator.allocate_tasks(fleet_status)
    assigned_drone = assignments[target_id]
    assert assigned_drone in [1, 2, 3, 4, 5]

    # 4. Precision engagement executes
    engager = PrecisionEngagementController(cruise_alt=10.0, drop_alt=2.0)
    engager.assign_target(est_pos)
    # Simulate approach & descent
    cmd, state, is_done = engager.update(drone_positions[assigned_drone], timestamp=0.0)
    assert state == 'CRUISE_APPROACH'

    # Fast forward to drop
    cmd, state, is_done = engager.update(Vector3(15.0, 15.0, 2.0), timestamp=5.0)
    assert state == 'ENGAGE'
    # Fast forward post-dwell
    cmd, state, is_done = engager.update(Vector3(15.0, 15.0, 2.0), timestamp=7.0)
    assert engager.payload_released is True
    assert state == 'CLIMB_REJOIN'

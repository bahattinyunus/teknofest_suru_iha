import pytest
import math
from swarm_core.algorithms import (
    Vector3,
    BoidsController,
    FormationController,
    ArtificialPotentialField,
    SearchPatternGenerator,
    AnomalyDetector,
    FailSafeManager,
    LeaderElectionEngine,
    GeofenceManager,
    TargetTracker
)


def test_vector3_operations():
    v1 = Vector3(1.0, 2.0, 3.0)
    v2 = Vector3(4.0, 5.0, 6.0)

    # Addition & Subtraction
    v_add = v1 + v2
    assert (v_add.x, v_add.y, v_add.z) == (5.0, 7.0, 9.0)

    v_sub = v2 - v1
    assert (v_sub.x, v_sub.y, v_sub.z) == (3.0, 3.0, 3.0)

    # Scalar multiplication & division
    v_mul = v1 * 2.0
    assert (v_mul.x, v_mul.y, v_mul.z) == (2.0, 4.0, 6.0)

    v_div = v2 / 2.0
    assert (v_div.x, v_div.y, v_div.z) == (2.0, 2.5, 3.0)

    # Magnitude & Normalize
    v3 = Vector3(3.0, 4.0, 0.0)
    assert v3.magnitude() == 5.0
    v3_norm = v3.normalized()
    assert math.isclose(v3_norm.magnitude(), 1.0)
    assert math.isclose(v3_norm.x, 0.6)
    assert math.isclose(v3_norm.y, 0.8)

    # Clamp
    v_clamped = v3.clamp(2.5)
    assert math.isclose(v_clamped.magnitude(), 2.5)


def test_boids_flocking_separation():
    boids = BoidsController(
        cohesion_weight=0.0,
        alignment_weight=0.0,
        separation_weight=2.0,
        goal_weight=0.0,
        safe_distance=4.0
    )

    curr_pos = Vector3(0.0, 0.0, 10.0)
    curr_vel = Vector3(0.0, 0.0, 0.0)

    # Neighbor is too close (at x=2.0, y=0.0)
    neighbors = {
        '2': (Vector3(2.0, 0.0, 10.0), Vector3(0.0, 0.0, 0.0))
    }

    cmd = boids.compute_velocity(curr_pos, curr_vel, neighbors)

    # Separation force should steer away from neighbor: x should be negative
    assert cmd.x < 0.0
    assert math.isclose(cmd.y, 0.0, abs_tol=1e-5)


def test_boids_flocking_cohesion():
    boids = BoidsController(
        cohesion_weight=2.0,
        alignment_weight=0.0,
        separation_weight=0.0,
        goal_weight=0.0,
        perception_radius=20.0,
        safe_distance=2.0
    )

    curr_pos = Vector3(0.0, 0.0, 10.0)
    curr_vel = Vector3(0.0, 0.0, 0.0)

    # Neighbor is within perception radius but outside safe distance
    neighbors = {
        '2': (Vector3(10.0, 0.0, 10.0), Vector3(0.0, 0.0, 0.0))
    }

    cmd = boids.compute_velocity(curr_pos, curr_vel, neighbors)

    # Cohesion should pull toward neighbor (+x)
    assert cmd.x > 0.0


def test_boids_flocking_alignment():
    boids = BoidsController(
        cohesion_weight=0.0,
        alignment_weight=2.0,
        separation_weight=0.0,
        goal_weight=0.0
    )

    curr_pos = Vector3(0.0, 0.0, 10.0)
    curr_vel = Vector3(0.0, 0.0, 0.0)

    # Neighbor flying fast in +Y direction
    neighbors = {
        '2': (Vector3(5.0, 0.0, 10.0), Vector3(0.0, 5.0, 0.0))
    }

    cmd = boids.compute_velocity(curr_pos, curr_vel, neighbors)

    # Alignment should steer in +y direction
    assert cmd.y > 0.0


def test_formation_controller_v_shape():
    fc = FormationController(formation_type='V_SHAPE', spacing=4.0)

    # Slot 1 is the leader at (0,0,0)
    offset_leader = fc.get_slot_offset(1, total_agents=5)
    assert (offset_leader.x, offset_leader.y, offset_leader.z) == (0.0, 0.0, 0.0)

    # Slot 2 is follower 1 (behind and to right)
    offset_f1 = fc.get_slot_offset(2, total_agents=5)
    assert offset_f1.x < 0.0
    assert offset_f1.y > 0.0

    # Slot 3 is follower 2 (behind and to left)
    offset_f2 = fc.get_slot_offset(3, total_agents=5)
    assert offset_f2.x < 0.0
    assert offset_f2.y < 0.0

    # Symmetry check: y offsets should be symmetric opposites
    assert math.isclose(offset_f1.y, -offset_f2.y)
    assert math.isclose(offset_f1.x, offset_f2.x)


def test_formation_tracking_velocity():
    fc = FormationController(formation_type='LINE', spacing=5.0)

    leader_pos = Vector3(0.0, 0.0, 10.0)
    leader_vel = Vector3(2.0, 0.0, 0.0)
    current_pos = Vector3(-10.0, 0.0, 10.0)

    cmd = fc.compute_velocity(
        current_pos=current_pos,
        leader_pos=leader_pos,
        leader_vel=leader_vel,
        slot_index=2,
        total_agents=3
    )

    # Drone is behind its slot, so cmd.x should be positive to catch up
    assert cmd.x > 0.0


def test_apf_obstacle_repulsion():
    apf = ArtificialPotentialField(k_att=1.0, k_rep=3.0, d_safe=3.0)

    # Obstacle scan right in front (angle 0.0 at range 1.0m)
    ranges = [1.0]
    rep = apf.compute_repulsion_from_scan(ranges, angle_min=0.0, angle_increment=0.1)

    # Obstacle is at angle 0 (+x), repulsion must push backwards (-x)
    assert rep.x < 0.0


def test_search_pattern_spiral():
    pos_t0, vel_t0 = SearchPatternGenerator.archimedean_spiral(t_seconds=0.0)
    assert math.isclose(pos_t0.x, 0.0, abs_tol=1e-5)
    assert math.isclose(pos_t0.y, 0.0, abs_tol=1e-5)

    pos_t10, vel_t10 = SearchPatternGenerator.archimedean_spiral(t_seconds=10.0)
    # Spiral should have expanded outwards
    assert pos_t10.magnitude_xy() > 0.0


def test_anomaly_detector():
    detector = AnomalyDetector(max_physical_speed=20.0, max_altitude=120.0)

    # Normal movement: 5 meters in 1 second = 5 m/s < 20 m/s
    is_valid, _ = detector.inspect_neighbor('drone_2', Vector3(0, 0, 10), timestamp=0.0)
    assert is_valid is True

    is_valid, _ = detector.inspect_neighbor('drone_2', Vector3(5, 0, 10), timestamp=1.0)
    assert is_valid is True
    assert not detector.is_flagged('drone_2')

    # Malicious teleportation: 500 meters in 0.1 second = 5000 m/s
    is_valid, reason = detector.inspect_neighbor('drone_2', Vector3(505, 0, 10), timestamp=1.1)
    assert is_valid is False
    assert detector.is_flagged('drone_2')
    assert "Spoofing" in reason or "Teleportation" in reason

    # Out-of-bounds altitude check
    is_valid, reason = detector.inspect_neighbor('drone_3', Vector3(0, 0, 200), timestamp=1.0)
    assert is_valid is False
    assert detector.is_flagged('drone_3')


def test_failsafe_manager():
    fs = FailSafeManager(heartbeat_timeout=3.0, min_battery_voltage=14.0)

    # Nominal flight
    state = fs.evaluate(last_heartbeat_age=1.0, battery_voltage=16.0)
    assert state == 'NORMAL'

    # Communication loss (> 3.0s timeout)
    state = fs.evaluate(last_heartbeat_age=4.5, battery_voltage=16.0)
    assert state == 'RTL'

    # Critical low battery (< 14.0V)
    state = fs.evaluate(last_heartbeat_age=0.5, battery_voltage=13.5)
    assert state == 'LAND'


def test_leader_election_engine():
    engine = LeaderElectionEngine(self_id=2, initial_leader_id=1, heartbeat_timeout=2.0)

    # Initial state
    assert engine.current_leader_id == 1
    assert engine.is_leader() is False

    # Leader 1 is active (fresh heartbeat)
    engine.record_leader_heartbeat(leader_id=1, timestamp=10.0)
    elected = engine.evaluate_election(timestamp=11.0, active_drone_ids=[1, 2, 3])
    assert elected == 1

    # Leader 1 times out (> 2.0s without heartbeat, e.g. at t=15.0)
    # Remaining active candidates: [2, 3]
    elected_after_failure = engine.evaluate_election(timestamp=15.0, active_drone_ids=[2, 3])
    # Drone 2 has lowest ID among active candidates, promoted to leader
    assert elected_after_failure == 2
    assert engine.is_leader() is True
    assert engine.term == 2


def test_geofence_manager():
    geo = GeofenceManager(
        bounds=(-50.0, 50.0, -50.0, 50.0, 0.5, 30.0),
        safety_margin=5.0,
        k_barrier=4.0
    )
    geo.add_nfz(x=10.0, y=10.0, radius=5.0, min_z=0.0, max_z=25.0)

    # In center: nominal, no boundary force
    pos_center = Vector3(0.0, 0.0, 15.0)
    assert geo.is_inside(pos_center) is True
    assert geo.is_in_nfz(pos_center) is False
    f_center = geo.compute_boundary_force(pos_center)
    assert (f_center.x, f_center.y, f_center.z) == (0.0, 0.0, 0.0)

    # Near +X boundary (x=48 > 45)
    pos_near_east = Vector3(48.0, 0.0, 15.0)
    f_east = geo.compute_boundary_force(pos_near_east)
    # Force must push back west (-x)
    assert f_east.x < 0.0

    # Inside NFZ at (10, 10)
    pos_in_nfz = Vector3(10.0, 10.0, 10.0)
    assert geo.is_in_nfz(pos_in_nfz) is True


def test_target_tracker():
    tracker = TargetTracker(confirmation_threshold=2, proximity_radius=5.0)

    # First detection from drone 1
    confirmed = tracker.report_detection('TARGET_1', Vector3(12.0, 14.0, 0.0), detector_id=1, timestamp=100.0)
    assert confirmed is False

    # Second detection from drone 2 within proximity
    confirmed = tracker.report_detection('TARGET_1', Vector3(12.2, 13.8, 0.0), detector_id=2, timestamp=101.0)
    assert confirmed is True

    targets = tracker.get_confirmed_targets()
    assert len(targets) == 1
    assert targets[0]['id'] == 'TARGET_1'

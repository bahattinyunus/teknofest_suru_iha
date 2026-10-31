from swarm_core.algorithms import Vector3
from swarm_core.sensor_fusion import SensorFusionEKF


def test_ekf_prediction_step():
    ekf = SensorFusionEKF(
        initial_pos=Vector3(0.0, 0.0, 10.0),
        initial_vel=Vector3(1.0, 0.0, 0.0)
    )

    # Predict with constant forward acceleration 2.0 m/s^2 for 0.5s
    accel = Vector3(2.0, 0.0, 0.0)
    pos, vel = ekf.predict(accel, dt=0.5)

    # Expected:
    # vel.x = 1.0 + 2.0 * 0.5 = 2.0 m/s
    # pos.x = 0.0 + 1.0 * 0.5 + 0.5 * 2.0 * (0.5^2) = 0.5 + 0.25 = 0.75 m
    assert abs(pos.x - 0.75) < 1e-4
    assert abs(vel.x - 2.0) < 1e-4
    assert abs(pos.z - 10.0) < 1e-4


def test_ekf_gps_update_and_innovation_gate():
    ekf = SensorFusionEKF(
        initial_pos=Vector3(0.0, 0.0, 10.0),
        initial_vel=Vector3(0.0, 0.0, 0.0)
    )

    # Valid GPS measurement close to current state
    valid_meas = Vector3(0.5, -0.2, 10.1)
    accepted = ekf.update_gps(valid_meas, hdop=1.0)
    assert accepted is True
    assert ekf.gnss_available is True
    assert not ekf.gnss_spoofed

    # Position should have shifted towards measurement
    assert ekf.pos.x > 0.1
    assert ekf.pos.y < -0.05

    # Spoofed GPS measurement (teleported 500m away) -> should be rejected by gate!
    spoofed_meas = Vector3(500.0, 500.0, 200.0)
    accepted_spoof = ekf.update_gps(spoofed_meas, hdop=1.0)
    assert accepted_spoof is False
    assert ekf.gnss_spoofed is True
    assert ekf.gnss_available is False


def test_ekf_barometer_update():
    ekf = SensorFusionEKF(
        initial_pos=Vector3(5.0, 5.0, 10.0)
    )

    # Altimeter reading indicates drone is at 12.0m
    ekf.update_barometer(12.0)
    # Z position should increase towards 12.0
    assert ekf.pos.z > 10.5
    assert ekf.cov_p.z < 1.0


def test_ekf_relative_uwb_ranging():
    ekf = SensorFusionEKF(
        initial_pos=Vector3(10.0, 0.0, 10.0)
    )

    # Known neighbor anchor at (0, 0, 10)
    anchor = Vector3(0.0, 0.0, 10.0)
    # True distance is 10.0, measured is 8.0 (meaning drone is closer to anchor)
    updated = ekf.update_relative_range(anchor, measured_range=8.0)
    assert updated is True
    # pos.x should have pulled inwards towards anchor (< 10.0)
    assert ekf.pos.x < 10.0


def test_gnss_denied_dead_reckoning_and_health():
    ekf = SensorFusionEKF(
        initial_pos=Vector3(0.0, 0.0, 10.0)
    )
    assert ekf.is_navigation_healthy()

    # Simulate GNSS loss
    ekf.gnss_available = False

    # Propagate for 10 seconds of dead-reckoning without GPS updates
    for _ in range(100):
        ekf.predict(Vector3(0.1, 0.0, 0.0), dt=0.1)

    assert ekf.dead_reckoning_duration > 9.0
    # Uncertainty should have grown
    uncertainty = ekf.get_position_uncertainty()
    assert uncertainty > 1.0

    telemetry = ekf.get_telemetry_dict()
    assert telemetry["gnss_available"] is False
    assert telemetry["dead_reckoning_seconds"] > 9.0

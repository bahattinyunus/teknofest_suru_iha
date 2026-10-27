import pytest
from swarm_simulation.mock_sitl_bridge import FastSwarmSim, SimulatedUAV


def test_simulated_uav_kinematics():
    uav = SimulatedUAV(uav_id=1, init_x=0.0, init_y=0.0, init_z=10.0)
    uav.cmd_vx = 2.0
    uav.cmd_vy = 1.0

    # Step dynamics for 1 second (10 steps of 0.1s)
    for _ in range(10):
        uav.update(dt=0.1)

    assert uav.x > 0.5
    assert uav.y > 0.2
    assert uav.z == 10.0


def test_fast_swarm_sim():
    sim = FastSwarmSim(num_drones=5)
    assert len(sim.drones) == 5

    # Step simulation
    sim.step(dt=0.05)

    # LiDAR scan raycast test
    scan = sim.generate_lidar_scan(sim.drones[1], num_rays=36)
    assert len(scan) == 36
    # Ranges should be positive within maximum range
    assert all(0.1 <= r <= 30.0 for r in scan)

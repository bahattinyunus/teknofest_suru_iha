import pytest
import math
from swarm_core.algorithms import Vector3, BoidsController


def test_boids_separation_math():
    boids = BoidsController(
        cohesion_weight=0.0,
        alignment_weight=0.0,
        separation_weight=1.5,
        safe_distance=3.0
    )
    curr_pos = Vector3(0.0, 0.0, 0.0)
    curr_vel = Vector3(0.0, 0.0, 0.0)

    # Neighbor is at (1.0, 1.0, 0.0), closer than safe_distance 3.0
    neighbors = {
        'drone_2': (Vector3(1.0, 1.0, 0.0), Vector3(0.0, 0.0, 0.0))
    }

    cmd = boids.compute_velocity(curr_pos, curr_vel, neighbors)

    # Separation must repel from (1, 1), so both cmd.x and cmd.y must be negative
    assert cmd.x < 0.0
    assert cmd.y < 0.0
    # Diagonal angle should be symmetric
    assert math.isclose(cmd.x, cmd.y, rel_tol=1e-3)


def test_boids_max_speed_clamping():
    boids = BoidsController(
        cohesion_weight=10.0,
        goal_weight=10.0,
        max_speed=4.5
    )
    curr_pos = Vector3(0.0, 0.0, 0.0)
    curr_vel = Vector3(0.0, 0.0, 0.0)
    goal = Vector3(100.0, 100.0, 0.0)

    cmd = boids.compute_velocity(curr_pos, curr_vel, neighbors={}, goal_pos=goal)

    # Resulting velocity magnitude must not exceed max_speed
    assert math.isclose(cmd.magnitude(), 4.5, rel_tol=1e-3)

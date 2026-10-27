import pytest
import math
from swarm_core.algorithms import Vector3, AuctionTaskAllocator, TrajectoryGenerator


def test_auction_task_allocator():
    allocator = AuctionTaskAllocator(weight_dist=1.0, weight_battery=0.5)

    # 2 tasks
    allocator.add_task("TARGET_NORTH", Vector3(0.0, 20.0, 0.0), priority=2)
    allocator.add_task("TARGET_SOUTH", Vector3(0.0, -20.0, 0.0), priority=1)

    # 2 UAVs: UAV-1 is near North (0, 15), UAV-2 is near South (0, -15)
    fleet = {
        1: {'pos': Vector3(0.0, 15.0, 10.0), 'battery': 90.0},
        2: {'pos': Vector3(0.0, -15.0, 10.0), 'battery': 90.0}
    }

    assignments = allocator.allocate_tasks(fleet)

    # UAV-1 should win North, UAV-2 should win South
    assert assignments["TARGET_NORTH"] == 1
    assert assignments["TARGET_SOUTH"] == 2
    assert allocator.get_assigned_task(1) == "TARGET_NORTH"
    assert allocator.get_assigned_task(2) == "TARGET_SOUTH"


def test_auction_battery_penalty():
    allocator = AuctionTaskAllocator(weight_dist=1.0, weight_battery=2.0)
    allocator.add_task("URGENT_TASK", Vector3(10.0, 0.0, 0.0))

    # UAV-1 is closer (dist 5m) but critically low battery (10%)
    # UAV-2 is slightly further (dist 10m) but full battery (100%)
    fleet = {
        1: {'pos': Vector3(5.0, 0.0, 0.0), 'battery': 10.0},
        2: {'pos': Vector3(0.0, 0.0, 0.0), 'battery': 100.0}
    }

    assignments = allocator.allocate_tasks(fleet)
    # UAV-2 wins because UAV-1 battery penalty dominates
    assert assignments["URGENT_TASK"] == 2


def test_quintic_trajectory_generator():
    p_start = Vector3(0.0, 0.0, 0.0)
    p_end = Vector3(10.0, 20.0, 30.0)
    duration = 5.0

    # At t=0: position is start, velocity is 0
    p0, v0 = TrajectoryGenerator.quintic_trajectory(p_start, p_end, duration, t=0.0)
    assert (p0.x, p0.y, p0.z) == (0.0, 0.0, 0.0)
    assert (v0.x, v0.y, v0.z) == (0.0, 0.0, 0.0)

    # At t=T: position is end, velocity is 0
    pT, vT = TrajectoryGenerator.quintic_trajectory(p_start, p_end, duration, t=5.0)
    assert math.isclose(pT.x, 10.0, rel_tol=1e-5)
    assert math.isclose(pT.y, 20.0, rel_tol=1e-5)
    assert math.isclose(pT.z, 30.0, rel_tol=1e-5)
    assert math.isclose(vT.magnitude(), 0.0, abs_tol=1e-5)

    # At midpoint t=2.5: position is midway, velocity is positive peak
    p_mid, v_mid = TrajectoryGenerator.quintic_trajectory(p_start, p_end, duration, t=2.5)
    assert math.isclose(p_mid.x, 5.0, rel_tol=1e-5)
    assert math.isclose(p_mid.y, 10.0, rel_tol=1e-5)
    assert v_mid.x > 0.0

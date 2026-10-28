import pytest
from swarm_core.algorithms import Vector3
from swarm_core.precision_engagement import PrecisionEngagementController


def test_precision_engagement_state_machine():
    controller = PrecisionEngagementController(
        cruise_alt=10.0,
        drop_alt=2.0,
        approach_speed=4.0,
        descent_speed=1.0,
        alignment_tolerance=0.5
    )

    # 1. Initially IDLE
    assert controller.current_state == 'IDLE'

    # Assign target at (20, 20, 0)
    target = Vector3(20.0, 20.0, 0.0)
    controller.assign_target(target)
    assert controller.current_state == 'CRUISE_APPROACH'

    # 2. Cruise approach: Drone at (0, 0, 10)
    drone_pos = Vector3(0.0, 0.0, 10.0)
    cmd, state, is_done = controller.update(drone_pos, timestamp=0.0)
    assert state == 'CRUISE_APPROACH'
    assert is_done is False
    assert cmd.x > 0.0 and cmd.y > 0.0

    # 3. Visual alignment: Drone arrives near target (20.3, 20.2, 10)
    drone_pos = Vector3(20.3, 20.2, 10.0)
    cmd, state, _ = controller.update(drone_pos, timestamp=5.0)
    assert state in ['VISUAL_ALIGN', 'CONTROLLED_DESCENT']

    # 4. Controlled descent: Drone perfectly centered (20.0, 20.0, 8.0)
    drone_pos = Vector3(20.0, 20.0, 8.0)
    cmd, state, _ = controller.update(drone_pos, timestamp=6.0)
    assert state == 'CONTROLLED_DESCENT'
    assert cmd.z < 0.0  # Descending

    # 5. Engagement at drop altitude (20.0, 20.0, 2.0)
    drone_pos = Vector3(20.0, 20.0, 2.0)
    cmd, state, _ = controller.update(drone_pos, timestamp=10.0)
    assert state == 'ENGAGE'

    # Simulate dwell time elapsed (> 1.5s)
    cmd, state, _ = controller.update(drone_pos, timestamp=12.0)
    assert controller.payload_released is True
    assert state == 'CLIMB_REJOIN'
    assert cmd.z > 0.0  # Climbing back up

    # 6. Reached cruise altitude (20.0, 20.0, 10.0)
    drone_pos = Vector3(20.0, 20.0, 10.0)
    cmd, state, is_done = controller.update(drone_pos, timestamp=15.0)
    assert state == 'COMPLETED'
    assert is_done is True

from swarm_core.algorithms import Vector3
from swarm_core.rvo_avoidance import RVOCollisionAvoidance


def test_rvo_vo_cone_head_on_collision():
    rvo = RVOCollisionAvoidance(drone_radius=1.0, time_horizon=5.0)

    # Self at (0, 0, 10), heading +X with speed 2.0
    pos_self = Vector3(0.0, 0.0, 10.0)
    vel_self = Vector3(2.0, 0.0, 0.0)

    # Other at (10, 0, 10), heading -X with speed 2.0 (Direct head-on collision course in 2.5s)
    pos_other = Vector3(10.0, 0.0, 10.0)
    vel_other = Vector3(-2.0, 0.0, 0.0)

    # In collision course:
    in_vo = rvo.is_velocity_in_vo(
        pos_self, vel_self, pos_other, vel_other, combined_radius=2.0, tau=5.0
    )
    assert in_vo is True


def test_rvo_vo_cone_diverging_safe():
    rvo = RVOCollisionAvoidance(drone_radius=1.0, time_horizon=5.0)

    # Self moving +X, other already behind self and moving away
    pos_self = Vector3(10.0, 0.0, 10.0)
    vel_self = Vector3(2.0, 0.0, 0.0)

    pos_other = Vector3(0.0, 0.0, 10.0)
    vel_other = Vector3(-2.0, 0.0, 0.0)

    in_vo = rvo.is_velocity_in_vo(
        pos_self, vel_self, pos_other, vel_other, combined_radius=2.0, tau=5.0
    )
    assert in_vo is False


def test_rvo_avoidance_computation():
    rvo = RVOCollisionAvoidance(drone_radius=0.8, time_horizon=4.0, max_speed=4.0)

    # Self at (0, 0, 10), wanting to fly directly +X at 3.0 m/s
    pos_self = Vector3(0.0, 0.0, 10.0)
    vel_self = Vector3(3.0, 0.0, 0.0)
    vel_pref = Vector3(3.0, 0.0, 0.0)

    # Other directly in front at (5, 0, 10), flying towards self at -2.0 m/s
    pos_other = Vector3(5.0, 0.0, 10.0)
    vel_other = Vector3(-2.0, 0.0, 0.0)

    avoid_vel = rvo.compute_avoidance_velocity(
        pos_self=pos_self,
        vel_current=vel_self,
        vel_preferred=vel_pref,
        neighbors=[(pos_other, vel_other)]
    )

    # The computed avoidance velocity must deflect laterally or vertically
    assert abs(avoid_vel.y) > 0.1 or abs(avoid_vel.z) > 0.1 or avoid_vel.x < 1.0
    # Must remain safe according to collision check
    assert rvo.is_collision_free(pos_self, avoid_vel, [(pos_other, vel_other)]) is True


def test_rvo_static_obstacle_avoidance():
    rvo = RVOCollisionAvoidance(drone_radius=0.5, time_horizon=3.0, max_speed=4.0)

    pos_self = Vector3(0.0, 0.0, 10.0)
    vel_self = Vector3(3.0, 0.0, 0.0)
    vel_pref = Vector3(3.0, 0.0, 0.0)

    # Obstacle with radius 2.0 at (4, 0, 10)
    obs = [(Vector3(4.0, 0.0, 10.0), 2.0)]

    avoid_vel = rvo.compute_avoidance_velocity(
        pos_self=pos_self,
        vel_current=vel_self,
        vel_preferred=vel_pref,
        neighbors=[],
        obstacles=obs
    )

    # Must steer around obstacle
    assert rvo.is_collision_free(pos_self, avoid_vel, [], obstacles=obs) is True
